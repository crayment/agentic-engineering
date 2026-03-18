---
name: git-spotlight
description: Use this skill for spotlighting a worktree branch in the main clone for review, and undoing a spotlight. Use when you want to spotlight a worktree, make the main clone reflect a worktree's HEAD, undo a spotlight, or restore the main clone after reviewing a worktree branch.
tags:
  - git
  - worktree
---

# Git Spotlight

The spotlight technique points the main clone's `spotlight` branch at the current HEAD of a worktree, so you can browse and review the work in your editor without disturbing your own branch.

## Operations

- **[spotlight.md](spotlight.md)** — Point the main clone at a worktree's HEAD
- **[undo-spotlight.md](undo-spotlight.md)** — Restore the main clone to its pre-spotlight state
