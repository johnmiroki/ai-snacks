# AI Snacks

Small, self-contained reference pages for the AI tools I use every day — each one a single
`index.html` with no build step, no dependencies, no analytics, and nothing loaded from another
server.

**→ [johnmiroki.github.io/ai-snacks](https://johnmiroki.github.io/ai-snacks/)**

## On the shelf

| Snack | What it is | Also as |
| --- | --- | --- |
| [Claude Code Command Index](https://johnmiroki.github.io/ai-snacks/claude-code-cheatsheet/) | Every slash command, bundled skill, `claude` subcommand and CLI flag in Claude Code 2.1.220 — extracted from the installed binary, probed for availability, linked to the official docs | [json](https://johnmiroki.github.io/ai-snacks/claude-code-cheatsheet/commands.json) · [md](https://johnmiroki.github.io/ai-snacks/claude-code-cheatsheet/commands.md) |

## Layout

```
ai-snacks/
├── index.html                          hub — lists every snack
├── 404.html                            shared not-found page
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
└── README.md
```

GitHub Pages serves the repo root, so a folder named `<slug>` is reachable at
`johnmiroki.github.io/ai-snacks/<slug>/`.

## Readable by people, machines and crawlers

Every page ships three ways: as HTML for people, as Markdown and JSON for agents, and with
`schema.org` metadata for search engines.

- **Content lives in the HTML.** Pages that build themselves with JavaScript are invisible to
  crawlers that do not run it — which is most of the ones that feed AI answers. The command index
  is rendered once at build time and baked into the file; its JavaScript only filters what is
  already there.
- **Every entry has a stable anchor.** `#cmd-compact`, `#cli-mcp-add` — deep-linkable and unchanged
  between builds.
- **`llms.txt`** indexes the site for language models; **`llms-full.txt`** is the whole thing in one
  fetch.
- **Structured data.** The hub carries `WebSite` + `CollectionPage`; each page carries `TechArticle`,
  a `Dataset` pointing at its JSON, and a `BreadcrumbList`.

`robots.txt` here is served at `/ai-snacks/robots.txt`. Crawlers only read the one at the domain
root, which belongs to the `johnmiroki.github.io` repo — so this file documents intent and would
become effective under a custom domain, but does not currently govern crawling. Submit
`sitemap.xml` through Search Console rather than relying on the robots pointer.

## Adding a snack

1. Create `<slug>/index.html` — one self-contained file. Include `<meta charset="utf-8">`,
   a viewport meta, both light and dark themes via `prefers-color-scheme`, and a `<link rel=
   "canonical">`.
2. In the root `index.html`, copy the `<a class="snack">` block and edit the href, title,
   description, and facts.
3. Add a row to the table above, a `<url>` entry to `sitemap.xml`, and a bullet to `llms.txt`.
4. Commit and push to `main`. Pages redeploys in about 20 seconds.

## House rules

- **One file per page.** No bundler, no CDN, no webfont URL — inline everything. A snack should
  still work saved to disk and opened offline.
- **Check claims against the thing itself,** not its documentation. Where the two disagree, follow
  the tool and say so on the page.
- **Say what was measured.** If a number came from a probe or a parse, the page should explain how.

---

If one of these saved you some time: [buy me a coffee](https://buymeacoffee.com/john42) ☕
