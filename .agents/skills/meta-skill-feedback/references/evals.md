# Meta-skill-feedback evals

Run evals with the **provider-agnostic-skill-creator** (PAC) harness in dotfiles —
do not fork PAC into this skill. Load:

`~/dev/me/dotfiles/agents/skills/provider-agnostic-skill-creator/SKILL.md`

## Layout

| Path | Purpose |
|------|---------|
| `evals/evals.json` | Prompts + expectations |
| `evals/overview.html` | Human-readable: skill purpose, what evals test, v0 results |
| `evals/fixtures/counter-skill*` | Fake mini-skills (copy-only) |
| `evals/examples/` | Sample friction notes from passing runs (linked by fixtures) |
| `scripts/check_eval_outputs.py` | Deterministic checks for grader |
| `meta-skill-feedback-workspace/` | Iteration runs (gitignored, repo sibling) |

## Quick run

From agentic-engineering repo root:

```bash
SKILL=./.agents/skills/meta-skill-feedback
PAC=~/dev/me/dotfiles/agents/skills/provider-agnostic-skill-creator
WS=./meta-skill-feedback-workspace/iteration-1
EVAL=eval-bootstrap-counter-skill
```

PAC expects eval directories named `eval-*`.

## Evals (v1)

See **[evals/overview.html](../evals/overview.html)** for a readable summary.

| id | name | Tests |
|----|------|-------|
| 1 | bootstrap-counter-skill | Install feedback/ on bare counter-skill |
| 2 | runtime-quiet | Routine run → no note |
| 3 | runtime-friction | Wrong path → new note with Votes format |
| 4 | runtime-vote | Same bug open → +1 on existing note, no duplicate file |
| 5 | runtime-stuck | Script fails → friction note, don't patch SKILL.md |

My Machines wake contracts are **not** part of this skill or its evals.

## Rules

- Executors **copy** fixtures into `outputs/` — never mutate `evals/fixtures/`.
- Subjective note quality → human review in viewer, not assertions.
- After a great runtime-friction run, refresh `evals/examples/sample-friction-note.md`.
