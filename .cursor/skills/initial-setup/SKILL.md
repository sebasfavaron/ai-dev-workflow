---
name: initial-setup
description: Configure local paths and validate workflow prerequisites
---

# /initial-setup - Environment Setup

## Workflow

1. Check prerequisites: `gh`, `git`, `jq`.
2. Ensure `gh auth status` is valid.
3. Create `.cursor/local-config.json` from example if missing.
4. Sync missing repo keys from `.cursor/repos.json` into local config with default `../<repo>` paths.
5. Validate each configured path:
- directory exists
- git repo exists
- write access (warning-only)
6. For missing repos, offer:
- clone now
- set different path
- skip/remove from local config
7. Verify every configured repo has metadata in `.cursor/repos.json`.
8. If `.cursor/teams.json` exists, validate JSON; if absent, report "optional file not present" and continue.
9. Print summary and offer `/start`.

## Notes

- Safe to re-run.
- No automatic pushes.
