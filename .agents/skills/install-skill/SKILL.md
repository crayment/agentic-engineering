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
Don't rely on that by accident -- pick one scope per skill, with a single
deliberate exception: a **vendored mirror** (see below), where the two copies
are kept byte-identical on purpose.

## Where to author

Two axes decide this:

- **Who needs it** -- only the repo you're in, or every repo (HOME scope)?
- **If every repo, is it public?** These two HOME-scope repos differ *only* by
  visibility:
  - `agentic-engineering` is a **public** repo. Author here only what you're
    happy to show off on your public GitHub profile.
  - `dotfiles` is a **private** repo. Author here anything you're still playing
    with, or that you don't want public (internal/company-specific tooling,
    secrets-adjacent workflows, half-baked experiments).

| Skill applies to... | Author the real files at |
|---|---|
| Only this one repo | `<project_root>/.agents/skills/<name>/` |
| Every repo, **public** (share-worthy on your GitHub) | `~/dev/me/agentic-engineering/.agents/skills/<name>/` |
| Every repo, **private** (WIP, or not for public eyes) | `~/dev/me/dotfiles/agents/skills/<name>/` |

When in doubt between the two HOME repos, prefer `dotfiles` -- it's easy to
promote a proven skill from private dotfiles to public agentic-engineering
later, but you can't un-publish something git history has already exposed.

## A skill in two places: the vendored mirror (personal + team)

Sometimes one skill genuinely needs two homes: it's generic enough to want on
all your machines (so it lives in `agentic-engineering`, HOME scope) *and* a
project's team needs it committed inside their repo (e.g. a browser-automation
skill you keep personally but also ship to a work project).

A symlink can't do this: a cross-repo symlink (the project copy pointing at your
`agentic-engineering` copy) dangles for teammates, who clone the project but
don't have your repo. So the files must physically exist in both places -- a
real copy, not a link. Manage it like a vendored dependency:

- **Canonical = the HOME copy** (`agentic-engineering`, public). This is the
  ONLY copy you edit. Canonical must be the public repo, not private `dotfiles`
  -- a skill going into a team's repo isn't really private.
- **Mirror = the PROJECT copy** (committed so the team gets it). Treat it as
  generated -- never hand-edit it; re-sync it from canonical:

```bash
rsync -a --delete \
  ~/dev/me/agentic-engineering/.agents/skills/<name>/ \
  <project_root>/.agents/skills/<name>/
```

**Before editing any skill that also lives in a project, find out whether it's a
mirror -- run the doctor.** Mirrors are *declared* in the git-ignored
`skills_doctor.config.json` next to the script, under
`"mirrors": {"<skill>": ["<project_root>", ...]}` (canonical is always the
HOME/`agentic-engineering` copy). `skills_doctor.py` reads that and, from
anywhere, prints a **MIRRORS** section listing each mirror, its canonical home,
and its live sync status -- with the exact `rsync` resync line on drift. So the
edit rule is simple: **if the doctor lists a skill under MIRRORS, edit the
canonical (`agentic-engineering`) copy and resync -- never edit the project
copy.**

- **Set up a new mirror:** author canonical in `agentic-engineering` and link it
  onto the machine (per Steps below), `rsync` a copy into the project, then add
  the skill to `"mirrors"` in your local `skills_doctor.config.json`.
- **Optional enforcement:** a `repo: local` pre-commit hook in the project can
  block committing a drifted mirror; guard it to no-op when the canonical repo
  isn't present so it never breaks a teammate's commit.

Which skills are mirrors lives *only* in your private `skills_doctor.config.json`
-- never in this doc or the script, which are public and describe the mechanism,
not your projects.

## Steps

1. Write `SKILL.md` (+ any supporting files) in the real location from the
   table above.
2. Link it into the harness skill dirs so it loads. A `.claude/skills/<name>`
   entry is always a **symlink to the nearest `.agents/skills/<name>`**, and a
   harness may read either dir -- so a HOME-scope skill has to be reachable from
   both `~/.agents/skills` and `~/.claude/skills`.
   - **Same repo (relative):** a project or dotfiles-native skill, where
     `.claude` and `.agents` share a tree:
     `ln -s ../../.agents/skills/<name> .claude/skills/<name>`.
   - **HOME-scope agentic-engineering skill -- two links, and commit one:** its
     real files live in another repo, and `~/.agents` -> `dotfiles/agents`, so
     `~/.agents/skills` is itself a harness dir *inside your dotfiles repo*.
     Create **both** as absolute symlinks to the agentic-engineering copy:
     - `~/dev/me/dotfiles/agents/skills/<name>` (this is `~/.agents/skills/<name>`)
       -- **commit it in dotfiles**. An untracked link won't survive a
       `git clean` and won't reach your other machine.
     - `~/.claude/skills/<name>`.
     `skills_doctor.py` checks for both; a missing `~/.agents` link shows as
     `claude only -- no .agents source`.
   - Do it **individually per skill** -- never a bulk "collection pointer"
     (`.agents/skills/some-bundle -> other-repo/skills/`), which `.claude` won't
     see and `skills_doctor.py` flags as a warning.
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
