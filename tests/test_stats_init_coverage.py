"""Test for stats __init__.py __getattr__ coverage."""

import gac.stats
import gac.stats.store as store


def test_stats_file_proxy():
    """gac.stats.STATS_FILE should proxy to gac.stats.store.STATS_FILE."""
    result = gac.stats.__getattr__("STATS_FILE")
    assert result == store.STATS_FILE


def test_stats_getattr_unknown_raises():
    """Unknown attribute should raise AttributeError."""
    try:
        gac.stats.__getattr__("nonexistent_attr")
        raise AssertionError("Expected AttributeError was not raised")
    except AttributeError as e:
        assert "has no attribute" in str(e)
