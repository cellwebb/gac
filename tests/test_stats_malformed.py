"""Tests for malformed stats handling, v1→v2 migration, and retry token inflation."""

import json
from unittest.mock import patch

from gac.stats import (
    get_stats_summary,
    load_stats,
    record_gac,
    record_tokens,
)


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
        with patch("gac.stats.store.STATS_FILE", stats_file):
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
        with patch("gac.stats.store.STATS_FILE", stats_file):
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
        with patch("gac.stats.store.STATS_FILE", stats_file):
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
        with patch("gac.stats.store.STATS_FILE", stats_file):
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

        with patch("gac.stats.store.STATS_FILE", tmp_path / "stats.json"):
            # Simulate leftover stale tokens from a failed previous request
            gac.stats.recorder._accumulator._current_tokens = 9999

            # MCP server resets at the start of each request
            reset_gac_token_accumulator()

            # Now a normal request
            gac.stats.recorder._accumulator.reset()
            record_tokens(100, 50, model="openai:gpt-4")
            record_gac(model="openai:gpt-4")

            stats = load_stats()
            # Should be 150, not 10149 (9999 stale + 150 new)
            assert stats["biggest_gac_tokens"] == 150

    def test_migration_v1_to_v2_subtracts_reasoning_from_completion(self, tmp_path):
        """V1 stats (inclusive completion) are migrated to V2 (exclusive)."""
        from gac.stats import _CURRENT_STATS_VERSION, _migrate_v1_to_v2

        v1_data = {
            "total_prompt_tokens": 1000,
            "total_completion_tokens": 800,  # inclusive of reasoning
            "total_reasoning_tokens": 200,
            "biggest_gac_tokens": 210,  # was prompt+completion+reasoning (double-counted)
            "biggest_gac_date": "2026-05-01T12:00:00",
            "daily_completion_tokens": {"2026-05-01": 800},
            "daily_reasoning_tokens": {"2026-05-01": 200},
            "weekly_completion_tokens": {"2026-W18": 800},
            "weekly_reasoning_tokens": {"2026-W18": 200},
            "projects": {
                "my-proj": {
                    "prompt_tokens": 1000,
                    "completion_tokens": 800,
                    "reasoning_tokens": 200,
                },
            },
            "models": {
                "openai:o3": {
                    "prompt_tokens": 1000,
                    "completion_tokens": 800,  # inclusive of reasoning
                    "reasoning_tokens": 200,
                    "timed_completion_tokens": 600,
                    "total_duration_ms": 3000,
                    "duration_count": 2,
                },
            },
        }

        migrated = _migrate_v1_to_v2(v1_data)

        # completion should be reduced by reasoning
        assert migrated["total_completion_tokens"] == 600
        assert migrated["daily_completion_tokens"]["2026-05-01"] == 600
        assert migrated["weekly_completion_tokens"]["2026-W18"] == 600
        assert migrated["projects"]["my-proj"]["completion_tokens"] == 600
        assert migrated["models"]["openai:o3"]["completion_tokens"] == 600
        # reasoning unchanged
        assert migrated["total_reasoning_tokens"] == 200
        assert migrated["models"]["openai:o3"]["reasoning_tokens"] == 200
        # timed_completion_tokens proportionally adjusted (600 * 600/800 = 450)
        assert migrated["models"]["openai:o3"]["timed_completion_tokens"] == 450
        # timed_reasoning_tokens backfilled so speed stays consistent (600-450=150)
        assert migrated["models"]["openai:o3"]["timed_reasoning_tokens"] == 150
        # biggest_gac_tokens reset (can't reconstruct per-gac reasoning)
        assert migrated["biggest_gac_tokens"] == 0
        assert migrated["biggest_gac_date"] is None
        # version set
        assert migrated["_version"] == _CURRENT_STATS_VERSION

    def test_migration_idempotent(self, tmp_path):
        """Running migration on already-v2 data is a no-op."""
        from gac.stats import _CURRENT_STATS_VERSION, _migrate_v1_to_v2

        v2_data = {
            "_version": _CURRENT_STATS_VERSION,
            "total_completion_tokens": 600,
            "total_reasoning_tokens": 200,
            "models": {
                "openai:o3": {
                    "completion_tokens": 600,
                    "reasoning_tokens": 200,
                },
            },
        }

        migrated = _migrate_v1_to_v2(v2_data)
        assert migrated["total_completion_tokens"] == 600  # unchanged
        assert migrated["models"]["openai:o3"]["completion_tokens"] == 600

    def test_migration_no_reasoning_is_noop(self):
        """Data with zero reasoning tokens is not changed by migration."""
        from gac.stats import _migrate_v1_to_v2

        v1_data = {
            "total_completion_tokens": 800,
            "total_reasoning_tokens": 0,
            "daily_completion_tokens": {"2026-05-01": 800},
            "daily_reasoning_tokens": {},
            "weekly_completion_tokens": {},
            "weekly_reasoning_tokens": {},
            "projects": {},
            "models": {},
        }

        migrated = _migrate_v1_to_v2(v1_data)
        assert migrated["total_completion_tokens"] == 800  # unchanged

    def test_migration_model_reasoning_without_total_resets_biggest(self):
        """Legacy stats with per-model reasoning but no total_reasoning_tokens
        still get biggest_gac_tokens reset."""
        from gac.stats import _migrate_v1_to_v2

        v1_data = {
            "total_completion_tokens": 80,
            # No total_reasoning_tokens field at all
            "biggest_gac_tokens": 210,  # inflated
            "biggest_gac_date": "2026-05-01T12:00:00",
            "daily_completion_tokens": {},
            "daily_reasoning_tokens": {},
            "weekly_completion_tokens": {},
            "weekly_reasoning_tokens": {},
            "projects": {},
            "models": {
                "openai:o3": {
                    "completion_tokens": 80,
                    "reasoning_tokens": 30,
                },
            },
        }

        migrated = _migrate_v1_to_v2(v1_data)
        assert migrated["biggest_gac_tokens"] == 0
        assert migrated["biggest_gac_date"] is None
        # Model completion still migrated
        assert migrated["models"]["openai:o3"]["completion_tokens"] == 50

    def test_migration_preserves_speed_with_timed_reasoning(self):
        """V1 migration must backfill timed_reasoning_tokens so speed stays consistent.

        Before this fix, migration reduced timed_completion_tokens but left
        timed_reasoning_tokens at 0, causing speed = (450+0)/3s = 150 tps
        instead of the original 600/3s = 200 tps.
        """
        from gac.stats import _migrate_v1_to_v2

        v1_data = {
            "total_prompt_tokens": 1000,
            "total_completion_tokens": 800,
            "total_reasoning_tokens": 200,
            "daily_completion_tokens": {},
            "daily_reasoning_tokens": {},
            "weekly_completion_tokens": {},
            "weekly_reasoning_tokens": {},
            "projects": {},
            "models": {
                "openai:o3": {
                    "prompt_tokens": 1000,
                    "completion_tokens": 800,
                    "reasoning_tokens": 200,
                    "timed_completion_tokens": 600,
                    "total_duration_ms": 3000,
                    "duration_count": 2,
                },
            },
        }

        migrated = _migrate_v1_to_v2(v1_data)
        m = migrated["models"]["openai:o3"]
        timed_output = m["timed_completion_tokens"] + m.get("timed_reasoning_tokens", 0)
        speed = round(timed_output * 1000 / m["total_duration_ms"])
        # Original speed was 600 tokens / 3000ms = 200 tps
        assert speed == 200, f"Speed regressed: {speed} tps (expected 200)"

    def test_speed_includes_reasoning_tokens(self):
        """_enrich_models_with_speed must count reasoning tokens in throughput.

        For thinking models, speed = (completion + reasoning) / seconds,
        not just completion / seconds.
        """
        from gac.stats import _enrich_models_with_speed

        models = [
            (
                "deepseek:deepseek-r1",
                {
                    "timed_completion_tokens": 500,
                    "timed_reasoning_tokens": 1500,
                    "total_duration_ms": 2000,
                    "duration_count": 1,
                },
            ),
        ]
        enriched = _enrich_models_with_speed(models)
        # (500 + 1500) / 2.0 = 1000 tps
        assert enriched[0][1]["avg_tps"] == 1000

    def test_speed_uses_zero_reasoning_when_absent(self):
        """Old stats files without timed_reasoning_tokens default to 0."""
        from gac.stats import _enrich_models_with_speed

        models = [
            (
                "openai:gpt-4",
                {
                    "timed_completion_tokens": 600,
                    "total_duration_ms": 3000,
                    "duration_count": 2,
                },
            ),
        ]
        enriched = _enrich_models_with_speed(models)
        # 600 / 3.0 = 200 tps (no reasoning, backward compat)
        assert enriched[0][1]["avg_tps"] == 200


class TestRetryTokenInflation:
    """Tests that content-level retries don't inflate biggest_gac_tokens.

    Before the fix, record_tokens() accumulated tokens from EVERY API call
    (including failed validation retries) into _accumulator.
    When record_gac() ran, it compared this inflated total against
    biggest_gac_tokens — so a 170k-token prompt with 1 retry would show
    as a 340k "biggest gac".

    The fix: reset_gac_token_accumulator() is called at the start of each
    retry iteration, so only the final successful call's tokens count.
    """

    def test_retry_tokens_not_in_biggest_gac(self, tmp_path):
        """Tokens from a failed retry should not inflate biggest_gac_tokens."""
        import gac.stats
        from gac.stats import reset_gac_token_accumulator

        gac.stats.recorder._accumulator.reset()
        with patch("gac.stats.store.STATS_FILE", tmp_path / "stats.json"):
            # Simulate: first AI call fails validation (100k tokens)
            record_tokens(100000, 500, model="wafer:glm-5.1", reasoning_tokens=200)

            # Retry loop resets accumulator before next call
            reset_gac_token_accumulator()

            # Second AI call succeeds (100k tokens — same size prompt + feedback)
            record_tokens(100000, 500, model="wafer:glm-5.1", reasoning_tokens=200)
            record_gac(model="wafer:glm-5.1")

            stats = load_stats()
            # Should be ~100,700 (last call only), NOT ~201,400 (both calls)
            assert stats["biggest_gac_tokens"] == 100700

    def test_retry_tokens_still_in_daily_totals(self, tmp_path):
        """Retry tokens should still count in daily/weekly/total stats (real cost)."""
        import gac.stats
        from gac.stats import reset_gac_token_accumulator

        gac.stats.recorder._accumulator.reset()
        with patch("gac.stats.store.STATS_FILE", tmp_path / "stats.json"):
            # First call (will be retried)
            record_tokens(100000, 500, model="wafer:glm-5.1", reasoning_tokens=200)

            # Reset accumulator for retry
            reset_gac_token_accumulator()

            # Second call
            record_tokens(100000, 500, model="wafer:glm-5.1", reasoning_tokens=200)
            record_gac(model="wafer:glm-5.1")

            stats = load_stats()
            # Daily/weekly/total stats include ALL tokens (both calls)
            assert stats["total_prompt_tokens"] == 200000  # Both calls
            assert stats["total_completion_tokens"] == 1000
            assert stats["total_reasoning_tokens"] == 400

    def test_multiple_retries_only_last_counts(self, tmp_path):
        """Multiple retries: only the last successful call counts for biggest_gac."""
        import gac.stats
        from gac.stats import reset_gac_token_accumulator

        gac.stats.recorder._accumulator.reset()
        with patch("gac.stats.store.STATS_FILE", tmp_path / "stats.json"):
            # First call fails
            record_tokens(50000, 100, model="openai:gpt-4")
            reset_gac_token_accumulator()

            # Second call fails
            record_tokens(60000, 100, model="openai:gpt-4")
            reset_gac_token_accumulator()

            # Third call succeeds
            record_tokens(70000, 100, model="openai:gpt-4")
            record_gac(model="openai:gpt-4")

            stats = load_stats()
            # Only the third call counts: 70000 + 100 = 70100
            assert stats["biggest_gac_tokens"] == 70100
            # But total tokens include all three calls
            assert stats["total_prompt_tokens"] == 180000
