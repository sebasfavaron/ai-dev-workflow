---
name: history
description: Browse archived feature history and find related transcripts
---

# /history - Browse Feature History

## Source

Read `.agents/feature-history.json` (array, newest first).

## Modes

- `/history`: list latest 10
- `/history <id>`: show one feature in detail
- `/history search <keyword>`: search by id/title/branch/summary/repo

## Detail View

Show:
- id
- type
- branch
- created/finished timestamps
- related issue link if present
- per-repo PR links
- summary

## Transcript Discovery (best-effort)

When showing detail for one feature:
1. Search workspace transcript directory under the local Codex transcript storage when available.
2. Match feature id and branch name with `rg -l`.
3. Show recent matching transcript files.
