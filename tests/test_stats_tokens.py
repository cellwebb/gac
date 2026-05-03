"""Tests for token recording, model tracking, disable/enable flags, and token summaries."""

from datetime import datetime
from unittest.mock import patch

import pytest

from gac.stats import (
    GACStats,
    get_stats_summary,
    load_stats,
    record_gac,
    record_tokens,
)


def _empty_stats() -> GACStats:
    return {
        "total_gacs": 0,
        "total_commits": 0,
        "total_prompt_tokens": 0,
        "total_completion_tokens": 0,
        "total_reasoning_tokens": 0,
        "biggest_gac_tokens": 0,
        "biggest_gac_date": None,
        "first_used": None,
        "last_used": None,
        "daily_gacs": {},
        "daily_commits": {},
        "daily_prompt_tokens": {},
        "daily_completion_tokens": {},
        "daily_reasoning_tokens": {},
        "weekly_gacs": {},
        "weekly_commits": {},
        "weekly_prompt_tokens": {},
        "weekly_completion_tokens": {},
        "weekly_reasoning_tokens": {},
        "projects": {},
        "models": {},
        "_version": 2,
    }


class TestRecordTokens:
    """Tests for record_tokens function."""

    def test_record_tokens_basic(self, tmp_path):
        """Test recording prompt and completion tokens updates totals."""
        stats_file = tmp_path / "stats.json"

        with patch("gac.stats.store.STATS_FILE", stats_file):
            record_tokens(100, 50, model="anthropic:test-model")

            stats = load_stats()
            assert stats["total_prompt_tokens"] == 100
            assert stats["total_completion_tokens"] == 50

    def test_record_tokens_accumulates(self, tmp_path):
        """Test that token counts accumulate across calls."""
        stats_file = tmp_path / "stats.json"

        with patch("gac.stats.store.STATS_FILE", stats_file):
            record_tokens(100, 50, model="anthropic:test-model")
            record_tokens(200, 75, model="anthropic:test-model")

            stats = load_stats()
            assert stats["total_prompt_tokens"] == 300
            assert stats["total_completion_tokens"] == 125

    def test_record_tokens_updates_daily_and_weekly(self, tmp_path):
        """Test daily and weekly token buckets are updated."""
        stats_file = tmp_path / "stats.json"
        today = datetime.now().strftime("%Y-%m-%d")
        iso_week = datetime.now().isocalendar()
        week_key = f"{iso_week[0]}-W{iso_week[1]:02d}"

        with patch("gac.stats.store.STATS_FILE", stats_file):
            record_tokens(100, 50)

            stats = load_stats()
            assert stats["daily_prompt_tokens"][today] == 100
            assert stats["daily_completion_tokens"][today] == 50
            assert stats["weekly_prompt_tokens"][week_key] == 100
            assert stats["weekly_completion_tokens"][week_key] == 50

    def test_record_tokens_per_model(self, tmp_path):
        """Test tokens are tracked per model."""
        stats_file = tmp_path / "stats.json"

        with patch("gac.stats.store.STATS_FILE", stats_file):
            record_tokens(100, 50, model="anthropic:claude-haiku-4-5")
            record_tokens(200, 75, model="openai:gpt-5")
            record_tokens(50, 25, model="anthropic:claude-haiku-4-5")

            stats = load_stats()
            assert stats["models"]["anthropic:claude-haiku-4-5"]["prompt_tokens"] == 150
            assert stats["models"]["anthropic:claude-haiku-4-5"]["completion_tokens"] == 75
            assert stats["models"]["openai:gpt-5"]["prompt_tokens"] == 200
            assert stats["models"]["openai:gpt-5"]["completion_tokens"] == 75

    def test_record_tokens_per_project(self, tmp_path):
        """Test tokens are attributed to a project bucket."""
        stats_file = tmp_path / "stats.json"

        with patch("gac.stats.store.STATS_FILE", stats_file):
            record_tokens(100, 50, model="anthropic:test", project_name="proj-a")
            record_tokens(200, 75, model="anthropic:test", project_name="proj-b")
            record_tokens(50, 25, model="anthropic:test", project_name="proj-a")

            stats = load_stats()
            assert stats["projects"]["proj-a"]["prompt_tokens"] == 150
            assert stats["projects"]["proj-a"]["completion_tokens"] == 75
            assert stats["projects"]["proj-b"]["prompt_tokens"] == 200
            assert stats["projects"]["proj-b"]["completion_tokens"] == 75

    def test_record_tokens_disabled(self, tmp_path):
        """Test record_tokens does nothing when GAC_DISABLE_STATS is set."""
        stats_file = tmp_path / "stats.json"

        with patch("gac.stats.store.STATS_FILE", stats_file), patch.dict("os.environ", {"GAC_DISABLE_STATS": "1"}):
            record_tokens(100, 50, model="anthropic:test")

            stats = load_stats()
            assert stats["total_prompt_tokens"] == 0
            assert stats["total_completion_tokens"] == 0

    def test_record_tokens_zero_no_op(self, tmp_path):
        """Test record_tokens skips when both counts are zero."""
        stats_file = tmp_path / "stats.json"

        with patch("gac.stats.store.STATS_FILE", stats_file):
            record_tokens(0, 0, model="anthropic:test")

            assert not stats_file.exists() or load_stats()["total_prompt_tokens"] == 0


class TestRecordGacWithModel:
    """Tests for record_gac model tracking."""

    def test_record_gac_tracks_model(self, tmp_path):
        """Test record_gac increments model.gacs counter."""
        stats_file = tmp_path / "stats.json"

        with patch("gac.stats.store.STATS_FILE", stats_file):
            record_gac(model="anthropic:claude-haiku-4-5")
            record_gac(model="anthropic:claude-haiku-4-5")
            record_gac(model="openai:gpt-5")

            stats = load_stats()
            assert stats["models"]["anthropic:claude-haiku-4-5"]["gacs"] == 2
            assert stats["models"]["openai:gpt-5"]["gacs"] == 1

    def test_record_gac_no_model(self, tmp_path):
        """Test record_gac without model still increments totals."""
        stats_file = tmp_path / "stats.json"

        with patch("gac.stats.store.STATS_FILE", stats_file):
            record_gac()

            stats = load_stats()
            assert stats["total_gacs"] == 1


class TestSummaryWithTokens:
    """Tests for token-related fields in get_stats_summary."""

    def test_summary_includes_token_totals(self, tmp_path):
        """Test summary surfaces token totals and peaks."""
        stats_file = tmp_path / "stats.json"
        today = datetime.now().strftime("%Y-%m-%d")
        iso_week = datetime.now().isocalendar()
        week_key = f"{iso_week[0]}-W{iso_week[1]:02d}"

        stats: GACStats = _empty_stats()
        stats["total_prompt_tokens"] = 1000
        stats["total_completion_tokens"] = 500
        stats["daily_prompt_tokens"] = {today: 200, "2024-01-01": 800}
        stats["daily_completion_tokens"] = {today: 100, "2024-01-01": 400}
        stats["weekly_prompt_tokens"] = {week_key: 200}
        stats["weekly_completion_tokens"] = {week_key: 100}
        stats_file.write_text(stats_file.parent.joinpath("dummy").read_text() if False else "")
        import json

        stats_file.write_text(json.dumps(stats))

        with patch("gac.stats.store.STATS_FILE", stats_file):
            summary = get_stats_summary()
            assert summary["total_prompt_tokens"] == 1000
            assert summary["total_completion_tokens"] == 500
            assert summary["total_tokens"] == 1500
            assert summary["today_tokens"] == 300  # 200 + 100
            assert summary["peak_daily_tokens"] == 1200  # 2024-01-01 had 800+400
            assert summary["week_tokens"] == 300

    def test_summary_includes_top_models(self, tmp_path):
        """Test summary returns top_models sorted by gacs then total tokens."""
        import json

        stats_file = tmp_path / "stats.json"

        stats: GACStats = _empty_stats()
        stats["models"] = {
            "model-a": {"gacs": 5, "prompt_tokens": 500, "completion_tokens": 100},
            "model-b": {"gacs": 10, "prompt_tokens": 100, "completion_tokens": 50},
        }
        stats_file.write_text(json.dumps(stats))

        with patch("gac.stats.store.STATS_FILE", stats_file):
            summary = get_stats_summary()
            top = summary["top_models"]
            assert top[0][0] == "model-b"
            assert top[1][0] == "model-a"

    def test_top_models_tiebreak_by_total_tokens(self, tmp_path):
        """When models have equal gacs, the one with more total tokens sorts first."""
        import json

        stats_file = tmp_path / "stats.json"

        stats: GACStats = _empty_stats()
        stats["models"] = {
            "model-a": {"gacs": 5, "prompt_tokens": 500, "completion_tokens": 100, "reasoning_tokens": 50},
            "model-b": {"gacs": 5, "prompt_tokens": 1000, "completion_tokens": 200, "reasoning_tokens": 100},
            "model-c": {"gacs": 5, "prompt_tokens": 200, "completion_tokens": 50, "reasoning_tokens": 0},
        }
        stats_file.write_text(json.dumps(stats))

        with patch("gac.stats.store.STATS_FILE", stats_file):
            summary = get_stats_summary()
            top = summary["top_models"]
            # All have 5 gacs; sort by total tokens (prompt+completion+reasoning): b=1300, a=650, c=250
            assert top[0][0] == "model-b"
            assert top[1][0] == "model-a"
            assert top[2][0] == "model-c"


class TestDisableStats:
    """Tests for GAC_DISABLE_STATS environment variable."""

    def test_record_gac_disabled(self, tmp_path):
        """Test that record_gac does nothing when GAC_DISABLE_STATS is set."""
        stats_file = tmp_path / "stats.json"

        with patch("gac.stats.store.STATS_FILE", stats_file), patch.dict("os.environ", {"GAC_DISABLE_STATS": "1"}):
            record_gac()

            stats = load_stats()
            assert stats["total_gacs"] == 0

    def test_record_commit_disabled(self, tmp_path):
        """Test that record_commit does nothing when GAC_DISABLE_STATS is set."""
        from gac.stats import record_commit

        stats_file = tmp_path / "stats.json"

        with patch("gac.stats.store.STATS_FILE", stats_file), patch.dict("os.environ", {"GAC_DISABLE_STATS": "1"}):
            record_commit()

            stats = load_stats()
            assert stats["total_commits"] == 0

    def test_record_gac_enabled_by_default(self, tmp_path):
        """Test that record_gac works when GAC_DISABLE_STATS is not set."""
        stats_file = tmp_path / "stats.json"

        with patch("gac.stats.store.STATS_FILE", stats_file):
            # Ensure env var is not set
            import os

            if "GAC_DISABLE_STATS" in os.environ:
                del os.environ["GAC_DISABLE_STATS"]

            record_gac()

            stats = load_stats()
            assert stats["total_gacs"] == 1


class TestStatsEnabled:
    """Tests for stats_enabled() value parsing."""

    @pytest.mark.parametrize(
        "value",
        ["false", "False", "FALSE", "0", "no", "No", "off", "OFF", "n", "", "  false  "],
    )
    def test_falsy_values_keep_stats_enabled(self, value):
        from gac.stats import stats_enabled

        with patch.dict("os.environ", {"GAC_DISABLE_STATS": value}):
            assert stats_enabled() is True

    @pytest.mark.parametrize(
        "value",
        ["true", "True", "TRUE", "1", "yes", "Yes", "on", "y", "anything-else"],
    )
    def test_truthy_values_disable_stats(self, value):
        from gac.stats import stats_enabled

        with patch.dict("os.environ", {"GAC_DISABLE_STATS": value}):
            assert stats_enabled() is False

    def test_unset_keeps_stats_enabled(self, monkeypatch):
        from gac.stats import stats_enabled

        monkeypatch.delenv("GAC_DISABLE_STATS", raising=False)
        assert stats_enabled() is True
