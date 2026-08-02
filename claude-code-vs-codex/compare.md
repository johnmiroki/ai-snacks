# Claude Code vs Codex CLI

> Claude Code 2.1.220 and OpenAI Codex CLI 0.146.0, command for command. 43 jobs both ship a command for, quoted in each build's own words; 69 Claude Code commands and 55 Codex commands with no counterpart; and 13 capability differences a command list cannot show.

- Canonical page: https://johnmiroki.github.io/ai-snacks/claude-code-vs-codex/
- Machine-readable: https://johnmiroki.github.io/ai-snacks/claude-code-vs-codex/compare.json
- Claude Code build: 2.1.220 · Codex CLI build: 0.146.0
- Last updated: 2026-08-02
- License: CC BY 4.0

## How this was established

The command halves are set operations over the two inventories published on this site, each read out of its installed build rather than its documentation. Every description below is the string that build carries, unedited.

What was **not** measured is the pairing: deciding that two commands do the same job is a judgement made by hand, which is why both descriptions are printed rather than summarised — so the judgement can be checked. The two unpaired lists are then the computed complement of the pairing, so every command in either inventory appears exactly once, and a bad pairing shows up as a missing entry rather than a silent one.

The capability section was measured separately, from `claude --help`, `codex --help` and the on-disk config layout of both tools on one machine. Each row names its evidence. The closing section is opinion and says so.

## The same job, both tools

43 jobs. Each tool's own description of its own command.

### Start it

  - **Claude Code:**
    - `claude` — Start an interactive session in the current directory
  - **Codex:**
    - `codex` — Start an interactive session in the current directory

  Word for word the same sentence in both builds — the only entry on this page where the two descriptions are identical.

### Start over

  - **Claude Code:**
    - `/clear` — Start a new session with empty context; the previous session stays on disk and is resumable with /resume
  - **Codex:**
    - `/new` — start a new chat during a conversation
    - `/clear` — clear the terminal and start a new chat

  Codex splits it in two: /new starts the chat over, /clear also wipes the terminal. Claude Code keeps the old session on disk either way.

### Reclaim context

  - **Claude Code:**
    - `/compact` — Free up context by summarizing the conversation so far
    - `/autocompact` — Set how full the context gets before auto-summarizing
    - `/context` — Visualize current context usage as a colored grid
  - **Codex:**
    - `/compact` — summarize conversation to prevent hitting the context limit

  Same summarise-and-continue move. Claude Code additionally lets you set the trigger threshold and draw the context as a grid; Codex reports usage through /status.

### Pick up an old session

  - **Claude Code:**
    - `/resume` — Resume a previous conversation
  - **Codex:**
    - `/resume` — resume a saved chat
    - `codex resume` — Resume a previous interactive session (picker by default; use --last to continue the most recent)

  Both offer a picker. Codex can also do it from the shell before launch, and takes --last to skip the picker.

### Branch the conversation

  - **Claude Code:**
    - `/branch` — Create a branch of the current conversation at this point
  - **Codex:**
    - `/fork` — fork the current chat
    - `codex fork` — Fork a previous interactive session (picker by default; use --last to fork the most recent)

  Different word, same idea — keep this history, continue down a second path. Claude Code's /fork is not this; it spawns a background agent.

### Ask a side question

  - **Claude Code:**
    - `/btw` — Ask a quick side question without interrupting the main conversation
  - **Codex:**
    - `/side` — start a side conversation in an ephemeral fork

  Codex's /side answers to the alias btw — the same name Claude Code gives the command, which it keeps out of /help.

### Rename the session

  - **Claude Code:**
    - `/rename` — Rename the current conversation
  - **Codex:**
    - `/rename` — rename the current thread

### Copy the last answer

  - **Claude Code:**
    - `/copy` — Copy Claude's last response to clipboard (or /copy N for the Nth-latest)
  - **Codex:**
    - `/copy` — copy last response as markdown

  Claude Code takes an index — /copy 3 for the third-latest.

### What is this session doing

  - **Claude Code:**
    - `/status` — Show Claude Code status including version, model, account, API connectivity, and tool statuses
  - **Codex:**
    - `/status` — show current session configuration and token usage

  Codex folds token usage into the same command; Claude Code puts that in /context and /usage.

### Leave

  - **Claude Code:**
    - `/exit` — End the session
  - **Codex:**
    - `/exit` — exit Codex

### Choose the model

  - **Claude Code:**
    - `/model` — Set the AI model for Claude Code
  - **Codex:**
    - `/model` — choose what model and reasoning effort to use

### Set reasoning effort

  - **Claude Code:**
    - `/effort` — Set effort level for model usage (low, medium, high, xhigh, max)
  - **Codex:**
    - `/model` — choose what model and reasoning effort to use

  Codex has no separate command — its own /model description says it picks “what model and reasoning effort to use”. Claude Code splits the two.

### Trade usage for speed

  - **Claude Code:**
    - `/fast` — Toggle fast mode — Opus with faster output, not a smaller model
  - **Codex:**
    - `/fast` — 1.5x speed, increased usage

  Same name, and both are explicit that you are not being downgraded to a smaller model — you are paying for speed.

### Plan before touching anything

  - **Claude Code:**
    - `/plan` — Enable plan mode or view the current session plan
  - **Codex:**
    - `/plan` — switch to Plan mode

### Set a goal to hold to

  - **Claude Code:**
    - `/goal` — Set a goal Claude checks before stopping
  - **Codex:**
    - `/goal` — set or view the goal for a long-running task

  Claude Code checks it before stopping; Codex frames it as the goal for a long-running task.

### Write the project instructions file

  - **Claude Code:**
    - `/init` — Initialize a new CLAUDE.md file with codebase documentation (the newer variant also scaffolds skills and hooks)
  - **Codex:**
    - `/init` — create an AGENTS.md file with instructions for Codex

  The one place the two ecosystems visibly diverge: CLAUDE.md against AGENTS.md. Same command, different filename.

### Show the working diff

  - **Claude Code:**
    - `/diff` — View uncommitted changes and per-turn diffs
  - **Codex:**
    - `/diff` — show git diff (including untracked files)

  Codex includes untracked files; Claude Code adds a per-turn view of what it changed.

### Review the changes you have not committed

  - **Claude Code:**
    - `/code-review` — Review the changes since a fixed point along two axes — repo standards and the originating spec — in parallel sub-agents
    - `/simplify` — Review changed code for reuse, simplification and efficiency, then apply the fixes
  - **Codex:**
    - `/review` — review my current changes and find issues
    - `codex review` — Run a code review non-interactively
    - `codex exec review` — Run a code review against the current repository

  Codex exposes review three ways, one of them non-interactive and scriptable. Claude Code's is a bundled skill, and it ships a second one that applies cleanups rather than reporting them.

### Work somewhere else on disk

  - **Claude Code:**
    - `/add-dir` — Add a new working directory
    - `/cd` — Move this session to a new working directory
    - `--add-dir <dirs...>` *(launch flag)* — Additional directories to allow tool access to
  - **Codex:**
    - `--add-dir <DIR>` *(launch flag)* — Additional directories that should be writable alongside the primary workspace
    - `-C, --cd <DIR>` *(launch flag)* — Tell the agent to use the specified directory as its working root

  Claude Code can move mid-session; Codex settles it at launch. The flag spellings are identical.

### Decide what it may do without asking

  - **Claude Code:**
    - `/permissions` — Manage allow and deny tool permission rules
  - **Codex:**
    - `/permissions` — choose what Codex is allowed to do

  Same command name, different model underneath — see the capability table below.

### Sandbox what it runs

  - **Claude Code:**
    - `/sandbox` — Toggle sandbox mode for the Bash tool; available on supported platforms only
  - **Codex:**
    - `codex sandbox` — Run commands within a Codex-provided sandbox
    - `/setup-default-sandbox` — set up elevated agent sandbox
    - `/sandbox-add-read-dir` — let sandbox read a directory: /sandbox-add-read-dir <absolute_path>

  Claude Code toggles a sandbox for its own Bash tool. Codex also ships the sandbox as a shell command you can wrap any process in, agent or not.

### Run your own code on lifecycle events

  - **Claude Code:**
    - `/hooks` — View hook configurations for tool events
  - **Codex:**
    - `/hooks` — view and manage lifecycle hooks

### Open the settings

  - **Claude Code:**
    - `/config` — Open settings
    - `/update-config` — Change settings: hooks, permissions, environment variables
  - **Codex:**
    - `/debug-config` — show config layers and requirement sources for debugging

  Claude Code has a settings UI and a skill that rewrites the file for you. Codex expects you to edit config.toml; its config command is hidden and read-only — it shows which layer a value came from.

### Change the colours

  - **Claude Code:**
    - `/theme` — Change the theme
    - `/color` — Set the prompt bar color for this session
  - **Codex:**
    - `/theme` — choose a syntax highlighting theme

### Configure the status line

  - **Claude Code:**
    - `/statusline` — Set up Claude Code's status line UI
  - **Codex:**
    - `/statusline` — configure which items appear in the status line
    - `/title` — configure which items appear in the terminal title

  Codex will also put session items in the terminal's title bar.

### Remap the keyboard

  - **Claude Code:**
    - `/keybindings` — Open your keyboard shortcuts file
    - `/keybindings-help` — Customize keyboard shortcuts, rebind keys, and add chord bindings
    - `/terminal-setup` — Configure terminal key bindings — Shift+Enter or Option+Enter for newlines
  - **Codex:**
    - `/keymap` — remap TUI shortcuts
    - `/vim` — toggle Vim mode for the composer

  Codex ships a Vim mode for the composer; Claude Code ships a skill that edits the keybindings file with you.

### Manage what it remembers

  - **Claude Code:**
    - `/memory` — Open a memory file in your editor
    - `/pause-memory` — Pause automemory for this session
  - **Codex:**
    - `/memories` — configure memory use and generation

  Both keep memory outside the conversation and let you pause or shape it.

### Import the other one's setup

  - **Claude Code:**
    - `/import` — Import config from another AI coding agent
  - **Codex:**
    - `/import` — import setup, this project, and recent chats from Claude Code

  Both ship it, and Codex names its source out loud: “import setup, this project, and recent chats from Claude Code.”

### Talk to the editor

  - **Claude Code:**
    - `/ide` — Manage IDE integrations and show status
  - **Codex:**
    - `/ide` — include current selection, open files, and other context from your IDE

  Claude Code manages an integration; Codex pulls your selection and open files in as context.

### Use skills

  - **Claude Code:**
    - `/skills` — List available skills
    - `/reload-skills` — Pick up skills added or changed on disk during this session
    - `/skill-doctor` — Show which loaded skills are unused and costing context
  - **Codex:**
    - `/skills` — use skills to improve how Codex performs specific tasks

  Claude Code additionally reloads them mid-session and reports which loaded skills are costing you context for nothing.

### Wire up MCP servers

  - **Claude Code:**
    - `/mcp` — Manage MCP servers
    - `claude mcp` — Configure and manage MCP servers
  - **Codex:**
    - `/mcp` — list configured MCP tools; use /mcp verbose for details
    - `codex mcp` — Manage external MCP servers for Codex
    - `codex mcp add` — Add an MCP server by URL or launch command
    - `codex mcp list` — List configured MCP servers
    - `codex mcp remove` — Remove a configured MCP server

  Codex breaks the shell side into one subcommand per operation, including login and logout for servers behind auth.

### Install plugins

  - **Claude Code:**
    - `/plugin` — Manage Claude Code plugins
    - `claude plugin` — Manage Claude Code plugins
    - `/reload-plugins` — Activate pending plugin changes in the current session
  - **Codex:**
    - `/plugins` — browse plugins
    - `codex plugin` — Manage Codex plugins
    - `codex plugin add` — Install a plugin from a configured marketplace snapshot
    - `codex plugin marketplace` — Add, list, upgrade, or remove configured plugin marketplaces

  Both have marketplaces. Codex's are explicit config entries you add, list, upgrade and remove by name.

### Sign in and out

  - **Claude Code:**
    - `/login` — Sign in with your Anthropic account, or switch accounts
    - `/logout` — Sign out from your Anthropic account
    - `claude auth` — Manage authentication
  - **Codex:**
    - `/logout` — log out of Codex
    - `codex login` — Manage login
    - `codex login status` — Show login status
    - `codex logout` — Remove stored authentication credentials

  Codex has no /login at the prompt — signing in is a shell command.

### See what it is costing

  - **Claude Code:**
    - `/usage` — Show session cost, plan usage, and activity stats
    - `/explain-usage` — See where this session's tokens went, in plain words
    - `/insights` — Generate a report analyzing your Claude Code sessions
  - **Codex:**
    - `/usage` — view account usage or use a usage limit reset

  Claude Code adds a plain-words breakdown of where a session's tokens went and a report across sessions.

### Diagnose the install

  - **Claude Code:**
    - `/doctor` — Health-check your setup and fix issues: installation, unused extensions, duplicates
    - `claude doctor` — Check the health of your installation, reading settings without a trust prompt
  - **Codex:**
    - `codex doctor` — Diagnose local Codex installation, config, auth, and runtime health

  Both check installation, config and auth. Claude Code's also runs inside a session.

### Update

  - **Claude Code:**
    - `/update` — Switch to the latest version; the conversation continues
    - `claude update` — Check for updates and install if available
    - `/version` — Show this session's version — autoupdate may have a newer one
  - **Codex:**
    - `codex update` — Update Codex to the latest version

  Claude Code can swap the binary without dropping the conversation.

### Send feedback

  - **Claude Code:**
    - `/feedback` — Send feedback to Anthropic or report a bug
    - `/bug` — Report a bug or share your conversation
  - **Codex:**
    - `/feedback` — send logs to maintainers

### Continue in the desktop app

  - **Claude Code:**
    - `/desktop` — Continue the current session in Claude Desktop
  - **Codex:**
    - `/app` — continue this session in the Desktop app
    - `codex app` — Launch the Desktop app (opens the app installer if missing)

### Run it non-interactively

  - **Claude Code:**
    - `claude -p` — Print mode: run a prompt non-interactively and exit, useful for pipes and scripts
  - **Codex:**
    - `codex exec` — Run Codex non-interactively
    - `codex exec resume` — Resume a previous session by id or pick the most recent with --last

  The scripting entry point on both. Claude Code drives it with flags — --output-format, --json-schema, --max-budget-usd; Codex gives exec its own subcommands.

### Background work

  - **Claude Code:**
    - `/background` — Send this session to the background and free the terminal
    - `/tasks` — View and manage everything running in the background
    - `/stop` — Stop this background session; transcript and worktree are kept
    - `claude agents` — Manage background agents
  - **Codex:**
    - `/ps` — list background terminals
    - `/stop` — stop all background terminals

  The names line up and the meanings do not. Claude Code backgrounds whole sessions and agents; Codex's /ps and /stop list and kill the shell processes the agent started.

### Hand work to another agent

  - **Claude Code:**
    - `/subtask` — Send a subagent off with your full context; its result comes back here
    - `/fork` — Spawn a background agent that inherits the full conversation
    - `/agents` — Removed. Ask Claude to create or manage subagents, or edit .claude/agents/ directly
  - **Codex:**
    - `/agent` — switch the active agent thread
    - `/subagents` — switch the active agent thread

  Codex switches which agent thread you are typing at. Claude Code sends work away and brings the result back, and its /agents entry says the command was removed in favour of editing .claude/agents/ directly.

### Drive it from somewhere else

  - **Claude Code:**
    - `/remote-control` — Control this session from your phone or claude.ai/code
    - `/session` — Show cloud session URL and QR code
    - `/teleport` — Resume a Claude Code session from claude.ai
  - **Codex:**
    - `codex remote-control` — Manage the app-server daemon with remote control enabled
    - `codex remote-control pair` — Create and print a short-lived manual pairing code

  Claude Code hands off to a phone or claude.ai; Codex pairs a daemon you connect a front-end to.

### Run it in the cloud

  - **Claude Code:**
    - `/ultrareview` — Find and verify bugs in your branch using Claude Code on the web
    - `/ultraplan` — Draft an editable plan in Claude Code on the web
    - `/web-setup` — Set up Claude Code on the web with your GitHub account
  - **Codex:**
    - `codex cloud` — Browse tasks from Codex Cloud and apply changes locally
    - `codex cloud exec` — Submit a new Codex Cloud task without launching the TUI
    - `codex cloud apply` — Apply the diff for a Codex Cloud task locally

  Both send work off-machine and bring a diff back. Codex's is a general task queue you drive from the shell; Claude Code's is job-shaped — review this branch, draft this plan.

## Only in Claude Code

Claude Code commands no pairing above claimed. 69 of 143.


**Session & context**

- **`/help`** — Show help and available commands
- **`/rewind`** — Restore the code and/or conversation to a previous point
- **`/export`** — Export the current conversation to a file or clipboard
- **`/focus`** — Toggle focus view: just your prompt, summary, and response
- **`/brief`** — Toggle brief-only mode
- **`/recap`** — Generate a one-line session recap now

**Model & reasoning**

- **`/advisor`** — Let Claude consult a stronger model at key moments

**Workspace & code**

- **`/review`** — Review a GitHub pull request; for your working diff use /code-review
- **`/security-review`** — Analyze pending changes on the current branch for security vulnerabilities — injection, auth issues, data exposure
- **`/batch`** — Plan a large change; background agents each open a PR
- **`/run`** — Launch this project's app to see your change working
- **`/run-skill-generator`** — Create a skill that knows how to run this project's app

**Config & environment**

- **`/fewer-permission-prompts`** — Pre-approve safe read-only commands based on your usage
- **`/tui`** — Set the terminal UI renderer
- **`/scroll-speed`** — Adjust mouse wheel scroll speed
- **`/voice`** — Toggle voice mode
- **`/wellbeing`** — Configure optional break reminders and quiet-hours nudges
- **`/debug`** — Turn on debug logging and investigate problems
- **`/setup-bedrock`** — Reconfigure Amazon Bedrock authentication, region, or model pins
- **`/setup-vertex`** — Reconfigure Google Vertex AI authentication, project, region, or model pins

**Background & parallel work**

- **`/workflows`** — Browse running and completed workflows
- **`/loops`** — List, create, and delete loops
- **`/loop`** — Repeat a prompt or command on an interval, e.g. /loop 5m /foo
- **`/daemon`** — Manage background services and routines
- **`/schedule`** — Create and manage routines: cloud agents on a schedule

**Cloud, web & devices**

- **`/remote-env`** — Choose the default environment for cloud agents
- **`/autofix-pr`** — Monitor and autofix any issues with the current PR
- **`/install-github-app`** — Set up Claude GitHub Actions for a repository
- **`/install-slack-app`** — Install the Claude Slack app
- **`/chrome`** — Open Claude in Chrome settings
- **`/claude-in-chrome`** — Let Claude browse and interact with pages in your Chrome
- **`/setup-cowork`** — Guided setup — pick a role, install a plugin, try a skill, connect a tool

**Design & artifacts**

- **`/artifacts`** — Browse your published and shared artifacts
- **`/artifact-design`** — Design guidance and fundamentals for Artifacts
- **`/artifact-capabilities`** — Runtime capabilities for published Artifacts
- **`/plan-artifact`** — Publish a plan as a shareable Artifact
- **`/whiteboard`** — Sketch on a whiteboard Artifact you can send to Claude
- **`/workshop`** — Workshop a document through artifact decisions
- **`/dataviz`** — Chart, dashboard and palette guidance for any visualization you build
- **`/design`** — Grant or revoke Claude agent access to your Design projects
- **`/design-login`** — Authorize design-system access for /design-sync with your claude.ai account
- **`/design-sync`** — Push your design system components to claude.ai/design

**Account, usage & install**

- **`/usage-credits`** — Configure usage credits or request them from your admin when you hit a limit
- **`/upgrade`** — Upgrade to Max for higher rate limits and more Opus
- **`/passes`** — Share a free week of Claude Code with friends and earn usage credits
- **`/privacy-settings`** — View and update your privacy settings
- **`/release-notes`** — View release notes
- **`/install`** — Install Claude Code native build

**Help, feedback & extras**

- **`/claude-api`** — Build and debug apps that use the Claude API
- **`/powerup`** — Discover Claude Code features through quick interactive lessons
- **`/team-onboarding`** — Help teammates ramp on Claude Code with a guide from your usage
- **`/mobile`** — Show QR code to download the Claude mobile app
- **`/stickers`** — Order Claude Code stickers
- **`/radio`** — Listen to Claude FM lo-fi radio

**Terminal CLI**

- **`claude auto-mode`** — Inspect or reset auto mode classifier configuration
- **`claude gateway`** — Run the enterprise auth/telemetry gateway
- **`claude install`** — Install the native build — stable, latest, or a specific version
- **`claude project`** — Manage Claude Code project state
- **`claude setup-token`** — Set up a long-lived authentication token, requires a Claude subscription
- **`claude ultrareview`** — Run a cloud-hosted multi-agent code review of the current branch or a PR and print the findings

**Hidden & internal**

- **`/auto-mode-setup`** — Set up and customise auto mode — environment context, plus optional rule tweaks
- **`/heapdump`** — Dump the JS heap to ~/Desktop
- **`/design-consent`** — Grant Claude agent access to your Design projects
- **`/design-revoke`** — Revoke Claude agent access to your Design projects
- **`/extra-usage`** — Renamed to /usage-credits
- **`/pro-trial-expired`** — Options shown when the Pro plan Claude Code trial has ended
- **`/rate-limit-options`** — Show options when rate limit is reached
- **`/__remote-workflow`** — Run the workflow script delivered in this session environment — server-launched sessions only
- **`/workflow-launch-exec`** — Execute a server-launched workflow handoff — workflow_launch event sessions only

## Only in Codex

Codex commands no pairing above claimed. 55 of 122.


**Session & context**

- **`/archive`** — archive this session and exit
- **`/delete`** — permanently delete this session and exit
- **`/raw`** — toggle raw scrollback mode for copy-friendly terminal selection

**Model & reasoning**

- **`/personality`** — choose a communication style for Codex

**Workspace & code**

- **`/mention`** — mention a file
- **`/approve`** — approve one retry of a recent auto-review denial

**Config & environment**

- **`/pets`** — choose or hide the terminal pet
- **`/experimental`** — toggle experimental features

**Hidden & internal**

- **`/apps`** — manage apps
- **`/rollout`** — print the rollout file path
- **`/test-approval`** — test approval request
- **`/debug-m-drop`** — DO NOT USE
- **`/debug-m-update`** — DO NOT USE

**Terminal CLI — core**

- **`codex apply`** — Apply the latest diff produced by Codex agent as a `git apply` to your local working tree
- **`codex archive`** — Archive a saved session by id or session name
- **`codex unarchive`** — Unarchive a saved session by id or session name
- **`codex delete`** — Permanently delete a saved session by id or session name
- **`codex completion`** — Generate shell completion scripts

**MCP & plugins**

- **`codex mcp get`** — Show one configured MCP server
- **`codex mcp login`** — Sign in to an MCP server that needs auth
- **`codex mcp logout`** — Sign out of an MCP server
- **`codex mcp-server`** — Start Codex as an MCP server (stdio)
- **`codex plugin list`** — List plugins available from configured marketplace snapshots
- **`codex plugin remove`** — Remove an installed plugin from local config and cache
- **`codex plugin marketplace add`** — Add a local or Git marketplace to the configured marketplace sources
- **`codex plugin marketplace list`** — List plugin marketplaces Codex is currently considering and their roots
- **`codex plugin marketplace remove`** — Remove a configured marketplace source by name
- **`codex plugin marketplace upgrade`** — Refresh configured Git marketplace snapshots

**App server, daemon & remote control**

- **`codex app-server`** — Run the app server or related tooling
- **`codex app-server daemon`** — Manage the local app-server daemon
- **`codex app-server daemon start`** — Start the local app server daemon if it is not already running
- **`codex app-server daemon stop`** — Stop the local app server daemon
- **`codex app-server daemon restart`** — Restart the local app server daemon
- **`codex app-server daemon bootstrap`** — Install durable local app-server management for SSH-driven use
- **`codex app-server daemon version`** — Print local CLI and running app-server versions as JSON
- **`codex app-server daemon enable-remote-control`** — Enable remote control for future starts and a currently running managed daemon
- **`codex app-server daemon disable-remote-control`** — Disable remote control for future starts and a currently running managed daemon
- **`codex app-server generate-json-schema`** — Generate JSON Schema for the app server protocol
- **`codex app-server generate-ts`** — Generate TypeScript bindings for the app server protocol
- **`codex app-server proxy`** — Proxy stdio bytes to the running app-server control socket
- **`codex remote-control start`** — Start the app-server daemon with remote control enabled
- **`codex remote-control stop`** — Stop the app-server daemon
- **`codex exec-server`** — Run the standalone exec-server service

**Codex Cloud**

- **`codex cloud list`** — List Codex Cloud tasks
- **`codex cloud status`** — Show the status of a Codex Cloud task
- **`codex cloud diff`** — Show the unified diff for a Codex Cloud task

**Debug & feature flags**

- **`codex debug`** — Debugging tools
- **`codex debug models`** — Render the raw model catalog as JSON
- **`codex debug prompt-input`** — Render the model-visible prompt input list as JSON
- **`codex debug app-server`** — Tooling: helps debug the app server
- **`codex debug app-server send-message-v2`** — Send one user message to the app server
- **`codex features`** — Inspect feature flags
- **`codex features list`** — List known features with their stage and effective state
- **`codex features enable`** — Enable a feature in config.toml
- **`codex features disable`** — Disable a feature in config.toml

## Capabilities, not commands

Differences a command list cannot show. Nothing here comes from either vendor's documentation; each row names how it was established.

| Topic | Claude Code 2.1.220 | Codex CLI 0.146.0 | How this was established |
| --- | --- | --- | --- |
| Where settings live | ~/.claude/settings.json — JSON, with a /config UI and a bundled skill that rewrites it for you. | ~/.codex/config.toml — TOML, layered. Any key is overridable per-run with -c foo.bar=value, and --profile &lt;name&gt; stacks $CODEX_HOME/&lt;name&gt;.config.toml on top. | Both files on this machine, plus codex --help. |
| Project instructions file | CLAUDE.md, written by /init, auto-discovered up the tree. | AGENTS.md, written by /init. | Each tool's own /init description, and both files present in the two config homes. |
| Permission model | One axis. --permission-mode takes acceptEdits, auto, bypassPermissions, manual, dontAsk or plan, with allow/deny rules per tool underneath. | Two orthogonal axes. --ask-for-approval takes untrusted, on-request or never; --sandbox independently takes read-only, workspace-write or danger-full-access. | The [possible values] block each CLI prints for those flags in --help. |
| Sandbox | /sandbox toggles sandboxing for the Bash tool, on supported platforms only. It applies to what Claude Code runs. | The same sandbox is also a command you can point at anything: codex sandbox -- &lt;cmd&gt; runs it under seatbelt, and --log-denials prints the macOS denials it collected. | codex sandbox --help; the /sandbox description in the build. |
| The escape hatch | --dangerously-skip-permissions, plus --allow-dangerously-skip-permissions to make it available without turning it on. | --dangerously-bypass-approvals-and-sandbox, and separately --dangerously-bypass-hook-trust for running hooks whose source has not been vetted. | --help on both. |
| Lifecycle hooks | Configured under hooks in settings.json. The binary carries eleven event names: PreToolUse, PostToolUse, PermissionRequest, UserPromptSubmit, Notification, PreCompact, SessionStart, SessionEnd, Stop, SubagentStart, SubagentStop. | A separate ~/.codex/hooks.json, with per-hook trust recorded back into config.toml under hooks.state — Codex will not run a hook it has not been trusted to run. | Event names read out of the Claude Code binary; the Codex side read off the two config files. See the caveat below the table. |
| Skills | 35 compiled into the binary — the whole prompt corpus is on its own page here — plus whatever is in ~/.claude/skills. 23 of the bundled ones are typeable as slash commands. | /skills, loading from ~/.codex/skills and from plugins. Whether Codex also bundles prompts of its own is not established here — no equivalent extractor was written for it, and a Rust binary does not give them up the way a Bun-compiled JavaScript bundle does. Read that as a gap in this page, not a finding about Codex. | The skills extraction behind the bundled-skills page; both skills directories on this machine. The Codex half is deliberately a non-claim. |
| Subagents | Definitions in .claude/agents/ or inline via --agents &lt;json&gt;. /subtask and /fork send work off and bring the result back; /workflows tracks multi-agent runs. | /agent and /subagents switch which agent thread you are typing at. SubagentStart and SubagentStop exist as hook points. | Both command inventories; ~/.claude/agents/; the hook state keys in config.toml. |
| MCP | A client. claude mcp manages servers; --mcp-config loads them from a file or string and --strict-mcp-config ignores everything else. | A client and a server: codex mcp-server starts Codex itself as an MCP server over stdio, so another agent can call it as a tool. | codex --help; the flag tables on both index pages. |
| Scripting surface | claude -p plus flags: --output-format json\|stream-json, --json-schema for structured output, --max-budget-usd, --input-format, --include-partial-messages. | codex exec with its own subcommands (resume, review), plus codex app-server — a protocol daemon that will emit its own JSON Schema and TypeScript bindings for you. | Both flag tables and subcommand trees. |
| Model providers | Anthropic, with /setup-bedrock and /setup-vertex for the cloud resellers, --fallback-model when the default is overloaded, and --betas for API-key users. | OpenAI, with --oss and --local-provider lmstudio\|ollama for running against a local model instead. | --help on both; the command inventories. |
| Feature switchboard | None user-facing. Gating is internal: ten commands are in the binary but withheld from /help, and some skills register only when a check passes. | codex features list prints 100 switches with a maturity stage each, 40 of them on in this build, toggleable per-run with --enable/--disable or persisted with codex features enable. | Both index pages; the feature table is codex features list verbatim. |
| Where the surface lives | At the prompt. 129 of 143 entries are typed after a / — 96 native, 23 bundled skills, 10 hidden — leaving 14 shell subcommands. | In the shell. 68 of 122 entries are codex subcommands, against 54 typed after a / — the only one of the two where the shell side is the bigger half. | Counted from the two inventories. Hidden commands are counted as slash commands on both sides, because that is how they are typed. |

One row is weaker than the others, and it is the hooks row. Both binaries carry the same eleven event names, which settles it for Claude Code — they are the keys its `settings.json` takes — but not for Codex, which also ships an importer for Claude Code setups and so has a reason to know those names either way. Which of the eleven Codex actually fires was not established here, and is not claimed.

## Which one to reach for

*Opinion. Everything above this line was measured; this is a reading of it.*

**Reach for Claude Code when**

- You want the session itself to be the workspace. Claude Code puts almost everything behind a /, including things Codex settles at launch — move to another directory, change effort, swap the model, background the whole session and get the terminal back.
- You want to undo. /rewind has no counterpart on the Codex side of this page.
- You lean on skills and subagents. 35 prompts ship in the binary, agents are files you write, and /subtask, /fork and /workflows exist to fan work out and collect it.
- You want the model choice to include Bedrock or Vertex.

**Reach for Codex when**

- You want the agent under a sandbox you can reason about — and reuse. Approval policy and sandbox policy are separate flags with named values, and codex sandbox will wrap any command, not just the agent's.
- You are building on top of it. codex mcp-server makes Codex a tool other agents call; codex app-server hands you a protocol daemon with generated schema and TypeScript bindings.
- You want the tool configured as data. One TOML file, layered profiles, and -c any.key=value for a single run.
- You want to run against a local model — --oss with LM Studio or Ollama.
- You want to see the feature flags rather than discover them.

**And mostly**

Neither list is a ranking, and the overlap is the real story: 43 jobs on this page have a command on both sides, several with the same name. Both ship hooks, MCP, plugins, skills, plan mode, a review command, a memory system and a desktop hand-off. Both also ship a command that imports the other one's setup, which tells you what the vendors expect you to be doing.

---

From [AI Snacks](https://johnmiroki.github.io/ai-snacks/) by johnmiroki. If it saved you time, [buy me a coffee](https://buymeacoffee.com/john42).
