---
name: start
description: Start a feature with issue context, branch creation, and feature context setup
---

# /start - Initialize Feature

## Inputs

Accepts:
- GitHub issue number (e.g. `123`)
- GitHub issue URL
- free text or `none`

## Data Sources

- `.cursor/repos.json` for repo metadata
- `.cursor/local-config.json` for local paths
- `.cursor/teams.json` only if present (optional)

## Workflow

1. Resolve optional issue context.
- If issue number/URL is provided: use `gh issue view` to fetch title/body.
- If lookup fails: continue with manual input.

2. Propose setup in one prompt.
- type (`fix|feat|chore|docs|test|style`)
- branch slug
- selected repos (from `repos.json`, ordered by `dependency_order`)
- work mode (`worktree` default, or in-place)
- start implementation now (`yes` default)

3. Build branch name.
- `<type>/<id-or-no-ticket>-<slug>`

4. Create branches per repo.
- Default worktree mode:
  - `git fetch origin`
  - `git worktree add ../<repo>--<branch-suffix> origin/<base_branch> -b <branch_name>`
- In-place mode:
  - `git fetch origin`
  - `git checkout <base_branch>`
  - `git pull origin <base_branch>`
  - `git checkout -b <branch_name>`

5. Save feature context.
- Write `.cursor/feature-contexts/<id>.json`
- Write `.cursor/current-feature` with the same id
- Support one-time migration from legacy `.cursor/feature-context.json`

6. Output short summary and offer next action.
- If user chose setup-only, stop and remind `/commit`.
