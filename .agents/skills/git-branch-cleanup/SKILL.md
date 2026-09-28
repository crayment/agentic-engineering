---
name: git-branch-cleanup
description: Inventory every local branch and worktree, then clean up only what the user approves.
trigger_phrases:
  - branch cleanup
  - clean up branches
  - delete gone branches
  - remove stale branches
  - list worktrees
  - list local branches
tags:
  - git
---

# Git Branch Cleanup

Inventory every local branch and every worktree, then clean up only what the user approves.

This skill is intentionally conservative.

- Inspect first.
- Show the full inventory before proposing deletions.
- Get explicit approval before deleting anything.
- Prefer safe deletion.
- Handle worktrees carefully.

## Core Rules

- Do not delete branches immediately after discovering them.
- Do not force-delete branches unless the user explicitly approves that escalation.
- Do not remove worktrees without explicit approval.
- Do not suggest editing global git config or adding aliases.
- Treat branch cleanup and worktree cleanup as related but separate actions.
- A branch with no worktree still belongs in the inventory. A worktree with a detached HEAD still belongs in the inventory.
- `: gone]` is one flag inside the inventory. An empty gone-list is not a clean repo.

## Step 1: Refresh Remote State

Run this from the main clone when the current directory is a linked worktree.

```bash
git fetch --prune
```

Default branch:

```bash
git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null || true
```

Fall back to `origin/main` when that ref is missing.

## Step 2: Inventory Everything

Build one record for every local branch and every worktree. Collect all of it before writing the report.

Branches:

```bash
git for-each-ref --sort=-committerdate \
  --format='%(committerdate:short)|%(refname:short)|%(upstream:short)|%(upstream:track)|%(objectname:short)|%(subject)' \
  refs/heads/
```

Worktrees:

```bash
git worktree list --porcelain
```

Dirty state, once per worktree path:

```bash
git -C "$path" status --porcelain
```

Unique commits against the default branch. When `git merge-base` fails, the histories are unrelated: report the tip date and subject, and say there is no common history. Do not print the unrelated commit count as if it were the branch's own work.

```bash
git merge-base "$default" "$branch"
git rev-list --count "$default".."$branch"
git log --reverse --format='%cs' "$default".."$branch"
```

The date range is the oldest and newest `%cs` in that unique range. Zero unique commits means the tip is already in the default branch.

Forge state, when the tool and the remote agree:

- GitHub (`gh`, `github.com` remote): `gh pr list --head "$branch" --state all --json number,state,title`
- GitLab (`glab`, `gitlab.com` remote): the commit's merge requests, `GET projects/:id/repository/commits/:sha/merge_requests`. A 404 means that commit is not on the server. Detached worktrees use the HEAD sha the same way.

Skip the forge call when neither tool matches the remote, and say the forge was not checked.

## Step 3: Inspect Worktree Metadata

```bash
git worktree list
git worktree prune --dry-run
```

Note stale metadata, a worktree whose branch you might delete, and a directory that is not a registered worktree.

## Step 4: Present The Inventory, Then A Cleanup Plan

Present the inventory first. Group it into checked out, detached, and not checked out. Every local branch appears once. Every worktree appears once.

Each record has:

- branch name, or `detached` plus the short sha
- worktree path, or `no worktree`
- tip date and the tip subject
- unique commit date range and count against the default branch
- dirty: `clean`, or the porcelain count and paths when the list is short
- upstream, including `: gone]` when the tracking branch is gone
- forge result: `!123 merged`, `no MR`, `commit not on server`, or `forge not checked`

After the inventory, propose cleanup in these buckets:

- `Safe to delete`
- `Needs force delete`
- `Stale worktree metadata`
- `Worktrees needing review`

`git branch --merged` and `git branch -d` are weak evidence. Squash merges and rewritten history leave shipped work looking unmerged, so `-d` refuses it. When the forge says the work merged, say that `-D` is required and ask before using it.

Ask explicitly which items should be cleaned up. Do not delete in this step.

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

Use this only after the user explicitly approves force deletion. Approval of a named set that you already described as requiring `-D` counts.

## Step 7: Worktree Cleanup

Handle worktrees separately from branches. Run removal from the main clone.

Stale metadata only:

```bash
git worktree prune
```

Remove a specific worktree directory only with explicit approval:

```bash
git worktree remove path/to/worktree
```

If a branch is still checked out in a worktree, remove the worktree before deleting the branch.

## Step 8: Verify Result

Repeat the inventory for what remains, plus:

```bash
git branch -vv | grep ': gone]' || true
git worktree list
git worktree prune --dry-run
```

Report what was deleted, what was skipped, and what still needs attention.

## Birdhouse Guidance

This is usually a single-agent task.

If the repo has many worktrees or a confusing branch state, it can help to delegate inspection to one child agent and keep deletion decisions with the main agent. Even then, only one agent should perform the actual cleanup commands.
