---
name: gitlab-mr-review
description: Review a GitLab merge request end-to-end with subagents — worktree the branch, investigate in parallel, validate findings, then post inline threads/suggestions after approval. Use to review an MR, review a merge request, or run an MR review.
trigger_phrases:
  - review this mr
  - review merge request
  - review this merge request
  - run an mr review
tags:
  - gitlab
  - merge-request
  - review
---

# GitLab MR Review

Run a thorough, trustworthy review of a GitLab merge request and deliver feedback the team will value.

**Stance:** pragmatic — catch real bugs, security issues, design/data-integrity problems, and maintainability risks. Don't nitpick style a linter would catch. Treat every candidate finding as suspect until it survives validation. **Post nothing to the MR until the human approves.**

**Input:** an MR URL (or project path + MR IID). Tools: the `glab` CLI (assumed authed) and `git`.

---

## 1. Understand the MR

```bash
glab mr view <iid> -R <group/project>     # intent, scope, target branch, draft status, reviewers
glab mr diff <iid> -R <group/project>     # the AUTHORITATIVE changes
```

The MR's own diff is the source of truth for what changed. Never infer the changes from the default branch — it drifts from the MR.

## 2. Check out the branch in a worktree

Review the real code in full repo context, not the diff alone and not the default branch. Use the **`git-worktree`** skill. GitLab exposes the MR head at `refs/merge-requests/<iid>/head`:

```bash
git fetch origin refs/merge-requests/<iid>/head:mr-<iid>   # needs SSH; `glab mr checkout` fails on HTTPS creds
git worktree add .worktrees/mr-<iid> mr-<iid>              # add .worktrees/ to .gitignore
```

Verify the worktree actually contains the change before reviewing it.

## 3. Investigate — fan out subagents

Split the review into independent concern-tracks sized to the MR (e.g. correctness, security/auth, tests, docs-sync, performance, API/contract). Delegate each to a subagent:

- Give a **fully self-contained brief**: the MR's intent, the track to own, the absolute worktree path, full tools to read/run/test. Subagents start with zero context — front-load it.
- Subagents can be **resumed** for follow-ups (don't assume one-shot).
- Judge against the repo's **committed** standards where they exist (`CLAUDE.md`, `.claude/rules/`, `CONTRIBUTING`, `docs/`). Never treat uncommitted or personal scratch as authoritative.
- Right-size: a small MR needs one or two agents, not a fleet.

## 4. Validate before believing

Treat every candidate finding as suspect — but validate differently depending on what kind of claim it is.

**Empirical claims** ("this test passes", "this reproduces the bug", "CI is green", "this function returns X for input Y") — verify by actually running it, not by asking another model to weigh in. An agent reporting a clean test run is trustworthy on the pass/fail fact itself (fabricating a passing run is rare); the real risk is scope, not hallucination — check *what the test actually asserts*, not just that it exited 0. Prefer execution over debate whenever a claim is checkable this way (spin up the real test env if the repo has one, e.g. a `worktree-test-env`-style skill, in the same worktree).

**Judgment claims** ("this is the right design", "this edge case matters", "this test covers the intended behavior", "this is architecturally sound") — these benefit hugely from **cross-model validation**. Same-model self-critique carries correlated blind spots: a model re-checking its own family's reasoning tends to miss the same things it already missed, so agreement isn't as informative as it looks. Instead:

- Run the validator as a **separate, serial** subagent — it needs the original claim as input, so it cannot run in parallel with the agent that produced it (unlike the independent concern-track fan-out in step 3, which *should* be parallel).
- Pin it to a **different model family** than the one that raised the claim (the `Task` tool's `model` parameter takes an explicit slug), pointed at the same worktree.
- Brief it adversarially — "try hard to disprove this claim; cite code; run commands; don't just agree" — not "does this seem right to you?".
- Reserve this for **Blocking** and high-confidence findings. Running it on every "notable, confirmed fine" note mostly burns tokens re-confirming low-stakes things.

Anchor every surviving finding to `file:line`.

## 5. Assemble + get approval

Present a queue, nothing posted yet:

- **Blocking** / **Non-blocking** / **Dropped**, each with location, severity, confidence, and a suggested fix.
- Get explicit human approval on wording before posting anything.

## 6. Post — conventions

- **Actionable feedback → inline, resolvable threads** anchored to the exact lines. Use **suggestion blocks** for concrete fixes (see recipes).
- **Summary comment is for thanks / general framing / non-actionable context only** — never put action items there.
- **Outcome:** leaving threads open + withholding approval is the "please address" signal. Approve only when satisfied. Don't submit a formal "request changes" unless the team actually uses it.
- **Tone:** concise, question-framed, collaborative. Credit good work. Skip style nitpicks.

## 7. Close the loop

- Detect replies: re-read discussions and filter to notes that aren't yours and aren't bots (see recipes). A background monitor can watch for replies/pushes.
- **Reply inside the existing thread** (`…/discussions/<id>/notes`), not a new thread.
- **Resolve** a thread once it's addressed.

---

## glab / API recipes

`PROJECT` below is the URL-encoded path, e.g. `group%2Fsubgroup%2Fproject`.

```bash
# diff refs needed to anchor inline comments
glab api "projects/$PROJECT/merge_requests/<iid>" | jq '.diff_refs'   # base_sha, start_sha, head_sha

# general (non-inline) comment — good for the summary
glab mr note <iid> -m "..."

# inline thread anchored to a changed line (JSON body — MUST set the content-type header)
jq -n --arg b "$BODY" --arg base "$BASE" --arg head "$HEAD" \
  '{body:$b, position:{position_type:"text", base_sha:$base, start_sha:$base, head_sha:$head,
                       old_path:"path", new_path:"path", new_line:<N>}}' \
  | glab api "projects/$PROJECT/merge_requests/<iid>/discussions" \
      --method POST --header "Content-Type: application/json" --input -

# reply INTO an existing thread (not a new discussion)
glab api "projects/$PROJECT/merge_requests/<iid>/discussions/<discussion_id>/notes" \
  --method POST --raw-field body="..."

# resolve a thread once addressed
glab api "projects/$PROJECT/merge_requests/<iid>/discussions/<discussion_id>?resolved=true" --method PUT

# detect replies (human, not you, not bots)
glab api "projects/$PROJECT/merge_requests/<iid>/discussions?per_page=100" \
  | jq -r --arg me "<your-username>" '.[].notes[]
      | select((.system|not) and .author.username!=$me and (.author.username|ascii_downcase|test("bot|duo|marge")|not))
      | "@\(.author.username): \(.body)"'

# approvals
glab api "projects/$PROJECT/merge_requests/<iid>/approvals"
```

**Suggestion blocks** (applicable fixes the author can accept in one click) — fenced with a range relative to the commented line:

````
```suggestion:-0+0
<replacement for the commented line>
```
````

`:-1+0` includes the line above; `:-0+2` includes two lines below — the range is what gets replaced.

---

## Pitfalls (don't repeat)

- Reviewing the default branch instead of the MR branch — they diverge.
- Trusting one diff source when two disagree; `glab mr diff` is the truth.
- Shallow clone has no merge-base, so `git diff main...HEAD` misleads (renders a merge as deletions). Use the GitLab diff.
- Citing uncommitted or personal notes as if they were project standards.
- Asserting without testing; assuming the author's shell / OS / arch matches yours.
- Posting before the human approves.
- Inline-discussion POST failing with "content-type '' is not supported" — set `--header "Content-Type: application/json"`.
- Fanning out more agents than the MR warrants.
- Treating same-model self-critique as if it were independent validation — it's correlated, not independent; use a different model family for judgment-claim validation (step 4).
- Running the cross-model validator in parallel with the agent that produced the claim — it needs the claim as input, so it must run serially, after.

## Related skills

`git-worktree` (check out the branch), `git-spotlight` (browse a worktree's HEAD in your editor), `git-surgeon` (hunk-level commits if you also fix things), `git-branch-cleanup` (tidy up after).
