---
name: install-skill
description: Link a newly authored, copied, or `npx skills add`-installed skill into the correct .agents/.claude locations on this machine, following the source-of-truth + symlink convention, then verify with skills_doctor.py. Use when creating a new skill, installing a skill, moving a skill between locations, or setting up skills in a new project repo -- anywhere on this machine or in any project.
---

# Installing a skill

This is about **where a skill's files physically live** and how they're linked
-- not what to write in `SKILL.md`. For content/structure/frontmatter, use
`create-skill` instead; use this skill after you've drafted the content, or
whenever you're placing/moving a skill that already exists.

## The model

Every place skills can live is a **scope**: the current project (nearest
`.git` root) and `~` (home). Within a scope:

- `.agents/skills/<name>/` is the **source of truth** -- the real files live
  here, git-tracked wherever this scope's repo is.
- `.claude/skills/<name>` **must be a symlink** pointing at the `.agents`
  copy. Never write skill content directly under `.claude/skills` (or
  `.cursor/skills`) -- those are link-only, never originals.

Directories can't be hardlinked (OS limitation on macOS/Linux) -- always use a
directory symlink, never a copy.

If the same skill name exists in both PROJECT and HOME scope, PROJECT wins
for anything run from inside that repo; the HOME copy is silently shadowed.
Don't rely on that -- pick one scope per skill.

## Where to author

| Skill applies to... | Author the real files at |
|---|---|
| Only this one repo | `<project_root>/.agents/skills/<name>/` |
| Every repo, and you'd share it publicly | `~/dev/me/agentic-engineering/.agents/skills/<name>/` |
| Every repo, more personal/private | `~/dev/me/dotfiles/agents/skills/<name>/` |

## Steps

1. Write `SKILL.md` (+ any supporting files) in the real location from the
   table above.
2. Symlink it into every `.claude/skills/` that needs to see it:
   - Same repo as the source: use a **relative** symlink, matching existing
     siblings, e.g. `ln -s ../../.agents/skills/<name> .claude/skills/<name>`.
   - Cross-repo (e.g. an agentic-engineering-authored skill needs to show up
     at `~/.claude/skills/<name>`): use an **absolute** symlink straight to
     the source, e.g.
     `ln -s ~/dev/me/agentic-engineering/.agents/skills/<name> ~/.claude/skills/<name>`.
   - Do this **individually per skill**. Never symlink a whole folder of
     skills at once as a bulk "collection pointer" (e.g.
     `.agents/skills/some-bundle -> other-repo/skills/`) -- it's invisible to
     `.claude/skills` unless something is also individually linked there, and
     `skills_doctor.py` (below) flags it as a warning.
3. Verify: `python3 ~/dev/me/agentic-engineering/scripts/skills_doctor.py [project_path]`.
   The new skill should show `\u2713 agents+claude` with no warning. Fix anything
   that shows `\u26a0`/`\u2717` before considering the install done.
4. If the skill's origin came from anywhere `npx skills add` wouldn't
   naturally record (hand-copied from a repo's docs, extracted from a CLI
   tool's generated help, pasted from a coworker, etc.), add an entry so the
   next person/agent doesn't have to re-trace it by hand:
   - Global: `~/dev/me/dotfiles/agents/.skill-notes.json`
   - Project: `<project_root>/skills-notes.json`
   - Schema: `{"<name>": {"source": "...", "url": "...", "note": "...", "recorded_at": "YYYY-MM-DD"}}`
   - `skills_doctor.py` surfaces this as `<- noted: ...` next to the skill.

## About `npx skills add`

It writes a real lockfile recording provenance (`.skill-lock.json` globally
at `dotfiles/agents/`, `skills-lock.json` at a project root) --
`skills_doctor.py` reads this automatically and shows `<- npx: <source>`.
Prefer it over hand-copying when the skill you want already exists on GitHub.
Still run `skills_doctor.py` afterward to confirm it landed in `.agents` with
a correct `.claude` symlink rather than as a bare `.claude`-only copy.

## Reference

`skills_doctor.py`'s own docstring is the up-to-date spec for what counts as
correctly linked vs. a warning -- read it if something here seems stale.
