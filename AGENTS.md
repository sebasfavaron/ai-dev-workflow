# AI Dev Workflow

This repo orchestrates development across multiple repositories as a unified feature workflow.

## Agent Rules

- Work style: telegraph; noun-phrases ok; drop grammar; min tokens.
- Before handoff: run full gate (lint/typecheck/tests/docs when configured).
- Workflow freshness: at session start, check if local `HEAD` is behind `origin/main`; if behind, show changelog and offer guided update.

### Git

- All changes to `main` through PRs.
- Pre-push gate mandatory: run `lint_cmd` and `type_check_cmd` from `.cursor/repos.json` before push.
- If branch introduces new failures: do not push until fixed.
- Pre-existing failures on base branch do not block push; call them out explicitly.
- Destructive ops forbidden unless explicit approval.
- Use worktrees when features would conflict.
- Never amend pushed commits; add follow-up commits.

### Critical Thinking

- Fix root cause.
- Call out conflicts/risks and choose safer path.
- Leave breadcrumb notes in thread.

## Repo Paths

Developer-local paths are in `.cursor/local-config.json` (gitignored).

Self-modification: include this repo key in local config with path `.`.

## Shared Data Files

| File | Committed | Purpose |
|------|-----------|---------|
| `local-config.json` | No | Local repo paths |
| `local-config.example.json` | Yes | Template for local config |
| `repos.json` | Yes | Repo metadata and workflow config |
| `teams.json` | Yes (optional) | Optional aliases/project map for teams/prefixes |
| `feature-contexts/` | No | Active feature contexts (`<id>.json`) |
| `current-feature` | No | Current feature id |
| `feature-history.json` | No | Archived feature history |

## Resolve Feature For Skills

When a skill operates on one feature (`/commit`, `/pr`, `/status --current`, `/merge-watch`), resolve in this order:

1. If explicit feature id argument exists and context file exists, use it.
2. Infer from conversation context (ticket/id/branch references).
3. Use `.cursor/current-feature` if valid.
4. If exactly one active context exists, use it and write `current-feature`.
5. If multiple exist and unresolved, ask user to choose.

Legacy migration:
- If `feature-contexts/` missing or empty and `.cursor/feature-context.json` exists, migrate once to `feature-contexts/<id>.json` + `current-feature`, then remove legacy file.

## Optional Team Mapping

`teams.json` is optional. Skills must:
- use it only if file exists and parses
- continue normally if absent
- never block execution because it is missing

## Available Skills

- `/initial-setup`
- `/start`
- `/commit`
- `/pr`
- `/status`
- `/merge-watch`
- `/archive-merged`
- `/history`

## Skill Chaining

Offer one next logical command after completing a skill:
- `/initial-setup` -> `/start`
- `/commit` -> `/pr`
- `/pr` -> `/merge-watch`
- `/merge-watch` (merged) -> `/archive-merged`
- `/status` -> most relevant next action by current state
