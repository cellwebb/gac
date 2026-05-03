"""Tests for model speed tracking and biggest-gac token tracking."""

import json
from unittest.mock import patch

from gac.stats import (
    get_stats_summary,
    load_stats,
    record_gac,
    record_tokens,
    reset_stats,
)


class TestModelSpeedTracking:
    """Tests for per-model speed (tokens/sec) tracking."""

    def test_record_tokens_with_duration_updates_speed_fields(self, tmp_path):
        """record_tokens with duration_ms > 0 updates timing fields."""
        with patch("gac.stats.store.STATS_FILE", tmp_path / "stats.json"):
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
        with patch("gac.stats.store.STATS_FILE", tmp_path / "stats.json"):
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
        with patch("gac.stats.store.STATS_FILE", tmp_path / "stats.json"):
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
        with patch("gac.stats.store.STATS_FILE", tmp_path / "stats.json"):
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
        with patch("gac.stats.store.STATS_FILE", tmp_path / "stats.json"):
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
        with patch("gac.stats.store.STATS_FILE", stats_file):
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
        with patch("gac.stats.store.STATS_FILE", stats_file):
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
        with patch("gac.stats.store.STATS_FILE", tmp_path / "stats.json"):
            record_tokens(100, 100, model="openai:gpt-4", duration_ms=1000)
            summary = get_stats_summary()
            top_models = summary["top_models"]
            model_data = next(data for name, data in top_models if name == "openai:gpt-4")
            assert model_data["avg_tps"] == 100

    def test_get_stats_summary_avg_tps_none_when_no_timing(self, tmp_path):
        """get_stats_summary sets avg_tps to None when no timing data."""
        with patch("gac.stats.store.STATS_FILE", tmp_path / "stats.json"):
            record_tokens(100, 50, model="openai:gpt-4")
            summary = get_stats_summary()
            top_models = summary["top_models"]
            model_data = next(data for name, data in top_models if name == "openai:gpt-4")
            assert model_data["avg_tps"] is None

    def test_record_tokens_reasoning_accumulates(self, tmp_path):
        """reasoning_tokens accumulates per model."""
        with patch("gac.stats.store.STATS_FILE", tmp_path / "stats.json"):
            record_tokens(100, 80, model="openai:o3", reasoning_tokens=30)
            record_tokens(100, 60, model="openai:o3", reasoning_tokens=20)
            stats = load_stats()
            assert stats["models"]["openai:o3"]["reasoning_tokens"] == 50
            assert stats["models"]["openai:o3"]["completion_tokens"] == 140

    def test_record_tokens_reasoning_defaults_zero(self, tmp_path):
        """reasoning_tokens defaults to 0 when not provided."""
        with patch("gac.stats.store.STATS_FILE", tmp_path / "stats.json"):
            record_tokens(100, 50, model="openai:gpt-4")
            stats = load_stats()
            assert stats["models"]["openai:gpt-4"]["reasoning_tokens"] == 0

    def test_get_stats_summary_reasoning_in_top_models(self, tmp_path):
        """reasoning_tokens appears in top_models from get_stats_summary."""
        with patch("gac.stats.store.STATS_FILE", tmp_path / "stats.json"):
            record_tokens(100, 80, model="openai:o3", reasoning_tokens=30)
            summary = get_stats_summary()
            top_models = summary["top_models"]
            model_data = next(data for name, data in top_models if name == "openai:o3")
            assert model_data["reasoning_tokens"] == 30

    def test_normalize_models_backfills_reasoning_tokens(self, tmp_path):
        """Old stats files without reasoning_tokens get it defaulted to 0."""
        with patch("gac.stats.store.STATS_FILE", tmp_path / "stats.json"):
            raw_stats = {"models": {"openai:gpt-4": {"gacs": 1, "prompt_tokens": 100, "completion_tokens": 50}}}
            (tmp_path / "stats.json").write_text(json.dumps(raw_stats))
            stats = load_stats()
            assert stats["models"]["openai:gpt-4"]["reasoning_tokens"] == 0


class TestBiggestGac:
    """Tests for biggest-gac token tracking."""

    def test_biggest_gac_records_on_first_gac(self, tmp_path):
        """First gac with tokens becomes the biggest gac."""
        import gac.stats

        gac.stats.recorder._accumulator.reset()  # Reset accumulator
        with patch("gac.stats.store.STATS_FILE", tmp_path / "stats.json"):
            record_tokens(500, 100, model="openai:gpt-4", reasoning_tokens=50)
            record_gac(model="openai:gpt-4")

            stats = load_stats()
            assert (
                stats["biggest_gac_tokens"] == 650
            )  # 500+100+50 (completion excludes reasoning, so three distinct numbers)
            assert stats["biggest_gac_date"] is not None

    def test_biggest_gac_updates_on_larger_gac(self, tmp_path):
        """A bigger gac overwrites the previous record."""
        import gac.stats

        gac.stats.recorder._accumulator.reset()
        with patch("gac.stats.store.STATS_FILE", tmp_path / "stats.json"):
            # First gac: small
            record_tokens(100, 50, model="openai:gpt-4")
            record_gac(model="openai:gpt-4")

            gac.stats.recorder._accumulator.reset()
            # Second gac: much bigger
            record_tokens(5000, 500, model="openai:gpt-4", reasoning_tokens=200)
            record_gac(model="openai:gpt-4")

            stats = load_stats()
            assert stats["biggest_gac_tokens"] == 5700  # 5000+500+200 (completion excludes reasoning)

    def test_biggest_gac_preserved_on_smaller_gac(self, tmp_path):
        """A smaller gac doesn't overwrite the record."""
        import gac.stats

        gac.stats.recorder._accumulator.reset()
        with patch("gac.stats.store.STATS_FILE", tmp_path / "stats.json"):
            # Big gac first
            record_tokens(5000, 500, model="openai:gpt-4", reasoning_tokens=200)
            record_gac(model="openai:gpt-4")

            gac.stats.recorder._accumulator.reset()
            # Smaller gac
            record_tokens(100, 50, model="openai:gpt-4")
            record_gac(model="openai:gpt-4")

            stats = load_stats()
            assert stats["biggest_gac_tokens"] == 5700  # Still the big one

    def test_biggest_gac_accumulates_multiple_record_tokens(self, tmp_path):
        """Tokens from multiple record_tokens calls in one gac accumulate."""
        import gac.stats

        gac.stats.recorder._accumulator.reset()
        with patch("gac.stats.store.STATS_FILE", tmp_path / "stats.json"):
            # Simulate grouped workflow with multiple AI calls
            record_tokens(1000, 200, model="openai:gpt-4", reasoning_tokens=50)
            record_tokens(2000, 400, model="openai:gpt-4", reasoning_tokens=100)
            record_tokens(500, 100, model="openai:gpt-4", reasoning_tokens=25)
            record_gac(model="openai:gpt-4")

            stats = load_stats()
            assert stats["biggest_gac_tokens"] == 4375  # 3500+700+175 (completion excludes reasoning)

    def test_biggest_gac_in_summary(self, tmp_path):
        """get_stats_summary includes biggest_gac_tokens and biggest_gac_date."""
        import gac.stats

        gac.stats.recorder._accumulator.reset()
        with patch("gac.stats.store.STATS_FILE", tmp_path / "stats.json"):
            record_tokens(500, 100, model="openai:gpt-4", reasoning_tokens=50)
            record_gac(model="openai:gpt-4")

            summary = get_stats_summary()
            assert summary["biggest_gac_tokens"] == 650  # 500+100+50
            assert summary["biggest_gac_date"] is not None

    def test_biggest_gac_defaults_zero(self, tmp_path):
        """biggest_gac_tokens defaults to 0 on fresh stats."""
        with patch("gac.stats.store.STATS_FILE", tmp_path / "stats.json"):
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
        with patch("gac.stats.store.STATS_FILE", stats_file):
            stats = load_stats()
            assert stats["biggest_gac_tokens"] == 0
            assert stats["biggest_gac_date"] is None

    def test_biggest_gac_reset(self, tmp_path):
        """reset_stats clears biggest_gac fields."""
        import gac.stats

        gac.stats.recorder._accumulator.reset()
        with patch("gac.stats.store.STATS_FILE", tmp_path / "stats.json"):
            record_tokens(500, 100, model="openai:gpt-4", reasoning_tokens=50)
            record_gac(model="openai:gpt-4")

            stats = load_stats()
            assert stats["biggest_gac_tokens"] == 650  # 500+100+50

            reset_stats()
            stats = load_stats()
            assert stats["biggest_gac_tokens"] == 0
            assert stats["biggest_gac_date"] is None

    def test_biggest_gac_no_tokens(self, tmp_path):
        """A gac with no tokens doesn't set biggest_gac."""
        import gac.stats

        gac.stats.recorder._accumulator.reset()
        with patch("gac.stats.store.STATS_FILE", tmp_path / "stats.json"):
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

        gac.stats.recorder._accumulator.reset()
        with patch("gac.stats.store.STATS_FILE", tmp_path / "stats.json"):
            # First request (e.g. dry_run): tokens recorded but no gac
            record_tokens(500, 100, model="openai:gpt-4", reasoning_tokens=50)
            reset_gac_token_accumulator()

            # Second request: a smaller successful gac
            gac.stats.recorder._accumulator.reset()
            record_tokens(50, 10, model="openai:gpt-4")
            record_gac(model="openai:gpt-4")

            stats = load_stats()
            # Should only be 60 (the second request), not 660 (both)
            assert stats["biggest_gac_tokens"] == 60

    def test_accumulator_leak_without_reset(self, tmp_path):
        """Without reset, tokens DO leak into the next gac (the bug we fixed)."""
        import gac.stats

        gac.stats.recorder._accumulator.reset()
        with patch("gac.stats.store.STATS_FILE", tmp_path / "stats.json"):
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
