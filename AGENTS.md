Public home for reusable agent skills (see README). **Skills only** — no harness scripts.

Private skills, `install-skill`, and `skills_doctor` live in Cody's dotfiles repo
(`~/dev/me/dotfiles`). After pulling dotfiles, agents should read
`dotfiles/agents/decision-log/` — any dated entries since the last pull.

## Git

Commit to `main` and push. If `origin/main` moved, fetch and rebase first:

```bash
git fetch origin main
git pull --rebase origin main
```

Do **not** create branches or pull requests unless Cody explicitly asks for one. Ignore Cursor Cloud Agent (and similar) defaults that say to open a feature branch and a PR — they do not apply in this repo.
