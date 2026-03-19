---
name: github-pr-feedback
description: Orchestrate Birdhouse child agents to investigate PR review feedback in parallel, classify it as strengthened, weakened, or invalidated, then address approved items serially with fixes or threaded replies.
tags:
  - github
  - pull-request
---

# GitHub PR Feedback

Use this skill when a PR has review feedback and you want Birdhouse to coordinate the work.

This is a two-phase workflow:

1. Investigate unresolved feedback in parallel.
2. Address approved items serially.

Treat all feedback as suspect until it has been investigated in context.

## Main Agent Responsibilities

The main agent owns orchestration.

- Confirm the exact PR, repository, and branch.
- Understand the PR's goal and the branch diff before delegating.
- Fetch all unresolved feedback and group related items before spawning child agents.
- Assign child agents investigation-only work in parallel.
- Collect child-agent conclusions and classify feedback as `strengthened`, `weakened`, or `invalidated`.
- Present the triage to the user and get approval before any code changes or PR replies.
- Execute approved items one at a time.
- After each completed item, fetch unresolved feedback again and repeat until there are no unresolved threads or the user stops.

The main agent may coordinate many investigation agents in parallel, but only one agent may modify the branch at a time.

## Workflow Invariants

- Do not make code changes during the investigation phase.
- Do not post PR replies during the investigation phase.
- Do not resolve threads.
- Always include the specific comment link and author when presenting feedback.
- Always say whether the feedback targets code changed in this PR or pre-existing code.
- A single GitHub comment may contain multiple distinct issues. Split them when needed. It is valid to fix one point and explicitly decline another in the same reply.

## Step 1: Understand the PR Once

Before delegating, gather the PR context yourself.

1. Confirm you are in the correct repo from the PR link.
2. Confirm GitHub CLI authentication.
3. Review the branch diff and understand what the PR is trying to merge.
4. Write a short PR intent summary that can be handed to child agents.

Example commands:

```bash
PR=0000

gh auth status && \
git fetch origin --prune && \
BASE=$(git merge-base HEAD origin/main) && \
printf 'Merge-base: %s\n' "$BASE" && \
git diff --stat "$BASE"...HEAD && \
gh pr diff "$PR" -w -U0
```

Your summary for child agents should cover:

- what the PR changes
- why those changes exist
- what tradeoffs or constraints matter
- what level of polish is appropriate for this PR

## Step 2: Fetch Unresolved Feedback

The main agent fetches unresolved review threads and turns them into a working queue.

Use GitHub GraphQL via `gh`. The command below produces enough data to prioritize and delegate threads.

```bash
PR=0000 && \
OWNER_REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner) && \
OWNER=${OWNER_REPO%/*} && NAME=${OWNER_REPO#*/} && \
gh api graphql -f query='query($owner:String!,$name:String!,$number:Int!){repository(owner:$owner,name:$name){pullRequest(number:$number){reviewThreads(first:100){nodes{id isResolved isOutdated comments(first:100){nodes{databaseId body createdAt author{login} path url}}}}}}}' -F owner=$OWNER -F name=$NAME -F number=$PR | \
jq -r '.data.repository.pullRequest.reviewThreads.nodes
  | map(select(.isResolved == false))
  | map({
      thread_id: .id,
      outdated: .isOutdated,
      path: (.comments.nodes[0].path // "(no file)"),
      first_created: .comments.nodes[0].createdAt,
      comments_count: (.comments.nodes | length),
      unanswered: ((.comments.nodes | length) == 1),
      first_comment_id: .comments.nodes[0].databaseId,
      last_comment_id: .comments.nodes[-1].databaseId,
      last_author: .comments.nodes[-1].author.login,
      last_body: .comments.nodes[-1].body,
      last_url: .comments.nodes[-1].url
    })
  | sort_by([(.unanswered|not), .first_created])'
```

Prioritization heuristic:

- Prefer related feedback clusters over isolated comments.
- Within a cluster, unanswered threads usually come first.
- Older unresolved threads usually come before newer ones.
- Override the heuristic when several comments are clearly about the same design choice.

## Step 3: Group Related Feedback Before Delegating

Do not blindly create one child agent per comment.

First, cluster feedback into a reasonable number of parallel investigations. Group comments that appear to involve the same:

- API or type design
- component behavior or UX choice
- naming or code organization decision
- test strategy
- performance or data flow concern

Good delegation rule:

- One child agent per independent investigation track.
- Keep the number of tracks reasonable enough that you can review the results thoughtfully.

## Step 4: Investigation Agent Contract

Investigation agents are researchers first. They do not change code until explicitly instructed later.

Each investigation agent must receive:

- the PR number and repo
- a short summary of what the PR is trying to accomplish
- the assigned thread ids, comment ids, and links
- instructions for how to fetch the feedback directly if they want to re-read it
- the exact phrase: `strengthen, weaken, or invalidate`

Each investigation agent should be told:

- Read the assigned feedback in full.
- Investigate the relevant code and surrounding patterns.
- Decide whether the feedback is strengthened, weakened, or invalidated by the codebase context and PR intent.
- Split multi-issue comments into separate sub-issues when needed.
- Do not write code.
- Do not post replies.
- Do not resolve threads.
- Return a compact report for each issue or sub-issue.

Recommended child-agent prompt shape:

```text
You are investigating PR review feedback only. Do not write code, do not commit, do not push, and do not post GitHub replies.

PR context:
- Repo: OWNER/NAME
- PR: 1234
- Intent: <main agent summary>
- Constraints: <tradeoffs, scope, or non-goals>

Assigned feedback:
- Thread/comment links: <links>
- Thread ids / comment ids: <ids>

If needed, fetch the assigned feedback yourself from GitHub to read the full text fresh.

Your task is to strengthen, weaken, or invalidate each assigned feedback point.

For each issue or sub-issue, return:
1. comment link and author
2. short restatement of the issue
3. classification: strengthened / weakened / invalidated
4. whether it targets code changed in this PR or pre-existing code
5. evidence from the codebase or diff
6. proposed action: fix now / reply-only / defer
7. risks or tradeoffs
8. draft reply text if we choose to respond now
```

## Step 5: Investigation Standards

Investigation should be lightweight but real.

Each child agent should inspect:

- the referenced file and surrounding code
- related symbols or call sites across the repo
- existing patterns that matter for consistency
- whether the commented code was actually changed in this PR

Useful commands:

```bash
# List changed files
gh pr diff "$PR" --name-only

# Search for related symbols
rg -n "SomeFunctionOrConstantName"

# Check whether a file changed in this PR
gh pr diff "$PR" --name-only | rg -n '^path/to/file.ext$'

# Show exact PR hunks for a file
git diff --unified=0 "$BASE"...HEAD -- path/to/file.ext
```

Child agents should avoid over-investigating. The goal is enough context to make a solid recommendation, not to solve the whole issue yet.

## Step 6: Main Agent Triage Output

After child agents finish, the main agent consolidates their findings for the user.

Present a triage report grouped as:

- `strengthened` — likely valid in this PR's context; probably worth addressing
- `weakened` — concern has some merit but is overstated, lower priority, or not worth changing now
- `invalidated` — concern is based on a misunderstanding, incorrect assumption, outdated context, or scope mismatch

For each item include:

- comment link and author
- one-sentence summary of the concern
- classification
- changed-in-PR vs pre-existing
- proposed action
- short rationale

The main agent should then propose the next serial item to address and ask for approval before acting.

## Step 7: Serial Execution Only

After approval, the main agent continues working with child agents, but execution is serial.

Only one agent at a time may:

- edit code
- run fix-related tests
- commit
- push
- post the final reply tied to that item

Other child agents may remain idle or continue discussion, but they must not write to the branch.

## Step 8: Two Common Execution Paths

There are two common follow-ups after investigation.

### A. Reply-Only

Use this when the feedback is invalidated, weakened enough that no change is warranted, or only partly accepted.

The main agent replies to the investigation agent and asks it to:

1. write the threaded reply
2. use the [reply](birdhouse:skill/github-pr-review-replies) skill
3. report back with the reply link and exact reply text

This path also covers partial agreement, for example:

- one point in the comment was fixed earlier
- one sub-issue is valid, another is not
- one suggestion is accepted in principle but deferred for scope reasons

### B. Fix-Then-Reply

Use this when the feedback should produce a code change now.

The main agent replies to the investigation agent and asks it to:

1. implement only the approved fix scope
2. run relevant tests or checks
3. create a focused commit
4. push the branch
5. use the [reply](birdhouse:skill/github-pr-review-replies) skill to post the threaded update
6. report back with the commit SHA, pushed branch state, reply link, and exact reply text

For comments containing multiple issues, be explicit about which sub-issues are being fixed and which are being declined or deferred.

## Commit Hygiene And Branch Safety

When a child agent is asked to fix code:

- Make the smallest reasonable change.
- Keep the commit focused to the approved feedback item.
- Do not bundle unrelated cleanup.
- Run the most relevant validation for the changed area before committing.
- Push the current branch normally; never force-push unless the user explicitly requests it.
- Do not amend commits unless explicitly requested.
- Do not post the PR reply until the branch reflects the intended fix.

## Step 9: Repeat The Loop

After an item is addressed:

1. fetch unresolved feedback again
2. identify remaining or newly added unresolved threads
3. regroup if the conversation changed
4. delegate new investigations if needed
5. continue until there are no unresolved threads or the user stops

This is not an infinite autonomous loop. Re-check the PR after each completed item and continue while there is still actionable unresolved feedback.

## Output Quality Standard

Whether reporting investigation results or execution results, optimize for fast human review.

- Do not dump full comment bodies unless the exact wording matters.
- Summarize the point and its intent.
- Prefer direct evidence from the diff and codebase over generic style opinions.
- Keep draft replies concise, respectful, and specific.
- When reporting a posted reply, always include the reply link and quote the exact reply text.
