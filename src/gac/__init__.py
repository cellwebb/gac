"""Git Auto Commit (GAC) - Generate commit messages using AI."""

from gac.__version__ import __version__
from gac.ai import generate_commit_message, generate_with_fallback
from gac.constants import EnvDefaults, FileStatus, Logging, Utility
from gac.format import format_files
from gac.git import get_staged_files, push_changes
from gac.prompt import build_prompt, clean_commit_message

__all__ = [
    "__version__",
    "generate_commit_message",
    "generate_with_fallback",
    "format_files",
    "build_prompt",
    "clean_commit_message",
    "get_staged_files",
    "push_changes",
]
