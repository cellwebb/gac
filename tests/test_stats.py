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
        """Test summary returns top_models sorted by gacs."""
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
