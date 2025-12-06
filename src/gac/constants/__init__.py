"""Constants for the Git Auto Commit (gac) project.

This package provides all constants used throughout gac, organized into
logical modules:

- defaults: Environment defaults, provider defaults, logging, and utility constants
- file_patterns: File pattern matching and importance weighting
- languages: Language code mappings for internationalization
- commit: Git file status and commit message constants

All constants are re-exported from this package for backward compatibility.
"""

from gac.constants.commit import CommitMessageConstants, FileStatus
from gac.constants.defaults import EnvDefaults, Logging, ProviderDefaults, Utility
from gac.constants.file_patterns import CodePatternImportance, FilePatterns, FileTypeImportance
from gac.constants.languages import Languages

__all__ = [
    # From defaults
    "EnvDefaults",
    "ProviderDefaults",
    "Logging",
    "Utility",
    # From file_patterns
    "FilePatterns",
    "FileTypeImportance",
    "CodePatternImportance",
    # From languages
    "Languages",
    # From commit
    "FileStatus",
    "CommitMessageConstants",
]
