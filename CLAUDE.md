# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A GitHub Pages site (`johnmiroki.github.io/ai-snacks/`) hosting single-page HTML references for AI
developer tools. One folder per page, served straight from the repo root. Two pages:
`claude-code-cheatsheet/` and `claude-code-built-in-skills/`.

## Build

```sh
python3 build/build.py    # assembles the site — the usual loop
node build/capture.mjs    # only when a page source or an OG template changed
```

No tests, no linter, no package to install for the Python half. Verification is that a clean
`python3 build/build.py` on an unchanged checkout leaves `git status` empty — if it produces a diff,
the source and the published output have drifted.

`capture.mjs` needs Playwright (`npm install` in `build/`; `CHROMIUM_PATH` overrides the browser).
Note `build/node_modules` is currently a symlink into a local npx cache and is gitignored, so a
Playwright install may be needed before `capture.mjs` will run.

A third script runs only when Claude Code itself updates, and rewrites the skills page's data:

```sh
python3 build/claude-code-built-in-skills/extract_skills.py \
    ~/.local/share/claude/versions/<version> \
    build/claude-code-built-in-skills/skills-data.json
```

It reads the CLI binary as text and never executes it. It finds each bundled skill's `ou({name:…})`
registration in the embedded JS bundle and resolves the prompt behind it, by four routes: a whole
`SKILL.md` module export, a single string constant, a joined section array, or a builder function
whose literals get stitched together. Interpolation it cannot resolve statically becomes `${…}`
rather than leaking minified JavaScript onto the page — see `expand()`.

## The one thing to get right: source vs. output

**Everything published is generated. Only `build/` is source.**

| Edit this | Not this |
| --- | --- |
| `build/claude-code-cheatsheet/claude-code-commands.html` | `claude-code-cheatsheet/index.html` (190KB, assembled) |
| `build/claude-code-built-in-skills/skills.html` (chrome) and `skills-data.json` (content) | `claude-code-built-in-skills/index.html` (500KB, assembled) |
| `build/build.py` (the `llms.txt` template, `PAGES`) | `llms.txt`, `llms-full.txt`, `sitemap.xml`, `robots.txt` |
| `build/og-hub.html`, `build/<slug>/og.html` | any `og.png` |
| `build/siteconf.py` | any URL, build number or date repeated in output |

Two exceptions, both hand-maintained and untouched by the build: the hub `index.html` and `404.html`.

`build/siteconf.py` is the only place URLs, `BUILD` (Claude Code version) and `UPDATED` (the date
stamped across the site) are defined. Change them there, never in a generated file.

## How build.py assembles a page

`build.py` does **exact string surgery** on the page source, and `swap()` raises `SystemExit` unless
each anchor is found exactly once. Both pages get the masthead, the coffee CSS block, a support
callout, and a machine-readable footer injected at literal anchors like `\n  <footer>`,
`\n  @media (prefers-reduced-motion`, and the page's content host (`<main id="sections"></main>` for
the cheatsheet, `<main id="skills"></main>` for the skills page).

Consequence: editing those regions of a page source breaks the build loudly. That is intended — fix
the anchor in `build.py` to match, and prefer changing the source over adding another swap. When a
whitespace-only diff appears in the output, it is almost always a `COFFEE_CSS` boundary, not a real
change.

The chrome is shared, not duplicated: `page_head()` builds every `<head>`, and `support()` /
`machine()` take the per-page copy and download links. Changing them changes both pages, so re-run
the build and check `git diff` on the cheatsheet before assuming a change is local to one page.

Data flows one way on both pages, and the counts are asserted at both ends:

```
claude-code-commands.html  ──capture.mjs──▶  extract.json    ──build.py──▶  commands.json, commands.md, llms-full.txt
     (builds cards in JS)                    prerender.json              ▶  claude-code-cheatsheet/index.html

claude-code CLI binary    ──extract_skills.py──▶  skills-data.json  ──build.py──▶  skills.json, skills.md, llms-full.txt
                                                                                ▶  claude-code-built-in-skills/index.html
```

`capture.mjs` throws unless it finds exactly `EXPECTED_COMMANDS = 143` and `EXPECTED_FLAGS = 57` and
all card anchors are unique; `build.py` re-checks the same two numbers against `prerender.json`, and
re-checks 35 skills against `skills-data.json`. **Changing either inventory means updating those
constants.**

Re-running `capture.mjs` rewrites every `og.png` with different bytes for a pixel-identical image,
because PNG output varies between Chromium versions. Don't commit that churn.

## Adding a third page

Write the source under `build/<slug>/`, carrying the four shared anchors above so the existing swaps
apply. Then add to `build.py`: a `build_<slug>_page()`, a `<slug>_ld()` for the structured data, its
`SRC` / `OUT` constants, an entry in `PAGES` (sitemap), and a line in the `llms.txt` template inside
`build_site_files()`. Add the URL and title to `siteconf.py` rather than repeating them. A page that
needs no generation can be a hand-written `<slug>/index.html` instead — but it still has to reach
`PAGES` and the `llms.txt` template, since those files are generated. Finally, add a card and a
`CollectionPage` list entry to the hand-maintained hub `index.html`.

## Site conventions

- **One self-contained file per page.** No bundler, no CDN, no webfont URL, no analytics — inline
  everything. A page must still work saved to disk and opened offline.
- **Content lives in the HTML, not in JavaScript.** Crawlers that feed AI answers don't run JS, so
  every card is baked in at build time; a page's own JS only filters what is already there. Don't
  introduce content that only exists after JS runs. On the skills page the prompts sit inside
  `<details>` — collapsed for readers, still present for crawlers — and the search index is built
  from `textContent` at load rather than shipped twice in a `data-` attribute.
- **Every entry keeps a stable anchor** (`#cmd-compact`, `#cli-claude-mcp`, `#skill-dataviz`) —
  deep-linked and unchanged between builds.
- Every page ships as HTML, Markdown and JSON, with `schema.org` metadata (`TechArticle`, `Dataset`,
  `BreadcrumbList`; the hub carries `WebSite` + `CollectionPage`).
- Both light and dark themes via `prefers-color-scheme`, plus `:root[data-theme=...]` overrides.
- `.nojekyll` and `404.html` only work at the repo root. `robots.txt` here is served at
  `/ai-snacks/robots.txt`, which crawlers do not read — it documents intent and would apply under a
  custom domain.

## Factual standard for page content

- **Check claims against the thing itself, not its documentation.** Where they disagree, follow the
  tool and say so on the page.
- **Say what was measured.** If a number came from a probe or a parse, the page explains how. The
  command index states that availability was established by probing the running CLI, and that
  commands which would have done real work were excluded rather than run — keep that true.
- **Reproduce, don't paraphrase.** The skills page prints prompt text as found. Where a prompt
  interpolates a run-time value the page shows `${…}` rather than inventing one, and where the
  interpolation chose between two phrasings it shows both and says so in "How this was read". If
  extraction ever gets lossier, update that section instead of quietly shipping a cleaner-looking
  page than the evidence supports.
