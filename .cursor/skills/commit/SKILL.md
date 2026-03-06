---
name: commit
description: Stage, commit, run pre-push gate, and push changes across feature repos
---

# /commit - Commit and Push

## Resolve Scope

Resolve current feature using `AGENTS.md` "Resolve Feature For Skills" and load `.cursor/feature-contexts/<id>.json`.

## Workflow

1. Show per-repo changes (`git status --short`, `git diff --stat`).
2. Ask once:
- commit scope (all repos / selected repos / selected files)
- commit message (suggested or custom)
3. Format commit message: `[Type] Summary (ID)` (ID optional).
4. Stage and commit in selected feature repos.
- never force-add ignored files
- do not include unrelated repos outside feature context
5. Mandatory pre-push gate for each repo with commits:
- run `lint_cmd` and `type_check_cmd` from `.cursor/repos.json` when configured
- if branch introduces new failures: stop and fix first
- if failures are already on base: report and proceed
6. Push branches (`git push -u origin <branch_name>`).
7. Keep context file focused on feature/PR linkage (no verbose commit log storage).
8. Offer `/pr`.
