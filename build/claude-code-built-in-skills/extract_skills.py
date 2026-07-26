"""Mine Claude Code's bundled skills out of the compiled CLI binary.

    python3 build/claude-code-built-in-skills/extract_skills.py \\
        ~/.local/share/claude/versions/2.1.220 \\
        build/claude-code-built-in-skills/skills-data.json

Claude Code ships as one Bun-compiled native executable with its JavaScript
bundle embedded verbatim. Every bundled skill is registered in that bundle by a
call of the form

    ou({name:"doctor", menuDescription:"...", description:"...",
        async getPromptForCommand(e){ ... }})

and its prompt arrives by one of four routes: a whole SKILL.md shipped as a
module export, one long string constant, an array of sections joined at run
time, or a builder function that stitches literals around interpolated state.
This resolves all four and writes the JSON the site build renders.

The binary is read as text and parsed. Nothing here executes it.
"""
import json, pathlib, re, sys

BIN = sys.argv[1] if len(sys.argv) > 1 else None

BUILD = pathlib.Path(BIN).name if BIN else "unknown"

def log(msg):
    sys.stderr.write(msg + "\n")


_RAW = pathlib.Path(BIN).read_bytes()


def _js_region(raw, center=243342764, step=4096):
    def ok(off):
        chunk = raw[off:off + 4096]
        if not chunk:
            return False
        good = sum(1 for b in chunk if 9 <= b <= 13 or 32 <= b < 127)
        return good / len(chunk) > 0.95
    lo = center
    while lo > 0 and ok(lo - step):
        lo -= step
    hi = center
    while hi < len(raw) and ok(hi + step):
        hi += step
    return lo, hi


JS_LO, JS_HI = _js_region(_RAW)
DATA = _RAW[JS_LO:JS_HI].decode("latin-1")
del _RAW


def scan_balanced(s, start, open_c="{", close_c="}"):
    depth = 0
    i = start
    n = len(s)
    while i < n:
        c = s[i]
        if c in "\"'`":
            q = c
            i += 1
            while i < n:
                if s[i] == "\\":
                    i += 2
                    continue
                if q == "`" and s[i] == "$" and i + 1 < n and s[i + 1] == "{":
                    i = scan_balanced(s, i + 1)
                    continue
                if s[i] == q:
                    break
                i += 1
            i += 1
            continue
        if c == open_c:
            depth += 1
        elif c == close_c:
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError("unbalanced")


ESC = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", "'": "'", '"': '"', "`": "`",
       "$": "$", "b": "\b", "f": "\f", "v": "\v", "0": "\0", "/": "/"}


def js_str_at(s, i):
    q = s[i]
    out = []
    i += 1
    n = len(s)
    while i < n:
        c = s[i]
        if c == "\\":
            nxt = s[i + 1]
            if nxt == "u":
                if s[i + 2] == "{":
                    j = s.index("}", i + 2)
                    out.append(chr(int(s[i + 3:j], 16)))
                    i = j + 1
                else:
                    out.append(chr(int(s[i + 2:i + 6], 16)))
                    i += 6
                continue
            if nxt == "x":
                out.append(chr(int(s[i + 2:i + 4], 16)))
                i += 4
                continue
            if nxt == "\r":
                i += 2
                continue
            if nxt == "\n":
                i += 2
                continue
            out.append(ESC.get(nxt, nxt))
            i += 2
            continue
        if q == "`" and c == "$" and s[i + 1] == "{":
            j = scan_balanced(s, i + 1)
            out.append("${" + s[i + 2:j - 1].strip() + "}")
            i = j
            continue
        if c == q:
            s2 = "".join(out)
            return s2.encode("utf-16", "surrogatepass").decode("utf-16", "replace"), i + 1
        out.append(c)
        i += 1
    raise ValueError("unterminated")


def read_expr_string(s, i):
    """Read a (possibly concatenated) string expression at i. Returns (value, end) or None."""
    parts = []
    n = len(s)
    while i < n:
        while i < n and s[i] in " \n\t":
            i += 1
        if i < n and s[i] in "\"'`":
            try:
                v, i = js_str_at(s, i)
            except Exception:
                return None
            parts.append(v)
        else:
            return None
        while i < n and s[i] in " \n\t":
            i += 1
        if i < n and s[i] == "+":
            i += 1
            continue
        break
    return ("".join(parts), i) if parts else None


# ---------- symbol tables ----------
STR_ASSIGN = {}     # ident -> string value
ALIAS = {}          # ident -> ident
FUNC_RET = {}       # ident -> string value (function f(){return "..."} )

for m in re.finditer(r'(?:^|[,;{()\s])(?:var\s+|let\s+|const\s+)?([A-Za-z_$][\w$]*)\s*=\s*(?=["\'`])', DATA):
    name = m.group(1)
    r = read_expr_string(DATA, m.end())
    if not r:
        continue
    val = r[0]
    if name not in STR_ASSIGN or len(val) > len(STR_ASSIGN[name]):
        STR_ASSIGN[name] = val

# IDENT = (args) => `template`   /   IDENT = args => "string"
for m in re.finditer(r'(?:^|[,;{(\s])([A-Za-z_$][\w$]*)\s*=\s*(?:\([^()]{0,160}\)|[A-Za-z_$][\w$]*)\s*=>\s*(?=["\'`])', DATA):
    name = m.group(1)
    r = read_expr_string(DATA, m.end())
    if not r:
        continue
    val = r[0]
    if name not in STR_ASSIGN or len(val) > len(STR_ASSIGN[name]):
        STR_ASSIGN[name] = val

for m in re.finditer(r'(?:^|[,;{(\s])([A-Za-z_$][\w$]*)\s*=\s*([A-Za-z_$][\w$]*)\s*(?=[,;)}])', DATA):
    a, b = m.group(1), m.group(2)
    if a != b:
        ALIAS.setdefault(a, b)

for m in re.finditer(r'function\s+([A-Za-z_$][\w$]*)\s*\(\s*\)\s*\{\s*return\s*(?=["\'`])', DATA):
    name = m.group(1)
    r = read_expr_string(DATA, m.end())
    if r:
        v = r[0]
        if name not in FUNC_RET or len(v) > len(FUNC_RET[name]):
            FUNC_RET[name] = v

# ---- IDENT = [ "a", "b", ... ].join(sep) --------------------------------------
ARR_JOIN = {}
for m in re.finditer(r'(?:^|[,;{(\s])(?:var\s+|let\s+|const\s+)?([A-Za-z_$][\w$]*)\s*=\s*\[(?=["\'`])', DATA):
    name = m.group(1)
    lb = m.end() - 1
    try:
        rb = scan_balanced(DATA, lb, "[", "]")
    except Exception:
        continue
    jm = re.match(r'\.join\(', DATA[rb:rb + 12])
    sep = "\n"
    if jm:
        sep_start = rb + jm.end()
        if sep_start < len(DATA) and DATA[sep_start] in "\"'`":
            try:
                sep, _ = js_str_at(DATA, sep_start)
            except Exception:
                sep = "\n"
    inner, i, n, parts, ok = DATA[lb + 1:rb - 1], 0, rb - lb - 2, [], True
    while i < n:
        while i < n and inner[i] in " \n\t,":
            i += 1
        if i >= n:
            break
        if inner[i] in "\"'`":
            try:
                v, i = js_str_at(inner, i)
            except Exception:
                ok = False
                break
            parts.append(v)
        else:
            j = i
            depth = 0
            while j < n and not (inner[j] == "," and depth == 0):
                if inner[j] in "([{":
                    try:
                        j = scan_balanced(inner, j, inner[j], {"(": ")", "[": "]", "{": "}"}[inner[j]])
                    except Exception:
                        ok = False
                        break
                    continue
                j += 1
            parts.append(" EXPR:" + inner[i:j].strip() + " ")
            i = j
    if ok and parts:
        val = sep.join(parts)
        if name not in ARR_JOIN or len(val) > len(ARR_JOIN[name]):
            ARR_JOIN[name] = val

log("symbols: %d strings, %d aliases, %d functions, %d arrays"
    % (len(STR_ASSIGN), len(ALIAS), len(FUNC_RET), len(ARR_JOIN)))


def resolve_ident(name, depth=0):
    if depth > 12 or not name:
        return None
    best = None
    for tbl in (STR_ASSIGN, ARR_JOIN, FUNC_RET):
        v = tbl.get(name)
        if v is not None and (best is None or len(v) > len(best)):
            best = v
    if best is not None:
        return best
    if name in ALIAS:
        return resolve_ident(ALIAS[name], depth + 1)
    return None


# ---------- SKILL_MD module map: module-namespace ident -> markdown ----------
SKILL_MD_BY_EXPORT = {}
for m in re.finditer(r'tt\(([A-Za-z_$][\w$]*),\{([^}]*)\}\)', DATA):
    ns, members = m.group(1), m.group(2)
    mm = re.search(r'SKILL_MD:\(\)=>([A-Za-z_$][\w$]*)', members)
    if not mm:
        continue
    md = resolve_ident(mm.group(1))
    files = re.search(r'SKILL_FILES:\(\)=>([A-Za-z_$][\w$]*)', members)
    SKILL_MD_BY_EXPORT[ns] = {"md": md, "md_ident": mm.group(1),
                              "files_ident": files.group(1) if files else None}

log("SKILL.md modules: %d (%d resolved)"
    % (len(SKILL_MD_BY_EXPORT), sum(1 for v in SKILL_MD_BY_EXPORT.values() if v["md"])))

# loader fn -> module ns:  function qom(){return bWS??=Promise.resolve().then(() => (Uom(),$om))}
LOADER = {}
for m in re.finditer(
        r'function\s+([A-Za-z_$][\w$]*)\s*\(\s*\)\s*\{\s*return\s+[A-Za-z_$][\w$]*\?\?=Promise\.resolve\(\)\.then\(\(\)\s*=>\s*\(\s*[A-Za-z_$][\w$]*\(\)\s*,\s*([A-Za-z_$][\w$]*)\s*\)\)',
        DATA):
    LOADER[m.group(1)] = m.group(2)
log("module loaders: %d" % len(LOADER))

# SKILL_FILES contents: ident -> {filename: ident}
FILES_MAP = {}
for m in re.finditer(r'([A-Za-z_$][\w$]*)\s*=\s*\{((?:"[^"]+":[A-Za-z_$][\w$()]*,?\s*)+)\}', DATA):
    entries = dict(re.findall(r'"([^"]+)":([A-Za-z_$][\w$]*)', m.group(2)))
    if entries and all("." in k for k in entries):
        FILES_MAP.setdefault(m.group(1), entries)



# ---------- registrations ----------
def parse_obj_top_level(body):
    """Split a JS object literal body into top-level key -> raw-value strings."""
    assert body[0] == "{"
    inner = body[1:-1]
    out, i, n = {}, 0, len(inner)
    while i < n:
        while i < n and inner[i] in " \n\t,":
            i += 1
        if i >= n:
            break
        km = re.match(r'(?:async\s+)?(?:get\s+)?([A-Za-z_$][\w$]*|"[^"]+")\s*', inner[i:])
        if not km:
            i += 1
            continue
        key = km.group(1).strip('"')
        j = i + km.end()
        if j < n and inner[j] == ":":
            j += 1
            start = j
            depth = 0
            while j < n:
                c = inner[j]
                if c in "\"'`":
                    _, j = js_str_at(inner, j)
                    continue
                if c in "{[(":
                    j = scan_balanced(inner, j, c, {"{": "}", "[": "]", "(": ")"}[c])
                    continue
                if c == "," and depth == 0:
                    break
                j += 1
            out[key] = inner[start:j].strip()
            i = j
        elif j < n and inner[j] == "(":
            j = scan_balanced(inner, j, "(", ")")
            while j < n and inner[j] in " \n\t":
                j += 1
            if j < n and inner[j] == "{":
                j = scan_balanced(inner, j)
            out[key] = "<method>"
            i = j
        else:
            i = j + 1
    return out


def val_to_string(raw):
    if raw is None:
        return None
    raw = raw.strip()
    if not raw:
        return None
    if raw[0] in "\"'`":
        r = read_expr_string(raw, 0)
        return r[0] if r else None
    if re.fullmatch(r'[A-Za-z_$][\w$]*', raw):
        return resolve_ident(raw)
    if re.fullmatch(r'[A-Za-z_$][\w$]*\(\)', raw):
        return resolve_ident(raw[:-2])
    return None


regs = []
for m in re.finditer(r'\bou\(\{', DATA):
    br = m.end() - 1
    try:
        end = scan_balanced(DATA, br)
    except Exception:
        continue
    regs.append((br, DATA[br:end]))

results = []
for br, body in regs:
    obj = parse_obj_top_level(body)
    raw_name = obj.get("name", "")
    name = val_to_string(raw_name) or raw_name
    entry = {
        "name": name,
        "raw_name": raw_name,
        "menuDescription": val_to_string(obj.get("menuDescription")),
        "description": val_to_string(obj.get("description")),
        "whenToUse": val_to_string(obj.get("whenToUse")),
        "argumentHint": val_to_string(obj.get("argumentHint")) or obj.get("argumentHint"),
        "allowedTools": obj.get("allowedTools"),
        "userInvocable": obj.get("userInvocable"),
        "disableModelInvocation": obj.get("disableModelInvocation"),
        "isEnabled": obj.get("isEnabled"),
        "requires": obj.get("requires"),
        "subcommands": obj.get("subcommands"),
        "progressMessage": val_to_string(obj.get("progressMessage")),
        "keys": sorted(obj.keys()),
        "offset": br,
        "body": body,
    }
    # prompt sources
    prompt = None
    src = None
    # a) files:()=>LOADER().then(...)  + SKILL_MD
    lm = re.search(r'([A-Za-z_$][\w$]*)\(\)\.then\(\(\w+\)=>\w+\.SKILL_(?:FILES|PROMPT|MD)', body)
    if not lm:
        lm = re.search(r'await\s+([A-Za-z_$][\w$]*)\(\)', body)
    if lm and lm.group(1) in LOADER:
        ns = LOADER[lm.group(1)]
        info = SKILL_MD_BY_EXPORT.get(ns)
        if info and info["md"]:
            prompt, src = info["md"], "SKILL_MD:" + ns
            entry["files_ident"] = info["files_ident"]
    # b) SKILL_MD destructure from a loader call
    if prompt is None:
        dm = re.search(r'\{SKILL_(?:MD|PROMPT):\w+\}\s*=\s*await\s+([A-Za-z_$][\w$]*)\(\)', body)
        if dm and dm.group(1) in LOADER:
            info = SKILL_MD_BY_EXPORT.get(LOADER[dm.group(1)])
            if info and info["md"]:
                prompt, src = info["md"], "SKILL_MD:" + LOADER[dm.group(1)]
    entry["prompt"] = prompt
    entry["prompt_source"] = src
    results.append(entry)

D = DATA


def func_src(name):
    m = re.search(r'(?:async\s+)?function\s+%s\s*\(' % re.escape(name), D)
    if m:
        j = D.index("{", m.end() - 1)
        try:
            return D[j:scan_balanced(D, j)]
        except Exception:
            return None
    m = re.search(r'(?<![\w$])%s\s*=\s*(?:async\s*)?\(?[^)=]{0,120}\)?\s*=>\s*\{' % re.escape(name), D)
    if m:
        j = D.index("{", m.end() - 1)
        try:
            return D[j:scan_balanced(D, j)]
        except Exception:
            return None
    return None


def literals_in(src, minlen=50):
    out, i, n = [], 0, len(src)
    while i < n:
        if src[i] in "\"'`":
            try:
                v, j = js_str_at(src, i)
            except Exception:
                i += 1
                continue
            if len(v) >= minlen:
                out.append(v)
            i = j
            continue
        i += 1
    return out


def placeholders(text):
    """Spans of `${...}` left in an extracted string, innermost-safe, as (start, end, expr)."""
    out, i, n = [], 0, len(text)
    while i < n - 1:
        if text[i] == "$" and text[i + 1] == "{":
            depth, j = 0, i + 1
            while j < n:
                if text[j] == "{":
                    depth += 1
                elif text[j] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            if j < n:
                out.append((i, j + 1, text[i + 2:j]))
                i = j + 1
                continue
        i += 1
    return out


def expand(text, depth=0):
    """Resolve what a `${...}` hole can be resolved to; mark the rest as a hole.

    Three outcomes, in order of preference. A bare identifier that names a short string
    constant is substituted, so `${Go}` becomes the tool name it holds. An expression that
    still carries literal text — most often a ternary picking between two phrasings — is
    reduced to that text, because both branches really are prompt the model can be shown.
    Anything else is a run-time value no static read can know, and becomes `${…}` rather
    than leaking minified JavaScript onto the page.
    """
    if depth > 3 or not text or "${" not in text:
        return text

    out, last = [], 0
    for start, end, expr in placeholders(text):
        out.append(text[last:start])
        last = end
        bare = re.fullmatch(r'\s*([A-Za-z_$][\w$]*)\(?\)?\s*', expr)
        if bare:
            v = resolve_ident(bare.group(1))
            if v and len(v) < 300 and "\n" not in v:
                out.append(v)
                continue
        lits = [v for v in literals_in(expr, 1) if v.strip()]
        out.append(expand(" ".join(lits), depth + 1) if lits else "${…}")
    out.append(text[last:])
    return "".join(out)


def ident(name, minlen=1):
    v = resolve_ident(name)
    return v if v and len(v) >= minlen else None


def builder(name, minlen=50):
    src = func_src(name)
    return "\n\n".join(literals_in(src, minlen)) if src else None



# ------------------------------------------------------------------ metadata
REG = {s["name"]: s for s in results}

# module namespaces that export SKILL_MD / SKILL_PROMPT
NS = {}
for m in re.finditer(r'tt\(([A-Za-z_$][\w$]*),\{([^}]{0,2000}?)\}\)', D):
    ex = dict(re.findall(r'([A-Z][A-Z0-9_]+):\(\)=>([A-Za-z_$][\w$]*)', m.group(2)))
    if ex:
        NS[m.group(1)] = ex

INLINE_NS = {m.group(1): m.group(2) for m in re.finditer(
    r'Promise\.resolve\(\)\.then\(\(\)\s*=>\s*\(\s*([A-Za-z_$][\w$]*)\(\)\s*,\s*([A-Za-z_$][\w$]*)\s*\)\)', D)}
LOADERS = dict(LOADER)
LOADERS.update(INLINE_NS)


def module_md(body):
    for m in re.finditer(r'([A-Za-z_$][\w$]*)\(\)', body):
        ns = LOADERS.get(m.group(1))
        if ns and ns in NS:
            for k in ("SKILL_MD", "SKILL_PROMPT", "SETUP_COWORK_PROMPT"):
                if k in NS[ns]:
                    v = resolve_ident(NS[ns][k])
                    if v:
                        return v, "SKILL.md embedded in the binary"
    return None, None


# per-skill prompt strategy, verified against the decompiled source
def P(*fns):
    for f in fns:
        v = f()
        if v:
            return v
    return None


STRATEGY = {
    "doctor":                   (lambda: ident("CGS"),  "single embedded prompt constant"),
    "fewer-permission-prompts": (lambda: ident("RGS"),  "single embedded prompt constant"),
    "update-config":            (lambda: "\n\n".join(filter(None, [ident("TVS"), ident("Csm"), ident("Asm")])),
                                 "prompt constant plus the hooks-reference sections it concatenates"),
    "simplify":                 (lambda: "\n\n".join(filter(None, [ident("gVS"), ident("_VS")])),
                                 "both branches: parallel-agent variant, then the inline fallback"),
    "keybindings-help":         (lambda: "\n\n".join(filter(None, [ident(i) for i in
                                 ["MGS", "NGS", "FGS", "BGS", "$GS", "UGS", "qGS", "jGS"]])),
                                 "the eight sections the skill joins at run time"),
    "memory-types":             (lambda: ident("UGr") or ident("qGr"), "the memory-taxonomy reference block"),
    "code-review":              (lambda: "\n\n".join(filter(None, [builder("q8S", 60)] + [
                                 ident(c) for c in ["Gnm", "iDd", "Nnm", "qnm"]])),
                                 "routing layer plus the per-effort review cells it selects between"),
    "code-walkthrough":         (lambda: builder("Y8S", 60), "assembled from the prompt builder's literals"),
    "pr-explainer":             (lambda: builder("pVS", 60), "assembled from the prompt builder's literals"),
    "design":                   (lambda: builder("CWS", 40), "assembled from the dispatch builder's literals"),
    "batch":                    (lambda: builder("c8S", 60), "assembled from the prompt builder's literals"),
    "claude-in-chrome":         (lambda: "\n\n".join(filter(None, [ident("Uyr"), ident("A8S")])),
                                 "the browser-automation prompt plus its tools-unavailable variant"),
    "artifact-capabilities":    (lambda: "\n\n".join(filter(None, [ident("Yll"), builder("Brm", 60)])),
                                 "static preamble; the capability roster is fetched at run time"),
    "loop":                     (lambda: "\n\n".join(filter(None, [builder("Vsm", 60), ident("$VS")])),
                                 "assembled from the loop-prompt builder plus the usage text"),
    "schedule":                 (lambda: builder("KVS", 60), "assembled from the prompt builder's literals"),
    "explain-usage":            (lambda: None, ""),
    "debug":                    (lambda: None, ""),
    "claude-api":               (lambda: None, ""),
    "claude-code-docs":         (lambda: None, ""),
}

ARTIFACT_KINDS = {"dashboard": "Qrm", "report": "unm", "data-table": "rnm", "explainer": "snm"}
A8S = {}
m = re.search(r'(?<![\w$])a8S\s*=\s*\[', D)
if m:
    lb = m.end() - 1
    arr = D[lb:scan_balanced(D, lb, "[", "]")]
    for om in re.finditer(r'\{kind:"([a-z-]+)"', arr):
        seg = arr[om.start():scan_balanced(arr, om.start())]
        obj = parse_obj_top_level(seg)
        A8S[om.group(1)] = {
            "menuDescription": val_to_string(obj.get("menuDescription")),
            "description": val_to_string(obj.get("description")),
        }

out = []
for name, s in REG.items():
    if name == "artifact-${e}":
        continue
    prompt = method = None
    if name in STRATEGY:
        fn, method = STRATEGY[name]
        prompt = fn()
    if prompt is None:
        prompt, method = module_md(s["body"])
    if prompt is None:
        segs = literals_in(s["body"], 150)
        if segs:
            prompt, method = "\n\n".join(segs), "assembled from the registration's own literals"
    out.append({**s, "prompt": expand(prompt), "prompt_method": method})

for kind, md_ident in ARTIFACT_KINDS.items():
    meta = A8S.get(kind, {})
    out.append({
        "name": "artifact-" + kind,
        "menuDescription": meta.get("menuDescription"),
        "description": meta.get("description"),
        "whenToUse": None, "argumentHint": None, "allowedTools": None,
        "userInvocable": "!0", "disableModelInvocation": None,
        "isEnabled": "QGr", "subcommands": None, "keys": [],
        "prompt": expand(resolve_ident(md_ident)),
        "prompt_method": "SKILL.md embedded in the binary",
        "body": "",
    })


for o in out:
    o["prompt_chars"] = len(o["prompt"] or "")
out.sort(key=lambda o: o["name"])
log("skills: %d (all with prompts: %s)"
    % (len(out), all(o["prompt"] for o in out)))

# ------------------------------------------------------------------ page data
src = out
SECTIONS = [
    ("Code, review and verification", "code", [
        "code-review", "simplify", "verify", "batch", "run", "run-skill-generator", "debug"]),
    ("Artifacts", "artifact", [
        "artifact-design", "artifact-capabilities", "artifact-dashboard", "artifact-report",
        "artifact-data-table", "artifact-explainer", "plan-artifact", "whiteboard", "workshop",
        "artifact-pr-review", "code-walkthrough", "pr-explainer"]),
    ("Configuration and setup", "config", [
        "doctor", "update-config", "keybindings-help", "fewer-permission-prompts",
        "memory-types", "explain-usage"]),
    ("Scheduling and repetition", "auto", ["loop", "schedule"]),
    ("Reference material", "ref", ["claude-api", "claude-code-docs", "dataviz"]),
    ("Design and browser", "design", ["design", "design-sync", "claude-in-chrome"]),
    ("Cowork", "cowork", ["cowork-plugin", "setup-cowork"]),
]

GATE_RE = re.compile(r'Ke\("([a-z0-9_]+)"')
ENV_RE = re.compile(r'CLAUDE_CODE_[A-Z_]+|process\.env\.([A-Z_]+)')

ARG_FIX = {
    "code-review": "[low|medium|high|xhigh|max] [target]",
    "loop": "[interval] [prompt]",
}


def flag(v):
    return True if v == "!0" else (False if v == "!1" else None)


def enable_expr(entry):
    """The isEnabled expression. Method shorthand — isEnabled(){...} — keeps its body instead."""
    expr = entry.get("isEnabled") or ""
    if expr != "<method>":
        return expr
    m = re.search(r'isEnabled\s*\(\s*\)\s*\{', entry.get("body") or "")
    if not m:
        return ""
    body = entry["body"]
    j = body.index("{", m.end() - 1)
    try:
        return body[j:scan_balanced(body, j)]
    except Exception:
        return ""


def gating(entry):
    """Feature flags and env vars an isEnabled check names directly, or one hop away.

    Deliberately shallow. Following the whole call graph turns up flags the skill only
    depends on transitively, which reads as precision the extraction does not have.
    """
    expr = enable_expr(entry)
    gates = set(GATE_RE.findall(expr))
    env = set(re.findall(r'CLAUDE_CODE_[A-Z_]+', expr))
    for fn in set(re.findall(r'(?<![\w$.])([A-Za-z_$][\w$]{1,})\s*\(', expr)) - {"Ke"}:
        m = re.search(r'function\s+%s\s*\(\s*\)\s*\{' % re.escape(fn), DATA)
        if not m:
            continue
        j = DATA.index("{", m.end() - 1)
        try:
            inner = DATA[j:scan_balanced(DATA, j)]
        except Exception:
            continue
        if len(inner) > 600:
            continue
        gates |= set(GATE_RE.findall(inner))
        env |= set(re.findall(r'CLAUDE_CODE_[A-Z_]+', inner))
    return sorted(gates), sorted(env)


by = {e["name"]: e for e in src}
placed = {n for _, _, names in SECTIONS for n in names}
leftover = sorted(n for n in by if n not in placed)
if leftover:
    SECTIONS.append(("Other", "other", leftover))

out_sections = []
count = 0
for title, key, names in SECTIONS:
    items = []
    for n in names:
        e = by.get(n)
        if not e:
            continue
        gates, env = gating(e)
        arg = ARG_FIX.get(n, e.get("argumentHint"))
        if arg in ("<method>", None) or (arg and "${" in arg):
            arg = ARG_FIX.get(n) or ""
        tools = e.get("allowedTools") or ""
        tools = re.findall(r'"([^"]+)"', tools) if tools else []
        items.append({
            "name": n,
            "menu": expand(e.get("menuDescription") or ""),
            "description": expand((e.get("description") or "").strip()),
            "whenToUse": expand((e.get("whenToUse") or "").strip()),
            "argumentHint": arg or "",
            "allowedTools": tools,
            "userInvocable": flag(e.get("userInvocable")),
            "modelInvocable": not (e.get("disableModelInvocation") == "!0"),
            "conditional": bool(e.get("isEnabled")),
            "gates": gates,
            "env": env,
            "prompt": e.get("prompt") or "",
            "promptMethod": e.get("promptMethod") or e.get("prompt_method") or "",
            "chars": len(e.get("prompt") or ""),
        })
        count += 1
    if items:
        out_sections.append({"title": title, "key": key, "items": items})

data = {
    "build": BUILD,
    "sections": out_sections,
    "totals": {
        "skills": count,
        "chars": sum(i["chars"] for s in out_sections for i in s["items"]),
        "userInvocable": sum(1 for s in out_sections for i in s["items"] if i["userInvocable"]),
        "modelInvocable": sum(1 for s in out_sections for i in s["items"] if i["modelInvocable"]),
        "embedded": sum(1 for s in out_sections for i in s["items"]
                        if i["promptMethod"].startswith("SKILL.md")),
        "conditional": sum(1 for s in out_sections for i in s["items"] if i["conditional"]),
    },
}
if len(sys.argv) > 2:
    pathlib.Path(sys.argv[2]).write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
    log("wrote %s" % sys.argv[2])
else:
    print(json.dumps(data, indent=1, ensure_ascii=False))
