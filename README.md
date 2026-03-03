# ClawRecord Global Leaderboard

Global leaderboard for [ClawRecord](https://github.com/luka2chat/clawrecord) — ranking OpenClaw tamers worldwide.

## How to Register

1. Set up ClawRecord in your own repo (fork the template or create from scratch)
2. Submit a PR to add your entry to `registry.json`:

```json
{
  "username": "your-github-username",
  "repo": "your-username/your-clawrecord-repo",
  "registered_at": "YYYY-MM-DD"
}
```

3. Once merged, the leaderboard will include your stats in the next update cycle.

## How It Works

A GitHub Action runs every 6 hours:
1. Reads `registry.json` for all registered repos
2. Fetches each repo's `data/public_profile.json` via GitHub API
3. Aggregates rankings (total XP, weekly XP, streak)
4. Deploys the leaderboard to GitHub Pages

## Leaderboard

Visit the live leaderboard: `https://luka2chat.github.io/clawrecord-leaderboard/`
