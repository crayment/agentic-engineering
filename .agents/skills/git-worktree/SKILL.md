---
name: git-worktree
description: Create isolated working directories using git worktrees without affecting the main workspace. Use when you want to use worktree, git worktree, worktree workflow, isolated development, work in worktree, create worktree, or worktree best practices.
trigger_phrases:
  - git worktree
  - create a worktree
  - use a worktree
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

### Commit early and often

**Commit whenever the user might want to test or review the work.** Switching to a worktree with uncommitted changes is often annoying or outright impossible — but pointing the spotlight at a commit is instant and clean. When in doubt, commit.

**If the user asks you to go make something on a worktree, treat a commit as the default finish line unless they explicitly say not to commit.** Handing back a worktree with uncommitted changes makes review, testing, and spotlighting harder than it needs to be.

**Implementation complete: NEVER call worktree work complete, ready to test, or ready for handoff until the current changes are committed.**

## Finishing Work

DO NOT stop and tell the user you have made the changes without first committing your work! 
When using the worktree workflow the human will likely be reviewing your commits - not unstaged changes. So please always commit before stopping.

**Never clean up a worktree without checking for uncommitted changes first.**

## Cleaning Up

When work is merged and you no longer need the worktree:

```bash
git worktree remove <path>
git branch -d <branch-name>
```
