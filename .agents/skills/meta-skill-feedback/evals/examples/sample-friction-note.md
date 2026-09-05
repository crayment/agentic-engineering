# 2026-09-05 — eval-agent · counter-run · fixture

From iteration-2 **runtime-friction** eval (counter-skill-trap). Refresh after
a better passing run if the convention evolves.

## Context

Finishing counter-skill-trap line-count step before final report.

## What happened

Step 1 says `wc -l data/project.txt`, but that path does not exist. The file is
at `inputs/project.txt` (3 lines). Completed the count using the correct path.

## Suggestion

Change step 1 to `inputs/project.txt`.

## Votes

- **2026-09-05T1028** — eval-agent · opened

## Agent comments

_(none yet)_
