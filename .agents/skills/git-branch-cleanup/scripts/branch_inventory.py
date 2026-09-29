#!/usr/bin/env python3
"""Print a markdown inventory of every local branch and worktree in a git repo."""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

GIT = shutil.which("git") or "/usr/bin/git"
TICKET_RE = re.compile(r"(?<![A-Za-z0-9])([A-Za-z][A-Za-z0-9]{1,9})-(\d+)(?![0-9])")


@dataclass
class Record:
    branch: str | None
    sha: str
    path: str | None = None
    is_main_clone: bool = False
    prunable: bool = False
    tip_date: str = ""
    subject: str = ""
    upstream: str = ""
    track: str = ""
    dirty_entries: list[str] = field(default_factory=list)
    dirty_files: int = 0
    unique: int | None = None
    behind: int = 0
    first_date: str = ""
    last_date: str = ""
    unique_subjects: list[str] = field(default_factory=list)
    has_remote: bool = False
    unpushed: int = 0
    unpushed_subjects: list[str] = field(default_factory=list)
    reviews: list[dict] = field(default_factory=list)
    not_on_server: bool = False
    tickets: list[dict] = field(default_factory=list)


def run(args: list[str], cwd: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


def git(repo: str, *args: str) -> subprocess.CompletedProcess:
    return run([GIT, "-C", repo, *args])


def git_out(repo: str, *args: str) -> str:
    result = git(repo, *args)
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout.strip()


def warn(message: str) -> None:
    print(f"warning: {message}", file=sys.stderr)


def main_clone(repo: str) -> str:
    common = git_out(repo, "rev-parse", "--path-format=absolute", "--git-common-dir")
    return os.path.dirname(common.rstrip("/"))


def default_ref(repo: str) -> str:
    result = git(repo, "symbolic-ref", "--short", "refs/remotes/origin/HEAD")
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    if git(repo, "rev-parse", "--verify", "--quiet", "origin/main").returncode == 0:
        return "origin/main"
    return "main"


def read_worktrees(repo: str) -> list[dict]:
    blocks, current = [], {}
    for line in git_out(repo, "worktree", "list", "--porcelain").splitlines() + [""]:
        if not line:
            if current:
                blocks.append(current)
            current = {}
            continue
        key, _, value = line.partition(" ")
        current[key] = value or True
    return blocks


def read_branches(repo: str) -> dict[str, dict]:
    fmt = "%00".join(
        [
            "%(refname:short)",
            "%(objectname)",
            "%(committerdate:short)",
            "%(upstream:short)",
            "%(upstream:track)",
            "%(subject)",
        ]
    )
    branches = {}
    for line in git_out(repo, "for-each-ref", f"--format={fmt}", "refs/heads/").splitlines():
        name, sha, date, upstream, track, subject = line.split("\x00")
        branches[name] = {"sha": sha, "date": date, "upstream": upstream, "track": track, "subject": subject}
    return branches


def fill_history(repo: str, record: Record, default: str) -> None:
    if not record.tip_date:
        record.tip_date, record.subject = git_out(repo, "log", "-1", "--format=%cs%x00%s", record.sha).split("\x00", 1)
    if git(repo, "merge-base", default, record.sha).returncode != 0:
        record.unique = None
        return
    record.unique = int(git_out(repo, "rev-list", "--count", f"{default}..{record.sha}"))
    record.behind = int(git_out(repo, "rev-list", "--count", f"{record.sha}..{default}"))
    if record.unique:
        lines = git_out(repo, "log", "--format=%cs%x00%s", f"{default}..{record.sha}").splitlines()
        dates = [line.split("\x00", 1)[0] for line in lines]
        record.last_date, record.first_date = dates[0], dates[-1]
        record.unique_subjects = [line.split("\x00", 1)[1] for line in lines[:50]]


def fill_push(repo: str, record: Record, default: str) -> None:
    if record.unique == 0:
        return
    excluded = [f"^{default}"]
    if record.branch:
        remote = f"refs/remotes/origin/{record.branch}"
        record.has_remote = git(repo, "rev-parse", "--verify", "--quiet", remote).returncode == 0
        if record.has_remote:
            excluded.append(f"^{remote}")
    if record.unique is None and not record.has_remote:
        record.unpushed_subjects = [record.subject]
        return
    lines = git_out(repo, "log", "--format=%s", record.sha, *excluded).splitlines()
    record.unpushed = len(lines)
    record.unpushed_subjects = lines[:20]


def fill_dirty(record: Record) -> None:
    if not record.path or not os.path.isdir(record.path):
        return
    record.dirty_entries = [line.strip() for line in git(record.path, "status", "--porcelain").stdout.splitlines() if line.strip()]
    if record.dirty_entries:
        record.dirty_files = len(git_out(record.path, "status", "--porcelain", "--untracked-files=all").splitlines())


def parse_remote(url: str) -> tuple[str, str] | None:
    match = re.match(r"^(?:ssh://)?[^@/]+@([^:/]+)[:/](.+?)(?:\.git)?/?$", url) or re.match(
        r"^https?://(?:[^@/]+@)?([^/]+)/(.+?)(?:\.git)?/?$", url
    )
    return (match.group(1), match.group(2)) if match else None


class Forge:
    def __init__(self, repo: str):
        self.kind = None
        remote = git(repo, "remote", "get-url", "origin").stdout.strip()
        parsed = parse_remote(remote)
        if not parsed:
            warn("origin remote not recognised; forge not checked")
            return
        host, self.path = parsed
        if "gitlab" in host and shutil.which("glab"):
            self.kind, self.noun = "gitlab", "MR"
        elif "github" in host and shutil.which("gh"):
            self.kind, self.noun = "github", "PR"
        else:
            warn(f"no matching forge CLI for {host}; forge not checked")

    def fill(self, record: Record, default_branch: str) -> None:
        if not self.kind:
            return
        found = {}
        if record.branch and record.branch != default_branch:
            for review in self.by_branch(record.branch):
                found[review["ref"]] = review
        if record.unique != 0:
            reviews, missing = self.by_commit(record.sha)
            record.not_on_server = missing
            for review in reviews:
                found.setdefault(review["ref"], review)
        record.reviews = list(found.values())

    def by_branch(self, branch: str) -> list[dict]:
        if self.kind == "gitlab":
            project = urllib.parse.quote(self.path, safe="")
            source = urllib.parse.quote(branch, safe="")
            result = run(["glab", "api", f"projects/{project}/merge_requests?source_branch={source}&state=all&per_page=20"])
            return self.gitlab_reviews(result)
        result = run(
            ["gh", "pr", "list", "--repo", self.path, "--head", branch, "--state", "all", "--json", "number,state,title,url"]
        )
        if result.returncode != 0:
            return []
        return [
            {"ref": f"#{pr['number']}", "state": pr["state"].lower(), "title": pr["title"], "url": pr["url"]}
            for pr in json.loads(result.stdout or "[]")
        ]

    def by_commit(self, sha: str) -> tuple[list[dict], bool]:
        if self.kind == "gitlab":
            project = urllib.parse.quote(self.path, safe="")
            result = run(["glab", "api", f"projects/{project}/repository/commits/{sha}/merge_requests"])
            if result.returncode != 0 and "404" in (result.stderr + result.stdout):
                return [], True
            return self.gitlab_reviews(result), False
        result = run(["gh", "api", f"repos/{self.path}/commits/{sha}/pulls"])
        if result.returncode != 0:
            return [], "422" in result.stderr or "404" in result.stderr
        reviews = []
        for pr in json.loads(result.stdout or "[]"):
            state = "merged" if pr.get("merged_at") else pr["state"]
            reviews.append({"ref": f"#{pr['number']}", "state": state, "title": pr["title"], "url": pr["html_url"]})
        return reviews, False

    @staticmethod
    def gitlab_reviews(result: subprocess.CompletedProcess) -> list[dict]:
        if result.returncode != 0:
            return []
        try:
            data = json.loads(result.stdout or "[]")
        except json.JSONDecodeError:
            return []
        states = {"opened": "open"}
        return [
            {"ref": f"!{mr['iid']}", "state": states.get(mr["state"], mr["state"]), "title": mr["title"], "url": mr["web_url"]}
            for mr in data
            if isinstance(mr, dict)
        ]


class Linear:
    def __init__(self):
        self.keys, self.url_key = set(), ""
        if not shutil.which("linear"):
            return
        result = run(["linear", "api", "query { organization { urlKey } teams(first: 250) { nodes { key } } }"])
        if result.returncode != 0:
            warn("linear api failed; ticket links skipped")
            return
        data = json.loads(result.stdout).get("data") or {}
        self.url_key = (data.get("organization") or {}).get("urlKey", "")
        self.keys = {team["key"].upper() for team in (data.get("teams") or {}).get("nodes", [])}

    def ids_for(self, record: Record) -> list[str]:
        if not self.keys:
            return []
        sources = [record.branch or ""] + (record.unique_subjects if record.unique else [record.subject] if record.unique is None else [])
        ids = []
        for text in sources:
            for key, number in TICKET_RE.findall(text):
                ticket = f"{key.upper()}-{number}"
                if key.upper() in self.keys and ticket not in ids:
                    ids.append(ticket)
        return ids

    def lookup(self, ids: list[str]) -> dict[str, dict]:
        if not ids:
            return {}
        fields = " ".join(f'i{n}: issue(id: "{ticket}") {{ identifier title url }}' for n, ticket in enumerate(ids))
        result = run(["linear", "api", f"query {{ {fields} }}"])
        found = {}
        if result.returncode == 0 or result.stdout:
            try:
                data = json.loads(result.stdout).get("data") or {}
            except json.JSONDecodeError:
                data = {}
            for issue in data.values():
                if issue:
                    found[issue["identifier"]] = issue
        for ticket in ids:
            if ticket not in found and self.url_key:
                found[ticket] = {"identifier": ticket, "title": "", "url": f"https://linear.app/{self.url_key}/issue/{ticket}"}
        return found


def plural(count: int, noun: str) -> str:
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


def sentence(text: str) -> str:
    return text[:1].upper() + text[1:]


def summarize(limit: str, items: list[str]) -> str:
    return "{{summarize in " + limit + ": " + " | ".join(items) + "}}"


def date_span(first: str, last: str) -> str:
    if first == last:
        return f"on {first}"
    return f"from {first} to {last[5:] if first[:4] == last[:4] else last}"


def commits_text(record: Record, default: str) -> str:
    if record.unique is None:
        return f"no shared history with {default}, last commit {record.tip_date}."
    trunk = sentence(default.split("/")[-1])
    moved = f"{trunk} has moved {plural(record.behind, 'commit')} since." if record.behind else f"{trunk} has not moved since."
    if record.unique == 0:
        return f"already in {default}. {moved}"
    span = date_span(record.first_date, record.last_date)
    return f"{plural(record.unique, 'commit')} {span}, from the shared base with {default}. {moved}"


def unpushed_text(record: Record, forge: Forge) -> str:
    if record.unique == 0:
        return ""
    summary = summarize("1 sentence", record.unpushed_subjects) if record.unpushed_subjects else ""
    if not record.branch:
        text = f"{plural(record.unpushed, 'commit')} not on any branch. {summary}" if record.not_on_server else "on the server."
    elif not record.has_remote:
        text = (f"{plural(record.unpushed, 'commit')}, never pushed." if record.unpushed else "never pushed.") + f" {summary}"
    elif record.unpushed:
        text = f"{plural(record.unpushed, 'commit')}. {summary}"
    else:
        text = "none."
    if "gone" in record.track:
        text += " Upstream is gone."
    if not forge.kind:
        text += " Forge not checked."
    elif record.has_remote and not record.reviews:
        text += f" No {forge.noun}."
    return text.strip()


def uncommitted_text(record: Record) -> str:
    if record.prunable or not os.path.isdir(record.path):
        return "worktree directory is missing, prunable."
    if not record.dirty_entries:
        return "none."
    count = len(record.dirty_entries)
    head = f"{count} {'entry' if count == 1 else 'entries'}, {plural(record.dirty_files, 'file')}"
    return summarize("2 sentences", [head, *record.dirty_entries[:12]])


def label(record: Record, root: str) -> str:
    if record.is_main_clone:
        return f"{os.path.basename(root)}/"
    if record.path:
        rel = os.path.relpath(record.path, root)
        return rel if not rel.startswith("..") else record.path
    return record.branch or record.sha[:9]


def link_text(text: str) -> str:
    return text.replace("[", "\\[").replace("]", "\\]")


def link_lines(record: Record, indent: str) -> list[str]:
    reviews = [
        f"{indent}- [{review['ref']} · {review['state']} · {link_text(review['title'])}]({review['url']})"
        for review in record.reviews
    ]
    tickets = [
        f"{indent}- [{ticket['identifier']}"
        + (f" · {link_text(ticket['title'])}" if ticket["title"] else "")
        + f"]({ticket['url']})"
        for ticket in record.tickets
    ]
    return reviews + tickets


def render(records: list[Record], root: str, default: str, forge: Forge) -> str:
    out, loose = [], []
    for record in records:
        if not record.path:
            loose.append(record)
            continue
        out.append(f"- `{label(record, root)}` · `{record.branch or 'detached ' + record.sha[:9]}`")
        out.append(f"  - Commits: {commits_text(record, default)}")
        unpushed = unpushed_text(record, forge)
        if unpushed:
            out.append(f"  - Unpushed: {unpushed}")
        out.append(f"  - Uncommitted: {uncommitted_text(record)}")
        out.extend(link_lines(record, "  "))
    if loose:
        out.append("- No worktree")
        for record in loose:
            parts = [commits_text(record, default)]
            unpushed = unpushed_text(record, forge)
            if unpushed:
                parts.append(sentence(unpushed))
            out.append(f"  - `{record.branch}`: " + " ".join(parts))
            out.extend(link_lines(record, "    "))
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", nargs="?", default=".", help="any path inside the repo")
    parser.add_argument("--no-fetch", action="store_true", help="skip git fetch --prune")
    args = parser.parse_args()

    root = main_clone(os.path.abspath(args.repo))
    if not args.no_fetch and git(root, "fetch", "--prune").returncode != 0:
        warn("git fetch --prune failed; remote state may be stale")
    default = default_ref(root)
    default_branch = default.split("/", 1)[-1]
    branches = read_branches(root)

    records, seen = [], set()
    for index, block in enumerate(read_worktrees(root)):
        if "bare" in block:
            continue
        branch = block["branch"].removeprefix("refs/heads/") if "branch" in block else None
        info = branches.get(branch, {}) if branch else {}
        record = Record(
            branch=branch,
            sha=block["HEAD"],
            path=block["worktree"],
            is_main_clone=index == 0,
            prunable="prunable" in block,
            tip_date=info.get("date", ""),
            subject=info.get("subject", ""),
            upstream=info.get("upstream", ""),
            track=info.get("track", ""),
        )
        records.append(record)
        if branch:
            seen.add(branch)
    for name, info in branches.items():
        if name not in seen:
            records.append(
                Record(
                    branch=name,
                    sha=info["sha"],
                    tip_date=info["date"],
                    subject=info["subject"],
                    upstream=info["upstream"],
                    track=info["track"],
                )
            )

    forge, linear = Forge(root), Linear()

    def enrich(record: Record) -> None:
        fill_history(root, record, default)
        fill_push(root, record, default)
        fill_dirty(record)
        forge.fill(record, default_branch)

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(enrich, records))

    wanted = {record.sha: linear.ids_for(record) for record in records}
    issues = linear.lookup(sorted({ticket for ids in wanted.values() for ticket in ids}))
    for record in records:
        record.tickets = [issues[ticket] for ticket in wanted[record.sha] if ticket in issues]

    head = [record for record in records if record.is_main_clone]
    worktrees = sorted(
        (record for record in records if record.path and not record.is_main_clone),
        key=lambda record: record.last_date or record.tip_date,
        reverse=True,
    )
    loose = sorted((record for record in records if not record.path), key=lambda record: record.tip_date, reverse=True)
    print(render(head + worktrees + loose, root, default, forge))
    return 0


if __name__ == "__main__":
    sys.exit(main())
