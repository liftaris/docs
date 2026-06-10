# Herm docs agent instructions

This is the Mintlify docs repo for Herm at `https://herm.liftaris.dev`.

## Product boundaries

- Herm is the keyboard-driven terminal UI for Hermes Agent.
- Hermes Agent owns inference, tools, model/provider setup, sessions, profiles, cron, skills, memory, MCP, gateway runtime, and slash command execution.
- Herm owns the OpenTUI interface, local TUI preferences, keybindings, themes, command palette, tab navigation, client-handled slash commands, bundled TUI plugins, and native Eikon UI.
- Eikon owns avatar package/runtime/catalog contracts, registry, CLI/library behavior, and the browser gallery.
- Do not describe Herm as a model provider, separate agent runtime, hosted marketplace backend, or replacement for Hermes Agent.

## Source of truth

Verify volatile claims against source before publishing:

| Surface | Source |
|---|---|
| Install and package metadata | `/home/kaio/Dev/herm/package.json`, `/home/kaio/Dev/herm/README.md` |
| Tabs and tab slash jumps | `/home/kaio/Dev/herm/src/app/tabs.ts` |
| Local slash commands | `/home/kaio/Dev/herm/src/app/slashCommands.ts`, `/home/kaio/Dev/herm/src/app/slash.tsx` |
| Keybindings | `/home/kaio/Dev/herm/src/keys/catalog.ts` |
| Theme list and colors | `/home/kaio/Dev/herm/src/theme/manifest.ts`, `/home/kaio/Dev/herm/src/theme/themes/*.json` |
| TUI preferences and env vars | `/home/kaio/Dev/herm/src/context/preferences.ts`, `/home/kaio/Dev/herm/src/utils/paths.ts`, `/home/kaio/Dev/herm/src/context/gateway-client.ts` |
| Plugin API | `/home/kaio/Dev/herm/src/plugins/types.ts`, `/home/kaio/Dev/herm/src/plugins/api.tsx`, `/home/kaio/Dev/herm/src/plugins/runtime.tsx` |
| Eikon integration | `/home/kaio/Dev/herm/src/service/eikon.ts`, `/home/kaio/Dev/eikon` |

## Generated sections

Sections between these comments are source-generated drafts:

```mdx
{/* BEGIN AUTO-GENERATED: name */}
...
{/* END AUTO-GENERATED: name */}
```

Regenerate them with:

```bash
python scripts/sync-herm-docs.py
```

Do not hand-edit inside generated blocks. Fix the generator or the source map instead.

## Style

- Use active voice and second person.
- Keep sentences short. One idea per sentence.
- Use sentence case for headings.
- Use root-relative links without `.mdx` extensions.
- Use language tags on all code fences.
- Prefer Mintlify components for scannability: `Steps`, `CardGroup`, `Accordion`, `ParamField`, `CodeGroup`, `Note`, `Tip`, `Warning`.
- Avoid marketing filler: "powerful", "seamless", "robust", "cutting-edge", "simply", "easily".
- Visual style: Vesper-like palette, warm near-black backgrounds, peach/amber accents, restrained monochrome terminal feel. Do not make teal/cyan the main theme.

## Validation before PR

Run all of these before claiming a docs change is ready:

```bash
mint validate
mint broken-links --check-anchors --check-redirects --check-snippets
mint a11y
```

Use `mint broken-links --check-external` on scheduled maintenance, not every small PR.
