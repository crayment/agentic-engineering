#!/usr/bin/env bash
# ABOUTME: Submits one pending GitHub pull request review with its final summary.
# ABOUTME: Reads the saved pending review id, posts the selected event, and reports the review URL.

set -euo pipefail

if [ "$#" -ne 4 ]; then
  echo "Error: expected 4 arguments, got $#." >&2
  echo "Usage: $(basename "$0") <PR> <REPO> <EVENT> <SUMMARY_FILE_PATH>" >&2
  echo "  EVENT must be one of: APPROVE, REQUEST_CHANGES, COMMENT" >&2
  exit 1
fi

PR="$1"
REPO="$2"
EVENT="$3"
SUMMARY_FILE_PATH="$4"

case "$EVENT" in
  APPROVE|REQUEST_CHANGES|COMMENT)
    ;;
  *)
    echo "Error: EVENT must be one of: APPROVE, REQUEST_CHANGES, COMMENT" >&2
    exit 1
    ;;
esac

[ -f "$SUMMARY_FILE_PATH" ] || { echo "Summary file not found: $SUMMARY_FILE_PATH" >&2; exit 1; }

REPO_SLUG=$(printf '%s' "$REPO" | tr '/' '_')
REVIEW_ID_FILE="/tmp/pending_review_${PR}_${REPO_SLUG}.txt"

if [ ! -f "$REVIEW_ID_FILE" ]; then
  echo "Error: No pending review found for PR #$PR in $REPO" >&2
  echo "Expected to find review ID in: $REVIEW_ID_FILE" >&2
  echo "You must create review comments with batched-review.sh first." >&2
  exit 1
fi

REVIEW_ID=$(cat -- "$REVIEW_ID_FILE")
SUMMARY=$(cat -- "$SUMMARY_FILE_PATH")

RESULT=$(gh api graphql -f query='
mutation($reviewId: ID!, $body: String!, $event: PullRequestReviewEvent!) {
  submitPullRequestReview(input: {
    pullRequestReviewId: $reviewId
    body: $body
    event: $event
  }) {
    pullRequestReview {
      id
      url
      state
    }
  }
}' -f reviewId="$REVIEW_ID" -f body="$SUMMARY" -f event="$EVENT")

REVIEW_URL=$(printf '%s' "$RESULT" | jq -r '.data.submitPullRequestReview.pullRequestReview.url')
REVIEW_STATE=$(printf '%s' "$RESULT" | jq -r '.data.submitPullRequestReview.pullRequestReview.state')

if [ -n "$REVIEW_URL" ] && [ "$REVIEW_URL" != "null" ]; then
  echo "Review submitted successfully"
  echo "State: $REVIEW_STATE"
  echo "URL: $REVIEW_URL"
  rm -f "$REVIEW_ID_FILE"
  echo "Cleaned up pending review tracking file"
else
  echo "Error: Failed to submit review" >&2
  printf '%s' "$RESULT" | jq . >&2
  exit 1
fi
