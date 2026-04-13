---
name: oss-research
description: Clone a GitHub repo or download a reference source locally to ~/dev/oss for searching and reading. Use when deeper understanding of an open source codebase would benefit the task at hand.
trigger_phrases:
  - clone the repo
  - ask the source code
  - research the git repo
tags:
  - github
  - oss
---

# Localref

Clone or download external references to `~/dev/oss` so that we can research the code, not the outdated docs.

## Workflow

1. **Clone** — shallow clone inside of `~/dev/oss`:
   First check if `~/oss/dev/repo-name` already exists. If so reuse it, just `git pull` inside instead so you are up to date.
   ```bash
   git clone --depth 1 https://github.com/owner/repo.git
   ```

2. **Search and read**
    Instead of reading yourself - warm up a child agent to own questions about this codebase.
    You can ask targeted questions and get answers without having to read the code yourself
