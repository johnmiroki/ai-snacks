"""Shared constants for the ai-snacks build."""

ORIGIN = "https://johnmiroki.github.io"
BASE = ORIGIN + "/ai-snacks/"
CHEATSHEET = BASE + "claude-code-cheatsheet/"
SKILLS = BASE + "claude-code-built-in-skills/"
CODEX = BASE + "codex-cheatsheet/"
REPO = "https://github.com/johnmiroki/ai-snacks"
BMC = "https://buymeacoffee.com/john42"
AUTHOR = "johnmiroki"

# Per-page, not site-wide: a page's stamp is the day its own content last changed, so adding
# one page does not restamp the others as modified when their bytes are identical.
UPDATED = "2026-07-26"
CODEX_UPDATED = "2026-08-02"
SITE_UPDATED = max(UPDATED, CODEX_UPDATED)

BUILD = "2.1.220"
CODEX_BUILD = "0.146.0"

SITE_NAME = "AI Snacks"
SITE_DESC = ("Small, self-contained reference pages for AI developer tools. "
             "One HTML file each, checked against the tool rather than its documentation.")

CS_TITLE = "Claude Code Command Index — 143 Slash Commands & CLI Flags"
CS_DESC = ("Every Claude Code command in build 2.1.220: 96 native slash commands, 23 bundled "
           "skills, 14 CLI subcommands and 57 launch flags. Searchable and linked to the docs.")

SK_TITLE = "Claude Code Bundled Skills — All 35 Prompts, In Full"
SK_DESC = ("The complete prompt behind every skill bundled inside Claude Code build 2.1.220 — "
           "all 35 of them, read out of the shipped binary and reproduced verbatim.")

CX_TITLE = "Codex CLI Command Index — 122 Commands, Flags & Feature Switches"
CX_DESC = ("Every OpenAI Codex CLI command in build 0.146.0: 46 slash commands, 68 subcommands, "
           "21 launch flags and 100 feature flags. Read from the running CLI, not the docs.")
