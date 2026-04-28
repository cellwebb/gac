"""Test suite for stats_cli.py module."""

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from gac.cli import cli


class TestStatsCLI:
    """Tests for the stats CLI commands."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner for testing."""
        return CliRunner()

    def test_stats_show_no_commits(self, runner):
        """Test stats show when no commits have been made."""
        with patch("gac.stats_cli.get_stats_summary") as mock_summary:
            mock_summary.return_value = {
                "total_gacs": 0,
                "total_commits": 0,
                "first_used": "Never",
                "last_used": "Never",
                "today_gacs": 0,
                "today_commits": 0,
                "week_gacs": 0,
                "week_commits": 0,
                "streak": 0,
                "longest_streak": 0,
                "peak_daily_gacs": 0,
                "peak_daily_commits": 0,
                "peak_weekly_gacs": 0,
                "peak_weekly_commits": 0,
                "daily_gacs": {},
                "daily_commits": {},
                "weekly_gacs": {},
                "weekly_commits": {},
            }
            result = runner.invoke(cli, ["stats", "show"])
            assert result.exit_code == 0
            assert "No gacs yet" in result.output
            assert "start gaccing" in result.output

    def test_stats_show_with_commits(self, runner):
        """Test stats show with commit history."""
        with patch("gac.stats_cli.get_stats_summary") as mock_summary:
            mock_summary.return_value = {
                "total_gacs": 15,
                "total_commits": 42,
                "first_used": "2024-01-01",
                "last_used": "2024-06-15",
                "today_gacs": 2,
                "today_commits": 5,
                "week_gacs": 10,
                "week_commits": 25,
                "streak": 7,
                "longest_streak": 12,
                "peak_daily_gacs": 5,
                "peak_daily_commits": 10,
                "peak_weekly_gacs": 15,
                "peak_weekly_commits": 30,
                "daily_gacs": {"2024-06-15": 2},
                "daily_commits": {"2024-06-15": 5},
                "weekly_gacs": {},
                "weekly_commits": {},
            }
            result = runner.invoke(cli, ["stats", "show"])
            assert result.exit_code == 0
            assert "You've gac'd" in result.output
            assert "15" in result.output
            assert "42" in result.output

    def test_stats_default_shows_stats(self, runner):
        """Test that running 'gac stats' without subcommand shows stats."""
        with patch("gac.stats_cli.get_stats_summary") as mock_summary:
            mock_summary.return_value = {
                "total_gacs": 5,
                "total_commits": 10,
                "first_used": "2024-01-01",
                "last_used": "2024-06-15",
                "today_gacs": 1,
                "today_commits": 2,
                "week_gacs": 3,
                "week_commits": 6,
                "streak": 3,
                "longest_streak": 5,
                "peak_daily_gacs": 3,
                "peak_daily_commits": 6,
                "peak_weekly_gacs": 8,
                "peak_weekly_commits": 15,
                "daily_gacs": {"2024-06-15": 1},
                "daily_commits": {"2024-06-15": 2},
                "weekly_gacs": {},
                "weekly_commits": {},
            }
            result = runner.invoke(cli, ["stats"])
            assert result.exit_code == 0
            assert "You've gac'd" in result.output
            assert "5" in result.output
            assert "10" in result.output

    def test_stats_reset_confirm(self, runner):
        """Test stats reset with confirmation."""
        with patch("gac.stats_cli.reset_stats") as mock_reset:
            result = runner.invoke(cli, ["stats", "reset"], input="y\n")
            assert result.exit_code == 0
            mock_reset.assert_called_once()
            assert "Statistics reset" in result.output

    def test_stats_reset_cancel(self, runner):
        """Test stats reset cancellation."""
        with patch("gac.stats_cli.reset_stats") as mock_reset:
            result = runner.invoke(cli, ["stats", "reset"], input="n\n")
            assert result.exit_code == 0
            mock_reset.assert_not_called()
            assert "Reset cancelled" in result.output

    def test_stats_help(self, runner):
        """Test stats command help."""
        result = runner.invoke(cli, ["stats", "--help"])
        assert result.exit_code == 0
        assert "View your gac usage statistics" in result.output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
