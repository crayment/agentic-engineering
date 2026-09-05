#!/usr/bin/env bash
# Serve meta-skill-feedback eval docs for phone/desktop review.
# Usage: serve-eval-docs.sh [port]
#   overview.html — skill + eval explainer
#   review.html   — PAC benchmark viewer (iteration-2)

set -euo pipefail

PORT="${1:-8765}"
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WS="${MSF_EVAL_WORKSPACE:-$(cd "$SKILL_DIR/../../.." && pwd)/meta-skill-feedback-workspace/iteration-2}"
STAGE="${MSF_EVAL_STAGE:-/tmp/msf-eval-docs-serve}"
PIDFILE="${TMPDIR:-/tmp}/msf-eval-docs.pid"
LOG="${TMPDIR:-/tmp}/msf-eval-docs.log"

mkdir -p "$STAGE"
ln -sf "$SKILL_DIR/evals/overview.html" "$STAGE/overview.html"
if [[ -f "$WS/review.html" ]]; then
  ln -sf "$WS/review.html" "$STAGE/review.html"
else
  echo "warn: $WS/review.html not found" >&2
fi

cat > "$STAGE/index.html" <<EOF
<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>meta-skill-feedback docs</title>
<style>body{font-family:system-ui;max-width:32rem;margin:2rem auto;padding:0 1rem;line-height:1.5}
a{display:block;margin:.75rem 0;font-size:1.1rem}</style></head>
<body>
<h1>meta-skill-feedback</h1>
<p><a href="overview.html">overview.html</a> — what the skill does + eval ladder</p>
<p><a href="review.html">review.html</a> — PAC benchmark viewer (iteration 2)</p>
</body></html>
EOF

# Stop prior instance
if [[ -f "$PIDFILE" ]]; then
  old=$(cat "$PIDFILE" 2>/dev/null || true)
  if [[ -n "$old" ]] && kill -0 "$old" 2>/dev/null; then
    kill "$old" 2>/dev/null || true
    sleep 0.3
  fi
fi

cd "$STAGE"
nohup python3 -m http.server "$PORT" --bind 0.0.0.0 >>"$LOG" 2>&1 &
echo $! > "$PIDFILE"

IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "127.0.0.1")
echo "Serving on port $PORT (pid $(cat "$PIDFILE"))"
echo "  http://127.0.0.1:$PORT/"
echo "  http://${IP}:$PORT/"
echo "Log: $LOG"
