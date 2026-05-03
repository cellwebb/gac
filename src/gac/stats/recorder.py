"""Stats recording — functions that write usage data on each gac/commit/token event."""

import logging
from datetime import datetime

import gac.stats.store as store

logger = logging.getLogger(__name__)

# Module-level accumulator for per-gac token totals.
# record_tokens() adds to this; record_gac() finalizes it and resets.
#
# ⚠️  MAINTAINER NOTE: Any code path that calls record_tokens() but does NOT
# call record_gac() (e.g. dry_run, message_only, user abort, generation
# failure) MUST call reset_gac_token_accumulator() before returning.
# Without this, a long-lived process (MCP server) will leak leftover
# tokens into the next successful request and inflate biggest_gac_tokens.


class TokenAccumulator:
    """Encapsulated mutable state for per-gac token tracking."""

    def __init__(self) -> None:
        self._current_tokens: int = 0
        self._is_new_biggest: bool = False

    def add(self, tokens: int) -> None:
        self._current_tokens += tokens

    def reset(self) -> None:
        self._current_tokens = 0

    @property
    def current(self) -> int:
        return self._current_tokens

    @property
    def is_new_biggest(self) -> bool:
        return self._is_new_biggest

    @is_new_biggest.setter
    def is_new_biggest(self, value: bool) -> None:
        self._is_new_biggest = value


# Module-level singleton — existing code continues to work
_accumulator = TokenAccumulator()


def reset_gac_token_accumulator() -> None:
    """Reset the per-gac token accumulator.

    Call this on **every** code path where ``record_tokens()`` was invoked
    but ``record_gac()`` will not be (e.g. ``message_only``, ``dry_run``,
    user abort, generation failure).  Without this, a long-lived process
    (MCP server) would leak leftover tokens into the next successful
    request and inflate ``biggest_gac_tokens``.

    One-shot CLI invocations do not strictly need this (the process
    exits), but calling it is good hygiene and keeps code paths
    consistent between CLI and MCP.
    """
    _accumulator.reset()


def _set_new_biggest_gac(value: bool) -> None:
    """Internal setter for _new_biggest_gac flag (used by reset_stats)."""
    _accumulator.is_new_biggest = value


def record_gac(project_name: str | None = None, model: str | None = None) -> None:
    """Record a gac workflow run in the statistics.

    Args:
        project_name: Name of the project. Auto-detected from git if not provided.
        model: Name of the AI model used for this gac (e.g. 'anthropic:claude-haiku-4-5').

    This should be called when a gac workflow starts (after validation passes).

    Does nothing if GAC_DISABLE_STATS environment variable is set.
    """
    if not store.stats_enabled():
        return

    if project_name is None:
        project_name = store.get_current_project_name()

    stats = store.load_stats()
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
                "timed_reasoning_tokens": 0,
                "min_duration_ms": 0,
                "max_duration_ms": 0,
            }
        stats["models"][model]["gacs"] += 1

    # Finalize per-gac token total: check if this gac is the biggest ever
    _accumulator.is_new_biggest = False
    if _accumulator.current > 0 and _accumulator.current > stats.get("biggest_gac_tokens", 0):
        stats["biggest_gac_tokens"] = _accumulator.current
        stats["biggest_gac_date"] = now.isoformat()
        _accumulator.is_new_biggest = True
    _accumulator.reset()

    store.save_stats(stats)
    logger.debug(f"Recorded gac. Total gacs: {stats['total_gacs']}")


def record_commit(project_name: str | None = None) -> None:
    """Record a successful commit in the statistics.

    Args:
        project_name: Name of the project. Auto-detected from git if not provided.

    This should be called after a commit is successfully created.

    Does nothing if GAC_DISABLE_STATS environment variable is set.
    """
    if not store.stats_enabled():
        return

    if project_name is None:
        project_name = store.get_current_project_name()

    stats = store.load_stats()
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

    store.save_stats(stats)
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
    if not store.stats_enabled():
        return

    if prompt_tokens <= 0 and completion_tokens <= 0:
        return

    if project_name is None:
        project_name = store.get_current_project_name()

    stats = store.load_stats()
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    iso_week = now.isocalendar()
    week_key = f"{iso_week[0]}-W{iso_week[1]:02d}"

    stats["total_prompt_tokens"] += prompt_tokens
    stats["total_completion_tokens"] += completion_tokens
    stats["total_reasoning_tokens"] = stats.get("total_reasoning_tokens", 0) + reasoning_tokens

    # Accumulate into per-gac token total (finalized by record_gac)
    _accumulator.add(prompt_tokens + completion_tokens + reasoning_tokens)

    stats["daily_prompt_tokens"][today] = stats["daily_prompt_tokens"].get(today, 0) + prompt_tokens
    stats["daily_completion_tokens"][today] = stats["daily_completion_tokens"].get(today, 0) + completion_tokens
    stats["daily_reasoning_tokens"][today] = stats.get("daily_reasoning_tokens", {}).get(today, 0) + reasoning_tokens
    stats["weekly_prompt_tokens"][week_key] = stats["weekly_prompt_tokens"].get(week_key, 0) + prompt_tokens
    stats["weekly_completion_tokens"][week_key] = stats["weekly_completion_tokens"].get(week_key, 0) + completion_tokens
    stats["weekly_reasoning_tokens"][week_key] = (
        stats.get("weekly_reasoning_tokens", {}).get(week_key, 0) + reasoning_tokens
    )

    if project_name:
        if project_name not in stats["projects"]:
            stats["projects"][project_name] = {
                "gacs": 0,
                "commits": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "reasoning_tokens": 0,
            }
        proj = stats["projects"][project_name]
        proj["prompt_tokens"] = proj.get("prompt_tokens", 0) + prompt_tokens
        proj["completion_tokens"] = proj.get("completion_tokens", 0) + completion_tokens
        proj["reasoning_tokens"] = proj.get("reasoning_tokens", 0) + reasoning_tokens

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
                "timed_reasoning_tokens": 0,
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
            m["timed_reasoning_tokens"] = m.get("timed_reasoning_tokens", 0) + reasoning_tokens
            if m.get("duration_count", 0) == 1:
                m["min_duration_ms"] = duration_ms
                m["max_duration_ms"] = duration_ms
            else:
                m["min_duration_ms"] = min(m.get("min_duration_ms", 0), duration_ms)
                m["max_duration_ms"] = max(m.get("max_duration_ms", 0), duration_ms)

    store.save_stats(stats)
    logger.debug(
        f"Recorded tokens. Total prompt: {stats['total_prompt_tokens']}, completion: {stats['total_completion_tokens']}"
    )
