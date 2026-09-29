# Skill feedback (runtime friction)

After a github-pr-review run, if something **non-routine** misled you, leave
feedback here. Do not edit the skill or its scripts.

Follows the [meta-skill-feedback](https://github.com/crayment/meta-skill-feedback)
convention (`feedback/*.md` open queue, `feedback/resolved/` after review).

**Public repo:** notes are committed and visible. Keep them generic — no company
or customer names, private repo names, PR URLs, author usernames, code or review
comments from the PR, agent links, or tokens. Describe the PR shape and the
failing step, not the findings. Use a generic machine label (`local`,
`ci-runner`) in the heading, or omit it.

## Before you write

1. Skim open `feedback/*.md` (not README, not `resolved/`).
2. **Same issue already open?** Add a **+1** under **Votes** and a short entry under **Agent comments** on that file.
3. **New issue?** Create one timestamped file — see format below.

## When to write

This skill owns **track splitting, cross-validation, the review artifact
layout, and batched submission through its bundled scripts**, so write here for:

- `batched-review.sh`, `submit-review.sh`, or `inline-comment.sh` failed — anchor text not found, line outside the diff, pending-review conflict, wrong event
- The `tmp/pr<N>_review/` layout or `NN-meta.yml` fields were unclear or not enough for the submission owner
- The "every located finding goes inline" rule collided with something GitHub would not accept
- A stale pending review in `/tmp` or on GitHub confused the one-submission-owner flow
- Track splitting or cross-validation guidance did not fit the PR (very small, very large, generated code)
- Skip routine reviews where the phases and scripts worked as written

## Not feedback

| Situation | Where |
|-----------|--------|
| Responding to feedback left on your own PR | `github-pr-feedback/feedback/` |
| Replying inside an existing thread | `github-reply/feedback/` |
| Failing CI checks on the PR | `github-ci-failure-diagnosis/feedback/` |
| Child-agent spawning, resuming, or agent links in the orchestration platform | that platform's issue tracker or your orchestration skill's inbox |
| The review findings and the submitted review | the review itself |

## Filename (new issues only)

`YYYY-MM-DDTHHMM-<short-slug>.md` — timestamp required; lowercase hyphens in slug.

## New issue — body

# YYYY-MM-DD — <id> · <role> · <machine>

## Context
The PR shape and which phase you were in.

## What happened
The phase, script, or rule, what you expected, what happened, the workaround you used.

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

- One topic per file · duplicates are +1 votes, not new files · no secrets or PR content · reviewer moves handled notes to `resolved/`
