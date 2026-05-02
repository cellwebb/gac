"""Test suite for stats.py module."""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from gac.stats import (
    GACStats,
    get_stats_summary,
    load_stats,
    record_commit,
    record_gac,
    record_tokens,
    reset_stats,
    save_stats,
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
    }


class TestLoadStats:
    """Tests for load_stats function."""

    def test_load_stats_empty(self, tmp_path):
        """Test loading stats when file doesn't exist."""
        with patch("gac.stats.STATS_FILE", tmp_path / "nonexistent.json"):
            stats = load_stats()
            assert stats["total_commits"] == 0
            assert stats["first_used"] is None
            assert stats["last_used"] is None
            assert stats["daily_commits"] == {}

    def test_load_stats_existing(self, tmp_path):
        """Test loading stats from existing file."""
        stats_file = tmp_path / "stats.json"
        test_data = {
            "total_gacs": 20,
            "total_commits": 42,
            "first_used": "2024-01-01T00:00:00",
            "last_used": "2024-06-15T12:30:00",
            "daily_gacs": {"2024-06-15": 3},
            "daily_commits": {"2024-06-15": 5},
            "weekly_gacs": {"2024-W24": 3},
            "weekly_commits": {"2024-W24": 5},
            "projects": {},
        }
        stats_file.write_text(json.dumps(test_data))

        with patch("gac.stats.STATS_FILE", stats_file):
            stats = load_stats()
            assert stats["total_commits"] == 42
            assert stats["first_used"] == "2024-01-01T00:00:00"
            assert stats["last_used"] == "2024-06-15T12:30:00"
            assert stats["daily_commits"] == {"2024-06-15": 5}

    def test_load_stats_corrupted(self, tmp_path):
        """Test loading stats from corrupted file."""
        stats_file = tmp_path / "stats.json"
        stats_file.write_text("not valid json")

        with patch("gac.stats.STATS_FILE", stats_file):
            stats = load_stats()
            assert stats["total_commits"] == 0
            assert stats["first_used"] is None
            assert stats["last_used"] is None


class TestSaveStats:
    """Tests for save_stats function."""

    def test_save_stats_success(self, tmp_path):
        """Test saving stats to file."""
        stats_file = tmp_path / "stats.json"
        stats: GACStats = {
            "total_gacs": 5,
            "total_commits": 10,
            "first_used": "2024-01-01T00:00:00",
            "last_used": "2024-06-15T12:30:00",
            "daily_gacs": {"2024-06-15": 2},
            "daily_commits": {"2024-06-15": 3},
            "weekly_gacs": {},
            "weekly_commits": {},
            "projects": {},
        }

        with patch("gac.stats.STATS_FILE", stats_file):
            save_stats(stats)

        loaded = json.loads(stats_file.read_text())
        assert loaded["total_commits"] == 10

    def test_save_stats_io_error(self, tmp_path, caplog):
        """Test handling IO error when saving stats."""
        stats_file = tmp_path / "stats.json"
        stats: GACStats = {
            "total_gacs": 5,
            "total_commits": 10,
            "first_used": None,
            "last_used": None,
            "daily_gacs": {},
            "daily_commits": {},
            "weekly_gacs": {},
            "weekly_commits": {},
            "projects": {},
        }

        with patch("gac.stats.STATS_FILE", stats_file):
            with patch.object(Path, "write_text", side_effect=OSError("Permission denied")):
                with caplog.at_level("WARNING"):
                    save_stats(stats)
                assert "Failed to save stats" in caplog.text


class TestRecordCommit:
    """Tests for record_commit function."""

    def test_record_first_commit(self, tmp_path):
        """Test recording first commit."""
        stats_file = tmp_path / "stats.json"

        with patch("gac.stats.STATS_FILE", stats_file):
            # Now record_gac and record_commit are called together after successful commit
            record_commit()
            record_gac()

            stats = load_stats()
            assert stats["total_commits"] == 1
            assert stats["total_gacs"] == 1
            assert stats["first_used"] is not None
            assert stats["last_used"] is not None

    def test_record_multiple_commits(self, tmp_path):
        """Test recording multiple commits."""
        stats_file = tmp_path / "stats.json"

        with patch("gac.stats.STATS_FILE", stats_file):
            record_commit()
            record_commit()
            record_commit()

            stats = load_stats()
            assert stats["total_commits"] == 3

    def test_record_commit_updates_daily(self, tmp_path):
        """Test that daily count is updated."""
        stats_file = tmp_path / "stats.json"
        today = datetime.now().strftime("%Y-%m-%d")

        with patch("gac.stats.STATS_FILE", stats_file):
            record_commit()
            record_commit()

            stats = load_stats()
            assert stats["daily_commits"][today] == 2

    def test_record_updates_weekly(self, tmp_path):
        """Test that weekly counts are updated."""
        stats_file = tmp_path / "stats.json"
        iso_week = datetime.now().isocalendar()
        week_key = f"{iso_week[0]}-W{iso_week[1]:02d}"

        with patch("gac.stats.STATS_FILE", stats_file):
            record_commit()
            record_commit()
            record_gac()

            stats = load_stats()
            assert stats["weekly_commits"][week_key] == 2
            assert stats["weekly_gacs"][week_key] == 1


class TestGetStatsSummary:
    """Tests for get_stats_summary function."""

    def test_summary_no_commits(self):
        """Test summary when no commits made."""
        with patch("gac.stats.load_stats") as mock_load:
            mock_load.return_value: GACStats = {
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
            summary = get_stats_summary()
            assert summary["total_gacs"] == 0
            assert summary["total_commits"] == 0
            assert summary["first_used"] == "Never"
            assert summary["last_used"] == "Never"

    def test_summary_with_commits(self, tmp_path):
        """Test summary with commit history."""
        stats_file = tmp_path / "stats.json"
        today = datetime.now().strftime("%Y-%m-%d")

        stats: GACStats = {
            "total_gacs": 5,
            "total_commits": 10,
            "first_used": "2024-01-01T00:00:00",
            "last_used": f"{today}T12:00:00",
            "daily_gacs": {today: 1, "2024-01-01": 1},
            "daily_commits": {today: 3, "2024-01-01": 2},
            "weekly_gacs": {},
            "weekly_commits": {},
            "projects": {"my-project": {"gacs": 3, "commits": 6}},
        }
        stats_file.write_text(json.dumps(stats))

        with patch("gac.stats.STATS_FILE", stats_file):
            summary = get_stats_summary()
            assert summary["total_commits"] == 10
            assert summary["today_commits"] == 3
            assert summary["first_used"] == "2024-01-01"
            assert summary["last_used"] == datetime.now().strftime("%Y-%m-%d")


class TestResetStats:
    """Tests for reset_stats function."""

    def test_reset_stats(self, tmp_path):
        """Test resetting stats to zero."""
        stats_file = tmp_path / "stats.json"
        stats: GACStats = {
            "total_gacs": 50,
            "total_commits": 100,
            "first_used": "2024-01-01T00:00:00",
            "last_used": "2024-06-15T12:30:00",
            "daily_gacs": {"2024-06-15": 3},
            "daily_commits": {"2024-06-15": 5},
            "weekly_gacs": {},
            "weekly_commits": {},
            "projects": {},
        }
        stats_file.write_text(json.dumps(stats))

        with patch("gac.stats.STATS_FILE", stats_file):
            reset_stats()

            new_stats = load_stats()
            assert new_stats["total_commits"] == 0
            assert new_stats["first_used"] is None
            assert new_stats["last_used"] is None
            assert new_stats["daily_commits"] == {}


class TestAtomicSave:
    """Tests for atomic save_stats behavior."""

    def test_save_stats_uses_atomic_replace(self, tmp_path):
        """Test that save_stats writes via temp file and atomic rename, leaving no leftover temp."""
        stats_file = tmp_path / "stats.json"
        stats: GACStats = _empty_stats()
        stats["total_gacs"] = 7

        with patch("gac.stats.STATS_FILE", stats_file):
            save_stats(stats)

        assert stats_file.exists()
        loaded = json.loads(stats_file.read_text())
        assert loaded["total_gacs"] == 7
        # No leftover .tmp.* sibling files
        leftovers = list(tmp_path.glob("stats.json.tmp.*"))
        assert leftovers == []

    def test_save_stats_failure_does_not_corrupt_existing(self, tmp_path):
        """Test that an interrupted/failed write preserves the previous stats file."""
        stats_file = tmp_path / "stats.json"
        good_stats: GACStats = _empty_stats()
        good_stats["total_gacs"] = 99

        with patch("gac.stats.STATS_FILE", stats_file):
            save_stats(good_stats)
            # Sanity: existing file is the good one.
            assert json.loads(stats_file.read_text())["total_gacs"] == 99

            # Force the temp-file write to fail mid-save.
            with patch.object(Path, "write_text", side_effect=OSError("boom")):
                bad_stats: GACStats = _empty_stats()
                bad_stats["total_gacs"] = 1
                save_stats(bad_stats)

            # Existing file must still hold the prior value, not be truncated.
            loaded = json.loads(stats_file.read_text())
            assert loaded["total_gacs"] == 99
            # No orphaned tmp files left behind
            assert list(tmp_path.glob("stats.json.tmp.*")) == []


class TestRecordTokens:
    """Tests for record_tokens function."""

    def test_record_tokens_basic(self, tmp_path):
        """Test recording prompt and completion tokens updates totals."""
        stats_file = tmp_path / "stats.json"

        with patch("gac.stats.STATS_FILE", stats_file):
            record_tokens(100, 50, model="anthropic:test-model")

            stats = load_stats()
            assert stats["total_prompt_tokens"] == 100
            assert stats["total_completion_tokens"] == 50

    def test_record_tokens_accumulates(self, tmp_path):
        """Test that token counts accumulate across calls."""
        stats_file = tmp_path / "stats.json"

        with patch("gac.stats.STATS_FILE", stats_file):
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

        with patch("gac.stats.STATS_FILE", stats_file):
            record_tokens(100, 50)

            stats = load_stats()
            assert stats["daily_prompt_tokens"][today] == 100
            assert stats["daily_completion_tokens"][today] == 50
            assert stats["weekly_prompt_tokens"][week_key] == 100
            assert stats["weekly_completion_tokens"][week_key] == 50

    def test_record_tokens_per_model(self, tmp_path):
        """Test tokens are tracked per model."""
        stats_file = tmp_path / "stats.json"

        with patch("gac.stats.STATS_FILE", stats_file):
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

        with patch("gac.stats.STATS_FILE", stats_file):
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

        with patch("gac.stats.STATS_FILE", stats_file), patch.dict("os.environ", {"GAC_DISABLE_STATS": "1"}):
            record_tokens(100, 50, model="anthropic:test")

            stats = load_stats()
            assert stats["total_prompt_tokens"] == 0
            assert stats["total_completion_tokens"] == 0

    def test_record_tokens_zero_no_op(self, tmp_path):
        """Test record_tokens skips when both counts are zero."""
        stats_file = tmp_path / "stats.json"

        with patch("gac.stats.STATS_FILE", stats_file):
            record_tokens(0, 0, model="anthropic:test")

            assert not stats_file.exists() or load_stats()["total_prompt_tokens"] == 0


class TestRecordGacWithModel:
    """Tests for record_gac model tracking."""

    def test_record_gac_tracks_model(self, tmp_path):
        """Test record_gac increments model.gacs counter."""
        stats_file = tmp_path / "stats.json"

        with patch("gac.stats.STATS_FILE", stats_file):
            record_gac(model="anthropic:claude-haiku-4-5")
            record_gac(model="anthropic:claude-haiku-4-5")
            record_gac(model="openai:gpt-5")

            stats = load_stats()
            assert stats["models"]["anthropic:claude-haiku-4-5"]["gacs"] == 2
            assert stats["models"]["openai:gpt-5"]["gacs"] == 1

    def test_record_gac_no_model(self, tmp_path):
        """Test record_gac without a model leaves models dict empty."""
        stats_file = tmp_path / "stats.json"

        with patch("gac.stats.STATS_FILE", stats_file):
            record_gac()

            stats = load_stats()
            assert stats["models"] == {}


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
        stats_file.write_text(json.dumps(stats))

        with patch("gac.stats.STATS_FILE", stats_file):
            summary = get_stats_summary()
            assert summary["total_prompt_tokens"] == 1000
            assert summary["total_completion_tokens"] == 500
            assert summary["total_tokens"] == 1500
            assert summary["today_tokens"] == 300  # 200 + 100
            assert summary["peak_daily_tokens"] == 1200  # 2024-01-01 had 800+400
            assert summary["week_tokens"] == 300

    def test_summary_includes_top_models(self, tmp_path):
        """Test summary returns top_models sorted by gacs then total tokens."""
        stats_file = tmp_path / "stats.json"

        stats: GACStats = _empty_stats()
        stats["models"] = {
            "model-a": {"gacs": 5, "prompt_tokens": 500, "completion_tokens": 100},
            "model-b": {"gacs": 10, "prompt_tokens": 100, "completion_tokens": 50},
        }
        stats_file.write_text(json.dumps(stats))

        with patch("gac.stats.STATS_FILE", stats_file):
            summary = get_stats_summary()
            top = summary["top_models"]
            assert top[0][0] == "model-b"
            assert top[1][0] == "model-a"

    def test_top_models_tiebreak_by_total_tokens(self, tmp_path):
        """When models have equal gacs, the one with more total tokens sorts first."""
        stats_file = tmp_path / "stats.json"

        stats: GACStats = _empty_stats()
        stats["models"] = {
            "model-a": {"gacs": 5, "prompt_tokens": 500, "completion_tokens": 100, "reasoning_tokens": 50},
            "model-b": {"gacs": 5, "prompt_tokens": 1000, "completion_tokens": 200, "reasoning_tokens": 100},
            "model-c": {"gacs": 5, "prompt_tokens": 200, "completion_tokens": 50, "reasoning_tokens": 0},
        }
        stats_file.write_text(json.dumps(stats))

        with patch("gac.stats.STATS_FILE", stats_file):
            summary = get_stats_summary()
            top = summary["top_models"]
            # All have 5 gacs; sort by total tokens: b=1300, a=650, c=250
            assert top[0][0] == "model-b"
            assert top[1][0] == "model-a"
            assert top[2][0] == "model-c"


class TestDisableStats:
    """Tests for GAC_DISABLE_STATS environment variable."""

    def test_record_gac_disabled(self, tmp_path):
        """Test that record_gac does nothing when GAC_DISABLE_STATS is set."""
        stats_file = tmp_path / "stats.json"

        with patch("gac.stats.STATS_FILE", stats_file), patch.dict("os.environ", {"GAC_DISABLE_STATS": "1"}):
            record_gac()

            stats = load_stats()
            assert stats["total_gacs"] == 0

    def test_record_commit_disabled(self, tmp_path):
        """Test that record_commit does nothing when GAC_DISABLE_STATS is set."""
        stats_file = tmp_path / "stats.json"

        with patch("gac.stats.STATS_FILE", stats_file), patch.dict("os.environ", {"GAC_DISABLE_STATS": "1"}):
            record_commit()

            stats = load_stats()
            assert stats["total_commits"] == 0

    def test_record_gac_enabled_by_default(self, tmp_path):
        """Test that record_gac works when GAC_DISABLE_STATS is not set."""
        stats_file = tmp_path / "stats.json"

        with patch("gac.stats.STATS_FILE", stats_file):
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


class TestModelSpeedTracking:
    """Tests for per-model speed (tokens/sec) tracking."""

    def test_record_tokens_with_duration_updates_speed_fields(self, tmp_path):
        """record_tokens with duration_ms > 0 updates timing fields."""
        with patch("gac.stats.STATS_FILE", tmp_path / "stats.json"):
            record_tokens(100, 50, model="openai:gpt-4", duration_ms=1000)
            stats = load_stats()
            m = stats["models"]["openai:gpt-4"]
            assert m["total_duration_ms"] == 1000
            assert m["duration_count"] == 1
            assert m["timed_completion_tokens"] == 50
            assert m["min_duration_ms"] == 1000
            assert m["max_duration_ms"] == 1000

    def test_record_tokens_duration_accumulates(self, tmp_path):
        """Multiple calls with duration_ms accumulate correctly."""
        with patch("gac.stats.STATS_FILE", tmp_path / "stats.json"):
            record_tokens(100, 50, model="openai:gpt-4", duration_ms=500)
            record_tokens(100, 100, model="openai:gpt-4", duration_ms=1000)
            stats = load_stats()
            m = stats["models"]["openai:gpt-4"]
            assert m["total_duration_ms"] == 1500
            assert m["duration_count"] == 2
            assert m["timed_completion_tokens"] == 150
            assert m["min_duration_ms"] == 500
            assert m["max_duration_ms"] == 1000

    def test_record_tokens_non_extreme_duration_preserves_bounds(self, tmp_path):
        """A non-extreme duration leaves prior min/max unchanged."""
        with patch("gac.stats.STATS_FILE", tmp_path / "stats.json"):
            record_tokens(100, 50, model="openai:gpt-4", duration_ms=200)
            record_tokens(100, 50, model="openai:gpt-4", duration_ms=800)
            record_tokens(100, 50, model="openai:gpt-4", duration_ms=400)
            stats = load_stats()
            m = stats["models"]["openai:gpt-4"]
            assert m["min_duration_ms"] == 200
            assert m["max_duration_ms"] == 800
            assert m["duration_count"] == 3

    def test_record_tokens_without_duration_leaves_fields_untouched(self, tmp_path):
        """record_tokens without duration_ms leaves timing fields at zero."""
        with patch("gac.stats.STATS_FILE", tmp_path / "stats.json"):
            record_tokens(100, 50, model="openai:gpt-4")
            stats = load_stats()
            m = stats["models"]["openai:gpt-4"]
            assert m["total_duration_ms"] == 0
            assert m["duration_count"] == 0
            assert m["timed_completion_tokens"] == 0
            assert m["min_duration_ms"] == 0
            assert m["max_duration_ms"] == 0

    def test_record_tokens_zero_duration_leaves_fields_untouched(self, tmp_path):
        """record_tokens with duration_ms=0 leaves timing fields at zero."""
        with patch("gac.stats.STATS_FILE", tmp_path / "stats.json"):
            record_tokens(100, 50, model="openai:gpt-4", duration_ms=0)
            stats = load_stats()
            m = stats["models"]["openai:gpt-4"]
            assert m["total_duration_ms"] == 0
            assert m["duration_count"] == 0

    def test_load_stats_defaults_missing_duration_fields(self, tmp_path):
        """load_stats defaults new timing fields when missing from on-disk file."""
        stats_file = tmp_path / "stats.json"
        old_data = {
            "total_gacs": 1,
            "total_commits": 0,
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "first_used": "2025-01-01",
            "last_used": "2025-01-01",
            "daily_gacs": {},
            "daily_commits": {},
            "daily_prompt_tokens": {},
            "daily_completion_tokens": {},
            "weekly_gacs": {},
            "weekly_commits": {},
            "weekly_prompt_tokens": {},
            "weekly_completion_tokens": {},
            "projects": {},
            "models": {"openai:gpt-4": {"gacs": 1, "prompt_tokens": 100, "completion_tokens": 50}},
        }
        stats_file.write_text(json.dumps(old_data))
        with patch("gac.stats.STATS_FILE", stats_file):
            stats = load_stats()
            m = stats["models"]["openai:gpt-4"]
            assert m["total_duration_ms"] == 0
            assert m["duration_count"] == 0
            assert m["timed_completion_tokens"] == 0
            assert m["min_duration_ms"] == 0
            assert m["max_duration_ms"] == 0

    def test_old_format_then_timed_record_tokens(self, tmp_path):
        """After loading an old-format file, a timed record_tokens updates cleanly."""
        stats_file = tmp_path / "stats.json"
        old_data = {
            "total_gacs": 1,
            "total_commits": 0,
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "first_used": "2025-01-01",
            "last_used": "2025-01-01",
            "daily_gacs": {},
            "daily_commits": {},
            "daily_prompt_tokens": {},
            "daily_completion_tokens": {},
            "weekly_gacs": {},
            "weekly_commits": {},
            "weekly_prompt_tokens": {},
            "weekly_completion_tokens": {},
            "projects": {},
            "models": {"openai:gpt-4": {"gacs": 1, "prompt_tokens": 100, "completion_tokens": 50}},
        }
        stats_file.write_text(json.dumps(old_data))
        with patch("gac.stats.STATS_FILE", stats_file):
            load_stats()
            record_tokens(200, 80, model="openai:gpt-4", duration_ms=500)
            stats = load_stats()
            m = stats["models"]["openai:gpt-4"]
            assert m["total_duration_ms"] == 500
            assert m["duration_count"] == 1
            assert m["timed_completion_tokens"] == 80
            assert m["min_duration_ms"] == 500
            assert m["max_duration_ms"] == 500

    def test_get_stats_summary_avg_tps(self, tmp_path):
        """get_stats_summary computes avg_tps when timing data is available."""
        with patch("gac.stats.STATS_FILE", tmp_path / "stats.json"):
            record_tokens(100, 100, model="openai:gpt-4", duration_ms=1000)
            summary = get_stats_summary()
            top_models = summary["top_models"]
            model_data = next(data for name, data in top_models if name == "openai:gpt-4")
            assert model_data["avg_tps"] == 100

    def test_get_stats_summary_avg_tps_none_when_no_timing(self, tmp_path):
        """get_stats_summary sets avg_tps to None when no timing data."""
        with patch("gac.stats.STATS_FILE", tmp_path / "stats.json"):
            record_tokens(100, 50, model="openai:gpt-4")
            summary = get_stats_summary()
            top_models = summary["top_models"]
            model_data = next(data for name, data in top_models if name == "openai:gpt-4")
            assert model_data["avg_tps"] is None

    def test_record_tokens_reasoning_accumulates(self, tmp_path):
        """reasoning_tokens accumulates per model."""
        with patch("gac.stats.STATS_FILE", tmp_path / "stats.json"):
            record_tokens(100, 80, model="openai:o3", reasoning_tokens=30)
            record_tokens(100, 60, model="openai:o3", reasoning_tokens=20)
            stats = load_stats()
            assert stats["models"]["openai:o3"]["reasoning_tokens"] == 50
            assert stats["models"]["openai:o3"]["completion_tokens"] == 140

    def test_record_tokens_reasoning_defaults_zero(self, tmp_path):
        """reasoning_tokens defaults to 0 when not provided."""
        with patch("gac.stats.STATS_FILE", tmp_path / "stats.json"):
            record_tokens(100, 50, model="openai:gpt-4")
            stats = load_stats()
            assert stats["models"]["openai:gpt-4"]["reasoning_tokens"] == 0

    def test_get_stats_summary_reasoning_in_top_models(self, tmp_path):
        """reasoning_tokens appears in top_models from get_stats_summary."""
        with patch("gac.stats.STATS_FILE", tmp_path / "stats.json"):
            record_tokens(100, 80, model="openai:o3", reasoning_tokens=30)
            summary = get_stats_summary()
            top_models = summary["top_models"]
            model_data = next(data for name, data in top_models if name == "openai:o3")
            assert model_data["reasoning_tokens"] == 30

    def test_normalize_models_backfills_reasoning_tokens(self, tmp_path):
        """Old stats files without reasoning_tokens get it defaulted to 0."""
        with patch("gac.stats.STATS_FILE", tmp_path / "stats.json"):
            raw_stats = {"models": {"openai:gpt-4": {"gacs": 1, "prompt_tokens": 100, "completion_tokens": 50}}}
            (tmp_path / "stats.json").write_text(json.dumps(raw_stats))
            stats = load_stats()
            assert stats["models"]["openai:gpt-4"]["reasoning_tokens"] == 0


class TestBiggestGac:
    """Tests for biggest-gac token tracking."""

    def test_biggest_gac_records_on_first_gac(self, tmp_path):
        """First gac with tokens becomes the biggest gac."""
        import gac.stats

        gac.stats._current_gac_tokens = 0  # Reset accumulator
        with patch("gac.stats.STATS_FILE", tmp_path / "stats.json"):
            record_tokens(500, 100, model="openai:gpt-4", reasoning_tokens=50)
            record_gac(model="openai:gpt-4")

            stats = load_stats()
            assert stats["biggest_gac_tokens"] == 650  # 500+100+50
            assert stats["biggest_gac_date"] is not None

    def test_biggest_gac_updates_on_larger_gac(self, tmp_path):
        """A bigger gac overwrites the previous record."""
        import gac.stats

        gac.stats._current_gac_tokens = 0
        with patch("gac.stats.STATS_FILE", tmp_path / "stats.json"):
            # First gac: small
            record_tokens(100, 50, model="openai:gpt-4")
            record_gac(model="openai:gpt-4")

            gac.stats._current_gac_tokens = 0
            # Second gac: much bigger
            record_tokens(5000, 500, model="openai:gpt-4", reasoning_tokens=200)
            record_gac(model="openai:gpt-4")

            stats = load_stats()
            assert stats["biggest_gac_tokens"] == 5700  # 5000+500+200

    def test_biggest_gac_preserved_on_smaller_gac(self, tmp_path):
        """A smaller gac doesn't overwrite the record."""
        import gac.stats

        gac.stats._current_gac_tokens = 0
        with patch("gac.stats.STATS_FILE", tmp_path / "stats.json"):
            # Big gac first
            record_tokens(5000, 500, model="openai:gpt-4", reasoning_tokens=200)
            record_gac(model="openai:gpt-4")

            gac.stats._current_gac_tokens = 0
            # Smaller gac
            record_tokens(100, 50, model="openai:gpt-4")
            record_gac(model="openai:gpt-4")

            stats = load_stats()
            assert stats["biggest_gac_tokens"] == 5700  # Still the big one

    def test_biggest_gac_accumulates_multiple_record_tokens(self, tmp_path):
        """Tokens from multiple record_tokens calls in one gac accumulate."""
        import gac.stats

        gac.stats._current_gac_tokens = 0
        with patch("gac.stats.STATS_FILE", tmp_path / "stats.json"):
            # Simulate grouped workflow with multiple AI calls
            record_tokens(1000, 200, model="openai:gpt-4", reasoning_tokens=50)
            record_tokens(2000, 400, model="openai:gpt-4", reasoning_tokens=100)
            record_tokens(500, 100, model="openai:gpt-4", reasoning_tokens=25)
            record_gac(model="openai:gpt-4")

            stats = load_stats()
            assert stats["biggest_gac_tokens"] == 4375  # 3500+700+175

    def test_biggest_gac_in_summary(self, tmp_path):
        """get_stats_summary includes biggest_gac_tokens and biggest_gac_date."""
        import gac.stats

        gac.stats._current_gac_tokens = 0
        with patch("gac.stats.STATS_FILE", tmp_path / "stats.json"):
            record_tokens(500, 100, model="openai:gpt-4", reasoning_tokens=50)
            record_gac(model="openai:gpt-4")

            summary = get_stats_summary()
            assert summary["biggest_gac_tokens"] == 650
            assert summary["biggest_gac_date"] is not None

    def test_biggest_gac_defaults_zero(self, tmp_path):
        """biggest_gac_tokens defaults to 0 on fresh stats."""
        with patch("gac.stats.STATS_FILE", tmp_path / "stats.json"):
            stats = load_stats()
            assert stats["biggest_gac_tokens"] == 0
            assert stats["biggest_gac_date"] is None

    def test_biggest_gac_backfills_from_old_stats_file(self, tmp_path):
        """Old stats files without biggest_gac fields get defaults."""
        stats_file = tmp_path / "stats.json"
        old_data = {
            "total_gacs": 5,
            "total_commits": 10,
            "first_used": "2025-01-01",
            "last_used": "2025-01-01",
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
        stats_file.write_text(json.dumps(old_data))
        with patch("gac.stats.STATS_FILE", stats_file):
            stats = load_stats()
            assert stats["biggest_gac_tokens"] == 0
            assert stats["biggest_gac_date"] is None

    def test_biggest_gac_reset(self, tmp_path):
        """reset_stats clears biggest_gac fields."""
        import gac.stats

        gac.stats._current_gac_tokens = 0
        with patch("gac.stats.STATS_FILE", tmp_path / "stats.json"):
            record_tokens(500, 100, model="openai:gpt-4", reasoning_tokens=50)
            record_gac(model="openai:gpt-4")

            stats = load_stats()
            assert stats["biggest_gac_tokens"] == 650

            reset_stats()
            stats = load_stats()
            assert stats["biggest_gac_tokens"] == 0
            assert stats["biggest_gac_date"] is None

    def test_biggest_gac_no_tokens(self, tmp_path):
        """A gac with no tokens doesn't set biggest_gac."""
        import gac.stats

        gac.stats._current_gac_tokens = 0
        with patch("gac.stats.STATS_FILE", tmp_path / "stats.json"):
            record_gac(model="openai:gpt-4")

            stats = load_stats()
            assert stats["biggest_gac_tokens"] == 0
            assert stats["biggest_gac_date"] is None

    def test_reset_gac_token_accumulator_prevents_leak(self, tmp_path):
        """reset_gac_token_accumulator prevents tokens leaking into the next gac.

        Simulates the MCP server scenario: record_tokens on a non-committing
        request, then reset, then a new request with fewer tokens.
        """
        import gac.stats
        from gac.stats import reset_gac_token_accumulator

        gac.stats._current_gac_tokens = 0
        with patch("gac.stats.STATS_FILE", tmp_path / "stats.json"):
            # First request (e.g. dry_run): tokens recorded but no gac
            record_tokens(500, 100, model="openai:gpt-4", reasoning_tokens=50)
            reset_gac_token_accumulator()

            # Second request: a smaller successful gac
            gac.stats._current_gac_tokens = 0
            record_tokens(50, 10, model="openai:gpt-4")
            record_gac(model="openai:gpt-4")

            stats = load_stats()
            # Should only be 60 (the second request), not 660 (both)
            assert stats["biggest_gac_tokens"] == 60

    def test_accumulator_leak_without_reset(self, tmp_path):
        """Without reset, tokens DO leak into the next gac (the bug we fixed)."""
        import gac.stats

        gac.stats._current_gac_tokens = 0
        with patch("gac.stats.STATS_FILE", tmp_path / "stats.json"):
            # First request (e.g. dry_run): tokens recorded but no gac
            record_tokens(500, 100, model="openai:gpt-4", reasoning_tokens=50)
            # Intentionally NOT calling reset_gac_token_accumulator()

            # Second request: a smaller successful gac
            record_tokens(50, 10, model="openai:gpt-4")
            record_gac(model="openai:gpt-4")

            stats = load_stats()
            # Without reset, the accumulator held 650 from the first request
            # plus 60 from the second = 710 (inflated!)
            assert stats["biggest_gac_tokens"] == 710


class TestMalformedStats:
    """Tests for defensive handling of malformed persisted stats values."""

    def test_malformed_biggest_gac_date_graceful(self, tmp_path):
        """A non-ISO biggest_gac_date doesn't crash get_stats_summary."""
        stats_file = tmp_path / "stats.json"
        data = {
            "total_gacs": 1,
            "total_commits": 1,
            "biggest_gac_tokens": 500,
            "biggest_gac_date": "not-a-date",
            "first_used": "2025-01-01T00:00:00",
            "last_used": "2025-01-01T00:00:00",
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
        stats_file.write_text(json.dumps(data))
        with patch("gac.stats.STATS_FILE", stats_file):
            summary = get_stats_summary()
            # Should not crash; date falls back to "?"
            assert summary["biggest_gac_tokens"] == 500
            assert summary["biggest_gac_date"] == "<invalid>"

    def test_malformed_biggest_gac_tokens_graceful(self, tmp_path):
        """A non-numeric biggest_gac_tokens coerces to 0 in the summary."""
        stats_file = tmp_path / "stats.json"
        data = {
            "total_gacs": 1,
            "total_commits": 1,
            "biggest_gac_tokens": "not-a-number",
            "biggest_gac_date": None,
            "first_used": "2025-01-01T00:00:00",
            "last_used": "2025-01-01T00:00:00",
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
        stats_file.write_text(json.dumps(data))
        with patch("gac.stats.STATS_FILE", stats_file):
            summary = get_stats_summary()
            # Should not crash; tokens coerce to 0
            assert summary["biggest_gac_tokens"] == 0

    def test_malformed_first_used_date_graceful(self, tmp_path):
        """A non-ISO first_used/last_used doesn't crash get_stats_summary."""
        stats_file = tmp_path / "stats.json"
        data = {
            "total_gacs": 1,
            "total_commits": 1,
            "first_used": "bogus",
            "last_used": "also-bogus",
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
        stats_file.write_text(json.dumps(data))
        with patch("gac.stats.STATS_FILE", stats_file):
            summary = get_stats_summary()
            # Should fall back to "?" instead of crashing
            assert summary["first_used"] == "<invalid>"
            assert summary["last_used"] == "<invalid>"

    def test_non_string_first_used_date_graceful(self, tmp_path):
        """A non-string first_used/last_used (e.g. int) doesn't crash stats_cli."""
        stats_file = tmp_path / "stats.json"
        data = {
            "total_gacs": 1,
            "total_commits": 1,
            "first_used": 123,
            "last_used": 456,
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
        stats_file.write_text(json.dumps(data))
        with patch("gac.stats.STATS_FILE", stats_file):
            summary = get_stats_summary()
            # Should fall back to "<invalid>" instead of passing through the int
            assert summary["first_used"] == "<invalid>"
            assert summary["last_used"] == "<invalid>"
            # Verify it's actually a string (won't crash .split("-"))
            assert isinstance(summary["first_used"], str)
            assert isinstance(summary["last_used"], str)

    def test_reset_gac_token_accumulator_at_request_start(self, tmp_path):
        """Simulates MCP server: stale tokens from a failed request are cleared
        when the next request starts (reset_gac_token_accumulator at try top)."""
        import gac.stats
        from gac.stats import reset_gac_token_accumulator

        with patch("gac.stats.STATS_FILE", tmp_path / "stats.json"):
            # Simulate leftover stale tokens from a failed previous request
            gac.stats._current_gac_tokens = 9999

            # MCP server resets at the start of each request
            reset_gac_token_accumulator()

            # Now a normal request
            gac.stats._current_gac_tokens = 0
            record_tokens(100, 50, model="openai:gpt-4")
            record_gac(model="openai:gpt-4")

            stats = load_stats()
            # Should be 150, not 10149 (9999 stale + 150 new)
            assert stats["biggest_gac_tokens"] == 150


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
