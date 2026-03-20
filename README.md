# Agentic Engineering Skills

Reusable agent skills I've built and battle-tested in real engineering workflows. Most work anywhere; some are designed specifically for [Birdhouse](https://github.com/Birdhouse-Labs/birdhouse), a multi-agent orchestration platform. Each skill is a self-contained `SKILL.md` that an AI agent can load on demand — opinionated workflows, not generic prompts.

## Install

```bash
# Will walk you through selecting skills and install location
npx skills add crayment/agentic-engineering
```

## What's Here

```
.agents/skills/
├── git-branch-cleanup/         # Inspect + plan + approve before deleting anything
├── git-commit-messages/        # Subject-first, scannable commit messages
├── git-merge-conflict-resolution/  # Understand both sides before resolving
├── git-release-notes-generation/  # Branch diff → customer-facing + technical notes
├── git-spotlight/              # Point main clone at a worktree HEAD for review
├── git-worktree/               # Parallel branches without touching main workspace
├── github-ci-failure-diagnosis/   # 3-step gh CLI workflow: status → detail → logs
├── github-pr-feedback/         # Parallel investigation → triage → serial execution
├── github-pr-review/           # Multi-agent review + one batched GitHub submission
├── github-pull-request-creation/  # Heredoc-safe gh pr create with structured bodies
├── github-reply/               # Threaded PR replies via the GitHub /replies endpoint
├── slack/                      # Send messages, DMs, thread replies via Slack API
└── software-principles/        # Foundational engineering principles for agent context
```

## Skills Worth Starting With

### PR Review Pipeline

Two skills that cover the full review lifecycle end-to-end.

**`github-pr-review`** — Spawn a team of agents to investigate different tracks in parallel, cross-validate candidate feedback, then submit one batched GitHub review. Catches the real problems without the noise.

**`github-pr-feedback`** — When a PR comes back with review comments, this skill picks up where the review left off. Investigate threads in parallel, classify each as `strengthened / weakened / invalidated`, then address approved items one at a time. Includes the exact GraphQL query to fetch unresolved threads.

### Parallel Worktree Workflow

Two skills designed to work together for agent-parallel development.

**`git-worktree`** — Each agent gets its own isolated worktree so parallel work never steps on itself. The skill enforces the golden rule: all operations happen inside the worktree, never in the main clone.

**`git-spotlight`** — When an agent finishes a chunk of work and you want to test it, Spotlight syncs the main clone to that agent's worktree HEAD in seconds. Jump between agents' work without disturbing anyone's branch. The pattern: agents work independently in their worktrees, you spotlight whichever one you want to review.

Together these two let you run multiple agents in parallel on separate branches, then drop into any of their workspaces on demand to test — clean, non-destructive, and reversible.

## Prerequisites

Most skills assume `git`, `gh` (GitHub CLI), and `jq` are installed and authenticated. The Slack skill requires a Slack API token. Skills that reference agent trees and `birdhouse:agent/...` links require [Birdhouse](https://github.com/Birdhouse-Labs/birdhouse), but the orchestration patterns are worth reading either way.

## Who This Is For

Engineers exploring practical multi-agent workflows — whether you are evaluating agent-assisted development on a team, looking for reusable patterns to adapt, or just want to see how I structure repeatable engineering processes.
