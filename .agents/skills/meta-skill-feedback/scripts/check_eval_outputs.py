#!/usr/bin/env python3
# ABOUTME: Deterministic eval checks for meta-skill-feedback bootstrap/runtime runs.
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
VOTE_PLUS_ONE = re.compile(r"·\s*\+1\b")
AGENT_COMMENT = re.compile(r"^###\s+\d{4}-\d{2}-\d{2}T\d{4}", re.MULTILINE)
DEDUPE_SEED = "2026-08-01T1200-wrong-data-path.md"


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
    return [p for p in feedback_dir.glob("*.md") if p.name != "README.md"]


def _skill_unchanged(fixture_root: Path, outputs: Path, fixture_name: str) -> bool:
    fixture_skill = fixture_root / fixture_name / "SKILL.md"
    out_skill = outputs / fixture_name / "SKILL.md"
    return (
        _exists(fixture_skill)
        and _exists(out_skill)
        and _read(fixture_skill) == _read(out_skill)
    )


def check_bootstrap_counter_skill(outputs: Path) -> list[dict]:
    target = outputs / "counter-skill"
    fb = target / "feedback"
    skill = target / "SKILL.md"
    readme = _read(fb / "README.md").lower()
    checks = [
        ("outputs/counter-skill/feedback/README.md exists", _exists(fb / "README.md")),
        (
            "outputs/counter-skill/feedback/resolved/ exists as a directory",
            _dir_exists(fb / "resolved"),
        ),
        (
            "outputs/counter-skill/SKILL.md references feedback/ or feedback/README.md",
            _skill_cues_feedback(_read(skill)),
        ),
        (
            "feedback/README.md mentions votes or +1 for duplicate issues",
            "vote" in readme or "+1" in readme,
        ),
        (
            "No friction note files in outputs/counter-skill/feedback/ except README.md",
            len(feedback_notes(fb)) == 0,
        ),
        (
            "No scripts/scaffold.py was created under outputs/counter-skill/",
            not _exists(target / "scripts" / "scaffold.py"),
        ),
    ]
    return [{"text": t, "passed": p} for t, p in checks]


def check_runtime_quiet(outputs: Path, fixture_root: Path) -> list[dict]:
    name = "counter-skill-ready"
    target = outputs / name
    fb = target / "feedback"
    notes = feedback_notes(fb)
    ts_notes = [p for p in notes if TIMESTAMP_NOTE.search(str(p.relative_to(target)))]
    checks = [
        (
            f"No new files matching outputs/{name}/feedback/YYYY-MM-DDTHHMM-*.md",
            len(ts_notes) == 0,
        ),
        (
            f"outputs/{name}/SKILL.md unchanged from fixture",
            _skill_unchanged(fixture_root, outputs, name),
        ),
        (
            "Only feedback/README.md under feedback/",
            len(notes) == 0,
        ),
    ]
    return [{"text": t, "passed": p} for t, p in checks]


def check_runtime_friction(outputs: Path, fixture_root: Path) -> list[dict]:
    name = "counter-skill-trap"
    target = outputs / name
    fb = target / "feedback"
    notes = feedback_notes(fb)
    ts_notes = [p for p in notes if TIMESTAMP_NOTE.search(str(p.relative_to(target)))]
    note_text = "\n".join(_read(p) for p in ts_notes).lower()
    path_mentioned = any(
        s in note_text
        for s in ("data/project", "inputs/project", "wrong path", "misleading")
    )
    checks = [
        (
            f"Exactly one new friction note in outputs/{name}/feedback/",
            len(ts_notes) == 1,
        ),
        (
            "Note mentions data/project or inputs/project path mismatch",
            path_mentioned,
        ),
        (
            "Note has What happened and Votes sections",
            "what happened" in note_text and "votes" in note_text,
        ),
        (
            f"outputs/{name}/SKILL.md unchanged from fixture",
            _skill_unchanged(fixture_root, outputs, name),
        ),
    ]
    return [{"text": t, "passed": p} for t, p in checks]


def check_runtime_vote(outputs: Path, fixture_root: Path) -> list[dict]:
    name = "counter-skill-dedupe"
    target = outputs / name
    fb = target / "feedback"
    notes = feedback_notes(fb)
    seed_path = fb / DEDUPE_SEED
    fixture_seed = fixture_root / name / "feedback" / DEDUPE_SEED
    out_text = _read(seed_path)
    fixture_text = _read(fixture_seed)
    plus_one_count = len(VOTE_PLUS_ONE.findall(out_text))
    fixture_plus_one = len(VOTE_PLUS_ONE.findall(fixture_text))
    new_comments = len(AGENT_COMMENT.findall(out_text)) - len(
        AGENT_COMMENT.findall(fixture_text)
    )
    checks = [
        (
            "Still exactly one open friction note (the seeded file) under feedback/",
            len(notes) == 1 and _exists(seed_path),
        ),
        (
            "Seeded note has a new +1 vote line",
            plus_one_count > fixture_plus_one,
        ),
        (
            "Seeded note has a new Agent comments entry",
            new_comments >= 1 or (
                "## agent comments" in out_text.lower()
                and out_text.strip() != fixture_text.strip()
                and "+1" in out_text.lower()
            ),
        ),
        (
            f"outputs/{name}/SKILL.md unchanged from fixture",
            _skill_unchanged(fixture_root, outputs, name),
        ),
    ]
    return [{"text": t, "passed": p} for t, p in checks]


def check_runtime_stuck(outputs: Path, fixture_root: Path) -> list[dict]:
    name = "counter-skill-stuck"
    target = outputs / name
    fb = target / "feedback"
    notes = feedback_notes(fb)
    ts_notes = [p for p in notes if TIMESTAMP_NOTE.search(str(p.relative_to(target)))]
    note_text = "\n".join(_read(p) for p in ts_notes).lower()
    blocked = any(
        s in note_text
        for s in ("count.sh", "exit", "fail", "blocked", "error", "stuck")
    )
    checks = [
        (
            f"Exactly one new friction note in outputs/{name}/feedback/",
            len(ts_notes) == 1,
        ),
        (
            "Note mentions count.sh failure, exit, or blocked run",
            blocked,
        ),
        (
            f"outputs/{name}/SKILL.md unchanged from fixture",
            _skill_unchanged(fixture_root, outputs, name),
        ),
    ]
    return [{"text": t, "passed": p} for t, p in checks]


CHECKERS = {
    "bootstrap-counter-skill": check_bootstrap_counter_skill,
    "runtime-quiet": check_runtime_quiet,
    "runtime-friction": check_runtime_friction,
    "runtime-vote": check_runtime_vote,
    "runtime-stuck": check_runtime_stuck,
}

RUNTIME_EVALS = frozenset({"runtime-quiet", "runtime-friction", "runtime-vote", "runtime-stuck"})


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
    if args.eval in RUNTIME_EVALS:
        if not args.fixture_root:
            raise SystemExit("--fixture-root required for runtime evals")
        fixture_root = args.fixture_root.resolve()
        results = CHECKERS[args.eval](outputs, fixture_root)
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
