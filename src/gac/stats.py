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

# Module-level accumulator for per-gac token totals.
# record_tokens() adds to this; record_gac() finalizes it and resets.
# In long-lived processes (e.g. MCP server), non-committing return paths
# must call reset_gac_token_accumulator() to avoid leaking tokens into
# the next request.
_current_gac_tokens: int = 0
# Flag set by record_gac when this run beat the previous biggest_gac_tokens record.
_new_biggest_gac: bool = False


def reset_gac_token_accumulator() -> None:
    """Reset the per-gac token accumulator.

    Call this on code paths where ``record_tokens()`` was invoked but
    ``record_gac()`` will not be (e.g. ``message_only``, ``dry_run``,
    user abort).  Without this, a long-lived process (MCP server) would
    leak leftover tokens into the next successful request and inflate
    ``biggest_gac_tokens``.

    One-shot CLI invocations do not strictly need this (the process
    exits), but calling it is good hygiene.
    """
    global _current_gac_tokens
    _current_gac_tokens = 0


_FALSY_VALUES = {"", "0", "false", "no", "off", "n"}

_DURATION_DEFAULTS: dict[str, int] = {
    "total_duration_ms": 0,
    "duration_count": 0,
    "timed_completion_tokens": 0,
    "min_duration_ms": 0,
    "max_duration_ms": 0,
    "reasoning_tokens": 0,
}


def _normalize_models(models: dict[str, Any]) -> dict[str, Any]:
    for _name, data in models.items():
        for field, default in _DURATION_DEFAULTS.items():
            data.setdefault(field, default)
    return models


def _enrich_models_with_speed(models: list[tuple[str, Any]]) -> list[tuple[str, Any]]:
    enriched: list[tuple[str, Any]] = []
    for name, data in models:
        if data.get("duration_count", 0) > 0 and data.get("total_duration_ms", 0) > 0:
            avg_tps = round(data["timed_completion_tokens"] * 1000 / data["total_duration_ms"])
        else:
            avg_tps = None
        enriched.append((name, {**data, "avg_tps": avg_tps}))
    return enriched


def _safe_format_date(iso_str: Any) -> str:
    """Format an ISO datetime string to YYYY-MM-DD, returning a safe fallback on failure.

    If the input is not a string or cannot be parsed, returns "?" to prevent
    downstream code from crashing on ``.split("-")`` or similar string ops.
    """
    if not isinstance(iso_str, str):
        return "?"
    try:
        return datetime.fromisoformat(iso_str).strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        # Return a fallback that .split("-") won't crash on
        return "?"


def stats_enabled() -> bool:
    """Check if stats tracking is enabled.

    Disabled only when GAC_DISABLE_STATS is set to a truthy value
    (e.g. ``true``, ``1``, ``yes``). Falsy values (``false``, ``0``, ``no``,
    ``off``, empty string) leave stats enabled.
    """
    raw = os.environ.get("GAC_DISABLE_STATS")
    if raw is None:
        return True
    return raw.strip().lower() in _FALSY_VALUES


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
    total_prompt_tokens: int  # Total prompt tokens consumed
    total_completion_tokens: int  # Total completion tokens consumed
    biggest_gac_tokens: int  # Most tokens (prompt+completion+reasoning) in a single gac run
    biggest_gac_date: str | None  # ISO datetime when the biggest gac occurred
    first_used: str | None
    last_used: str | None
    daily_gacs: dict[str, int]  # date -> gac count
    daily_commits: dict[str, int]  # date -> commit count
    daily_prompt_tokens: dict[str, int]  # date -> prompt token count
    daily_completion_tokens: dict[str, int]  # date -> completion token count
    weekly_gacs: dict[str, int]  # ISO week (e.g. 2026-W18) -> gac count
    weekly_commits: dict[str, int]  # ISO week -> commit count
    weekly_prompt_tokens: dict[str, int]  # ISO week -> prompt token count
    weekly_completion_tokens: dict[str, int]  # ISO week -> completion token count
    projects: dict[str, Any]  # project_name -> {gacs, commits, prompt_tokens, completion_tokens}
    models: dict[str, Any]  # model_name -> {gacs, prompt_tokens, completion_tokens}


def load_stats() -> GACStats:
    """Load statistics from the stats file.

    Returns:
        GACStats dictionary with usage statistics
    """
    empty: GACStats = {
        "total_gacs": 0,
        "total_commits": 0,
        "total_prompt_tokens": 0,
        "total_completion_tokens": 0,
        "biggest_gac_tokens": 0,
        "biggest_gac_date": None,
        "first_used": None,
        "last_used": None,
        "daily_gacs": {},
        "daily_commits": {},
        "daily_prompt_tokens": {},
        "daily_completion_tokens": {},
        "weekly_gacs": {},
        "weekly_commits": {},
        "weekly_prompt_tokens": {},
        "weekly_completion_tokens": {},
        "projects": {},
        "models": {},
    }

    if not STATS_FILE.exists():
        return empty

    try:
        with open(STATS_FILE) as f:
            data = json.load(f)
        return {
            "total_gacs": data.get("total_gacs", 0),
            "total_commits": data.get("total_commits", 0),
            "total_prompt_tokens": data.get("total_prompt_tokens", 0),
            "total_completion_tokens": data.get("total_completion_tokens", 0),
            "biggest_gac_tokens": data.get("biggest_gac_tokens", 0),
            "biggest_gac_date": data.get("biggest_gac_date"),
            "first_used": data.get("first_used"),
            "last_used": data.get("last_used"),
            "daily_gacs": data.get("daily_gacs", {}),
            "daily_commits": data.get("daily_commits", {}),
            "daily_prompt_tokens": data.get("daily_prompt_tokens", {}),
            "daily_completion_tokens": data.get("daily_completion_tokens", {}),
            "weekly_gacs": data.get("weekly_gacs", {}),
            "weekly_commits": data.get("weekly_commits", {}),
            "weekly_prompt_tokens": data.get("weekly_prompt_tokens", {}),
            "weekly_completion_tokens": data.get("weekly_completion_tokens", {}),
            "projects": data.get("projects", {}),
            "models": _normalize_models(data.get("models", {})),
        }
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Failed to load stats: {e}")
        return empty


def save_stats(stats: GACStats) -> None:
    """Save statistics to the stats file atomically.

    Writes to a temporary file in the same directory and then renames it
    over the destination so an interrupted write cannot leave a truncated
    or partially-written JSON file behind.

    Args:
        stats: GACStats dictionary to save
    """
    # Write to a sibling temp file then atomic-rename. os.replace is
    # atomic on POSIX and Windows when source and dest are on the same
    # filesystem, which they are here (sibling of STATS_FILE).
    tmp_file = STATS_FILE.with_suffix(STATS_FILE.suffix + f".tmp.{os.getpid()}")
    try:
        STATS_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp_file.write_text(json.dumps(stats, indent=2))
        os.replace(tmp_file, STATS_FILE)
    except OSError as e:
        logger.warning(f"Failed to save stats: {e}")
        try:
            tmp_file.unlink(missing_ok=True)
        except OSError:
            pass


def record_gac(project_name: str | None = None, model: str | None = None) -> None:
    """Record a gac workflow run in the statistics.

    Args:
        project_name: Name of the project. Auto-detected from git if not provided.
        model: Name of the AI model used for this gac (e.g. 'anthropic:claude-haiku-4-5').

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
            stats["projects"][project_name] = {
                "gacs": 0,
                "commits": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
            }
        stats["projects"][project_name]["gacs"] += 1

    # Update model stats
    if model:
        if model not in stats["models"]:
            stats["models"][model] = {
                "gacs": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_duration_ms": 0,
                "duration_count": 0,
                "timed_completion_tokens": 0,
                "min_duration_ms": 0,
                "max_duration_ms": 0,
            }
        stats["models"][model]["gacs"] += 1

    # Finalize per-gac token total: check if this gac is the biggest ever
    global _current_gac_tokens, _new_biggest_gac
    _new_biggest_gac = False
    if _current_gac_tokens > 0 and _current_gac_tokens > stats.get("biggest_gac_tokens", 0):
        stats["biggest_gac_tokens"] = _current_gac_tokens
        stats["biggest_gac_date"] = now.isoformat()
        _new_biggest_gac = True
    _current_gac_tokens = 0  # Reset accumulator for the next gac

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
            stats["projects"][project_name] = {
                "gacs": 0,
                "commits": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
            }
        stats["projects"][project_name]["commits"] += 1

    save_stats(stats)
    logger.debug(f"Recorded commit. Total commits: {stats['total_commits']}")


def record_tokens(
    prompt_tokens: int,
    completion_tokens: int,
    model: str | None = None,
    project_name: str | None = None,
    duration_ms: int | None = None,
    reasoning_tokens: int = 0,
) -> None:
    """Record token usage for an AI generation call.

    Args:
        prompt_tokens: Number of prompt (input) tokens used.
        completion_tokens: Number of completion (output) tokens used.
        model: Name of the AI model used (e.g. 'anthropic:claude-haiku-4-5').
        project_name: Name of the project. Auto-detected from git if not provided.
        duration_ms: Wall-clock duration of the API call in milliseconds. When provided and > 0,
            per-model speed tracking fields are updated.
        reasoning_tokens: Number of reasoning/thinking tokens used by the model.

    Does nothing if GAC_DISABLE_STATS environment variable is set.
    """
    if not stats_enabled():
        return

    if prompt_tokens <= 0 and completion_tokens <= 0:
        return

    if project_name is None:
        project_name = get_current_project_name()

    stats = load_stats()
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    iso_week = now.isocalendar()
    week_key = f"{iso_week[0]}-W{iso_week[1]:02d}"

    stats["total_prompt_tokens"] += prompt_tokens
    stats["total_completion_tokens"] += completion_tokens

    # Accumulate into per-gac token total (finalized by record_gac)
    global _current_gac_tokens
    _current_gac_tokens += prompt_tokens + completion_tokens + reasoning_tokens

    stats["daily_prompt_tokens"][today] = stats["daily_prompt_tokens"].get(today, 0) + prompt_tokens
    stats["daily_completion_tokens"][today] = stats["daily_completion_tokens"].get(today, 0) + completion_tokens
    stats["weekly_prompt_tokens"][week_key] = stats["weekly_prompt_tokens"].get(week_key, 0) + prompt_tokens
    stats["weekly_completion_tokens"][week_key] = stats["weekly_completion_tokens"].get(week_key, 0) + completion_tokens

    if project_name:
        if project_name not in stats["projects"]:
            stats["projects"][project_name] = {
                "gacs": 0,
                "commits": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
            }
        proj = stats["projects"][project_name]
        proj["prompt_tokens"] = proj.get("prompt_tokens", 0) + prompt_tokens
        proj["completion_tokens"] = proj.get("completion_tokens", 0) + completion_tokens

    if model:
        if model not in stats["models"]:
            stats["models"][model] = {
                "gacs": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "reasoning_tokens": 0,
                "total_duration_ms": 0,
                "duration_count": 0,
                "timed_completion_tokens": 0,
                "min_duration_ms": 0,
                "max_duration_ms": 0,
            }
        m = stats["models"][model]
        m["prompt_tokens"] = m.get("prompt_tokens", 0) + prompt_tokens
        m["completion_tokens"] = m.get("completion_tokens", 0) + completion_tokens
        m["reasoning_tokens"] = m.get("reasoning_tokens", 0) + reasoning_tokens
        if duration_ms is not None and duration_ms > 0:
            m["total_duration_ms"] = m.get("total_duration_ms", 0) + duration_ms
            m["duration_count"] = m.get("duration_count", 0) + 1
            m["timed_completion_tokens"] = m.get("timed_completion_tokens", 0) + completion_tokens
            if m.get("duration_count", 0) == 1:
                m["min_duration_ms"] = duration_ms
                m["max_duration_ms"] = duration_ms
            else:
                m["min_duration_ms"] = min(m.get("min_duration_ms", 0), duration_ms)
                m["max_duration_ms"] = max(m.get("max_duration_ms", 0), duration_ms)

    save_stats(stats)
    logger.debug(
        f"Recorded tokens. Total prompt: {stats['total_prompt_tokens']}, completion: {stats['total_completion_tokens']}"
    )


def get_stats_summary() -> dict[str, Any]:
    """Get a human-readable summary of usage statistics.

    Returns:
        Dictionary with formatted statistics
    """
    stats = load_stats()

    total_gacs = stats["total_gacs"]
    total_commits = stats["total_commits"]
    total_prompt_tokens = stats.get("total_prompt_tokens", 0)
    total_completion_tokens = stats.get("total_completion_tokens", 0)
    total_tokens = total_prompt_tokens + total_completion_tokens
    biggest_gac_tokens = stats.get("biggest_gac_tokens", 0)
    biggest_gac_date = stats.get("biggest_gac_date")
    first_used = stats["first_used"]
    last_used = stats["last_used"]
    daily_gacs = stats["daily_gacs"]
    daily_commits = stats["daily_commits"]
    daily_prompt_tokens = stats.get("daily_prompt_tokens", {})
    daily_completion_tokens = stats.get("daily_completion_tokens", {})
    weekly_gacs = stats["weekly_gacs"]
    weekly_commits = stats["weekly_commits"]
    weekly_prompt_tokens = stats.get("weekly_prompt_tokens", {})
    weekly_completion_tokens = stats.get("weekly_completion_tokens", {})

    # Combine daily/weekly token totals (prompt + completion) for peak/period display
    daily_total_tokens: dict[str, int] = {}
    for day_key in set(daily_prompt_tokens) | set(daily_completion_tokens):
        daily_total_tokens[day_key] = daily_prompt_tokens.get(day_key, 0) + daily_completion_tokens.get(day_key, 0)
    weekly_total_tokens: dict[str, int] = {}
    for wk in set(weekly_prompt_tokens) | set(weekly_completion_tokens):
        weekly_total_tokens[wk] = weekly_prompt_tokens.get(wk, 0) + weekly_completion_tokens.get(wk, 0)

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
    today_tokens = daily_total_tokens.get(today, 0)

    # This week's stats
    iso_week = datetime.now().isocalendar()
    week_key = f"{iso_week[0]}-W{iso_week[1]:02d}"
    week_gacs = weekly_gacs.get(week_key, 0)
    week_commits = weekly_commits.get(week_key, 0)
    week_tokens = weekly_total_tokens.get(week_key, 0)

    # Format dates (defensive: malformed persisted values degrade gracefully)
    first_used_str = "Never" if first_used is None else _safe_format_date(first_used)
    last_used_str = "Never" if last_used is None else _safe_format_date(last_used)
    biggest_gac_date_str = None if biggest_gac_date is None else _safe_format_date(biggest_gac_date)

    # Coerce biggest_gac_tokens to int safely
    try:
        biggest_gac_tokens = int(biggest_gac_tokens)
    except (ValueError, TypeError):
        biggest_gac_tokens = 0

    # Get projects and sort by total activity
    projects = stats.get("projects", {})

    top_projects = sorted(projects.items(), key=project_activity, reverse=True)

    models = stats.get("models", {})
    top_models = _enrich_models_with_speed(sorted(models.items(), key=model_activity, reverse=True))

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
        "daily_total_tokens": daily_total_tokens,
        "weekly_gacs": weekly_gacs,
        "weekly_commits": weekly_commits,
        "weekly_prompt_tokens": weekly_prompt_tokens,
        "weekly_completion_tokens": weekly_completion_tokens,
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


def model_activity(model_data: tuple[str, Any]) -> int:
    """Sort key for models by gacs (workflow uses).

    Args:
        model_data: Tuple of (model_name, data) where data is a dict
            with 'gacs', 'prompt_tokens', and 'completion_tokens' keys.

    Returns:
        Number of gacs run with this model.
    """
    data = model_data[1]
    return int(data.get("gacs", 0))


def reset_stats() -> None:
    """Reset all statistics to zero."""
    empty_stats: GACStats = {
        "total_gacs": 0,
        "total_commits": 0,
        "total_prompt_tokens": 0,
        "total_completion_tokens": 0,
        "biggest_gac_tokens": 0,
        "biggest_gac_date": None,
        "first_used": None,
        "last_used": None,
        "daily_gacs": {},
        "daily_commits": {},
        "daily_prompt_tokens": {},
        "daily_completion_tokens": {},
        "weekly_gacs": {},
        "weekly_commits": {},
        "weekly_prompt_tokens": {},
        "weekly_completion_tokens": {},
        "projects": {},
        "models": {},
    }
    save_stats(empty_stats)
    global _new_biggest_gac
    reset_gac_token_accumulator()
    _new_biggest_gac = False
    logger.info("Statistics reset")
