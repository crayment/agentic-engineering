---
name: agent-browser-isolation
description: "Use a dedicated, always-available second Chrome (the \"agent browser\") for all local browser automation instead of driving the user's real Chrome. Covers launching/keeping it alive on a fixed debug port + persistent profile, attaching browser-use to it via BU_CDP_URL, and owning a single tab by its stable targetId. Use whenever doing local browser-use / CDP work where you want isolation from the user's own browser (screenshots, testing a local app, clicking through a web UI)."
---

# The Agent Browser

One dedicated Chrome on this machine that **every agent shares** for browser
automation — separate from the user's main Chrome. Drive it with the
`browser-use` skill (that skill owns all CDP mechanics; this one only covers
*which* browser to attach to and how to keep it healthy).

## Prerequisites (one-time)

- Install the CLI once: `brew install browser-use browser-harness` (or follow
  the `browser-use` skill's install pointer). Afterward `browser-use` is on PATH.
- You do **not** need Chrome's `chrome://inspect` "Allow remote debugging" toggle
  for the agent browser — see "No permission popup / lockdown" below. That toggle
  only matters when attaching to your *normal* Chrome.

## Why a separate browser

Attaching `browser-use` to the user's normal Chrome is fragile. A dedicated
browser on a non-default profile fixes all of it:

- **No permission popup / lockdown.** A non-default profile with
  `--remote-debugging-port` sidesteps Chrome's "Allow remote debugging" dialog
  and the default-profile lockdown. `browser-use`'s own source calls this out.
- **No tab drift.** Driving the user's real Chrome means dozens of their tabs
  and OS focus events can silently steal the "current tab". The agent browser
  has only the tabs agents opened.
- **Persistent login.** The profile keeps cookies/SSO between sessions, so
  SSO logins survive across agents and restarts.
- **No surprise cloud spend.** Setting `BU_CDP_URL` blocks `browser-use` from
  auto-spawning a billed cloud browser.

## Defaults

| Thing | Value | Override env |
|---|---|---|
| Debug port | `9333` | `AGENT_BROWSER_PORT` |
| Profile dir | `~/.agent-browser` | `AGENT_BROWSER_PROFILE` |
| CDP endpoint | `http://127.0.0.1:9333` | derived from debug port |
| Chrome binary | macOS Google Chrome | `AGENT_BROWSER_CHROME` |
| Launch log | `/tmp/agent-browser.log` | `AGENT_BROWSER_LOG` |
| `BU_NAME` | you pick a short, memorable, unique one (see "Attach") | — |

The Chrome-binary default is the macOS path; on Linux/Windows set
`AGENT_BROWSER_CHROME` to your Chrome/Chromium binary.

## Running the helper scripts

The helpers live in **this skill's own `scripts/` directory** — invoke them by
the absolute path this skill was loaded from (the skill system hands you that
path), so it works no matter where the skill lives: a user-level dir, a
spotlighted worktree, or merged `main`. The examples below abbreviate that path
as `$SKILL`; set it once to this skill's directory:

```bash
export SKILL="<the absolute path this skill's SKILL.md was loaded from>"
```

If the path wasn't handed to you, it's simply the directory that contains the
SKILL.md you're reading now (the one holding `scripts/`). `abu.sh` finds
`agent-browser.sh` relative to itself, so only `$SKILL` matters.

## Start it (idempotent)

`scripts/agent-browser.sh` launches Chrome only if it isn't already up, clears
a stale `Singleton` lock left by a crash, waits for the DevTools endpoint, and
prints the CDP url:

```bash
"$SKILL"/scripts/agent-browser.sh ensure          # launch if needed, print url
"$SKILL"/scripts/agent-browser.sh status          # is it running?
"$SKILL"/scripts/agent-browser.sh restart         # kill this profile's Chrome + relaunch
```

`ensure` is safe to call every time — if the browser is already running it does
nothing but print the url. It **keeps the window open**: never `close_tab` the
last tab or quit Chrome when you finish; just leave it running for the next
agent.

If some *other* Chrome is already listening on the port with a different profile,
`ensure`/`status` print a loud **WARNING** (and still return the url, so shared
setups keep working) — that means you're not on the dedicated profile. Free the
port or set `AGENT_BROWSER_PORT` if you need true isolation.

## Attach browser-use to it

Point `browser-use` at the agent browser with two env vars: `BU_CDP_URL` (the
agent browser's HTTP DevTools endpoint) and `BU_NAME` (your daemon/tab handle).

**Set both on *every* `browser-use` call, inline — do not rely on a prior
`export` surviving.** A shell `export` can silently drop between calls, turns, or
resumes, and when it does `browser-use` does **not** error — it falls back to the
default daemon, which drives the **user's real Chrome** (the worst outcome: wrong
browser, their tabs, their focus). Inlining both vars on the same line as the
command makes the correct browser impossible to miss.

**Recommended: skip to the `abu.sh` wrapper below** — it eliminates this footgun.
The raw form here just shows what it does under the hood.

```bash
# One-time bootstrap, just to bring the browser up and see the endpoint:
export BU_NAME="agent-otter"   # YOU pick this once — see below
export BU_CDP_URL="$("$SKILL"/scripts/agent-browser.sh ensure)"

# Then prefix EVERY call with both vars (belt-and-suspenders against export loss):
BU_NAME="agent-otter" BU_CDP_URL="http://127.0.0.1:9333" browser-use <<'PY'
print(page_info())
PY
```

### Easiest: the `abu.sh` wrapper (recommended)

Typing both vars on every call is easy to forget, and inlining a *static*
`BU_CDP_URL` still breaks if the browser comes up on a different port or isn't
running yet. `scripts/abu.sh` removes the footgun structurally: it re-runs
`ensure` on every call and sets `BU_CDP_URL` from the **live** endpoint itself,
so a dropped/absent var can never fall back to the user's real Chrome. It refuses
to run if `BU_NAME` is unset (a shared default would let parallel agents clobber
each other's tab), so you set that **once** and then just call `abu.sh`:

```bash
export BU_NAME="agent-otter"   # once — your short, unique daemon/tab handle
"$SKILL"/scripts/abu.sh <<'PY'
print(page_info())
PY
```

It's a drop-in for `browser-use` (same args, same heredoc stdin) and prints a
one-line `abu: BU_NAME=… BU_CDP_URL=… (agent browser)` banner to stderr so you
can see which browser you hit. The raw inline form above still works if you'd
rather not use the wrapper.

**Preflight guard:** under `abu.sh`, the thing to check is the **`abu:` banner on
stderr** — it prints the live `BU_NAME`/`BU_CDP_URL` the wrapper actually used.
Your *own* shell's `$BU_CDP_URL` stays empty under `abu.sh` (the wrapper sets it
only inside its subprocess), so **don't** test that — an empty parent-shell value
is expected, not a problem. If the banner is missing, or `page_info()`/
`list_tabs()` shows a tab or URL you didn't open, stop and re-run
`agent-browser.sh ensure` before continuing.

- **Pick your own `BU_NAME` — short and memorable, and unique to you.** It's your
  handle on your own daemon and tab: `browser-use` runs one daemon per `BU_NAME`,
  so a name you reuse reconnects you to the same tab, and a name no other agent
  is using keeps you from colliding with them. `agent-otter`, `agent-hn-scrape` —
  anything you'll remember. Avoid long random UUIDs; they're just harder to recall.
- **Remember your `BU_NAME` and reuse it the whole session** — reconnecting with
  the same name returns you to your same daemon and tab. A `cdp_disconnected` or
  failing `current_tab()` means you lost the connection — re-attach before opening
  a new tab.
- `BU_CDP_URL` is the **HTTP** DevTools endpoint (`http://127.0.0.1:9333`); the
  daemon resolves it to a WebSocket itself. Don't hand it a `ws://` url.
- If you use the raw inline form (not `abu.sh`), keep both vars set for the whole
  session and don't mix the agent endpoint with the default daemon in the same
  shell.
- If it can't connect, the browser probably isn't running — run
  `agent-browser.sh ensure` (or `restart`) and retry.

## Own one tab by its id (don't spawn new tabs)

`new_tab(url)` returns a **stable `targetId`** (a GUID). That id does **not**
change as the tab navigates — verified across same-site *and* cross-origin
navigations. It only changes if the tab is closed or crashes. So the workflow
is: open one tab, remember its id, and re-attach by that id for the rest of the
session instead of opening a new tab each turn.

**Switch only when you're not already on your tab.** `switch_tab` (and
`new_tab`) call `Target.activateTarget`, which raises Chrome to the macOS
foreground — a focus grab the user feels. Your daemon *keeps* your tab as its
current target across calls, so re-switching every turn is both redundant and
annoying. Check first with `current_tab()` (a read — no focus steal) and switch
only on a mismatch:

```python
TAB = new_tab("https://example.com/")    # returns a targetId GUID — WRITE IT DOWN
                                         # (this one raise is unavoidable + expected)
# ... any later turn, in a SEPARATE browser-use/abu.sh call:
TAB = "5F4D96A2...your saved id..."       # paste the literal — see note below
if current_tab().get("targetId") != TAB: # cheap read, no focus steal
    switch_tab(TAB)                       # only now does Chrome come to the front
goto_url("https://example.com/other")     # same tab, id unchanged
```

- **The daemon persists your tab; your Python does not.** Each `browser-use`/
  `abu.sh` call is a *separate process*, so Python variables (like `TAB`) do
  **not** carry over — a later call referencing `TAB` without redefining it
  raises `NameError`. What *does* persist per `BU_NAME` is the daemon's own
  "current tab" pointer. So record the `targetId` string yourself and paste it
  as a literal into each new call (or recover it with `current_tab()`/
  `list_tabs()`); don't assume the variable survives.
- Actions that **don't** steal focus: `goto_url`, `click_at_xy`, `type_text`,
  `capture_screenshot`, `js`, `page_info`, `current_tab`, `wait_for_load`. Only
  `switch_tab`/`new_tab` do (via `Target.activateTarget`) — minimize them.
- `switch_tab` also stamps a 🐴 into the tab title so the user can see which tab
  the agent controls.
- Before opening a tab, reuse an existing one you already own; only `new_tab`
  when you have no live tab id. If `switch_tab(TAB)` fails, the tab was closed —
  open a fresh one and store the new id. (For a brand-new `BU_NAME`, `current_tab()`
  may point at Chrome's default `about:blank` window — treat that as not-yours and
  `new_tab` your own rather than adopting it.)
- Recover a lost id with `list_tabs()` (each entry has `targetId` + `url`) or
  `current_tab()`.

## Parallel agents (one browser, many drivers)

Multiple agents **share the one agent browser** — that's how they all inherit the
same login (one sign-in, shared profile). Concurrency is safe as long as each
agent picked a **different `BU_NAME`**: `browser-use` runs **one daemon per
`BU_NAME`**, and each daemon tracks a single "current tab". Two agents sharing one
`BU_NAME` would clobber each other's active tab (verified: shared `BU_NAME` leaks
one agent's page into the other's reads). Distinct `BU_NAME`s = separate
daemons/CDP sessions on the same Chrome, each owning its own tab; CDP routes input
per-session, not by which tab is foreground, so the tabs don't fight.

Rules for concurrent agents:

- **One tab each, owned by id.** Open exactly one tab, remember its `targetId`,
  and only ever `switch_tab` to *your* id. Reading `current_tab()` to compare is
  fine, but never *adopt* whatever tab happens to be current (or `list_tabs()[0]`)
  as yours — it may be another agent's.
- **Don't close other tabs or quit Chrome.** Only `close_tab(YOUR_TAB)` at most;
  leave everyone else's tabs alone.
- Background-tab throttling is already disabled by the launch flags, so your tab
  keeps running full-speed even while another agent's tab is foregrounded.

### Spawning a sub-agent that uses the browser

Same rule — just give the child a different `BU_NAME` than yours. Easiest is to
inject a literal one at launch so it doesn't have to invent it (and a literal
avoids CLI security hooks that can block shell `$`-expansion in the child's
commands):

```bash
BU_NAME="agent-heron" BU_CDP_URL="http://127.0.0.1:9333" \
  <your-agent-launch-command>
```

The child inherits both env vars, so `browser-use` just works there. Make sure the
name you give it differs from your own and any sibling's. (The `:9333` literal
assumes the default port — if you overrode `AGENT_BROWSER_PORT`, inject the
endpoint that `"$SKILL"/scripts/agent-browser.sh ensure` printed instead.)

## Keeping it alive

`ensure` is idempotent — it won't relaunch a browser that's already up, so open
tabs are preserved across calls. And `launch()` starts Chrome **detached from the
calling shell**: on macOS it uses `open`, so Chrome becomes a child of launchd
(PPID 1), not of your shell. That means it **survives the agent/shell that
launched it dying** — no holder job and no launchd plist required. It stays up
until something quits it or you reboot.

- **Why this matters:** many agents run shell commands in a sandbox that reaps
  the whole process group when the command ends — a plain `&`-backgrounded Chrome
  (even with `nohup`/`disown`) dies with it, so every `ensure` would relaunch with
  a fresh PID and no tabs. Launching via `open` (PPID 1) sidesteps that entirely.
- **Verify detachment:** the listener's parent should be launchd —
  `ps -o ppid= -p "$(lsof -tiTCP:${AGENT_BROWSER_PORT:-9333} -sTCP:LISTEN -nP | head -1)"` → `1`.
- **Only if you still see it die** (a stricter sandbox, or the non-`open` fallback
  path): keep a background holder job alive (`agent-browser.sh ensure && sleep
  <long>`), or add a launchd LaunchAgent if you *also* want it auto-started on boot.
