---
name: archive-merged
description: Archive features whose PRs are all merged or closed
---

# /archive-merged - Archive Completed Features

## Workflow

1. Load target features from `.cursor/feature-contexts/*.json` (or a specific id).
2. For each feature, gather PR references from `repos.<repo>.pr.number`.
3. Resolve PR states in batches.
4. A feature is archivable only if:
- it has at least one PR
- every PR state is `MERGED` or `CLOSED`
5. For archivable features:
- upsert entry into `.cursor/feature-history.json`
- remove `.cursor/feature-contexts/<id>.json`
- remove worktree paths where `worktree: true` (best effort)
- update `.cursor/current-feature` if needed
6. Report archived features; if none, state unchanged.
