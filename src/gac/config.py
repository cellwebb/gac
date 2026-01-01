"""Configuration loading for gac.

Handles environment variable and .gac.env file precedence for application settings.
"""

import os
from pathlib import Path
from typing import TypedDict

from dotenv import load_dotenv

from gac.constants import EnvDefaults, Logging
from gac.errors import ConfigError


class GACConfig(TypedDict, total=False):
    """TypedDict for GAC configuration values.

    Fields that can be None or omitted are marked with total=False.
    """

    model: str | None
    temperature: float
    max_output_tokens: int
    max_retries: int
    log_level: str
    warning_limit_tokens: int
    always_include_scope: bool
    skip_secret_scan: bool
    no_verify_ssl: bool
    verbose: bool
    system_prompt_path: str | None
    language: str | None
    translate_prefixes: bool
    rtl_confirmed: bool
    hook_timeout: int


def validate_config(config: GACConfig) -> None:
    """Validate configuration values at load time.

    Args:
        config: Configuration dictionary to validate

    Raises:
        ConfigError: If any configuration value is invalid
    """
    # Validate temperature (0.0 to 2.0)
    if config.get("temperature") is not None:
        temp = config["temperature"]
        if not isinstance(temp, (int, float)):
            raise ConfigError(f"temperature must be a number, got {type(temp).__name__}")
        if not 0.0 <= temp <= 2.0:
            raise ConfigError(f"temperature must be between 0.0 and 2.0, got {temp}")

    # Validate max_output_tokens (1 to 100000)
    if config.get("max_output_tokens") is not None:
        tokens = config["max_output_tokens"]
        if not isinstance(tokens, int):
            raise ConfigError(f"max_output_tokens must be an integer, got {type(tokens).__name__}")
        if tokens < 1 or tokens > 100000:
            raise ConfigError(f"max_output_tokens must be between 1 and 100000, got {tokens}")

    # Validate max_retries (1 to 10)
    if config.get("max_retries") is not None:
        retries = config["max_retries"]
        if not isinstance(retries, int):
            raise ConfigError(f"max_retries must be an integer, got {type(retries).__name__}")
        if retries < 1 or retries > 10:
            raise ConfigError(f"max_retries must be between 1 and 10, got {retries}")

    # Validate warning_limit_tokens (must be positive)
    if config.get("warning_limit_tokens") is not None:
        warning_limit = config["warning_limit_tokens"]
        if not isinstance(warning_limit, int):
            raise ConfigError(f"warning_limit_tokens must be an integer, got {type(warning_limit).__name__}")
        if warning_limit < 1:
            raise ConfigError(f"warning_limit_tokens must be positive, got {warning_limit}")

    # Validate hook_timeout (must be positive)
    if config.get("hook_timeout") is not None:
        hook_timeout = config["hook_timeout"]
        if not isinstance(hook_timeout, int):
            raise ConfigError(f"hook_timeout must be an integer, got {type(hook_timeout).__name__}")
        if hook_timeout < 1:
            raise ConfigError(f"hook_timeout must be positive, got {hook_timeout}")


def load_config() -> GACConfig:
    """Load configuration from $HOME/.gac.env, then ./.gac.env, then environment variables."""
    user_config = Path.home() / ".gac.env"
    if user_config.exists():
        load_dotenv(user_config)

    # Check for .gac.env in project directory
    project_gac_env = Path(".gac.env")

    if project_gac_env.exists():
        load_dotenv(project_gac_env, override=True)

    config: GACConfig = {
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
        "no_verify_ssl": os.getenv("GAC_NO_VERIFY_SSL", str(EnvDefaults.NO_VERIFY_SSL)).lower()
        in ("true", "1", "yes", "on"),
        "verbose": os.getenv("GAC_VERBOSE", str(EnvDefaults.VERBOSE)).lower() in ("true", "1", "yes", "on"),
        "system_prompt_path": os.getenv("GAC_SYSTEM_PROMPT_PATH"),
        "language": os.getenv("GAC_LANGUAGE"),
        "translate_prefixes": os.getenv("GAC_TRANSLATE_PREFIXES", "false").lower() in ("true", "1", "yes", "on"),
        "rtl_confirmed": os.getenv("GAC_RTL_CONFIRMED", "false").lower() in ("true", "1", "yes", "on"),
        "hook_timeout": int(os.getenv("GAC_HOOK_TIMEOUT", EnvDefaults.HOOK_TIMEOUT)),
    }

    validate_config(config)
    return config
