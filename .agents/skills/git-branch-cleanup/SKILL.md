---
name: git-branch-cleanup
description: Safely inspect and clean up local branches whose remote counterparts have been deleted, with explicit approval before deletions.
trigger_phrases:
  - branch cleanup
  - clean up branches
  - delete gone branches
  - remove stale branches
tags:
  - git
---

# Git Branch Cleanup

Use this skill to safely inspect and clean up local branches whose remote tracking branches are gone.

This skill is intentionally conservative.

- Inspect first.
- Present a cleanup plan.
- Get explicit approval before deleting anything.
- Prefer safe deletion.
- Handle worktrees carefully.

## Core Rules

- Do not delete branches immediately after discovering them.
- Do not force-delete branches unless the user explicitly approves that escalation.
- Do not remove worktrees without explicit approval.
- Do not suggest editing global git config or adding aliases.
- Treat branch cleanup and worktree cleanup as related but separate actions.

## Step 1: Refresh Remote State

Start by pruning deleted remote refs.

```bash
git fetch --prune
```

This updates your local view of which remote branches still exist.

## Step 2: Inspect Stale Branches

Find local branches whose tracking branch is gone.

```bash
git branch -vv | grep ': gone]'
```

Useful follow-up commands:

```bash
# Count stale branches
git branch -vv | grep -c ': gone]'

# Show all local branches with tracking info
git branch -vv
```

The goal here is to inspect, not delete.

## Step 3: Inspect Worktrees

If the repo uses worktrees, inspect them too.

```bash
git worktree list
git worktree prune --dry-run
```

Look for:

- stale worktree metadata
- worktrees attached to branches you might want to delete
- paths that should not be touched without confirmation

## Step 4: Present A Cleanup Plan

Before making changes, present a short cleanup plan to the user.

Include:

- branches that appear safe to delete with `git branch -d`
- branches that are not fully merged and would require force deletion
- worktrees that are stale metadata only
- worktrees or directories that would need removal

Recommended presentation shape:

- `Safe to delete`
- `Needs force delete`
- `Stale worktree metadata`
- `Worktrees needing review`

Ask explicitly which items should be cleaned up.

## Step 5: Safe Deletion First

For approved branches, prefer safe deletion:

```bash
git branch -d branch-name
```

If deleting multiple approved branches, do it as a reviewed list, not a blind one-liner.

Example:

```bash
git branch -d branch-one branch-two branch-three
```

If a branch does not delete cleanly, stop and report why instead of automatically escalating.

## Step 6: Force Delete Only By Explicit Approval

If a branch still contains unmerged work and the user wants it removed anyway:

```bash
git branch -D branch-name
```

Use this only after the user explicitly approves force deletion.

## Step 7: Worktree Cleanup

Handle worktrees separately from branches.

Stale metadata only:

```bash
git worktree prune
```

Remove a specific worktree directory only with explicit approval:

```bash
git worktree remove path/to/worktree
```

If a branch is still checked out in a worktree, resolve that relationship before deleting the branch.

## Step 8: Verify Result

After cleanup, verify the remaining state.

```bash
# Remaining stale branches
git branch -vv | grep ': gone]' || true

# Current branches
git branch -vv

# Current worktrees
git worktree list
```

Report back with:

- what was deleted
- what was skipped
- what still needs attention

## Birdhouse Guidance

This is usually a single-agent task.

If the repo has many worktrees or a confusing branch state, it can help to delegate inspection to one child agent and keep deletion decisions with the main agent. Even then, only one agent should perform the actual cleanup commands.
