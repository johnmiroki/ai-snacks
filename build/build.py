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


def swap(text, old, new, label):
    if text.count(old) != 1:
        raise SystemExit("expected exactly one %s anchor, found %d" % (label, text.count(old)))
    return text.replace(old, new)


def esc(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


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
def masthead(build):
    old = """  <header class="masthead">
    <p class="eyebrow">Reference &middot; build {build} &middot; extracted from the installed binary</p>""".format(build=build)

    new = """  <header class="masthead">
    <div class="masthead-top">
      <p class="eyebrow"><a href="../" class="home">AI Snacks</a> &middot; build {build} &middot; extracted from the installed binary</p>
      <a class="coffee" href="{bmc}" target="_blank" rel="noopener noreferrer">
        <span class="cup" aria-hidden="true">&#9749;</span>Buy me a coffee</a>
    </div>""".format(build=build, bmc=S.BMC)
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


# ============================================================ site-wide files

AI_AGENTS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User",
             "Claude-SearchBot", "PerplexityBot", "Perplexity-User", "Google-Extended",
             "Applebot-Extended", "CCBot", "Bingbot", "DuckAssistBot", "cohere-ai",
             "Meta-ExternalAgent", "Amazonbot", "YouBot"]

# url, sitemap priority, lastmod — each page carries the day its own content last changed.
PAGES = [(S.BASE, "1.0", S.SITE_UPDATED),
         (S.CHEATSHEET, "0.9", S.UPDATED),
         (S.SKILLS, "0.9", S.UPDATED),
         (S.CODEX, "0.9", S.CODEX_UPDATED)]


def build_site_files(markdown, counts, skill_counts, codex_counts):
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
- [Everything as one file]({base}llms-full.txt): every page's Markdown concatenated.

## About

- [Source repository]({repo}): all pages, hand-built, no framework.
- [Support the work]({bmc}).
""".format(site=S.SITE_NAME, desc=S.SITE_DESC, cs=S.CHEATSHEET, sk=S.SKILLS, cx=S.CODEX,
           base=S.BASE, repo=S.REPO, bmc=S.BMC, build=S.BUILD, total=counts["total"],
           flags=counts["flags"], skills=skill_counts["total"],
           words=format(skill_counts["promptWords"], ","), cxbuild=S.CODEX_BUILD,
           cxtotal=codex_counts["total"], cxflags=codex_counts["flags"],
           cxfeat=codex_counts["features"])
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

    build_site_files(markdown + "\n\n---\n\n" + sk_markdown + "\n\n---\n\n" + cx_markdown,
                     counts, sk_payload["counts"], cx_counts)

    written = ["claude-code-cheatsheet/index.html", "claude-code-cheatsheet/commands.json",
               "claude-code-cheatsheet/commands.md", "claude-code-built-in-skills/index.html",
               "claude-code-built-in-skills/skills.json", "claude-code-built-in-skills/skills.md",
               "codex-cheatsheet/index.html", "codex-cheatsheet/codex-commands.json",
               "codex-cheatsheet/codex-commands.md",
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
    print("index.html and 404.html are hand-maintained — this script does not touch them.")


if __name__ == "__main__":
    main()
