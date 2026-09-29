# Skill feedback (runtime friction)

After diagnosing CI with github-ci-failure-diagnosis, if something
**non-routine** misled you, leave feedback here. Do not edit the skill.

Follows the [meta-skill-feedback](https://github.com/crayment/meta-skill-feedback)
convention (`feedback/*.md` open queue, `feedback/resolved/` after review).

**Public repo:** notes are committed and visible. Keep them generic — no company
or customer names, private repo names, run IDs or URLs, internal hostnames, log
excerpts from private builds, or tokens. Describe the check type (GitHub Actions,
external status, required check), not the project. Use a generic machine label
(`local`, `ci-runner`) in the heading, or omit it.

## Before you write

1. Skim open `feedback/*.md` (not README, not `resolved/`).
2. **Same issue already open?** Add a **+1** under **Votes** and a short entry under **Agent comments** on that file.
3. **New issue?** Create one timestamped file — see format below.

## When to write

This skill owns **the three `gh` steps and the report shape**, so write here for:

- A `gh pr checks`, `gh pr view --json statusCheckRollup`, or `gh run view --log` call behaved differently than documented — exit code, missing fields, output too large
- A failed check had no workflow run ID (external status, third-party app) and the skill gave no path forward
- A better flag existed and you only found it outside the skill
- Logs pointed at a matrix job, reusable workflow, or rerun and the skill's "first meaningful error" advice misled you
- Skip routine diagnoses where the three steps simply worked

## Not feedback

| Situation | Where |
|-----------|--------|
| The CI failure itself | the diagnosis you report back |
| A bug in the `gh` CLI | the `gh` issue tracker |
| Opening or updating the PR | `github-pull-request-creation/feedback/` |
| Reviewer comments on the PR | `github-pr-feedback/feedback/` |

## Filename (new issues only)

`YYYY-MM-DDTHHMM-<short-slug>.md` — timestamp required; lowercase hyphens in slug.

## New issue — body

# YYYY-MM-DD — <id> · <role> · <machine>

## Context
The kind of check that failed and what you were trying to learn.

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

- One topic per file · duplicates are +1 votes, not new files · no secrets or private logs · reviewer moves handled notes to `resolved/`
