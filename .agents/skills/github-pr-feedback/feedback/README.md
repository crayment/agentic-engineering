# Skill feedback (runtime friction)

After a github-pr-feedback run, if something **non-routine** misled you, leave
feedback here. Do not edit the skill.

Follows the [meta-skill-feedback](https://github.com/crayment/meta-skill-feedback)
convention (`feedback/*.md` open queue, `feedback/resolved/` after review).

**Public repo:** notes are committed and visible. Keep them generic — no company
or customer names, private repo names, PR or comment URLs, reviewer usernames,
quoted review comments, agent links, or tokens. Describe the thread shape
("outdated thread with three replies"), not the conversation. Use a generic
machine label (`local`, `ci-runner`) in the heading, or omit it.

## Before you write

1. Skim open `feedback/*.md` (not README, not `resolved/`).
2. **Same issue already open?** Add a **+1** under **Votes** and a short entry under **Agent comments** on that file.
3. **New issue?** Create one timestamped file — see format below.

## When to write

This skill owns **fetching unresolved threads, grouping, the investigation
contract, triage, and serial execution**, so write here for:

- The Step 2 GraphQL query missed threads (more than 100 threads or comments, no pagination), returned the wrong ids, or the jq filter broke
- Grouping or the one-agent-per-track rule did not fit the feedback, and the skill gave no fallback
- `strengthened` / `weakened` / `invalidated` did not fit an item (e.g. valid but out of scope for this PR)
- The approval gate, the serial-only rule, or the branch-safety rules conflicted with the situation — stacked PRs, a force-pushed branch, a reviewer asking for a rebase
- Verifying that a reply was actually posted was harder than the skill implied
- Skip routine runs where the loop worked as written

## Not feedback

| Situation | Where |
|-----------|--------|
| `/replies` endpoint mechanics, `-f body=` quoting, @mentions | `github-reply/feedback/` — also say here if the copy in this skill needs the same fix |
| Running a review of someone else's PR | `github-pr-review/feedback/` |
| Failing CI checks on the PR | `github-ci-failure-diagnosis/feedback/` |
| Child-agent spawning, resuming, or agent links in the orchestration platform | that platform's issue tracker or your orchestration skill's inbox |
| Whether a reviewer is right, and the triage table itself | the task output shown to the user |

## Filename (new issues only)

`YYYY-MM-DDTHHMM-<short-slug>.md` — timestamp required; lowercase hyphens in slug.

## New issue — body

# YYYY-MM-DD — <id> · <role> · <machine>

## Context
The PR's feedback shape and which step you were on.

## What happened
The step, rule, or command, what you expected, what happened, the workaround you used.

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

- One topic per file · duplicates are +1 votes, not new files · no secrets or quoted review text · reviewer moves handled notes to `resolved/`
