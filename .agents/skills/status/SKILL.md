---
name: status
description: View cross-repo status for all active features or current feature
---

# /status - Feature Status

## Modes

- `/status`: show all features in `.agents/feature-contexts/`
- `/status --current [id]`: show one resolved feature

## Table

Use one row per feature/repo with columns:
- Feature
- Ticket/ID
- Started
- Repo
- Branch
- Unpushed (uncommitted files)
- Unmerged (`origin/<base>..HEAD` commit count)
- PR (`#number state`)

## Workflow

1. Load context files.
2. For each repo path in context, gather git state.
3. Resolve PR states in batches via GraphQL where possible.
4. Also report open PR branches not mapped in any active context.
5. Mark archivable features (all PRs merged/closed).
6. Offer one most relevant next command (`/archive-merged`, `/commit`, `/pr`, or `/merge-watch`).
