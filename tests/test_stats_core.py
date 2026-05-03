"""Tests for core stats operations: load, save, record_commit, summary, reset, atomic save."""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from gac.stats import (
    GACStats,
    get_stats_summary,
    load_stats,
    record_commit,
    record_gac,
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
