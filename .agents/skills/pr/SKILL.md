---
name: pr
description: Create or update PRs across feature repos in dependency order
---

# /pr - Create or Update PRs

## Resolve Scope

Resolve feature via `AGENTS.md` procedure and load `.agents/feature-contexts/<id>.json`.

## Workflow

1. If feature has 2+ repos, ask scope (all repos or one repo).
2. Ensure each selected repo is committed and pushed.
- if uncommitted changes exist, run `/commit` flow first
- enforce pre-push gate (`lint_cmd`, `type_check_cmd`) before pushes
3. Ask once for PR metadata.
- title (suggested or custom)
- summary bullets
- test plan checklist
- labels
4. Create/update PRs in `dependency_order`.
- base branch from `pr_base`
- fill repo PR template
- ensure sections: Summary, What Changed, Test Plan
5. Cross-link related PRs for multi-repo features.
6. Update `repos.<repo>.pr` in feature context with `{number,url,state}`.
7. Offer `/merge-watch`.

## Issue Linking

When feature has issue id/url, add "Related Issue" section in PR body with GitHub issue link.
