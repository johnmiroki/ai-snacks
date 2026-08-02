#!/usr/bin/env python3
"""Assemble the whole site into the repo root. No browser needed.

Reads the page sources under build/<slug>/ plus the JSON that capture.mjs
snapshots out of a headless browser, and writes the published files.

    python3 build/build.py

Run `node build/capture.mjs` first if the page source or an OG template changed.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import siteconf as S  # noqa: E402

BUILD = pathlib.Path(__file__).resolve().parent
ROOT = BUILD.parent
CS_SRC = BUILD / "claude-code-cheatsheet"
CS_OUT = ROOT / "claude-code-cheatsheet"
SK_SRC = BUILD / "claude-code-built-in-skills"
SK_OUT = ROOT / "claude-code-built-in-skills"
CX_SRC = BUILD / "codex-cheatsheet"
CX_OUT = ROOT / "codex-cheatsheet"
MEM_SRC = BUILD / "agent-memory"
MEM_OUT = ROOT / "agent-memory"
CMP_SRC = BUILD / "claude-code-vs-codex"
CMP_OUT = ROOT / "claude-code-vs-codex"


def swap(text, old, new, label):
    if text.count(old) != 1:
        raise SystemExit("expected exactly one %s anchor, found %d" % (label, text.count(old)))
    return text.replace(old, new)


def esc(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


# The memory page's prose is authored as HTML in memory-data.json so it can carry inline markup,
# and the Markdown twin is derived from it rather than written a second time. Only this subset is
# allowed, so the conversion stays exact: <p>, <code>, <b>, <em>, <a href>, <ul>/<li>.
MD_INLINE = [("<code>", "`"), ("</code>", "`"), ("<b>", "**"), ("</b>", "**"),
             ("<em>", "*"), ("</em>", "*")]


def to_md(html):
    import re
    unknown = sorted({t.lower() for t in re.findall(r"</?([a-zA-Z]+)", html)}
                     - {"p", "code", "b", "em", "a", "ul", "li"})
    if unknown:
        raise SystemExit("memory prose uses unsupported tags: %s" % ", ".join(unknown))

    text = re.sub(r'<a href="([^"]+)">(.*?)</a>', r"[\2](\1)", html, flags=re.S)
    for tag, mark in MD_INLINE:
        text = text.replace(tag, mark)
    text = text.replace("<ul>", "\n").replace("</ul>", "\n")
    text = re.sub(r"\s*<li>\s*", "\n- ", text)
    text = text.replace("</li>", "")
    text = re.sub(r"\s*</p>\s*<p>\s*", "\n\n", text)
    text = re.sub(r"\s*</?p>\s*", "", text)
    text = (text.replace("&mdash;", "\u2014").replace("&ndash;", "\u2013")
            .replace("&hellip;", "\u2026").replace("&lt;", "<").replace("&gt;", ">")
            .replace("&quot;", '"').replace("&nbsp;", " ").replace("&amp;", "&"))
    return re.sub(r"\n{3,}", "\n\n", re.sub(r"[ \t]+", " ", text)).strip()


# ============================================================ chrome shared by every page

COFFEE_CSS = """
  /* ---------- support ---------- */
  .masthead-top { display:flex; flex-wrap:wrap; align-items:baseline; gap:var(--sp-3); }
  .masthead-top .eyebrow { flex:1 1 260px; margin-bottom:0; }

  .coffee {
    display:inline-flex; align-items:center; gap:7px; flex:0 0 auto;
    font-family:var(--mono); font-size:11px; letter-spacing:.12em; text-transform:uppercase;
    color:var(--fam-cli); text-decoration:none; white-space:nowrap;
    border:1px solid color-mix(in srgb, var(--fam-cli) 40%, var(--rule));
    background:color-mix(in srgb, var(--fam-cli) 7%, var(--surface));
    border-radius:3px; padding:7px 11px;
    transition:background .12s ease, border-color .12s ease;
  }
  .coffee:hover {
    background:color-mix(in srgb, var(--fam-cli) 16%, var(--surface));
    border-color:var(--fam-cli);
  }
  .coffee:focus-visible { outline:2px solid var(--fam-cli); outline-offset:2px; }
  .coffee .cup { font-size:13px; }

  .support {
    display:flex; flex-wrap:wrap; align-items:center; gap:var(--sp-4);
    background:var(--surface); border:1px solid var(--rule);
    border-left:2px solid var(--fam-cli); border-radius:3px;
    padding:var(--sp-4); margin-top:var(--sp-6);
  }
  .support p { margin:0; flex:1 1 340px; font-size:13.5px; color:var(--muted); }
  .support b { color:var(--ink); font-weight:600; }
  .support code { font-family:var(--mono); font-size:.9em; color:var(--ink); }
  .support .coffee { font-size:12px; padding:9px 14px; }

  .machine {
    display:flex; flex-wrap:wrap; align-items:baseline; gap:var(--sp-2) var(--sp-3);
    margin-top:var(--sp-4); padding-top:var(--sp-3); border-top:1px solid var(--rule);
    font-family:var(--mono); font-size:11.5px; letter-spacing:.04em; color:var(--faint);
  }
  .machine b { color:var(--muted); font-weight:500; text-transform:uppercase; letter-spacing:.12em; }
  .machine a { color:var(--accent); text-decoration:none; border-bottom:1px solid transparent; }
  .machine a:hover { border-bottom-color:currentColor; }


  .eyebrow .home { color:var(--muted); text-decoration:none; border-bottom:1px solid var(--rule); }
  .eyebrow .home:hover { color:var(--accent); border-bottom-color:currentColor; }
"""

# Both anchors carry the page's build number rather than a literal, so bumping it in siteconf
# fails the swap loudly instead of quietly publishing a masthead that still names the old one.
# The fix when it fires is to update the eyebrow in that page source to match.
def masthead(build, tail="extracted from the installed binary"):
    old = """  <header class="masthead">
    <p class="eyebrow">Reference &middot; build {build} &middot; {tail}</p>""".format(
        build=build, tail=tail)

    new = """  <header class="masthead">
    <div class="masthead-top">
      <p class="eyebrow"><a href="../" class="home">AI Snacks</a> &middot; build {build} &middot; {tail}</p>
      <a class="coffee" href="{bmc}" target="_blank" rel="noopener noreferrer">
        <span class="cup" aria-hidden="true">&#9749;</span>Buy me a coffee</a>
    </div>""".format(build=build, tail=tail, bmc=S.BMC)
    return old, new


def support(pitch):
    return """
  <div class="support">
    <p>{pitch}</p>
    <a class="coffee" href="{bmc}" target="_blank" rel="noopener noreferrer">
      <span class="cup" aria-hidden="true">&#9749;</span>Buy me a coffee</a>
  </div>

  <footer>""".format(pitch=pitch, bmc=S.BMC)


def machine(links, tail):
    rows = "\n".join('      <a href="%s">%s</a>' % (href, name) for name, href in links)
    return """
    <p class="machine">
      <b>Machine-readable</b>
{rows}
      <span>&mdash; {tail}</span>
    </p>
  </footer>""".format(rows=rows, tail=tail)


SUPPORT = support(
    """<b>Found this useful?</b> Every entry here was parsed out of the shipped binary, probed
      against the running CLI to see whether it is actually reachable, and matched to its page in
      the official docs. If it saved you a trip through <code>/help</code>, you can put a coffee
      toward keeping it current with the next build.""")

MACHINE = machine([("commands.json", "commands.json"), ("commands.md", "commands.md"),
                   ("llms.txt", "../llms.txt")],
                  "the same data, for scripts and agents.")


def cheatsheet_ld():
    return [
        {
            "@context": "https://schema.org",
            "@type": "TechArticle",
            "@id": S.CHEATSHEET + "#article",
            "headline": "Claude Code Command Index",
            "name": S.CS_TITLE,
            "description": S.CS_DESC,
            "url": S.CHEATSHEET,
            "mainEntityOfPage": {"@type": "WebPage", "@id": S.CHEATSHEET},
            "inLanguage": "en",
            "datePublished": S.UPDATED,
            "dateModified": S.UPDATED,
            "author": {"@type": "Person", "name": S.AUTHOR,
                       "url": "https://github.com/" + S.AUTHOR},
            "publisher": {"@type": "Organization", "name": S.SITE_NAME, "url": S.BASE},
            "isPartOf": {"@type": "CollectionPage", "@id": S.BASE + "#collection"},
            "image": S.CHEATSHEET + "og.png",
            "about": {
                "@type": "SoftwareApplication",
                "name": "Claude Code",
                "applicationCategory": "DeveloperApplication",
                "operatingSystem": "macOS, Linux, Windows",
                "softwareVersion": S.BUILD,
                "url": "https://code.claude.com/docs/",
                "publisher": {"@type": "Organization", "name": "Anthropic"},
            },
            "keywords": ("Claude Code, slash commands, CLI flags, bundled skills, command "
                         "reference, cheat sheet, Anthropic, terminal, AI coding agent"),
            "articleSection": ["Slash commands", "Bundled skills", "CLI subcommands", "CLI flags"],
        },
        {
            "@context": "https://schema.org",
            "@type": "Dataset",
            "@id": S.CHEATSHEET + "#dataset",
            "name": "Claude Code %s command and flag inventory" % S.BUILD,
            "description": ("Structured inventory of every slash command, bundled skill, CLI "
                            "subcommand and launch flag registered by Claude Code build %s, with "
                            "descriptions, aliases, availability and documentation links."
                            % S.BUILD),
            "url": S.CHEATSHEET,
            "license": "https://creativecommons.org/licenses/by/4.0/",
            "creator": {"@type": "Person", "name": S.AUTHOR},
            "dateModified": S.UPDATED,
            "isAccessibleForFree": True,
            "measurementTechnique": ("Static extraction from the compiled binary, plus runtime "
                                     "probing of the command registry"),
            "variableMeasured": ["command name", "family", "description", "aliases",
                                 "argument hint", "CLI registration status", "documentation URL"],
            "distribution": [
                {"@type": "DataDownload", "encodingFormat": "application/json",
                 "contentUrl": S.CHEATSHEET + "commands.json"},
                {"@type": "DataDownload", "encodingFormat": "text/markdown",
                 "contentUrl": S.CHEATSHEET + "commands.md"},
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": S.SITE_NAME, "item": S.BASE},
                {"@type": "ListItem", "position": 2, "name": "Claude Code Command Index",
                 "item": S.CHEATSHEET},
            ],
        },
    ]


HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta name="author" content="{author}">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#F6F7FA" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0F1117" media="(prefers-color-scheme: dark)">

<meta property="og:type" content="article">
<meta property="og:site_name" content="{site}">
<meta property="og:locale" content="en_US">
<meta property="og:title" content="{ogtitle}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{url}og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{ogalt}">
<meta property="article:published_time" content="{updated}">
<meta property="article:modified_time" content="{updated}">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{ogtitle}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{url}og.png">

{alts}
<link rel="sitemap" type="application/xml" href="../sitemap.xml">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 \
100 100'%3E%3Ctext x='50' y='54' font-size='76' text-anchor='middle' dominant-baseline='central'\
%3E{icon}%3C/text%3E%3C/svg%3E">
{ld}"""


def page_head(title, desc, url, ld, ogtitle, ogalt, icon, alts, updated=S.UPDATED):
    links = "\n".join('<link rel="alternate" type="%s" href="%s" title="%s">' % a for a in alts)
    body = json.dumps(ld, indent=2, ensure_ascii=False).replace("</", "<\\/")
    return HEAD.format(title=title, desc=desc, url=url, author=S.AUTHOR, site=S.SITE_NAME,
                       build=S.BUILD, updated=updated, ogtitle=ogtitle, ogalt=ogalt,
                       icon=icon, alts=links,
                       ld='<script type="application/ld+json">\n%s\n</script>\n' % body)


def build_cheatsheet_page(prerender):
    frag = (CS_SRC / "claude-code-commands.html").read_text(encoding="utf-8")

    if prerender["cardCount"] != 143 or prerender["flagcount"] != "57":
        raise SystemExit("prerender.json looks wrong: %d cards, %s flags"
                         % (prerender["cardCount"], prerender["flagcount"]))

    frag = swap(frag, '<main id="sections"></main>',
                '<main id="sections">' + prerender["sections"] + "</main>", "sections host")
    frag = swap(frag, '<tbody id="flagbody"></tbody>',
                '<tbody id="flagbody">' + prerender["flagbody"] + "</tbody>", "flags host")
    frag = swap(frag, '<span class="n" id="flagcount"></span>',
                '<span class="n" id="flagcount">%s</span>' % prerender["flagcount"], "flag count")
    for key, value in prerender["stats"].items():
        frag = swap(frag, '<b id="s-%s">0</b>' % key,
                    '<b id="s-%s">%s</b>' % (key, value), "stat " + key)

    frag = swap(frag, *masthead(S.BUILD), label="masthead")
    frag = swap(frag, "\n  <footer>", SUPPORT, "footer")
    frag = swap(frag, "\n  </footer>", MACHINE, "machine-readable")
    frag = swap(frag, "\n  @media (prefers-reduced-motion",
                COFFEE_CSS + "  @media (prefers-reduced-motion", "css")
    frag = swap(frag, "<title>Claude Code Command Index — v%s</title>\n" % S.BUILD, "",
                "old title")

    head = page_head(
        title=S.CS_TITLE, desc=S.CS_DESC, url=S.CHEATSHEET, ld=cheatsheet_ld(),
        ogtitle="Claude Code Command Index — every command in build %s" % S.BUILD,
        ogalt="Claude Code Command Index — 143 commands, 57 flags, build %s" % S.BUILD,
        icon="%E2%8C%98",
        alts=[("text/markdown", "commands.md", "Markdown version of this page"),
              ("application/json", "commands.json",
               "JSON dataset of every command and flag")])

    cut = frag.index("</style>") + len("</style>")
    return head + frag[:cut] + "\n</head>\n<body>\n" + frag[cut:].lstrip("\n") + "\n</body>\n</html>\n"


# ============================================================ the bundled-skills page

SK_SUPPORT = support(
    """<b>Found this useful?</b> Every prompt here was read out of the shipped binary and
      reproduced in full, including the ones the CLI never puts in front of you. If seeing what
      the model is actually told saved you an afternoon of guessing, you can put a coffee toward
      keeping it current with the next build.""")

SK_MACHINE = machine([("skills.json", "skills.json"), ("skills.md", "skills.md"),
                      ("llms.txt", "../llms.txt")],
                     "every prompt as plain text, for scripts and agents.")

SECTION_BLURB = {
    "code": "Reviewing a diff, cleaning it up, proving it works, and running the thing.",
    "artifact": "Publishing an HTML page to claude.ai, and the house style it is held to.",
    "config": "Reading and rewriting your own Claude Code setup.",
    "auto": "Doing it again later, or on a schedule, or in the cloud.",
    "ref": "Documentation the model loads instead of guessing from training data.",
    "design": "Claude Design and the Chrome extension.",
    "cowork": "Cowork's own onboarding and plugin authoring.",
    "other": "Everything that did not fit another shelf.",
}

SECTION_SHORT = {
    "code": "Code", "artifact": "Artifacts", "config": "Config", "auto": "Scheduling",
    "ref": "Reference", "design": "Design", "cowork": "Cowork", "other": "Other",
}


def skill_card(item, key):
    name = item["name"]
    anchor = "skill-" + name
    tags = []
    if item["userInvocable"]:
        tags.append(('slash', '/' + name))
    if item["modelInvocable"]:
        tags.append(('auto', 'model picks it'))
    if not item["userInvocable"]:
        tags.append(('gate', 'internal'))
    if item["conditional"]:
        tags.append(('gate', 'conditional'))

    meta = []
    if item["argumentHint"]:
        meta.append("<span><b>Takes</b> <code>%s</code></span>" % esc(item["argumentHint"]))
    if item["allowedTools"]:
        meta.append("<span><b>Tools</b> <code>%s</code></span>"
                    % esc(", ".join(item["allowedTools"])))
    if item["gates"]:
        meta.append("<span><b>Flag</b> <code>%s</code></span>" % esc(", ".join(item["gates"])))
    if item["env"]:
        meta.append("<span><b>Env</b> <code>%s</code></span>" % esc(", ".join(item["env"])))
    meta.append("<span><b>Prompt</b> %s words</span>" % format(len(item["prompt"].split()), ","))

    when = ""
    if item["whenToUse"]:
        when = '\n        <p class="desc"><b>When:</b> %s</p>' % esc(item["whenToUse"])

    return """      <article class="skill" id="{anchor}" data-key="{key}">
        <div class="skill-top">
          <h3 class="skill-name"><span class="slash">/</span>{name}</h3>
          <a class="anchor" href="#{anchor}" aria-label="Link to {name}">#</a>
          <span class="tags">{tags}</span>
        </div>
        <p class="desc">{desc}</p>{when}
        <p class="meta">{meta}</p>
        <details class="prompt">
          <summary>Read the prompt <span class="how">&mdash; {how}</span></summary>
          <div class="prompt-body">
            <button class="copy" type="button">Copy</button>
            <pre>{prompt}</pre>
          </div>
        </details>
      </article>
""".format(anchor=anchor, key=key, name=esc(name),
           tags="".join('<span class="tag %s">%s</span>' % (c, esc(t)) for c, t in tags),
           desc=esc(item["description"] or item["menu"]), when=when,
           meta="\n          ".join(meta), how=esc(item["promptMethod"]),
           prompt=esc(item["prompt"]))


def build_skills_page(data):
    frag = (SK_SRC / "skills.html").read_text(encoding="utf-8")
    totals = data["totals"]

    if totals["skills"] != 35:
        raise SystemExit("skills-data.json has %d skills, expected 35" % totals["skills"])

    body = []
    for sec in data["sections"]:
        key = sec["key"]
        body.append("""    <section class="sec" data-key="{key}" data-short="{short}" id="sec-{key}">
      <div class="sec-head">
        <h2>{title}</h2>
        <p>{blurb} {n} skills.</p>
      </div>
{cards}    </section>
""".format(key=key, short=esc(SECTION_SHORT.get(key, key)), title=esc(sec["title"]),
           blurb=esc(SECTION_BLURB.get(key, "")), n=len(sec["items"]),
           cards="".join(skill_card(i, key) for i in sec["items"])))

    words = sum(len(i["prompt"].split()) for s in data["sections"] for i in s["items"])
    stats = {"skills": totals["skills"], "words": format(words, ","),
             "verbatim": totals["embedded"], "gated": totals["conditional"]}

    frag = swap(frag, '<main id="skills"></main>',
                '<main id="skills">\n' + "".join(body) + "  </main>", "skills host")
    for key, value in stats.items():
        frag = swap(frag, '<b id="s-%s">0</b>' % key,
                    '<b id="s-%s">%s</b>' % (key, value), "stat " + key)

    frag = swap(frag, *masthead(S.BUILD), label="masthead")
    frag = swap(frag, "\n  <footer>", SK_SUPPORT, "footer")
    frag = swap(frag, "\n  </footer>", SK_MACHINE, "machine-readable")
    frag = swap(frag, "\n  @media (prefers-reduced-motion",
                COFFEE_CSS + "  @media (prefers-reduced-motion", "css")
    frag = swap(frag, "<title>Claude Code Bundled Skills — v%s</title>\n" % S.BUILD, "",
                "old title")

    head = page_head(
        title=S.SK_TITLE, desc=S.SK_DESC, url=S.SKILLS, ld=skills_ld(data),
        ogtitle="Claude Code bundled skills — all %d prompts, in full" % totals["skills"],
        ogalt="Claude Code bundled skills — %d prompts read out of build %s"
              % (totals["skills"], S.BUILD),
        icon="%F0%9F%A7%A9",
        alts=[("text/markdown", "skills.md", "Every prompt as one Markdown file"),
              ("application/json", "skills.json",
               "JSON dataset of every bundled skill and its prompt")])

    cut = frag.index("</style>") + len("</style>")
    return head + frag[:cut] + "\n</head>\n<body>\n" + frag[cut:].lstrip("\n") + "\n</body>\n</html>\n"


def skills_ld(data):
    totals = data["totals"]
    return [
        {
            "@context": "https://schema.org",
            "@type": "TechArticle",
            "@id": S.SKILLS + "#article",
            "headline": "Claude Code Bundled Skills",
            "name": S.SK_TITLE,
            "description": S.SK_DESC,
            "url": S.SKILLS,
            "mainEntityOfPage": {"@type": "WebPage", "@id": S.SKILLS},
            "inLanguage": "en",
            "datePublished": S.UPDATED,
            "dateModified": S.UPDATED,
            "author": {"@type": "Person", "name": S.AUTHOR,
                       "url": "https://github.com/" + S.AUTHOR},
            "publisher": {"@type": "Organization", "name": S.SITE_NAME, "url": S.BASE},
            "isPartOf": {"@type": "CollectionPage", "@id": S.BASE + "#collection"},
            "image": S.SKILLS + "og.png",
            "about": {
                "@type": "SoftwareApplication",
                "name": "Claude Code",
                "applicationCategory": "DeveloperApplication",
                "operatingSystem": "macOS, Linux, Windows",
                "softwareVersion": S.BUILD,
                "url": "https://code.claude.com/docs/",
                "publisher": {"@type": "Organization", "name": "Anthropic"},
            },
            "keywords": ("Claude Code, bundled skills, skill prompts, system prompt, "
                         "SKILL.md, Anthropic, prompt engineering, AI coding agent"),
            "articleSection": [s["title"] for s in data["sections"]],
        },
        {
            "@context": "https://schema.org",
            "@type": "Dataset",
            "@id": S.SKILLS + "#dataset",
            "name": "Claude Code %s bundled skill prompts" % S.BUILD,
            "description": ("The full prompt text of all %d skills bundled inside Claude Code "
                            "build %s, with the description and gating metadata each skill "
                            "carries in the binary." % (totals["skills"], S.BUILD)),
            "url": S.SKILLS,
            "license": "https://creativecommons.org/licenses/by/4.0/",
            "creator": {"@type": "Person", "name": S.AUTHOR},
            "dateModified": S.UPDATED,
            "isAccessibleForFree": True,
            "measurementTechnique": ("Static extraction of the JavaScript bundle embedded in the "
                                     "compiled binary; each prompt resolved back to its source "
                                     "string without executing the program"),
            "variableMeasured": ["skill name", "menu description", "model-facing description",
                                 "when-to-use hint", "argument hint", "allowed tools",
                                 "feature gate", "prompt text", "how the prompt is assembled"],
            "distribution": [
                {"@type": "DataDownload", "encodingFormat": "application/json",
                 "contentUrl": S.SKILLS + "skills.json"},
                {"@type": "DataDownload", "encodingFormat": "text/markdown",
                 "contentUrl": S.SKILLS + "skills.md"},
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": S.SITE_NAME, "item": S.BASE},
                {"@type": "ListItem", "position": 2, "name": "Claude Code Bundled Skills",
                 "item": S.SKILLS},
            ],
        },
    ]


# ============================================================ the Codex CLI page

CX_SUPPORT = support(
    """<b>Found this useful?</b> Every entry here was read out of the running CLI — the slash
      commands off the picker itself, the subcommand tree off <code>codex --help</code>, and the
      feature table off <code>codex features list</code>. If it saved you a lap through
      <code>--help</code>, you can put a coffee toward keeping it current with the next build.""")

CX_MACHINE = machine([("codex-commands.json", "codex-commands.json"),
                      ("codex-commands.md", "codex-commands.md"),
                      ("llms.txt", "../llms.txt")],
                     "the same data, for scripts and agents.")


def codex_ld(counts):
    return [
        {
            "@context": "https://schema.org",
            "@type": "TechArticle",
            "@id": S.CODEX + "#article",
            "headline": "Codex CLI Command Index",
            "name": S.CX_TITLE,
            "description": S.CX_DESC,
            "url": S.CODEX,
            "mainEntityOfPage": {"@type": "WebPage", "@id": S.CODEX},
            "inLanguage": "en",
            "datePublished": S.CODEX_UPDATED,
            "dateModified": S.CODEX_UPDATED,
            "author": {"@type": "Person", "name": S.AUTHOR,
                       "url": "https://github.com/" + S.AUTHOR},
            "publisher": {"@type": "Organization", "name": S.SITE_NAME, "url": S.BASE},
            "isPartOf": {"@type": "CollectionPage", "@id": S.BASE + "#collection"},
            "image": S.CODEX + "og.png",
            "about": {
                "@type": "SoftwareApplication",
                "name": "OpenAI Codex CLI",
                "applicationCategory": "DeveloperApplication",
                "operatingSystem": "macOS, Linux, Windows",
                "softwareVersion": S.CODEX_BUILD,
                "url": "https://learn.chatgpt.com/docs/codex/cli",
                "publisher": {"@type": "Organization", "name": "OpenAI"},
            },
            "keywords": ("Codex CLI, OpenAI Codex, slash commands, CLI flags, feature flags, "
                         "command reference, cheat sheet, terminal, AI coding agent"),
            "articleSection": ["Slash commands", "CLI subcommands", "Launch flags",
                               "Feature flags"],
        },
        {
            "@context": "https://schema.org",
            "@type": "Dataset",
            "@id": S.CODEX + "#dataset",
            "name": "OpenAI Codex CLI %s command, flag and feature inventory" % S.CODEX_BUILD,
            "description": ("Structured inventory of every slash command, subcommand, launch flag "
                            "and feature flag in OpenAI Codex CLI build %s, with descriptions, "
                            "aliases, availability and documentation links."
                            % S.CODEX_BUILD),
            "url": S.CODEX,
            "license": "https://creativecommons.org/licenses/by/4.0/",
            "creator": {"@type": "Person", "name": S.AUTHOR},
            "dateModified": S.CODEX_UPDATED,
            "isAccessibleForFree": True,
            "measurementTechnique": ("Runtime probing of the installed CLI: the TUI slash-command "
                                     "picker driven in a pseudo-terminal, a recursive walk of "
                                     "`codex --help`, and `codex features list`"),
            "variableMeasured": ["command name", "family", "description", "aliases",
                                 "argument hint", "registration status", "documentation URL",
                                 "feature stage", "feature enabled state"],
            "distribution": [
                {"@type": "DataDownload", "encodingFormat": "application/json",
                 "contentUrl": S.CODEX + "codex-commands.json"},
                {"@type": "DataDownload", "encodingFormat": "text/markdown",
                 "contentUrl": S.CODEX + "codex-commands.md"},
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": S.SITE_NAME, "item": S.BASE},
                {"@type": "ListItem", "position": 2, "name": "Codex CLI Command Index",
                 "item": S.CODEX},
            ],
        },
    ]


def build_codex_page(prerender, counts):
    frag = (CX_SRC / "codex-commands.html").read_text(encoding="utf-8")

    if prerender["cardCount"] != 122 or prerender["flagcount"] != "21" \
            or prerender["featcount"] != "100":
        raise SystemExit("codex prerender.json looks wrong: %d cards, %s flags, %s features"
                         % (prerender["cardCount"], prerender["flagcount"],
                            prerender["featcount"]))

    frag = swap(frag, '<main id="sections"></main>',
                '<main id="sections">' + prerender["sections"] + "</main>", "sections host")
    frag = swap(frag, '<tbody id="flagbody"></tbody>',
                '<tbody id="flagbody">' + prerender["flagbody"] + "</tbody>", "flags host")
    frag = swap(frag, '<tbody id="featbody"></tbody>',
                '<tbody id="featbody">' + prerender["featbody"] + "</tbody>", "features host")
    frag = swap(frag, '<span class="n" id="flagcount"></span>',
                '<span class="n" id="flagcount">%s</span>' % prerender["flagcount"], "flag count")
    frag = swap(frag, '<span class="n" id="featcount"></span>',
                '<span class="n" id="featcount">%s</span>' % prerender["featcount"],
                "feature count")
    for key, value in prerender["stats"].items():
        frag = swap(frag, '<b id="s-%s">0</b>' % key,
                    '<b id="s-%s">%s</b>' % (key, value), "stat " + key)

    frag = swap(frag, *masthead(S.CODEX_BUILD), label="masthead")
    frag = swap(frag, "\n  <footer>", CX_SUPPORT, "footer")
    frag = swap(frag, "\n  </footer>", CX_MACHINE, "machine-readable")
    frag = swap(frag, "\n  @media (prefers-reduced-motion",
                COFFEE_CSS + "  @media (prefers-reduced-motion", "css")
    frag = swap(frag, "<title>Codex CLI Command Index — v%s</title>\n" % S.CODEX_BUILD, "",
                "old title")

    head = page_head(
        title=S.CX_TITLE, desc=S.CX_DESC, url=S.CODEX, ld=codex_ld(counts),
        ogtitle="Codex CLI Command Index — every command in build %s" % S.CODEX_BUILD,
        ogalt="Codex CLI Command Index — %d commands, %d flags, build %s"
              % (counts["total"], counts["flags"], S.CODEX_BUILD),
        icon="%E2%9A%A1", updated=S.CODEX_UPDATED,
        alts=[("text/markdown", "codex-commands.md", "Markdown version of this page"),
              ("application/json", "codex-commands.json",
               "JSON dataset of every command, flag and feature")])

    cut = frag.index("</style>") + len("</style>")
    return head + frag[:cut] + "\n</head>\n<body>\n" + frag[cut:].lstrip("\n") + "\n</body>\n</html>\n"


# ============================================================ the auto-memory page

MEM_SUPPORT = support(
    """<b>Found this useful?</b> Both mechanisms here were read out of the installed binaries and
      checked against the stores they actually write on disk, because neither tool's documentation
      describes the file layout. If it saved you an afternoon of guessing where your agent's memory
      goes, you can put a coffee toward keeping it current with the next build.""")

MEM_MACHINE = machine([("memory.json", "memory.json"), ("memory.md", "memory.md"),
                       ("llms.txt", "../llms.txt")],
                      "the same comparison, for scripts and agents.")


def evidence_html(items):
    out = []
    for ev in items:
        out.append("""        <div class="ev">
          <div class="ev-body">
            <button class="copy" type="button">Copy</button>
            <pre>{quote}</pre>
          </div>
          <span class="src"><b>Source</b> {source}</span>
        </div>
""".format(quote=esc(ev["quote"]), source=esc(ev["source"])))
    return "".join(out)


def tool_html(tool):
    steps = []
    for n, stage in enumerate(tool["stages"], 1):
        steps.append("""      <article class="step" id="{sid}">
        <div class="step-top">
          <span class="step-n">{n:02d}</span>
          <h3>{title}</h3>
          <a class="anchor" href="#{sid}" aria-label="Link to {title}">#</a>
        </div>
        {body}
{ev}      </article>
""".format(sid=stage["id"], n=n, title=esc(stage["title"]), body=stage["body"],
           ev=evidence_html(stage.get("evidence", []))))

    rows = "".join(
        """          <tr><td class="p">{path}</td><td class="r">{role}</td>
            <td class="r">{writer}</td><td class="r">{loaded}</td></tr>
""".format(path=esc(f["path"]), role=f["role"], writer=f["writer"], loaded=f["loaded"])
        for f in tool["files"])

    return """    <section class="tool" id="{key}" style="--tc:var(--fam-{key})">
      <div class="tool-head">
        <p class="kicker">{kicker}</p>
        <h2>{title}</h2>
        {intro}
      </div>
{steps}
      <div class="files">
        <table>
          <thead>
            <tr><th scope="col">Path</th><th scope="col">What it holds</th>
              <th scope="col">Written by</th><th scope="col">Reaches the model</th></tr>
          </thead>
          <tbody>
{rows}          </tbody>
        </table>
      </div>
    </section>
""".format(key=tool["key"], kicker=esc(tool["kicker"]), title=esc(tool["title"]),
           intro=tool["intro"], steps="".join(steps), rows=rows)


def comparison_html(rows):
    body = "".join(
        """          <tr id="{rid}">
            <th scope="row">{aspect}<span class="q">{question}</span></th>
            <td class="cc">{claude}</td>
            <td class="cx">{codex}</td>
          </tr>
{note}""".format(rid=r["id"], aspect=esc(r["aspect"]), question=esc(r["question"]),
                 claude=r["claude"], codex=r["codex"],
                 note=('          <tr class="noterow"><td colspan="3">%s</td></tr>\n' % r["note"])
                 if r.get("note") else "")
        for r in rows)

    return """    <section class="closing" id="side-by-side">
      <h2>Side by side</h2>
      <div class="cmp">
        <table>
          <thead>
            <tr><th scope="col" class="as">Dimension</th>
              <th scope="col" class="cc">Claude Code</th>
              <th scope="col" class="cx">Codex CLI</th></tr>
          </thead>
          <tbody>
{body}          </tbody>
        </table>
      </div>
    </section>
""".format(body=body)


def build_memory_page(data):
    frag = (MEM_SRC / "memory.html").read_text(encoding="utf-8")

    if len(data["tools"]) != 2:
        raise SystemExit("memory-data.json describes %d tools, expected 2" % len(data["tools"]))

    toc = ['      <li><a href="#%s">%s</a></li>' % (t["key"], esc(t["name"])) for t in data["tools"]]
    toc.append('      <li><a href="#side-by-side">Side by side</a></li>')
    toc.append('      <li><a href="#what-it-means">What it means in practice</a></li>')

    takeaways = "".join(
        """      <div class="take" id="{tid}">
        <h3>{title}</h3>
        {body}
      </div>
""".format(tid=t["id"], title=esc(t["title"]), body=t["body"]) for t in data["takeaways"])

    method = "".join("      %s</p>\n" % para
                     for para in data["method"].split("</p>") if para.strip())

    body = ('    <div class="method">\n      <h2>How this was established</h2>\n'
            + method + "    </div>\n\n"
            + '    <ul class="toc">\n%s\n    </ul>\n\n' % "\n".join(toc)
            + "\n".join(tool_html(t) for t in data["tools"])
            + "\n" + comparison_html(data["comparison"])
            + """
    <section class="closing" id="what-it-means">
      <h2>What it means in practice</h2>
{takeaways}    </section>
""".format(takeaways=takeaways))

    frag = swap(frag, '<main id="memory"></main>',
                '<main id="memory">\n' + body + "  </main>", "memory host")
    frag = swap(frag, *masthead("%s + codex %s" % (S.BUILD, S.CODEX_BUILD),
                                "read out of both installed binaries"), label="masthead")
    frag = swap(frag, "\n  <footer>", MEM_SUPPORT, "footer")
    frag = swap(frag, "\n  </footer>", MEM_MACHINE, "machine-readable")
    frag = swap(frag, "\n  @media (prefers-reduced-motion",
                COFFEE_CSS + "  @media (prefers-reduced-motion", "css")
    frag = swap(frag, "<title>Agent Memory — v%s + %s</title>\n" % (S.BUILD, S.CODEX_BUILD), "",
                "old title")

    head = page_head(
        title=S.MEM_TITLE, desc=S.MEM_DESC, url=S.MEMORY, ld=memory_ld(data),
        ogtitle="Auto-memory in Claude Code and Codex — how each one remembers",
        ogalt="Auto-memory compared — Claude Code %s and Codex CLI %s, read from both binaries"
              % (S.BUILD, S.CODEX_BUILD),
        icon="%F0%9F%A7%A0", updated=S.MEM_UPDATED,
        alts=[("text/markdown", "memory.md", "Markdown version of this page"),
              ("application/json", "memory.json",
               "JSON dataset of both mechanisms and the comparison")])

    cut = frag.index("</style>") + len("</style>")
    return head + frag[:cut] + "\n</head>\n<body>\n" + frag[cut:].lstrip("\n") + "\n</body>\n</html>\n"


def memory_ld(data):
    return [
        {
            "@context": "https://schema.org",
            "@type": "TechArticle",
            "@id": S.MEMORY + "#article",
            "headline": "Auto-Memory in Claude Code and Codex",
            "name": S.MEM_TITLE,
            "description": S.MEM_DESC,
            "url": S.MEMORY,
            "mainEntityOfPage": {"@type": "WebPage", "@id": S.MEMORY},
            "inLanguage": "en",
            "datePublished": S.MEM_UPDATED,
            "dateModified": S.MEM_UPDATED,
            "author": {"@type": "Person", "name": S.AUTHOR,
                       "url": "https://github.com/" + S.AUTHOR},
            "publisher": {"@type": "Organization", "name": S.SITE_NAME, "url": S.BASE},
            "isPartOf": {"@type": "CollectionPage", "@id": S.BASE + "#collection"},
            "image": S.MEMORY + "og.png",
            "about": [
                {"@type": "SoftwareApplication", "name": "Claude Code",
                 "applicationCategory": "DeveloperApplication",
                 "operatingSystem": "macOS, Linux, Windows", "softwareVersion": S.BUILD,
                 "url": "https://code.claude.com/docs/",
                 "publisher": {"@type": "Organization", "name": "Anthropic"}},
                {"@type": "SoftwareApplication", "name": "OpenAI Codex CLI",
                 "applicationCategory": "DeveloperApplication",
                 "operatingSystem": "macOS, Linux, Windows", "softwareVersion": S.CODEX_BUILD,
                 "url": "https://learn.chatgpt.com/docs/codex/cli",
                 "publisher": {"@type": "Organization", "name": "OpenAI"}},
            ],
            "keywords": ("agent memory, auto memory, Claude Code memory, Codex memories, "
                         "MEMORY.md, AGENTS.md, CLAUDE.md, persistent context, AI coding agent"),
            "articleSection": [t["name"] for t in data["tools"]] + ["Side by side",
                                                                   "What it means in practice"],
        },
        {
            "@context": "https://schema.org",
            "@type": "Dataset",
            "@id": S.MEMORY + "#dataset",
            "name": "Auto-memory mechanisms of Claude Code %s and Codex CLI %s"
                    % (S.BUILD, S.CODEX_BUILD),
            "description": ("Structured description of how each tool writes, stores and recalls "
                            "memory across sessions — the on-disk artefacts, the prompt text that "
                            "governs them, and a dimension-by-dimension comparison."),
            "url": S.MEMORY,
            "license": "https://creativecommons.org/licenses/by/4.0/",
            "creator": {"@type": "Person", "name": S.AUTHOR},
            "dateModified": S.MEM_UPDATED,
            "isAccessibleForFree": True,
            "measurementTechnique": ("Static extraction of prompt and path literals from both "
                                     "installed binaries, corroborated against the stores each "
                                     "tool writes on disk"),
            "variableMeasured": ["storage location", "what writes a memory", "when it is written",
                                 "what is loaded at session start", "how a memory is recalled",
                                 "scope", "user control", "file format"],
            "distribution": [
                {"@type": "DataDownload", "encodingFormat": "application/json",
                 "contentUrl": S.MEMORY + "memory.json"},
                {"@type": "DataDownload", "encodingFormat": "text/markdown",
                 "contentUrl": S.MEMORY + "memory.md"},
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": S.SITE_NAME, "item": S.BASE},
                {"@type": "ListItem", "position": 2, "name": "Auto-Memory in Claude Code and Codex",
                 "item": S.MEMORY},
            ],
        },
    ]


def build_memory_data(data):
    payload = {
        "name": "Auto-memory mechanisms compared",
        "description": ("How Claude Code build %s and OpenAI Codex CLI build %s each write, store "
                        "and recall memory across sessions." % (S.BUILD, S.CODEX_BUILD)),
        "claudeCodeBuild": S.BUILD,
        "codexBuild": S.CODEX_BUILD,
        "generated": S.MEM_UPDATED,
        "license": "CC BY 4.0",
        "canonicalPage": S.MEMORY,
        "source": {
            "method": to_md(data["method"]),
            "claudeBinary": "~/.local/share/claude/versions/%s" % S.BUILD,
            "codexBinary": "codex %s (Homebrew cask)" % S.CODEX_BUILD,
        },
        "counts": {
            "dimensions": len(data["comparison"]),
            "stages": sum(len(t["stages"]) for t in data["tools"]),
            "artefacts": sum(len(t["files"]) for t in data["tools"]),
            "quotes": sum(len(s.get("evidence", []))
                          for t in data["tools"] for s in t["stages"]),
        },
        "fields": {
            "stages": "The lifecycle of one memory, in the order the tool performs it",
            "evidence": ("Verbatim strings from the binary or the on-disk store, with where each "
                         "was found; nothing here is paraphrased"),
            "files": "Every artefact the tool writes, what writes it, and whether the model sees it",
            "comparison": "One row per dimension the two mechanisms can actually be compared on",
        },
        "tools": [{
            "key": t["key"], "name": t["name"], "build": t["build"],
            "summary": to_md(t["intro"]),
            "stages": [{"id": s["id"], "title": s["title"], "body": to_md(s["body"]),
                        "evidence": s.get("evidence", []),
                        "url": S.MEMORY + "#" + s["id"]} for s in t["stages"]],
            "files": [{"path": f["path"], "holds": to_md(f["role"]),
                       "writtenBy": to_md(f["writer"]), "reachesTheModel": to_md(f["loaded"])}
                      for f in t["files"]],
        } for t in data["tools"]],
        "comparison": [{"id": r["id"], "dimension": r["aspect"], "question": r["question"],
                        "claudeCode": to_md(r["claude"]), "codexCli": to_md(r["codex"]),
                        "note": to_md(r["note"]) if r.get("note") else None,
                        "url": S.MEMORY + "#" + r["id"]} for r in data["comparison"]],
        "takeaways": [{"id": t["id"], "title": t["title"], "body": to_md(t["body"]),
                       "url": S.MEMORY + "#" + t["id"]} for t in data["takeaways"]],
    }

    md = [
        "# Auto-Memory in Claude Code and Codex",
        "",
        "> How Claude Code build %s and OpenAI Codex CLI build %s each write, store and recall "
        "memory between sessions. Both mechanisms were read out of the installed binaries and "
        "checked against the stores they actually write on disk, rather than taken from the "
        "documentation." % (S.BUILD, S.CODEX_BUILD),
        "",
        "- Canonical page: %s" % S.MEMORY,
        "- Machine-readable: %smemory.json" % S.MEMORY,
        "- Claude Code build: %s" % S.BUILD,
        "- Codex CLI build: %s" % S.CODEX_BUILD,
        "- Last updated: %s" % S.MEM_UPDATED,
        "- License: CC BY 4.0",
        "",
        "## How this was established",
        "",
        to_md(data["method"]),
        "",
    ]
    for t in data["tools"]:
        md += ["## %s" % t["title"], "", to_md(t["intro"]), ""]
        for n, s in enumerate(t["stages"], 1):
            md += ["### %d. %s" % (n, s["title"]), "", to_md(s["body"]), ""]
            for ev in s.get("evidence", []):
                md += ["```text", ev["quote"].replace("```", "​```"), "```",
                       "", "*Source: %s*" % to_md(ev["source"]), ""]
            md += ["Anchor: %s#%s" % (S.MEMORY, s["id"]), ""]
        md += ["### Where %s keeps the bytes" % t["name"], "",
               "| Path | What it holds | Written by | Reaches the model |",
               "| --- | --- | --- | --- |"]
        md += ["| `%s` | %s | %s | %s |"
               % (f["path"], to_md(f["role"]).replace("|", "\\|"),
                  to_md(f["writer"]).replace("|", "\\|"), to_md(f["loaded"]).replace("|", "\\|"))
               for f in t["files"]]
        md += [""]

    md += ["## Side by side", "",
           "| Dimension | Claude Code %s | Codex CLI %s |" % (S.BUILD, S.CODEX_BUILD),
           "| --- | --- | --- |"]
    for r in data["comparison"]:
        flat = lambda html: to_md(html).replace("\n", " ").replace("|", "\\|")  # noqa: E731
        dimension = "**%s** — %s" % (r["aspect"], r["question"].rstrip("?"))
        if r.get("note"):
            dimension += " *(%s)*" % flat(r["note"])
        md += ["| %s | %s | %s |" % (dimension, flat(r["claude"]), flat(r["codex"]))]
    md += [""]

    md += ["## What it means in practice", ""]
    for t in data["takeaways"]:
        md += ["### %s" % t["title"], "", to_md(t["body"]), ""]

    md += ["---", "",
           "From [%s](%s) by %s. If it saved you time, [buy me a coffee](%s)."
           % (S.SITE_NAME, S.BASE, S.AUTHOR, S.BMC), ""]

    return payload, "\n".join(md)


# ============================================================ the data twins

FAMILY_DESC = {
    "native": "Slash command compiled into the binary's own command registry",
    "skill": "Prompt-driven skill bundled inside the binary",
    "cli": "Subcommand of the claude executable, run in the shell",
    "hidden": "Registered and runnable but withheld from /help",
}


def md_command(c):
    bits = ["- **`%s`**" % c["name"]]
    if c["argument"]:
        bits.append("`%s`" % c["argument"])
    if c["aliases"]:
        bits.append("*(aliases: %s)*" % ", ".join("`%s`" % a for a in c["aliases"]))
    line = " ".join(bits) + " — " + c["description"].rstrip(".") + "."
    notes = []
    if c["conditional"]:
        notes.append("registered only under a feature gate")
    if not c["registeredInCli"]:
        reason = (c["unregisteredReason"] or "Not registered by the terminal CLI").rstrip(".")
        notes.append("**typing it returns `Unknown command`** — " + reason)
    if notes:
        line += " *(" + "; ".join(notes) + ")*"
    if c["docs"]:
        line += " [docs](%s)" % c["docs"]
    return line


def build_data(extract):
    sections, flags = extract["sections"], extract["flags"]
    commands = [dict(c, section=s["title"], sectionId=s["id"])
                for s in sections for c in s["commands"]]

    counts = {
        "total": len(commands),
        "native": sum(1 for c in commands if c["family"] == "native"),
        "skills": sum(1 for c in commands if c["family"] == "skill"),
        "cli": sum(1 for c in commands if c["family"] == "cli"),
        "hidden": sum(1 for c in commands if c["family"] == "hidden"),
        "flags": len(flags),
        "documented": sum(1 for c in commands if c["docs"]),
        "notRegisteredInCli": sum(1 for c in commands if not c["registeredInCli"]),
    }

    payload = {
        "name": "Claude Code command and flag inventory",
        "description": ("Every slash command, bundled skill, CLI subcommand and launch flag "
                        "registered by Claude Code build %s." % S.BUILD),
        "claudeCodeBuild": S.BUILD,
        "generated": S.UPDATED,
        "license": "CC BY 4.0",
        "canonicalPage": S.CHEATSHEET,
        "source": {
            "method": ("Names, descriptions, aliases and argument hints were parsed out of the "
                       "command registry inside the installed binary. CLI subcommands and flags "
                       "come from `claude --help` on the same build. Availability was established "
                       "by probing the running CLI, not by reading the documentation."),
            "binary": "~/.local/share/claude/versions/%s" % S.BUILD,
            "officialDocs": "https://code.claude.com/docs/",
        },
        "counts": counts,
        "families": FAMILY_DESC,
        "fields": {
            "id": "Stable anchor on the canonical page; append as #id to deep-link",
            "name": "How the command is typed (/name for slash commands, bare for CLI subcommands)",
            "family": "One of native, skill, cli, hidden — see families",
            "description": "Description string carried in the build",
            "argument": "Argument hint shown by the CLI, when it has one",
            "aliases": "Other names that resolve to the same command",
            "conditional": "Registered only when a feature gate or environment condition is met",
            "registeredInCli": ("false means the entry exists in the bundle but the terminal build "
                                "never registers it — typing it returns Unknown command"),
            "unregisteredReason": "Why it is not registered, when known",
            "docs": "Most specific official documentation page, or null if none exists",
        },
        "sections": [{"id": s["id"], "title": s["title"], "description": s["blurb"],
                      "commandCount": len(s["commands"])} for s in sections],
        "commands": [{
            "id": c["id"], "name": c["name"], "family": c["family"], "section": c["section"],
            "description": c["description"], "argument": c["argument"], "aliases": c["aliases"],
            "conditional": c["conditional"], "registeredInCli": c["registeredInCli"],
            "unregisteredReason": c["unregisteredReason"], "docs": c["docs"],
            "url": S.CHEATSHEET + "#" + c["id"],
        } for c in commands],
        "flags": flags,
    }

    md = [
        "# Claude Code Command Index",
        "",
        "> Every slash command, bundled skill, `claude` CLI subcommand and launch flag in Claude "
        "Code build %s. Extracted from the installed binary rather than the documentation, probed "
        "against the running CLI to establish what is actually reachable, and linked entry by "
        "entry to the official docs." % S.BUILD,
        "",
        "- Canonical page: %s" % S.CHEATSHEET,
        "- Machine-readable: %scommands.json" % S.CHEATSHEET,
        "- Claude Code build: %s" % S.BUILD,
        "- Last updated: %s" % S.UPDATED,
        "- License: CC BY 4.0",
        "",
        "## Totals",
        "",
        "| Group | Count | What it means |",
        "| --- | ---: | --- |",
        "| Native slash commands | %d | Compiled into the binary's own command registry |" % counts["native"],
        "| Bundled skills | %d | Prompt-driven skills shipped inside the binary |" % counts["skills"],
        "| CLI subcommands | %d | Subcommands of the `claude` executable |" % counts["cli"],
        "| Hidden commands | %d | Registered and runnable but withheld from `/help` |" % counts["hidden"],
        "| Launch flags | %d | Options passed to `claude` at startup |" % counts["flags"],
        "| Linked to official docs | %d | The rest have no official page |" % counts["documented"],
        "| Defined but not registered | %d | Typing them returns `Unknown command` |" % counts["notRegisteredInCli"],
        "",
        "## How this was established",
        "",
        "Names, descriptions, aliases and argument hints come from the command registry inside "
        "`~/.local/share/claude/versions/%s`. CLI subcommands and flags come from `claude --help` "
        "on the same build. Availability was tested, not inferred: each command was probed against "
        "the running CLI and classified by its response — real output means registered and "
        "enabled, *isn't available in this environment* means registered but gated, and *Unknown "
        "command* means never registered at all. Commands that would have executed real work were "
        "excluded from the probe rather than run." % S.BUILD,
        "",
    ]
    for s in sections:
        md += ["## %s" % s["title"], "",
               "%s. %d entries." % (s["blurb"].rstrip("."), len(s["commands"])), ""]
        md += [md_command(c) for c in s["commands"]]
        md += [""]
    md += ["## CLI flags", "", "Passed to `claude` at launch. %d in total." % len(flags), "",
           "| Flag | What it does |", "| --- | --- |"]
    md += ["| `%s` | %s |" % (f["flag"], f["description"].replace("|", "\\|")) for f in flags]
    md += ["", "---", "",
           "From [%s](%s) by %s. If it saved you time, [buy me a coffee](%s)."
           % (S.SITE_NAME, S.BASE, S.AUTHOR, S.BMC), ""]

    return payload, "\n".join(md), counts


CX_FAMILY_DESC = {
    "slash": "Slash command typed at the Codex prompt and offered by the / picker",
    "cli": "Subcommand of the codex executable, run in the shell",
    "hidden": "Named in the binary but never offered by the / picker",
}


def build_codex_data(extract):
    sections, flags, features = extract["sections"], extract["flags"], extract["features"]
    commands = [dict(c, section=s["title"], sectionId=s["id"])
                for s in sections for c in s["commands"]]

    counts = {
        "total": len(commands),
        "slash": sum(1 for c in commands if c["family"] == "slash"),
        "cli": sum(1 for c in commands if c["family"] == "cli"),
        "hidden": sum(1 for c in commands if c["family"] == "hidden"),
        "flags": len(flags),
        "features": len(features),
        "featuresOn": sum(1 for f in features if f["enabled"]),
        "documented": sum(1 for c in commands if c["docs"]),
        # null means unestablished, which is not the same claim as false — see `probe`.
        "notRegistered": sum(1 for c in commands if c["registered"] is False),
        "notProbed": sum(1 for c in commands if c["probe"] == "not probed"),
    }

    payload = {
        "name": "OpenAI Codex CLI command, flag and feature inventory",
        "description": ("Every slash command, subcommand, launch flag and feature flag in OpenAI "
                        "Codex CLI build %s." % S.CODEX_BUILD),
        "codexBuild": S.CODEX_BUILD,
        "generated": S.CODEX_UPDATED,
        "license": "CC BY 4.0",
        "canonicalPage": S.CODEX,
        "source": {
            "method": ("Slash-command names and descriptions were read from the running TUI: the "
                       "CLI was driven in a pseudo-terminal, the / picker opened and paged to its "
                       "end, and every row it rendered captured. Subcommands, arguments and launch "
                       "flags come from a recursive walk of `codex --help` on the same build, and "
                       "the feature table is `codex features list` verbatim. Availability was "
                       "established by probing, not by reading the documentation."),
            "binary": "codex %s (Homebrew cask)" % S.CODEX_BUILD,
            "officialDocs": "https://learn.chatgpt.com/docs/codex/cli",
        },
        "counts": counts,
        "families": CX_FAMILY_DESC,
        "fields": {
            "id": "Stable anchor on the canonical page; append as #id to deep-link",
            "name": "How the command is typed (/name for slash commands, bare for subcommands)",
            "family": "One of slash, cli, hidden — see families",
            "description": "Description string the build itself carries",
            "argument": "Argument hint the CLI shows, when it has one",
            "aliases": "Other names that resolve to the same command",
            "experimental": "The build labels the subcommand experimental",
            "registered": ("false means the name exists in the binary but typing it returns "
                           "Unrecognized command"),
            "probe": ("How availability was established: 'picker' listed by the / picker, 'ran' "
                      "runs but is withheld from the picker, 'unrecognized' rejected when typed, "
                      "'not probed' deliberately not executed"),
            "probeNote": "Why, where the classification needs one",
            "docs": "Most specific official documentation page, or null if none exists",
        },
        "sections": [{"id": s["id"], "title": s["title"], "description": s["blurb"],
                      "commandCount": len(s["commands"])} for s in sections],
        "commands": [{
            "id": c["id"], "name": c["name"], "family": c["family"], "section": c["section"],
            "description": c["description"], "argument": c["argument"], "aliases": c["aliases"],
            "experimental": c["experimental"], "registered": c["registered"],
            "probe": c["probe"], "probeNote": c["probeNote"], "docs": c["docs"],
            "url": S.CODEX + "#" + c["id"],
        } for c in commands],
        "flags": flags,
        "features": features,
    }

    md = [
        "# Codex CLI Command Index",
        "",
        "> Every slash command, `codex` subcommand, launch flag and feature flag in OpenAI Codex "
        "CLI build %s. Read out of the running CLI rather than the documentation: the slash "
        "commands off the picker itself, the subcommand tree off `codex --help`, and the feature "
        "table off `codex features list`." % S.CODEX_BUILD,
        "",
        "- Canonical page: %s" % S.CODEX,
        "- Machine-readable: %scodex-commands.json" % S.CODEX,
        "- Codex CLI build: %s" % S.CODEX_BUILD,
        "- Last updated: %s" % S.CODEX_UPDATED,
        "- License: CC BY 4.0",
        "",
        "## Totals",
        "",
        "| Group | Count | What it means |",
        "| --- | ---: | --- |",
        "| Slash commands | %d | Offered by the `/` picker at the Codex prompt |" % counts["slash"],
        "| CLI subcommands | %d | The `codex` executable and its whole subcommand tree |" % counts["cli"],
        "| Hidden | %d | In the binary, never offered by the picker |" % counts["hidden"],
        "| Launch flags | %d | Options passed to `codex` at startup |" % counts["flags"],
        "| Feature flags | %d | From `codex features list`; %d on in this build |"
        % (counts["features"], counts["featuresOn"]),
        "| Linked to official docs | %d | The rest have no official page |" % counts["documented"],
        "| Named but not registered | %d | Typing them returns `Unrecognized command` |" % counts["notRegistered"],
        "| Deliberately not probed | %d | Running them would have done real work |" % counts["notProbed"],
        "",
        "## How this was established",
        "",
        "Slash commands were read from the running TUI, not from a string dump: build %s was "
        "driven in a pseudo-terminal, the `/` picker opened and paged to its end, and every row it "
        "rendered captured with its description. Reading the binary as text additionally turns up "
        "names the picker never offers, and those were each typed at the prompt and classified by "
        "the response — running normally means registered but withheld, while *Unrecognized "
        "command* is the identical answer a deliberately nonsensical control command got. Commands "
        "that would have executed real work were excluded from the probe rather than run, and are "
        "marked as not probed rather than guessed at. Subcommands, arguments and launch flags come "
        "from a recursive walk of `codex --help` across every subcommand on the same build."
        % S.CODEX_BUILD,
        "",
    ]
    for s in sections:
        md += ["## %s" % s["title"], "",
               "%s. %d entries." % (s["blurb"].rstrip("."), len(s["commands"])), ""]
        md += [cx_md_command(c) for c in s["commands"]]
        md += [""]
    md += ["## Launch flags", "",
           "Passed to `codex` at launch. %d in total." % len(flags), "",
           "| Flag | What it does |", "| --- | --- |"]
    md += ["| `%s` | %s |" % (f["flag"], f["description"].replace("|", "\\|")) for f in flags]
    md += ["", "## Feature flags", "",
           "From `codex features list`. %d in total, %d on in this build. The stage is what the "
           "build calls the feature's maturity; the state depends on your `config.toml`, your "
           "account and the build's own defaults."
           % (len(features), counts["featuresOn"]), "",
           "| Feature | Stage | On in this build |", "| --- | --- | --- |"]
    md += ["| `%s` | %s | %s |" % (f["name"], f["stage"], "yes" if f["enabled"] else "no")
           for f in features]
    md += ["", "---", "",
           "From [%s](%s) by %s. If it saved you time, [buy me a coffee](%s)."
           % (S.SITE_NAME, S.BASE, S.AUTHOR, S.BMC), ""]

    return payload, "\n".join(md), counts


def cx_md_command(c):
    bits = ["- **`%s`**" % c["name"]]
    if c["argument"]:
        bits.append("`%s`" % c["argument"])
    if c["aliases"]:
        bits.append("*(aliases: %s)*" % ", ".join("`%s`" % a for a in c["aliases"]))
    line = " ".join(bits) + " — " + c["description"].rstrip(".") + "."
    notes = []
    if c["experimental"]:
        notes.append("the build labels this experimental")
    if c["probe"] == "ran":
        notes.append("withheld from the `/` picker, but runs when typed")
    elif c["probe"] == "unrecognized":
        notes.append("**typing it returns `Unrecognized command`** — " +
                     (c["probeNote"] or "").rstrip("."))
    elif c["probe"] == "not probed":
        notes.append("**not probed** — " + (c["probeNote"] or "").rstrip("."))
    if notes:
        line += " *(" + "; ".join(notes) + ")*"
    if c["docs"]:
        line += " [docs](%s)" % c["docs"]
    return line


METHOD_DESC = {
    "SKILL.md embedded in the binary":
        "The skill's whole SKILL.md ships as a module export; reproduced byte for byte.",
    "single embedded prompt constant":
        "One long string constant in the bundle; reproduced byte for byte.",
}


def build_skills_data(data):
    items = [dict(i, section=s["title"], sectionId=s["key"])
             for s in data["sections"] for i in s["items"]]

    payload = {
        "name": "Claude Code bundled skill prompts",
        "description": ("The full prompt behind every skill bundled inside Claude Code build %s."
                        % S.BUILD),
        "claudeCodeBuild": S.BUILD,
        "generated": S.UPDATED,
        "license": "CC BY 4.0",
        "canonicalPage": S.SKILLS,
        "source": {
            "method": ("Static extraction from the JavaScript bundle embedded in the compiled "
                       "binary. Each skill is registered there with its name, the description the "
                       "model sees, and a function returning its prompt; every prompt was resolved "
                       "back to its source string. The binary was read as text, never executed."),
            "binary": "~/.local/share/claude/versions/%s" % S.BUILD,
            "extractor": "%s/blob/main/build/claude-code-built-in-skills/extract_skills.py" % S.REPO,
            "officialDocs": "https://code.claude.com/docs/skills",
        },
        "counts": {
            "total": len(items),
            "userInvocable": data["totals"]["userInvocable"],
            "modelInvocable": data["totals"]["modelInvocable"],
            "verbatimSkillMd": data["totals"]["embedded"],
            "conditional": data["totals"]["conditional"],
            "promptChars": data["totals"]["chars"],
            "promptWords": sum(len(i["prompt"].split()) for i in items),
        },
        "fields": {
            "name": "How the skill is named in the binary; user-invocable ones are typed as /name",
            "id": "Stable anchor on the canonical page; append as #id to deep-link",
            "menu": "One-liner shown in the slash-command menu",
            "description": "The description the model reads when deciding whether to invoke it",
            "whenToUse": "Extra trigger guidance, when the skill carries any",
            "argumentHint": "Argument hint shown by the CLI, when it has one",
            "allowedTools": "Tools the skill restricts itself to, when it declares any",
            "userInvocable": "Whether you can type it as a slash command",
            "modelInvocable": "Whether Claude may reach for it on its own",
            "conditional": ("True when the skill carries an isEnabled check, so it registers only "
                            "in some sessions"),
            "gates": ("Feature-flag names the isEnabled check reads directly, where it names one; "
                      "empty does not mean unconditional — check conditional"),
            "env": "Environment variables the isEnabled check reads, where it names any",
            "promptMethod": "How the prompt is stored and assembled — see promptMethods",
            "prompt": "The prompt text itself",
        },
        "promptMethods": METHOD_DESC,
        "sections": [{"id": s["key"], "title": s["title"], "skillCount": len(s["items"])}
                     for s in data["sections"]],
        "skills": [{
            "id": "skill-" + i["name"], "name": i["name"], "section": i["section"],
            "sectionId": i["sectionId"], "menu": i["menu"], "description": i["description"],
            "whenToUse": i["whenToUse"], "argumentHint": i["argumentHint"],
            "allowedTools": i["allowedTools"], "userInvocable": i["userInvocable"],
            "modelInvocable": i["modelInvocable"], "conditional": i["conditional"],
            "gates": i["gates"], "env": i["env"],
            "promptMethod": i["promptMethod"], "promptChars": i["chars"],
            "prompt": i["prompt"], "url": S.SKILLS + "#skill-" + i["name"],
        } for i in items],
    }

    md = [
        "# Claude Code Bundled Skills",
        "",
        "> The complete prompt behind every skill bundled inside Claude Code build %s — all %d of "
        "them, read out of the shipped binary and reproduced verbatim. These are the texts pushed "
        "into the context window when you type the command or when Claude reaches for the skill "
        "itself." % (S.BUILD, len(items)),
        "",
        "- Canonical page: %s" % S.SKILLS,
        "- Machine-readable: %sskills.json" % S.SKILLS,
        "- Claude Code build: %s" % S.BUILD,
        "- Last updated: %s" % S.UPDATED,
        "- License: CC BY 4.0 for this compilation; the prompts themselves are Anthropic's.",
        "",
        "## Totals",
        "",
        "| Group | Count | What it means |",
        "| --- | ---: | --- |",
        "| Bundled skills | %d | Registered inside the binary, not in `~/.claude/skills` |"
        % len(items),
        "| Typed as a slash command | %d | The rest are reachable only by the model |"
        % payload["counts"]["userInvocable"],
        "| Claude may invoke on its own | %d | The rest are user-only |"
        % payload["counts"]["modelInvocable"],
        "| Shipped as a whole SKILL.md | %d | Stored complete, frontmatter and all |"
        % payload["counts"]["verbatimSkillMd"],
        "| Registered conditionally | %d | Present in the binary, but gated by an `isEnabled` check |"
        % payload["counts"]["conditional"],
        "| Words of prompt | %s | The whole corpus below |"
        % format(payload["counts"]["promptWords"], ","),
        "",
        "## How this was read",
        "",
        "Claude Code ships as one Bun-compiled executable with its JavaScript bundle embedded "
        "verbatim. Every bundled skill is registered in that bundle by a call carrying the skill's "
        "name, the description the model sees when deciding whether to invoke it, and a "
        "`getPromptForCommand` function returning the prompt. The extractor reads the binary as "
        "text, finds those calls, and resolves each prompt back to its source string; it never "
        "executes the program.",
        "",
        "Prompts arrive by four routes, and every entry says which one it took. A whole `SKILL.md` "
        "shipped as a module export is reproduced byte for byte, and so is a single string "
        "constant. A joined section array is concatenated in the order the skill joins it. A "
        "builder function stitches literals around values known only at run time — those are "
        "marked *assembled*, and their interpolation points are left visible as `${…}` rather than "
        "guessed at. Nothing here is paraphrased.",
        "",
    ]
    for sec in data["sections"]:
        md += ["## %s" % sec["title"], "",
               "%s %d skills." % (SECTION_BLURB.get(sec["key"], ""), len(sec["items"])), ""]
        for i in sec["items"]:
            md += ["### `%s%s`" % ("/" if i["userInvocable"] else "", i["name"]), ""]
            md += ["%s" % (i["description"] or i["menu"]), ""]
            bullets = []
            if i["whenToUse"]:
                bullets.append("- **When:** %s" % i["whenToUse"])
            if i["argumentHint"]:
                bullets.append("- **Takes:** `%s`" % i["argumentHint"])
            if i["allowedTools"]:
                bullets.append("- **Tools:** `%s`" % ", ".join(i["allowedTools"]))
            if i["conditional"]:
                extra = []
                if i["gates"]:
                    extra.append("flag `%s`" % ", ".join(i["gates"]))
                if i["env"]:
                    extra.append("env `%s`" % ", ".join(i["env"]))
                bullets.append("- **Registered conditionally**%s"
                               % ((" — " + "; ".join(extra)) if extra else ""))
            bullets.append("- **Invoked by:** %s" % " and ".join(filter(None, [
                "you" if i["userInvocable"] else "", "Claude" if i["modelInvocable"] else ""])))
            bullets.append("- **Prompt:** %s words, %s"
                           % (format(len(i["prompt"].split()), ","), i["promptMethod"]))
            bullets.append("- **Anchor:** %s#skill-%s" % (S.SKILLS, i["name"]))
            md += bullets + [""]
            md += ["```markdown", i["prompt"].replace("```", "​```"), "```", ""]
        md += [""]
    md += ["---", "",
           "From [%s](%s) by %s. If it saved you time, [buy me a coffee](%s)."
           % (S.SITE_NAME, S.BASE, S.AUTHOR, S.BMC), ""]

    return payload, "\n".join(md)


# ============================================================ the comparison page

CMP_SUPPORT = support(
    """<b>Found this useful?</b> Both halves of this page were measured rather than looked up — the
      pairing against the two inventories on this site, the capability table against
      <code>--help</code> on the two installed builds. If it saved you from installing both just to
      find out how they differ, you can put a coffee toward keeping it current.""")

CMP_MACHINE = machine([("compare.json", "compare.json"), ("compare.md", "compare.md"),
                       ("llms.txt", "../llms.txt")],
                      "every pairing and both leftovers, for scripts and agents.")

# label, CSS tone, the page each side's names link back to
CMP_SIDE = {"cc": ("Claude Code", "cc", "../claude-code-cheatsheet/#"),
            "cx": ("Codex CLI", "cx", "../codex-cheatsheet/#")}

# the two inventories slice themselves differently, so the bar has different segments per side
CMP_SEGMENTS = {"cc": [("native", "native slash"), ("skills", "bundled skills"),
                       ("cli", "shell subcommands"), ("hidden", "hidden")],
                "cx": [("slash", "slash commands"), ("cli", "shell subcommands"),
                       ("hidden", "hidden")]}
CMP_MIX = [100, 62, 38, 20]


def strip_tags(text):
    """Editorial fields carry inline HTML; the search index wants only the words."""
    out, depth = [], 0
    for ch in text:
        if ch == "<":
            depth += 1
        elif ch == ">":
            depth = max(0, depth - 1)
        elif depth == 0:
            out.append(ch)
    return "".join(out)


def cmp_resolve(names, index, what, pair_id):
    """A pairing that names a command the tool no longer has fails the build, rather than
    publishing a dead half-row that still looks authoritative."""
    picked = []
    for name in names:
        if name not in index:
            raise SystemExit("compare-data.json: %s names %s %r, which is not in the inventory"
                             % (pair_id, what, name))
        picked.append(index[name])
    return picked


def cmp_side(which, commands, flags):
    label, tone, base = CMP_SIDE[which]
    rows = ['<p class="said"><a href="%s%s">%s</a> <q>%s</q></p>'
            % (base, c["id"], esc(c["name"]), esc(c["description"].rstrip(".")))
            for c in commands]
    rows += ['<p class="said"><span class="nm">%s</span> <q>%s</q></p>'
             % (esc(f["flag"]), esc(f["description"].rstrip(".")))
             for f in flags]
    if not rows:
        rows = ['<p class="none">&mdash; no counterpart</p>']
    return ('        <div class="side" style="--tc:var(--%s)">\n'
            '          <span class="who">%s</span>\n'
            '          <div class="body">\n%s\n          </div>\n'
            '        </div>\n'
            % (tone, label, "\n".join("            " + r for r in rows)))


def cmp_pair(p, cc_idx, cx_idx, cc_flags, cx_flags):
    cc = cmp_resolve(p["cc"], cc_idx, "Claude Code command", p["id"])
    cx = cmp_resolve(p["cx"], cx_idx, "Codex command", p["id"])
    ccf = cmp_resolve(p.get("ccFlags", []), cc_flags, "Claude Code flag", p["id"])
    cxf = cmp_resolve(p.get("cxFlags", []), cx_flags, "Codex flag", p["id"])

    hay = " ".join([p["job"]]
                   + [c["name"] for c in cc + cx] + [f["flag"] for f in ccf + cxf]
                   + [c["description"] for c in cc + cx]
                   + [f["description"] for f in ccf + cxf]
                   + [strip_tags(p["note"])]).lower()
    note = '\n        <p class="pair-note">%s</p>' % p["note"] if p["note"] else ""

    return """      <article class="pair" id="{id}" data-hay="{hay}">
        <div class="pair-top">
          <h3 class="pair-job">{job}</h3>
          <a class="anchor" href="#{id}" aria-label="Link to {job}">#</a>
        </div>
{cc}{cx}{note}
      </article>
""".format(id=p["id"], hay=esc(hay), job=esc(p["job"]),
           cc=cmp_side("cc", cc, ccf), cx=cmp_side("cx", cx, cxf), note=note)


def cmp_only(commands, which):
    """Grouped by the section the command sits in on its own page, in that page's order."""
    _, _, base = CMP_SIDE[which]
    groups = []
    for c in commands:
        if not groups or groups[-1][0] != c["section"]:
            groups.append((c["section"], []))
        groups[-1][1].append(c)

    out = []
    for title, items in groups:
        rows = "".join(
            '          <div class="only" data-hay="%s"><a href="%s%s">%s</a><p>%s</p></div>\n'
            % (esc((c["name"] + " " + c["description"]).lower()), base, c["id"],
               esc(c["name"]), esc(c["description"].rstrip(".")))
            for c in items)
        out.append('        <div class="onlygroup">\n          <h4>%s</h4>\n%s        </div>\n'
                   % (esc(title), rows))
    return "".join(out)


def cmp_caps(caps):
    return "".join(
        '        <tr id="%s" data-hay="%s"><td class="topic">%s</td><td class="body">%s</td>'
        '<td class="body">%s</td><td class="how">%s</td></tr>\n'
        % (c["id"],
           esc(strip_tags(" ".join([c["topic"], c["cc"], c["cx"], c["evidence"]])).lower()),
           esc(c["topic"]), c["cc"], c["cx"], c["evidence"])
        for c in caps)


def cmp_verdict(v):
    def col(title, tone, items):
        return ('      <div class="vcol" style="--tc:var(--%s)">\n        <h3>%s</h3>\n'
                '        <ul>\n%s        </ul>\n      </div>\n'
                % (tone, title, "".join("          <li>%s</li>\n" % i for i in items)))

    return (col("Reach for Claude Code when", "cc", v["cc"])
            + col("Reach for Codex when", "cx", v["cx"])
            + col("And mostly", "fam-cli", [v["both"]]))


def cmp_shape(cc_counts, cx_counts, shape):
    def one(which, title, counts, blurb):
        _, tone, _ = CMP_SIDE[which]
        bars, legend = [], []
        for i, (key, name) in enumerate(CMP_SEGMENTS[which]):
            fill = ("var(--%s)" % tone if i == 0 else
                    "color-mix(in srgb, var(--%s) %d%%, var(--surface-2))" % (tone, CMP_MIX[i]))
            bars.append('<i style="width:%.2f%%;background:%s"></i>'
                        % (100.0 * counts[key] / counts["total"], fill))
            legend.append('<li><i style="background:%s"></i><b>%d</b> %s</li>'
                          % (fill, counts[key], name))
        return """      <div class="surface" style="--tc:var(--{tone})">
        <h3>{title}</h3>
        <p class="tot">{total} <span>commands</span></p>
        <div class="bar">{bars}</div>
        <ul class="legend">{legend}</ul>
        <p class="say">{blurb}</p>
      </div>
""".format(tone=tone, title=esc(title), total=counts["total"], bars="".join(bars),
           legend="".join(legend), blurb=blurb)

    return (one("cc", "Claude Code %s" % S.BUILD, cc_counts, shape["cc"])
            + one("cx", "Codex CLI %s" % S.CODEX_BUILD, cx_counts, shape["cx"]))


def compare_split(data, cc_payload, cx_payload):
    """Pair what the data names, and leave everything else as the computed complement."""
    cc_idx = {c["name"]: c for c in cc_payload["commands"]}
    cx_idx = {c["name"]: c for c in cx_payload["commands"]}
    cc_flags = {f["flag"]: f for f in cc_payload["flags"]}
    cx_flags = {f["flag"]: f for f in cx_payload["flags"]}

    cards, used_cc, used_cx = [], set(), set()
    for p in data["pairs"]:
        cards.append(cmp_pair(p, cc_idx, cx_idx, cc_flags, cx_flags))
        used_cc.update(p["cc"])
        used_cx.update(p["cx"])

    only_cc = [c for c in cc_payload["commands"] if c["name"] not in used_cc]
    only_cx = [c for c in cx_payload["commands"] if c["name"] not in used_cx]

    # The page claims every command appears exactly once, paired or left over. Hold it to that.
    for label, used, only, total in [("Claude Code", used_cc, only_cc, len(cc_payload["commands"])),
                                     ("Codex", used_cx, only_cx, len(cx_payload["commands"]))]:
        if len(used) + len(only) != total:
            raise SystemExit("compare: %s splits %d paired + %d left over, but the inventory has %d"
                             % (label, len(used), len(only), total))

    return cards, only_cc, only_cx


def build_compare_page(data, cc_payload, cx_payload, cc_counts, cx_counts):
    frag = (CMP_SRC / "compare.html").read_text(encoding="utf-8")
    cards, only_cc, only_cx = compare_split(data, cc_payload, cx_payload)

    stats = {"pairs": len(data["pairs"]), "onlycc": len(only_cc), "onlycx": len(only_cx),
             "caps": len(data["capabilities"]),
             "verdict": len(data["verdict"]["cc"]) + len(data["verdict"]["cx"]) + 1}

    frag = swap(frag, '<div class="shape" id="shape"></div>',
                '<div class="shape" id="shape">\n%s    </div>'
                % cmp_shape(cc_counts, cx_counts, data["shape"]), "shape host")
    frag = swap(frag, '<main id="pairs"></main>',
                '<main id="pairs">\n      <div class="pairgrid">\n%s      </div>\n    </main>'
                % "".join(cards), "pairs host")
    frag = swap(frag, '<div id="onlycc"></div>',
                '<div id="onlycc">\n%s        </div>' % cmp_only(only_cc, "cc"), "only-cc host")
    frag = swap(frag, '<div id="onlycx"></div>',
                '<div id="onlycx">\n%s        </div>' % cmp_only(only_cx, "cx"), "only-cx host")
    frag = swap(frag, '<tbody id="capbody"></tbody>',
                '<tbody id="capbody">\n%s      </tbody>' % cmp_caps(data["capabilities"]),
                "capabilities host")
    frag = swap(frag, '<div class="verdict" id="verdict"></div>',
                '<div class="verdict" id="verdict">\n%s    </div>'
                % cmp_verdict(data["verdict"]), "verdict host")

    for key, value in stats.items():
        frag = swap(frag, '<b id="s-%s">0</b>' % key,
                    '<b id="s-%s">%s</b>' % (key, value), "stat " + key)
    # Baked so the counts read correctly with JavaScript off; the page's own script re-derives
    # them as soon as a filter moves.
    for key, value in [("paircount", stats["pairs"]), ("cccount", stats["onlycc"]),
                       ("cxcount", stats["onlycx"]),
                       ("onlycount", stats["onlycc"] + stats["onlycx"]),
                       ("capcount", stats["caps"]), ("verdictcount", stats["verdict"])]:
        frag = swap(frag, '<span class="n" id="%s"></span>' % key,
                    '<span class="n" id="%s">%s</span>' % (key, value), "count " + key)

    frag = swap(frag, *masthead("%s + codex %s" % (S.BUILD, S.CODEX_BUILD),
                                "both read from the installed binaries"), label="masthead")
    frag = swap(frag, "\n  <footer>", CMP_SUPPORT, "footer")
    frag = swap(frag, "\n  </footer>", CMP_MACHINE, "machine-readable")
    frag = swap(frag, "\n  @media (prefers-reduced-motion",
                COFFEE_CSS + "  @media (prefers-reduced-motion", "css")
    frag = swap(frag, "<title>Claude Code vs Codex CLI — %s vs %s</title>\n"
                % (S.BUILD, S.CODEX_BUILD), "", "old title")

    head = page_head(
        title=S.CMP_TITLE, desc=S.CMP_DESC, url=S.COMPARE,
        ld=compare_ld(stats), updated=S.COMPARE_UPDATED,
        ogtitle="Claude Code vs Codex CLI — %d jobs both do, %d neither shares"
                % (stats["pairs"], stats["onlycc"] + stats["onlycx"]),
        ogalt="Claude Code %s against Codex CLI %s, command for command"
              % (S.BUILD, S.CODEX_BUILD),
        icon="%E2%9A%96",
        alts=[("text/markdown", "compare.md", "Markdown version of this page"),
              ("application/json", "compare.json",
               "JSON dataset of every pairing and both leftovers")])

    cut = frag.index("</style>") + len("</style>")
    return head + frag[:cut] + "\n</head>\n<body>\n" + frag[cut:].lstrip("\n") + "\n</body>\n</html>\n"


def compare_ld(stats):
    return [
        {
            "@context": "https://schema.org",
            "@type": "TechArticle",
            "@id": S.COMPARE + "#article",
            "headline": "Claude Code vs Codex CLI",
            "name": S.CMP_TITLE,
            "description": S.CMP_DESC,
            "url": S.COMPARE,
            "mainEntityOfPage": {"@type": "WebPage", "@id": S.COMPARE},
            "inLanguage": "en",
            "datePublished": S.COMPARE_UPDATED,
            "dateModified": S.COMPARE_UPDATED,
            "author": {"@type": "Person", "name": S.AUTHOR,
                       "url": "https://github.com/" + S.AUTHOR},
            "publisher": {"@type": "Organization", "name": S.SITE_NAME, "url": S.BASE},
            "isPartOf": {"@type": "CollectionPage", "@id": S.BASE + "#collection"},
            "image": S.COMPARE + "og.png",
            "about": [
                {"@type": "SoftwareApplication", "name": "Claude Code",
                 "applicationCategory": "DeveloperApplication",
                 "operatingSystem": "macOS, Linux, Windows", "softwareVersion": S.BUILD,
                 "url": "https://code.claude.com/docs/",
                 "publisher": {"@type": "Organization", "name": "Anthropic"}},
                {"@type": "SoftwareApplication", "name": "OpenAI Codex CLI",
                 "applicationCategory": "DeveloperApplication",
                 "operatingSystem": "macOS, Linux, Windows", "softwareVersion": S.CODEX_BUILD,
                 "url": "https://learn.chatgpt.com/docs/codex/cli",
                 "publisher": {"@type": "Organization", "name": "OpenAI"}},
            ],
            "keywords": ("Claude Code vs Codex, Codex CLI comparison, AI coding agent comparison, "
                         "slash commands, sandboxing, approval policy, hooks, CLAUDE.md, AGENTS.md"),
            "articleSection": ["The shape of each surface", "The same job, both tools",
                               "Only in one of them", "Capabilities", "Which one to reach for"],
        },
        {
            "@context": "https://schema.org",
            "@type": "Dataset",
            "@id": S.COMPARE + "#dataset",
            "name": "Claude Code %s and Codex CLI %s command comparison" % (S.BUILD, S.CODEX_BUILD),
            "description": ("%d jobs both tools ship a command for, with each build's own "
                            "description of its command, plus the %d Claude Code commands and %d "
                            "Codex commands that have no counterpart, and %d capability "
                            "comparisons sourced from the running CLIs."
                            % (stats["pairs"], stats["onlycc"], stats["onlycx"], stats["caps"])),
            "url": S.COMPARE,
            "license": "https://creativecommons.org/licenses/by/4.0/",
            "creator": {"@type": "Person", "name": S.AUTHOR},
            "dateModified": S.COMPARE_UPDATED,
            "isAccessibleForFree": True,
            "measurementTechnique": ("Set operations over the two published command inventories, "
                                     "plus `claude --help`, `codex --help` and the on-disk config "
                                     "layout of both tools"),
            "variableMeasured": ["job", "Claude Code commands", "Codex commands",
                                 "each build's own description", "unpaired commands",
                                 "capability topic", "how each capability was established"],
            "distribution": [
                {"@type": "DataDownload", "encodingFormat": "application/json",
                 "contentUrl": S.COMPARE + "compare.json"},
                {"@type": "DataDownload", "encodingFormat": "text/markdown",
                 "contentUrl": S.COMPARE + "compare.md"},
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": S.SITE_NAME, "item": S.BASE},
                {"@type": "ListItem", "position": 2, "name": "Claude Code vs Codex CLI",
                 "item": S.COMPARE},
            ],
        },
    ]


def build_compare_data(data, cc_payload, cx_payload):
    _, only_cc, only_cx = compare_split(data, cc_payload, cx_payload)
    cc_idx = {c["name"]: c for c in cc_payload["commands"]}
    cx_idx = {c["name"]: c for c in cx_payload["commands"]}
    cc_flags = {f["flag"]: f for f in cc_payload["flags"]}
    cx_flags = {f["flag"]: f for f in cx_payload["flags"]}

    def side(names, flag_names, index, flag_index, base):
        return {
            "commands": [{"name": n, "description": index[n]["description"],
                          "url": base + "#" + index[n]["id"]} for n in names],
            "flags": [{"flag": f, "description": flag_index[f]["description"]}
                      for f in flag_names],
        }

    pairs = [{
        "id": p["id"],
        "job": p["job"],
        "claudeCode": side(p["cc"], p.get("ccFlags", []), cc_idx, cc_flags, S.CHEATSHEET),
        "codex": side(p["cx"], p.get("cxFlags", []), cx_idx, cx_flags, S.CODEX),
        "note": strip_tags(p["note"]) or None,
        "url": S.COMPARE + "#" + p["id"],
    } for p in data["pairs"]]

    def leftover(items, base):
        return [{"name": c["name"], "section": c["section"], "description": c["description"],
                 "url": base + "#" + c["id"]} for c in items]

    payload = {
        "name": "Claude Code and Codex CLI, compared command for command",
        "description": ("Where Claude Code %s and OpenAI Codex CLI %s ship a command for the same "
                        "job, what only one of them has, and how they differ on sandboxing, "
                        "permissions, hooks and configuration." % (S.BUILD, S.CODEX_BUILD)),
        "claudeCodeBuild": S.BUILD,
        "codexBuild": S.CODEX_BUILD,
        "generated": S.COMPARE_UPDATED,
        "license": "CC BY 4.0",
        "canonicalPage": S.COMPARE,
        "source": {
            "method": ("The command halves are set operations over the two inventories published "
                       "on this site, which were themselves read out of the installed builds. "
                       "Descriptions are each build's own string, unedited. Which two commands "
                       "count as the same job is a hand-made judgement — that is the one part of "
                       "this file that was not measured — and the unpaired lists are then the "
                       "computed complement, so every command appears exactly once. The capability "
                       "rows come from `claude --help`, `codex --help` and the on-disk config "
                       "layout of both tools; each carries how it was established."),
            "claudeCodeInventory": S.CHEATSHEET + "commands.json",
            "codexInventory": S.CODEX + "codex-commands.json",
        },
        "counts": {
            "pairedJobs": len(pairs),
            "claudeCodeCommands": len(cc_payload["commands"]),
            "codexCommands": len(cx_payload["commands"]),
            "onlyClaudeCode": len(only_cc),
            "onlyCodex": len(only_cx),
            "capabilities": len(data["capabilities"]),
        },
        "fields": {
            "id": "Stable anchor on the canonical page; append as #id to deep-link",
            "job": "The shared job, named by hand — this is the editorial part",
            "claudeCode": "The Claude Code commands and launch flags that do it, with their own "
                          "descriptions and a link to the full entry",
            "codex": "The same for Codex",
            "note": "Where the two differ in kind rather than in name",
            "onlyClaudeCode": "Every Claude Code command no pairing claimed",
            "onlyCodex": "Every Codex command no pairing claimed",
            "capabilities": "Differences a command list cannot show, each with its evidence",
            "verdict": "Opinion, derived from the rows above and marked as such",
        },
        "pairs": pairs,
        "onlyClaudeCode": leftover(only_cc, S.CHEATSHEET),
        "onlyCodex": leftover(only_cx, S.CODEX),
        "capabilities": [{"id": c["id"], "topic": c["topic"],
                          "claudeCode": strip_tags(c["cc"]), "codex": strip_tags(c["cx"]),
                          "establishedBy": strip_tags(c["evidence"]),
                          "url": S.COMPARE + "#" + c["id"]} for c in data["capabilities"]],
        "verdict": {
            "disclaimer": "Opinion, not measurement. Everything else in this file was measured.",
            "reachForClaudeCode": [strip_tags(x) for x in data["verdict"]["cc"]],
            "reachForCodex": [strip_tags(x) for x in data["verdict"]["cx"]],
            "andMostly": strip_tags(data["verdict"]["both"]),
        },
    }

    def md_side(label, entry):
        bits = ["  - **%s:**" % label]
        if not entry["commands"] and not entry["flags"]:
            return "  - **%s:** *no counterpart.*" % label
        parts = ["`%s` — %s" % (c["name"], c["description"].rstrip("."))
                 for c in entry["commands"]]
        parts += ["`%s` *(launch flag)* — %s" % (f["flag"], f["description"].rstrip("."))
                  for f in entry["flags"]]
        return "\n".join(bits + ["    - " + p for p in parts])

    md = [
        "# Claude Code vs Codex CLI",
        "",
        "> Claude Code %s and OpenAI Codex CLI %s, command for command. %d jobs both ship a command "
        "for, quoted in each build's own words; %d Claude Code commands and %d Codex commands with "
        "no counterpart; and %d capability differences a command list cannot show."
        % (S.BUILD, S.CODEX_BUILD, len(pairs), len(only_cc), len(only_cx),
           len(data["capabilities"])),
        "",
        "- Canonical page: %s" % S.COMPARE,
        "- Machine-readable: %scompare.json" % S.COMPARE,
        "- Claude Code build: %s · Codex CLI build: %s" % (S.BUILD, S.CODEX_BUILD),
        "- Last updated: %s" % S.COMPARE_UPDATED,
        "- License: CC BY 4.0",
        "",
        "## How this was established",
        "",
        "The command halves are set operations over the two inventories published on this site, "
        "each read out of its installed build rather than its documentation. Every description "
        "below is the string that build carries, unedited.",
        "",
        "What was **not** measured is the pairing: deciding that two commands do the same job is a "
        "judgement made by hand, which is why both descriptions are printed rather than "
        "summarised — so the judgement can be checked. The two unpaired lists are then the "
        "computed complement of the pairing, so every command in either inventory appears exactly "
        "once, and a bad pairing shows up as a missing entry rather than a silent one.",
        "",
        "The capability section was measured separately, from `claude --help`, `codex --help` and "
        "the on-disk config layout of both tools on one machine. Each row names its evidence. The "
        "closing section is opinion and says so.",
        "",
        "## The same job, both tools",
        "",
        "%d jobs. Each tool's own description of its own command." % len(pairs),
        "",
    ]
    for p in pairs:
        md += ["### %s" % p["job"], ""]
        md += [md_side("Claude Code", p["claudeCode"]), md_side("Codex", p["codex"])]
        if p["note"]:
            md += ["", "  %s" % p["note"]]
        md += [""]

    for title, items, blurb in [
            ("Only in Claude Code", only_cc,
             "Claude Code commands no pairing above claimed. %d of %d."
             % (len(only_cc), len(cc_payload["commands"]))),
            ("Only in Codex", only_cx,
             "Codex commands no pairing above claimed. %d of %d."
             % (len(only_cx), len(cx_payload["commands"])))]:
        md += ["## %s" % title, "", blurb, ""]
        section = None
        for c in items:
            if c["section"] != section:
                section = c["section"]
                md += ["", "**%s**" % section, ""]
            md += ["- **`%s`** — %s" % (c["name"], c["description"].rstrip("."))]
        md += [""]

    md += ["## Capabilities, not commands", "",
           "Differences a command list cannot show. Nothing here comes from either vendor's "
           "documentation; each row names how it was established.", "",
           "| Topic | Claude Code %s | Codex CLI %s | How this was established |"
           % (S.BUILD, S.CODEX_BUILD),
           "| --- | --- | --- | --- |"]
    md += ["| %s | %s | %s | %s |"
           % (c["topic"], strip_tags(c["cc"]).replace("|", "\\|"),
              strip_tags(c["cx"]).replace("|", "\\|"),
              strip_tags(c["evidence"]).replace("|", "\\|"))
           for c in data["capabilities"]]
    md += ["",
           "One row is weaker than the others, and it is the hooks row. Both binaries carry the "
           "same eleven event names, which settles it for Claude Code — they are the keys its "
           "`settings.json` takes — but not for Codex, which also ships an importer for Claude "
           "Code setups and so has a reason to know those names either way. Which of the eleven "
           "Codex actually fires was not established here, and is not claimed.",
           "",
           "## Which one to reach for", "",
           "*Opinion. Everything above this line was measured; this is a reading of it.*", ""]
    md += ["**Reach for Claude Code when**", ""]
    md += ["- %s" % strip_tags(x) for x in data["verdict"]["cc"]]
    md += ["", "**Reach for Codex when**", ""]
    md += ["- %s" % strip_tags(x) for x in data["verdict"]["cx"]]
    md += ["", "**And mostly**", "", strip_tags(data["verdict"]["both"]), "",
           "---", "",
           "From [%s](%s) by %s. If it saved you time, [buy me a coffee](%s)."
           % (S.SITE_NAME, S.BASE, S.AUTHOR, S.BMC), ""]

    return payload, "\n".join(md)


# ============================================================ site-wide files

AI_AGENTS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User",
             "Claude-SearchBot", "PerplexityBot", "Perplexity-User", "Google-Extended",
             "Applebot-Extended", "CCBot", "Bingbot", "DuckAssistBot", "cohere-ai",
             "Meta-ExternalAgent", "Amazonbot", "YouBot"]

# url, sitemap priority, lastmod — each page carries the day its own content last changed.
PAGES = [(S.BASE, "1.0", S.SITE_UPDATED),
         (S.CHEATSHEET, "0.9", S.UPDATED),
         (S.SKILLS, "0.9", S.UPDATED),
         (S.CODEX, "0.9", S.CODEX_UPDATED),
         (S.COMPARE, "0.9", S.COMPARE_UPDATED),
         (S.MEMORY, "0.9", S.MEM_UPDATED)]


def build_site_files(markdown, counts, skill_counts, codex_counts, compare_counts, memory_counts):
    llms = """# {site}

> {desc}

Every page is a single self-contained HTML file with no external requests. Facts on each page were
checked against the tool itself rather than its documentation; where the two disagree, the page
follows the tool and says so.

## Pages

- [Claude Code Command Index]({cs}): every slash command, bundled skill, `claude` CLI subcommand
  and launch flag in Claude Code build {build} — {total} commands and {flags} flags, extracted from
  the installed binary, probed for availability, and linked to the official docs.
- [Claude Code Bundled Skills]({sk}): the complete prompt behind every skill bundled inside build
  {build} — all {skills} of them, {words} words in total, read out of the shipped binary and
  reproduced verbatim rather than summarised.
- [Codex CLI Command Index]({cx}): every slash command, `codex` subcommand, launch flag and feature
  flag in OpenAI Codex CLI build {cxbuild} — {cxtotal} commands, {cxflags} flags and {cxfeat}
  feature switches, read out of the running CLI and probed for availability.
- [Claude Code vs Codex CLI]({cmp}): the two agents side by side — {cmppairs} jobs both ship a
  command for, quoted in each build's own words, {cmpcc} commands only Claude Code has and {cmpcx}
  only Codex has, plus {cmpcaps} capability differences measured from the running CLIs.
- [Auto-Memory in Claude Code and Codex]({mem}): how each tool writes, stores and recalls memory
  between sessions — the on-disk layout, the prompt text that governs it and the switches that turn
  it off, read out of both installed binaries and compared across {memdims} dimensions.

## Machine-readable data

- [Claude Code commands as Markdown]({cs}commands.md): the full command index as plain Markdown.
- [Claude Code commands as JSON]({cs}commands.json): the same inventory as structured data, with
  descriptions, aliases, argument hints, availability and documentation links per command.
- [Claude Code skill prompts as Markdown]({sk}skills.md): every bundled skill's prompt in full.
- [Claude Code skill prompts as JSON]({sk}skills.json): the same prompts as structured data, with
  the description, trigger hint, gating and assembly method per skill.
- [Codex CLI commands as Markdown]({cx}codex-commands.md): the full Codex index as plain Markdown.
- [Codex CLI commands as JSON]({cx}codex-commands.json): the same inventory as structured data,
  with how each command's availability was established, plus the whole feature table.
- [The comparison as Markdown]({cmp}compare.md): every pairing and both leftovers as plain Markdown.
- [The comparison as JSON]({cmp}compare.json): the same as structured data — each pairing with both
  builds' own descriptions, the unpaired commands on each side, and the capability rows.
- [Auto-memory as Markdown]({mem}memory.md): both mechanisms and the comparison as plain Markdown.
- [Auto-memory as JSON]({mem}memory.json): the same as structured data — each lifecycle stage with
  the verbatim strings behind it, the artefacts each tool writes, and every comparison row.
- [Everything as one file]({base}llms-full.txt): every page's Markdown concatenated.

## About

- [Source repository]({repo}): all pages, hand-built, no framework.
- [Support the work]({bmc}).
""".format(site=S.SITE_NAME, desc=S.SITE_DESC, cs=S.CHEATSHEET, sk=S.SKILLS, cx=S.CODEX,
           base=S.BASE, repo=S.REPO, bmc=S.BMC, build=S.BUILD, total=counts["total"],
           flags=counts["flags"], skills=skill_counts["total"],
           words=format(skill_counts["promptWords"], ","), cxbuild=S.CODEX_BUILD,
           cxtotal=codex_counts["total"], cxflags=codex_counts["flags"],
           cxfeat=codex_counts["features"],
           cmp=S.COMPARE, cmppairs=compare_counts["pairedJobs"],
           cmpcc=compare_counts["onlyClaudeCode"], cmpcx=compare_counts["onlyCodex"],
           cmpcaps=compare_counts["capabilities"],
           mem=S.MEMORY, memdims=memory_counts["dimensions"])
    (ROOT / "llms.txt").write_text(llms, encoding="utf-8")

    (ROOT / "llms-full.txt").write_text(
        "# %s — full text\n\n> %s\n\nGenerated %s. Canonical site: %s\n\n---\n\n%s"
        % (S.SITE_NAME, S.SITE_DESC, S.SITE_UPDATED, S.BASE, markdown), encoding="utf-8")

    robots = ["User-agent: *", "Allow: /", ""]
    for agent in AI_AGENTS:
        robots += ["User-agent: %s" % agent, "Allow: /", ""]
    robots += ["Sitemap: %ssitemap.xml" % S.BASE, ""]
    (ROOT / "robots.txt").write_text("\n".join(robots), encoding="utf-8")

    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, priority, lastmod in PAGES:
        sitemap += ["  <url>", "    <loc>%s</loc>" % loc,
                    "    <lastmod>%s</lastmod>" % lastmod,
                    "    <changefreq>monthly</changefreq>",
                    "    <priority>%s</priority>" % priority, "  </url>"]
    sitemap += ["</urlset>", ""]
    (ROOT / "sitemap.xml").write_text("\n".join(sitemap), encoding="utf-8")

    (ROOT / ".nojekyll").write_text("", encoding="utf-8")


# ============================================================ run

def main():
    for src in [CS_SRC, CX_SRC]:
        for required in ["extract.json", "prerender.json"]:
            if not (src / required).exists():
                raise SystemExit("missing %s/%s — run `node build/capture.mjs` first"
                                 % (src.name, required))

    extract = json.loads((CS_SRC / "extract.json").read_text(encoding="utf-8"))
    prerender = json.loads((CS_SRC / "prerender.json").read_text(encoding="utf-8"))

    CS_OUT.mkdir(parents=True, exist_ok=True)
    (CS_OUT / "index.html").write_text(build_cheatsheet_page(prerender), encoding="utf-8")

    payload, markdown, counts = build_data(extract)
    (CS_OUT / "commands.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                                          encoding="utf-8")
    (CS_OUT / "commands.md").write_text(markdown, encoding="utf-8")

    skills = json.loads((SK_SRC / "skills-data.json").read_text(encoding="utf-8"))
    SK_OUT.mkdir(parents=True, exist_ok=True)
    (SK_OUT / "index.html").write_text(build_skills_page(skills), encoding="utf-8")
    sk_payload, sk_markdown = build_skills_data(skills)
    (SK_OUT / "skills.json").write_text(json.dumps(sk_payload, indent=2, ensure_ascii=False) + "\n",
                                        encoding="utf-8")
    (SK_OUT / "skills.md").write_text(sk_markdown, encoding="utf-8")

    cx_extract = json.loads((CX_SRC / "extract.json").read_text(encoding="utf-8"))
    cx_prerender = json.loads((CX_SRC / "prerender.json").read_text(encoding="utf-8"))
    cx_payload, cx_markdown, cx_counts = build_codex_data(cx_extract)
    CX_OUT.mkdir(parents=True, exist_ok=True)
    (CX_OUT / "index.html").write_text(build_codex_page(cx_prerender, cx_counts),
                                       encoding="utf-8")
    (CX_OUT / "codex-commands.json").write_text(
        json.dumps(cx_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (CX_OUT / "codex-commands.md").write_text(cx_markdown, encoding="utf-8")

    cmp_data = json.loads((CMP_SRC / "compare-data.json").read_text(encoding="utf-8"))
    CMP_OUT.mkdir(parents=True, exist_ok=True)
    (CMP_OUT / "index.html").write_text(
        build_compare_page(cmp_data, payload, cx_payload, counts, cx_counts), encoding="utf-8")
    cmp_payload, cmp_markdown = build_compare_data(cmp_data, payload, cx_payload)
    (CMP_OUT / "compare.json").write_text(
        json.dumps(cmp_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (CMP_OUT / "compare.md").write_text(cmp_markdown, encoding="utf-8")

    mem_data = json.loads((MEM_SRC / "memory-data.json").read_text(encoding="utf-8"))
    MEM_OUT.mkdir(parents=True, exist_ok=True)
    (MEM_OUT / "index.html").write_text(build_memory_page(mem_data), encoding="utf-8")
    mem_payload, mem_markdown = build_memory_data(mem_data)
    (MEM_OUT / "memory.json").write_text(
        json.dumps(mem_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (MEM_OUT / "memory.md").write_text(mem_markdown, encoding="utf-8")

    build_site_files(markdown + "\n\n---\n\n" + sk_markdown + "\n\n---\n\n" + cx_markdown
                     + "\n\n---\n\n" + cmp_markdown + "\n\n---\n\n" + mem_markdown,
                     counts, sk_payload["counts"], cx_counts, cmp_payload["counts"],
                     mem_payload["counts"])

    written = ["claude-code-cheatsheet/index.html", "claude-code-cheatsheet/commands.json",
               "claude-code-cheatsheet/commands.md", "claude-code-built-in-skills/index.html",
               "claude-code-built-in-skills/skills.json", "claude-code-built-in-skills/skills.md",
               "codex-cheatsheet/index.html", "codex-cheatsheet/codex-commands.json",
               "codex-cheatsheet/codex-commands.md",
               "claude-code-vs-codex/index.html", "claude-code-vs-codex/compare.json",
               "claude-code-vs-codex/compare.md",
               "agent-memory/index.html", "agent-memory/memory.json", "agent-memory/memory.md",
               "llms.txt", "llms-full.txt", "robots.txt", "sitemap.xml", ".nojekyll"]
    for f in written:
        print("  %-42s %8d bytes" % (f, (ROOT / f).stat().st_size))
    print("\n%d commands, %d flags, %d linked to docs"
          % (counts["total"], counts["flags"], counts["documented"]))
    print("%d bundled skills, %s words of prompt"
          % (sk_payload["counts"]["total"], format(sk_payload["counts"]["promptWords"], ",")))
    print("codex %s: %d commands, %d flags, %d feature switches (%d on), %d linked to docs"
          % (S.CODEX_BUILD, cx_counts["total"], cx_counts["flags"], cx_counts["features"],
             cx_counts["featuresOn"], cx_counts["documented"]))
    print("memory: %d lifecycle stages, %d artefacts, %d verbatim quotes, %d dimensions compared"
          % (mem_payload["counts"]["stages"], mem_payload["counts"]["artefacts"],
             mem_payload["counts"]["quotes"], mem_payload["counts"]["dimensions"]))
    print("compare: %d paired jobs, %d only Claude Code, %d only Codex, %d capabilities"
          % (cmp_payload["counts"]["pairedJobs"], cmp_payload["counts"]["onlyClaudeCode"],
             cmp_payload["counts"]["onlyCodex"], cmp_payload["counts"]["capabilities"]))
    print("index.html and 404.html are hand-maintained — this script does not touch them.")


if __name__ == "__main__":
    main()
