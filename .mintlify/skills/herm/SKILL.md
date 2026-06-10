---
name: herm
description: Use Herm, the keyboard-driven terminal UI for Hermes Agent.
license: MIT
metadata:
  product: Herm
  docs: https://herm.liftaris.dev
  source: https://github.com/liftaris/herm
  related:
    - https://hermes-agent.nousresearch.com/docs
    - https://eikon.liftaris.dev
---

# Herm

Herm is the keyboard-driven terminal UI for Hermes Agent. Use this skill when you need to install Herm, understand its tabs, operate Hermes Agent from the terminal, customize keybindings and themes, manage eikons, or extend the TUI with bundled plugins.

Herm is not a model provider or a separate agent runtime. Hermes Agent owns inference, tool execution, sessions, profiles, cron, skills, memory, MCP, and the gateway runtime. Herm gives you a terminal interface for those surfaces.

## Quick start

Install and configure [Hermes Agent](https://hermes-agent.nousresearch.com/docs) first. Herm expects a Hermes home at `~/.hermes`, or `HERMES_HOME` pointing to another Hermes home.

Run Herm without installing:

```bash
bunx herm-tui
```

Install Herm globally:

```bash
bun add -g herm-tui
# or
npm i -g herm-tui
```

Launch Herm:

```bash
herm
herm -c
```

## Main docs

- [Introduction](/introduction) — what Herm is and where it fits.
- [Quickstart](/quickstart) — install and launch Herm.
- [Configuration](/configuration) — environment variables and local preferences.
- [Chat](/features/chat) — streaming chat, images, tool calls, voice, and slash commands.
- [Sessions](/features/sessions) — browse, resume, rename, and inspect sessions.
- [Automation](/features/automation) — kanban, profiles, and cron jobs.
- [Config tab](/features/config) — settings, skills, toolsets, env vars, and memory.
- [Eikon overview](/eikon/overview) — terminal avatars and the Eikon tab.
- [Themes](/customization/themes) — built-in themes and skins.
- [Keybindings](/customization/keybindings) — default and rebindable shortcuts.
- [Slash commands](/customization/slash-commands) — local Herm commands and gateway commands.
- [Plugins](/plugins/overview) — bundled TUI plugin extension points.
- [Troubleshooting](/troubleshooting/common-issues) — common terminal, gateway, and config issues.

## High-value workflows

### Start a session

1. Install Hermes Agent and verify it can run.
2. Install Herm with Bun or npm.
3. Run `herm` for a fresh session or `herm -c` to resume the last session.
4. Use `/status` if the gateway fails or you need active model/path details.

### Navigate the TUI

- Use `Alt+Left` and `Alt+Right` to switch top-level tabs.
- Use `Tab` and `Shift+Tab` to move focus inside a tab.
- Press `Ctrl+K` for the command palette.
- Type `/` in the composer for slash commands.
- Press `F1` for the keybinding reference.

### Customize Herm

- Use `/theme` or `<leader>t` to open the theme picker.
- Use `/skin [name]` to switch a coordinated theme and eikon preset.
- Use `/keys` to view and rebind shortcuts.
- Preferences persist in `~/.hermes/herm/tui.json`, or `$HERM_CONFIG_DIR/tui.json` when set.

### Work with eikons

- Use `/gallery` to browse installed eikons.
- Use `/studio` to create or tune avatar states.
- Use `/marketplace` to browse the public catalog.
- Herm owns the native Eikon UI. The Eikon project owns runtime package, catalog, registry, CLI/library, and browser gallery contracts.

### Extend Herm

Herm plugins are bundled TypeScript modules that register slots, routes, command-palette entries, gateway event listeners, namespaced KV state, and Eikon rasterizers through `HermPluginApi`. Start with the [plugin overview](/plugins/overview), then use the [API reference](/plugins/api-reference) and [examples](/plugins/examples).

## Source truth for agents

When documenting or answering detailed behavior questions, verify volatile surfaces against source:

- Install/package metadata: `package.json`, `README.md` in `liftaris/herm`.
- Tabs and tab slash jumps: `src/app/tabs.ts`.
- Local slash commands: `src/app/slashCommands.ts`, `src/app/slash.tsx`.
- Keybindings: `src/keys/catalog.ts`.
- Themes: `src/theme/manifest.ts`, `src/theme/themes/*.json`.
- TUI preferences and env vars: `src/context/preferences.ts`, `src/utils/paths.ts`, `src/context/gateway-client.ts`.
- Plugin API: `src/plugins/types.ts`, `src/plugins/api.tsx`, `src/plugins/runtime.tsx`.
- Eikon integration: `src/service/eikon.ts` in Herm and the `liftaris/eikon` repo.

Do not invent gateway RPCs, marketplace account flows, hosted moderation, or model-provider behavior. If the docs and source disagree, treat source as truth and open a docs fix.
