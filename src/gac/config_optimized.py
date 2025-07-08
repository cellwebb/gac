"""Optimized configuration loading with caching."""

import json
import os
import time
from pathlib import Path
from typing import Dict, Union

from dotenv import load_dotenv

from gac.constants import EnvDefaults, Logging


class CachedConfig:
    """Configuration with file-based caching."""

    def __init__(self):
        self.cache_file = Path.home() / ".cache" / "gac" / "config.json"
        self._ensure_cache_dir()

    def _ensure_cache_dir(self):
        """Ensure cache directory exists."""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            # Can't create cache dir, disable caching
            self.cache_file = None

    def _get_cache_key(self) -> dict:
        """Generate cache validation key."""
        key = {}

        # Track file modification times
        for name, path in [("user", Path.home() / ".gac.env"), ("project", Path(".env"))]:
            if path.exists():
                try:
                    stat = path.stat()
                    key[f"{name}_mtime"] = stat.st_mtime
                    key[f"{name}_size"] = stat.st_size
                except OSError:
                    pass

        # Track current working directory (affects .env loading)
        key["cwd"] = os.getcwd()

        # Track relevant environment variables
        for var in ["GAC_MODEL", "GAC_TEMPERATURE", "GAC_MAX_OUTPUT_TOKENS"]:
            if var in os.environ:
                key[f"env_{var}"] = os.environ[var]

        return key

    def load(self) -> Dict[str, Union[str, int, float, bool]]:
        """Load configuration with caching."""
        # No cache file = always load fresh
        if not self.cache_file:
            return self._load_fresh()

        current_key = self._get_cache_key()

        # Try cache
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r") as f:
                    cached = json.load(f)

                if cached.get("key") == current_key:
                    # Cache hit!
                    config = cached["config"]
                    # Restore proper types
                    config["temperature"] = float(config["temperature"])
                    config["max_output_tokens"] = int(config["max_output_tokens"])
                    config["max_retries"] = int(config["max_retries"])
                    config["warning_limit_tokens"] = int(config["warning_limit_tokens"])
                    return config
            except Exception:
                # Any cache error = reload
                pass

        # Cache miss
        config = self._load_fresh()

        # Save to cache
        try:
            cache_data = {"key": current_key, "config": config, "timestamp": time.time()}

            # Atomic write
            temp_file = self.cache_file.with_suffix(".tmp")
            with open(temp_file, "w") as f:
                json.dump(cache_data, f)
            temp_file.replace(self.cache_file)
        except Exception:
            # Cache write failed, continue without caching
            pass

        return config

    def _load_fresh(self) -> Dict[str, Union[str, int, float, bool]]:
        """Load configuration from files and environment."""
        # Original load_config logic
        user_config = Path.home() / ".gac.env"
        if user_config.exists():
            load_dotenv(user_config)

        project_env = Path(".env")
        if project_env.exists():
            load_dotenv(project_env, override=True)

        config = {
            "model": os.getenv("GAC_MODEL"),
            "temperature": float(os.getenv("GAC_TEMPERATURE", EnvDefaults.TEMPERATURE)),
            "max_output_tokens": int(os.getenv("GAC_MAX_OUTPUT_TOKENS", EnvDefaults.MAX_OUTPUT_TOKENS)),
            "max_retries": int(os.getenv("GAC_RETRIES", EnvDefaults.MAX_RETRIES)),
            "log_level": os.getenv("GAC_LOG_LEVEL", Logging.DEFAULT_LEVEL),
            "warning_limit_tokens": int(os.getenv("GAC_WARNING_LIMIT_TOKENS", EnvDefaults.WARNING_LIMIT_TOKENS)),
        }

        return config


# Global instance
_cached_config = CachedConfig()


def load_config() -> Dict[str, Union[str, int, float, bool]]:
    """Load configuration with caching.

    This is a drop-in replacement for the original load_config().
    """
    return _cached_config.load()


# For testing/benchmarking
def clear_cache():
    """Clear the configuration cache."""
    if _cached_config.cache_file and _cached_config.cache_file.exists():
        _cached_config.cache_file.unlink()
