#!/usr/bin/env bash
# abu — run browser-use against the shared *agent browser*, never the user's Chrome.
#
# Why this exists: browser-use silently falls back to the default daemon (which
# drives the USER'S REAL CHROME) whenever BU_CDP_URL is unset — and a shell
# `export` can drop between calls, turns, or resumes. This wrapper removes that
# footgun structurally: it (re)ensures the agent browser on every call and sets
# BU_CDP_URL itself from the live endpoint, so you can never accidentally target
# the wrong browser. It also fails loudly if BU_NAME is missing.
#
# Usage (identical to browser-use, heredocs included):
#   export BU_NAME=agent-otter        # once: your short, unique daemon/tab handle
#   abu.sh <<'PY'
#   print(page_info())
#   PY
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# BU_NAME is required, never defaulted: a shared default would let parallel
# agents clobber each other's current tab (see SKILL.md "Parallel agents").
if [[ -z "${BU_NAME:-}" ]]; then
  cat >&2 <<'MSG'
abu: BU_NAME is not set. Pick a short, unique handle first, e.g.
       export BU_NAME=agent-otter
     One daemon/tab lives per BU_NAME; a unique name keeps parallel agents apart.
MSG
  exit 2
fi

# The critical safety line: always resolve the agent browser's live endpoint, so
# an absent/dropped BU_CDP_URL can never fall back to the user's real Chrome.
BU_CDP_URL="$("${SCRIPT_DIR}/agent-browser.sh" ensure)"
export BU_CDP_URL BU_NAME

echo "abu: BU_NAME=${BU_NAME} BU_CDP_URL=${BU_CDP_URL} (agent browser)" >&2

exec browser-use "$@"
