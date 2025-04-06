"""Git Auto Commit (GAC) - Generate commit messages using AI."""

from gac.__about__ import __version__
from gac.ai import generate_commit_message
from gac.format import format_files
from gac.git import (
    commit_changes_with_options,
    create_commit_options,
    get_staged_files,
    get_status,
    perform_commit,
    push_changes,
    stage_all_files,
    stage_files,
)
from gac.prompt import build_prompt, clean_commit_message

__all__ = [
    "__version__",
    "generate_commit_message",
    "commit_changes_with_options",
    "create_commit_options",
    "format_files",
    "build_prompt",
    "clean_commit_message",
    "get_staged_files",
    "get_status",
    "stage_all_files",
    "stage_files",
    "perform_commit",
    "push_changes",
]
