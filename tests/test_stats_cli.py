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
                "biggest_gac_tokens": 0,
                "biggest_gac_date": None,
                "first_used": "Never",
                "last_used": "Never",
                "today_gacs": 0,
                "today_commits": 0,
                "today_tokens": 0,
                "week_gacs": 0,
                "week_commits": 0,
                "week_tokens": 0,
                "streak": 0,
                "longest_streak": 0,
                "peak_daily_gacs": 0,
                "peak_daily_commits": 0,
                "peak_daily_tokens": 0,
                "peak_weekly_gacs": 0,
                "peak_weekly_commits": 0,
                "peak_weekly_tokens": 0,
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
                "biggest_gac_tokens": 5000,
                "biggest_gac_date": "2024-06-15",
                "first_used": "2024-01-01",
                "last_used": "2024-06-15",
                "today_gacs": 2,
                "today_commits": 5,
                "today_tokens": 1000,
                "week_gacs": 10,
                "week_commits": 25,
                "week_tokens": 3000,
                "streak": 7,
                "longest_streak": 12,
                "peak_daily_gacs": 5,
                "peak_daily_commits": 10,
                "peak_daily_tokens": 2000,
                "peak_weekly_gacs": 15,
                "peak_weekly_commits": 30,
                "peak_weekly_tokens": 4000,
                "daily_gacs": {"2024-06-15": 2},
                "daily_commits": {"2024-06-15": 5},
                "daily_total_tokens": {"2024-06-15": 1000},
                "weekly_gacs": {},
                "weekly_commits": {},
                "weekly_total_tokens": {},
                "daily_prompt_tokens": {},
                "daily_completion_tokens": {},
                "daily_reasoning_tokens": {},
                "weekly_prompt_tokens": {},
                "weekly_completion_tokens": {},
                "weekly_reasoning_tokens": {},
                "top_projects": [],
                "top_models": [],
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
                "biggest_gac_tokens": 0,
                "biggest_gac_date": None,
                "first_used": "2024-01-01",
                "last_used": "2024-06-15",
                "today_gacs": 1,
                "today_commits": 2,
                "today_tokens": 500,
                "week_gacs": 3,
                "week_commits": 6,
                "week_tokens": 1500,
                "streak": 3,
                "longest_streak": 5,
                "peak_daily_gacs": 3,
                "peak_daily_commits": 6,
                "peak_daily_tokens": 1000,
                "peak_weekly_gacs": 8,
                "peak_weekly_commits": 15,
                "peak_weekly_tokens": 3000,
                "daily_gacs": {"2024-06-15": 1},
                "daily_commits": {"2024-06-15": 2},
                "daily_total_tokens": {"2024-06-15": 500},
                "weekly_gacs": {},
                "weekly_commits": {},
                "weekly_total_tokens": {},
                "daily_prompt_tokens": {},
                "daily_completion_tokens": {},
                "daily_reasoning_tokens": {},
                "weekly_prompt_tokens": {},
                "weekly_completion_tokens": {},
                "weekly_reasoning_tokens": {},
                "top_projects": [],
                "top_models": [],
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

    def test_stats_show_with_token_only_history(self, runner):
        """Test stats show renders activity even when only tokens were recorded
        (e.g. dry-run or message-only sessions where no commit/gac was created).
        """
        with patch("gac.stats_cli.get_stats_summary") as mock_summary, patch("gac.stats_cli.load_stats") as mock_load:
            mock_summary.return_value = {
                "total_gacs": 0,
                "total_commits": 0,
                "biggest_gac_tokens": 0,
                "biggest_gac_date": None,
                "total_prompt_tokens": 1000,
                "total_completion_tokens": 200,
                "total_reasoning_tokens": 0,
                "total_tokens": 1200,
                "first_used": "2026-04-01",
                "last_used": "2026-04-29",
                "today_gacs": 0,
                "today_commits": 0,
                "today_tokens": 1200,
                "week_gacs": 0,
                "week_commits": 0,
                "week_tokens": 1200,
                "streak": 0,
                "longest_streak": 0,
                "peak_daily_gacs": 0,
                "peak_daily_commits": 0,
                "peak_daily_tokens": 1200,
                "peak_weekly_gacs": 0,
                "peak_weekly_commits": 0,
                "peak_weekly_tokens": 1200,
                "daily_gacs": {},
                "daily_commits": {},
                "daily_total_tokens": {"2026-04-29": 1200},
                "weekly_gacs": {},
                "weekly_commits": {},
                "weekly_total_tokens": {"2026-W18": 1200},
                "top_projects": [],
                "top_models": [],
            }
            mock_load.return_value = {"projects": {}, "models": {}}
            result = runner.invoke(cli, ["stats", "show"])
            assert result.exit_code == 0
            # Should NOT short-circuit with the empty message
            assert "No gacs yet" not in result.output
            # Should render token activity
            assert "1,200" in result.output

    def test_stats_projects_with_token_only_history(self, runner):
        """Test stats projects renders all projects including one that has only token usage
        (no recorded commits or gacs yet)."""
        with patch("gac.stats_cli.load_stats") as mock_load:
            mock_load.return_value = {
                "projects": {
                    "my-proj": {
                        "gacs": 0,
                        "commits": 0,
                        "prompt_tokens": 800,
                        "completion_tokens": 150,
                        "reasoning_tokens": 0,
                    }
                }
            }
            result = runner.invoke(cli, ["stats", "projects"])
            assert result.exit_code == 0
            assert "All Projects" in result.output
            # Total = 800 + 150 + 0 = 950
            assert "950" in result.output

    def test_stats_show_biggest_gac(self, runner):
        """Test stats show displays biggest gac when it exists."""
        with patch("gac.stats_cli.get_stats_summary") as mock_summary, patch("gac.stats_cli.load_stats") as mock_load:
            mock_summary.return_value = {
                "total_gacs": 10,
                "total_commits": 15,
                "total_tokens": 50000,
                "biggest_gac_tokens": 12000,
                "biggest_gac_date": "2025-05-20",
                "first_used": "2024-01-01",
                "last_used": "2025-05-20",
                "today_gacs": 3,
                "today_commits": 5,
                "today_tokens": 12000,
                "week_gacs": 8,
                "week_commits": 12,
                "week_tokens": 30000,
                "streak": 2,
                "longest_streak": 5,
                "peak_daily_gacs": 5,
                "peak_daily_commits": 8,
                "peak_daily_tokens": 15000,
                "peak_weekly_gacs": 10,
                "peak_weekly_commits": 20,
                "peak_weekly_tokens": 40000,
                "daily_gacs": {"2025-05-20": 3},
                "daily_commits": {"2025-05-20": 5},
                "daily_total_tokens": {"2025-05-20": 12000},
                "weekly_gacs": {},
                "weekly_commits": {},
                "weekly_total_tokens": {},
                "daily_prompt_tokens": {},
                "daily_completion_tokens": {},
                "daily_reasoning_tokens": {},
                "weekly_prompt_tokens": {},
                "weekly_completion_tokens": {},
                "weekly_reasoning_tokens": {},
                "top_projects": [],
                "top_models": [],
            }
            mock_load.return_value = {"projects": {}, "models": {}}
            result = runner.invoke(cli, ["stats", "show"])
            assert result.exit_code == 0
            # Should show biggest gac in the details table
            assert "Biggest gac" in result.output
            assert "12,000" in result.output

    def test_stats_show_new_biggest_gac_celebration(self, runner):
        """Test stats show celebrates when today set a new biggest gac record."""
        from datetime import datetime

        today_str = datetime.now().strftime("%Y-%m-%d")
        with patch("gac.stats_cli.get_stats_summary") as mock_summary, patch("gac.stats_cli.load_stats") as mock_load:
            mock_summary.return_value = {
                "total_gacs": 5,
                "total_commits": 8,
                "total_tokens": 20000,
                "biggest_gac_tokens": 8000,
                "biggest_gac_date": today_str,
                "first_used": "2024-01-01",
                "last_used": today_str,
                "today_gacs": 1,
                "today_commits": 2,
                "today_tokens": 8000,
                "week_gacs": 3,
                "week_commits": 5,
                "week_tokens": 12000,
                "streak": 1,
                "longest_streak": 3,
                "peak_daily_gacs": 3,
                "peak_daily_commits": 5,
                "peak_daily_tokens": 10000,
                "peak_weekly_gacs": 5,
                "peak_weekly_commits": 8,
                "peak_weekly_tokens": 15000,
                "daily_gacs": {today_str: 1},
                "daily_commits": {today_str: 2},
                "daily_total_tokens": {today_str: 8000},
                "weekly_gacs": {},
                "weekly_commits": {},
                "weekly_total_tokens": {},
                "daily_prompt_tokens": {},
                "daily_completion_tokens": {},
                "daily_reasoning_tokens": {},
                "weekly_prompt_tokens": {},
                "weekly_completion_tokens": {},
                "weekly_reasoning_tokens": {},
                "top_projects": [],
                "top_models": [],
            }
            mock_load.return_value = {"projects": {}, "models": {}}
            result = runner.invoke(cli, ["stats", "show"])
            assert result.exit_code == 0
            assert "New biggest gac record" in result.output
            assert "8,000" in result.output

    def test_stats_show_survives_non_string_dates(self, runner):
        """Test stats show doesn't crash when summary returns non-string dates.

        This can happen when a persisted stats file has malformed first_used/
        last_used values that get_stats_summary() couldn't parse.
        """
        with patch("gac.stats_cli.get_stats_summary") as mock_summary, patch("gac.stats_cli.load_stats") as mock_load:
            mock_summary.return_value = {
                "total_gacs": 5,
                "total_commits": 8,
                "total_tokens": 20000,
                "biggest_gac_tokens": 0,
                "biggest_gac_date": None,
                "first_used": "<invalid>",
                "last_used": "<invalid>",
                "today_gacs": 1,
                "today_commits": 2,
                "today_tokens": 500,
                "week_gacs": 3,
                "week_commits": 5,
                "week_tokens": 1500,
                "streak": 0,
                "longest_streak": 0,
                "peak_daily_gacs": 3,
                "peak_daily_commits": 5,
                "peak_daily_tokens": 1000,
                "peak_weekly_gacs": 5,
                "peak_weekly_commits": 8,
                "peak_weekly_tokens": 3000,
                "daily_gacs": {"2024-06-15": 1},
                "daily_commits": {"2024-06-15": 2},
                "daily_total_tokens": {"2024-06-15": 500},
                "weekly_gacs": {},
                "weekly_commits": {},
                "weekly_total_tokens": {},
                "daily_prompt_tokens": {},
                "daily_completion_tokens": {},
                "daily_reasoning_tokens": {},
                "weekly_prompt_tokens": {},
                "weekly_completion_tokens": {},
                "weekly_reasoning_tokens": {},
                "top_projects": [],
                "top_models": [],
            }
            mock_load.return_value = {"projects": {}, "models": {}}
            result = runner.invoke(cli, ["stats", "show"])
            assert result.exit_code == 0
            # Should not crash on .split("-") with the "<invalid>" fallback
            assert "You've gac'd" in result.output


class TestStatsModelsCommand:
    """Tests for the 'gac stats models' subcommand."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_models_no_data(self, runner) -> None:
        with patch("gac.stats_cli.load_stats", return_value={"models": {}}):
            result = runner.invoke(cli, ["stats", "models"])
            assert result.exit_code == 0
            assert "No model usage yet" in result.output

    def test_models_with_data(self, runner) -> None:
        with (
            patch(
                "gac.stats_cli.load_stats",
                return_value={
                    "models": {
                        "openai:gpt-4": {
                            "gacs": 10,
                            "prompt_tokens": 5000,
                            "completion_tokens": 1000,
                            "reasoning_tokens": 200,
                        },
                    }
                },
            ),
            patch("gac.stats_cli.stats_enabled", return_value=True),
            patch("gac.stats.store._enrich_models_with_speed", side_effect=lambda x: x),
        ):
            result = runner.invoke(cli, ["stats", "models"])
            assert result.exit_code == 0
            assert "All Models" in result.output
            assert "openai:gpt-4" in result.output

    def test_models_disabled(self, runner) -> None:
        with patch("gac.stats_cli.stats_enabled", return_value=False):
            result = runner.invoke(cli, ["stats", "models"])
            assert result.exit_code == 0
            assert "disabled" in result.output.lower()

    def test_models_with_speed_data(self, runner) -> None:
        def enrich(data):
            result = []
            for name, d in data:
                d_copy = dict(d)
                d_copy["avg_tps"] = 42.0
                d_copy["avg_latency_ms"] = 1500
                result.append((name, d_copy))
            return result

        with (
            patch(
                "gac.stats_cli.load_stats",
                return_value={
                    "models": {
                        "openai:gpt-4": {
                            "gacs": 10,
                            "prompt_tokens": 5000,
                            "completion_tokens": 1000,
                            "reasoning_tokens": 200,
                        },
                    }
                },
            ),
            patch("gac.stats_cli.stats_enabled", return_value=True),
            patch("gac.stats.store._enrich_models_with_speed", side_effect=enrich),
        ):
            result = runner.invoke(cli, ["stats", "models"])
            assert result.exit_code == 0
            assert "Speed Comparison" in result.output
            assert "Latency Comparison" in result.output


class TestStatsProjectsCommand:
    """Tests for the 'gac stats projects' subcommand."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_projects_no_data(self, runner) -> None:
        with (
            patch("gac.stats_cli.load_stats", return_value={"projects": {}}),
            patch("gac.stats_cli.stats_enabled", return_value=True),
        ):
            result = runner.invoke(cli, ["stats", "projects"])
            assert result.exit_code == 0
            assert "No project usage yet" in result.output

    def test_projects_with_data(self, runner) -> None:
        with (
            patch(
                "gac.stats_cli.load_stats",
                return_value={
                    "projects": {
                        "my-app": {
                            "gacs": 20,
                            "commits": 50,
                            "prompt_tokens": 10000,
                            "completion_tokens": 2000,
                            "reasoning_tokens": 500,
                        },
                        "other-proj": {
                            "gacs": 5,
                            "commits": 10,
                            "prompt_tokens": 2000,
                            "completion_tokens": 400,
                            "reasoning_tokens": 0,
                        },
                    }
                },
            ),
            patch("gac.stats_cli.stats_enabled", return_value=True),
        ):
            result = runner.invoke(cli, ["stats", "projects"])
            assert result.exit_code == 0
            assert "All Projects" in result.output
            assert "my-app" in result.output

    def test_projects_disabled(self, runner) -> None:
        with patch("gac.stats_cli.stats_enabled", return_value=False):
            result = runner.invoke(cli, ["stats", "projects"])
            assert result.exit_code == 0
            assert "disabled" in result.output.lower()


class TestFormatLatency:
    """Tests for the _format_latency helper."""

    def test_milliseconds(self) -> None:
        from gac.stats_cli import _format_latency

        assert _format_latency(420) == "420ms"

    def test_seconds(self) -> None:
        from gac.stats_cli import _format_latency

        assert _format_latency(2500) == "2.5s"

    def test_exactly_one_second(self) -> None:
        from gac.stats_cli import _format_latency

        assert _format_latency(1000) == "1.0s"


class TestBuildBarChart:
    """Tests for the _build_bar_chart helper."""

    def test_basic_chart(self) -> None:
        from gac.stats_cli import _build_bar_chart

        models_data = [("model-a", {"avg_tps": 50}), ("model-b", {"avg_tps": 25})]
        table = _build_bar_chart(models_data, value_key="avg_tps", max_value=50, label_fmt=lambda v: f"{v} tps")
        # Table should have rows
        assert table.row_count == 2

    def test_empty_data(self) -> None:
        from gac.stats_cli import _build_bar_chart

        table = _build_bar_chart([], value_key="avg_tps", max_value=100, label_fmt=lambda v: str(v))
        assert table.row_count == 0

    def test_latency_chart_lower_is_better(self) -> None:
        from gac.stats_cli import _build_bar_chart

        models_data = [("fast", {"avg_latency_ms": 100}), ("slow", {"avg_latency_ms": 500})]
        table = _build_bar_chart(
            models_data,
            value_key="avg_latency_ms",
            max_value=500,
            label_fmt=lambda v: f"{v}ms",
            higher_is_better=False,
        )
        assert table.row_count == 2

    def test_latency_all_speed_tiers(self) -> None:
        """Hit all color tier branches for latency (lower is better)."""
        from gac.stats_cli import _build_bar_chart

        # 500 max, test 0.25 (125), 0.5 (250), 0.75 (375), and above
        models_data = [
            ("blazing", {"lat": 50}),  # <= 0.25 ratio (50/500=0.1)
            ("fast", {"lat": 200}),  # <= 0.5 ratio
            ("moderate", {"lat": 350}),  # <= 0.75 ratio
            ("slow", {"lat": 450}),  # > 0.75 ratio
        ]
        table = _build_bar_chart(
            models_data,
            value_key="lat",
            max_value=500,
            label_fmt=lambda v: f"{v}ms",
            higher_is_better=False,
        )
        assert table.row_count == 4

    def test_speed_all_tiers(self) -> None:
        """Hit all color tier branches for speed (higher is better)."""
        from gac.stats_cli import _build_bar_chart

        models_data = [
            ("fastest", {"tps": 100}),  # >= 0.75 ratio
            ("fast", {"tps": 60}),  # >= 0.5 ratio
            ("medium", {"tps": 30}),  # >= 0.25 ratio
            ("slow", {"tps": 10}),  # < 0.25 ratio
        ]
        table = _build_bar_chart(
            models_data,
            value_key="tps",
            max_value=100,
            label_fmt=lambda v: f"{v} tps",
            higher_is_better=True,
        )
        assert table.row_count == 4

    def test_zero_max_value(self) -> None:
        """Handle max_value=0 gracefully."""
        from gac.stats_cli import _build_bar_chart

        models_data = [("zero", {"tps": 0})]
        table = _build_bar_chart(
            models_data,
            value_key="tps",
            max_value=0,
            label_fmt=lambda v: str(v),
        )
        assert table.row_count == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
