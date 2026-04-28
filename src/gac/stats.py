"""Usage statistics tracking for gac.

Tracks how many times users have made commits with gac.
"""

import json
import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, TypedDict

logger = logging.getLogger(__name__)

STATS_FILE = Path.home() / ".gac_stats.json"


def stats_enabled() -> bool:
    """Check if stats tracking is enabled.

    Returns False if GAC_DISABLE_STATS environment variable is set to any value.
    """
    return os.environ.get("GAC_DISABLE_STATS") is None


def get_current_project_name() -> str | None:
    """Get the current project name from git remote or directory name.

    Returns:
        Project name (repo name) or None if not in a git repo
    """
    try:
        # Try to get the remote origin URL
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            remote_url = result.stdout.strip()
            # Extract repo name from URL (handles https:// and git@ formats)
            if "/" in remote_url:
                repo_name = remote_url.split("/")[-1]
                # Remove .git suffix if present
                if repo_name.endswith(".git"):
                    repo_name = repo_name[:-4]
                return repo_name

        # Fallback: get directory name
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            repo_path = result.stdout.strip()
            return Path(repo_path).name
    except (subprocess.SubprocessError, OSError):
        pass

    return None


class GACStats(TypedDict):
    """TypedDict for GAC usage statistics."""

    total_gacs: int  # Number of gac workflow runs
    total_commits: int  # Number of actual commits created
    first_used: str | None
    last_used: str | None
    daily_gacs: dict[str, int]  # date -> gac count
    daily_commits: dict[str, int]  # date -> commit count
    weekly_gacs: dict[str, int]  # ISO week (e.g. 2026-W18) -> gac count
    weekly_commits: dict[str, int]  # ISO week -> commit count
    projects: dict[str, Any]  # project_name -> {gacs, commits}


def load_stats() -> GACStats:
    """Load statistics from the stats file.

    Returns:
        GACStats dictionary with usage statistics
    """
    empty: GACStats = {
        "total_gacs": 0,
        "total_commits": 0,
        "first_used": None,
        "last_used": None,
        "daily_gacs": {},
        "daily_commits": {},
        "weekly_gacs": {},
        "weekly_commits": {},
        "projects": {},
    }

    if not STATS_FILE.exists():
        return empty

    try:
        with open(STATS_FILE) as f:
            data = json.load(f)
        return {
            "total_gacs": data.get("total_gacs", 0),
            "total_commits": data.get("total_commits", 0),
            "first_used": data.get("first_used"),
            "last_used": data.get("last_used"),
            "daily_gacs": data.get("daily_gacs", {}),
            "daily_commits": data.get("daily_commits", {}),
            "weekly_gacs": data.get("weekly_gacs", {}),
            "weekly_commits": data.get("weekly_commits", {}),
            "projects": data.get("projects", {}),
        }
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Failed to load stats: {e}")
        return empty


def save_stats(stats: GACStats) -> None:
    """Save statistics to the stats file.

    Args:
        stats: GACStats dictionary to save
    """
    try:
        STATS_FILE.write_text(json.dumps(stats, indent=2))
    except OSError as e:
        logger.warning(f"Failed to save stats: {e}")


def record_gac(project_name: str | None = None) -> None:
    """Record a gac workflow run in the statistics.

    Args:
        project_name: Name of the project. Auto-detected from git if not provided.

    This should be called when a gac workflow starts (after validation passes).

    Does nothing if GAC_DISABLE_STATS environment variable is set.
    """
    if not stats_enabled():
        return

    if project_name is None:
        project_name = get_current_project_name()

    stats = load_stats()
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")

    # Update total gacs
    stats["total_gacs"] += 1

    # Set first_used if this is the first gac
    if stats["first_used"] is None:
        stats["first_used"] = now.isoformat()

    # Update last_used
    stats["last_used"] = now.isoformat()

    # Update daily gac count
    if today not in stats["daily_gacs"]:
        stats["daily_gacs"][today] = 0
    stats["daily_gacs"][today] += 1

    # Update weekly gac count
    iso_week = now.isocalendar()
    week_key = f"{iso_week[0]}-W{iso_week[1]:02d}"
    if week_key not in stats["weekly_gacs"]:
        stats["weekly_gacs"][week_key] = 0
    stats["weekly_gacs"][week_key] += 1

    # Update project stats
    if project_name:
        if project_name not in stats["projects"]:
            stats["projects"][project_name] = {"gacs": 0, "commits": 0}
        stats["projects"][project_name]["gacs"] += 1

    save_stats(stats)
    logger.debug(f"Recorded gac. Total gacs: {stats['total_gacs']}")


def record_commit(project_name: str | None = None) -> None:
    """Record a successful commit in the statistics.

    Args:
        project_name: Name of the project. Auto-detected from git if not provided.

    This should be called after a commit is successfully created.

    Does nothing if GAC_DISABLE_STATS environment variable is set.
    """
    if not stats_enabled():
        return

    if project_name is None:
        project_name = get_current_project_name()

    stats = load_stats()
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")

    # Update total commits
    stats["total_commits"] += 1

    # Update daily commit count
    if today not in stats["daily_commits"]:
        stats["daily_commits"][today] = 0
    stats["daily_commits"][today] += 1

    # Update weekly commit count
    iso_week = now.isocalendar()
    week_key = f"{iso_week[0]}-W{iso_week[1]:02d}"
    if week_key not in stats["weekly_commits"]:
        stats["weekly_commits"][week_key] = 0
    stats["weekly_commits"][week_key] += 1

    # Update last_used on every commit
    stats["last_used"] = now.isoformat()

    # Update project stats
    if project_name:
        if project_name not in stats["projects"]:
            stats["projects"][project_name] = {"gacs": 0, "commits": 0}
        stats["projects"][project_name]["commits"] += 1

    save_stats(stats)
    logger.debug(f"Recorded commit. Total commits: {stats['total_commits']}")


def get_stats_summary() -> dict[str, Any]:
    """Get a human-readable summary of usage statistics.

    Returns:
        Dictionary with formatted statistics
    """
    stats = load_stats()

    total_gacs = stats["total_gacs"]
    total_commits = stats["total_commits"]
    first_used = stats["first_used"]
    last_used = stats["last_used"]
    daily_gacs = stats["daily_gacs"]
    daily_commits = stats["daily_commits"]
    weekly_gacs = stats["weekly_gacs"]
    weekly_commits = stats["weekly_commits"]

    # Calculate streaks (based on gacs, not commits)
    today = datetime.now().strftime("%Y-%m-%d")
    streak = 0
    longest_streak = 0

    if daily_gacs:
        sorted_days = sorted(daily_gacs.keys())

        # Calculate longest streak
        longest_streak = 1
        current_longest = 1
        for i in range(1, len(sorted_days)):
            prev_day = datetime.strptime(sorted_days[i - 1], "%Y-%m-%d")
            curr_day = datetime.strptime(sorted_days[i], "%Y-%m-%d")
            if (curr_day - prev_day).days == 1:
                current_longest += 1
                longest_streak = max(longest_streak, current_longest)
            else:
                current_longest = 1

        # Calculate current streak (from today backwards)
        sorted_days_rev = sorted(daily_gacs.keys(), reverse=True)
        current_streak = 0
        check_date = datetime.now()

        for day_str in sorted_days_rev:
            day = datetime.strptime(day_str, "%Y-%m-%d")
            expected_diff = (check_date - day).days

            if expected_diff == current_streak:
                current_streak += 1
            elif expected_diff > current_streak:
                break

        streak = current_streak

    # Today's stats
    today_gacs = daily_gacs.get(today, 0)
    today_commits = daily_commits.get(today, 0)

    # This week's stats
    iso_week = datetime.now().isocalendar()
    week_key = f"{iso_week[0]}-W{iso_week[1]:02d}"
    week_gacs = weekly_gacs.get(week_key, 0)
    week_commits = weekly_commits.get(week_key, 0)

    # Format dates
    first_used_str = "Never" if first_used is None else datetime.fromisoformat(first_used).strftime("%Y-%m-%d")
    last_used_str = "Never" if last_used is None else datetime.fromisoformat(last_used).strftime("%Y-%m-%d")

    # Get projects and sort by total activity
    projects = stats.get("projects", {})

    top_projects = sorted(projects.items(), key=project_activity, reverse=True)

    # Calculate peak single-day stats
    peak_daily_gacs: int = max(daily_gacs.values()) if daily_gacs else 0
    peak_daily_commits: int = max(daily_commits.values()) if daily_commits else 0

    # Calculate peak weekly stats
    peak_weekly_gacs: int = max(weekly_gacs.values()) if weekly_gacs else 0
    peak_weekly_commits: int = max(weekly_commits.values()) if weekly_commits else 0

    return {
        "total_gacs": total_gacs,
        "total_commits": total_commits,
        "first_used": first_used_str,
        "last_used": last_used_str,
        "today_gacs": today_gacs,
        "today_commits": today_commits,
        "week_gacs": week_gacs,
        "week_commits": week_commits,
        "streak": streak,
        "longest_streak": longest_streak,
        "daily_gacs": daily_gacs,
        "daily_commits": daily_commits,
        "weekly_gacs": weekly_gacs,
        "weekly_commits": weekly_commits,
        "peak_daily_gacs": peak_daily_gacs,
        "peak_daily_commits": peak_daily_commits,
        "peak_weekly_gacs": peak_weekly_gacs,
        "peak_weekly_commits": peak_weekly_commits,
        "top_projects": top_projects,
    }


def project_activity(project_data: tuple[str, Any]) -> int:
    """Sort key for projects by total activity (gacs + commits).

    Args:
        project_data: Tuple of (project_name, data) where data is a dict
            with 'gacs' and 'commits' keys.

    Returns:
        Total activity count for sorting.
    """
    data = project_data[1]
    return int(data.get("gacs", 0)) + int(data.get("commits", 0))


def reset_stats() -> None:
    """Reset all statistics to zero."""
    empty_stats: GACStats = {
        "total_gacs": 0,
        "total_commits": 0,
        "first_used": None,
        "last_used": None,
        "daily_gacs": {},
        "daily_commits": {},
        "weekly_gacs": {},
        "weekly_commits": {},
        "projects": {},
    }
    save_stats(empty_stats)
    logger.info("Statistics reset")
