# Meta-skill-feedback evals

Run evals with the **provider-agnostic-skill-creator** (PAC) harness in dotfiles —
do not fork PAC into this skill. Load:

`~/dev/me/dotfiles/agents/skills/provider-agnostic-skill-creator/SKILL.md`

## Layout

| Path | Purpose |
|------|---------|
| `evals/evals.json` | Prompts + expectations |
| `evals/fixtures/` | Copy-only target skills (never edit in place) |
| `scripts/check_eval_outputs.py` | Deterministic checks for grader |
| `meta-skill-feedback-workspace/` | Iteration runs (gitignored, repo sibling) |

## Quick run (iteration 1)

From agentic-engineering repo root:

```bash
SKILL=./.agents/skills/meta-skill-feedback
PAC=~/dev/me/dotfiles/agents/skills/provider-agnostic-skill-creator
WS=./meta-skill-feedback-workspace/iteration-1
EVAL=bootstrap-minimal
```

1. **Orchestrator** creates `$WS/$EVAL/with_skill/` and `$WS/$EVAL/without_skill/`.
2. **Executor workers** (parallel when possible):
   - **with_skill:** read `$SKILL/SKILL.md`, run prompt from `evals/evals.json`, write deliverables under `{run}/outputs/`, `transcript.md`, `outputs/metrics.json`.
   - **without_skill:** same prompt, no meta-skill-feedback (baseline improvises).
3. **Grader:** run `python3 $SKILL/scripts/check_eval_outputs.py --eval bootstrap-minimal --outputs {run}/outputs` and cite results; fill `grading.json` per PAC `agents/grader.md`.
4. **Aggregate:** `python3 -m scripts.aggregate_benchmark $WS/iteration-1 --skill-name meta-skill-feedback` from PAC directory.
5. **Viewer:** `python3 eval-viewer/generate_review.py $WS/iteration-1 --skill-name meta-skill-feedback --benchmark $WS/iteration-1/benchmark.json --static $WS/iteration-1/review.html`

## Evals (v0)

| id | name | Tests |
|----|------|-------|
| 1 | bootstrap-minimal | feedback/ on bare SKILL.md |
| 2 | bootstrap-wake-shaped | + wake.md cue, adapted README |
| 3 | runtime-quiet | pre-bootstrapped; no new friction file |

## Rules

- Executors **copy** fixtures into `outputs/` — never mutate `evals/fixtures/`.
- Subjective adaptation quality → human review in viewer, not assertions.
- Improving meta-skill-feedback: baseline uses `workspace/skill-snapshot/` per PAC improve mode.
