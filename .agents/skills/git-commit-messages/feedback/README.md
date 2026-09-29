# Skill feedback (runtime friction)

After writing a commit message with git-commit-messages, if something
**non-routine** misled you, leave feedback here. Do not edit the skill.

Follows the [meta-skill-feedback](https://github.com/crayment/meta-skill-feedback)
convention (`feedback/*.md` open queue, `feedback/resolved/` after review).

**Public repo:** notes are committed and visible. Keep them generic — no company
or customer names, internal hostnames, ticket IDs, real commit subjects from
private repos, or tokens. Invent a stand-in subject to show the problem. Use a
generic machine label (`local`, `ci-runner`) in the heading, or omit it.

## Before you write

1. Skim open `feedback/*.md` (not README, not `resolved/`).
2. **Same issue already open?** Add a **+1** under **Votes** and a short entry under **Agent comments** on that file.
3. **New issue?** Create one timestamped file — see format below.

## When to write

This skill owns **the subject-first format**, so write here for:

- The repo required another format (Conventional Commits, ticket prefix, hook-enforced pattern) and the skill gave no hint which wins
- "Start with the changed subject" did not fit — a change spanning several components, a revert, a merge, a dependency bump
- The skill was silent on the body, line length, or trailers and you had to guess
- An example misled you
- Skip routine commits where the format simply applied

## Not feedback

| Situation | Where |
|-----------|--------|
| General prose quality of the body | `elements-of-style/feedback/` |
| PR title or description | `github-pull-request-creation/feedback/` |
| Release notes built from commit history | `git-release-notes-generation/feedback/` |
| A commit hook rejected the message for a repo-specific rule | follow the repo; note here only if the skill should have warned you |

## Filename (new issues only)

`YYYY-MM-DDTHHMM-<short-slug>.md` — timestamp required; lowercase hyphens in slug.

## New issue — body

# YYYY-MM-DD — <id> · <role> · <machine>

## Context
What kind of change you were committing.

## What happened
The rule, what it produced, and why that subject was worse or ambiguous.

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
