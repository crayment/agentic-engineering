---
name: git-merge-conflict-resolution
description: Resolve git merge conflicts by understanding both sides first. Use when you need to resolve conflicts, merge conflict, git conflict, fix merge conflict, resolve merge conflict, handle conflict, or deal with conflicting changes.
trigger_phrases:
  - merge conflict
  - resolve merge conflict
  - fix merge conflict
  - git conflict
tags:
  - git
---

# Git Merge Conflict Resolution

Before resolving any merge conflict, understand what changed on both sides.

Conflict markers show where the conflict is, not why it exists.

## The Workflow

### 1. Find The Merge Base

```bash
# For merge conflicts
git merge-base HEAD MERGE_HEAD

# For rebase conflicts
git merge-base HEAD REBASE_HEAD
```

Save the SHA. You will need it.

### 2. Read What Your Branch Changed

```bash
git diff <merge-base-sha>..HEAD -- path/to/file.ts
```

Read this carefully. What did your branch do?

### 3. Read What Their Branch Changed

```bash
git diff <merge-base-sha>..MERGE_HEAD -- path/to/file.ts
```

Read this carefully. What did their branch do?

For rebase conflicts, compare against `REBASE_HEAD` instead of `MERGE_HEAD`.

### 4. Only Then Read The Conflict Markers

```bash
cat path/to/file.ts
```

With both sides understood, decide how the final code should work.

### 5. Resolve

Edit the file to incorporate both changes appropriately, or choose one side if that is clearly correct.

### 6. Mark As Resolved

```bash
git add path/to/file.ts
git commit
git rebase --continue
```

Use the command that matches the situation. `git commit` is for merges. `git rebase --continue` is for rebases.

## Ours vs Theirs

These meanings flip between merge and rebase.

Check which state you are in:

```bash
test -f .git/MERGE_HEAD && echo "MERGE" || echo "not merge"
test -f .git/REBASE_HEAD && echo "REBASE" || echo "not rebase"
```

During merge:

- `--ours` = current branch, what you are merging into
- `--theirs` = incoming branch, what you are merging from

During rebase:

- `--ours` = upstream branch, what you are rebasing onto
- `--theirs` = your commits being replayed

Why this flips: rebase checks out the target first, then replays your commits on top.

```bash
git checkout --ours path/to/file.ts
git checkout --theirs path/to/file.ts
```

Use those only when you are certain one side should win.

## Remember

1. Always find the merge base first.
2. Always read diffs from both sides.
3. Never blindly accept one side.
4. A few minutes of context saves hours of debugging.
