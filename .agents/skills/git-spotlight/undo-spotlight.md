# Git: Undo Spotlight Worktree

Reverse a spotlight: return the main clone to its pre-spotlight branch and delete the `spotlight` branch.

## Prerequisites

- You must know the **previous branch** the main clone was on before spotlighting. This should have been recorded and communicated to the user during the spotlight procedure.
- You must know the absolute path to the main clone directory.

## Step 1 — Check out the previous branch

```bash
# workdir: <MAIN_CLONE_PATH>
git checkout <PREVIOUS_BRANCH>
```

The main clone is now restored to where it was before the spotlight was applied.

## Step 2 — Delete the spotlight branch

```bash
# workdir: <MAIN_CLONE_PATH>
git branch -D spotlight
```

## Step 3 — Verify

```bash
# workdir: <MAIN_CLONE_PATH>
git branch --list spotlight   # should return nothing
git status                    # should show the previous branch, clean
```

## Tell the user

Inform the user that the spotlight has been undone and the `spotlight` branch has been deleted. The main clone is back on `<PREVIOUS_BRANCH>`.

## Notes

- `-D` (force delete) is used because `spotlight` will not be merged into anything — this is intentional.
- The worktree and its branch are completely unaffected by this operation.
- To re-apply the spotlight later, follow [spotlight.md](spotlight.md) again.
