# Skill feedback (runtime friction)

After posting a threaded reply with github-reply, if something **non-routine**
misled you, leave feedback here. Do not edit the skill.

Follows the [meta-skill-feedback](https://github.com/crayment/meta-skill-feedback)
convention (`feedback/*.md` open queue, `feedback/resolved/` after review).

**Public repo:** notes are committed and visible. Keep them generic — no company
or customer names, private repo names, PR or comment URLs, comment IDs, reviewer
usernames, reply text from private work, or tokens. Use placeholders like
`COMMENT_ID`. Use a generic machine label (`local`, `ci-runner`) in the heading,
or omit it.

## Before you write

1. Skim open `feedback/*.md` (not README, not `resolved/`).
2. **Same issue already open?** Add a **+1** under **Votes** and a short entry under **Agent comments** on that file.
3. **New issue?** Create one timestamped file — see format below.

## When to write

This skill owns **the `/replies` endpoint, reply-body quoting, and @mention
etiquette**, so write here for:

- The endpoint returned 404 or 422 — wrong id type (GraphQL node id vs numeric `databaseId`), a reply to a reply, a thread on an outdated diff
- `-f body="$(cat ...)"` still mangled the text, or `gh api` needed another flag
- The reply landed top-level, or the @mention did not notify when the skill said it would
- The reply URL could not be found or built for Reporting Back
- Skip routine replies that posted in-thread as written

## Not feedback

| Situation | Where |
|-----------|--------|
| Which feedback to address, or triage of review threads | `github-pr-feedback/feedback/` |
| Submitting a new review with inline comments | `github-pr-review/feedback/` |
| A bug in the `gh` CLI or the GitHub API | the `gh` issue tracker or GitHub support |
| The reply wording itself | the task output |

## Filename (new issues only)

`YYYY-MM-DDTHHMM-<short-slug>.md` — timestamp required; lowercase hyphens in slug.

## New issue — body

# YYYY-MM-DD — <id> · <role> · <machine>

## Context
The kind of thread you were replying to.

## What happened
The command, the response or status, what you expected, the workaround you used.

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
