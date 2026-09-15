---
reviewed: 2026-08-09
---

# 2026-08-06 — local · Cursor / Opus 4.8, morning FVD login

> Migrated 2026-09-15 from agent-memories/skills-feedback/agent-browser-isolation.md.

## Context

Working in "Driving the user's MAIN Chrome instead", verifying which daemon
was attached to the user's main Chrome.

## What happened

Acknowledge that multiple daemons may already be attached to the user's main
Chrome; verify by tab-set (the skill already says this) and note you can
reuse a descriptive existing handle (e.g. `cody-main`) bound to that Chrome
rather than minting one.

Evidence: `--doctor` showed 4 daemons (`agent-fvd`, `default`, `cody-main`,
`probe-default`); `default` and `cody-main` both saw the same 75 real tabs
(the main Chrome), so tab-set verification disambiguated cleanly.

Severity: doc-gap (minor).

## Resolution

- status: applied 2026-08-09 — same section: reuse existing main-Chrome handle
  after tab-set verify

## Votes

- **2026-08-06T0001** — local · opened

## Agent comments

_(none yet)_
