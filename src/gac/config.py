import os
from pathlib import Path
from typing import Dict, Union

from dotenv import load_dotenv

from gac.constants import EnvDefaults, Logging


def load_config() -> Dict[str, Union[str, int, float, bool]]:
    """Load configuration from environment files with precedence.

    Order of precedence (lowest to highest):
    1. Package-level _config.env
    2. User-specific ~/.gac.env
    3. Project-level ./.env
    4. Project-level ./.gac.env
    5. Environment variables (highest priority)

    Returns:
        Dict with configuration values.
    """
    # (lowest priority) Package-level _config.env
    package_config = Path(__file__).parent / "_config.env"
    if package_config.exists():
        load_dotenv(package_config)
    # User-specific configuration
    user_config = Path.home() / ".gac.env"
    if user_config.exists():
        load_dotenv(user_config)
    # Project-level ./.env
    env_config = Path(".env")
    if env_config.exists():
        load_dotenv(env_config)
    # (highest priority) Project-level .gac.env
    project_config = Path(".gac.env")
    if project_config.exists():
        load_dotenv(project_config)

    config = {
        "model": os.getenv("GAC_MODEL"),
        "backup_model": os.getenv("GAC_BACKUP_MODEL"),
        "format_files": os.getenv("GAC_FORMAT_FILES", "true").lower() == "true",
        "temperature": float(os.getenv("GAC_TEMPERATURE", EnvDefaults.TEMPERATURE)),
        "max_output_tokens": int(os.getenv("GAC_MAX_OUTPUT_TOKENS", EnvDefaults.MAX_OUTPUT_TOKENS)),
        "max_retries": int(os.getenv("GAC_RETRIES", EnvDefaults.MAX_RETRIES)),
        "log_level": os.getenv("GAC_LOG_LEVEL", Logging.DEFAULT_LEVEL),
    }

    return config
