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

## Filename

```
YYYY-MM-DDTHHMM-<slug>.md
```

- **Timestamp required** — local time is fine; use the run's wall clock.
- **Slug** — lowercase, hyphens, ~3–6 words, agent's choice (human scan aid).
- **Collision** (same minute) — append `-2` or a short bc/id suffix.

Examples:

- `2026-08-29T1130-no-feedback-pointer-in-wake.md`
- `2026-08-29T1130-actions-md-unicode-append-bc7b8f6.md`

## File body template

```markdown
# YYYY-MM-DD — <id> · <role/title> · <machine>

## Context
One or two sentences: what you were trying to finish.

## What happened
Specific: wrong path, missing step, misleading instruction, workaround you used.

## Suggestion (optional)
Smallest change that would have prevented the friction. Do not edit the skill yourself.
```

Heading slots (omit unknowns, don't invent):

| Slot | Examples |
|------|----------|
| id | `bc-7b8f6238-…`, `local — Cursor` |
| role/title | `inbox-auto`, `link-dump drain` |
| machine | `birdhouse-mac-mini`, `Cody's MacBook Pro 2021` |

## feedback/README.md (starter content)

See [bootstrap.md](bootstrap.md) for a copy-paste starter. Agents read this when
writing a note. Keep it short:

- One topic per file
- Write only after non-routine friction
- Filename rules above
- No secrets, tokens, passwords, full email bodies
- Do not edit the skill — leave notes here
- Resolved notes live in `resolved/` (Cody moves them)
- Skill-specific "not feedback" routes as needed

## Not feedback

Route these elsewhere:

| Situation | Where |
|-----------|--------|
| Cody should approve a new inbox/mail rule | task audit log (e.g. `actions.md`) |
| Durable world fact | appropriate wiki page |
| Skill eval benchmark complaint | eval workspace `feedback.json` |
| Bug in application code | issue tracker / PR |
