#!/usr/bin/env python3
# ABOUTME: Scaffold feedback/ on an existing skill for meta-skill-feedback.
# ABOUTME: Creates README, resolved/, optional .gitkeep, optional SKILL.md patch.

from __future__ import annotations

import argparse
import sys
from pathlib import Path

FEEDBACK_README = """# Skill feedback (runtime friction)

Agents: write **one markdown file per non-routine surprise** after using this skill.

## When to write

- Something misled you, failed oddly, or required discovery not in this skill
- Skip routine successful runs

## Filename

`YYYY-MM-DDTHHMM-<short-slug>.md` (timestamp required; lowercase hyphens in slug)

If two notes land in the same minute, append `-2` or a short id suffix.

## Body

```markdown
# YYYY-MM-DD — <id> · <role/title> · <machine>

## Context
What you were trying to finish.

## What happened
Specific friction — paths, errors, workarounds.

## Suggestion (optional)
Smallest skill change that would help. Do not edit the skill yourself.
```

## Rules

- One topic per file
- No secrets, tokens, passwords, or sensitive customer data
- Do not edit this skill — leave notes here
- Cody moves handled notes to `resolved/`
"""

SKILL_PATCH = """
## Before you finish

If anything misled you, failed oddly, or required discovery not covered here,
write **one file** in `feedback/` — see [feedback/README.md](feedback/README.md).
Do not edit this skill. Skip when the run was routine.
"""

MARKER = "## Before you finish"


def scaffold(skill_dir: Path, patch_skill: bool) -> list[str]:
    actions: list[str] = []
    if not (skill_dir / "SKILL.md").is_file():
        raise SystemExit(f"ERROR: no SKILL.md in {skill_dir}")

    feedback = skill_dir / "feedback"
    resolved = feedback / "resolved"
    readme = feedback / "README.md"

    feedback.mkdir(exist_ok=True)
    resolved.mkdir(exist_ok=True)
    actions.append(f"mkdir {feedback.relative_to(skill_dir)}/")

    gitkeep = resolved / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.write_text("")
        actions.append(f"wrote {gitkeep.relative_to(skill_dir)}")

    if not readme.exists():
        readme.write_text(FEEDBACK_README)
        actions.append(f"wrote {readme.relative_to(skill_dir)}")
    else:
        actions.append(f"exists {readme.relative_to(skill_dir)} (unchanged)")

    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text()
    if patch_skill:
        if MARKER in text:
            actions.append("SKILL.md already has 'Before you finish' (unchanged)")
        else:
            skill_md.write_text(text.rstrip() + "\n" + SKILL_PATCH)
            actions.append("appended 'Before you finish' to SKILL.md")
    else:
        actions.append("SKILL.md not patched (pass --patch-skill to add cue block)")

    return actions


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scaffold feedback/ on an existing skill (meta-skill-feedback)."
    )
    parser.add_argument("skill_dir", type=Path, help="Path to skill directory")
    parser.add_argument(
        "--patch-skill",
        action="store_true",
        help="Append 'Before you finish' block to SKILL.md if missing",
    )
    args = parser.parse_args()
    skill_dir = args.skill_dir.resolve()
    if not skill_dir.is_dir():
        raise SystemExit(f"ERROR: not a directory: {skill_dir}")

    for line in scaffold(skill_dir, args.patch_skill):
        print(line)


if __name__ == "__main__":
    main()
