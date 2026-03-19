---
name: github-reply
description: Reply to GitHub PR review comments as threaded responses using the GitHub API replies endpoint.
trigger_phrases:
  - github reply
  - reply to github comment
  - reply in github thread
  - threaded github reply
tags:
  - github
  - pull-request
---

# GitHub Reply

Use this skill when you need to reply to an existing GitHub PR review comment thread.

Always use the GitHub `/replies` endpoint so the response appears in the existing thread instead of as a new top-level comment.

## Basic Usage

Use the numeric review comment id, usually the `last_comment_id` from thread data.

```bash
gh api \
  "/repos/OWNER/NAME/pulls/PR_NUMBER/comments/COMMENT_ID/replies" \
  --method POST \
  -f body="Your reply text here"
```

## Posting Reply Text From A File

Read the file contents first, then pass the content to `-f body=`.

Correct:

```bash
REPLY_BODY=$(cat /path/to/reply.txt)
gh api \
  "/repos/OWNER/NAME/pulls/PR_NUMBER/comments/COMMENT_ID/replies" \
  --method POST \
  -f body="$REPLY_BODY"
```

Also correct:

```bash
gh api \
  "/repos/OWNER/NAME/pulls/PR_NUMBER/comments/COMMENT_ID/replies" \
  --method POST \
  -f body="$(cat /path/to/reply.txt)"
```

Wrong:

```bash
gh api \
  "/repos/OWNER/NAME/pulls/PR_NUMBER/comments/COMMENT_ID/replies" \
  --method POST \
  -f body=@/path/to/reply.txt
```

That wrong form posts the filename literally instead of the file contents.

## Complete Example

```bash
PR=6313
COMMENT_ID=2508381598
OWNER_REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
OWNER=${OWNER_REPO%/*}
NAME=${OWNER_REPO#*/}

cat > /tmp/pr-reply-${COMMENT_ID}.txt << 'EOF'
Thanks for the review! I've addressed this by...
EOF

REPLY_BODY=$(cat /tmp/pr-reply-${COMMENT_ID}.txt)
gh api \
  "/repos/$OWNER/$NAME/pulls/$PR/comments/$COMMENT_ID/replies" \
  --method POST \
  -f body="$REPLY_BODY"
```

## What Not To Use

Do not use these for threaded review replies:

- `gh pr review --comment`
- `gh pr comment`
- `-f body=@filename`

Those create top-level comments or malformed replies instead of threaded responses.

## Reporting Back

After posting, report back with:

- the reply URL if GitHub returns it or you can construct it
- the exact reply text that was posted
- the comment id you replied to
