"""Stats summary computation — formatting and aggregating usage data for display."""

from datetime import datetime
from typing import Any

import gac.stats.store as store


def get_stats_summary() -> dict[str, Any]:
    """Get a human-readable summary of usage statistics.

    Returns:
        Dictionary with formatted statistics
    """
    stats = store.load_stats()

    total_gacs = stats["total_gacs"]
    total_commits = stats["total_commits"]
    total_prompt_tokens = stats.get("total_prompt_tokens", 0)
    total_completion_tokens = stats.get("total_completion_tokens", 0)
    total_reasoning_tokens = stats.get("total_reasoning_tokens", 0)
    total_tokens = total_prompt_tokens + total_completion_tokens + total_reasoning_tokens
    biggest_gac_tokens = stats.get("biggest_gac_tokens", 0)
    biggest_gac_date = stats.get("biggest_gac_date")
    first_used = stats["first_used"]
    last_used = stats["last_used"]
    daily_gacs = stats["daily_gacs"]
    daily_commits = stats["daily_commits"]
    daily_prompt_tokens = stats.get("daily_prompt_tokens", {})
    daily_completion_tokens = stats.get("daily_completion_tokens", {})
    daily_reasoning_tokens = stats.get("daily_reasoning_tokens", {})
    weekly_gacs = stats["weekly_gacs"]
    weekly_commits = stats["weekly_commits"]
    weekly_prompt_tokens = stats.get("weekly_prompt_tokens", {})
    weekly_completion_tokens = stats.get("weekly_completion_tokens", {})
    weekly_reasoning_tokens = stats.get("weekly_reasoning_tokens", {})

    # Combine daily/weekly token totals
    daily_total_tokens: dict[str, int] = {}
    for day_key in set(daily_prompt_tokens) | set(daily_completion_tokens) | set(daily_reasoning_tokens):
        daily_total_tokens[day_key] = (
            daily_prompt_tokens.get(day_key, 0)
            + daily_completion_tokens.get(day_key, 0)
            + daily_reasoning_tokens.get(day_key, 0)
        )
    weekly_total_tokens: dict[str, int] = {}
    for wk in set(weekly_prompt_tokens) | set(weekly_completion_tokens) | set(weekly_reasoning_tokens):
        weekly_total_tokens[wk] = (
            weekly_prompt_tokens.get(wk, 0) + weekly_completion_tokens.get(wk, 0) + weekly_reasoning_tokens.get(wk, 0)
        )
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
    today_tokens = daily_total_tokens.get(today, 0)

    # This week's stats
    iso_week = datetime.now().isocalendar()
    week_key = f"{iso_week[0]}-W{iso_week[1]:02d}"
    week_gacs = weekly_gacs.get(week_key, 0)
    week_commits = weekly_commits.get(week_key, 0)
    week_tokens = weekly_total_tokens.get(week_key, 0)

    # Format dates (defensive: malformed persisted values degrade gracefully)
    first_used_str = "Never" if first_used is None else store._safe_format_date(first_used)
    last_used_str = "Never" if last_used is None else store._safe_format_date(last_used)
    biggest_gac_date_str = None if biggest_gac_date is None else store._safe_format_date(biggest_gac_date)

    # Coerce biggest_gac_tokens to int safely
    try:
        biggest_gac_tokens = int(biggest_gac_tokens)
    except (ValueError, TypeError):
        biggest_gac_tokens = 0

    # Get projects and sort by total activity
    projects = stats.get("projects", {})
    top_projects = sorted(projects.items(), key=store.project_activity, reverse=True)

    models = stats.get("models", {})
    top_models = store._enrich_models_with_speed(sorted(models.items(), key=store.model_activity, reverse=True))

    # Calculate peak single-day stats
    peak_daily_gacs: int = max(daily_gacs.values()) if daily_gacs else 0
    peak_daily_commits: int = max(daily_commits.values()) if daily_commits else 0
    peak_daily_tokens: int = max(daily_total_tokens.values()) if daily_total_tokens else 0

    # Calculate peak weekly stats
    peak_weekly_gacs: int = max(weekly_gacs.values()) if weekly_gacs else 0
    peak_weekly_commits: int = max(weekly_commits.values()) if weekly_commits else 0
    peak_weekly_tokens: int = max(weekly_total_tokens.values()) if weekly_total_tokens else 0

    return {
        "total_gacs": total_gacs,
        "total_commits": total_commits,
        "total_prompt_tokens": total_prompt_tokens,
        "total_completion_tokens": total_completion_tokens,
        "total_reasoning_tokens": total_reasoning_tokens,
        "total_tokens": total_tokens,
        "biggest_gac_tokens": biggest_gac_tokens,
        "biggest_gac_date": biggest_gac_date_str,
        "first_used": first_used_str,
        "last_used": last_used_str,
        "today_gacs": today_gacs,
        "today_commits": today_commits,
        "today_tokens": today_tokens,
        "week_gacs": week_gacs,
        "week_commits": week_commits,
        "week_tokens": week_tokens,
        "streak": streak,
        "longest_streak": longest_streak,
        "daily_gacs": daily_gacs,
        "daily_commits": daily_commits,
        "daily_prompt_tokens": daily_prompt_tokens,
        "daily_completion_tokens": daily_completion_tokens,
        "daily_reasoning_tokens": daily_reasoning_tokens,
        "daily_total_tokens": daily_total_tokens,
        "weekly_gacs": weekly_gacs,
        "weekly_commits": weekly_commits,
        "weekly_prompt_tokens": weekly_prompt_tokens,
        "weekly_completion_tokens": weekly_completion_tokens,
        "weekly_reasoning_tokens": weekly_reasoning_tokens,
        "weekly_total_tokens": weekly_total_tokens,
        "peak_daily_gacs": peak_daily_gacs,
        "peak_daily_commits": peak_daily_commits,
        "peak_daily_tokens": peak_daily_tokens,
        "peak_weekly_gacs": peak_weekly_gacs,
        "peak_weekly_commits": peak_weekly_commits,
        "peak_weekly_tokens": peak_weekly_tokens,
        "top_projects": top_projects,
        "top_models": top_models,
    }
