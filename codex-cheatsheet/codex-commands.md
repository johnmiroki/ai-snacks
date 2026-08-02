# Codex CLI Command Index

> Every slash command, `codex` subcommand, launch flag and feature flag in OpenAI Codex CLI build 0.146.0. Read out of the running CLI rather than the documentation: the slash commands off the picker itself, the subcommand tree off `codex --help`, and the feature table off `codex features list`.

- Canonical page: https://johnmiroki.github.io/ai-snacks/codex-cheatsheet/
- Machine-readable: https://johnmiroki.github.io/ai-snacks/codex-cheatsheet/codex-commands.json
- Codex CLI build: 0.146.0
- Last updated: 2026-08-02
- License: CC BY 4.0

## Totals

| Group | Count | What it means |
| --- | ---: | --- |
| Slash commands | 46 | Offered by the `/` picker at the Codex prompt |
| CLI subcommands | 68 | The `codex` executable and its whole subcommand tree |
| Hidden | 8 | In the binary, never offered by the picker |
| Launch flags | 21 | Options passed to `codex` at startup |
| Feature flags | 100 | From `codex features list`; 40 on in this build |
| Linked to official docs | 110 | The rest have no official page |
| Named but not registered | 3 | Typing them returns `Unrecognized command` |
| Deliberately not probed | 3 | Running them would have done real work |

## How this was established

Slash commands were read from the running TUI, not from a string dump: build 0.146.0 was driven in a pseudo-terminal, the `/` picker opened and paged to its end, and every row it rendered captured with its description. Reading the binary as text additionally turns up names the picker never offers, and those were each typed at the prompt and classified by the response — running normally means registered but withheld, while *Unrecognized command* is the identical answer a deliberately nonsensical control command got. Commands that would have executed real work were excluded from the probe rather than run, and are marked as not probed rather than guessed at. Subcommands, arguments and launch flags come from a recursive walk of `codex --help` across every subcommand on the same build.

## Session & context

Steering the conversation you are in right now. 15 entries.

- **`/new`** — start a new chat during a conversation. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli#built-in-slash-commands)
- **`/clear`** — clear the terminal and start a new chat. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli#built-in-slash-commands)
- **`/compact`** — summarize conversation to prevent hitting the context limit. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli#built-in-slash-commands)
- **`/resume`** — resume a saved chat. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli#built-in-slash-commands)
- **`/fork`** — fork the current chat. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli#built-in-slash-commands)
- **`/rename`** — rename the current thread. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli#built-in-slash-commands)
- **`/archive`** — archive this session and exit. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli#built-in-slash-commands)
- **`/delete`** — permanently delete this session and exit. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli#built-in-slash-commands)
- **`/status`** — show current session configuration and token usage. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli#built-in-slash-commands)
- **`/copy`** — copy last response as markdown. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli#built-in-slash-commands)
- **`/raw`** — toggle raw scrollback mode for copy-friendly terminal selection.
- **`/side`** *(aliases: `btw`)* — start a side conversation in an ephemeral fork. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli#built-in-slash-commands)
- **`/agent`** — switch the active agent thread. [docs](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- **`/subagents`** — switch the active agent thread. [docs](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- **`/exit`** *(aliases: `quit`)* — exit Codex. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli#built-in-slash-commands)

## Model & reasoning

How much horsepower each turn gets, and how it talks back. 5 entries.

- **`/model`** — choose what model and reasoning effort to use. [docs](https://learn.chatgpt.com/docs/models)
- **`/fast`** — 1.5x speed, increased usage. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli#built-in-slash-commands)
- **`/plan`** — switch to Plan mode. [docs](https://learn.chatgpt.com/docs/permission-modes)
- **`/goal`** — set or view the goal for a long-running task. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli#built-in-slash-commands)
- **`/personality`** — choose a communication style for Codex. [docs](https://learn.chatgpt.com/docs/customization/overview)

## Workspace & code

Project instructions, your working diff, and review. 5 entries.

- **`/init`** — create an AGENTS.md file with instructions for Codex. [docs](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- **`/review`** — review my current changes and find issues. [docs](https://learn.chatgpt.com/docs/code-review)
- **`/diff`** — show git diff (including untracked files). [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli#built-in-slash-commands)
- **`/mention`** — mention a file. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli#built-in-slash-commands)
- **`/approve`** — approve one retry of a recent auto-review denial. [docs](https://learn.chatgpt.com/docs/sandboxing/auto-review)

## Config & environment

Settings, permissions, hooks, and how the terminal behaves. 13 entries.

- **`/permissions`** — choose what Codex is allowed to do. [docs](https://learn.chatgpt.com/docs/permissions)
- **`/keymap`** — remap TUI shortcuts. [docs](https://learn.chatgpt.com/docs/cli-customization)
- **`/vim`** — toggle Vim mode for the composer. [docs](https://learn.chatgpt.com/docs/cli-customization)
- **`/theme`** — choose a syntax highlighting theme. [docs](https://learn.chatgpt.com/docs/cli-customization)
- **`/statusline`** — configure which items appear in the status line. [docs](https://learn.chatgpt.com/docs/cli-customization)
- **`/title`** — configure which items appear in the terminal title. [docs](https://learn.chatgpt.com/docs/cli-customization)
- **`/pets`** — choose or hide the terminal pet. [docs](https://learn.chatgpt.com/docs/cli-customization)
- **`/experimental`** — toggle experimental features. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli#built-in-slash-commands)
- **`/import`** — import setup, this project, and recent chats from Claude Code.
- **`/hooks`** — view and manage lifecycle hooks. [docs](https://learn.chatgpt.com/docs/hooks)
- **`/memories`** — configure memory use and generation. [docs](https://learn.chatgpt.com/docs/customization/memories)
- **`/skills`** — use skills to improve how Codex performs specific tasks. [docs](https://learn.chatgpt.com/docs/build-skills)
- **`/ide`** — include current selection, open files, and other context from your IDE. [docs](https://learn.chatgpt.com/docs/codex/ide)

## Extensions

MCP servers and plugins. 2 entries.

- **`/mcp`** — list configured MCP tools; use /mcp verbose for details. [docs](https://learn.chatgpt.com/docs/extend/mcp)
- **`/plugins`** — browse plugins. [docs](https://learn.chatgpt.com/docs/plugins)

## Account & usage

Who you are signed in as, what it costs, and the desktop app. 4 entries.

- **`/usage`** — view account usage or use a usage limit reset. [docs](https://learn.chatgpt.com/docs/reference/troubleshooting)
- **`/logout`** — log out of Codex. [docs](https://learn.chatgpt.com/docs/auth)
- **`/feedback`** — send logs to maintainers. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli#built-in-slash-commands)
- **`/app`** — continue this session in the Desktop app. [docs](https://learn.chatgpt.com/docs/web)

## Background terminals

Long-running shells the agent started. 2 entries.

- **`/ps`** — list background terminals.
- **`/stop`** — stop all background terminals.

## Hidden & internal

In the binary but not offered by the / picker — listed for completeness. 8 entries.

- **`/apps`** — manage apps. *(withheld from the `/` picker, but runs when typed)*
- **`/debug-config`** — show config layers and requirement sources for debugging. *(withheld from the `/` picker, but runs when typed)*
- **`/rollout`** — print the rollout file path. *(**typing it returns `Unrecognized command`** — Answers “Unrecognized command” in build 0.146.0, exactly as a nonsense control command does)*
- **`/sandbox-add-read-dir`** — let sandbox read a directory: /sandbox-add-read-dir <absolute_path>. *(**typing it returns `Unrecognized command`** — Answers “Unrecognized command” in build 0.146.0, exactly as a nonsense control command does)*
- **`/test-approval`** — test approval request. *(**typing it returns `Unrecognized command`** — Answers “Unrecognized command” in build 0.146.0, exactly as a nonsense control command does)*
- **`/setup-default-sandbox`** — set up elevated agent sandbox. *(**not probed** — Not run: it would have reconfigured the agent sandbox. Availability unestablished)*
- **`/debug-m-drop`** — DO NOT USE. *(**not probed** — Not run: the binary labels this DO NOT USE. Availability unestablished)*
- **`/debug-m-update`** — DO NOT USE. *(**not probed** — Not run: the binary labels this DO NOT USE. Availability unestablished)*

## Terminal CLI — core

The codex executable itself, run from your shell. 19 entries.

- **`codex`** `[PROMPT]` — Start an interactive session in the current directory. [docs](https://learn.chatgpt.com/docs/codex/cli)
- **`codex exec`** `[PROMPT] codex exec <COMMAND> [ARGS]` *(aliases: `e`)* — Run Codex non-interactively. [docs](https://learn.chatgpt.com/docs/non-interactive-mode)
- **`codex exec resume`** `[SESSION_ID] [PROMPT]` — Resume a previous session by id or pick the most recent with --last. [docs](https://learn.chatgpt.com/docs/non-interactive-mode)
- **`codex exec review`** `[PROMPT]` — Run a code review against the current repository. [docs](https://learn.chatgpt.com/docs/non-interactive-mode)
- **`codex review`** `[PROMPT]` — Run a code review non-interactively. [docs](https://learn.chatgpt.com/docs/code-review)
- **`codex resume`** `[SESSION_ID] [PROMPT]` — Resume a previous interactive session (picker by default; use --last to continue the most recent). [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli#codex-resume)
- **`codex fork`** `[SESSION_ID] [PROMPT]` — Fork a previous interactive session (picker by default; use --last to fork the most recent). [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli#codex-fork)
- **`codex apply`** `<TASK_ID>` *(aliases: `a`)* — Apply the latest diff produced by Codex agent as a `git apply` to your local working tree. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
- **`codex archive`** `<SESSION>` — Archive a saved session by id or session name. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
- **`codex unarchive`** `<SESSION>` — Unarchive a saved session by id or session name. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
- **`codex delete`** `<SESSION>` — Permanently delete a saved session by id or session name. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
- **`codex login`** `[COMMAND]` — Manage login. [docs](https://learn.chatgpt.com/docs/auth)
- **`codex login status`** — Show login status. [docs](https://learn.chatgpt.com/docs/auth)
- **`codex logout`** — Remove stored authentication credentials. [docs](https://learn.chatgpt.com/docs/auth)
- **`codex update`** — Update Codex to the latest version. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli#codex-update)
- **`codex doctor`** — Diagnose local Codex installation, config, auth, and runtime health. [docs](https://learn.chatgpt.com/docs/reference/troubleshooting)
- **`codex completion`** `[SHELL]` — Generate shell completion scripts. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
- **`codex sandbox`** `[COMMAND]...` — Run commands within a Codex-provided sandbox. [docs](https://learn.chatgpt.com/docs/sandboxing)
- **`codex app`** `[PATH]` — Launch the Desktop app (opens the app installer if missing). [docs](https://learn.chatgpt.com/docs/web)

## MCP & plugins

External tool servers, and the plugin marketplace. 17 entries.

- **`codex mcp`** `<COMMAND>` — Manage external MCP servers for Codex. [docs](https://learn.chatgpt.com/docs/extend/mcp)
- **`codex mcp add`** `<NAME> (--url <URL> | -- <COMMAND>...)` — Add an MCP server by URL or launch command. [docs](https://learn.chatgpt.com/docs/extend/mcp)
- **`codex mcp get`** `<NAME>` — Show one configured MCP server. [docs](https://learn.chatgpt.com/docs/extend/mcp)
- **`codex mcp list`** — List configured MCP servers. [docs](https://learn.chatgpt.com/docs/extend/mcp)
- **`codex mcp login`** `<NAME>` — Sign in to an MCP server that needs auth. [docs](https://learn.chatgpt.com/docs/extend/mcp)
- **`codex mcp logout`** `<NAME>` — Sign out of an MCP server. [docs](https://learn.chatgpt.com/docs/extend/mcp)
- **`codex mcp remove`** `<NAME>` — Remove a configured MCP server. [docs](https://learn.chatgpt.com/docs/extend/mcp)
- **`codex mcp-server`** — Start Codex as an MCP server (stdio). [docs](https://learn.chatgpt.com/docs/mcp-server)
- **`codex plugin`** `<COMMAND>` — Manage Codex plugins. [docs](https://learn.chatgpt.com/docs/plugins)
- **`codex plugin add`** `<PLUGIN[@MARKETPLACE]>` — Install a plugin from a configured marketplace snapshot. [docs](https://learn.chatgpt.com/docs/plugins)
- **`codex plugin list`** — List plugins available from configured marketplace snapshots. [docs](https://learn.chatgpt.com/docs/plugins)
- **`codex plugin remove`** `<PLUGIN[@MARKETPLACE]>` — Remove an installed plugin from local config and cache. [docs](https://learn.chatgpt.com/docs/plugins)
- **`codex plugin marketplace`** `<COMMAND>` — Add, list, upgrade, or remove configured plugin marketplaces. [docs](https://learn.chatgpt.com/docs/build-plugins)
- **`codex plugin marketplace add`** `<SOURCE>` — Add a local or Git marketplace to the configured marketplace sources. [docs](https://learn.chatgpt.com/docs/build-plugins)
- **`codex plugin marketplace list`** — List plugin marketplaces Codex is currently considering and their roots. [docs](https://learn.chatgpt.com/docs/build-plugins)
- **`codex plugin marketplace remove`** `<MARKETPLACE_NAME>` — Remove a configured marketplace source by name. [docs](https://learn.chatgpt.com/docs/build-plugins)
- **`codex plugin marketplace upgrade`** `[MARKETPLACE_NAME]` — Refresh configured Git marketplace snapshots. [docs](https://learn.chatgpt.com/docs/build-plugins)

## App server, daemon & remote control

The long-running service other front-ends talk to. 17 entries.

- **`codex app-server`** `[COMMAND]` — Run the app server or related tooling. *(the build labels this experimental)* [docs](https://learn.chatgpt.com/docs/app-server)
- **`codex app-server daemon`** `<COMMAND>` — Manage the local app-server daemon. [docs](https://learn.chatgpt.com/docs/app-server)
- **`codex app-server daemon start`** — Start the local app server daemon if it is not already running. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
- **`codex app-server daemon stop`** — Stop the local app server daemon. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
- **`codex app-server daemon restart`** — Restart the local app server daemon. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
- **`codex app-server daemon bootstrap`** — Install durable local app-server management for SSH-driven use. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
- **`codex app-server daemon version`** — Print local CLI and running app-server versions as JSON. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
- **`codex app-server daemon enable-remote-control`** — Enable remote control for future starts and a currently running managed daemon. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
- **`codex app-server daemon disable-remote-control`** — Disable remote control for future starts and a currently running managed daemon. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
- **`codex app-server generate-json-schema`** `--out <DIR>` — Generate JSON Schema for the app server protocol. *(the build labels this experimental)* [docs](https://learn.chatgpt.com/docs/app-server)
- **`codex app-server generate-ts`** `--out <DIR>` — Generate TypeScript bindings for the app server protocol. *(the build labels this experimental)* [docs](https://learn.chatgpt.com/docs/app-server)
- **`codex app-server proxy`** — Proxy stdio bytes to the running app-server control socket. [docs](https://learn.chatgpt.com/docs/app-server)
- **`codex remote-control`** `[COMMAND]` — Manage the app-server daemon with remote control enabled. *(the build labels this experimental)* [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
- **`codex remote-control start`** — Start the app-server daemon with remote control enabled. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
- **`codex remote-control stop`** — Stop the app-server daemon. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
- **`codex remote-control pair`** — Create and print a short-lived manual pairing code. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
- **`codex exec-server`** — Run the standalone exec-server service. *(the build labels this experimental)* [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli)

## Codex Cloud

Tasks running on OpenAI's infrastructure, driven from your shell. 6 entries.

- **`codex cloud`** `[COMMAND]` — Browse tasks from Codex Cloud and apply changes locally. *(the build labels this experimental)* [docs](https://learn.chatgpt.com/docs/cloud)
- **`codex cloud list`** — List Codex Cloud tasks. [docs](https://learn.chatgpt.com/docs/cloud)
- **`codex cloud status`** `<TASK_ID>` — Show the status of a Codex Cloud task. [docs](https://learn.chatgpt.com/docs/cloud)
- **`codex cloud diff`** `<TASK_ID>` — Show the unified diff for a Codex Cloud task. [docs](https://learn.chatgpt.com/docs/cloud)
- **`codex cloud exec`** `--env <ENV_ID> [QUERY]` — Submit a new Codex Cloud task without launching the TUI. [docs](https://learn.chatgpt.com/docs/cloud)
- **`codex cloud apply`** `<TASK_ID>` — Apply the diff for a Codex Cloud task locally. [docs](https://learn.chatgpt.com/docs/cloud)

## Debug & feature flags

Diagnostics, and the switchboard behind the build. 9 entries.

- **`codex debug`** `<COMMAND>` — Debugging tools. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
- **`codex debug models`** — Render the raw model catalog as JSON. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
- **`codex debug prompt-input`** `[PROMPT]` — Render the model-visible prompt input list as JSON. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
- **`codex debug app-server`** `<COMMAND>` — Tooling: helps debug the app server. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
- **`codex debug app-server send-message-v2`** `2 <USER_MESSAGE>` — Send one user message to the app server. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
- **`codex features`** `<COMMAND>` — Inspect feature flags. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
- **`codex features list`** — List known features with their stage and effective state. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
- **`codex features enable`** `<FEATURE>` — Enable a feature in config.toml. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
- **`codex features disable`** `<FEATURE>` — Disable a feature in config.toml. [docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli)

## Launch flags

Passed to `codex` at launch. 21 in total.

| Flag | What it does |
| --- | --- |
| `-c, --config <key=value>` | Override a configuration value that would otherwise be loaded from `~/.codex/config.toml`. Use a dotted path (`foo.bar.baz`) to override nested values. The `value` portion is parsed as TOML. If it fails to parse as TOML, the raw string is used as a literal |
| `--enable <FEATURE>` | Enable a feature (repeatable). Equivalent to `-c features.<name>=true` |
| `--disable <FEATURE>` | Disable a feature (repeatable). Equivalent to `-c features.<name>=false` |
| `--remote <ADDR>` | Connect the TUI to a remote app server endpoint. Accepted forms: `ws://host:port`, `wss://host:port`, `unix://`, or `unix://PATH` |
| `--remote-auth-token-env <ENV_VAR>` | Name of the environment variable containing the bearer token to send to a remote app server websocket |
| `--strict-config` | Error out when config.toml contains fields that are not recognized by this version of Codex |
| `-i, --image <FILE>...` | Optional image(s) to attach to the initial prompt |
| `-m, --model <MODEL>` | Model the agent should use |
| `--oss` | Use open-source provider |
| `--local-provider <OSS_PROVIDER>` | Specify which local provider to use (lmstudio or ollama). If not specified with --oss, will use config default or show selection |
| `-p, --profile <CONFIG_PROFILE_V2>` | Layer $CODEX_HOME/<name>.config.toml on top of the base user config |
| `-s, --sandbox <SANDBOX_MODE>` | Select the sandbox policy to use when executing model-generated shell commands [possible values: read-only, workspace-write, danger-full-access] |
| `--dangerously-bypass-approvals-and-sandbox` | Skip all confirmation prompts and execute commands without sandboxing. EXTREMELY DANGEROUS. Intended solely for running in environments that are externally sandboxed |
| `--dangerously-bypass-hook-trust` | Run enabled hooks without requiring persisted hook trust for this invocation. DANGEROUS. Intended only for automation that already vets hook sources |
| `-C, --cd <DIR>` | Tell the agent to use the specified directory as its working root |
| `--add-dir <DIR>` | Additional directories that should be writable alongside the primary workspace |
| `-a, --ask-for-approval <APPROVAL_POLICY>` | Configure when the model requires human approval before executing a command |
| `--search` | Enable live web search. When enabled, the native Responses `web_search` tool is available to the model (no per‑call approval) |
| `--no-alt-screen` | Disable alternate screen mode Runs the TUI in inline mode, preserving terminal scrollback history |
| `-h, --help` | Print help (see a summary with '-h') |
| `-V, --version` | Print version |

## Feature flags

From `codex features list`. 100 in total, 40 on in this build. The stage is what the build calls the feature's maturity; the state depends on your `config.toml`, your account and the build's own defaults.

| Feature | Stage | On in this build |
| --- | --- | --- |
| `apply_patch_freeform` | removed | no |
| `apply_patch_streaming_events` | under development | no |
| `apps` | stable | yes |
| `apps_mcp_path_override` | removed | no |
| `artifact` | under development | no |
| `auth_elicitation` | stable | yes |
| `browser_use` | stable | yes |
| `browser_use_external` | stable | yes |
| `browser_use_full_cdp_access` | stable | yes |
| `chronicle` | under development | yes |
| `code_mode` | under development | no |
| `code_mode_buffered_exec` | under development | no |
| `code_mode_host` | stable | yes |
| `code_mode_only` | under development | no |
| `codex_git_commit` | removed | no |
| `collaboration_modes` | removed | yes |
| `computer_use` | stable | yes |
| `concurrent_reasoning_summaries` | under development | no |
| `current_time_reminder` | under development | no |
| `default_mode_request_user_input` | under development | no |
| `deferred_executor` | under development | no |
| `deferred_tool_world_state` | under development | no |
| `elevated_windows_sandbox` | removed | no |
| `enable_fanout` | removed | no |
| `enable_mcp_apps` | under development | no |
| `enable_request_compression` | stable | yes |
| `exec_permission_approvals` | under development | no |
| `executor_capability_discovery` | under development | no |
| `experimental_windows_sandbox` | removed | no |
| `external_agent_memory_import` | under development | no |
| `external_migration` | removed | no |
| `fast_mode` | stable | yes |
| `goals` | stable | yes |
| `guardian_approval` | stable | yes |
| `guardianv2` | under development | no |
| `hooks` | stable | yes |
| `image_detail_original` | removed | no |
| `image_generation` | stable | yes |
| `in_app_browser` | stable | yes |
| `in_app_updates` | stable | yes |
| `item_ids` | removed | yes |
| `js_repl` | removed | no |
| `js_repl_tools_only` | removed | no |
| `local_thread_store_compression` | under development | no |
| `mcp_2026_07_28` | under development | no |
| `memories` | stable | yes |
| `mentions_v2` | stable | yes |
| `multi_agent` | stable | yes |
| `multi_agent_mode` | removed | no |
| `multi_agent_v2` | stable | no |
| `network_proxy` | experimental | no |
| `non_prefixed_mcp_tool_names` | under development | no |
| `personality` | stable | yes |
| `plugin_hooks` | removed | no |
| `plugin_sharing` | stable | yes |
| `plugins` | stable | yes |
| `prevent_idle_sleep` | experimental | no |
| `realtime_conversation` | under development | no |
| `remote_compaction_v2` | stable | yes |
| `remote_control` | removed | no |
| `remote_models` | removed | no |
| `remote_plugin` | stable | yes |
| `request_permissions_tool` | under development | no |
| `request_rule` | removed | no |
| `resize_all_images` | removed | yes |
| `respect_system_proxy` | under development | no |
| `responses_websockets` | removed | no |
| `responses_websockets_v2` | removed | no |
| `rollout_budget` | under development | no |
| `runtime_metrics` | under development | no |
| `search_tool` | removed | no |
| `secret_auth_storage` | stable | no |
| `shell_snapshot` | stable | yes |
| `shell_tool` | stable | yes |
| `shell_zsh_fork` | under development | no |
| `skill_env_var_dependency_prompt` | removed | no |
| `skill_mcp_dependency_install` | stable | yes |
| `skill_search` | stable | yes |
| `sqlite` | removed | yes |
| `standalone_web_search` | under development | no |
| `steer` | removed | yes |
| `terminal_resize_reflow` | removed | yes |
| `terminal_visualization_instructions` | under development | no |
| `token_budget` | under development | no |
| `tool_call_mcp_elicitation` | stable | yes |
| `tool_search` | removed | no |
| `tool_search_always_defer_mcp_tools` | removed | yes |
| `tool_suggest` | stable | yes |
| `tui_app_server` | removed | yes |
| `unavailable_dummy_tools` | removed | no |
| `undo` | removed | no |
| `unified_exec` | stable | yes |
| `unified_exec_zsh_fork` | under development | no |
| `use_agent_identity` | under development | no |
| `use_legacy_landlock` | deprecated | no |
| `use_linux_sandbox_bwrap` | removed | no |
| `web_search_cached` | deprecated | no |
| `web_search_request` | deprecated | no |
| `workspace_dependencies` | stable | yes |
| `workspace_owner_usage_nudge` | removed | no |

---

From [AI Snacks](https://johnmiroki.github.io/ai-snacks/) by johnmiroki. If it saved you time, [buy me a coffee](https://buymeacoffee.com/john42).
