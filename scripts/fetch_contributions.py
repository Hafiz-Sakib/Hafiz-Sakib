"""
fetch_contributions.py — pull real contribution data with no token.

GitHub serves the contribution calendar as public HTML at
https://github.com/users/<username>/contributions — the same fragment
the profile page itself uses. Parse the day cells with BeautifulSoup
and write data/contributions.json with raw days + derived stats.

    python scripts/fetch_contributions.py
"""
import json
import os
from datetime import datetime

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_USERNAME", "Hafiz-Sakib")
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT = "data/contributions.json"


def fetch_days(username: str) -> list[dict]:
    resp = requests.get(
        f"https://github.com/users/{username}/contributions",
        headers={"User-Agent": "profile-art-bot"},
        timeout=20,
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    days = []
    cells = soup.select("td.ContributionCalendar-day") or soup.select("[data-date]")
    for cell in cells:
        date = cell.get("data-date")
        if not date:
            continue
        count = cell.get("data-level")
        level = int(count) if count is not None else 0
        tooltip_id = cell.get("id")
        days.append({"date": date, "level": level, "tooltip_id": tooltip_id})
    return days


def derive_stats(days: list[dict]) -> dict:
    if not days:
        return {"current_streak": 0, "longest_streak": 0, "total": 0}

    total = sum(1 for d in days if d["level"] > 0)

    longest = current = 0
    for d in days:
        if d["level"] > 0:
            current += 1
            longest = max(longest, current)
        else:
            current = 0

    # trailing streak (from most recent day backwards)
    trailing = 0
    for d in reversed(days):
        if d["level"] > 0:
            trailing += 1
        else:
            break

    monthly = {}
    for d in days:
        month = d["date"][:7]
        monthly[month] = monthly.get(month, 0) + (1 if d["level"] > 0 else 0)

    return {
        "total_active_days": total,
        "longest_streak": longest,
        "current_streak": trailing,
        "monthly": monthly,
    }


if __name__ == "__main__":
    days = fetch_days(USERNAME)
    payload = {
        "username": USERNAME,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "days": days,
        "stats": derive_stats(days),
    }
    os.makedirs("data", exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"wrote {OUT} ({len(days)} days)")
