"""Usage statistics tracking for gac.

Tracks how many times users have made commits with gac.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, TypedDict

logger = logging.getLogger(__name__)

STATS_FILE = Path.home() / ".gac_stats.json"


class GACStats(TypedDict):
    """TypedDict for GAC usage statistics."""

    total_commits: int
    first_used: str | None
    last_used: str | None
    daily_commits: dict[str, int]


def load_stats() -> GACStats:
    """Load statistics from the stats file.

    Returns:
        GACStats dictionary with usage statistics
    """
    if not STATS_FILE.exists():
        return {
            "total_commits": 0,
            "first_used": None,
            "last_used": None,
            "daily_commits": {},
        }

    try:
        with open(STATS_FILE) as f:
            data = json.load(f)
        return {
            "total_commits": data.get("total_commits", 0),
            "first_used": data.get("first_used"),
            "last_used": data.get("last_used"),
            "daily_commits": data.get("daily_commits", {}),
        }
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Failed to load stats: {e}")
        return {
            "total_commits": 0,
            "first_used": None,
            "last_used": None,
            "daily_commits": {},
        }


def save_stats(stats: GACStats) -> None:
    """Save statistics to the stats file.

    Args:
        stats: GACStats dictionary to save
    """
    try:
        STATS_FILE.write_text(json.dumps(stats, indent=2))
    except OSError as e:
        logger.warning(f"Failed to save stats: {e}")


def record_commit() -> None:
    """Record a successful commit in the statistics.

    This should be called after a commit is successfully created.
    """
    stats = load_stats()
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")

    # Update total
    stats["total_commits"] += 1

    # Set first_used if this is the first commit
    if stats["first_used"] is None:
        stats["first_used"] = now.isoformat()

    # Update last_used
    stats["last_used"] = now.isoformat()

    # Update daily count
    if today not in stats["daily_commits"]:
        stats["daily_commits"][today] = 0
    stats["daily_commits"][today] += 1

    save_stats(stats)
    logger.debug(f"Recorded commit. Total: {stats['total_commits']}")


def get_stats_summary() -> dict[str, Any]:
    """Get a human-readable summary of usage statistics.

    Returns:
        Dictionary with formatted statistics
    """
    stats = load_stats()

    total = stats["total_commits"]
    first_used = stats["first_used"]
    last_used = stats["last_used"]
    daily = stats["daily_commits"]

    # Calculate streak
    today = datetime.now().strftime("%Y-%m-%d")
    streak = 0
    if daily:
        sorted_days = sorted(daily.keys(), reverse=True)
        current_streak = 0
        check_date = datetime.now()

        for day_str in sorted_days:
            day = datetime.strptime(day_str, "%Y-%m-%d")
            expected_diff = (check_date - day).days

            if expected_diff == current_streak:
                current_streak += 1
            elif expected_diff > current_streak:
                break

        streak = current_streak

    # Today's commits
    today_commits = daily.get(today, 0)

    # Format dates
    first_used_str = "Never" if first_used is None else datetime.fromisoformat(first_used).strftime("%Y-%m-%d")
    last_used_str = "Never" if last_used is None else datetime.fromisoformat(last_used).strftime("%Y-%m-%d")

    return {
        "total_commits": total,
        "first_used": first_used_str,
        "last_used": last_used_str,
        "today_commits": today_commits,
        "streak": streak,
        "daily_commits": daily,
    }


def reset_stats() -> None:
    """Reset all statistics to zero."""
    empty_stats: GACStats = {
        "total_commits": 0,
        "first_used": None,
        "last_used": None,
        "daily_commits": {},
    }
    save_stats(empty_stats)
    logger.info("Statistics reset")
