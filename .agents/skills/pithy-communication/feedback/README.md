# Skill feedback (runtime friction)

After communicating under pithy-communication, if something **non-routine**
misled you, leave feedback here. Do not edit the skill.

Follows the [meta-skill-feedback](https://github.com/crayment/meta-skill-feedback)
convention (`feedback/*.md` open queue, `feedback/resolved/` after review).

**Public repo:** notes are committed and visible. Keep them generic — no company
or customer names, personal details, internal hostnames, quotes from private
conversations, or tokens. Paraphrase the exchange. Use a generic machine label
(`local`, `ci-runner`) in the heading, or omit it.

## Before you write

1. Skim open `feedback/*.md` (not README, not `resolved/`).
2. **Same issue already open?** Add a **+1** under **Votes** and a short entry under **Agent comments** on that file.
3. **New issue?** Create one timestamped file — see format below.

## When to write

This skill owns **voice: signal-to-noise, candor, and when to ask a clarifying
question**, so write here for:

- The directive conflicted with a harness, repo, or user style rule and gave no hint which wins
- Pithiness cost clarity — a reader had to ask what you meant, or you dropped a caveat that mattered
- "Ask a clarifying question" did not fit an unattended or delegated run with nobody to answer
- An example or "what kills pithiness" item pushed you the wrong way
- Skip routine runs where the voice simply applied

## Not feedback

| Situation | Where |
|-----------|--------|
| Sentence-level prose rules (active voice, needless words) | `elements-of-style/feedback/` |
| Framing a research subagent | `recruit-junior/feedback/` |
| A user just wants a different tone, with no gap in the skill | nowhere — follow the user |
| The reply itself | the conversation |

## Filename (new issues only)

`YYYY-MM-DDTHHMM-<short-slug>.md` — timestamp required; lowercase hyphens in slug.

## New issue — body

# YYYY-MM-DD — <id> · <role> · <machine>

## Context
Who you were writing for and what kind of reply it was.

## What happened
The directive, what it pushed you toward, and what went wrong.

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

- One topic per file · duplicates are +1 votes, not new files · no secrets or private quotes · reviewer moves handled notes to `resolved/`
