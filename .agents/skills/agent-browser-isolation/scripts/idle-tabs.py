#!/usr/bin/env python3
"""Collapse agent-browser page tabs to a single about:blank.

Keeps Chrome itself running (cookies/SSO stay in the profile). Extra page tabs
are what eat RAM on a long-lived Mini; this is the cleanup for automated tasks.

Only closes type=page targets. Workers, iframes, and Chrome UI targets are left
alone (they die with their parent page).
"""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

IDLE_URLS = frozenset(
    {
        "about:blank",
        "chrome://newtab",
        "chrome://newtab/",
        "chrome://new-tab-page",
        "chrome://new-tab-page/",
        "chrome://new-tab-page/local-ntp.html",
    }
)


def is_idle_url(url: str) -> bool:
    u = (url or "").strip()
    if u in IDLE_URLS:
        return True
    # New-tab chrome URLs sometimes carry a query/hash.
    return u.startswith("chrome://newtab") or u.startswith("chrome://new-tab-page")


def request(base: str, path: str, timeout: float = 5.0, method: str = "GET") -> str:
    url = base.rstrip("/") + path
    req = urllib.request.Request(url, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")



def list_targets(base: str) -> list[dict]:
    raw = request(base, "/json/list")
    data = json.loads(raw)
    if not isinstance(data, list):
        raise SystemExit(f"idle-tabs: unexpected /json/list payload: {raw[:200]!r}")
    return data


def page_tabs(base: str) -> list[dict]:
    return [t for t in list_targets(base) if t.get("type") == "page"]


def open_blank(base: str) -> str | None:
    # Chrome 111+ requires PUT /json/new. Older builds accepted GET.
    path = "/json/new?" + urllib.parse.quote("about:blank", safe=":/")
    last_err: Exception | None = None
    for method in ("PUT", "GET"):
        try:
            raw = request(base, path, method=method)
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                return None
            if isinstance(data, dict):
                return data.get("id")
            return None
        except urllib.error.HTTPError as e:
            last_err = e
            continue
        except urllib.error.URLError as e:
            last_err = e
            continue
    raise SystemExit(f"idle-tabs: could not open about:blank ({last_err})")



def close_tab(base: str, target_id: str) -> None:
    request(base, "/json/close/" + urllib.parse.quote(target_id, safe=""))


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: idle-tabs.py <cdp-http-url>", file=sys.stderr)
        return 2
    base = sys.argv[1]

    pages = page_tabs(base)
    keepers = [t for t in pages if is_idle_url(t.get("url") or "")]
    keep_id = keepers[0].get("id") if keepers else None
    if not keep_id:
        keep_id = open_blank(base)
        pages = page_tabs(base)
        if not keep_id:
            keepers = [t for t in pages if is_idle_url(t.get("url") or "")]
            keep_id = (keepers[0].get("id") if keepers else None) or (
                pages[0].get("id") if pages else None
            )
        if not keep_id:
            print("idle: no page tabs after opening about:blank", file=sys.stderr)
            return 1
    closed = 0
    for tab in pages:
        tid = tab.get("id")
        if not tid or tid == keep_id:
            continue
        url = tab.get("url") or ""
        try:
            close_tab(base, tid)
            closed += 1
            print(f"idle: closed {url}", file=sys.stderr)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            print(f"idle: WARN could not close {tid} ({url}): {e}", file=sys.stderr)

    # Chrome's /json/list can lag; sweep once more so we don't log a false leftover.
    time.sleep(0.15)
    for tab in page_tabs(base):
        tid = tab.get("id")
        if not tid or tid == keep_id:
            continue
        url = tab.get("url") or ""
        try:
            close_tab(base, tid)
            closed += 1
            print(f"idle: closed leftover {url}", file=sys.stderr)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            print(f"idle: WARN could not close leftover {tid} ({url}): {e}", file=sys.stderr)

    remaining = page_tabs(base)
    print(f"idle: kept {len(remaining)} page tab(s), closed {closed}")
    for tab in remaining:
        print(f"idle: remain {tab.get('url')}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
