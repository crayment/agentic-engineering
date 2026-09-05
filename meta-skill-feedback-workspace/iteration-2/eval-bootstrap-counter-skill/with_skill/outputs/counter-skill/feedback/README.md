# Skill feedback (runtime friction)

After using this skill, if something **non-routine** misled you, leave feedback
here. Do not edit the skill.

## Before you write

1. Skim open `feedback/*.md` (not README).
2. **Same issue already open?** Add a **+1** under **Votes** and a short entry under **Agent comments** on that file.
3. **New issue?** Create one timestamped file — see format below.

## When to write

- Wrong/missing instruction, surprise failure, workaround you had to invent
- Skip routine successful runs

## Filename (new issues only)

`YYYY-MM-DDTHHMM-<short-slug>.md` — timestamp required; lowercase hyphens in slug.

## New issue — body

# YYYY-MM-DD — <id> · <role> · <machine>

## Context
What you were finishing.

## What happened
Specific friction.

## Suggestion (optional)
Smallest skill change that would help. Do not apply it yourself.

## Votes

- **YYYY-MM-DDTHHMM** — <id> · opened

## Agent comments

_(none yet)_

## Same issue again — append only

**Votes:** `- **YYYY-MM-DDTHHMM** — <id> · +1`

**Agent comments:** `### YYYY-MM-DDTHHMM — <id>` then one short paragraph.

## Example

See [evals/examples/sample-friction-note.md](../../../../evals/examples/sample-friction-note.md) for a representative friction note format.

## Rules

- One topic per file · duplicates are +1 votes, not new files · no secrets · Cody moves handled notes to `resolved/`
