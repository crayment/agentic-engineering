# Skill feedback (runtime friction)

After a git-branch-cleanup run, if something **non-routine** misled you, leave
feedback here. Do not edit the skill or its scripts.

Follows the [meta-skill-feedback](https://github.com/crayment/meta-skill-feedback)
convention (`feedback/*.md` open queue, `feedback/resolved/` after review).
See `resolved/` for a handled example.

**Public repo:** notes are committed and visible. Keep them generic — no company
or customer names, internal hostnames, remote URLs, real branch or ticket names,
or tokens. Describe the repo shape (squash-merges, nested worktrees, detached
HEADs), not the repo. Use a generic machine label (`local`, `ci-runner`) in the
heading, or omit it.

## Before you write

1. Skim open `feedback/*.md` (not README, not `resolved/`).
2. **Same issue already open?** Add a **+1** under **Votes** and a short entry under **Agent comments** on that file.
3. **New issue?** Create one timestamped file — see format below.

## When to write

This skill owns **the inventory, the proposal rules, and the trash/delete
scripts**, so write here for:

- `branch_inventory.py` missed a branch or worktree, miscounted commits, unpushed, or uncommitted work, or chose the wrong base
- MR/PR or ticket links were wrong or missing when `glab`, `gh`, or `linear` was installed and matched
- A `{{summarize ...}}` placeholder was ambiguous about what to write
- A proposal rule was wrong for the repo — a branch that should have been Trash landed in Delete, or the reverse
- `trash_branch.py` lost or mis-snapshotted work, refused unexpectedly, or the restore steps did not bring it back
- `git branch -d`, `worktree remove`, or the spotlight `merge --ff-only` failed in a way the skill did not predict
- Skip routine runs where the inventory, proposal, and cleanup went as written

## Not feedback

| Situation | Where |
|-----------|--------|
| Creating or working inside a worktree | `git-worktree/feedback/` |
| Pointing the main clone's `spotlight` branch at a worktree | `git-spotlight/feedback/` |
| Which branches the user wants to keep | the user's own rules — follow them |
| A bug in `glab`, `gh`, or the `linear` CLI itself | that tool's issue tracker |
| The filled inventory and the trashed/deleted/skipped list | the answer to the user |

## Filename (new issues only)

`YYYY-MM-DDTHHMM-<short-slug>.md` — timestamp required; lowercase hyphens in slug.

## New issue — body

# YYYY-MM-DD — <id> · <role> · <machine>

## Context
The repo shape and what you were cleaning up.

## What happened
The step or script, what you expected, what happened, the workaround you used.

## Suggestion (optional)
Smallest skill change that would help. Do not apply it yourself.

## Votes

- **YYYY-MM-DDTHHMM** — <id> · opened

## Agent comments

_(none yet)_

## Same issue again — append only

**Votes:** `- **YYYY-MM-DDTHHMM** — <id> · +1`

**Agent comments:** `### YYYY-MM-DDTHHMM — <id>` then one short paragraph.

## Rules

- One topic per file · duplicates are +1 votes, not new files · no secrets · reviewer moves handled notes to `resolved/`
