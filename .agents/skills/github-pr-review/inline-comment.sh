#!/usr/bin/env bash
# ABOUTME: Posts one standalone inline pull request comment immediately.
# ABOUTME: Uses the same anchor matching and Birdhouse PR review footer as batched review comments.

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

[ -f "$ANCHOR_TEXT_FILE_PATH" ] || { echo "Anchor text file not found: $ANCHOR_TEXT_FILE_PATH" >&2; exit 1; }
[ -f "$COMMENT_BODY_FILE_PATH" ] || { echo "Comment file not found: $COMMENT_BODY_FILE_PATH" >&2; exit 1; }

perl -0777 -pe 's/\s+\z//' -i -- "$ANCHOR_TEXT_FILE_PATH"

SHA=$(gh pr view "$PR" -R "$REPO" --json headRefOid --jq .headRefOid)
ANCHOR_TARGET_FILE=$(mktemp "/tmp/birdhouse-inline-comment-anchor.XXXXXX")
COMMENT_PAYLOAD_FILE=$(mktemp "/tmp/birdhouse-inline-comment-payload.XXXXXX")
COMMENT_TEXT_FILE=$(mktemp "/tmp/birdhouse-inline-comment-body.XXXXXX")
trap 'rm -f "$ANCHOR_TARGET_FILE" "$COMMENT_PAYLOAD_FILE" "$COMMENT_TEXT_FILE"' EXIT

gh api "repos/$REPO/contents/$PATH_IN_REPO?ref=$SHA" \
  | jq -r .content | base64 --decode > "$ANCHOR_TARGET_FILE"

LINE=$( { grep -nFx -f "$ANCHOR_TEXT_FILE_PATH" "$ANCHOR_TARGET_FILE" | head -n1 | cut -d: -f1; } || true )

if [ -z "${LINE:-}" ]; then
  LINE=$( { grep -nF -f "$ANCHOR_TEXT_FILE_PATH" "$ANCHOR_TARGET_FILE" | head -n1 | cut -d: -f1; } || true )
fi

[ -n "${LINE:-}" ] || { echo "Anchor not found in $PATH_IN_REPO" >&2; exit 1; }

cat -- "$COMMENT_BODY_FILE_PATH" > "$COMMENT_TEXT_FILE"
printf '\n\n---\n\n<sub>Posted using the <a href="https://birdhouselabs.ai">Birdhouse PR review skill</a>.</sub>\n' >> "$COMMENT_TEXT_FILE"

jq -n \
  --rawfile body "$COMMENT_TEXT_FILE" \
  --arg sha "$SHA" \
  --arg path "$PATH_IN_REPO" \
  --argjson line "$LINE" \
  '{body:$body, commit_id:$sha, path:$path, line:$line, side:"RIGHT"}' > "$COMMENT_PAYLOAD_FILE"

COMMENT_URL=$(gh api -X POST "repos/$REPO/pulls/$PR/comments" --input "$COMMENT_PAYLOAD_FILE" --jq .html_url)
printf '%s\n' "$COMMENT_URL"
