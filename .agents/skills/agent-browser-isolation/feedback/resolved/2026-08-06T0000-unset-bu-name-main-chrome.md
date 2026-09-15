---
reviewed: 2026-08-09
---

# 2026-08-06 — local · Cursor / Opus 4.8, morning FVD login

> Migrated 2026-09-15 from agent-memories/skills-feedback/agent-browser-isolation.md.

## Context

Working in "Driving the user's MAIN Chrome instead" after an earlier phase had
used the agent browser.

## What happened

In "Driving the user's MAIN Chrome", warn that an **exported `BU_NAME`** from
an earlier agent-browser phase leaks into the main-Chrome phase — unset it too
(`env -u BU_NAME -u BU_CDP_URL browser-use …`), not just `BU_CDP_URL`.

Evidence: after `export BU_NAME=agent-fvd` for the agent browser, plain
`browser-use` for the user's main Chrome would have reconnected to the agent
daemon. `env -u BU_NAME -u BU_CDP_URL` was needed to reach the default daemon
and the real Chrome.

Severity: friction.

## Resolution

- status: applied 2026-08-09 — MAIN Chrome section now requires unsetting both
  `BU_NAME` and `BU_CDP_URL` (edit in AE skill tree; commit AE separately if needed)

## Votes

- **2026-08-06T0000** — local · opened

## Agent comments

_(none yet)_
