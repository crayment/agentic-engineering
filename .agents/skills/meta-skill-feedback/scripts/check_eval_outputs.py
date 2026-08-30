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
            "feedback" in _read(skill).lower(),
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


def check_bootstrap_wake(outputs: Path) -> list[dict]:
    target = outputs / "wake-shaped-skill"
    fb = target / "feedback"
    skill = _read(target / "SKILL.md")
    wake = _read(target / "references" / "wake.md")
    readme = _read(fb / "README.md").lower()
    wake_ctx = any(
        w in readme for w in ("wake", "scheduled", "unattended")
    )
    checks = [
        ("outputs/wake-shaped-skill/feedback/README.md exists", _exists(fb / "README.md")),
        (
            "outputs/wake-shaped-skill/SKILL.md references feedback",
            "feedback" in skill.lower(),
        ),
        (
            "references/wake.md or SKILL.md mentions feedback/ for agents finishing a wake run",
            "feedback" in skill.lower() or "feedback" in wake.lower(),
        ),
        (
            "feedback/README.md mentions wake or scheduled/unattended context",
            wake_ctx,
        ),
        (
            "No friction note files seeded except README.md",
            len(feedback_notes(fb)) == 0,
        ),
    ]
    return [{"text": t, "passed": p} for t, p in checks]


def check_runtime_quiet(outputs: Path, fixture_root: Path) -> list[dict]:
    target = outputs / "wake-shaped-bootstrapped"
    fb = target / "feedback"
    fixture_skill = fixture_root / "wake-shaped-bootstrapped" / "SKILL.md"
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
            "No new files matching outputs/wake-shaped-bootstrapped/feedback/YYYY-MM-DDTHHMM-*.md",
            len(ts_notes) == 0,
        ),
        (
            "outputs/wake-shaped-bootstrapped/SKILL.md was not modified from the fixture copy",
            skill_unchanged,
        ),
        (
            "Only feedback/README.md exists under feedback/ (no extra .md notes)",
            len(notes) == 0,
        ),
    ]
    return [{"text": t, "passed": p} for t, p in checks]


CHECKERS = {
    "bootstrap-minimal": check_bootstrap_minimal,
    "bootstrap-wake-shaped": check_bootstrap_wake,
    "runtime-quiet": check_runtime_quiet,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Check meta-skill-feedback eval outputs.")
    parser.add_argument("--eval", required=True, choices=sorted(CHECKERS))
    parser.add_argument("--outputs", type=Path, required=True, help="Executor outputs/ dir")
    parser.add_argument(
        "--fixture-root",
        type=Path,
        default=None,
        help="evals/fixtures path (required for runtime-quiet)",
    )
    args = parser.parse_args()
    outputs = args.outputs.resolve()
    if args.eval == "runtime-quiet":
        if not args.fixture_root:
            raise SystemExit("--fixture-root required for runtime-quiet")
        results = check_runtime_quiet(outputs, args.fixture_root.resolve())
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
