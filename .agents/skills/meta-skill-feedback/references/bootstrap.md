# Bootstrapping feedback on a target skill

You are wiring a **runtime friction inbox** onto an **existing target skill**.
Cody’s ask is usually explicit: use the **meta-skill-feedback** skill to add a
feedback system to `<target-skill>` (e.g. email-inbox-agent). Load meta-skill-feedback
first; do not bootstrap from memory alone.

Use judgment; adapt names, sections, and extra cues to that skill's shape.

## Minimum deliverables

| Artifact | Purpose |
|----------|---------|
| `feedback/resolved/` | Archive after Cody reviews (may stay empty) |
| `feedback/README.md` | Instructions for agents *using* this skill |
| Cue in target `SKILL.md` | So agents see the path before they finish |

Optional: one extra cue in `references/wake.md`, wake prompt string, or similar —
only if this skill has a clear "finish line" away from `SKILL.md`.

## feedback/README.md — starter template

Copy and adapt. Drop bullets that do not apply; add skill-specific "not feedback"
routes (audit logs, rule proposals, eval JSON, etc.).

```markdown
# Skill feedback (runtime friction)

After using this skill, if something **non-routine** misled you, write **one**
markdown file here. Do not edit the skill.

## When to write

- Wrong/missing instruction, surprise failure, workaround you had to invent
- Skip routine successful runs

## Filename

`YYYY-MM-DDTHHMM-<short-slug>.md` — timestamp required; lowercase hyphens in slug.

## Body

# YYYY-MM-DD — <id> · <role> · <machine>

## Context
What you were finishing.

## What happened
Specific friction.

## Suggestion (optional)
Smallest skill change that would help. Do not apply it yourself.

## Rules

- One topic per file · no secrets · Cody moves handled notes to `resolved/`
```

## Adapting to common skill shapes

| Shape | Typical extra work |
|-------|-------------------|
| **Scheduled wake** (My Machines) | One line in `references/wake.md` + wake prompt if embedded in `wake.sh` |
| **Wiki + skill** (external Obsidian rules) | In README: "wiki wrong → feedback; rule proposals → `<audit path>`" |
| **Interactive triage** | Cue in final-report / batch-complete section, not mid-workflow |
| **Public AE skill** | README note: entries must stay generic; optional gitignore for `feedback/*.md` |

## Iron laws vs new section

If the target skill already has **Iron laws** or a **Final report** checklist,
add feedback there instead of a redundant **Before you finish** — one pointer to
`feedback/README.md` is enough.

## Do not

- Run a one-size-fits-all script that blind-patches every skill the same way
- Add cues in every reference file
- Create friction files as part of bootstrap (unless you hit real friction)
- Replace task-specific outputs (proposals, Slack reports) with feedback files
