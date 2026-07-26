# Claude Code Cheatsheet

An interactive index of every command in Claude Code **build 2.1.220** — 96 native slash commands,
23 bundled skills, 14 `claude` CLI subcommands, 10 hidden entries, and 57 CLI flags. Search, filter
by category, and follow any name through to its page in the official documentation.

**→ [johnmiroki.github.io/claude-code-cheatsheet](https://johnmiroki.github.io/claude-code-cheatsheet/)**

## Where the data comes from

Names, descriptions, aliases, and argument hints were parsed out of the command registry inside the
installed binary (`~/.local/share/claude/versions/2.1.220`) rather than copied from the published
docs. CLI commands and flags come from `claude --help` on the same build. As a result the index
covers commands the documentation doesn't mention — and omits four it lists that this build does not
register.

## Defined is not the same as available

Being compiled into the binary does not make a command reachable: the CLI builds its registry from a
list with conditional entries, so a command can ship in the bundle and never be registered. Every
command that cannot execute in print mode was probed against the build and classified by its
response:

| Response to `claude -p "/x"`             | Meaning                       |
| ---------------------------------------- | ----------------------------- |
| actual output                             | registered and enabled        |
| `/x isn't available in this environment.` | registered, gated at runtime  |
| `Unknown command: /x`                     | not in the registry at all    |

Eleven entries fall into the last group and are tagged as such on the page. Commands that *would*
have executed were excluded from the probe rather than run.

## The page

One self-contained `index.html`. No build step, no dependencies, no external requests; light and
dark themes follow your system setting.

---

If it saved you some time: [buy me a coffee](https://buymeacoffee.com/johnmiroki) ☕
