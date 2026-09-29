# Skill feedback (runtime friction)

After a git-spotlight run, if something **non-routine** misled you, leave
feedback here. Do not edit the skill.

Follows the [meta-skill-feedback](https://github.com/crayment/meta-skill-feedback)
convention (`feedback/*.md` open queue, `feedback/resolved/` after review).

**Public repo:** notes are committed and visible. Keep them generic — no company
or customer names, internal hostnames, real repo or worktree paths, branch
names, or tokens. Use placeholders like `<MAIN_CLONE_PATH>`. Use a generic
machine label (`local`, `ci-runner`) in the heading, or omit it.

## Before you write

1. Skim open `feedback/*.md` (not README, not `resolved/`).
2. **Same issue already open?** Add a **+1** under **Votes** and a short entry under **Agent comments** on that file.
3. **New issue?** Create one timestamped file — see format below.

## When to write

This skill owns **moving the main clone's `spotlight` branch to a worktree
HEAD**, so write here for:

- A step failed — `git checkout spotlight` refused, `reset --hard` hit something unexpected, the SHA did not match after Step 5
- The main clone was dirty or on another branch and the skill's "stop and ask" left you without a safe option to offer
- The spotlight branch was already checked out elsewhere, or had commits of its own
- Tooling in the main clone (editor, dev server, build cache) reacted badly to the switch and the skill did not warn you
- Skip routine runs where the spotlight moved cleanly

## Not feedback

| Situation | Where |
|-----------|--------|
| Creating, bootstrapping, or committing in the worktree | `git-worktree/feedback/` |
| Cleaning up stale worktrees, branches, or a lagging `spotlight` | `git-branch-cleanup/feedback/` |
| What the user found while reviewing the spotlighted work | the task or review itself |

## Filename (new issues only)

`YYYY-MM-DDTHHMM-<short-slug>.md` — timestamp required; lowercase hyphens in slug.

## New issue — body

# YYYY-MM-DD — <id> · <role> · <machine>

## Context
Main clone and worktree state when you started.

## What happened
The step, what you expected, what happened, the workaround you used.

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
