"""Tests for core stats operations: load, save, record_commit, summary, reset, atomic save."""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from gac.stats import (
    GACStats,
    find_model_key,
    get_stats_summary,
    load_stats,
    record_commit,
    record_gac,
    reset_model_stats,
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
        "_version": 2,
    }


class TestLoadStats:
    """Tests for load_stats function."""

    def test_load_stats_empty(self, tmp_path):
        """Test loading stats when file doesn't exist."""
        with patch("gac.stats.store.STATS_FILE", tmp_path / "nonexistent.json"):
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

        with patch("gac.stats.store.STATS_FILE", stats_file):
            stats = load_stats()
            assert stats["total_commits"] == 42
            assert stats["first_used"] == "2024-01-01T00:00:00"
            assert stats["last_used"] == "2024-06-15T12:30:00"
            assert stats["daily_commits"] == {"2024-06-15": 5}

    def test_load_stats_corrupted(self, tmp_path):
        """Test loading stats from corrupted file."""
        stats_file = tmp_path / "stats.json"
        stats_file.write_text("not valid json")

        with patch("gac.stats.store.STATS_FILE", stats_file):
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

        with patch("gac.stats.store.STATS_FILE", stats_file):
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

        with patch("gac.stats.store.STATS_FILE", stats_file):
            with patch.object(Path, "write_text", side_effect=OSError("Permission denied")):
                with caplog.at_level("WARNING"):
                    save_stats(stats)
                assert "Failed to save stats" in caplog.text


class TestRecordCommit:
    """Tests for record_commit function."""

    def test_record_first_commit(self, tmp_path):
        """Test recording first commit."""
        stats_file = tmp_path / "stats.json"

        with patch("gac.stats.store.STATS_FILE", stats_file):
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

        with patch("gac.stats.store.STATS_FILE", stats_file):
            record_commit()
            record_commit()
            record_commit()

            stats = load_stats()
            assert stats["total_commits"] == 3

    def test_record_commit_updates_daily(self, tmp_path):
        """Test that daily count is updated."""
        stats_file = tmp_path / "stats.json"
        today = datetime.now().strftime("%Y-%m-%d")

        with patch("gac.stats.store.STATS_FILE", stats_file):
            record_commit()
            record_commit()

            stats = load_stats()
            assert stats["daily_commits"][today] == 2

    def test_record_updates_weekly(self, tmp_path):
        """Test that weekly counts are updated."""
        stats_file = tmp_path / "stats.json"
        iso_week = datetime.now().isocalendar()
        week_key = f"{iso_week[0]}-W{iso_week[1]:02d}"

        with patch("gac.stats.store.STATS_FILE", stats_file):
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
        with patch("gac.stats.store.load_stats") as mock_load:
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

        with patch("gac.stats.store.STATS_FILE", stats_file):
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

        with patch("gac.stats.store.STATS_FILE", stats_file):
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

        with patch("gac.stats.store.STATS_FILE", stats_file):
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

        with patch("gac.stats.store.STATS_FILE", stats_file):
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


class TestStreakCalculation:
    """Tests for streak calculation in get_stats_summary."""

    def test_streak_with_consecutive_days(self, tmp_path):
        """Test that streaks are calculated correctly for consecutive days."""
        from datetime import datetime, timedelta

        from gac.stats.summary import get_stats_summary

        stats_file = tmp_path / "stats.json"
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        two_days_ago = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")

        stats_data = {
            "total_gacs": 3,
            "daily_gacs": {two_days_ago: 1, yesterday: 1, today: 1},
            "daily_commits": {},
        }

        stats_file.write_text(json.dumps(stats_data))
        with patch("gac.stats.store.STATS_FILE", stats_file):
            summary = get_stats_summary()
            assert summary["streak"] == 3
            assert summary["longest_streak"] >= 3


class TestFindModelKey:
    """Tests for find_model_key helper function."""

    def test_exact_case_match(self):
        """Test finding a model with exact case match."""
        models = {"wafer:deepseek-v4-pro": {"gacs": 10}}
        result = find_model_key(models, "wafer:deepseek-v4-pro")
        assert result == "wafer:deepseek-v4-pro"

    def test_case_insensitive_match(self):
        """Test finding a model with different casing."""
        models = {"Wafer:DeepSeek-V4-PRO": {"gacs": 10}}
        result = find_model_key(models, "wafer:deepseek-v4-pro")
        assert result == "Wafer:DeepSeek-V4-PRO"

    def test_mixed_case_model_id(self):
        """Test finding a model when search term has mixed case."""
        models = {"wafer:deepseek-v4-pro": {"gacs": 10}}
        result = find_model_key(models, "WAFER:DEEPSEEK-V4-PRO")
        assert result == "wafer:deepseek-v4-pro"

    def test_model_not_found(self):
        """Test when model is not in dict."""
        models = {"openai:gpt-4": {"gacs": 5}}
        result = find_model_key(models, "wafer:deepseek-v4-pro")
        assert result is None

    def test_empty_models_dict(self):
        """Test with empty models dict."""
        result = find_model_key({}, "wafer:deepseek-v4-pro")
        assert result is None


class TestResetModelStats:
    """Tests for reset_model_stats function."""

    def test_reset_model_exact_match(self, tmp_path):
        """Test resetting a model with exact case match."""
        stats_file = tmp_path / "stats.json"
        stats: GACStats = _empty_stats()
        stats["total_gacs"] = 15
        stats["total_prompt_tokens"] = 10000
        stats["models"] = {
            "wafer:deepseek-v4-pro": {
                "gacs": 10,
                "prompt_tokens": 5000,
                "completion_tokens": 2000,
                "reasoning_tokens": 500,
            },
            "openai:gpt-4": {"gacs": 5, "prompt_tokens": 3000, "completion_tokens": 1500, "reasoning_tokens": 0},
        }
        stats_file.write_text(json.dumps(stats))

        with patch("gac.stats.store.STATS_FILE", stats_file):
            result = reset_model_stats("wafer:deepseek-v4-pro")
            assert result is True

            loaded = load_stats()
            # Model should be removed
            assert "wafer:deepseek-v4-pro" not in loaded["models"]
            # Other model should remain
            assert "openai:gpt-4" in loaded["models"]
            # Overall totals should be unchanged
            assert loaded["total_gacs"] == 15
            assert loaded["total_prompt_tokens"] == 10000

    def test_reset_model_case_insensitive(self, tmp_path):
        """Test resetting a model with case-insensitive match."""
        stats_file = tmp_path / "stats.json"
        stats: GACStats = _empty_stats()
        stats["models"] = {
            "Wafer:DeepSeek-V4-PRO": {
                "gacs": 10,
                "prompt_tokens": 5000,
                "completion_tokens": 2000,
                "reasoning_tokens": 500,
            },
        }
        stats_file.write_text(json.dumps(stats))

        with patch("gac.stats.store.STATS_FILE", stats_file):
            result = reset_model_stats("wafer:deepseek-v4-pro")
            assert result is True

            loaded = load_stats()
            # Original-cased key should be removed
            assert "Wafer:DeepSeek-V4-PRO" not in loaded["models"]

    def test_reset_model_not_found(self, tmp_path):
        """Test resetting a non-existent model."""
        stats_file = tmp_path / "stats.json"
        stats: GACStats = _empty_stats()
        stats["models"] = {
            "openai:gpt-4": {"gacs": 5},
        }
        stats_file.write_text(json.dumps(stats))

        with patch("gac.stats.store.STATS_FILE", stats_file):
            result = reset_model_stats("nonexistent:model")
            assert result is False

            loaded = load_stats()
            # Original data should be unchanged
            assert "openai:gpt-4" in loaded["models"]

    def test_reset_model_empty_models_dict(self, tmp_path):
        """Test resetting when models dict is empty."""
        stats_file = tmp_path / "stats.json"
        stats: GACStats = _empty_stats()
        stats_file.write_text(json.dumps(stats))

        with patch("gac.stats.store.STATS_FILE", stats_file):
            result = reset_model_stats("any:model")
            assert result is False

    def test_reset_model_preserves_totals(self, tmp_path):
        """Test that resetting a model does NOT modify overall totals."""
        stats_file = tmp_path / "stats.json"
        stats: GACStats = _empty_stats()
        stats["total_gacs"] = 100
        stats["total_commits"] = 250
        stats["total_prompt_tokens"] = 50000
        stats["total_completion_tokens"] = 20000
        stats["total_reasoning_tokens"] = 5000
        stats["models"] = {
            "wafer:deepseek-v4-pro": {
                "gacs": 10,
                "prompt_tokens": 5000,
                "completion_tokens": 2000,
                "reasoning_tokens": 500,
            },
        }
        stats_file.write_text(json.dumps(stats))

        with patch("gac.stats.store.STATS_FILE", stats_file):
            result = reset_model_stats("wafer:deepseek-v4-pro")
            assert result is True

            loaded = load_stats()
            # Totals must be unchanged
            assert loaded["total_gacs"] == 100
            assert loaded["total_commits"] == 250
            assert loaded["total_prompt_tokens"] == 50000
            assert loaded["total_completion_tokens"] == 20000
            assert loaded["total_reasoning_tokens"] == 5000

    def test_reset_model_other_models_unaffected(self, tmp_path):
        """Test that only the target model is removed, others remain."""
        stats_file = tmp_path / "stats.json"
        stats: GACStats = _empty_stats()
        stats["models"] = {
            "model-a": {"gacs": 10, "prompt_tokens": 5000, "completion_tokens": 2000, "reasoning_tokens": 0},
            "model-b": {"gacs": 5, "prompt_tokens": 2500, "completion_tokens": 1000, "reasoning_tokens": 0},
            "model-c": {"gacs": 3, "prompt_tokens": 1500, "completion_tokens": 600, "reasoning_tokens": 0},
        }
        stats_file.write_text(json.dumps(stats))

        with patch("gac.stats.store.STATS_FILE", stats_file):
            result = reset_model_stats("model-b")
            assert result is True

            loaded = load_stats()
            assert "model-a" in loaded["models"]
            assert "model-b" not in loaded["models"]
            assert "model-c" in loaded["models"]

    def test_reset_model_stats_disabled(self, tmp_path):
        """Test that reset_model_stats returns False when stats are disabled."""
        stats_file = tmp_path / "stats.json"
        stats: GACStats = _empty_stats()
        stats["models"] = {
            "model-a": {"gacs": 10},
        }
        stats_file.write_text(json.dumps(stats))

        with patch("gac.stats.store.STATS_FILE", stats_file):
            with patch("gac.stats.store.stats_enabled", return_value=False):
                result = reset_model_stats("model-a")
                assert result is False

                # Data should be unchanged
                loaded = load_stats()
                assert "model-a" in loaded["models"]
