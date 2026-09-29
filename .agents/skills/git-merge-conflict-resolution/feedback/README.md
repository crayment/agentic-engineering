# Skill feedback (runtime friction)

After resolving conflicts with git-merge-conflict-resolution, if something
**non-routine** misled you, leave feedback here. Do not edit the skill.

Follows the [meta-skill-feedback](https://github.com/crayment/meta-skill-feedback)
convention (`feedback/*.md` open queue, `feedback/resolved/` after review).

**Public repo:** notes are committed and visible. Keep them generic — no company
or customer names, internal hostnames, real file paths or code from private
repos, or tokens. Describe the git state (merge, rebase, cherry-pick, worktree),
not the codebase. Use a generic machine label (`local`, `ci-runner`) in the
heading, or omit it.

## Before you write

1. Skim open `feedback/*.md` (not README, not `resolved/`).
2. **Same issue already open?** Add a **+1** under **Votes** and a short entry under **Agent comments** on that file.
3. **New issue?** Create one timestamped file — see format below.

## When to write

This skill owns **the merge-base-first workflow and the ours/theirs rules**, so
write here for:

- A command failed or pointed at the wrong ref — e.g. `MERGE_HEAD`/`REBASE_HEAD` absent, a cherry-pick or revert conflict, a stash pop conflict
- The `.git/MERGE_HEAD` state checks gave the wrong answer (in a worktree `.git` is a file, not a directory)
- `--ours`/`--theirs` did the opposite of what the skill said for your situation
- The "mark as resolved" step was wrong for the operation you were in
- A conflict type the workflow does not cover — delete/modify, rename, binary, submodule
- Skip routine resolutions where the workflow simply applied

## Not feedback

| Situation | Where |
|-----------|--------|
| Which side is semantically correct for the code | ask the user or the other change's author |
| Setting up or working in a worktree | `git-worktree/feedback/` |
| Wording the merge commit message | `git-commit-messages/feedback/` |
| Conflicts caused by addressing PR review feedback | `github-pr-feedback/feedback/` only if that skill's steps misled you |

## Filename (new issues only)

`YYYY-MM-DDTHHMM-<short-slug>.md` — timestamp required; lowercase hyphens in slug.

## New issue — body

# YYYY-MM-DD — <id> · <role> · <machine>

## Context
The git operation in progress and the conflict type.

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
