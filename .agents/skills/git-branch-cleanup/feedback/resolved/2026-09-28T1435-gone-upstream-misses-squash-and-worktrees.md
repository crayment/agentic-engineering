# Gone-upstream scan misses squash-merged and rewritten history

## Context

Cleanup of a repo that squash-merges by default, rewrote history (old local branches share no merge-base with current main), and keeps nested git worktrees. The ask was to consider every local branch and worktree, not only ones whose upstream disappeared.

## What happened

`git branch -vv | grep ": gone]"` returned nothing, so the skill's only discovery step reported a clean repo. The stale set was elsewhere: local branches with no upstream, detached review worktrees of merged merge requests, and an empty leftover directory. `git branch --merged` and `git branch -d` both refuse those branches, because squash merges and the history rewrite mean the commits are not ancestors of main. Forge MR state was the check that actually said whether the work had shipped. Worktrees have to be removed from the main clone before their branches.

## Suggestion

Inventory every local branch and every worktree. Classify with the forge MR state. Treat "MR merged, but -d refuses" as expected for squash merges and rewritten history, and ask for -D explicitly. Keep gone-upstream as one bucket, not the whole job.

## Votes

- **2026-09-28T1435** — opened

## Agent comments

### 2026-09-28T1715 — skill update
The inventory step now covers every local branch and worktree. Gone-upstream is one flag. Forge state is how shipped squash-merges get classified, and -D stays behind an explicit ask.
