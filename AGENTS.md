# Herm documentation repo instructions

This repository contains the Mintlify site for Herm.

- Site config: `docs.json`
- Pages: `*.mdx`
- Reusable snippets: `snippets/`
- Private Mintlify agent instructions: `.mintlify/AGENTS.md`
- Source repo: `/home/kaio/Dev/herm`
- Eikon source repo: `/home/kaio/Dev/eikon`

Root `AGENTS.md` is ignored by Mintlify through `.mintignore`. Keep public-facing docs in MDX pages and private operational notes under `.ignore/`.

## Required checks

```bash
mint validate
mint broken-links --check-anchors --check-redirects --check-snippets
mint a11y
```

Run `python scripts/sync-herm-docs.py` before editing generated reference sections.
