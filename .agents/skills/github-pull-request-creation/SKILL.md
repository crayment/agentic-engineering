---
name: github-pull-request-creation
description: Create GitHub pull requests using gh CLI with proper formatting for multi-line descriptions. Use when you want to create a pr, submit a pr, pull request, create a pull request, submit a pull request, open a pr, or new pr.
trigger_phrases:
  - create a PR
  - create pull request
  - submit a PR
  - open a PR
tags:
  - github
---

# How to Submit GitHub Pull Requests with `gh` CLI

Use heredoc syntax for multi-line PR descriptions.

If you already generated branch notes or release notes, use that material as the starting PR body instead of rewriting the description from scratch.

## Basic Usage

Simple PR that opens an interactive prompt for the body:

```bash
gh pr create --title "Add feature X"
```

With inline body for short descriptions:

```bash
gh pr create --title "Fix login redirect" --body "Fixes issue with OAuth callback URL"
```

## Multi-line Descriptions

```bash
gh pr create --title "Add rocket boosters to the login button" --body "$(cat <<'EOF'
## Summary

Made the login button go REALLY fast. Like, uncomfortably fast.

## Changes

- Added flames emoji 🔥
- Increased button velocity by 300%
- Users now experience mild g-forces during authentication
- Login success rate: still 100% (just faster)

## Testing

- Tested on production (yolo)
- My mouse caught fire but in a good way
EOF
)"
```

How it works:

- `cat <<'EOF'` starts a heredoc and keeps the content literal.
- `$(...)` captures the heredoc output as a string.
- `--body "..."` receives the complete multi-line string.
- Single quotes around `'EOF'` prevent variable expansion.

## Common Options

Draft PR:

```bash
gh pr create --draft --title "WIP: Experimental feature" --body "..."
```

Different base branch:

```bash
gh pr create --base develop --title "Feature X" --body "..."
```

Add reviewers:

```bash
gh pr create --title "Fix bug" --body "..." --reviewer alice,bob
```

From a file:

```bash
gh pr create --title "Feature: User preferences" --body "$(cat pr-description.md)"
```

This works especially well when another step already generated a branch summary or release notes document for the PR.

## Avoid Fragile Inline Strings

```bash
# This breaks because the shell tries to interpret special characters and newlines
gh pr create --title "Add rocket boosters!" --body "Added cool stuff!\nReally fast now!"
```

Use heredoc instead.

## Overview

Guides agents to use heredoc syntax when creating GitHub PRs with multi-line descriptions to avoid shell interpretation issues. Generated branch notes or release notes often make a good starting point for the PR body.
