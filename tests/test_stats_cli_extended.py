"""Additional tests for stats_cli.py: disabled state, singular messages, edge cases."""

from datetime import datetime
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from gac.cli import cli


def _base_summary(**overrides):
    """Build a complete stats summary dict with sensible defaults."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    iso_week = datetime.now().isocalendar()
    this_week_key = f"{iso_week[0]}-W{iso_week[1]:02d}"

    base = {
        "total_gacs": 10,
        "total_commits": 20,
        "total_tokens": 50000,
        "total_prompt_tokens": 30000,
        "total_completion_tokens": 15000,
        "total_reasoning_tokens": 5000,
        "biggest_gac_tokens": 50000,
        "biggest_gac_date": "2024-01-01",
        "first_used": "2024-01-01",
        "last_used": "2024-06-15",
        "today_gacs": 2,
        "today_commits": 3,
        "today_tokens": 1000,
        "week_gacs": 5,
        "week_commits": 8,
        "week_tokens": 8000,
        "streak": 3,
        "longest_streak": 7,
        "peak_daily_gacs": 20,
        "peak_daily_commits": 50,
        "peak_daily_tokens": 100000,
        "peak_weekly_gacs": 50,
        "peak_weekly_commits": 100,
        "peak_weekly_tokens": 200000,
        "daily_gacs": {today_str: 2, "2024-01-01": 20},
        "daily_commits": {today_str: 3, "2024-01-01": 50},
        "daily_total_tokens": {today_str: 1000, "2024-01-01": 100000},
        "weekly_gacs": {this_week_key: 5, "2024-W01": 50},
        "weekly_commits": {this_week_key: 8, "2024-W01": 100},
        "weekly_total_tokens": {this_week_key: 8000, "2024-W01": 200000},
        "daily_prompt_tokens": {},
        "daily_completion_tokens": {},
        "daily_reasoning_tokens": {},
        "weekly_prompt_tokens": {},
        "weekly_completion_tokens": {},
        "weekly_reasoning_tokens": {},
        "top_projects": [],
        "top_models": [],
    }
    base.update(overrides)
    return base


class TestStatsDisabled:
    """Tests for the stats disabled message (lines 37-39)."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_stats_show_disabled(self, runner):
        """Test that a disabled-stats message is shown when GAC_DISABLE_STATS is truthy."""
        with patch("gac.stats_cli.stats_enabled", return_value=False):
            result = runner.invoke(cli, ["stats", "show"])
            assert result.exit_code == 0
            assert "disabled" in result.output.lower()
            assert "GAC_DISABLE_STATS" in result.output


class TestSingularMessages:
    """Tests for singular '1 time' / '1 commit' messages (lines 111, 117)."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_stats_show_singular_gac_and_commit(self, runner):
        """Test '1 time' and '1 commit' pluralization when totals equal 1."""
        with (
            patch("gac.stats_cli.get_stats_summary") as mock_summary,
            patch("gac.stats_cli.load_stats") as mock_load,
        ):
            mock_summary.return_value = _base_summary(
                total_gacs=1,
                total_commits=1,
            )
            mock_load.return_value = {"projects": {}, "models": {}}
            result = runner.invoke(cli, ["stats", "show"])
            assert result.exit_code == 0
            assert "1 time" in result.output
            assert "1 commit" in result.output
            # Should NOT say "times" (plural)
            assert "1 times" not in result.output


class TestEdgeCases:
    """Tests for remaining edge cases to reach 99%+ coverage."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_biggest_gac_without_date(self, runner):
        """Test biggest gac display when date is None but tokens > 0."""
        with (
            patch("gac.stats_cli.get_stats_summary") as mock_summary,
            patch("gac.stats_cli.load_stats") as mock_load,
        ):
            mock_summary.return_value = _base_summary(
                biggest_gac_tokens=8000,
                biggest_gac_date=None,
            )
            mock_load.return_value = {"projects": {}, "models": {}}
            result = runner.invoke(cli, ["stats", "show"])
            assert result.exit_code == 0
            assert "Biggest gac" in result.output
            assert "8,000" in result.output

    def test_no_today_activity_zero_streak(self, runner):
        """Test no celebration or streak message when streak=0 and no today activity."""
        datetime.now().strftime("%Y-%m-%d")
        with (
            patch("gac.stats_cli.get_stats_summary") as mock_summary,
            patch("gac.stats_cli.load_stats") as mock_load,
        ):
            mock_summary.return_value = _base_summary(
                today_gacs=0,
                today_commits=0,
                today_tokens=0,
                streak=0,
                daily_gacs={"2024-06-14": 2, "2024-01-01": 20},
                daily_commits={"2024-06-14": 3, "2024-01-01": 50},
                daily_total_tokens={"2024-06-14": 1000, "2024-01-01": 100000},
                biggest_gac_tokens=50000,
                biggest_gac_date="2024-01-01",
            )
            mock_load.return_value = {"projects": {}, "models": {}}
            result = runner.invoke(cli, ["stats", "show"])
            assert result.exit_code == 0
            # No celebration/trophy messages should appear
            assert "high score" not in result.output.lower()
            assert "Don't break that streak" not in result.output
            assert "New longest streak" not in result.output
