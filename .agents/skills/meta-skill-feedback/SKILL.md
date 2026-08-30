---
name: meta-skill-feedback
description: >-
  Meta-skill: add a runtime friction-feedback inbox to an existing skill — feedback/
  folder, one timestamped markdown file per note, resolved/ archive, and progressive
  disclosure cues in SKILL.md. Use when bootstrapping skill feedback, retrofitting
  feedback folders, meta skill feedback, agent friction logs, or teaching agents
  where to leave notes after a skill run. Independent of eval harnesses and skill-creator.
license: Apache-2.0
---

# Meta skill feedback

Add a **runtime friction inbox** to an existing skill. Agents write one markdown
file per surprise; Cody reviews and edits the skill; resolved notes move to
`feedback/resolved/`.

This is **not** eval-harness feedback (JSON in a workspace). It is **not**
task output (rule proposals, audit logs). It is: *the skill misled me, I had to
discover something, or a near-miss happened.*

## When to use this skill

| Mode | Trigger |
|------|---------|
| **Bootstrap** | Cody asks to add feedback to a skill, or you're packaging a skill that lacks `feedback/` |
| **Runtime** | You finished a job using a skill that already has `feedback/README.md` — follow that README, not this file |

## Bootstrap workflow

1. Read [references/convention.md](references/convention.md) — naming, folders, body template.
2. Confirm the **target skill path** (real `.agents/skills/<name>/`, not a symlink leaf only).
3. Run the scaffold (preferred) or create dirs by hand:

```bash
python3 scripts/scaffold.py /path/to/skill-name [--patch-skill]
```

4. If the skill has a wake prompt or `references/wake.md`, add one line per
   [references/cue-points.md](references/cue-points.md).
5. Verify: `feedback/README.md` exists, `feedback/resolved/` exists, target
   `SKILL.md` has a **Before you finish** block (when `--patch-skill` used).
6. Tell Cody what was added. Do **not** write sample friction files unless this
   bootstrap run itself hit friction worth recording.

## Runtime (agents using a skill that already has feedback/)

At end of the primary workflow — **only if something was non-routine**:

1. Read `<skill>/feedback/README.md`.
2. Write **one new file** in `<skill>/feedback/` (not `resolved/`).
3. Do **not** edit the skill. Do **not** duplicate the same note in Obsidian
   `skills-feedback/` unless Cody still uses that legacy queue for this skill.

Skip when the run was routine and nothing misled you.

## Public vs private skills

This skill lives in public **agentic-engineering**. Friction files agents write
in **any** skill may be committed. Entries must stay **generic** — no company
names, secrets, tokens, or customer data. For skills that cannot tolerate public
friction history, gitignore `feedback/*.md` in that skill (keep `README.md` and
`resolved/.gitkeep` tracked) — document that in the skill's own README.

## Review (Cody)

See [references/review.md](references/review.md) — sweep open files, brief,
edit skill, `git mv` to `resolved/`.

## References

| File | Purpose |
|------|---------|
| [references/convention.md](references/convention.md) | Folder layout, filenames, file body |
| [references/cue-points.md](references/cue-points.md) | Where to patch target skills |
| [references/review.md](references/review.md) | Review and resolve workflow |
