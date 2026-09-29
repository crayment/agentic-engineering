# Skill feedback (runtime friction)

After opening a PR with github-pull-request-creation, if something
**non-routine** misled you, leave feedback here. Do not edit the skill.

Follows the [meta-skill-feedback](https://github.com/crayment/meta-skill-feedback)
convention (`feedback/*.md` open queue, `feedback/resolved/` after review).

**Public repo:** notes are committed and visible. Keep them generic — no company
or customer names, private repo names, PR URLs, reviewer usernames, PR body text
from private work, or tokens. Invent a stand-in body to show a quoting problem.
Use a generic machine label (`local`, `ci-runner`) in the heading, or omit it.

## Before you write

1. Skim open `feedback/*.md` (not README, not `resolved/`).
2. **Same issue already open?** Add a **+1** under **Votes** and a short entry under **Agent comments** on that file.
3. **New issue?** Create one timestamped file — see format below.

## When to write

This skill owns **`gh pr create` usage and safe multi-line bodies**, so write
here for:

- The write-to-file-then-`--body "$(cat ...)"` pattern still mangled the body — a shell, a harness sandbox, or a character it did not survive
- `--body-file` or another flag would have been simpler and the skill did not mention it
- The repo's `.github/pull_request_template.md` was ignored or overwritten and the skill gave no hint
- `gh pr create` prompted interactively, picked the wrong base or head, or failed on a fork, and the skill did not cover it
- Skip routine PRs that opened cleanly

## Not feedback

| Situation | Where |
|-----------|--------|
| What goes in the PR body | `git-release-notes-generation/feedback/` |
| CI failing after the PR opened | `github-ci-failure-diagnosis/feedback/` |
| Review comments on the PR | `github-pr-feedback/feedback/` |
| A bug in the `gh` CLI | the `gh` issue tracker |

## Filename (new issues only)

`YYYY-MM-DDTHHMM-<short-slug>.md` — timestamp required; lowercase hyphens in slug.

## New issue — body

# YYYY-MM-DD — <id> · <role> · <machine>

## Context
The shell or harness and the kind of PR you were opening.

## What happened
The command, what you expected, what happened, the workaround you used.

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
