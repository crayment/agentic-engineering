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

Add a **runtime friction inbox** to an existing skill. Agents leave notes after
surprises — new issues get a file; repeat issues get **+1 votes** on the open
file. Cody reviews and edits the skill; resolved notes move to `feedback/resolved/`.

This is **not** eval-harness feedback (JSON in a workspace). It is **not**
task output (rule proposals, audit logs). It is: *the skill misled me, I had to
discover something, or a near-miss happened.*

## When to use this skill

| Mode | Trigger |
|------|---------|
| **Bootstrap** | Cody asks an agent to use **meta-skill-feedback** to add a feedback system to a target skill, or you're packaging a skill that lacks `feedback/` |
| **Runtime** | You finished a job using a skill that already has `feedback/README.md` — follow that README, not this file |

## Bootstrap workflow

Cody’s typical ask: *“Use **meta-skill-feedback** to add a feedback system to &lt;target-skill&gt;.”* Load this skill first, then work on the target skill’s tree.

Read the target skill first. Adapt layout and cues to **how that skill actually
works** — interactive triage, one-shot CLI, wiki-backed rules, etc. The convention
is fixed; the wiring is not. **My Machines wake contracts** (`wake.md`, `wake.sh`)
are a separate system — do not create or patch them from this skill.

1. Read [references/convention.md](references/convention.md) and
   [references/bootstrap.md](references/bootstrap.md).
2. Resolve the **real source path** (`install-skill` — edit the canonical
   `.agents/skills/<name>/`, not a harness symlink only).
3. **Create the inbox** under the target skill:
   - `feedback/resolved/` (empty archive folder)
   - `feedback/README.md` — agent-facing instructions; start from the template in
     bootstrap.md and trim or extend for this skill (e.g. Obsidian paths or task
     outputs that are *not* feedback)
4. **Cue future agents** — one touchpoint in `SKILL.md`; see
   [references/cue-points.md](references/cue-points.md):
   - Required: **Before you finish** (or equivalent) near the end of `SKILL.md`
   Match the target skill's voice and section names; do not paste boilerplate
   blindly if Iron laws or a final-report step already exists — extend those.
5. **Verify** by reading back: an agent finishing a routine run knows to skip;
   an agent hitting repeat friction knows to vote +1 on an open note.
6. Summarize for Cody what you added and where. Do **not** seed example friction
   files unless this bootstrap run itself hit friction worth recording.

Use normal file tools (`mkdir`, write, search/replace). No scaffold script.

## Runtime (agents using a skill that already has feedback/)

See **[references/runtime.md](references/runtime.md)** — decision tree, vote/+1
format, and examples. Load `<skill>/feedback/README.md` when executing.

## Public vs private skills

This skill lives in public **agentic-engineering**. Friction files agents write
in **any** skill may be committed. Entries must stay **generic** — no company
names, secrets, tokens, or customer data. For skills that cannot tolerate public
friction history, gitignore `feedback/*.md` in that skill (keep `feedback/README.md`
tracked) — document that in the skill's own README.

## Review (Cody)

See [references/review.md](references/review.md) — sweep open files, brief,
edit skill, move notes to `resolved/`.

## References

| File | Purpose |
|------|---------|
| [references/convention.md](references/convention.md) | Folder layout, filenames, note body |
| [references/bootstrap.md](references/bootstrap.md) | What to create, README starter, adaptation |
| [references/runtime.md](references/runtime.md) | Runtime decision tree, votes, new vs +1 |
| [references/cue-points.md](references/cue-points.md) | Where to patch target skills |
| [references/review.md](references/review.md) | Review and resolve workflow |
| [references/evals.md](references/evals.md) | PAC eval harness (v0 fixtures) |

Human overview (phone-friendly): [evals/overview.html](evals/overview.html)
