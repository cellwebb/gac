"""Git operations for GAC."""

import logging
import os
from typing import List, Optional

from gac.errors import GitError, with_error_handling
from gac.utils import run_subprocess

logger = logging.getLogger(__name__)


def run_git_command(args: List[str], silent: bool = False, timeout: int = 30) -> str:
    """Run a git command and return the output."""
    command = ["git"] + args
    return run_subprocess(command, silent=silent, timeout=timeout, raise_on_error=False, strip_output=True)


def get_staged_files(file_type: Optional[str] = None, existing_only: bool = False) -> List[str]:
    """Get list of staged files with optional filtering."""
    output = run_git_command(["diff", "--name-only", "--cached"])
    if not output:
        return []
    files = [line.strip() for line in output.splitlines() if line.strip()]
    if file_type:
        files = [f for f in files if f.endswith(file_type)]
    if existing_only:
        files = [f for f in files if os.path.isfile(f)]
    return files


@with_error_handling(GitError, "Failed to push changes")
def push_changes() -> bool:
    """Push committed changes to the remote repository."""
    remote_exists = run_git_command(["remote"])
    if not remote_exists:
        logger.error("No configured remote repository.")
        return False

    try:
        run_git_command(["push"])
    except GitError as e:
        if "fatal: No configured push destination" in str(e):
            logger.error("No configured push destination.")
            return False

    return True
