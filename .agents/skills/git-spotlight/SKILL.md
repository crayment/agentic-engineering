---
name: git-spotlight
description: Use this skill to make the main clone of a repo reflect the current HEAD of a worktree branch for review. Use when you want to spotlight a worktree, make the main clone reflect a worktree's HEAD, or browse worktree work in your editor.
tags:
  - git
  - worktree
---

# Git Spotlight

The spotlight technique points the main clone's `spotlight` branch at the current HEAD of a worktree, so you can browse and review the work in your editor without disturbing your own branch.

## Prerequisites

- You must know the absolute path to the worktree directory.
- You must know the absolute path to the main clone directory (the repo root, not the worktree).

## Step 1 - Confirm worktree is fully committed

```bash
# workdir: <WORKTREE_PATH>
git status
```

Must show `nothing to commit, working tree clean`. If not, commit or stash all changes before continuing.

## Step 2 - Check main clone state

```bash
# workdir: <MAIN_CLONE_PATH>
git status
```

Stop and ask the user what to do if the main clone is dirty. Do not proceed until the main clone is clean.

## Step 3 - Get the worktree HEAD SHA

```bash
# workdir: <WORKTREE_PATH>
git rev-parse HEAD
```

Save this SHA for the next step.

## Step 4 - Check out the spotlight branch in the main clone

```bash
# workdir: <MAIN_CLONE_PATH>
git branch --list spotlight
```

- If the branch does not exist: `git checkout -b spotlight`
- If the branch already exists: `git checkout spotlight`

Then reset it to the worktree HEAD:

```bash
# workdir: <MAIN_CLONE_PATH>
git reset --hard <SHA>
```

## Step 5 - Verify

```bash
# workdir: <MAIN_CLONE_PATH>
git log --oneline -1
git status
```

Confirm the top commit matches the worktree HEAD and the tree is clean.

## Tell the user

Inform the user that the spotlight is set.

## Notes

- The `spotlight` branch is a plain local branch. It is never pushed to the remote.
- `reset --hard` is safe here because `spotlight` is dedicated to this purpose and has no independent history worth preserving.
- If the worktree gains new commits later, re-run this procedure to advance `spotlight` to the new HEAD.
