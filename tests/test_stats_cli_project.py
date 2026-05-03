"""Tests for stats_cli.py project subcommand and top-models/projects display."""

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


class TestProjectSubcommand:
    """Tests for the 'gac stats project' subcommand (lines 262-354)."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_project_not_in_git_repo(self, runner):
        """Test project subcommand when not in a git repository."""
        with patch("gac.stats_cli.get_current_project_name", return_value=None):
            result = runner.invoke(cli, ["stats", "project"])
            assert result.exit_code == 0
            assert "Not in a git repository" in result.output

    def test_project_no_activity(self, runner):
        """Test project subcommand when project has no activity."""
        with (
            patch("gac.stats_cli.get_current_project_name", return_value="my-proj"),
            patch("gac.stats_cli.load_stats") as mock_load,
        ):
            mock_load.return_value = {
                "projects": {
                    "my-proj": {
                        "gacs": 0,
                        "commits": 0,
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                    }
                }
            }
            result = runner.invoke(cli, ["stats", "project"])
            assert result.exit_code == 0
            assert "No gacs yet" in result.output

    def test_project_no_data_at_all(self, runner):
        """Test project subcommand when project not in stats at all."""
        with (
            patch("gac.stats_cli.get_current_project_name", return_value="new-proj"),
            patch("gac.stats_cli.load_stats") as mock_load,
        ):
            mock_load.return_value = {"projects": {}}
            result = runner.invoke(cli, ["stats", "project"])
            assert result.exit_code == 0
            assert "No gacs yet" in result.output

    def test_project_with_activity_and_tokens(self, runner):
        """Test project subcommand with full activity including tokens."""
        with (
            patch("gac.stats_cli.get_current_project_name", return_value="active-proj"),
            patch("gac.stats_cli.load_stats") as mock_load,
        ):
            mock_load.return_value = {
                "projects": {
                    "active-proj": {
                        "gacs": 5,
                        "commits": 10,
                        "prompt_tokens": 3000,
                        "completion_tokens": 1500,
                        "reasoning_tokens": 500,
                    }
                }
            }
            result = runner.invoke(cli, ["stats", "project"])
            assert result.exit_code == 0
            assert "active-proj" in result.output
            assert "5" in result.output
            assert "10" in result.output
            # Total = 3000 + 1500 + 500 = 5000
            assert "5,000" in result.output

    def test_project_singular_gac(self, runner):
        """Test project subcommand singular '1 time' message."""
        with (
            patch("gac.stats_cli.get_current_project_name", return_value="solo-proj"),
            patch("gac.stats_cli.load_stats") as mock_load,
        ):
            mock_load.return_value = {
                "projects": {
                    "solo-proj": {
                        "gacs": 1,
                        "commits": 1,
                        "prompt_tokens": 100,
                        "completion_tokens": 50,
                        "reasoning_tokens": 0,
                    }
                }
            }
            result = runner.invoke(cli, ["stats", "project"])
            assert result.exit_code == 0
            assert "1 time" in result.output
            assert "1 commit" in result.output

    def test_project_zero_tokens(self, runner):
        """Test project subcommand when project has gacs but no tokens."""
        with (
            patch("gac.stats_cli.get_current_project_name", return_value="notok-proj"),
            patch("gac.stats_cli.load_stats") as mock_load,
        ):
            mock_load.return_value = {
                "projects": {
                    "notok-proj": {
                        "gacs": 3,
                        "commits": 5,
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "reasoning_tokens": 0,
                    }
                }
            }
            result = runner.invoke(cli, ["stats", "project"])
            assert result.exit_code == 0
            assert "notok-proj" in result.output
            # Token table should NOT be rendered when total_t is 0
            assert "Prompt tokens" not in result.output


class TestTopModelsAndProjects:
    """Tests for top models and projects rendering in stats show."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_stats_show_with_top_projects(self, runner):
        """Test that top projects table is rendered."""
        with (
            patch("gac.stats_cli.get_stats_summary") as mock_summary,
            patch("gac.stats_cli.load_stats") as mock_load,
        ):
            mock_summary.return_value = _base_summary(
                top_projects=[
                    (
                        "gac",
                        {
                            "gacs": 10,
                            "commits": 20,
                            "prompt_tokens": 5000,
                            "completion_tokens": 2000,
                            "reasoning_tokens": 0,
                        },
                    )
                ],
            )
            mock_load.return_value = {
                "projects": {
                    "gac": {
                        "gacs": 10,
                        "commits": 20,
                        "prompt_tokens": 5000,
                        "completion_tokens": 2000,
                        "reasoning_tokens": 0,
                    }
                },
            }
            result = runner.invoke(cli, ["stats", "show"])
            assert result.exit_code == 0
            assert "Top Projects" in result.output
            assert "gac" in result.output

    def test_stats_show_with_top_models(self, runner):
        """Test that top models table is rendered with speed info."""
        with (
            patch("gac.stats_cli.get_stats_summary") as mock_summary,
            patch("gac.stats_cli.load_stats") as mock_load,
        ):
            mock_summary.return_value = _base_summary(
                top_models=[
                    (
                        "openai:gpt-4",
                        {
                            "gacs": 5,
                            "prompt_tokens": 3000,
                            "completion_tokens": 1000,
                            "reasoning_tokens": 500,
                            "avg_tps": 42,
                        },
                    ),
                ],
            )
            mock_load.return_value = {"projects": {}, "models": {}}
            result = runner.invoke(cli, ["stats", "show"])
            assert result.exit_code == 0
            assert "Top Models" in result.output
            assert "openai:gpt-4" in result.output
            assert "42 tps" in result.output

    def test_stats_show_with_model_no_speed(self, runner):
        """Test models table when avg_tps is None (no duration data)."""
        with (
            patch("gac.stats_cli.get_stats_summary") as mock_summary,
            patch("gac.stats_cli.load_stats") as mock_load,
        ):
            mock_summary.return_value = _base_summary(
                top_models=[
                    (
                        "anthropic:claude-3",
                        {
                            "gacs": 2,
                            "prompt_tokens": 1000,
                            "completion_tokens": 500,
                            "reasoning_tokens": 0,
                            "avg_tps": None,
                        },
                    ),
                ],
            )
            mock_load.return_value = {"projects": {}, "models": {}}
            result = runner.invoke(cli, ["stats", "show"])
            assert result.exit_code == 0
            assert "Top Models" in result.output
            assert "—" in result.output  # em dash for no speed
