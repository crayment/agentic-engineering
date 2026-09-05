#!/usr/bin/env python3
# ABOUTME: Deterministic eval checks for meta-skill-feedback bootstrap/quiet runs.
# ABOUTME: Used by PAC grader workers; prints JSON for evidence citation.

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TIMESTAMP_NOTE = re.compile(
    r"feedback/(\d{4}-\d{2}-\d{2}T\d{4}-.+\.md)$"
)


def _exists(path: Path) -> bool:
    return path.exists()


def _dir_exists(path: Path) -> bool:
    return path.is_dir()


def _read(path: Path) -> str:
    return path.read_text() if path.is_file() else ""


def _skill_cues_feedback(skill_text: str) -> bool:
    lower = skill_text.lower()
    return (
        "feedback/readme" in lower
        or "`feedback/`" in lower
        or "feedback/" in lower and "before you finish" in lower
        or "before you finish" in lower
    )


def feedback_notes(feedback_dir: Path) -> list[Path]:
    if not feedback_dir.is_dir():
        return []
    return [
        p
        for p in feedback_dir.glob("*.md")
        if p.name != "README.md"
    ]


def check_bootstrap_minimal(outputs: Path) -> list[dict]:
    target = outputs / "minimal-skill"
    fb = target / "feedback"
    skill = target / "SKILL.md"
    checks = [
        ("outputs/minimal-skill/feedback/README.md exists", _exists(fb / "README.md")),
        (
            "outputs/minimal-skill/feedback/resolved/ exists as a directory",
            _dir_exists(fb / "resolved"),
        ),
        (
            "outputs/minimal-skill/SKILL.md references feedback/ or feedback/README.md",
            _skill_cues_feedback(_read(skill)),
        ),
        (
            "No new friction note files in outputs/minimal-skill/feedback/ except README.md",
            len(feedback_notes(fb)) == 0,
        ),
        (
            "No scripts/scaffold.py was created under outputs/minimal-skill/",
            not _exists(target / "scripts" / "scaffold.py"),
        ),
    ]
    return [{"text": t, "passed": p} for t, p in checks]


def check_runtime_quiet(outputs: Path, fixture_root: Path) -> list[dict]:
    target = outputs / "minimal-bootstrapped"
    fb = target / "feedback"
    fixture_skill = fixture_root / "minimal-bootstrapped" / "SKILL.md"
    out_skill = target / "SKILL.md"
    notes = feedback_notes(fb)
    ts_notes = [p for p in notes if TIMESTAMP_NOTE.search(str(p.relative_to(target)))]
    skill_unchanged = (
        _exists(fixture_skill)
        and _exists(out_skill)
        and _read(fixture_skill) == _read(out_skill)
    )
    checks = [
        (
            "No new files matching outputs/minimal-bootstrapped/feedback/YYYY-MM-DDTHHMM-*.md",
            len(ts_notes) == 0,
        ),
        (
            "outputs/minimal-bootstrapped/SKILL.md was not modified from the fixture copy",
            skill_unchanged,
        ),
        (
            "Only feedback/README.md exists under feedback/ (no extra .md notes)",
            len(notes) == 0,
        ),
    ]
    return [{"text": t, "passed": p} for t, p in checks]


def check_runtime_friction(outputs: Path, fixture_root: Path) -> list[dict]:
    target = outputs / "trap-skill"
    fb = target / "feedback"
    fixture_skill = fixture_root / "trap-skill" / "SKILL.md"
    out_skill = target / "SKILL.md"
    notes = feedback_notes(fb)
    ts_notes = [p for p in notes if TIMESTAMP_NOTE.search(str(p.relative_to(target)))]
    note_text = "\n".join(_read(p) for p in ts_notes).lower()
    path_mentioned = any(
        s in note_text
        for s in ("data/project", "inputs/project", "wrong path", "misleading")
    )
    has_what_happened = "what happened" in note_text
    skill_unchanged = (
        _exists(fixture_skill)
        and _exists(out_skill)
        and _read(fixture_skill) == _read(out_skill)
    )
    checks = [
        (
            "Exactly one new friction note matching outputs/trap-skill/feedback/YYYY-MM-DDTHHMM-*.md",
            len(ts_notes) == 1,
        ),
        (
            "Friction note mentions the wrong or correct path (data/project or inputs/project)",
            path_mentioned,
        ),
        (
            "Friction note has a What happened section",
            has_what_happened,
        ),
        (
            "outputs/trap-skill/SKILL.md was not modified from the fixture copy",
            skill_unchanged,
        ),
    ]
    return [{"text": t, "passed": p} for t, p in checks]


CHECKERS = {
    "bootstrap-minimal": check_bootstrap_minimal,
    "runtime-quiet": check_runtime_quiet,
    "runtime-friction": check_runtime_friction,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Check meta-skill-feedback eval outputs.")
    parser.add_argument("--eval", required=True, choices=sorted(CHECKERS))
    parser.add_argument("--outputs", type=Path, required=True, help="Executor outputs/ dir")
    parser.add_argument(
        "--fixture-root",
        type=Path,
        default=None,
        help="evals/fixtures path (required for runtime-* evals)",
    )
    args = parser.parse_args()
    outputs = args.outputs.resolve()
    if args.eval in ("runtime-quiet", "runtime-friction"):
        if not args.fixture_root:
            raise SystemExit("--fixture-root required for runtime evals")
        fixture_root = args.fixture_root.resolve()
        if args.eval == "runtime-quiet":
            results = check_runtime_quiet(outputs, fixture_root)
        else:
            results = check_runtime_friction(outputs, fixture_root)
    else:
        results = CHECKERS[args.eval](outputs)
    summary = {
        "eval": args.eval,
        "outputs": str(outputs),
        "passed": sum(1 for r in results if r["passed"]),
        "total": len(results),
        "expectations": results,
    }
    print(json.dumps(summary, indent=2))
    sys.exit(0 if summary["passed"] == summary["total"] else 1)


if __name__ == "__main__":
    main()
