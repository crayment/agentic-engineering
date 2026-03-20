---
name: github-ci-failure-diagnosis
description: Systematically diagnose GitHub PR CI check failures using gh CLI with a simple 3-step workflow.
trigger_phrases:
  - github checks failing
  - diagnose github CI failures
  - investigate CI failures
tags:
  - git
  - github
  - ci
---

# Diagnose GitHub PR CI Failures

When asked to investigate CI failures on a GitHub pull request, use this simple workflow with the GitHub CLI.

## Prerequisites

- GitHub CLI `gh` is installed and authenticated
- You know the repository name and PR number

## Workflow

### Step 1: Quick Status Overview

Use `gh pr checks` to get a quick visual summary of all check statuses:

```bash
gh pr checks <PR_NUMBER> --repo <OWNER>/<REPO>
```

What this shows:

- successful checks
- failed checks
- skipped checks
- summary counts
- URLs to each check

Start here. This is often enough to spot a formatter, lint, or test failure immediately.

### Step 2: Get Detailed Check Information

If you need workflow run ids or more structured detail, use:

```bash
gh pr view <PR_NUMBER> --repo <OWNER>/<REPO> --json statusCheckRollup
```

What this shows:

- complete list of checks with conclusions such as `FAILURE`, `SUCCESS`, and `SKIPPED`
- workflow run ids needed for fetching logs
- direct URLs to each check
- timestamps

Key fields to look for:

- `conclusion: FAILURE`
- `detailsUrl`
- `name`

If more than one check failed, list them and work through the most actionable one first.

### Step 3: Fetch Failure Logs

Once you have the run id for the failed check, get the logs:

```bash
gh run view <RUN_ID> --repo <OWNER>/<REPO> --log
```

What this shows:

- workflow logs
- error messages and stack traces
- the point where the workflow failed
- environment and setup output

Look for the first meaningful error. Later errors are often cascading noise.

## Complete Example

```bash
# 1. Quick overview
gh pr checks 1886 --repo myorg/myrepo

# 2. Get detailed status if needed
gh pr view 1886 --repo myorg/myrepo --json statusCheckRollup

# 3. Fetch logs for a failed run
gh run view 19084697022 --repo myorg/myrepo --log
```

## Tips

- Step 1 is often sufficient for simple failures.
- Use Step 2 when you need run ids or machine-readable status.
- Use Step 3 when you need logs to understand the failure.
- If multiple checks failed, separate root cause from follow-on failures.
- Prefer a concise diagnosis over dumping raw logs back to the user.

## Reporting Back

When you report back, include:

- which check failed
- the likely root cause
- the most relevant error line or short excerpt
- the recommended next step
