---
name: git-worktree
description: Create isolated working directories using git worktrees without affecting the main workspace. Use when you want to use worktree, git worktree, worktree workflow, isolated development, work in worktree, create worktree, or worktree best practices.
tags:
  - git
  - worktree
---

# Git Worktrees

Git worktrees let you check out multiple branches at once into separate directories. This is useful for working on a feature in isolation while keeping your main workspace untouched, or for reviewing another branch without disturbing your current work.

## The Golden Rule

**ALL work happens inside the worktree directory.** Never run git operations, edit files, or switch branches in the main clone while a worktree is active for that branch.

## Creating a Worktree

Create a new worktree with a new branch in one command:

```bash
git worktree add <path> -b <branch-name> origin/main
```

- `<path>` — where to place the worktree (e.g. `worktrees/my-feature`)
- `-b <branch-name>` — creates a new branch starting from `origin/main`
- Always base from `origin/main` (or your repo's default branch) to get a clean, up-to-date starting point

### Why one command matters

Splitting this into `git checkout -b` followed by `git worktree add` creates the branch in your main clone first — changing its state. The single-command form creates everything inside the worktree, leaving the main clone untouched.

### Absolute paths for file editing tools

When using file editing tools inside a worktree, always use absolute paths. Run `pwd` first if you're unsure of your current worktree path.

## Working in the Worktree

Once inside the worktree directory, all normal git operations work as expected — `git add`, `git commit`, `git push`, etc. Just stay in the worktree directory.

## Cleaning Up

When work is merged and you no longer need the worktree:

```bash
git worktree remove <path>
git branch -d <branch-name>
```
