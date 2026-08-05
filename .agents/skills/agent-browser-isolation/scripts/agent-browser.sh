#!/usr/bin/env bash
# The "agent browser": one dedicated Chrome, isolated from your main browser,
# that every agent shares via a fixed remote-debugging port + persistent profile.
# Idempotent: launches Chrome only if it isn't already listening on the port.
#
# Usage:
#   agent-browser.sh ensure [url]   # launch if needed (default), then print the CDP url
#   agent-browser.sh status         # report whether it's running
#   agent-browser.sh restart [url]  # kill this profile's Chrome and relaunch
#
# Attach browser-use to it with the abu.sh wrapper (recommended — see SKILL.md):
#   export BU_NAME=agent-otter    # once; then run:  abu.sh <<'PY' ... PY

set -euo pipefail

PORT="${AGENT_BROWSER_PORT:-9333}"
PROFILE="${AGENT_BROWSER_PROFILE:-$HOME/.agent-browser}"
CHROME="${AGENT_BROWSER_CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
LOG="${AGENT_BROWSER_LOG:-/tmp/agent-browser.log}"
CDP_URL="http://127.0.0.1:${PORT}"

is_running() {
  # Probe the DevTools endpoint, not a bare TCP connect, so a non-Chrome process
  # bound to the port doesn't masquerade as our browser. Retry a few times: a
  # single slow probe must NOT read as "dead" — that would trigger launch() ->
  # Singleton removal -> a relaunch that wipes a live browser's tabs.
  local i
  for i in 1 2 3; do
    curl -fsS --max-time 3 "${CDP_URL}/json/version" >/dev/null 2>&1 && return 0
    sleep 0.3
  done
  return 1
}

is_ours() {
  # Is the Chrome actually LISTENing on our port using our dedicated profile? So
  # a different Chrome squatting on the port isn't mistaken for the agent browser
  # (the isolation the skill promises). lsof finds the real listener; `ps -ww`
  # avoids macOS command-line truncation; grep -F keeps profile paths regex-safe.
  local lpid
  lpid="$(lsof -tiTCP:"${PORT}" -sTCP:LISTEN -n -P 2>/dev/null | head -1)"
  [ -n "${lpid}" ] || return 1
  ps -ww -o command= -p "${lpid}" 2>/dev/null | grep -qF -- "--user-data-dir=${PROFILE}"
}

launch() {
  local url="${1:-about:blank}"
  # Race/false-negative guard: if it's actually up, do NOT relaunch — removing the
  # Singleton lock + relaunching would wipe a live browser's tabs.
  if is_running; then
    echo "agent browser already running on port ${PORT} (launch skipped)" >&2
    return 0
  fi
  # A stale Singleton lock from a crashed session blocks relaunch on a persistent
  # profile. Only safe to remove when nothing is actually running on the port.
  rm -f "${PROFILE}/Singleton"* 2>/dev/null || true
  mkdir -p "${PROFILE}"
  # Anti-throttling flags keep every tab running full-speed even when backgrounded
  # (Chrome otherwise throttles timers / pauses rAF / sets document.hidden), so
  # parallel agents each driving their own tab don't stall each other.
  local flags=(
    --remote-debugging-port="${PORT}"
    --user-data-dir="${PROFILE}"
    --no-first-run
    --no-default-browser-check
    --disable-background-timer-throttling
    --disable-backgrounding-occluded-windows
    --disable-renderer-backgrounding
    --new-window "${url}"
  )
  if [[ -z "${AGENT_BROWSER_CHROME:-}" ]] && command -v open >/dev/null 2>&1; then
    # macOS: launch via `open` so Chrome is handed to LaunchServices and becomes a
    # child of launchd (PPID 1), NOT of this shell. It therefore SURVIVES the
    # agent/shell that launched it dying — no launchd plist or holder job needed.
    open -na "${AGENT_BROWSER_APP:-Google Chrome}" --args "${flags[@]}"
  elif command -v setsid >/dev/null 2>&1; then
    # Fallback (explicit CHROME binary / non-macOS): new session so it's not in the
    # launching shell's process group.
    setsid "${CHROME}" "${flags[@]}" >"${LOG}" 2>&1 < /dev/null &
  else
    nohup "${CHROME}" "${flags[@]}" >"${LOG}" 2>&1 < /dev/null &
    disown 2>/dev/null || true
  fi
  # Wait for the DevTools endpoint to come up.
  for _ in $(seq 1 30); do
    if is_running; then
      echo "agent browser up (port ${PORT}, profile ${PROFILE})" >&2
      return 0
    fi
    sleep 0.5
  done
  echo "agent browser did not come up on port ${PORT} within 15s -- check ${LOG}" >&2
  return 1
}

cmd="${1:-ensure}"
case "${cmd}" in
  ensure)
    if is_running; then
      if is_ours; then
        echo "agent browser already running on port ${PORT}" >&2
      else
        # Don't silently adopt a foreign Chrome (was the whole isolation promise),
        # but don't hard-fail either — the port may be held by a browser other
        # agents are actively using. Surface it loudly and continue.
        echo "WARNING: port ${PORT} is held by a Chrome that is NOT the agent profile (${PROFILE}) — using it anyway. For a truly dedicated profile, free the port or set AGENT_BROWSER_PORT." >&2
      fi
    else
      launch "${2:-about:blank}"
    fi
    echo "${CDP_URL}"
    ;;
  status)
    if is_running && is_ours; then
      echo "running: ${CDP_URL} (profile ${PROFILE})"
    elif is_running; then
      echo "running: ${CDP_URL} but on a DIFFERENT profile (not ${PROFILE}) — see 'ensure' warning"
    else
      echo "not running (port ${PORT})"
      exit 1
    fi
    ;;
  restart)
    pkill -f -- "--user-data-dir=${PROFILE}" 2>/dev/null || true
    sleep 1
    launch "${2:-about:blank}"
    echo "${CDP_URL}"
    ;;
  *)
    echo "usage: agent-browser.sh {ensure [url]|status|restart [url]}" >&2
    exit 2
    ;;
esac
