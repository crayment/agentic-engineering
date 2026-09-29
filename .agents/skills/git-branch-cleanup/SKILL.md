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
- Prefer trash over deletion for anything that exists nowhere else.
- Do not remove worktrees without explicit approval.
- Do not suggest editing global git config or adding aliases.
- Treat branch cleanup and worktree cleanup as related but separate actions.
- A branch with no worktree still belongs in the inventory. A worktree with a detached HEAD still belongs in the inventory.
- `: gone]` is one flag inside the inventory. An empty gone-list is not a clean repo.

## Step 1: Run The Inventory Script

Run the bundled script. Do not assemble the inventory by hand.

```bash
python3 <this-skill-dir>/scripts/branch_inventory.py <any path inside the repo>
```

It finds the main clone, runs `git fetch --prune` (skip with `--no-fetch`), and prints one nested markdown list. It counts commits against `origin/HEAD` (falling back to `origin/main`), never the local `main` branch. Unpushed commits exclude anything already on the remote branch or on `origin/main`. MRs and PRs come from `glab` or `gh` when one matches `origin`. Linear ticket links come from the `linear` CLI when it is installed. Warnings go to stderr.

Each worktree gets a `Commits`, `Unpushed`, and `Uncommitted` bullet, then its MR and ticket links. Branches without a worktree get one line each under `No worktree`.

## Step 2: Fill The Summaries

The script leaves `{{summarize in ...: ...}}` placeholders where a sentence needs judgment. Replace every one. Do not leave a placeholder in the answer.

- `Unpushed` placeholders list commit subjects. Replace with one sentence saying what that work does. Read `git log -p` only when the subjects are vague.
- `Uncommitted` placeholders list entry and file counts, then porcelain paths. Replace with at most two sentences after reading `git -C <worktree> diff` and any short untracked files. Summarize a large untracked folder by what is in it, not file by file.

Say what changed, not the file count alone. Name a change that appears in more than one worktree.

## Step 3: Present It

Paste the filled list as-is. Do not re-format it into tables or code blocks, and do not add a second inventory.

Then check worktree metadata:

```bash
git worktree prune --dry-run
```

Mention it only when it prints something.

## Step 4: Propose Cleanup

Two short bullet lists under the inventory, **Trash** and **Delete**. Name each item and why, in a few words. Leave out anything that stays.

- **Trash** is for anything that exists nowhere else: unpushed commits or uncommitted changes. It stays local and can be restored.
- **Delete** is for work that is already safe elsewhere: fully pushed, or merged through an MR or PR, with no uncommitted changes.

When you judge work superseded or folded into something else, give the evidence in a few words, for example "SSF-2016 shipped in !5454."

Never propose:

- a branch with an open MR or PR
- the branch checked out in the main clone
- the local default branch when the user's rules say to keep it

Propose deleting the local default branch when the user's rules say not to keep one.

When the main clone is on `spotlight`, read its `Spotlight` bullet:

- `tracking origin/main, N commits behind`: propose updating it with `git -C <main clone> merge --ff-only origin/main`.
- `showing <branch>`: flag which branch it shows and how far behind origin/main that branch is. Propose nothing.
- Commits on no other local branch: flag them. Propose nothing.

When the Trash section has branches older than 30 days, propose emptying them in a third list.

Ask which items should go. Do not change anything in this step.

A bare "approved", "yes", or "go ahead" approves every item you proposed: each trash, each delete, any `-D` you flagged, and a spotlight update. Items the user names as exceptions stay. Then run Steps 5 to 7 without asking again.

## Step 5: Trash Approved Items

Dry-run first, then run it on the approved branches, from anywhere in the repo:

```bash
python3 <this-skill-dir>/scripts/trash_branch.py <repo> <branch>... --dry-run
python3 <this-skill-dir>/scripts/trash_branch.py <repo> <branch>...
```

For each branch it snapshots uncommitted and untracked changes in its worktree as one commit on top of the branch, creates `trash/<date>/<branch>`, removes the worktree, then deletes the original name. Ignored files such as `.env` links are not saved. It refuses a branch checked out in the main clone. `trash/*` is local only; never push it.

To restore, rename it back and re-add the worktree. When the tip is a `trash: snapshot` commit, `git reset HEAD~1` inside the worktree brings the changes back as uncommitted:

```bash
git branch -m trash/<date>/<branch> <branch>
git worktree add .worktrees/<name> <branch>
git -C .worktrees/<name> reset HEAD~1
```

## Step 6: Delete Approved Items

Run from the main clone. Remove the worktree before its branch.

```bash
git worktree remove .worktrees/<name>
git branch -d <branch>
```

`git branch -d` refuses squash-merged and rewritten work even when it shipped. If you already said an item needs `-D` and the user approved it, use `git branch -D`. Otherwise stop and report why instead of escalating.

Emptying trash is a deletion. Use `git branch -D trash/<date>/<branch>` only for items the user named.

Stale worktree metadata:

```bash
git worktree prune
```

An approved spotlight update is `git -C <main clone> merge --ff-only origin/main`. If it refuses, report why. Do not reset.

## Step 7: Verify Result

Rerun the inventory script with `--no-fetch`, fill its placeholders, and paste it. Then say in one short list what was trashed, deleted, and skipped.

If a script or step misled you, failed oddly, or needed discovery not covered here, write one file in `feedback/`. See [feedback/README.md](feedback/README.md). Do not edit this skill or its scripts. Skip when the run was routine.

## Birdhouse Guidance

This is usually a single-agent task.

If the repo has many worktrees or a confusing branch state, it can help to delegate inspection to one child agent and keep deletion decisions with the main agent. Even then, only one agent should perform the actual cleanup commands.
