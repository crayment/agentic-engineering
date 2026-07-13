#!/usr/bin/env python3
"""
skills-doctor: for the project you're standing in right now, print every
skill visible from PROJECT scope (this repo) then HOME scope (~), one line
each, colored so your eye goes straight to what needs fixing.

The model: `.agents/skills/<name>/` is the source of truth. `.claude/skills/
<name>` must be a symlink pointing at it. Everything else is a warning:

    OK     .agents/skills/<name>  <-symlink-  .claude/skills/<name>
    WARN   .agents has it, .claude doesn't (missing link)
    WARN   .claude has it, .agents doesn't (source-of-truth violation --
           this skill isn't reachable from wherever `.agents` is canonical)
    WARN   .claude is a real dir, not a symlink, but content currently
           matches .agents (drift risk: editing one won't update the other)
    WARN   .claude is a symlink, but points somewhere OTHER than this
           scope's .agents copy (overridden from elsewhere)
    WARN   reachable only via a collection-pointer folder in .agents
           (e.g. `.agents/skills/some-bundle -> other/skills/`) rather than
           its own individual entry -- fine for now, but not the convention
    WARN   same name also exists in the other scope (PROJECT always wins;
           the HOME copy is shadowed and invisible to tools run from here)
    ERROR  .claude is a real dir AND content has actually diverged from
           .agents -- someone edited one copy without the other

Run from anywhere inside a repo:

    python3 scripts/skills_doctor.py              # scope report for cwd's repo
    python3 scripts/skills_doctor.py /some/path    # scope report for a specific project dir
    python3 scripts/skills_doctor.py --json        # machine-readable scope report
    python3 scripts/skills_doctor.py --no-color    # plain text (auto-detected for non-ttys anyway)
    python3 scripts/skills_doctor.py --full        # also dump cross-machine provenance/plugin detail

Stdlib only, no dependencies.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

HOME = Path.home()

# Repos where skills actually get authored -- used to label what a symlink
# resolves back to (e.g. "agentic-engineering/git-worktree") and as the scan
# targets for --full's cross-machine linkage report.
SOURCE_REPOS = [
    ("agentic-engineering", HOME / "dev/me/agentic-engineering/.agents/skills"),
    ("dotfiles", HOME / "dev/me/dotfiles/agents/skills"),
]

# --full only: personal install roots whose immediate children are individual
# skill dirs, cross-linked against each other and against SOURCE_REPOS.
LINKABLE_ROOTS = SOURCE_REPOS + [
    ("cursor-personal", HOME / ".cursor/skills"),
    ("claude-personal", HOME / ".claude/skills"),
    ("agents-personal", HOME / ".agents/skills"),
]

READONLY_ROOTS = [("cursor built-in", HOME / ".cursor/skills-cursor")]
PLUGIN_CACHE_ROOT = HOME / ".cursor/plugins/cache"
PROJECT_REPOS = [HOME / "dev/financial-vendor-data"]

# `npx skills add` (https://github.com/vercel-labs/skills) writes a lockfile
# recording exactly where an installed skill came from -- but that's the
# only tool that leaves an automatic trail. Everything else (a homebrew
# formula's own docs, a gist you curled, a coworker's paste) has no
# structural record on disk, so GLOBAL_NOTES_FILE / PROJECT_NOTES_FILE are a
# hand-maintained fallback: add an entry there when you trace a skill's
# origin by hand so the next `skills_doctor` run remembers it for you.
# Global installs lock in the source repo's own agents dir; project installs
# lock at the project root.
GLOBAL_LOCKFILES = [HOME / "dev/me/dotfiles/agents/.skill-lock.json"]
GLOBAL_NOTES_FILE = HOME / "dev/me/dotfiles/agents/.skill-notes.json"


# --------------------------------------------------------------------------
# color
# --------------------------------------------------------------------------

class Colors:
    def __init__(self, enabled: bool):
        self.enabled = enabled

    def _wrap(self, code: str, text: str) -> str:
        return f"\033[{code}m{text}\033[0m" if self.enabled else text

    def green(self, t: str) -> str:
        return self._wrap("32", t)

    def yellow(self, t: str) -> str:
        return self._wrap("33", t)

    def red(self, t: str) -> str:
        return self._wrap("31", t)

    def dim(self, t: str) -> str:
        return self._wrap("2", t)

    def bold(self, t: str) -> str:
        return self._wrap("1", t)


GLYPH = {"OK": "\u2713", "WARN": "\u26a0", "ERROR": "\u2717"}  # check, warning, cross


def status_color(C: Colors, status: str, text: str) -> str:
    return {"OK": C.green, "WARN": C.yellow, "ERROR": C.red}[status](text)


# --------------------------------------------------------------------------
# filesystem scanning
# --------------------------------------------------------------------------

def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()[:12]


def find_project_root(start: Path) -> Path:
    cur = start.resolve()
    for p in [cur, *cur.parents]:
        if (p / ".git").exists():
            return p
    return cur


def label_target(target: Path) -> str:
    for label, root in SOURCE_REPOS:
        try:
            target.relative_to(root)
            return f"{label}/{target.name}"
        except ValueError:
            continue
    try:
        return f"~/{target.relative_to(HOME)}"
    except ValueError:
        return str(target)


@dataclass
class Canonical:
    real_path: Path
    via_pointer: str | None  # name of the .agents/skills/<pointer> dir it was found under, if not a direct entry


def discover_canonical(agents_skills_dir: Path) -> dict[str, Canonical]:
    """Direct children of `.agents/skills` with a SKILL.md are canonical.
    A child that's a symlinked folder WITHOUT its own SKILL.md is treated as
    a collection pointer -- one level inside it is scanned too, but flagged
    as non-canonical (`via_pointer` set)."""
    out: dict[str, Canonical] = {}
    if not agents_skills_dir.is_dir():
        return out
    for child in sorted(agents_skills_dir.iterdir()):
        if not child.exists():
            continue  # broken symlink directly under .agents/skills -- rare, ignored here
        if (child / "SKILL.md").is_file():
            out[child.name] = Canonical(child.resolve(), None)
        elif child.is_dir():
            for inner in sorted(child.iterdir()):
                if inner.exists() and (inner / "SKILL.md").is_file():
                    out.setdefault(inner.name, Canonical(inner.resolve(), child.name))
    return out


@dataclass
class ClaudeEntry:
    path: Path
    is_symlink: bool
    target: Path | None  # resolved target, only set for a live symlink
    broken: bool


def discover_claude(claude_skills_dir: Path) -> dict[str, ClaudeEntry]:
    out: dict[str, ClaudeEntry] = {}
    if not claude_skills_dir.is_dir():
        return out
    for child in sorted(claude_skills_dir.iterdir()):
        is_symlink = child.is_symlink()
        exists = child.exists()
        if is_symlink and not exists:
            out[child.name] = ClaudeEntry(child, True, None, True)
            continue
        if exists and (child / "SKILL.md").is_file():
            out[child.name] = ClaudeEntry(child, is_symlink, child.resolve() if is_symlink else None, False)
    return out


@dataclass
class Skill:
    name: str
    canonical: Canonical | None
    claude: ClaudeEntry | None
    sha_source: str | None
    sha_claude: str | None
    shadowed_by_project: bool = False
    shadows_home: bool = False


def build_scope(root: Path) -> dict[str, Skill]:
    canonical = discover_canonical(root / ".agents/skills")
    claude = discover_claude(root / ".claude/skills")
    names = sorted(set(canonical) | set(claude))
    out = {}
    for name in names:
        c = canonical.get(name)
        ce = claude.get(name)
        sha_source = sha256_of(c.real_path / "SKILL.md") if c else None
        sha_claude = sha256_of(ce.path / "SKILL.md") if ce and not ce.broken else None
        out[name] = Skill(name, c, ce, sha_source, sha_claude)
    return out


def classify(sk: Skill) -> tuple[str, str]:
    """(status, message). message is '' for a clean OK."""
    if sk.canonical is None:
        return "WARN", "only in .claude -- no .agents source (source-of-truth violation)"

    base_status, base_msg = _classify_link(sk)

    if sk.canonical.via_pointer:
        note = f"via collection pointer '{sk.canonical.via_pointer}' in .agents, not an individual entry"
        if base_status == "OK":
            return "WARN", note
        return base_status, f"{base_msg}; {note}"

    return base_status, base_msg


def _classify_link(sk: Skill) -> tuple[str, str]:
    if sk.claude is None:
        return "WARN", "missing .claude link"
    if sk.claude.broken:
        return "ERROR", "broken .claude symlink"
    if sk.claude.is_symlink:
        if sk.claude.target == sk.canonical.real_path:
            return "OK", ""
        return "WARN", f"overridden -- .claude points to {label_target(sk.claude.target)} instead"
    if sk.sha_source == sk.sha_claude:
        return "WARN", "unlinked copy, identical for now (drift risk)"
    return "ERROR", f"DIVERGED from .agents (agents:{sk.sha_source} claude:{sk.sha_claude})"


def location(sk: Skill) -> str:
    if sk.canonical and sk.claude:
        return "agents+claude"
    if sk.canonical:
        return "agents only"
    return "claude only"


def provenance_hint(
    name: str,
    scope_label: str,
    project_root: Path,
    global_prov: dict,
    project_prov: dict,
    global_notes: dict,
    project_notes: dict,
) -> str:
    prov = project_prov.get(name) if scope_label == "PROJECT" else global_prov.get(name)
    if prov and prov.get("source"):
        return f"npx: {prov['source']}"
    note = project_notes.get(name) if scope_label == "PROJECT" else global_notes.get(name)
    if note and note.get("source"):
        return f"noted: {note['source']}"
    return ""


# --------------------------------------------------------------------------
# reporting
# --------------------------------------------------------------------------

def print_scope(C: Colors, label: str, root: Path, skills: dict[str, Skill], project_root: Path,
                 global_prov: dict, project_prov: dict, global_notes: dict, project_notes: dict) -> tuple[int, int]:
    print(C.bold(f"{label}  {root}"))
    warns = errors = 0
    if not skills:
        print(C.dim("  (no skills found)"))
        return warns, errors
    for name, sk in skills.items():
        status, msg = classify(sk)
        if sk.shadowed_by_project:
            status = "WARN" if status == "OK" else status
            msg = "shadowed by same-named PROJECT skill" if not msg else f"{msg}; shadowed by same-named PROJECT skill"
        if status == "WARN":
            warns += 1
        elif status == "ERROR":
            errors += 1

        glyph = status_color(C, status, GLYPH[status])
        name_col = f"{name:<30}"
        loc_col = f"{location(sk):<14}"
        hint = msg if msg else provenance_hint(name, label, project_root, global_prov, project_prov, global_notes, project_notes)
        if msg:
            hint = status_color(C, status, hint)
        elif hint:
            hint = C.dim(f"<- {hint}")
        shadow_note = C.dim("  (shadows home copy)") if sk.shadows_home else ""
        print(f"  {glyph} {name_col} {loc_col} {hint}{shadow_note}")
    return warns, errors


def main() -> None:
    argv = sys.argv[1:]
    as_json = "--json" in argv
    full = "--full" in argv
    no_color = "--no-color" in argv or os.environ.get("NO_COLOR") is not None
    positional = [a for a in argv if not a.startswith("--")]

    C = Colors(enabled=(not no_color) and sys.stdout.isatty())

    start = Path(positional[0]) if positional else Path.cwd()
    project_root = find_project_root(start)

    same = project_root.resolve() == HOME.resolve()
    scopes = [("HOME", HOME)] if same else [("PROJECT", project_root), ("HOME", HOME)]

    per_scope = {label: build_scope(root) for label, root in scopes}

    if not same:
        project_names = set(per_scope["PROJECT"])
        for name, sk in per_scope["HOME"].items():
            if name in project_names:
                sk.shadowed_by_project = True
        for name, sk in per_scope["PROJECT"].items():
            if name in per_scope["HOME"]:
                sk.shadows_home = True

    global_prov: dict[str, dict] = {}
    for lockfile in GLOBAL_LOCKFILES:
        global_prov.update(parse_lockfile(lockfile))
    project_prov = parse_lockfile(project_root / "skills-lock.json")
    global_notes = parse_notes(GLOBAL_NOTES_FILE)
    project_notes = parse_notes(project_root / "skills-notes.json")

    if as_json:
        def skill_to_dict(sk: Skill) -> dict:
            status, msg = classify(sk)
            return {
                "status": status,
                "message": msg,
                "location": location(sk),
                "agents_path": str(sk.canonical.real_path) if sk.canonical else None,
                "via_pointer": sk.canonical.via_pointer if sk.canonical else None,
                "claude_path": str(sk.claude.path) if sk.claude else None,
                "claude_is_symlink": sk.claude.is_symlink if sk.claude else None,
                "shadowed_by_project": sk.shadowed_by_project,
            }

        out = {label: {name: skill_to_dict(sk) for name, sk in skills.items()} for label, skills in per_scope.items()}
        json.dump(out, sys.stdout, indent=2)
        print()
        return

    total_warns = total_errors = 0
    for label, root in scopes:
        w, e = print_scope(C, label, root, per_scope[label], project_root, global_prov, project_prov, global_notes, project_notes)
        total_warns += w
        total_errors += e
        print()

    total = sum(len(s) for s in per_scope.values())
    summary = f"{total} skills"
    if total_errors:
        summary += "  \u00b7  " + C.red(f"{total_errors} error{'s' if total_errors != 1 else ''}")
    if total_warns:
        summary += "  \u00b7  " + C.yellow(f"{total_warns} warning{'s' if total_warns != 1 else ''}")
    if not total_warns and not total_errors:
        summary += "  \u00b7  " + C.green("all linked correctly")
    print(summary)

    if full:
        print_full_report()


# --------------------------------------------------------------------------
# --full: cross-machine inventory (unscoped)
# --------------------------------------------------------------------------

@dataclass
class Instance:
    root_label: str
    path: Path
    dir_is_symlink: bool
    dir_symlink_target: Path | None
    dev: int
    ino: int
    sha256: str

    @property
    def cluster_key(self) -> tuple[int, int]:
        return (self.dev, self.ino)


def scan_linkable_root(label: str, root: Path) -> dict[str, Instance]:
    out: dict[str, Instance] = {}
    if not root.is_dir():
        return out
    for child in sorted(root.iterdir()):
        skill_md = child / "SKILL.md"
        if not skill_md.is_file():
            continue
        st = skill_md.stat()
        out[child.name] = Instance(
            root_label=label,
            path=child,
            dir_is_symlink=child.is_symlink(),
            dir_symlink_target=child.resolve() if child.is_symlink() else None,
            dev=st.st_dev,
            ino=st.st_ino,
            sha256=sha256_of(skill_md),
        )
    return out


def scan_readonly_root(root: Path) -> list[str]:
    if not root.is_dir():
        return []
    return sorted(p.name for p in root.iterdir() if (p / "SKILL.md").is_file())


def scan_plugin_cache(root: Path) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    if not root.is_dir():
        return out
    for skill_md in root.rglob("SKILL.md"):
        parts = skill_md.relative_to(root).parts
        if len(parts) >= 5 and parts[3] == "skills":
            key = f"{parts[0]}/{parts[1]}"
            out.setdefault(key, []).append(parts[4])
    for key in out:
        out[key] = sorted(set(out[key]))
    return out


def parse_lockfile(path: Path) -> dict[str, dict]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}
    out = {}
    for name, entry in (data.get("skills") or {}).items():
        out[name] = {
            "source": entry.get("source"),
            "sourceUrl": entry.get("sourceUrl"),
            "installedAt": entry.get("installedAt"),
        }
    return out


def parse_notes(path: Path) -> dict[str, dict]:
    """Hand-maintained fallback for provenance a lockfile can't capture --
    a flat {name: {"source", "url", "note", "recorded_at"}} JSON map. Add an
    entry whenever you trace a skill's origin by hand (e.g. `gog` -> a
    homebrew formula whose docs you copied in)."""
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}
    out = {}
    for name, entry in data.items():
        out[name] = {
            "source": entry.get("source"),
            "url": entry.get("url"),
            "note": entry.get("note"),
            "recorded_at": entry.get("recorded_at"),
        }
    return out


def dedupe_aliased_roots(roots: list[tuple[str, Path]]) -> tuple[list[tuple[str, Path]], list[tuple[str, str, Path]]]:
    seen: dict[Path, str] = {}
    deduped: list[tuple[str, Path]] = []
    aliases: list[tuple[str, str, Path]] = []
    for label, root in roots:
        real = root.resolve()
        if real in seen:
            aliases.append((label, seen[real], real))
            continue
        seen[real] = label
        deduped.append((label, root))
    return deduped, aliases


def print_full_report() -> None:
    print()
    print("#" * 70)
    print("--full: CROSS-MACHINE INVENTORY (all configured roots, not scoped to cwd)")
    print("#" * 70)

    active_roots, root_aliases = dedupe_aliased_roots(LINKABLE_ROOTS)
    per_root = {label: scan_linkable_root(label, root) for label, root in active_roots}
    all_names = sorted({name for instances in per_root.values() for name in instances})

    print()
    print("ALIASED ROOTS (same real directory, not two copies)")
    if not root_aliases:
        print("  (none)")
    for alias_label, canonical_label, real in root_aliases:
        print(f"  {alias_label}  ==  {canonical_label}   (both resolve to {real})")

    print()
    print("CURSOR BUILT-IN (~/.cursor/skills-cursor -- managed by Cursor, not you)")
    for name in scan_readonly_root(READONLY_ROOTS[0][1]):
        print(f"  {name}")

    print()
    print("MARKETPLACE / PLUGIN-INSTALLED (~/.cursor/plugins/cache -- read-only)")
    for plugin, names in sorted(scan_plugin_cache(PLUGIN_CACHE_ROOT).items()):
        print(f"  {plugin}: {', '.join(names)}")

    print()
    print("PROVENANCE (`.skill-lock.json` / `skills-lock.json` -- the only on-disk")
    print("record of *how* a skill arrived, vs. being hand-placed)")
    global_provenance: dict[str, dict] = {}
    for lockfile in GLOBAL_LOCKFILES:
        global_provenance.update(parse_lockfile(lockfile))
    project_provenance = {repo: parse_lockfile(repo / "skills-lock.json") for repo in PROJECT_REPOS}
    if not global_provenance and not any(project_provenance.values()):
        print("  (no lockfiles found)")
    for name, info in sorted(global_provenance.items()):
        print(f"  [global] {name:<28} <- {info['source']}  ({info['sourceUrl']})")
    for repo, prov in project_provenance.items():
        for name, info in sorted(prov.items()):
            print(f"  [{repo}] {name:<28} <- {info['source']}")

    print()
    print(f"names visible across all linkable roots: {len(all_names)}")


if __name__ == "__main__":
    main()
