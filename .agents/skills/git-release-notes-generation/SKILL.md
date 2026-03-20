---
name: git-release-notes-generation
description: Generate release notes from git branch commit history and analyze changes. Use when you want to generate release notes, prepare release notes, prep for a PR, find what changed in this branch, or get branch change summary.
trigger_phrases:
  - generate release notes
  - prepare release notes
  - generate a PR description
tags:
  - git
  - github
---

# Generate Release Notes from Git Branch

Analyze git commit history and generate customer-facing "What's New" and technical release notes from branch changes.

When this skill is used during PR preparation, the generated notes usually make a strong starting point for the pull request description.

## Quick Commands

See what changed on your branch:

```bash
git log main..HEAD --oneline
```

Get detailed commit messages:

```bash
git log main..HEAD --pretty=format:"%h %s%n%n%b%n"
```

See file changes:

```bash
git diff main..HEAD --name-status
```

Get commit stats:

```bash
git log main..HEAD --stat
```

## Release Notes Template

Use this structure for your release notes:

```markdown
## What's New

### ✨ Features
- [User-facing feature descriptions]

### 🐛 Bug Fixes
- [User-visible bug fixes]

### 💫 Improvements
- [Performance, UX, and quality improvements]

---

## Technical Changes

### 🏗️ Infrastructure
- [Build, CI, tooling changes]

### 🧹 Code Quality
- [Refactoring, cleanup, technical debt]

### 📝 Documentation
- [Doc updates, comments, README changes]

## Files Changed
[Summary of key files modified]

## Testing
[What was tested, test coverage changes]
```

## Analysis Process

1. Review commits and understand each change.
2. Group by type: feature, bug fix, improvement, infrastructure, and so on.
3. Focus on user impact.
4. Include technical context.
5. Mention testing.

## PR Preparation Hint

If you are using this skill while preparing a pull request:

- Treat the generated notes as a draft PR body, not just standalone release notes.
- Keep the strongest reviewer-facing sections near the top, especially summary and testing.
- Trim customer-marketing language if the audience is primarily engineers reviewing the PR.

## Example Output

```markdown
## What's New

### ✨ Features
- Added dark mode toggle in user preferences
- New keyboard shortcut (Cmd+D) for duplicating items

### 🐛 Bug Fixes
- Fixed login redirect loop when session expires
- Resolved memory leak in file upload component

## Technical Changes

### 🏗️ Infrastructure
- Upgraded React from v17 to v18
- Added TypeScript strict mode

### Files Changed
- `src/components/LoginForm.tsx` - Session handling
- `src/hooks/useTheme.ts` - Dark mode implementation
- `package.json` - React upgrade

## Testing
- Added unit tests for theme switching
- Manual testing on Chrome, Firefox, Safari
- Verified session edge cases
```

## Overview

Analyzes git commit history and generates customer-facing "What's New" and technical release notes from branch changes. The output also works well as a draft pull request description when preparing a PR.
