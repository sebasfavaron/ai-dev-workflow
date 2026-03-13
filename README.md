# AI Dev Workflow

A Codex-based orchestration layer for developing features across multiple repositories from one control repo.

## Prerequisites

- [Git](https://git-scm.com/)
- [GitHub CLI (`gh`)](https://cli.github.com/) — authenticated via `gh auth login`
- [`jq`](https://jqlang.github.io/jq/) — used by merge-watch
- [Codex](https://openai.com/codex/)

## Quick Start

1. Clone this repo.
2. Open it in Codex.
3. Run `/initial-setup`.

`/initial-setup` will:
- Create `.agents/local-config.json` from the example when missing
- Validate configured repos and write access
- Offer clone or path updates for missing repos
- Verify every configured repo has metadata in `.agents/repos.json`

## Commands

| Command | What it does |
|---------|-------------|
| `/start <issue-or-text>` | Loads issue context (GitHub issue when provided), creates branches/worktrees, saves feature context |
| `/commit` | Shows changes across feature repos, commits with one message, runs pre-push gate, pushes |
| `/pr` | Ensures commits/pushes, creates or updates PRs in dependency order, cross-links PRs |
| `/status` | Read-only status table for all active features or current feature |
| `/merge-watch` | Polls PR, keeps branch updated, attempts auto-merge when checks/reviews allow |
| `/archive-merged` | Moves fully merged/closed features from active context to history |
| `/history` | Browses archived feature history and related transcript hints |
| `/initial-setup` | First-time setup and local config validation |

## Typical Workflow

```text
/start 123              # GitHub issue number, URL, or plain description
  ... make changes ...
/commit
  ... make more changes ...
/pr
/merge-watch
/archive-merged
```

## Configuration

### Local config (gitignored)

`.agents/local-config.json` maps repo names to local filesystem paths.

## Skill Ownership

- `ai-dev-workflow` skills stay in this repo and remain project-workflow specific.
- reusable personal-assistant skills live in the separate `personal-agent` repo.
- expose `personal-agent` skills globally via symlinks in `~/.codex/skills`; do not copy them here.

### Repo config (committed)

`.agents/repos.json` is the single source of truth for:
- platform
- base branch / PR base
- lint and type-check commands
- dependency order
- labels

### Optional team/project map

`.agents/teams.json` is optional.
- If present: skills can use aliases/prefix validation.
- If missing: skills continue without team-based validation.

### Feature context (gitignored)

- `.agents/feature-contexts/<id>.json` — one file per active feature
- `.agents/current-feature` — pointer used by `/commit`, `/pr`, `/status --current`, `/merge-watch`
- `.agents/feature-history.json` — archived features, written by `/archive-merged`

## Naming Conventions

- Branch: `<type>/<id-or-no-ticket>-<description>`
- Commit: `[Type] Summary (ID)` (ID optional)
- PR title: `[ID] Area | Area | Summary` (ID optional)
- Types: `Feat`, `Fix`, `Chore`, `Docs`, `Test`, `Style`
