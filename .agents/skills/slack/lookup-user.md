# Slack: Lookup User

Find a Slack user's ID by searching by name or email using the Slack API.

## Prerequisites

- A Slack token must be provided by the caller. If no token has been specified, ask before proceeding.
- The token must have `users:read` scope

## How to Look Up a User

```bash
curl -s "https://slack.com/api/users.list" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '[.members[] | select(.real_name != null) | select(.real_name | test("(?i)<search_term>")) | {id: .id, name: .real_name}]'
```

Replace `<search_term>` with a name or partial name (e.g. `alice`, `bob`). The `(?i)` flag makes the match case-insensitive.

## Key Fields

- **id** — Use this for @mentions in Slack messages: `<@U0EXAMPLE1>`

## Example: Looking Up Multiple Users

```bash
curl -s "https://slack.com/api/users.list" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '[.members[] | select(.real_name != null) | select(.real_name | test("(?i)alice|bob")) | {id: .id, name: .real_name}]'
```

Then use the IDs in a message:

```
<@U0EXAMPLE1> <@U0EXAMPLE2> — could one of you approve this?
```

## Notes

- Search is case-insensitive via the `(?i)` flag in `test()`
- If multiple results are returned, match by `name` to pick the right one
- The `id` field is the user's Slack ID (starts with `U`)
- Requires `users:read` scope — if you get `missing_scope`, the token doesn't have it
