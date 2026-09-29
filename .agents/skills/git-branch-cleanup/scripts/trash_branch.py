#!/usr/bin/env python3
"""Move local branches into trash/<date>/, snapshotting uncommitted worktree changes first."""

import argparse
import datetime
import os
import shutil
import subprocess
import sys
import tempfile

GIT = shutil.which("git") or "/usr/bin/git"
SNAPSHOT_PREFIX = "trash: snapshot uncommitted changes"


def git(cwd: str, *args: str, env: dict | None = None) -> str:
    result = subprocess.run([GIT, "-C", cwd, *args], capture_output=True, text=True, env=env)
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout.strip()


def main_clone(path: str) -> str:
    return os.path.dirname(git(path, "rev-parse", "--path-format=absolute", "--git-common-dir").rstrip("/"))


def worktree_for(root: str, branch: str) -> tuple[str | None, bool]:
    path, index = None, -1
    for line in git(root, "worktree", "list", "--porcelain").splitlines():
        if line.startswith("worktree "):
            path, index = line[len("worktree ") :], index + 1
        elif line == f"branch refs/heads/{branch}":
            return path, index == 0
    return None, False


def snapshot(worktree: str) -> str | None:
    if not git(worktree, "status", "--porcelain"):
        return None
    with tempfile.TemporaryDirectory() as tmp:
        env = {**os.environ, "GIT_INDEX_FILE": os.path.join(tmp, "index")}
        git(worktree, "read-tree", "HEAD", env=env)
        git(worktree, "add", "-A", env=env)
        tree = git(worktree, "write-tree", env=env)
    message = f"{SNAPSHOT_PREFIX}\n\nFrom worktree {worktree}"
    return git(worktree, "commit-tree", tree, "-p", "HEAD", "-m", message)


def trash(root: str, branch: str, date: str, dry_run: bool) -> str:
    if branch.startswith("trash/"):
        raise RuntimeError(f"{branch} is already in trash")
    tip = git(root, "rev-parse", "--verify", f"refs/heads/{branch}")
    target_ref = f"refs/heads/trash/{date}/{branch}"
    if subprocess.run([GIT, "-C", root, "rev-parse", "--verify", "--quiet", target_ref], capture_output=True).returncode == 0:
        raise RuntimeError(f"{target_ref} already exists")
    worktree, is_main = worktree_for(root, branch)
    if is_main:
        raise RuntimeError(f"{branch} is checked out in the main clone")
    dirty = bool(worktree and os.path.isdir(worktree) and git(worktree, "status", "--porcelain"))
    plan = f"{branch} -> trash/{date}/{branch}" + (f", remove {worktree}" if worktree else "") + (", snapshot uncommitted" if dirty else "")
    if dry_run:
        return f"would move {plan}"

    target = (snapshot(worktree) if dirty else None) or tip
    git(root, "update-ref", target_ref, target, "")
    if worktree:
        git(root, "worktree", "remove", "--force", worktree)
    git(root, "branch", "-D", branch)
    return f"moved {plan}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", help="any path inside the repo")
    parser.add_argument("branches", nargs="+", help="local branch names to trash")
    parser.add_argument("--dry-run", action="store_true", help="print the plan without changing anything")
    args = parser.parse_args()

    root = main_clone(os.path.abspath(args.repo))
    date = datetime.date.today().isoformat()
    failed = False
    for branch in args.branches:
        try:
            print(trash(root, branch, date, args.dry_run))
        except RuntimeError as error:
            failed = True
            print(f"skipped {branch}: {error}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
