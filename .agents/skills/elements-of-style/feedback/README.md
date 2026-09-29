# Skill feedback (runtime friction)

After applying elements-of-style, if something **non-routine** misled you, leave
feedback here. Do not edit the skill.

Follows the [meta-skill-feedback](https://github.com/crayment/meta-skill-feedback)
convention (`feedback/*.md` open queue, `feedback/resolved/` after review).

**Public repo:** notes are committed and visible. Keep them generic — no company
or customer names, internal hostnames, personal details, or tokens. Quote a short
invented sentence to show the problem, never the private text you were editing.
Use a generic machine label (`local`, `ci-runner`) in the heading, or omit it.

## Before you write

1. Skim open `feedback/*.md` (not README, not `resolved/`).
2. **Same issue already open?** Add a **+1** under **Votes** and a short entry under **Agent comments** on that file.
3. **New issue?** Create one timestamped file — see format below.

## When to write

This skill owns **prose rules and their examples**, so write here for:

- A rule gave worse prose in a real context — e.g. active voice or positive form fought a technical, legal, or UI-copy convention, with no hint which wins
- An example or wordy/concise pair is wrong, dated, or misleads
- The "creative efforts" deference was unclear: you could not tell whether a requested style overrode a rule
- The skill was silent on something common you had to decide yourself (lists, headings, bullet fragments, code-adjacent prose)
- Skip routine runs where the rules simply applied

## Not feedback

| Situation | Where |
|-----------|--------|
| Tone, candor, directness, or length of a reply | `pithy-communication/feedback/` |
| Commit subject wording | `git-commit-messages/feedback/` |
| Release notes or PR body structure | `git-release-notes-generation/feedback/` |
| The text you were writing or editing | the task output itself |
| A reader just prefers a different style, with no gap in the skill | nowhere — follow the requested style |

## Filename (new issues only)

`YYYY-MM-DDTHHMM-<short-slug>.md` — timestamp required; lowercase hyphens in slug.

## New issue — body

# YYYY-MM-DD — <id> · <role> · <machine>

## Context
What you were writing or editing (genre, audience), in one or two sentences.

## What happened
The rule or example, what it pushed you toward, and why that was worse.

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

- One topic per file · duplicates are +1 votes, not new files · no secrets or private text · reviewer moves handled notes to `resolved/`
