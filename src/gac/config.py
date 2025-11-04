"""Configuration loading for gac.

Handles environment variable and .env file precedence for application settings.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

from gac.constants import EnvDefaults, Logging


def load_config() -> dict[str, str | int | float | bool | None]:
    """Load configuration from $HOME/.gac.env, then ./.gac.env or ./.env, then environment variables."""
    user_config = Path.home() / ".gac.env"
    if user_config.exists():
        load_dotenv(user_config)

    # Check for both .gac.env and .env in project directory
    project_gac_env = Path(".gac.env")
    project_env = Path(".env")

    if project_gac_env.exists():
        load_dotenv(project_gac_env, override=True)
    elif project_env.exists():
        load_dotenv(project_env, override=True)

    config = {
        "model": os.getenv("GAC_MODEL"),
        "temperature": float(os.getenv("GAC_TEMPERATURE", EnvDefaults.TEMPERATURE)),
        "max_output_tokens": int(os.getenv("GAC_MAX_OUTPUT_TOKENS", EnvDefaults.MAX_OUTPUT_TOKENS)),
        "max_retries": int(os.getenv("GAC_RETRIES", EnvDefaults.MAX_RETRIES)),
        "log_level": os.getenv("GAC_LOG_LEVEL", Logging.DEFAULT_LEVEL),
        "warning_limit_tokens": int(os.getenv("GAC_WARNING_LIMIT_TOKENS", EnvDefaults.WARNING_LIMIT_TOKENS)),
        "always_include_scope": os.getenv("GAC_ALWAYS_INCLUDE_SCOPE", str(EnvDefaults.ALWAYS_INCLUDE_SCOPE)).lower()
        in ("true", "1", "yes", "on"),
        "skip_secret_scan": os.getenv("GAC_SKIP_SECRET_SCAN", str(EnvDefaults.SKIP_SECRET_SCAN)).lower()
        in ("true", "1", "yes", "on"),
        "verbose": os.getenv("GAC_VERBOSE", str(EnvDefaults.VERBOSE)).lower() in ("true", "1", "yes", "on"),
        "system_prompt_path": os.getenv("GAC_SYSTEM_PROMPT_PATH"),
        "language": os.getenv("GAC_LANGUAGE"),
        "translate_prefixes": os.getenv("GAC_TRANSLATE_PREFIXES", "false").lower() in ("true", "1", "yes", "on"),
        "rtl_confirmed": os.getenv("GAC_RTL_CONFIRMED", "false").lower() in ("true", "1", "yes", "on"),
        "hook_timeout": int(os.getenv("GAC_HOOK_TIMEOUT", EnvDefaults.HOOK_TIMEOUT)),
    }

    return config
