"""Git operations for gac.

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


def get_diff(
    staged: bool = True, color: bool = True, commit1: Optional[str] = None, commit2: Optional[str] = None
) -> str:
    """Get the diff between commits or working tree.

    Args:
        staged: If True, show staged changes. If False, show unstaged changes.
            This is ignored if commit1 and commit2 are provided.
        color: If True, include ANSI color codes in the output.
        commit1: First commit hash, branch name, or reference to compare from.
        commit2: Second commit hash, branch name, or reference to compare to.
            If only commit1 is provided, compares working tree to commit1.

    Returns:
        String containing the diff output

    Raises:
        GitError: If the git command fails
    """
    try:
        args = ["diff"]

        if color:
            args.append("--color")

        # If specific commits are provided, use them for comparison
        if commit1 and commit2:
            args.extend([commit1, commit2])
        elif commit1:
            args.append(commit1)
        elif staged:
            args.append("--cached")

        output = run_git_command(args)
        return output
    except Exception as e:
        logger.error(f"Failed to get diff: {str(e)}")
        raise GitError(f"Failed to get diff: {str(e)}")


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


def run_pre_commit_hooks() -> bool:
    """Run pre-commit hooks if they exist.

    Returns:
        True if pre-commit hooks passed or don't exist, False if they failed.
    """
    # Check if .pre-commit-config.yaml exists
    if not os.path.exists(".pre-commit-config.yaml"):
        logger.debug("No .pre-commit-config.yaml found, skipping pre-commit hooks")
        return True

    # Check if pre-commit is installed and configured
    try:
        # First check if pre-commit is installed
        result = run_subprocess(["pre-commit", "--version"], silent=True, raise_on_error=False)
        if not result:
            logger.debug("pre-commit not installed, skipping hooks")
            return True

        # Run pre-commit hooks on staged files
        logger.info("Running pre-commit hooks...")
        try:
            run_subprocess(["pre-commit", "run"], silent=False, raise_on_error=True)
            # If we get here, all hooks passed
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Pre-commit hooks failed with exit code {e.returncode}")
            return False
    except Exception as e:
        logger.debug(f"Error running pre-commit: {e}")
        # If pre-commit isn't available, don't block the commit
        return True


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
