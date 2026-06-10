---
title: "feat: Add Mintlify automation and maintenance loop"
type: feat
status: active
created: 2026-06-10
---

# feat: Add Mintlify automation and maintenance loop

## Problem frame

The Herm docs site now deploys from `liftaris/docs`, but the remaining Mintlify setup is still mostly manual. The site needs hosted source checks, Mintlify workflows, an agent-facing `skill.md`, a cron-backed external link checker, and a content-quality pass so docs maintenance is durable instead of dependent on manual audits.

## Scope

In scope:

- Enable Mintlify source checks for link rot, anchors/snippets, and spellcheck at a useful non-disruptive level.
- Add Mintlify workflows for source sync, Eikon boundary audits, writing/style typo checks, and SEO metadata audits. Mintlify currently allows one `source-code-agent` workflow per deployment, so the Herm and Eikon source audits share one combined workflow with both source repos in context.
- Add `.mintlify/skills/herm/SKILL.md` so Mintlify can expose an agent-useful Herm skill.
- Add a cron-backed external link checker for `https://herm.liftaris.dev` with durable scripts and scheduler setup.
- Run a page-by-page content-quality pass against the current docs, preserving Herm/Hermes/Eikon boundaries and Vesper-like visual direction.

Out of scope:

- Adding OpenAPI/API playground pages. Herm is a TUI docs site, not an HTTP API reference.
- Adding i18n, versioning, or product dropdowns before there is product need.
- Changing Herm product behavior in `/home/kaio/Dev/herm` or Eikon behavior in `/home/kaio/Dev/eikon`.

## Current context

- Mintlify deploy branch is `main` in `liftaris/docs`.
- `mcp_mintlify_admin_search_code_operations` confirms `deployment.updateSourceChecks` and `workflows.createWorkflow` are available.
- Current hosted deployment has no source checks and no Mintlify workflows.
- Existing repo foundation includes `npm run check`, `.mintlify/AGENTS.md`, snippets, and `scripts/sync-herm-docs.py`.

## Key technical decisions

- Use hosted Mintlify source checks for dashboard-level enforcement, and keep GitHub Actions for repo-level CI. These are complementary: hosted checks catch Mintlify-native source issues, while CI blocks PR regressions.
- Keep workflow prompts narrow and source-verification-first. Workflows should open PRs only for verifiable docs deltas, not broad rewrites.
- Store cron link-check implementation in the docs repo and schedule it through Hermes cron. The script should stay quiet when no issue exists and print actionable diagnostics when links fail.
- Treat content-quality edits as docs changes only. Do not invent Herm capabilities that are not supported by source.

## Implementation units

### U1. Enable hosted Mintlify source checks

**Goal:** Configure Mintlify deployment source checks for link rot and spellcheck.

**Requirements:** hosted link checking, snippet/anchor checking, spellcheck if useful.

**Dependencies:** none.

**Files:** none expected for source-check configuration. Changes happen through Mintlify Admin MCP.

**Approach:** Use `deployment.updateSourceChecks` with `link-rot` enabled at warning level and `checkAnchors` / `checkSnippets` enabled. Enable `vale-spellcheck` at warning level so it surfaces issues without blocking legitimate product terms like Herm, Hermes, and Eikon until a vocabulary pass exists.

**Test scenarios:**

- Source checks readback returns configured `link-rot` with anchors/snippets enabled.
- Source checks readback returns configured `vale-spellcheck` at warning level.

**Verification:** Admin MCP readback shows the source-check configuration, and local `npm run check` still passes.

### U2. Add Mintlify workflows

**Goal:** Create narrow Mintlify workflows for maintenance automation.

**Requirements:** weekly combined Herm/Eikon source sync audit, docs style/typo PR workflow, SEO metadata audit.

**Dependencies:** U1 optional but preferred.

**Files:** `.mintlify/AGENTS.md` may be updated if workflow prompts reveal missing project instructions.

**Approach:** Use `workflows.createWorkflow` with V2 workflows. Use one combined source-code-agent workflow for Herm and Eikon because Mintlify enforces one source-code-agent workflow per deployment. Use cron triggers for weekly source and SEO audits. Use push triggers for typo/style or broken-link maintenance where supported. Include context repos for `liftaris/docs`, `liftaris/herm`, and `liftaris/eikon` as appropriate. Prompts must require source verification, avoid public provenance/process language, preserve generated blocks, and include validation output in PRs.

**Test scenarios:**

- `workflows.listWorkflows` returns all intended workflows with expected names, types, triggers, and context repos.
- At least one workflow can be manually triggered if safe and plan limits allow, or readback confirms it is enabled.
- Workflow prompts do not instruct broad rewrites or unsupported feature invention.

**Verification:** Admin MCP lists workflows and no failed workflow creation responses remain.

### U3. Add agent-facing Herm skill

**Goal:** Add `.mintlify/skills/herm/SKILL.md` so `/skill.md` and agent consumers can understand how to use Herm docs.

**Requirements:** useful to agents, source-aligned, boundary-aware.

**Dependencies:** none.

**Files:** `.mintlify/skills/herm/SKILL.md`, possibly `.mintignore` if needed to ensure the skill is processed correctly.

**Approach:** Write a compact skill with Herm overview, install/start commands, key docs links, source boundaries, and high-value workflows. Keep it factual and avoid unsupported claims.

**Test scenarios:**

- `mint validate` accepts the skill file.
- `https://herm.liftaris.dev/skill.md` or equivalent skill export reflects Herm guidance after deploy.
- The skill links to existing root-relative docs pages.

**Verification:** Local Mintlify checks pass and live export can be fetched after deploy.

### U4. Add cron-backed external link checker

**Goal:** Add a durable external link checker for `herm.liftaris.dev` and schedule it through Hermes cron.

**Requirements:** cron-backed, external links, actionable output.

**Dependencies:** none.

**Files:** `scripts/check-external-links.py`, `package.json`, `.github/workflows/mintlify-checks.yml` if an optional manual command is useful.

**Approach:** Implement a script that fetches live Markdown exports or `llms.txt`, extracts external links, checks HTTP status with timeouts, and prints only failures. Add an npm script for manual use. Create a Hermes cron job that runs the script weekly and delivers output only when failures exist.

**Test scenarios:**

- Script exits zero and prints nothing when all checked links pass.
- Script reports URL, source page, status/error, and suggested action for failures.
- Cron job exists with a self-contained prompt or script path and does not recursively create cron jobs.

**Verification:** Run the script locally; list cron jobs and confirm the scheduled job exists.

### U5. Run page-by-page content-quality pass

**Goal:** Improve docs quality now that the repo is source-synced and deployed correctly.

**Requirements:** page-by-page pass, preserve source truth, best-practice Mintlify docs quality.

**Dependencies:** U3 helpful but not required.

**Files:** all `*.mdx` pages may be touched, but edits should be targeted.

**Approach:** Read each page, remove stale or unsupported claims, improve headings/descriptions, keep code fences tagged, add links between related pages, and preserve generated blocks. Verify volatile feature surfaces against `/home/kaio/Dev/herm` and `/home/kaio/Dev/eikon` before changing them.

**Test scenarios:**

- `mint validate` passes.
- `mint broken-links --check-anchors --check-redirects --check-snippets` passes.
- `mint a11y` passes.
- Page exports still include the main docs pages in `llms.txt`.

**Verification:** `npm run check` passes and spot checks of live Markdown exports show updated content after deployment.

## Risks and mitigations

- **Workflow churn:** Keep prompts narrow, source-verification-first, and PR-producing only when a concrete diff is justified.
- **Spellcheck false positives:** Start at warning level until product vocabulary is tuned.
- **Mintlify API shape mismatch:** Use `search_code_operations` schemas before each write call and verify with readback.
- **Cron noise:** Script should be silent on success and include failure-only output.
- **Content drift:** Generated blocks must be updated through `scripts/sync-herm-docs.py`, not hand-edited.

## Completion criteria

- Source checks configured and verified by readback.
- Mintlify workflows configured and verified by readback.
- `.mintlify/skills/herm/SKILL.md` exists and validates.
- External link checker script exists, runs locally, and a Hermes cron job is scheduled.
- Content pass completed with targeted page edits.
- `npm run check` passes.
- Changes are committed, pushed, PR opened, CI watched, and live deployment verified after merge.
