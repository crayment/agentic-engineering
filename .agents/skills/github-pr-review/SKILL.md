---
name: github-pr-review
description: Orchestrate Birdhouse child agents to review a pull request in parallel, cross-validate proposed feedback, and submit one batched GitHub review with inline comments and a final decision.
tags:
  - github
  - pull-request
---

# GitHub PR Review

Use this skill when you want Birdhouse to run a serious PR review with a team of agents and then submit the review to GitHub.

This skill has two phases:

1. Investigate and cross-validate feedback in parallel.
2. Submit one batched GitHub review after explicit approval.

## Core Stance

- Be pragmatic. Catch bugs, security issues, architectural mistakes, and real maintainability problems.
- Do not nitpick style when the substance is sound.
- Treat candidate feedback as suspect until another agent strengthens it or the main agent independently agrees it holds up.
- Use batched review comments by default so the author gets one coherent review instead of a notification storm.
- Do not post anything to GitHub until the user explicitly approves the final review payload.

## Main Agent Responsibilities

The main agent is the review lead.

- Confirm the exact PR, repo, branch, and GitHub auth state.
- Understand the PR's intent, scope, and constraints before delegating.
- Break the review into a reasonable number of independent investigation tracks.
- Create fresh child agents for investigation by default. Do not clone yourself unless you intentionally need competing judgments on the same already-scoped issue.
- Treat child agents as teammates. Ask follow-up questions, challenge weak reasoning, and reuse the best-informed agent later when drafting or refining a surviving comment.
- Run cross-validation so weak feedback gets weakened or invalidated before it reaches GitHub.
- Curate the final review queue and ask for approval.
- Appoint one submission owner agent for GitHub posting. Only that one agent may touch the pending review state.

## Workflow Invariants

- No GitHub comments or review submissions before explicit user approval.
- One submission owner only. Never let multiple agents write to the same pending review.
- Prefer inline comments only for line-specific feedback on changed code.
- Put PR-wide themes, praise, or non-line-specific guidance in the final review summary.
- If a concern is invalidated, do not surface it as GitHub feedback.
- If a concern is weakened but still worth mentioning, keep the wording humble and narrow.
- Every posted inline comment must include the standard Birdhouse footer. The bundled scripts handle this automatically.

## Phase 1: Understand The PR

Before spawning agents:

1. Confirm the repo and PR number.
2. Confirm `gh auth status` works.
3. Review the PR diff and gather the PR's high-level purpose.
4. Read any relevant AGENTS files, project docs, or dependency docs that change the review standard.

Useful commands:

```bash
PR=0000

gh auth status && \
git fetch origin --prune && \
BASE=$(git merge-base HEAD origin/main) && \
printf 'Merge-base: %s\n' "$BASE" && \
git diff --stat "$BASE"...HEAD && \
gh pr diff "$PR" -w -U0
```

Prepare a short PR intent summary for child agents:

- what is changing
- why it is changing
- what risks matter most
- what level of polish is appropriate for this PR

## Phase 2: Parallel Investigation

Break the review into tracks that can be investigated independently. Good track boundaries often follow:

- backend logic or state transitions
- frontend behavior or UX
- API contracts and typing
- tests and fixtures
- security or auth boundaries
- data migrations or persistence rules

Fresh-agent default matters here. Hand each child agent the PR intent explicitly instead of relying on inherited clone context.

Each investigation agent should be told to:

- review its assigned files or concern area
- identify candidate feedback only when the concern is substantive
- return exact file/path context for any candidate
- draft a concise proposed comment body when useful
- state severity and confidence
- clearly say what still needs verification
- avoid posting anything or editing code

## Phase 3: Cross-Validate Findings

Do not trust first-pass review comments automatically.

Have other agents or the main agent pressure-test candidate feedback. Use the same `strengthen, weaken, or invalidate` language from the feedback skill.

Cross-validation questions:

- Is the concern actually about changed code in this PR?
- Is the reasoning grounded in codebase patterns or docs, not generic preference?
- Is it blocking, important, or just nice-to-have?
- Would we still say this if we fully understood the PR's intent?
- Should this be an inline comment, a summary comment, or dropped entirely?

The main agent should keep the surviving queue small and high-signal.

## Phase 4: Present The Review Queue

Before anything is posted, present the proposed review to the user.

Use a manager-style summary with these sections:

- `Request changes`
- `Comment only`
- `Dropped`
- `Next submission step if approved`

For each surviving item include:

- short issue label
- GitHub file/comment target if known
- owner agent link in Birdhouse markdown
- severity and confidence
- whether it will be inline or summary-only

The `Next submission step if approved` section should name:

- the single submission owner agent
- which inline comments it will post
- what review event it will use: `REQUEST_CHANGES`, `COMMENT`, or `APPROVE`
- what it will report back with: review URL and final submitted summary

## Review Artifact Layout

Once the user approves the final queue, materialize a lightweight review workspace:

```text
tmp/pr<PR_NUMBER>_review/
  comments/
    01-anchor.txt
    01-body.md
    01-meta.yml
    02-anchor.txt
    02-body.md
    02-meta.yml
  review-summary.md
  review-decision.txt
```

Use one comment bundle per approved inline comment.

`NN-meta.yml` should contain enough structured context for the submission owner:

```yaml
path: path/in/repo.ext
severity: high
confidence: high
owner_agent: birdhouse:agent/agent_abc123
source_agents:
  - birdhouse:agent/agent_abc123
  - birdhouse:agent/agent_def456
```

Guidelines:

- `NN-anchor.txt` contains only the exact anchor text to match in the target file.
- `NN-body.md` contains only the human-facing comment body. Do not manually add the footer.
- `review-decision.txt` contains exactly one of `APPROVE`, `REQUEST_CHANGES`, or `COMMENT`.
- `review-summary.md` contains the exact final review body to submit.

You do not need candidate/result markdown files in Birdhouse. The agent tree is the investigation record.

## Comment Quality Standard

Every inline comment should be:

- specific about the problem
- tied to the changed code
- clear about why it matters
- actionable without being prescriptive for trivial details
- concise enough to read quickly in GitHub

Good inline comments often include:

- the observed problem
- the practical impact
- a direct question or suggested direction if helpful

Do not use inline comments for:

- broad architectural essays
- uncertain concerns that did not survive cross-validation
- style-only preferences
- praise that does not need file-level anchoring

## Submission Owner Workflow

After approval, pick one submission owner agent. That agent may be the main agent or a child agent, but only one agent may post the review.

The submission owner should:

1. verify the review workspace files are complete
2. verify `gh auth status`
3. check for an existing pending review tracking file in `/tmp`
4. if a stale pending review file exists from a different run, stop and ask whether to reuse or discard it
5. run the bundled `batched-review.sh` once per approved inline comment
6. run the bundled `submit-review.sh` once with the final review summary and event
7. verify the review URL
8. report back with the review URL and submitted summary

Important:

- Post all inline comments first, then submit the review once.
- Keep submission serial and centralized.
- Use the bundled `inline-comment.sh` only if the user explicitly wants a standalone immediate comment instead of a batched review.

## Bundled Scripts

This skill bundles helper scripts in the same directory:

- `batched-review.sh` — add one inline comment to a pending review
- `submit-review.sh` — submit the pending review with `APPROVE`, `REQUEST_CHANGES`, or `COMMENT`
- `inline-comment.sh` — post one standalone inline comment immediately; not the default path

These scripts automatically append this footer to posted inline comments:

`Posted using the Birdhouse PR Review skill` with a link to `https://birdhouselabs.ai`

## Batched Submission Commands

Run the bundled scripts from the skill directory or with an absolute path.

Add one pending review comment:

```bash
/path/to/github-pr-review/batched-review.sh \
  <PR_NUMBER> \
  <OWNER/REPO> \
  <PATH_IN_REPO> \
  <ANCHOR_TEXT_FILE> \
  <COMMENT_BODY_FILE>
```

Submit the completed review:

```bash
/path/to/github-pr-review/submit-review.sh \
  <PR_NUMBER> \
  <OWNER/REPO> \
  <EVENT> \
  <SUMMARY_FILE>
```

Verify the final review:

```bash
gh pr view <PR_NUMBER> --repo <OWNER/REPO> --json reviews --jq '.reviews | last'
```

## Reporting Back

Before submission, report:

- the proposed inline comments
- the summary-only feedback
- the review event you intend to submit
- the submission owner agent link

After submission, report:

- the review URL
- the event used
- the final submitted summary text
- any comments that were intentionally dropped or converted to summary-only

If the review later receives feedback and you need to respond in-thread, use `[github-pr-feedback](birdhouse:skill/github-pr-feedback)`.
