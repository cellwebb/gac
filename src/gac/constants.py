"""Constants for the Git Auto Commit (GAC) project."""

from enum import Enum


class FileStatus(Enum):
    """File status for Git operations."""

    MODIFIED = "M"
    ADDED = "A"
    DELETED = "D"
    RENAMED = "R"
    COPIED = "C"
    UNTRACKED = "?"


# AI and Commit Message Generation Constants
MAX_RETRIES = 3
TEMPERATURE = 0.7
MAX_OUTPUT_TOKENS = 256

# Logging Constants
DEFAULT_LOG_LEVEL = "WARNING"
LOGGING_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR"]

# Utility Constants
DEFAULT_ENCODING = "cl100k_base"
