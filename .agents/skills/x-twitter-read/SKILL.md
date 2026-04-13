---
name: x-twitter-read
description: Fetch the full content of a tweet by ID using the X API v2. Use when you need to read a tweet, get its full text, or extract URLs from it.
trigger_phrases:
  - read tweet
  - fetch tweet
  - get tweet
tags:
  - twitter
  - x
---

# X Twitter Read Skill

Fetch the full content of a tweet using the X API v2 with no external dependencies beyond Python stdlib.

## Credentials

The following environment variables are expected to be set:

| Variable | Description |
|---|---|
| `X_API_KEY` | OAuth 1.0a Consumer Key |
| `X_API_SECRET` | OAuth 1.0a Consumer Key Secret |
| `X_ACCESS_TOKEN` | OAuth 1.0a Access Token |
| `X_ACCESS_TOKEN_SECRET` | OAuth 1.0a Access Token Secret |

## Fetching a Tweet

Run this Python snippet via Bash. It handles OAuth 1.0a signing entirely via stdlib — no pip installs needed.

Replace `TWEET_ID` with the numeric ID from the tweet URL:
`https://x.com/username/status/2023495040258261460` → ID is `2023495040258261460`

```bash
python3 - <<'EOF'
import os, time, random, string, hmac, hashlib, base64, urllib.parse, urllib.request, json

key     = os.environ["X_API_KEY"]
secret  = os.environ["X_API_SECRET"]
token   = os.environ["X_ACCESS_TOKEN"]
tsecret = os.environ["X_ACCESS_TOKEN_SECRET"]

tweet_id = "TWEET_ID"
url = f"https://api.twitter.com/2/tweets/{tweet_id}"
params = {"tweet.fields": "note_tweet,entities,attachments,public_metrics,created_at"}

nonce = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
ts    = str(int(time.time()))

oauth = {
    "oauth_consumer_key":     key,
    "oauth_nonce":            nonce,
    "oauth_signature_method": "HMAC-SHA1",
    "oauth_timestamp":        ts,
    "oauth_token":            token,
    "oauth_version":          "1.0",
}

# Signature base string includes both oauth params and query params
enc = lambda s: urllib.parse.quote(s, safe='')
all_params = {**oauth, **params}
sorted_params = "&".join(f"{enc(k)}={enc(v)}" for k, v in sorted(all_params.items()))
base = "&".join(["GET", enc(url), enc(sorted_params)])
signing_key = f"{enc(secret)}&{enc(tsecret)}"
sig = base64.b64encode(hmac.new(signing_key.encode(), base.encode(), hashlib.sha1).digest()).decode()

oauth["oauth_signature"] = sig
auth_header = "OAuth " + ", ".join(f'{enc(k)}="{enc(v)}"' for k, v in sorted(oauth.items()))

full_url = url + "?" + urllib.parse.urlencode(params)
req = urllib.request.Request(full_url, headers={"Authorization": auth_header})
with urllib.request.urlopen(req) as r:
    print(json.dumps(json.loads(r.read()), indent=2))
EOF
```

## Important: Always Request `note_tweet`

X truncates tweets at 280 chars in the default `text` field. Long-form tweets store their full content in `noteTweet.text` and `noteTweet.entities.urls`. The snippet above always requests it.

## Reading the Response

- `data.noteTweet.text` — full untruncated text (prefer this when present)
- `data.text` — truncated to 280 chars (fallback)
- `data.noteTweet.entities.urls[].expandedUrl` — fully resolved URLs (GitHub links etc.)
- `data.entities.urls[].expandedUrl` — URLs in the truncated portion only
