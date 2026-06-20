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

## Multi-line Descriptions — always write to a file first

PR descriptions almost always contain markdown code blocks with backticks. Backticks inside `$()` command substitution terminate the substitution early and cause a syntax error. The safe, reliable pattern is to write the body to a temp file first, then read it:

```bash
# Step 1: write the body to a temp file
cat > /tmp/pr-body.md << 'EOF'
## ✨ Features
- Added rocket boosters to the login button so authentication feels dramatically faster

## Testing

- Tested on production (yolo)
- My mouse caught fire but in a good way
EOF

# Step 2: create the PR from the file
gh pr create --title "Add rocket boosters to the login button" --body "$(cat /tmp/pr-body.md)"
```

This approach:
- Handles backticks, code blocks, and special characters without escaping
- Works regardless of PR body length or complexity
- Is easy to inspect before submitting

**Never use inline heredoc with `$()` when the body contains backticks or code fences.** It will break.

## Common Options

Draft PR:

```bash
gh pr create --draft --title "WIP: Experimental feature" --body "$(cat /tmp/pr-body.md)"
```

Different base branch:

```bash
gh pr create --base develop --title "Feature X" --body "$(cat /tmp/pr-body.md)"
```

Add reviewers:

```bash
gh pr create --title "Fix bug" --body "$(cat /tmp/pr-body.md)" --reviewer alice,bob
```

If release notes already exist, preserve their headings and bullets with only minimal reviewer-focused trimming.

## Avoid These Patterns

```bash
# BREAKS: backticks inside $() end the substitution early
gh pr create --title "Fix bug" --body "$(cat <<'EOF'
Run `bun test` to verify
EOF
)"

# BREAKS: shell tries to interpret special characters and newlines
gh pr create --title "Add feature!" --body "Added cool stuff!\nReally fast now!"
```

## Overview

Guides agents to use heredoc syntax when creating GitHub PRs with multi-line descriptions to avoid shell interpretation issues. Generated release notes should usually determine the PR body structure.
