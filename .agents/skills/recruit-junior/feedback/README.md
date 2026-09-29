# Skill feedback (runtime friction)

After framing an agent with recruit-junior, if something **non-routine** misled
you, leave feedback here. Do not edit the skill.

Follows the [meta-skill-feedback](https://github.com/crayment/meta-skill-feedback)
convention (`feedback/*.md` open queue, `feedback/resolved/` after review).

**Public repo:** notes are committed and visible. Keep them generic — no company
or customer names, private research topics, internal hostnames, agent links, or
tokens. Name the kind of research ("a fast-moving SDK"), not the subject. Use a
generic machine label (`local`, `ci-runner`) in the heading, or omit it.

## Before you write

1. Skim open `feedback/*.md` (not README, not `resolved/`).
2. **Same issue already open?** Add a **+1** under **Votes** and a short entry under **Agent comments** on that file.
3. **New issue?** Create one timestamped file — see format below.

## When to write

This skill owns **the junior framing and its example prompt**, so write here for:

- The framed agent still skipped tool use or cited nothing, even with the prompt as written
- Hedging got bad enough to bury the findings, and the "What to Watch For" follow-ups did not fix it
- The example prompt was missing something you had to add every time (scope, deadline, report shape)
- The agent could not load `pithy-communication` or `elements-of-style` in its harness and the skill gave no fallback
- The when-to-use line was unclear for a mixed research-and-implement task
- Skip routine runs where the framing worked

## Not feedback

| Situation | Where |
|-----------|--------|
| Voice of the final report | `pithy-communication/feedback/` |
| Prose quality of the final report | `elements-of-style/feedback/` |
| Spawning, resuming, or tooling of the subagent | your harness's orchestration skill or issue tracker |
| The research findings | the task output |

## Filename (new issues only)

`YYYY-MM-DDTHHMM-<short-slug>.md` — timestamp required; lowercase hyphens in slug.

## New issue — body

# YYYY-MM-DD — <id> · <role> · <machine>

## Context
The kind of research and how you framed the agent.

## What happened
What the agent did, what you expected, and the follow-up you had to add.

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
