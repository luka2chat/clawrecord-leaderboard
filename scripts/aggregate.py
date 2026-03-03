#!/usr/bin/env python3
"""
ClawRecord Global Leaderboard Aggregator

Runs in the central clawrecord-leaderboard repo via GitHub Actions.
Reads registry.json, fetches each user's public_profile.json via
the GitHub API, aggregates into a global leaderboard, and generates
a static HTML page.
"""

import json
import os
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

REGISTRY_PATH = Path(__file__).parent.parent / "registry.json"
OUTPUT_DIR = Path(__file__).parent.parent / "docs"
OUTPUT_DIR.mkdir(exist_ok=True)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")


def fetch_profile(repo):
    """Fetch public_profile.json from a GitHub repo's default branch."""
    url = f"https://raw.githubusercontent.com/{repo}/main/data/public_profile.json"
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[aggregate] Failed to fetch {repo}: {e}")
        return None


def build_leaderboard(profiles):
    """Sort profiles into leaderboard rankings."""
    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_users": len(profiles),
        "by_xp": sorted(profiles, key=lambda p: p.get("xp", 0), reverse=True),
        "by_weekly_xp": sorted(profiles, key=lambda p: p.get("weekly_xp", 0), reverse=True),
        "by_streak": sorted(profiles, key=lambda p: p.get("streak", 0), reverse=True),
    }


def generate_leaderboard_html(leaderboard):
    profiles = leaderboard["by_xp"]
    rows = []
    for i, p in enumerate(profiles[:100], 1):
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"#{i}")
        avatar = p.get("avatar", "🥚")
        username = p.get("username", "unknown")
        level = p.get("level", 1)
        xp = p.get("xp", 0)
        streak = p.get("streak", 0)
        badges = p.get("badge_count", 0)
        league = p.get("league", "bronze")
        rows.append(
            f'<tr><td class="rank">{medal}</td>'
            f'<td class="user">{avatar} {username}</td>'
            f'<td>Lv.{level}</td>'
            f'<td class="xp">{xp:,}</td>'
            f'<td>🔥 {streak}</td>'
            f'<td>{badges}</td>'
            f'<td class="league">{league}</td></tr>'
        )

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ClawRecord Global Leaderboard</title>
<style>
:root{{--bg:#0b1120;--card:#182240;--border:#1e2d4a;--primary:#22c55e;--text:#e2e8f0;--dim:#94a3b8}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:var(--bg);color:var(--text);padding:20px}}
.wrap{{max-width:900px;margin:0 auto}}
h1{{text-align:center;margin-bottom:8px;font-size:1.5em}}
.subtitle{{text-align:center;color:var(--dim);margin-bottom:24px;font-size:.9em}}
table{{width:100%;border-collapse:collapse;background:var(--card);border-radius:12px;overflow:hidden;border:1px solid var(--border)}}
th{{background:#131c31;padding:10px 14px;text-align:left;font-size:.8em;color:var(--dim);text-transform:uppercase;letter-spacing:.05em}}
td{{padding:10px 14px;border-top:1px solid var(--border);font-size:.9em}}
tr:hover td{{background:rgba(34,197,94,.04)}}
.rank{{font-weight:700;text-align:center;width:50px}}
.user{{font-weight:600}}
.xp{{color:var(--primary);font-weight:700}}
.league{{text-transform:capitalize}}
.footer{{text-align:center;color:var(--dim);font-size:.75em;margin-top:24px}}
</style>
</head>
<body>
<div class="wrap">
<h1>🐾 ClawRecord Global Leaderboard</h1>
<p class="subtitle">{leaderboard["total_users"]} tamers worldwide &middot; Updated {leaderboard["generated_at"][:10]}</p>
<table>
<thead><tr><th>Rank</th><th>Tamer</th><th>Level</th><th>XP</th><th>Streak</th><th>Badges</th><th>League</th></tr></thead>
<tbody>{"".join(rows)}</tbody>
</table>
<p class="footer">Powered by <a href="https://github.com/openclaw/openclaw" style="color:var(--primary)">OpenClaw</a> &middot; Data aggregated from public GitHub repos</p>
</div>
</body>
</html>'''


def main():
    if not REGISTRY_PATH.exists():
        print("[aggregate] registry.json not found")
        sys.exit(1)

    registry = json.loads(REGISTRY_PATH.read_text())
    users = registry.get("users", [])
    print(f"[aggregate] Fetching profiles for {len(users)} registered users...")

    profiles = []
    for user in users:
        profile = fetch_profile(user["repo"])
        if profile:
            profile["_repo"] = user["repo"]
            profiles.append(profile)
            print(f"[aggregate]   ✓ {user['username']} — Lv.{profile.get('level', '?')} / {profile.get('xp', 0)} XP")
        else:
            print(f"[aggregate]   ✗ {user['username']} — failed")

    leaderboard = build_leaderboard(profiles)

    with open(OUTPUT_DIR / "leaderboard.json", "w") as f:
        json.dump(leaderboard, f, indent=2, ensure_ascii=False)

    with open(OUTPUT_DIR / "index.html", "w") as f:
        f.write(generate_leaderboard_html(leaderboard))

    print(f"[aggregate] Leaderboard generated: {len(profiles)} users ranked")


if __name__ == "__main__":
    main()
