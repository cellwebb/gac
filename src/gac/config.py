"""Configuration loading for gac.

Handles environment variable and .gac.env file precedence for application settings.
"""

import os
from pathlib import Path
from typing import TypedDict, cast

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
    use_50_72_rule: bool
    signoff: bool


def _parse_bool_env(key: str, default: bool) -> bool:
    """Parse a boolean environment variable with standard truthy values."""
    return os.getenv(key, str(default)).lower() in ("true", "1", "yes", "on")


_TYPE_DISPLAY_NAMES: dict[type, str] = {
    int: "integer",
    float: "number",
}

_CONFIG_VALIDATORS: list[tuple[str, type | tuple[type, ...], float | int | None, float | int | None]] = [
    # (field_name, expected_type, min_value, max_value) — None means no bound
    ("temperature", (int, float), 0.0, 2.0),
    ("max_output_tokens", int, 1, 100000),
    ("max_retries", int, 1, 10),
    ("warning_limit_tokens", int, 1, None),
    ("hook_timeout", int, 1, None),
]


def validate_config(config: GACConfig) -> None:
    """Validate configuration values at load time.

    Args:
        config: Configuration dictionary to validate

    Raises:
        ConfigError: If any configuration value is invalid
    """
    for field, expected_type, min_val, max_val in _CONFIG_VALIDATORS:
        value = config.get(field)
        if value is None:
            continue
        if not isinstance(value, expected_type):
            type_name = (
                "number"
                if isinstance(expected_type, tuple)
                else _TYPE_DISPLAY_NAMES.get(expected_type, expected_type.__name__)
            )
            article = "an" if type_name[0].lower() in "aeiou" else "a"
            raise ConfigError(f"{field} must be {article} {type_name}, got {type(value).__name__}")
        # isinstance check above guarantees value is numeric; cast for mypy
        numeric_value = cast(float, value)
        if min_val is not None and numeric_value < min_val:
            raise ConfigError(f"{field} must be >= {min_val}, got {value}")
        if max_val is not None and numeric_value > max_val:
            raise ConfigError(f"{field} must be <= {max_val}, got {value}")


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
        "always_include_scope": _parse_bool_env("GAC_ALWAYS_INCLUDE_SCOPE", EnvDefaults.ALWAYS_INCLUDE_SCOPE),
        "skip_secret_scan": _parse_bool_env("GAC_SKIP_SECRET_SCAN", EnvDefaults.SKIP_SECRET_SCAN),
        "no_verify_ssl": _parse_bool_env("GAC_NO_VERIFY_SSL", EnvDefaults.NO_VERIFY_SSL),
        "verbose": _parse_bool_env("GAC_VERBOSE", EnvDefaults.VERBOSE),
        "system_prompt_path": os.getenv("GAC_SYSTEM_PROMPT_PATH"),
        "language": os.getenv("GAC_LANGUAGE"),
        "translate_prefixes": _parse_bool_env("GAC_TRANSLATE_PREFIXES", False),
        "rtl_confirmed": _parse_bool_env("GAC_RTL_CONFIRMED", False),
        "hook_timeout": int(os.getenv("GAC_HOOK_TIMEOUT", EnvDefaults.HOOK_TIMEOUT)),
        "use_50_72_rule": _parse_bool_env("GAC_USE_50_72_RULE", EnvDefaults.USE_50_72_RULE),
        "signoff": _parse_bool_env("GAC_SIGNOFF", EnvDefaults.SIGNOFF),
    }

    validate_config(config)
    return config
