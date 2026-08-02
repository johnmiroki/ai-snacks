# AI Snacks

Small, self-contained reference pages for the AI tools I use every day — each one a single
`index.html` with no build step, no dependencies, no analytics, and nothing loaded from another
server.

**→ [johnmiroki.github.io/ai-snacks](https://johnmiroki.github.io/ai-snacks/)**

## On the shelf

| Snack | What it is | Also as |
| --- | --- | --- |
| [Auto-Memory in Claude Code and Codex](https://johnmiroki.github.io/ai-snacks/agent-memory/) | How each tool writes, stores and recalls memory between sessions — the on-disk layout, the prompt text that governs it and the switches that turn it off, read out of both installed binaries and compared across 15 dimensions | [json](https://johnmiroki.github.io/ai-snacks/agent-memory/memory.json) · [md](https://johnmiroki.github.io/ai-snacks/agent-memory/memory.md) |
| [Claude Code vs Codex CLI](https://johnmiroki.github.io/ai-snacks/claude-code-vs-codex/) | The two agents command for command — 43 jobs both ship a command for, quoted in each build's own words, 69 commands only Claude Code has and 55 only Codex has, plus 13 capability differences measured from the running CLIs | [json](https://johnmiroki.github.io/ai-snacks/claude-code-vs-codex/compare.json) · [md](https://johnmiroki.github.io/ai-snacks/claude-code-vs-codex/compare.md) |
| [Claude Code Bundled Skills](https://johnmiroki.github.io/ai-snacks/claude-code-built-in-skills/) | The full prompt behind all 35 skills bundled inside Claude Code 2.1.220 — read out of the shipped binary and reproduced verbatim, not summarised | [json](https://johnmiroki.github.io/ai-snacks/claude-code-built-in-skills/skills.json) · [md](https://johnmiroki.github.io/ai-snacks/claude-code-built-in-skills/skills.md) |
| [Claude Code Command Index](https://johnmiroki.github.io/ai-snacks/claude-code-cheatsheet/) | Every slash command, bundled skill, `claude` subcommand and CLI flag in Claude Code 2.1.220 — extracted from the installed binary, probed for availability, linked to the official docs | [json](https://johnmiroki.github.io/ai-snacks/claude-code-cheatsheet/commands.json) · [md](https://johnmiroki.github.io/ai-snacks/claude-code-cheatsheet/commands.md) |
| [Codex CLI Command Index](https://johnmiroki.github.io/ai-snacks/codex-cheatsheet/) | Every slash command, `codex` subcommand, launch flag and feature switch in OpenAI Codex CLI 0.146.0 — slash commands read off the running `/` picker, availability settled by probing | [json](https://johnmiroki.github.io/ai-snacks/codex-cheatsheet/codex-commands.json) · [md](https://johnmiroki.github.io/ai-snacks/codex-cheatsheet/codex-commands.md) |

## Layout

```
ai-snacks/
├── index.html                          hub — lists every snack (hand-maintained)
├── 404.html                            shared not-found page (hand-maintained)
├── og.png                              social preview for the hub
├── llms.txt                            site index for language models
├── llms-full.txt                       every page's Markdown, concatenated
├── robots.txt                          crawl directives + sitemap pointer
├── sitemap.xml                         one entry per page
├── .nojekyll                           serve files as-is, no Jekyll pass
├── claude-code-cheatsheet/             one folder per snack
│   ├── index.html                      the page, content pre-rendered
│   ├── commands.json                   the same data, structured
│   ├── commands.md                     the same page, plain Markdown
│   └── og.png
├── claude-code-built-in-skills/
│   ├── index.html                      the page, prompts baked in
│   ├── skills.json                     every prompt, structured
│   ├── skills.md                       every prompt, plain Markdown
│   └── og.png
├── codex-cheatsheet/
│   ├── index.html                      the page, content pre-rendered
│   ├── codex-commands.json             commands, flags and features, structured
│   ├── codex-commands.md               the same page, plain Markdown
│   └── og.png
├── claude-code-vs-codex/
│   ├── index.html                      the page, every pairing baked in
│   ├── compare.json                    pairings, leftovers and capabilities, structured
│   ├── compare.md                      the same page, plain Markdown
│   └── og.png
├── agent-memory/
│   ├── index.html                      the page, both walkthroughs baked in
│   ├── memory.json                     stages, evidence and comparison rows, structured
│   ├── memory.md                       the same page, plain Markdown
│   └── og.png
├── build/                              what everything above is built from
│   ├── build.py                        assembles the site into the repo root
│   ├── capture.mjs                     pre-renders the cards, shoots the OG images
│   ├── siteconf.py                     URLs, build number, titles, date
│   ├── og-hub.html                     OG template for the hub
│   ├── claude-code-cheatsheet/
│   │   ├── claude-code-commands.html   the page source — edit this, not the output
│   │   ├── og.html                     OG template for the page
│   │   ├── extract.json                captured command and flag data
│   │   └── prerender.json              captured HTML for the cards
│   ├── claude-code-built-in-skills/
│   │   ├── skills.html                 the page source — edit this, not the output
│   │   ├── og.html                     OG template for the page
│   │   ├── extract_skills.py           mines the prompts out of the CLI binary
│   │   └── skills-data.json            what it mined — the page's source of truth
│   ├── codex-cheatsheet/
│   │   ├── codex-commands.html         the page source — edit this, not the output
│   │   ├── og.html                     OG template for the page
│   │   ├── probe_codex.py              re-measures the CLI: TUI picker, help tree, features
│   │   ├── extract.json                captured command, flag and feature data
│   │   └── prerender.json              captured HTML for the cards and tables
│   ├── claude-code-vs-codex/
│   │   ├── compare.html                the page source — edit this, not the output
│   │   ├── og.html                     OG template for the page
│   │   └── compare-data.json           the pairings, capabilities and verdict — hand-authored
│   └── agent-memory/
│       ├── memory.html                 the page source — chrome only, edit this
│       ├── og.html                     OG template for the page
│       └── memory-data.json            both walkthroughs, the evidence and the comparison
└── README.md
```

GitHub Pages serves the repo root, so a folder named `<slug>` is reachable at
`johnmiroki.github.io/ai-snacks/<slug>/`.

Everything outside `build/` and the two hand-maintained pages is **generated**. Editing a published
file directly is wasted work — the next build overwrites it.

## Building

```sh
node build/capture.mjs    # only when a page source or an OG template changed
python3 build/build.py    # always — assembles the site
```

`capture.mjs` opens both command-index sources in headless Chromium, snapshots the JavaScript-built
cards into each page's `extract.json` and `prerender.json`, and screenshots all four OG images.
`build.py` needs nothing but the checked-in JSON, so the usual edit-and-rebuild loop is Python only.
It verifies the Claude capture still holds 143 commands and 57 flags, the skill data still holds 35
skills, and the Codex capture still holds 122 commands, 21 flags and 100 feature switches, and stops
rather than publish a half-built page.

Playwright provides the browser (`npm install` in `build/`); set `CHROMIUM_PATH` to use one it did
not install itself. A clean `python3 build/build.py` on an unchanged checkout produces no diff — if
it does, the source and the published output have drifted. Re-running `capture.mjs` does rewrite
every `og.png` with different bytes for a pixel-identical image, since PNG output varies between
Chromium versions; that churn is not worth committing.

The skill prompts come from a third script, run only when Claude Code itself updates:

```sh
python3 build/claude-code-built-in-skills/extract_skills.py \
    ~/.local/share/claude/versions/2.1.220 \
    build/claude-code-built-in-skills/skills-data.json
```

It reads the binary as text — it never executes it — finds each bundled skill's registration in the
embedded JavaScript bundle, and resolves every prompt back to its source string.

The Codex numbers come from a fourth script, run only when Codex itself updates:

```sh
CODEX_PROBE_CWD=~/some/trusted/repo \
python3 build/codex-cheatsheet/probe_codex.py /opt/homebrew/bin/codex codex-probe.json
```

Unlike the Claude extractor, this one runs the tool. Codex is a Rust binary whose slash-command
names are packed into one undelimited string block, so they cannot be recovered by reading it — the
script drives the TUI in a pseudo-terminal instead, opens the `/` picker and walks it to the end.
Names that appear in the binary but never in the picker are then typed at the prompt and classified
against a deliberately nonsensical control command, which separates *runs but is withheld from the
picker* from *"Unrecognized command"*. Three commands that would have done real work are declared in
`DO_NOT_RUN` and reported as not probed rather than executed. Diff its report against the page
source; it does not write the page.

The comparison page needs no script of its own either. `build/claude-code-vs-codex/compare-data.json`
names which commands on each side count as the same job, and `build.py` resolves every one of those
names against the two published inventories — a pairing that names a command the tool no longer
ships fails the build rather than publishing a dead half-row. The two *only in* lists are then the
computed complement of the pairing, and the build asserts that paired + unpaired equals each
inventory exactly, so every command lands on the page precisely once. The capability table and the
closing verdict are prose in the same file; the verdict is the one section on the site that is
opinion, and it says so.

The auto-memory page needs no script of its own, and its prose lives in the data rather than the
page source: `build/agent-memory/memory-data.json` carries both walkthroughs, every verbatim quote
with its provenance, and the comparison rows, while `memory.html` is chrome only. That is what lets
the Markdown twin carry the whole argument instead of a hollowed-out version of it — `to_md()` in
`build.py` derives it from the same HTML the page renders, and rejects any tag outside the small
allowed subset rather than emitting Markdown with stray markup in it. Both mechanisms were read out
of the two installed binaries; a path is only attributed to a tool when the literal also appears
inside that tool's binary, because plugins and extensions write under the same directories.

## Readable by people, machines and crawlers

Every page ships three ways: as HTML for people, as Markdown and JSON for agents, and with
`schema.org` metadata for search engines.

- **Content lives in the HTML.** Pages that build themselves with JavaScript are invisible to
  crawlers that do not run it — which is most of the ones that feed AI answers. Both pages are
  rendered once at build time and baked into the file; their JavaScript only filters what is
  already there. On the skills page the prompts sit inside `<details>`, which collapses them for
  readers without hiding them from a crawler.
- **Every entry has a stable anchor.** `#cmd-compact`, `#cli-claude-mcp`, `#skill-dataviz` —
  deep-linkable and unchanged between builds.
- **`llms.txt`** indexes the site for language models; **`llms-full.txt`** is the whole thing in one
  fetch.
- **Structured data.** The hub carries `WebSite` + `CollectionPage`; each page carries `TechArticle`,
  a `Dataset` pointing at its JSON, and a `BreadcrumbList`.

`robots.txt` here is served at `/ai-snacks/robots.txt`. Crawlers only read the one at the domain
root, which belongs to the `johnmiroki.github.io` repo — so this file documents intent and would
become effective under a custom domain, but does not currently govern crawling. Submit
`sitemap.xml` through Search Console rather than relying on the robots pointer.

## Adding a snack

1. Write the page source under `build/<slug>/`. One self-contained file: `<meta charset="utf-8">`,
   a viewport meta, both light and dark themes via `prefers-color-scheme`, and a `<link rel=
   "canonical">`.
2. Teach `build.py` about it — a build function that writes `<slug>/index.html`, a `schema.org`
   block, an entry in `PAGES`, and a line in the `llms.txt` template. The masthead, coffee CSS,
   support callout, `<head>` and machine-readable footer are already shared; a new page picks them
   up by carrying the same anchors in its source and calling `page_head()`.
3. In the root `index.html`, copy the `<a class="snack">` block and edit the href, title,
   description, and facts. Add a row to the table above.
4. Run the build, then commit and push to `main`. Pages redeploys in about 20 seconds.

`sitemap.xml`, `llms.txt` and `llms-full.txt` are generated — add the page to `build.py` rather than
editing them by hand.

## House rules

- **One file per page.** No bundler, no CDN, no webfont URL — inline everything. A snack should
  still work saved to disk and opened offline.
- **Check claims against the thing itself,** not its documentation. Where the two disagree, follow
  the tool and say so on the page.
- **Say what was measured.** If a number came from a probe or a parse, the page should explain how.

---

If one of these saved you some time: [buy me a coffee](https://buymeacoffee.com/john42) ☕
