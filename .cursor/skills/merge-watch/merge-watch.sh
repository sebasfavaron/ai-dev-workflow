#!/usr/bin/env bash
# Avoid set -e: gh pr merge returns non-zero when blocked, which would kill the loop.
set -uo pipefail

REPO_ARG="${1:-}"       # owner/repo or local path to repo directory
PR="${2:-}"
SLEEP_SECS="${SLEEP_SECS:-20}"
EXIT_ON_CI_FAIL="${EXIT_ON_CI_FAIL:-}"

if ! command -v jq >/dev/null 2>&1; then
  echo "Error: jq is required for merge-watch. Install jq and retry." >&2
  exit 4
fi

# Resolve REPO to owner/repo format
if [[ -n "$REPO_ARG" && -d "$REPO_ARG" ]]; then
  cd "$REPO_ARG"
fi

if [[ -z "$REPO_ARG" || -d "$REPO_ARG" ]]; then
  REPO="$(gh repo view --json nameWithOwner -q .nameWithOwner)"
else
  REPO="$REPO_ARG"
fi

# Resolve PR number
if [[ -z "$PR" ]]; then
  if [[ -d "${REPO_ARG:-}" || -z "$REPO_ARG" ]]; then
    PR="$(gh pr view --json number -q .number)"
  else
    echo "PR number is required when passing repo as owner/repo." >&2
    echo "Usage: $0 [repo_path|owner/repo] [pr_number]" >&2
    exit 1
  fi
fi

echo "Watching PR #$PR in $REPO (every ${SLEEP_SECS}s)"

# Auto-detect allowed merge method
MERGE_METHOD=""
REPO_SETTINGS="$(gh api "repos/$REPO" --jq '{s:.allow_squash_merge, m:.allow_merge_commit, r:.allow_rebase_merge}' 2>/dev/null || echo '{}')"
if echo "$REPO_SETTINGS" | jq -e '.s == true' >/dev/null 2>&1; then
  MERGE_METHOD="--squash"
elif echo "$REPO_SETTINGS" | jq -e '.m == true' >/dev/null 2>&1; then
  MERGE_METHOD="--merge"
elif echo "$REPO_SETTINGS" | jq -e '.r == true' >/dev/null 2>&1; then
  MERGE_METHOD="--rebase"
fi
echo "Merge method: ${MERGE_METHOD:---auto}"

UPDATE_FAIL_COUNT=0

while true; do
  # Single API call per iteration; parse with jq
  JSON="$(gh pr view "$PR" --repo "$REPO" --json mergeStateStatus,headRefOid,state -q '.')"
  STATE="$(echo "$JSON" | jq -r .state)"
  MERGE_STATE="$(echo "$JSON" | jq -r .mergeStateStatus)"
  HEAD="$(echo "$JSON" | jq -r .headRefOid)"
  echo "[$(date +%T)] state=$STATE mergeStateStatus=$MERGE_STATE head=${HEAD:0:12}"

  # Early exit if PR is already done
  if [[ "$STATE" == "MERGED" ]]; then
    echo "PR #$PR is already merged!"
    exit 0
  fi

  if [[ "$STATE" == "CLOSED" ]]; then
    echo "PR #$PR was closed without merging."
    exit 1
  fi

  # Keep branch up-to-date when possible
  if [[ "$MERGE_STATE" == "BEHIND" ]]; then
    echo "  -> Updating branch..."
    if gh api -X PUT "repos/$REPO/pulls/$PR/update-branch" >/dev/null 2>&1; then
      UPDATE_FAIL_COUNT=0
    else
      UPDATE_FAIL_COUNT=$((UPDATE_FAIL_COUNT + 1))
      if [[ -n "$EXIT_ON_CI_FAIL" && "$UPDATE_FAIL_COUNT" -ge 2 ]]; then
        echo "  -> Branch is behind and API update failed twice (likely merge conflicts)"
        exit 3
      fi
      echo "  -> Update failed, will retry next cycle"
    fi
  fi

  # Detect definitive CI failure when exit-on-ci-fail is enabled
  if [[ -n "$EXIT_ON_CI_FAIL" && "$MERGE_STATE" == "BLOCKED" ]]; then
    CHECKS="$(gh pr checks "$PR" --repo "$REPO" --json name,bucket 2>/dev/null || echo "[]")"
    N_CHECKS="$(echo "$CHECKS" | jq 'length')"
    if [[ "$N_CHECKS" -gt 0 ]]; then
      N_PENDING="$(echo "$CHECKS" | jq '[.[] | select(.bucket == "pending")] | length')"
      N_FAILED="$(echo "$CHECKS" | jq '[.[] | select(.bucket == "fail")] | length')"
      if [[ "$N_PENDING" -eq 0 && "$N_FAILED" -gt 0 ]]; then
        FAILED_NAMES="$(echo "$CHECKS" | jq -r '[.[] | select(.bucket == "fail") | .name] | join(", ")')"
        echo "  -> CI failed ($N_FAILED of $N_CHECKS): $FAILED_NAMES"
        exit 2
      fi
    fi
  fi

  # Only attempt merge when the PR is actually mergeable
  if [[ "$MERGE_STATE" == "CLEAN" || "$MERGE_STATE" == "HAS_HOOKS" || "$MERGE_STATE" == "UNSTABLE" ]]; then
    echo "  -> Attempting merge..."
    if gh pr merge "$PR" --repo "$REPO" $MERGE_METHOD --delete-branch --match-head-commit "$HEAD" 2>&1; then
      echo "Merged PR #$PR!"
      exit 0
    else
      echo "  -> Merge attempt failed, will retry..."
    fi
  fi

  sleep "$SLEEP_SECS"
done
