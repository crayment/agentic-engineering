# Skill feedback (runtime friction)

After applying software-principles, if something **non-routine** misled you,
leave feedback here. Do not edit the skill.

Follows the [meta-skill-feedback](https://github.com/crayment/meta-skill-feedback)
convention (`feedback/*.md` open queue, `feedback/resolved/` after review).

**Public repo:** notes are committed and visible. Keep them generic — no company
or customer names, private code, internal hostnames, or tokens. Sketch the
design choice in a few invented lines if you need to. Use a generic machine
label (`local`, `ci-runner`) in the heading, or omit it.

## Before you write

1. Skim open `feedback/*.md` (not README, not `resolved/`).
2. **Same issue already open?** Add a **+1** under **Votes** and a short entry under **Agent comments** on that file.
3. **New issue?** Create one timestamped file — see format below.

## When to write

This skill owns **the design principles and their stated exceptions**, so write
here for:

- Two principles pulled opposite ways on a real decision (DRY vs compose-with-values, crash vs log) and the skill gave no tiebreak
- A principle conflicted with a repo's established convention and the skill was silent on which wins
- An exception ("when inheritance is fine", "when registries are fine") was missing a case you hit
- "When it is good to crash" or the testing guidance was too vague to act on
- Skip routine runs where the principles simply applied

## Not feedback

| Situation | Where |
|-----------|--------|
| Prose in docs or comments | `elements-of-style/feedback/` |
| Commit message wording | `git-commit-messages/feedback/` |
| Raising a design concern on someone's PR | `github-pr-review/feedback/` if that skill misled you |
| The design decision itself | the task output or PR |

## Filename (new issues only)

`YYYY-MM-DDTHHMM-<short-slug>.md` — timestamp required; lowercase hyphens in slug.

## New issue — body

# YYYY-MM-DD — <id> · <role> · <machine>

## Context
The kind of design decision you were making.

## What happened
Which principle, what it pointed to, and why that was wrong or unclear.

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

- One topic per file · duplicates are +1 votes, not new files · no secrets or private code · reviewer moves handled notes to `resolved/`
