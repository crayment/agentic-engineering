#!/usr/bin/env python3
"""
skills-doctor: inventory every SKILL.md this machine's tools can see, work out
where each one actually comes from, and flag any same-named copies that
*aren't* linked together (symlink or hardlink) despite looking like they
should be -- i.e. silent-drift risk, where editing one copy won't update
the others.

Run with no arguments. Stdlib only, no dependencies.

    python3 scripts/skills_doctor.py
    python3 scripts/skills_doctor.py --json   # machine-readable dump instead

Add new source repos / install roots to SOURCE_REPOS / LINKABLE_ROOTS below as
your setup evolves -- this file is meant to be edited, not just run.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

HOME = Path.home()

# Repos where you actually author skills. Everything else is expected to be a
# symlink or hardlink pointing back into one of these.
SOURCE_REPOS = [
    ("agentic-engineering", HOME / "dev/me/agentic-engineering/.agents/skills"),
    ("dotfiles", HOME / "dev/me/dotfiles/agents/skills"),
]

# Personal install roots whose immediate children are individual skill dirs.
# These get cross-linked against each other and against SOURCE_REPOS. Source
# repos listed first so they win as the "canonical" label when a root turns
# out to be a symlinked alias of one (see dedupe_aliased_roots) -- the repo is
# ground truth, the install root is just how a tool sees it.
LINKABLE_ROOTS = SOURCE_REPOS + [
    ("cursor-personal", HOME / ".cursor/skills"),
    ("claude-personal", HOME / ".claude/skills"),
    ("agents-personal", HOME / ".agents/skills"),
]

# Read-only, managed-by-something-else roots. Inventoried, never expected to
# link anywhere -- just informational.
READONLY_ROOTS = [
    ("cursor built-in", HOME / ".cursor/skills-cursor"),
]

PLUGIN_CACHE_ROOT = HOME / ".cursor/plugins/cache"

# Repos to scan for repo-local ("project scope") skills. Add more paths here
# as you pick up new projects with their own .claude/skills or .cursor/skills.
PROJECT_REPOS = [
    HOME / "dev/financial-vendor-data",
]

# `npx skills add` (https://github.com/vercel-labs/skills) writes a lockfile
# recording exactly where an installed skill came from -- this is the only
# place real provenance lives; nothing else on disk records "how" a skill
# arrived. Global installs lock in the *source* repo's own agents dir (not a
# fixed dotfile location), project installs lock at the project root.
GLOBAL_LOCKFILES = [HOME / "dev/me/dotfiles/agents/.skill-lock.json"]
PROJECT_LOCKFILES = [repo / "skills-lock.json" for repo in PROJECT_REPOS]


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


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()[:12]


def scan_collection_pointers(label: str, root: Path) -> list[tuple[str, Path]]:
    """Symlinked children of `root` that point at a whole OTHER skills folder
    (no SKILL.md directly inside them) rather than being a skill themselves,
    e.g. ~/.agents/skills/cody-public-skills -> .../agentic-engineering/.agents/skills.
    """
    out: list[tuple[str, Path]] = []
    if not root.is_dir():
        return out
    for child in sorted(root.iterdir()):
        if child.is_symlink() and child.is_dir() and not (child / "SKILL.md").is_file():
            out.append((child.name, child.resolve()))
    return out


def scan_linkable_root(label: str, root: Path) -> dict[str, Instance]:
    """Return {skill_name: Instance} for immediate children of `root`."""
    out: dict[str, Instance] = {}
    if not root.is_dir():
        return out
    for child in sorted(root.iterdir()):
        skill_md = child / "SKILL.md"
        if not skill_md.is_file():
            continue
        st = skill_md.stat()  # follows symlinks -- gives the REAL underlying file
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


def scan_readonly_root(label: str, root: Path) -> list[str]:
    if not root.is_dir():
        return []
    return sorted(p.name for p in root.iterdir() if (p / "SKILL.md").is_file())


def scan_plugin_cache(root: Path) -> dict[str, list[str]]:
    """{publisher/plugin: [skill names]} for cached marketplace plugin skills."""
    out: dict[str, list[str]] = {}
    if not root.is_dir():
        return out
    for skill_md in root.rglob("SKILL.md"):
        parts = skill_md.relative_to(root).parts
        # <publisher>/<plugin>/<hash>/skills/<skill-name>/SKILL.md
        if len(parts) >= 5 and parts[3] == "skills":
            key = f"{parts[0]}/{parts[1]}"
            out.setdefault(key, []).append(parts[4])
    for key in out:
        out[key] = sorted(set(out[key]))
    return out


def parse_lockfile(path: Path) -> dict[str, dict]:
    """Normalize a `.skill-lock.json` / `skills-lock.json` into
    {skill_name: {"source": ..., "sourceUrl": ..., "installedAt": ...}}.
    Schema has changed across versions (v1: computedHash, no timestamp; v3:
    skillFolderHash + installedAt) -- read leniently, only keys we use.
    """
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


def scan_project_repo(repo: Path) -> dict[str, list[str]]:
    """{'.claude/skills' | '.cursor/skills': [skill names]} for one repo."""
    out: dict[str, list[str]] = {}
    for rel in (".claude/skills", ".cursor/skills"):
        d = repo / rel
        if not d.is_dir():
            continue
        names = sorted(p.name for p in d.iterdir() if (p / "SKILL.md").is_file())
        if names:
            out[rel] = names
    return out


def dedupe_aliased_roots(
    roots: list[tuple[str, Path]]
) -> tuple[list[tuple[str, Path]], list[tuple[str, str, Path]]]:
    """Some configured roots may resolve to the identical real directory (e.g.
    `~/.agents` is itself a symlink to a source repo) -- scanning both as if
    independent double-counts every skill inside as a phantom extra copy.
    Collapse aliases to the first label seen; return (deduped, aliases) where
    aliases is [(alias_label, canonical_label, real_path), ...] for reporting.
    """
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


def main() -> None:
    as_json = "--json" in sys.argv[1:]

    active_roots, root_aliases = dedupe_aliased_roots(LINKABLE_ROOTS)

    per_root: dict[str, dict[str, Instance]] = {}
    for label, root in active_roots:
        per_root[label] = scan_linkable_root(label, root)

    all_names = sorted({name for instances in per_root.values() for name in instances})

    report = {"linked": [], "unlinked_identical": [], "diverged": [], "single_location": []}

    for name in all_names:
        instances = [per_root[label][name] for label, _ in active_roots if name in per_root[label]]
        if len(instances) == 1:
            report["single_location"].append((name, instances))
            continue

        clusters: dict[tuple[int, int], list[Instance]] = {}
        for inst in instances:
            clusters.setdefault(inst.cluster_key, []).append(inst)

        if len(clusters) == 1:
            report["linked"].append((name, instances))
            continue

        hashes = {inst.sha256 for inst in instances}
        if len(hashes) == 1:
            report["unlinked_identical"].append((name, instances, clusters))
        else:
            report["diverged"].append((name, instances, clusters))

    readonly = {label: scan_readonly_root(label, root) for label, root in READONLY_ROOTS}
    plugins = scan_plugin_cache(PLUGIN_CACHE_ROOT)
    projects = {str(repo): scan_project_repo(repo) for repo in PROJECT_REPOS}
    pointers = {label: scan_collection_pointers(label, root) for label, root in active_roots}

    global_provenance: dict[str, dict] = {}
    for lockfile in GLOBAL_LOCKFILES:
        global_provenance.update(parse_lockfile(lockfile))
    project_provenance = {str(repo): parse_lockfile(lockfile) for repo, lockfile in zip(PROJECT_REPOS, PROJECT_LOCKFILES)}

    if as_json:
        def inst_to_dict(i: Instance) -> dict:
            return {
                "root": i.root_label,
                "path": str(i.path),
                "symlink_target": str(i.dir_symlink_target) if i.dir_symlink_target else None,
                "sha256_12": i.sha256,
            }

        json.dump(
            {
                "diverged": [(n, [inst_to_dict(i) for i in insts]) for n, insts, _ in report["diverged"]],
                "unlinked_identical": [
                    (n, [inst_to_dict(i) for i in insts]) for n, insts, _ in report["unlinked_identical"]
                ],
                "linked": [(n, [inst_to_dict(i) for i in insts]) for n, insts in report["linked"]],
                "single_location": [(n, [inst_to_dict(i) for i in insts]) for n, insts in report["single_location"]],
                "cursor_builtin": readonly.get("cursor built-in", []),
                "plugin_cache": plugins,
                "project_local": projects,
            },
            sys.stdout,
            indent=2,
        )
        return

    def print_instances(instances: list[Instance]) -> None:
        for i in instances:
            via = f" -> {i.dir_symlink_target}" if i.dir_is_symlink else ""
            print(f"      [{i.root_label}] {i.path}{via}  (sha256:{i.sha256})")

    print("=" * 70)
    print("ALIASED ROOTS -- these configured roots are the SAME real directory")
    print("(one is a symlink to the other at a higher level -- not two copies)")
    print("=" * 70)
    if not root_aliases:
        print("  (none)")
    for alias_label, canonical_label, real in root_aliases:
        print(f"  {alias_label}  ==  {canonical_label}   (both resolve to {real})")

    print()
    print("=" * 70)
    print("DIVERGED -- same skill name, different content, NOT linked")
    print("(someone edited one copy without updating the others -- fix this first)")
    print("=" * 70)
    if not report["diverged"]:
        print("  (none)")
    for name, instances, clusters in report["diverged"]:
        print(f"\n  {name}  ({len(clusters)} distinct versions across {len(instances)} locations)")
        print_instances(instances)

    print()
    print("=" * 70)
    print("UNLINKED BUT CURRENTLY IDENTICAL -- separate copies, same content today")
    print("(drift risk: editing one will NOT update the others)")
    print("=" * 70)
    if not report["unlinked_identical"]:
        print("  (none)")
    for name, instances, clusters in report["unlinked_identical"]:
        print(f"\n  {name}  ({len(clusters)} separate copies, {len(instances)} locations)")
        print_instances(instances)

    print()
    print("=" * 70)
    print("LINKED -- all copies share one underlying file (symlink or hardlink)")
    print("=" * 70)
    for name, instances in report["linked"]:
        locations = ", ".join(i.root_label for i in instances)
        print(f"  {name:<32} <- {locations}")

    print()
    print("=" * 70)
    print("SINGLE LOCATION -- only exists in one place")
    print("=" * 70)
    for name, instances in report["single_location"]:
        prov = global_provenance.get(name)
        origin = f"  installed via `npx skills add` from {prov['source']}" if prov else "  origin unknown (hand-placed, or installed by something other than `npx skills add`)"
        print(f"  {name:<32} [{instances[0].root_label}]{origin}")

    print()
    print("=" * 70)
    print("COLLECTION POINTERS -- a named symlink to a whole other skills folder")
    print("=" * 70)
    for label, links in pointers.items():
        for name, target in links:
            print(f"  [{label}] {name} -> {target}")

    print()
    print("=" * 70)
    print("CURSOR BUILT-IN (~/.cursor/skills-cursor -- managed by Cursor, not you)")
    print("=" * 70)
    for name in readonly.get("cursor built-in", []):
        print(f"  {name}")

    print()
    print("=" * 70)
    print("MARKETPLACE / PLUGIN-INSTALLED (~/.cursor/plugins/cache -- read-only)")
    print("=" * 70)
    for plugin, names in sorted(plugins.items()):
        print(f"  {plugin}: {', '.join(names)}")

    print()
    print("=" * 70)
    print("PROJECT-LOCAL (repo-scoped -- authored in-repo OR installed there via `npx skills add`)")
    print("=" * 70)
    for repo, dirs in projects.items():
        prov = project_provenance.get(repo, {})
        for rel, names in dirs.items():
            for name in names:
                if name in prov:
                    print(f"  {repo}/{rel}/{name}  <- npx skills add from {prov[name]['source']}")
                else:
                    print(f"  {repo}/{rel}/{name}  (authored directly in this repo)")

    print()
    print("=" * 70)
    print("PROVENANCE -- everything a `.skill-lock.json` / `skills-lock.json` remembers")
    print("(the ONLY on-disk record of *how* a skill arrived, vs. being hand-placed)")
    print("=" * 70)
    if not global_provenance and not any(project_provenance.values()):
        print("  (no lockfiles found)")
    for name, info in sorted(global_provenance.items()):
        print(f"  [global] {name:<28} <- {info['source']}  ({info['sourceUrl']})")
    for repo, prov in project_provenance.items():
        for name, info in sorted(prov.items()):
            print(f"  [{repo}] {name:<28} <- {info['source']}")


if __name__ == "__main__":
    main()
