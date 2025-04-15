"""Git operations for GAC.

This module provides a simplified interface to Git commands.
It focuses on the core operations needed for commit generation.
"""

import logging
import os
import subprocess
from typing import List, Optional

from gac.errors import GitError
from gac.utils import run_subprocess

logger = logging.getLogger(__name__)


def run_git_command(args: List[str], silent: bool = False, timeout: int = 30) -> str:
    """Run a git command and return the output."""
    command = ["git"] + args
    return run_subprocess(command, silent=silent, timeout=timeout, raise_on_error=False, strip_output=True)


def get_staged_files(file_type: Optional[str] = None, existing_only: bool = False) -> List[str]:
    """Get list of staged files with optional filtering.

    Args:
        file_type: Optional file extension to filter by
        existing_only: If True, only include files that exist on disk

    Returns:
        List of staged file paths
    """
    try:
        output = run_git_command(["diff", "--name-only", "--cached"])
        if not output:
            return []

        # Parse and filter the file list
        files = [line.strip() for line in output.splitlines() if line.strip()]

        if file_type:
            files = [f for f in files if f.endswith(file_type)]

        if existing_only:
            files = [f for f in files if os.path.isfile(f)]

        return files
    except GitError:
        # If git command fails, return empty list as a fallback
        return []


def get_repo_root() -> str:
    """Get absolute path of repository root."""
    result = subprocess.check_output(["git", "rev-parse", "--show-toplevel"])
    return result.decode().strip()


def get_current_branch() -> str:
    """Get name of current git branch."""
    result = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    return result.decode().strip()


def get_commit_hash() -> str:
    """Get SHA-1 hash of current commit."""
    result = subprocess.check_output(["git", "rev-parse", "HEAD"])
    return result.decode().strip()


def push_changes() -> bool:
    """Push committed changes to the remote repository."""
    remote_exists = run_git_command(["remote"])
    if not remote_exists:
        logger.error("No configured remote repository.")
        return False

    try:
        run_git_command(["push"])
        return True
    except GitError as e:
        if "fatal: No configured push destination" in str(e):
            logger.error("No configured push destination.")
        else:
            logger.error(f"Failed to push changes: {e}")
        return False
