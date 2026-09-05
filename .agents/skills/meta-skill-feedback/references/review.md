# Reviewing open skill feedback

Cody (or an agent **explicitly asked** to review feedback) sweeps open friction
files and decides skill edits.

## Find open notes

From a repo root or home skills tree:

```bash
find .agents/skills -path '*/feedback/*.md' ! -path '*/feedback/resolved/*' ! -name README.md 2>/dev/null
```

Or one skill:

```bash
ls path/to/skill/feedback/*.md 2>/dev/null | grep -v README
```

## Per-file loop

1. **Read** the friction file — context, what happened, suggestion, **vote count**.
2. **Brief** (if live Cody): job, friction, break vs inconvenience, vote weight, smallest fix, ask ship/defer/kill.
3. **Ship** — edit the target skill (real source-of-truth path per `install-skill`).
4. **Resolve** — move the note:

```bash
git mv feedback/2026-08-29T1130-example.md feedback/resolved/
```

Optional frontmatter at top after move:

```markdown
---
reviewed: 2026-08-29
---
```

5. **Commit** skill fix + resolved move together when possible.

## Do not

- Auto-apply skill edits on unattended scheduled runs (unless Cody's prompt says otherwise).
- Delete friction files — move to `resolved/` for history.
- Treat open feedback as approval to change behavior silently.

## Aggregating across skills

No central index required. Optional future: extend `skills_doctor.py` to list
open `feedback/*.md` counts per skill.
