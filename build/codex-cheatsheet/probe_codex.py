#!/usr/bin/env python3
"""Re-measure the Codex CLI surface that codex-commands.html publishes.

    python3 build/codex-cheatsheet/probe_codex.py [/path/to/codex] [out.json]

This does not write the page. It writes a JSON report you diff against the page source
after a Codex release, so the published numbers can be re-established rather than trusted.

Three measurements, none of which read the documentation:

  slash commands   The TUI is launched in a pseudo-terminal, "/" opens the picker, and the
                   arrow key walks it to the end. Every row the picker renders is captured
                   with the description it renders. This, not the binary, is the source for
                   the published list.

  availability     CANDIDATES below are names read by hand out of the registry's string
                   block in the binary. They cannot be recovered by regex: the block packs
                   the names end to end with no delimiter, and Rust interns duplicate
                   literals, so any name that also appears elsewhere in the program is
                   missing from the block entirely. The script therefore does not try to
                   parse them out - it confirms each candidate string is really present in
                   the binary, then establishes the verdict by probing, which is the actual
                   evidence. Any candidate the picker already offered is skipped; the rest
                   are typed at the prompt and classified against a deliberately nonsensical
                   control command:
                     ran           - runs normally; withheld from the picker only
                     unrecognized  - "Unrecognized command", identical to the control
                   Commands that would have done real work are listed in DO_NOT_RUN and
                   reported as "not probed" rather than executed. Their availability is
                   left unestablished instead of guessed at.
                   A candidate that stops appearing in the binary is reported as gone, so a
                   later build shrinking this set is visible rather than silent.

  cli + features   A recursive walk of `codex --help` over every subcommand, plus
                   `codex features list` verbatim.

The TUI is driven with MCP servers disabled and a read-only sandbox, in a directory Codex
already trusts, so no trust prompt swallows the keystrokes.
"""
import fcntl
import json
import os
import pty
import re
import select
import struct
import sys
import subprocess
import termios
import time

try:
    import pyte
except ImportError:
    raise SystemExit("needs pyte to render the TUI: pip3 install pyte")

ROWS, COLS = 90, 180

# Read by hand out of the slash-command registry's string block in the binary, which sits
# immediately before the matching block of descriptions. See the module docstring for why
# this is a hand-kept list rather than something the script parses. Names the picker already
# offers are skipped at run time, so this list may safely contain them.
CANDIDATES = [
    "ide", "keymap", "vim", "setup-default-sandbox", "sandbox-add-read-dir", "approve",
    "import", "rename", "new", "archive", "resume", "fork", "app", "init", "side", "btw",
    "copy", "raw", "usage", "debug-config", "statusline", "pets", "logout", "quit", "exit",
    "rollout", "ps", "clear", "test-approval", "debug-m-drop", "debug-m-update", "apps",
]

# Present in the binary, never offered by the picker, and deliberately never executed:
# running them would reconfigure the sandbox, or the build itself labels them DO NOT USE.
DO_NOT_RUN = {
    "setup-default-sandbox": "would have reconfigured the agent sandbox",
    "debug-m-drop": "the binary labels this DO NOT USE",
    "debug-m-update": "the binary labels this DO NOT USE",
}

CONTROL = "zzz-not-a-command"
ROW = re.compile(r"^\s*(?:[>❯»▌│┃\s]*)/([a-z][a-z0-9-]*)\s\s+(\S.*?)\s*$")


# ------------------------------------------------------------------ pseudo-terminal driver

class Tui:
    def __init__(self, codex, cwd):
        self.pid, self.fd = pty.fork()
        if self.pid == 0:
            os.environ.update(TERM="xterm-256color", NO_COLOR="1",
                              COLUMNS=str(COLS), LINES=str(ROWS))
            os.execv(codex, [codex, "--sandbox", "read-only", "-C", cwd,
                             "-c", "mcp_servers={}",
                             "-c", "suppress_unstable_features_warning=true"])
        fcntl.ioctl(self.fd, termios.TIOCSWINSZ, struct.pack("HHHH", ROWS, COLS, 0, 0))
        self.screen = pyte.Screen(COLS, ROWS)
        self.stream = pyte.ByteStream(self.screen)

    def pump(self, seconds):
        end = time.time() + seconds
        while time.time() < end:
            ready, _, _ = select.select([self.fd], [], [], 0.08)
            if ready:
                try:
                    data = os.read(self.fd, 65536)
                except OSError:
                    return
                if data:
                    self.stream.feed(data)

    def send(self, keys, settle=0.12):
        os.write(self.fd, keys)
        self.pump(settle)

    def rows(self):
        return [line.rstrip() for line in self.screen.display]

    def close(self):
        try:
            self.send(b"\x1b", 0.3)
            self.send(b"\x03", 0.3)
            self.send(b"\x03", 0.3)
        except OSError:
            pass
        try:
            os.kill(self.pid, 9)
        except OSError:
            pass
        try:
            os.close(self.fd)
        except OSError:
            pass


def picker_commands(codex, cwd, boot=14):
    """Open the / picker and walk it to the end, collecting every row it renders."""
    tui = Tui(codex, cwd)
    tui.pump(boot)
    tui.send(b"/", 3)
    found, order = {}, []

    def harvest():
        for line in tui.rows():
            m = ROW.match(line)
            if not m:
                continue
            name, desc = m.group(1), re.sub(r"\s*│\s*$", "", m.group(2)).strip()
            if name not in found:
                found[name] = desc
                order.append(name)

    harvest()
    for _ in range(120):
        tui.send(b"\x1b[B", 0.14)
        harvest()
    tui.close()
    return [{"name": n, "description": found[n]} for n in order]


def classify(codex, cwd, name, boot=13):
    """Type one command at the prompt, submit it, and read the response.

    A fresh process per command: the composer is stateful, and a half-cleared composer
    silently turns the next probe into a prompt rather than a command.
    """
    tui = Tui(codex, cwd)
    tui.pump(boot)
    tui.send(("/" + name).encode(), 1.0)
    tui.send(b"\r", 3.5)
    text = [line for line in tui.rows() if line.strip()]
    tui.close()
    unrecognized = any("Unrecognized command" in line for line in text)
    return "unrecognized" if unrecognized else "ran", text


# ------------------------------------------------------------------ static + help surface

def present_in_binary(codex, names):
    """Which candidate names still appear in the binary at all.

    Confirmation only, never discovery: the names are packed end to end in the registry's
    string block, so there is no delimiter to split on. A candidate that has vanished is
    reported rather than silently dropped.
    """
    data = open(codex, "rb").read()
    return {n: (b"/" + n.encode() in data or n.encode() in data) for n in names}


def run(codex, args, timeout=60):
    r = subprocess.run([codex] + args, capture_output=True, text=True, timeout=timeout)
    return (r.stdout or "") + (r.stderr or "")


def help_tree(codex):
    tree = {}

    def subs(text):
        m = re.search(r"^Commands:\n((?:  \S.*\n|    .*\n)+)", text, re.M)
        if not m:
            return []
        out = []
        for line in m.group(1).splitlines():
            mm = re.match(r"^  (\S+)\s\s+", line)
            if mm and mm.group(1) != "help":
                out.append(mm.group(1))
        return out

    def walk(path, depth=0):
        if depth > 3:
            return
        text = run(codex, path + ["--help"])
        tree[" ".join(["codex"] + path)] = text
        for s in subs(text):
            walk(path + [s], depth + 1)

    walk([])
    return tree


def features(codex):
    out = []
    for line in run(codex, ["features", "list"]).strip().splitlines():
        m = re.match(r"^(\S+)\s+(stable|under development|removed|deprecated|experimental)"
                     r"\s+(true|false)\s*$", line)
        if m:
            out.append({"name": m.group(1), "stage": m.group(2), "enabled": m.group(3) == "true"})
    return out


# ------------------------------------------------------------------ run

def main():
    codex = sys.argv[1] if len(sys.argv) > 1 else "/opt/homebrew/bin/codex"
    out = sys.argv[2] if len(sys.argv) > 2 else "codex-probe.json"
    codex = os.path.realpath(codex)
    cwd = os.environ.get("CODEX_PROBE_CWD", os.path.expanduser("~"))

    version = run(codex, ["--version"]).strip()
    print("probing %s (%s)" % (codex, version))
    print("  driving the TUI in %s" % cwd)

    listed = picker_commands(codex, cwd)
    print("  picker listed %d slash commands" % len(listed))

    names = {c["name"] for c in listed}
    still_there = present_in_binary(codex, CANDIDATES)
    gone = [n for n, ok in still_there.items() if not ok]
    if gone:
        print("  candidate(s) no longer in the binary: %s" % ", ".join(gone))
    extra = [n for n in CANDIDATES if still_there[n] and n not in names]
    print("  %d candidate(s) the picker never offered: %s"
          % (len(extra), ", ".join(extra) or "none"))

    probed = []
    control_verdict, _ = classify(codex, cwd, CONTROL)
    print("  control /%s -> %s" % (CONTROL, control_verdict))
    if control_verdict != "unrecognized":
        raise SystemExit("control command was not rejected; the probe cannot distinguish states")

    for name in extra:
        if name in DO_NOT_RUN:
            probed.append({"name": name, "probe": "not probed", "note": DO_NOT_RUN[name]})
            print("    /%-22s not probed (%s)" % (name, DO_NOT_RUN[name]))
            continue
        verdict, _ = classify(codex, cwd, name)
        probed.append({"name": name, "probe": verdict, "note": None})
        print("    /%-22s %s" % (name, verdict))

    tree = help_tree(codex)
    feats = features(codex)
    print("  %d help pages, %d feature flags (%d on)"
          % (len(tree), len(feats), sum(1 for f in feats if f["enabled"])))

    report = {
        "codex": codex,
        "version": version,
        "method": {
            "slash": "TUI driven in a pseudo-terminal; / picker opened and paged to its end",
            "availability": "each candidate not offered by the picker typed at the prompt, "
                            "classified against a nonsensical control command",
            "control": CONTROL,
            "cli": "recursive walk of `codex --help`",
            "features": "`codex features list` verbatim",
        },
        "pickerCommands": listed,
        "candidatesGoneFromBinary": gone,
        "binaryOnly": probed,
        "helpPages": sorted(tree),
        "help": tree,
        "features": feats,
    }
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=1, ensure_ascii=False)
    print("wrote %s" % out)


if __name__ == "__main__":
    main()
