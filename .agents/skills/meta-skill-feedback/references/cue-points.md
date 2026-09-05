# Cue points — where to patch target skills

Goal: agents **see** the feedback path without loading this meta-skill. Use **one
touchpoint** in the target skill — end of `SKILL.md`.

My Machines wake contracts are **out of scope** for this meta-skill. Patch
`references/wake.md` or `wake.sh` separately if Cody wants unattended runs to
see the feedback path.

## Required — end of SKILL.md

Add a **Before you finish** section (or fold into **Iron laws** if the skill
already has one). Keep to ~5 lines:

```markdown
## Before you finish

If anything misled you, failed oddly, or required discovery not covered here,
write **one file** in `feedback/` — see [feedback/README.md](feedback/README.md).
Do not edit this skill. Skip when the run was routine.
```

Extend existing **Iron laws** or **Final report** sections instead when that
fits the target skill better.

## Optional — second cue (rare)

Add **one** extra cue only where agents repeatedly get lost mid-workflow — and
only in `SKILL.md` or a domain reference file, not wake:

| Skill shape | Where |
|-------------|--------|
| Multi-phase workflow | After error recovery or auth failure section |
| External wiki paths | Next to the path table: "wiki wrong/missing → `feedback/`" |
| Long reference chains | Do **not** cue in every reference — end of SKILL.md is enough |

## Good moments to leave feedback

- Had to guess because the skill was silent
- Wrong path, flag, account, or command
- Same manual workaround as a prior run
- Near-miss (almost wrong action)
- Found the answer only by searching outside the skill

## Skip feedback

- Routine success, no surprises
- The output belongs in the task itself (proposals, summaries, audit rows)
- Pure user preference with no skill gap

## Legacy Obsidian queues

If a skill still has `agent-memories/skills-feedback/<name>.md`, **do not add a
second write path**. Prefer in-skill `feedback/` only; migrate open Obsidian
entries when Cody reviews.
