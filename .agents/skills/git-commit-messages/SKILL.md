---
name: git-commit-messages
description: Writing scannable, searchable commit messages that prioritize the what over the why.
trigger_phrases:
  - git commit
  - commit
tags:
  - git
---

# Subject-First Commit Messages

Write commit messages optimized for scanning and searching.

## Format

```text
Subject line

[Body with details...]
```

## Subject Line Rules

- Start with the changed subject, such as the file, feature, or component.
- Use present tense verbs.
- Be specific: `UserAuth: Fix session timeout` is better than `fix bug`.

## Examples

- `AgentCard: Add gradient border on hover.`
- `PatternsDialog: Fix mobile responsive layout.`
