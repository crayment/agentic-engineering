#!/usr/bin/env bash
# ABOUTME: Adds one inline comment to a pending GitHub pull request review.
# ABOUTME: Appends the Birdhouse PR Review footer and reuses one pending review per PR.

set -euo pipefail
set -f

if [ "$#" -ne 5 ]; then
  echo "Error: expected 5 arguments, got $#." >&2
  echo "Usage: $(basename "$0") <PR> <REPO> <PATH_IN_REPO> <ANCHOR_TEXT_FILE_PATH> <COMMENT_BODY_FILE_PATH>" >&2
  exit 1
fi

PR="$1"
REPO="$2"
PATH_IN_REPO="$3"
ANCHOR_TEXT_FILE_PATH="$4"
COMMENT_BODY_FILE_PATH="$5"

REPO_SLUG=$(printf '%s' "$REPO" | tr '/' '_')
REVIEW_ID_FILE="/tmp/pending_review_${PR}_${REPO_SLUG}.txt"

[ -f "$ANCHOR_TEXT_FILE_PATH" ] || { echo "Anchor text file not found: $ANCHOR_TEXT_FILE_PATH" >&2; exit 1; }
[ -f "$COMMENT_BODY_FILE_PATH" ] || { echo "Comment file not found: $COMMENT_BODY_FILE_PATH" >&2; exit 1; }

perl -0777 -pe 's/\s+\z//' -i -- "$ANCHOR_TEXT_FILE_PATH"

SHA=$(gh pr view "$PR" -R "$REPO" --json headRefOid --jq .headRefOid)
PR_NODE_ID=$(gh pr view "$PR" -R "$REPO" --json id --jq .id)

ANCHOR_TARGET_FILE=$(mktemp "/tmp/birdhouse-pr-review-anchor.XXXXXX")
trap 'rm -f "$ANCHOR_TARGET_FILE"' EXIT

gh api "repos/$REPO/contents/$PATH_IN_REPO?ref=$SHA" \
  | jq -r .content | base64 --decode > "$ANCHOR_TARGET_FILE"

LINE=$( { grep -nFx -f "$ANCHOR_TEXT_FILE_PATH" "$ANCHOR_TARGET_FILE" | head -n1 | cut -d: -f1; } || true )

if [ -z "${LINE:-}" ]; then
  LINE=$( { grep -nF -f "$ANCHOR_TEXT_FILE_PATH" "$ANCHOR_TARGET_FILE" | head -n1 | cut -d: -f1; } || true )
fi

[ -n "${LINE:-}" ] || { echo "Anchor not found in $PATH_IN_REPO" >&2; exit 1; }

COMMENT_BODY=$(cat -- "$COMMENT_BODY_FILE_PATH")
COMMENT_FOOTER='<sub>Posted using the <a href="https://birdhouselabs.ai">Birdhouse PR Review skill</a>.</sub>'
COMMENT_BODY=$(printf "%s\n\n---\n\n%s\n" "$COMMENT_BODY" "$COMMENT_FOOTER")

RESULT=$(gh api graphql -f query='
mutation($prId: ID!, $body: String!, $path: String!, $line: Int!) {
  addPullRequestReviewThread(input: {
    pullRequestId: $prId
    body: $body
    path: $path
    line: $line
  }) {
    thread {
      id
      comments(first: 1) {
        nodes {
          pullRequestReview {
            id
          }
        }
      }
    }
  }
}' -f prId="$PR_NODE_ID" -f body="$COMMENT_BODY" -f path="$PATH_IN_REPO" -F line="$LINE")

if [ ! -f "$REVIEW_ID_FILE" ]; then
  REVIEW_ID=$(printf '%s' "$RESULT" | jq -r '.data.addPullRequestReviewThread.thread.comments.nodes[0].pullRequestReview.id')
  if [ -n "$REVIEW_ID" ] && [ "$REVIEW_ID" != "null" ]; then
    printf '%s\n' "$REVIEW_ID" > "$REVIEW_ID_FILE"
    echo "Started new pending review. Review ID saved to: $REVIEW_ID_FILE"
  fi
fi

THREAD_ID=$(printf '%s' "$RESULT" | jq -r '.data.addPullRequestReviewThread.thread.id')
echo "Added comment to pending review (thread: $THREAD_ID)"
echo "Run submit-review.sh to submit all pending comments together."
