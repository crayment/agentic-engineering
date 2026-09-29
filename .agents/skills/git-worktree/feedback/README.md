# Skill feedback (runtime friction)

After working with git-worktree, if something **non-routine** misled you, leave
feedback here. Do not edit the skill.

Follows the [meta-skill-feedback](https://github.com/crayment/meta-skill-feedback)
convention (`feedback/*.md` open queue, `feedback/resolved/` after review).

**Public repo:** notes are committed and visible. Keep them generic — no company
or customer names, internal hostnames, real repo paths, the names or contents of
gitignored config files, or tokens. Say "a gitignored env file", not its name or
values. Use a generic machine label (`local`, `ci-runner`) in the heading, or
omit it.

## Before you write

1. Skim open `feedback/*.md` (not README, not `resolved/`).
2. **Same issue already open?** Add a **+1** under **Votes** and a short entry under **Agent comments** on that file.
3. **New issue?** Create one timestamped file — see format below.

## When to write

This skill owns **creating a worktree, bootstrapping it, staying inside it, and
committing before handoff**, so write here for:

- `git worktree add <path> -b <branch> origin/main` failed or still touched the main clone
- The bootstrapping guidance missed a class of gitignored state you needed, or the symlink-back advice broke a build or test
- You drifted into the main clone (or a tool did) and the golden rule gave no way to notice
- "Commit before handoff" conflicted with a user or repo rule, with no hint which wins
- Cleanup commands failed in a way the skill did not predict
- Skip routine runs where the worktree behaved as written

## Not feedback

| Situation | Where |
|-----------|--------|
| Showing worktree work in the main clone | `git-spotlight/feedback/` |
| Bulk cleanup of stale worktrees and branches | `git-branch-cleanup/feedback/` |
| A repo has no bootstrap step, or its step is broken | tell the user; that repo's docs or setup script own the fix |
| Conflicts when rebasing the worktree branch | `git-merge-conflict-resolution/feedback/` |

## Filename (new issues only)

`YYYY-MM-DDTHHMM-<short-slug>.md` — timestamp required; lowercase hyphens in slug.

## New issue — body

# YYYY-MM-DD — <id> · <role> · <machine>

## Context
What you were building or reviewing in the worktree.

## What happened
The step or command, what you expected, what happened, the workaround you used.

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
