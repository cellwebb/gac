"""Test suite for report_cli.py module."""

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from gac.cli import cli


class TestReportCLI:
    """Tests for the gac report command."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_report_no_activity(self, runner):
        """Test report when no activity exists."""
        with patch("gac.report_cli.load_stats") as mock_load:
            mock_load.return_value = {
                "daily_gacs": {},
                "daily_commits": {},
                "daily_prompt_tokens": {},
                "daily_completion_tokens": {},
            }
            result = runner.invoke(cli, ["report"])
            assert result.exit_code == 0
            assert "No activity yet" in result.output

    def test_report_with_activity(self, runner):
        """Test report renders with activity data."""
        with patch("gac.report_cli.load_stats") as mock_load:
            mock_load.return_value = {
                "daily_gacs": {"2026-05-01": 3, "2026-05-02": 5},
                "daily_commits": {"2026-05-01": 4, "2026-05-02": 7},
                "daily_prompt_tokens": {"2026-05-01": 1000, "2026-05-02": 2000},
                "daily_completion_tokens": {"2026-05-01": 200, "2026-05-02": 400},
                "projects": {},
                "models": {},
            }
            result = runner.invoke(cli, ["report"])
            assert result.exit_code == 0
            assert "GAC Report" in result.output
            assert "Daily Activity" in result.output
            assert "Token Usage" in result.output

    def test_report_help(self, runner):
        """Test report --help."""
        result = runner.invoke(cli, ["report", "--help"])
        assert result.exit_code == 0
        assert "weekly activity report" in result.output.lower() or "report" in result.output

    def test_report_multi_week(self, runner):
        """Test report --weeks 2 shows weekly breakdown."""
        with patch("gac.report_cli.load_stats") as mock_load:
            mock_load.return_value = {
                "daily_gacs": {"2026-05-02": 5},
                "daily_commits": {"2026-05-02": 7},
                "daily_prompt_tokens": {"2026-05-02": 2000},
                "daily_completion_tokens": {"2026-05-02": 400},
                "weekly_gacs": {"2026-W18": 5},
                "weekly_commits": {"2026-W18": 7},
                "weekly_prompt_tokens": {"2026-W18": 2000},
                "weekly_completion_tokens": {"2026-W18": 400},
                "projects": {},
                "models": {},
            }
            result = runner.invoke(cli, ["report", "--weeks", "2"])
            assert result.exit_code == 0
            assert "Weekly Breakdown" in result.output

    def test_report_with_projects(self, runner):
        """Test report shows top projects."""
        with patch("gac.report_cli.load_stats") as mock_load:
            mock_load.return_value = {
                "daily_gacs": {"2026-05-02": 5},
                "daily_commits": {"2026-05-02": 7},
                "daily_prompt_tokens": {"2026-05-02": 2000},
                "daily_completion_tokens": {"2026-05-02": 400},
                "projects": {
                    "my-proj": {"gacs": 5, "commits": 7, "prompt_tokens": 2000, "completion_tokens": 400},
                },
                "models": {},
            }
            result = runner.invoke(cli, ["report"])
            assert result.exit_code == 0
            assert "Top Projects" in result.output
            assert "my-proj" in result.output

    def test_report_with_models(self, runner):
        """Test report shows top models."""
        with patch("gac.report_cli.load_stats") as mock_load:
            mock_load.return_value = {
                "daily_gacs": {"2026-05-02": 5},
                "daily_commits": {"2026-05-02": 7},
                "daily_prompt_tokens": {"2026-05-02": 2000},
                "daily_completion_tokens": {"2026-05-02": 400},
                "projects": {},
                "models": {
                    "openai:gpt-4": {
                        "gacs": 5,
                        "prompt_tokens": 2000,
                        "completion_tokens": 400,
                        "reasoning_tokens": 0,
                        "total_duration_ms": 1000,
                        "duration_count": 1,
                        "timed_completion_tokens": 400,
                    },
                },
            }
            result = runner.invoke(cli, ["report"])
            assert result.exit_code == 0
            assert "Top Models" in result.output
            assert "openai:gpt-4" in result.output

    def test_report_stats_disabled(self, runner):
        """Test report when stats are disabled."""
        with patch("gac.report_cli.stats_enabled", return_value=False):
            result = runner.invoke(cli, ["report"])
            assert result.exit_code == 0
            assert "disabled" in result.output.lower()

    def test_report_weeks_zero_rejected(self, runner):
        """Test report --weeks 0 is rejected by the IntRange constraint."""
        result = runner.invoke(cli, ["report", "--weeks", "0"])
        assert result.exit_code != 0
        assert "--weeks" in result.output.lower() or "invalid" in result.output.lower()

    def test_report_token_only_activity(self, runner):
        """Test report shows token-only usage even with zero gacs/commits."""
        with patch("gac.report_cli.load_stats") as mock_load:
            mock_load.return_value = {
                "daily_gacs": {},
                "daily_commits": {},
                "daily_prompt_tokens": {"2026-05-02": 1000},
                "daily_completion_tokens": {"2026-05-02": 200},
                "projects": {},
                "models": {},
            }
            result = runner.invoke(cli, ["report"])
            assert result.exit_code == 0
            assert "No activity yet" not in result.output
            assert "1,200" in result.output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
