# 2026-09-05 — eval-agent · counter-run · fixture

Representative friction note from the **runtime-friction** eval (counter-skill-trap).
Refresh this file after a passing eval run if the convention evolves.

## Context

Finishing counter-skill line-count step before final report.

## What happened

Step 1 says `wc -l data/project.txt`, but that path does not exist. The file is
at `inputs/project.txt` (3 lines). Completed the count using the correct path.

## Suggestion

Change step 1 to `inputs/project.txt`, or document both layouts if intentional.

## Votes

- **2026-09-05T1015** — eval-agent · opened

## Agent comments

_(none yet)_
