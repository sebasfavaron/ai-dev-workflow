---
name: merge-watch
description: Watch PR checks/review status, keep branch updated, and auto-merge when ready
---

# /merge-watch - Watch and Merge

## Behavior

1. Resolve target PR:
- explicit repo + PR number
- PR number in current repo
- current branch PR

2. Resolve local repo path from feature context first, then local config.

3. Verify `jq` is installed.

4. Run watcher script in foreground first:
- `EXIT_ON_CI_FAIL=1 bash .agents/skills/merge-watch/merge-watch.sh "<repo_path>" "<pr_number>"`
- 1-hour timeout

5. Exit handling:
- `0`: merged
- `1`: closed/fatal
- `2`: CI failed -> inspect failed runs, fix locally, commit/push, retry (max 3 attempts)
- `3`: branch behind and update failed -> rebase/fix conflicts/push, retry
- `4`: missing jq

6. If unresolved after retries or timeout, optional background fallback with log file.

7. On successful merge, offer `/archive-merged`.
