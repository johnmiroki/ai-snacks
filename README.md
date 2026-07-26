# AI Snacks

Small, self-contained reference pages for the AI tools I use every day — each one a single
`index.html` with no build step, no dependencies, no analytics, and nothing loaded from another
server.

**→ [johnmiroki.github.io/ai-snacks](https://johnmiroki.github.io/ai-snacks/)**

## On the shelf

| Snack | What it is |
| --- | --- |
| [Claude Code Command Index](https://johnmiroki.github.io/ai-snacks/claude-code-cheatsheet/) | Every slash command, bundled skill, `claude` subcommand and CLI flag in Claude Code 2.1.220 — extracted from the installed binary, probed for availability, linked to the official docs |

## Layout

```
ai-snacks/
├── index.html                          hub — lists every snack
├── 404.html                            shared not-found page
├── claude-code-cheatsheet/index.html   one folder per snack
└── README.md
```

GitHub Pages serves the repo root, so a folder named `<slug>` is reachable at
`johnmiroki.github.io/ai-snacks/<slug>/`.

## Adding a snack

1. Create `<slug>/index.html` — one self-contained file. Include `<meta charset="utf-8">`,
   a viewport meta, and both light and dark themes via `prefers-color-scheme`.
2. In the root `index.html`, copy the `<a class="snack">` block and edit the href, title,
   description, and facts.
3. Add a row to the table above.
4. Commit and push to `main`. Pages redeploys in about 20 seconds.

## House rules

- **One file per page.** No bundler, no CDN, no webfont URL — inline everything. A snack should
  still work saved to disk and opened offline.
- **Check claims against the thing itself,** not its documentation. Where the two disagree, follow
  the tool and say so on the page.
- **Say what was measured.** If a number came from a probe or a parse, the page should explain how.

---

If one of these saved you some time: [buy me a coffee](https://buymeacoffee.com/john42) ☕
