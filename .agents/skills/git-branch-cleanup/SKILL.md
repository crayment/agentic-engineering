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

One short bullet list under the inventory. Name each item and why, in a few words. Leave out anything that stays.

Never propose:

- a branch with an open MR or PR
- the branch checked out in the main clone
- the local default branch when the user's rules say to keep it

`git branch -d` refuses squash-merged and rewritten work even when it shipped. When the forge says the work merged, say `-D` is needed and ask before using it.

Ask which items should go. Do not delete in this step.

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

Rerun the script with `--no-fetch`, fill its placeholders, and paste it. Then say in one short list what was deleted and what was skipped.

## Birdhouse Guidance

This is usually a single-agent task.

If the repo has many worktrees or a confusing branch state, it can help to delegate inspection to one child agent and keep deletion decisions with the main agent. Even then, only one agent should perform the actual cleanup commands.
