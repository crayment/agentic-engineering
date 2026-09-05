# Feedback convention

Standard layout for runtime friction on any skill:

```
skill-name/
├── SKILL.md
├── feedback/
│   ├── README.md
│   ├── YYYY-MM-DDTHHMM-short-slug.md    # open queue
│   └── resolved/
│       └── YYYY-MM-DDTHHMM-short-slug.md # after review
```

## Folders

| Path | Meaning |
|------|---------|
| `feedback/*.md` except `README.md` | **Open** — needs review |
| `feedback/resolved/` | **Done** — reviewed; skill may already be updated |
| `feedback/README.md` | Agent instructions (loaded on demand) |

State is the filesystem: **move file = change status**. No status enums in filenames.

Duplicate reports of the **same issue** are **+1 votes** on the existing open
file — extra signal for Cody, not inbox spam.

## Filename

```
YYYY-MM-DDTHHMM-<slug>.md
```

- **Timestamp required** — local time is fine; use the run's wall clock.
- **Slug** — lowercase, hyphens, ~3–6 words, agent's choice (human scan aid).
- **Collision** (same minute) — append `-2` or a short bc/id suffix.

Examples:

- `2026-08-29T1130-wrong-path-in-step-two.md`
- `2026-08-29T1130-actions-md-unicode-append-bc7b8f6.md`

## File body template (new issue)

```markdown
# YYYY-MM-DD — <id> · <role/title> · <machine>

## Context
One or two sentences: what you were trying to finish.

## What happened
Specific: wrong path, missing step, misleading instruction, workaround you used.

## Suggestion (optional)
Smallest change that would have prevented the friction. Do not edit the skill yourself.

## Votes

- **YYYY-MM-DDTHHMM** — <id> · opened

## Agent comments

_(none yet)_
```

Heading slots (omit unknowns, don't invent):

| Slot | Examples |
|------|----------|
| id | `bc-7b8f6238-…`, `local — Cursor` |
| role/title | `inbox-auto`, `link-dump drain` |
| machine | `birdhouse-mac-mini`, `Cody's MacBook Pro 2021` |

## Votes and agent comments (same issue again)

Before creating a file, **skim open notes** in `feedback/` (not README).

| Situation | Action |
|-----------|--------|
| Same issue already has an open file | Append to **Votes** and **Agent comments** on that file |
| New issue | Create a new timestamped file using the template above |
| Routine run, no friction | Write nothing |

**Vote line** (under `## Votes`):

```markdown
- **2026-09-05T1024** — bc-abc123 · +1
```

Use `· opened` on the first line only; later lines use `· +1`. Optional brief
note after `+1` on the same line.

**Agent comment** (under `## Agent comments`):

```markdown
### 2026-09-05T1024 — bc-abc123 · Cody's Mac
+1 — same wrong path; used workaround X.
```

Add new information when you have it (different workaround, new repro). Pure
+1 with no new facts is fine — duplicates are votes.

## feedback/README.md (starter content)

See [bootstrap.md](bootstrap.md) for a copy-paste starter. Agents read this when
writing a note. Keep it short:

- Skim open notes before writing; vote + comment instead of duplicating
- Write only after non-routine friction
- Filename rules above
- No secrets, tokens, passwords, full email bodies
- Do not edit the skill — leave notes here
- Resolved notes live in `resolved/` (Cody moves them)
- Optional: link a real example note from evals or a prior resolved file

## Not feedback

Route these elsewhere:

| Situation | Where |
|-----------|--------|
| Cody should approve a new inbox/mail rule | task audit log (e.g. `actions.md`) |
| Durable world fact | appropriate wiki page |
| Skill eval benchmark complaint | eval workspace `feedback.json` |
| Bug in application code | issue tracker / PR |
