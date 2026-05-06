"""Usage statistics tracking for gac.

Tracks how many times users have made commits with gac.

This package is split into three sub-modules:
    - store: Persistence layer (load/save/reset, migration, TypedDict)
    - recorder: Recording functions (record_gac, record_commit, record_tokens)
    - summary: Computation and formatting (get_stats_summary, helpers)
Backward compatibility (read):
    All public names are re-exported here, so ``from gac.stats import X``
    continues to work as before.

STATS_FILE — compatibility note:
    Reading ``gac.stats.STATS_FILE`` works via __getattr__ and returns
    the current ``gac.stats.store.STATS_FILE``.  However, writing
    ``gac.stats.STATS_FILE = X`` only shadows the proxy in the package
    dict — it does **not** propagate to ``gac.stats.store.STATS_FILE``
    (Python modules have no __setattr__ per PEP 562).  Code that
    monkeypatches STATS_FILE must target the canonical location:
        gac.stats.store.STATS_FILE
    This is a change from the pre-split monolith, where ``gac.stats.STATS_FILE``
    was the single binding.
"""

from pathlib import Path

import gac.stats.store as _store

# Re-export everything that was previously available from gac.stats
from gac.stats.recorder import (
    record_commit,
    record_gac,
    record_tokens,
    reset_gac_token_accumulator,
)
from gac.stats.store import (
    _CURRENT_STATS_VERSION,
    _DURATION_DEFAULTS,
    _FALSY_VALUES,
    GACStats,
    _enrich_models_with_speed,
    _migrate_v1_to_v2,
    _normalize_models,
    _safe_format_date,
    compute_total_tokens,
    find_model_key,
    format_tokens,
    get_current_project_name,
    load_stats,
    model_activity,
    project_activity,
    reset_model_stats,
    reset_stats,
    save_stats,
    stats_enabled,
)
from gac.stats.summary import get_stats_summary

# Type-only annotation: tells mypy that STATS_FILE is a Path without
# creating a static binding that shadows __getattr__.  At runtime,
# __getattr__ still provides the read-through proxy to store.
STATS_FILE: Path

# STATS_FILE is intentionally omitted from the static imports above.
# __getattr__ makes gac.stats.STATS_FILE a read-through proxy to
# gac.stats.store.STATS_FILE.  However, assignment to gac.stats.STATS_FILE
# only shadows the proxy in the package dict and does NOT propagate to
# store (PEP 562 has no module __setattr__).  Monkeypatches must target
# gac.stats.store.STATS_FILE directly — this differs from the pre-split
# monolith where gac.stats.STATS_FILE was the canonical binding.

__all__ = [
    # Recorder
    "record_commit",
    "record_gac",
    "record_tokens",
    "reset_gac_token_accumulator",
    # Store
    "GACStats",
    "STATS_FILE",
    "_CURRENT_STATS_VERSION",
    "_DURATION_DEFAULTS",
    "_FALSY_VALUES",
    "_migrate_v1_to_v2",
    "_enrich_models_with_speed",
    "_normalize_models",
    "_safe_format_date",
    "compute_total_tokens",
    "find_model_key",
    "format_tokens",
    "get_current_project_name",
    "load_stats",
    "model_activity",
    "project_activity",
    "reset_model_stats",
    "reset_stats",
    "save_stats",
    "stats_enabled",
    # Summary
    "get_stats_summary",
]


def __getattr__(name: str) -> Path:
    """Read-through proxy for STATS_FILE.

    ``gac.stats.STATS_FILE`` returns ``gac.stats.store.STATS_FILE``.
    Assignment to ``gac.stats.STATS_FILE`` only shadows this proxy —
    it does not propagate to store.  See module docstring for details.
    """
    if name == "STATS_FILE":
        return _store.STATS_FILE
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
