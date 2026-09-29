# Skill feedback (runtime friction)

After generating release notes with git-release-notes-generation, if something
**non-routine** misled you, leave feedback here. Do not edit the skill.

Follows the [meta-skill-feedback](https://github.com/crayment/meta-skill-feedback)
convention (`feedback/*.md` open queue, `feedback/resolved/` after review).

**Public repo:** notes are committed and visible. Keep them generic — no company
or customer names, product or feature names from private work, internal
hostnames, or tokens. Describe the branch shape ("one feature plus two infra
commits"), not its contents. Use a generic machine label (`local`, `ci-runner`)
in the heading, or omit it.

## Before you write

1. Skim open `feedback/*.md` (not README, not `resolved/`).
2. **Same issue already open?** Add a **+1** under **Votes** and a short entry under **Agent comments** on that file.
3. **New issue?** Create one timestamped file — see format below.

## When to write

This skill owns **the git range, the template, and the grouping rules**, so
write here for:

- `main..HEAD` was the wrong range — default branch is not `main`, local `main` was stale, the branch is stacked on another
- The template did not fit — no user-facing change, a pure refactor, a breaking change or migration with nowhere to go
- The feature-vs-fix or "collapse into the parent feature" rules were ambiguous for this branch
- The PR-preparation hint conflicted with a repo's PR template
- Skip routine runs where the template and rules simply applied

## Not feedback

| Situation | Where |
|-----------|--------|
| Creating the PR with `gh` or quoting the body | `github-pull-request-creation/feedback/` |
| Commit subjects too vague to summarize | `git-commit-messages/feedback/` if its rules were followed and still failed |
| Prose quality of the notes | `elements-of-style/feedback/` |
| The release notes themselves | the task output |

## Filename (new issues only)

`YYYY-MM-DDTHHMM-<short-slug>.md` — timestamp required; lowercase hyphens in slug.

## New issue — body

# YYYY-MM-DD — <id> · <role> · <machine>

## Context
The branch shape and who the notes were for.

## What happened
The command or rule, what it produced, and what you did instead.

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
