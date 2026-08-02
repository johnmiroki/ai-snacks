# Claude Code Command Index

> Every slash command, bundled skill, `claude` CLI subcommand and launch flag in Claude Code build 2.1.220. Extracted from the installed binary rather than the documentation, probed against the running CLI to establish what is actually reachable, and linked entry by entry to the official docs.

- Canonical page: https://johnmiroki.github.io/ai-snacks/claude-code-cheatsheet/
- Machine-readable: https://johnmiroki.github.io/ai-snacks/claude-code-cheatsheet/commands.json
- Claude Code build: 2.1.220
- Last updated: 2026-07-26
- License: CC BY 4.0

## Totals

| Group | Count | What it means |
| --- | ---: | --- |
| Native slash commands | 96 | Compiled into the binary's own command registry |
| Bundled skills | 23 | Prompt-driven skills shipped inside the binary |
| CLI subcommands | 14 | Subcommands of the `claude` executable |
| Hidden commands | 10 | Registered and runnable but withheld from `/help` |
| Launch flags | 57 | Options passed to `claude` at startup |
| Linked to official docs | 131 | The rest have no official page |
| Defined but not registered | 11 | Typing them returns `Unknown command` |

## How this was established

Names, descriptions, aliases and argument hints come from the command registry inside `~/.local/share/claude/versions/2.1.220`. CLI subcommands and flags come from `claude --help` on the same build. Availability was tested, not inferred: each command was probed against the running CLI and classified by its response — real output means registered and enabled, *isn't available in this environment* means registered but gated, and *Unknown command* means never registered at all. Commands that would have executed real work were excluded from the probe rather than run.

## Session & context

Steering the conversation you are in right now. 19 entries.

- **`/help`** — Show help and available commands. [docs](https://code.claude.com/docs/en/commands#all-commands)
- **`/clear`** `[name]` *(aliases: `reset`, `new`)* — Start a new session with empty context; the previous session stays on disk and is resumable with /resume. [docs](https://code.claude.com/docs/en/sessions)
- **`/compact`** `<optional custom summarization instructions>` — Free up context by summarizing the conversation so far. [docs](https://code.claude.com/docs/en/context-window)
- **`/autocompact`** `[auto|<tokens>]` — Set how full the context gets before auto-summarizing. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/context-window)
- **`/context`** `[all]` — Visualize current context usage as a colored grid. [docs](https://code.claude.com/docs/en/context-window)
- **`/resume`** `[conversation id or search term]` *(aliases: `continue`)* — Resume a previous conversation. [docs](https://code.claude.com/docs/en/sessions)
- **`/rewind`** *(aliases: `checkpoint`, `undo`)* — Restore the code and/or conversation to a previous point. [docs](https://code.claude.com/docs/en/checkpointing)
- **`/branch`** `[name]` — Create a branch of the current conversation at this point. [docs](https://code.claude.com/docs/en/sessions)
- **`/rename`** `[name]` *(aliases: `name`)* — Rename the current conversation. [docs](https://code.claude.com/docs/en/sessions)
- **`/export`** `[filename]` — Export the current conversation to a file or clipboard. [docs](https://code.claude.com/docs/en/commands#all-commands)
- **`/copy`** `[n]` — Copy Claude's last response to clipboard (or /copy N for the Nth-latest). [docs](https://code.claude.com/docs/en/commands#all-commands)
- **`/plan`** `[open|share|<description>]` — Enable plan mode or view the current session plan. [docs](https://code.claude.com/docs/en/permission-modes)
- **`/goal`** `[<condition> | clear]` — Set a goal Claude checks before stopping. [docs](https://code.claude.com/docs/en/goal)
- **`/focus`** — Toggle focus view: just your prompt, summary, and response. [docs](https://code.claude.com/docs/en/commands#all-commands)
- **`/brief`** — Toggle brief-only mode. *(registered only under a feature gate)*
- **`/recap`** — Generate a one-line session recap now. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/commands#all-commands)
- **`/memory`** — Open a memory file in your editor. [docs](https://code.claude.com/docs/en/memory)
- **`/pause-memory`** *(aliases: `memory-pause`, `toggle-memory`)* — Pause automemory for this session. [docs](https://code.claude.com/docs/en/memory)
- **`/exit`** *(aliases: `quit`)* — End the session. [docs](https://code.claude.com/docs/en/commands#all-commands)

## Model & reasoning

How much horsepower each turn gets. 4 entries.

- **`/model`** `<model>` — Set the AI model for Claude Code. [docs](https://code.claude.com/docs/en/model-config)
- **`/effort`** `<level>` — Set effort level for model usage (low, medium, high, xhigh, max). [docs](https://code.claude.com/docs/en/model-config)
- **`/fast`** `[on|off]` — Toggle fast mode — Opus with faster output, not a smaller model. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/fast-mode)
- **`/advisor`** — Let Claude consult a stronger model at key moments. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/advisor)

## Workspace & code

Directories, project memory, and your working diff. 11 entries.

- **`/init`** — Initialize a new CLAUDE.md file with codebase documentation (the newer variant also scaffolds skills and hooks). [docs](https://code.claude.com/docs/en/memory)
- **`/add-dir`** `<path>` — Add a new working directory. [docs](https://code.claude.com/docs/en/commands#all-commands)
- **`/cd`** `<path>` — Move this session to a new working directory. [docs](https://code.claude.com/docs/en/commands#all-commands)
- **`/diff`** — View uncommitted changes and per-turn diffs. [docs](https://code.claude.com/docs/en/commands#all-commands)
- **`/review`** `[pr number]` — Review a GitHub pull request; for your working diff use /code-review. [docs](https://code.claude.com/docs/en/code-review#review-a-diff-locally)
- **`/code-review`** `[since]` — Review the changes since a fixed point along two axes — repo standards and the originating spec — in parallel sub-agents. [docs](https://code.claude.com/docs/en/code-review)
- **`/security-review`** — Analyze pending changes on the current branch for security vulnerabilities — injection, auth issues, data exposure. [docs](https://code.claude.com/docs/en/commands#all-commands)
- **`/simplify`** — Review changed code for reuse, simplification and efficiency, then apply the fixes. [docs](https://code.claude.com/docs/en/commands#all-commands)
- **`/batch`** — Plan a large change; background agents each open a PR. [docs](https://code.claude.com/docs/en/commands#all-commands)
- **`/run`** — Launch this project's app to see your change working. [docs](https://code.claude.com/docs/en/commands#all-commands)
- **`/run-skill-generator`** — Create a skill that knows how to run this project's app. [docs](https://code.claude.com/docs/en/commands#all-commands)

## Config & environment

Settings, permissions, hooks, and how the terminal behaves. 22 entries.

- **`/config`** `[key=value]` *(aliases: `settings`)* — Open settings. [docs](https://code.claude.com/docs/en/settings)
- **`/permissions`** *(aliases: `allowed-tools`)* — Manage allow and deny tool permission rules. [docs](https://code.claude.com/docs/en/permissions)
- **`/sandbox`** — Toggle sandbox mode for the Bash tool; available on supported platforms only. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/sandboxing)
- **`/hooks`** — View hook configurations for tool events. [docs](https://code.claude.com/docs/en/hooks)
- **`/update-config`** — Change settings: hooks, permissions, environment variables. [docs](https://code.claude.com/docs/en/settings)
- **`/fewer-permission-prompts`** — Pre-approve safe read-only commands based on your usage. [docs](https://code.claude.com/docs/en/permissions)
- **`/statusline`** — Set up Claude Code's status line UI. [docs](https://code.claude.com/docs/en/statusline)
- **`/theme`** — Change the theme. [docs](https://code.claude.com/docs/en/commands#all-commands)
- **`/color`** — Set the prompt bar color for this session. [docs](https://code.claude.com/docs/en/commands#all-commands)
- **`/tui`** `[default|fullscreen]` — Set the terminal UI renderer. [docs](https://code.claude.com/docs/en/fullscreen)
- **`/terminal-setup`** — Configure terminal key bindings — Shift+Enter or Option+Enter for newlines. [docs](https://code.claude.com/docs/en/terminal-config)
- **`/keybindings`** — Open your keyboard shortcuts file. [docs](https://code.claude.com/docs/en/keybindings)
- **`/keybindings-help`** — Customize keyboard shortcuts, rebind keys, and add chord bindings. [docs](https://code.claude.com/docs/en/keybindings)
- **`/scroll-speed`** — Adjust mouse wheel scroll speed. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/commands#all-commands)
- **`/voice`** `[hold|tap|off]` — Toggle voice mode. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/voice-dictation)
- **`/wellbeing`** *(aliases: `breaks`, `break-reminder`, `downtime`)* — Configure optional break reminders and quiet-hours nudges. *(registered only under a feature gate)*
- **`/import`** `[codex|gemini] [--dry-run]` — Import config from another AI coding agent. *(registered only under a feature gate)*
- **`/ide`** `[open]` — Manage IDE integrations and show status. [docs](https://code.claude.com/docs/en/commands#all-commands)
- **`/doctor`** *(aliases: `checkup`)* — Health-check your setup and fix issues: installation, unused extensions, duplicates. [docs](https://code.claude.com/docs/en/commands#all-commands)
- **`/debug`** — Turn on debug logging and investigate problems. [docs](https://code.claude.com/docs/en/debug-your-config)
- **`/setup-bedrock`** — Reconfigure Amazon Bedrock authentication, region, or model pins. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/amazon-bedrock)
- **`/setup-vertex`** — Reconfigure Google Vertex AI authentication, project, region, or model pins. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/google-vertex-ai)

## Extensions

MCP servers, plugins, and skills. 7 entries.

- **`/mcp`** `[reconnect|enable|disable [<server>|all]]` — Manage MCP servers. [docs](https://code.claude.com/docs/en/mcp)
- **`/plugin`** *(aliases: `plugins`, `marketplace`)* — Manage Claude Code plugins. [docs](https://code.claude.com/docs/en/plugins)
- **`/reload-plugins`** `[--force]` — Activate pending plugin changes in the current session. [docs](https://code.claude.com/docs/en/plugins)
- **`/skills`** — List available skills. [docs](https://code.claude.com/docs/en/skills)
- **`/reload-skills`** — Pick up skills added or changed on disk during this session. [docs](https://code.claude.com/docs/en/skills)
- **`/skill-doctor`** — Show which loaded skills are unused and costing context. *(**typing it returns `Unknown command`** — Registered only when the tengu_lantern_prism feature gate is on. Works with CLAUDE_CODE_LANTERN_PRISM=1 set in the environment)* [docs](https://code.claude.com/docs/en/skills)
- **`/agents`** — Removed. Ask Claude to create or manage subagents, or edit .claude/agents/ directly. [docs](https://code.claude.com/docs/en/sub-agents)

## Background & parallel work

Sending work off and getting it back. 10 entries.

- **`/background`** `[prompt]` *(aliases: `bg`)* — Send this session to the background and free the terminal. [docs](https://code.claude.com/docs/en/agents)
- **`/stop`** — Stop this background session; transcript and worktree are kept. [docs](https://code.claude.com/docs/en/agents)
- **`/tasks`** *(aliases: `bashes`)* — View and manage everything running in the background. [docs](https://code.claude.com/docs/en/agent-view)
- **`/fork`** `<directive>` — Spawn a background agent that inherits the full conversation. [docs](https://code.claude.com/docs/en/agents)
- **`/subtask`** `<task>` — Send a subagent off with your full context; its result comes back here. [docs](https://code.claude.com/docs/en/sub-agents)
- **`/workflows`** — Browse running and completed workflows. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/workflows)
- **`/loops`** — List, create, and delete loops. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/scheduled-tasks)
- **`/loop`** `[interval] [prompt]` *(aliases: `proactive`)* — Repeat a prompt or command on an interval, e.g. /loop 5m /foo. [docs](https://code.claude.com/docs/en/scheduled-tasks)
- **`/daemon`** — Manage background services and routines. *(**typing it returns `Unknown command`** — Not registered by the terminal CLI; the `claude daemon` subcommand works)* [docs](https://code.claude.com/docs/en/agent-view)
- **`/schedule`** *(aliases: `routines`)* — Create and manage routines: cloud agents on a schedule. [docs](https://code.claude.com/docs/en/routines)

## Cloud, web & devices

Moving a session between the terminal, the web, and your phone. 14 entries.

- **`/teleport`** *(aliases: `tp`)* — Resume a Claude Code session from claude.ai. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/claude-code-on-the-web)
- **`/session`** *(aliases: `remote`)* — Show cloud session URL and QR code. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/claude-code-on-the-web)
- **`/remote-control`** *(aliases: `rc`)* — Control this session from your phone or claude.ai/code. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/remote-control)
- **`/remote-env`** — Choose the default environment for cloud agents. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/commands#all-commands)
- **`/web-setup`** — Set up Claude Code on the web with your GitHub account. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/web-quickstart)
- **`/desktop`** *(aliases: `app`)* — Continue the current session in Claude Desktop. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/desktop)
- **`/ultraplan`** `<prompt>` — Draft an editable plan in Claude Code on the web. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/ultraplan)
- **`/ultrareview`** `[target]` — Find and verify bugs in your branch using Claude Code on the web. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/ultrareview)
- **`/autofix-pr`** — Monitor and autofix any issues with the current PR. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/commands#all-commands)
- **`/install-github-app`** — Set up Claude GitHub Actions for a repository. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/github-actions)
- **`/install-slack-app`** — Install the Claude Slack app. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/slack)
- **`/chrome`** — Open Claude in Chrome settings. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/chrome)
- **`/claude-in-chrome`** — Let Claude browse and interact with pages in your Chrome. *(**typing it returns `Unknown command`** — Not registered by the terminal CLI)* [docs](https://code.claude.com/docs/en/chrome)
- **`/setup-cowork`** — Guided setup — pick a role, install a plugin, try a skill, connect a tool. *(**typing it returns `Unknown command`** — Not registered by the terminal CLI)*

## Design & artifacts

Publishing pages and syncing design systems. 10 entries.

- **`/artifacts`** — Browse your published and shared artifacts. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/artifacts)
- **`/artifact-design`** — Design guidance and fundamentals for Artifacts. *(**typing it returns `Unknown command`** — Not registered by the terminal CLI)* [docs](https://code.claude.com/docs/en/artifacts)
- **`/artifact-capabilities`** — Runtime capabilities for published Artifacts. *(**typing it returns `Unknown command`** — Not registered by the terminal CLI)* [docs](https://code.claude.com/docs/en/artifacts)
- **`/plan-artifact`** — Publish a plan as a shareable Artifact. *(**typing it returns `Unknown command`** — Not registered by the terminal CLI)* [docs](https://code.claude.com/docs/en/artifacts)
- **`/whiteboard`** — Sketch on a whiteboard Artifact you can send to Claude. *(**typing it returns `Unknown command`** — Not registered by the terminal CLI)* [docs](https://code.claude.com/docs/en/artifacts)
- **`/workshop`** — Workshop a document through artifact decisions. *(**typing it returns `Unknown command`** — Not registered by the terminal CLI)* [docs](https://code.claude.com/docs/en/artifacts)
- **`/dataviz`** — Chart, dashboard and palette guidance for any visualization you build. [docs](https://code.claude.com/docs/en/commands#all-commands)
- **`/design`** `consent | revoke` — Grant or revoke Claude agent access to your Design projects. *(registered only under a feature gate)*
- **`/design-login`** — Authorize design-system access for /design-sync with your claude.ai account. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/commands#all-commands)
- **`/design-sync`** — Push your design system components to claude.ai/design. [docs](https://code.claude.com/docs/en/commands#all-commands)

## Account, usage & install

Who you are signed in as, what it costs, and keeping current. 14 entries.

- **`/login`** — Sign in with your Anthropic account, or switch accounts. [docs](https://code.claude.com/docs/en/authentication)
- **`/logout`** — Sign out from your Anthropic account. [docs](https://code.claude.com/docs/en/authentication)
- **`/status`** — Show Claude Code status including version, model, account, API connectivity, and tool statuses. [docs](https://code.claude.com/docs/en/commands#all-commands)
- **`/usage`** *(aliases: `cost`, `stats`)* — Show session cost, plan usage, and activity stats. [docs](https://code.claude.com/docs/en/costs)
- **`/explain-usage`** — See where this session's tokens went, in plain words. *(**typing it returns `Unknown command`** — Not registered by the terminal CLI)* [docs](https://code.claude.com/docs/en/costs)
- **`/insights`** — Generate a report analyzing your Claude Code sessions. [docs](https://code.claude.com/docs/en/analytics)
- **`/usage-credits`** — Configure usage credits or request them from your admin when you hit a limit. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/costs)
- **`/upgrade`** — Upgrade to Max for higher rate limits and more Opus. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/commands#all-commands)
- **`/passes`** — Share a free week of Claude Code with friends and earn usage credits. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/commands#all-commands)
- **`/privacy-settings`** — View and update your privacy settings. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/data-usage)
- **`/version`** — Show this session's version — autoupdate may have a newer one. [docs](https://code.claude.com/docs/en/setup)
- **`/release-notes`** — View release notes. [docs](https://code.claude.com/docs/en/changelog)
- **`/update`** *(aliases: `restart`)* — Switch to the latest version; the conversation continues. [docs](https://code.claude.com/docs/en/setup)
- **`/install`** `[options]` — Install Claude Code native build. *(**typing it returns `Unknown command`** — Not registered by the terminal CLI; the `claude install` subcommand works)* [docs](https://code.claude.com/docs/en/setup)

## Help, feedback & extras

Learning the tool, reporting problems, and a few indulgences. 8 entries.

- **`/claude-api`** — Build and debug apps that use the Claude API. [docs](https://code.claude.com/docs/en/commands#all-commands)
- **`/powerup`** — Discover Claude Code features through quick interactive lessons. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/commands#all-commands)
- **`/team-onboarding`** — Help teammates ramp on Claude Code with a guide from your usage. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/commands#all-commands)
- **`/mobile`** *(aliases: `ios`, `android`)* — Show QR code to download the Claude mobile app. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/mobile)
- **`/bug`** `[report]` *(aliases: `share`)* — Report a bug or share your conversation. [docs](https://code.claude.com/docs/en/commands#all-commands)
- **`/feedback`** `[report]` — Send feedback to Anthropic or report a bug. [docs](https://code.claude.com/docs/en/commands#all-commands)
- **`/stickers`** — Order Claude Code stickers. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/commands#all-commands)
- **`/radio`** — Listen to Claude FM lo-fi radio. *(registered only under a feature gate)* [docs](https://code.claude.com/docs/en/commands#all-commands)

## Terminal CLI

Subcommands of the claude executable, run from your shell. 14 entries.

- **`claude`** `[prompt]` — Start an interactive session in the current directory. [docs](https://code.claude.com/docs/en/cli-reference)
- **`claude -p`** `<prompt>` *(aliases: `--print`)* — Print mode: run a prompt non-interactively and exit, useful for pipes and scripts. [docs](https://code.claude.com/docs/en/cli-reference)
- **`claude agents`** `[options]` — Manage background agents. [docs](https://code.claude.com/docs/en/cli-reference)
- **`claude auth`** — Manage authentication. [docs](https://code.claude.com/docs/en/cli-reference)
- **`claude auto-mode`** — Inspect or reset auto mode classifier configuration. [docs](https://code.claude.com/docs/en/cli-reference)
- **`claude doctor`** — Check the health of your installation, reading settings without a trust prompt. [docs](https://code.claude.com/docs/en/cli-reference)
- **`claude gateway`** `[options]` — Run the enterprise auth/telemetry gateway. [docs](https://code.claude.com/docs/en/cli-reference)
- **`claude install`** `[target]` — Install the native build — stable, latest, or a specific version. [docs](https://code.claude.com/docs/en/cli-reference)
- **`claude mcp`** — Configure and manage MCP servers. [docs](https://code.claude.com/docs/en/cli-reference)
- **`claude plugin`** *(aliases: `plugins`)* — Manage Claude Code plugins. [docs](https://code.claude.com/docs/en/cli-reference)
- **`claude project`** — Manage Claude Code project state. [docs](https://code.claude.com/docs/en/cli-reference)
- **`claude setup-token`** — Set up a long-lived authentication token, requires a Claude subscription. [docs](https://code.claude.com/docs/en/cli-reference)
- **`claude ultrareview`** `[target]` — Run a cloud-hosted multi-agent code review of the current branch or a PR and print the findings. [docs](https://code.claude.com/docs/en/cli-reference)
- **`claude update`** *(aliases: `upgrade`)* — Check for updates and install if available. [docs](https://code.claude.com/docs/en/cli-reference)

## Hidden & internal

Present in the registry but suppressed from /help — listed for completeness. 10 entries.

- **`/btw`** `[question]` — Ask a quick side question without interrupting the main conversation. [docs](https://code.claude.com/docs/en/commands#all-commands)
- **`/auto-mode-setup`** `[--wizard ...]` — Set up and customise auto mode — environment context, plus optional rule tweaks. [docs](https://code.claude.com/docs/en/auto-mode-config)
- **`/heapdump`** — Dump the JS heap to ~/Desktop. [docs](https://code.claude.com/docs/en/commands#all-commands)
- **`/design-consent`** — Grant Claude agent access to your Design projects.
- **`/design-revoke`** — Revoke Claude agent access to your Design projects.
- **`/extra-usage`** — Renamed to /usage-credits.
- **`/pro-trial-expired`** — Options shown when the Pro plan Claude Code trial has ended.
- **`/rate-limit-options`** — Show options when rate limit is reached.
- **`/__remote-workflow`** — Run the workflow script delivered in this session environment — server-launched sessions only.
- **`/workflow-launch-exec`** — Execute a server-launched workflow handoff — workflow_launch event sessions only.

## CLI flags

Passed to `claude` at launch. 57 in total.

| Flag | What it does |
| --- | --- |
| `--add-dir <dirs...>` | Additional directories to allow tool access to |
| `--agent <agent>` | Agent for the current session; overrides the 'agent' setting |
| `--agents <json>` | JSON object defining custom agents |
| `--allow-dangerously-skip-permissions` | Make permission bypass available as an option without enabling it by default |
| `--allowedTools <tools...>` | Comma or space-separated list of tool names to allow, e.g. "Bash(git *) Edit" |
| `--append-system-prompt <prompt>` | Append text to the default system prompt |
| `--ax-screen-reader` | Render screen-reader friendly output: flat text, no borders or animations |
| `--bg, --background` | Start as a background agent and return immediately |
| `--bare` | Minimal mode: skip hooks, LSP, plugin sync, auto-memory, keychain reads and CLAUDE.md discovery |
| `--betas <betas...>` | Beta headers to include in API requests (API key users only) |
| `--brief` | Enable the SendUserMessage tool for agent-to-user communication |
| `--chrome / --no-chrome` | Enable or disable the Claude in Chrome integration |
| `-c, --continue` | Continue the most recent conversation in the current directory |
| `--dangerously-skip-permissions` | Bypass all permission checks; for sandboxes with no internet access |
| `-d, --debug [filter]` | Debug mode with optional category filtering, e.g. "api,hooks" or "!1p,!file" |
| `--debug-file <path>` | Write debug logs to a specific path, implicitly enabling debug mode |
| `--disable-slash-commands` | Disable all skills |
| `--disallowedTools <tools...>` | Comma or space-separated list of tool names to deny |
| `--effort <level>` | Effort level for the session: low, medium, high, xhigh, max |
| `--exclude-dynamic-system-prompt-sections` | Move per-machine sections into the first user message to improve prompt-cache reuse |
| `--fallback-model <model>` | Fall back to these models when the default is overloaded (--print only) |
| `--file <specs...>` | File resources to download at startup, as file_id:relative_path |
| `--fork-session` | When resuming, create a new session ID instead of reusing the original |
| `--forward-subagent-text` | Forward subagent text and thinking as messages with parent_tool_use_id set |
| `--from-pr [value]` | Resume a session linked to a PR by number or URL, or open a picker |
| `-h, --help` | Display help for command |
| `--ide` | Automatically connect to the IDE on startup if exactly one is available |
| `--include-hook-events` | Include all hook lifecycle events in the output stream |
| `--include-partial-messages` | Include partial message chunks as they arrive |
| `--input-format <format>` | Input format with --print: text (default) or stream-json |
| `--json-schema <schema>` | JSON Schema for structured output validation |
| `--max-budget-usd <amount>` | Maximum dollar amount to spend on API calls (--print only) |
| `--mcp-config <configs...>` | Load MCP servers from JSON files or strings |
| `--model <model>` | Model for the session: an alias like 'fable', 'opus', 'sonnet', or a full model name |
| `-n, --name <name>` | Display name for the session, shown in the prompt box, /resume picker and title |
| `--no-session-persistence` | Do not save the session to disk; it cannot be resumed (--print only) |
| `--output-format <format>` | Output format with --print: text, json, or stream-json |
| `--permission-mode <mode>` | acceptEdits, auto, bypassPermissions, manual, dontAsk, or plan |
| `--plugin-dir <path>` | Load a plugin from a directory or .zip for this session only (repeatable) |
| `--plugin-url <url>` | Fetch a plugin .zip from a URL for this session only (repeatable) |
| `-p, --print` | Print the response and exit; skips the workspace trust dialog |
| `--prompt-suggestions [value]` | Emit a predicted next user prompt after each turn |
| `--remote-control [name]` | Start an interactive session with Remote Control enabled |
| `--remote-control-session-name-prefix <prefix>` | Prefix for auto-generated Remote Control session names |
| `--replay-user-messages` | Re-emit user messages from stdin back on stdout for acknowledgment |
| `-r, --resume [value]` | Resume a conversation by session ID, or open a picker with an optional search term |
| `--safe-mode` | Start with all customizations disabled; useful for troubleshooting a broken config |
| `--session-id <uuid>` | Use a specific session ID for the conversation |
| `--setting-sources <sources>` | Comma-separated setting sources to load: user, project, local |
| `--settings <file-or-json>` | Path to a settings JSON file, or a JSON string of additional settings |
| `--strict-mcp-config` | Only use MCP servers from --mcp-config, ignoring all other MCP configuration |
| `--system-prompt <prompt>` | System prompt to use for the session |
| `--tmux` | Create a tmux session for the worktree; requires --worktree |
| `--tools <tools...>` | Available tools from the built-in set; "" disables all, "default" uses all |
| `--verbose` | Override the verbose mode setting from config |
| `-v, --version` | Output the version number |
| `-w, --worktree [name]` | Create a new git worktree for this session |

---

From [AI Snacks](https://johnmiroki.github.io/ai-snacks/) by johnmiroki. If it saved you time, [buy me a coffee](https://buymeacoffee.com/john42).
