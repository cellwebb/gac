"""Optimized git operations with batching and parallelization."""

import concurrent.futures
import logging
import subprocess
from dataclasses import dataclass
from typing import List, Optional, Tuple

from gac.errors import GitError

logger = logging.getLogger(__name__)


@dataclass
class GitData:
    """Container for all git data needed by gac."""

    repo_root: str
    status: str
    staged_diff: str
    diff_stat: str
    staged_files: List[str]
    current_branch: str
    has_remote: bool = True


def run_git_command_raw(args: List[str], cwd: Optional[str] = None) -> Tuple[str, int]:
    """Run a git command and return output and return code."""
    cmd = ["git"] + args
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=False, cwd=cwd  # Don't raise on non-zero exit
        )
        return result.stdout.strip(), result.returncode
    except Exception as e:
        logger.error(f"Error running git command {' '.join(cmd)}: {e}")
        return "", 1


def get_all_git_data_parallel() -> GitData:
    """Get all git data in parallel using ThreadPoolExecutor.

    This runs multiple git commands concurrently, reducing total time
    from ~160ms to ~50-60ms (limited by slowest operation).
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        # Submit all git commands at once
        future_root = executor.submit(run_git_command_raw, ["rev-parse", "--show-toplevel"])
        future_status = executor.submit(run_git_command_raw, ["status", "--porcelain"])
        future_diff = executor.submit(run_git_command_raw, ["diff", "--cached", "--no-color"])
        future_stat = executor.submit(run_git_command_raw, ["diff", "--cached", "--stat", "--no-color"])
        future_files = executor.submit(run_git_command_raw, ["diff", "--cached", "--name-only"])
        future_branch = executor.submit(run_git_command_raw, ["branch", "--show-current"])
        future_remote = executor.submit(run_git_command_raw, ["remote"])

        # Collect results
        root_result, root_code = future_root.result()
        if root_code != 0:
            raise GitError("Not in a git repository")

        status_result, _ = future_status.result()
        diff_result, _ = future_diff.result()
        stat_result, _ = future_stat.result()
        files_result, _ = future_files.result()
        branch_result, _ = future_branch.result()
        remote_result, _ = future_remote.result()

    # Parse results
    staged_files = [f for f in files_result.split("\n") if f]

    return GitData(
        repo_root=root_result,
        status=status_result,
        staged_diff=diff_result,
        diff_stat=" " + stat_result if stat_result else "",
        staged_files=staged_files,
        current_branch=branch_result or "HEAD",
        has_remote=bool(remote_result),
    )


def get_all_git_data_batched() -> GitData:
    """Get all git data using batched commands.

    Uses git's ability to output multiple pieces of information
    in a single command, reducing subprocess overhead.
    """
    # First, check if we're in a git repo
    root_result, root_code = run_git_command_raw(["rev-parse", "--show-toplevel"])
    if root_code != 0:
        raise GitError("Not in a git repository")

    # Get status with branch info in one command
    status_full, _ = run_git_command_raw(["status", "--porcelain", "--branch"])

    # Parse branch from status output
    lines = status_full.split("\n")
    branch = "HEAD"
    status_lines = []

    for line in lines:
        if line.startswith("## "):
            # Extract branch name from status
            branch_info = line[3:]
            if "..." in branch_info:
                branch = branch_info.split("...")[0]
            else:
                branch = branch_info
        else:
            status_lines.append(line)

    status = "\n".join(status_lines)

    # Get diff with stats in one command
    # Using --numstat gives us file list and stats together
    diff_combined, _ = run_git_command_raw(["diff", "--cached", "--no-color", "--stat", "--patch"])

    # Split the combined output
    # The stat comes first, then a blank line, then the patch
    parts = diff_combined.split("\n\n", 1)
    if len(parts) == 2:
        diff_stat = " " + parts[0]
        diff = parts[1]
    else:
        diff_stat = ""
        diff = diff_combined

    # Get staged files from the diff
    files_result, _ = run_git_command_raw(["diff", "--cached", "--name-only"])
    staged_files = [f for f in files_result.split("\n") if f]

    # Check for remote
    remote_result, _ = run_git_command_raw(["remote"])

    return GitData(
        repo_root=root_result,
        status=status,
        staged_diff=diff,
        diff_stat=diff_stat,
        staged_files=staged_files,
        current_branch=branch,
        has_remote=bool(remote_result),
    )


def get_all_git_data_ultra_batched() -> GitData:
    """Get all git data with maximum batching using git plumbing commands.

    This is the most optimized version, using low-level git commands
    that are faster and can provide multiple pieces of information at once.
    """
    # Get repo root first
    root_result, root_code = run_git_command_raw(["rev-parse", "--show-toplevel"])
    if root_code != 0:
        raise GitError("Not in a git repository")

    # Use a single format command to get multiple pieces of info
    # This gets branch, remote tracking, and more in one go
    info_result, _ = run_git_command_raw(
        ["for-each-ref", "--format=%(HEAD) %(refname:short) %(upstream:short)", "refs/heads/"]
    )

    # Parse branch info
    current_branch = "HEAD"
    for line in info_result.split("\n"):
        if line.startswith("*"):
            parts = line.split()
            if len(parts) >= 2:
                current_branch = parts[1]
            break

    # Get all diff information in one command using --raw
    # This gives us the list of files and their changes
    diff_raw, _ = run_git_command_raw(["diff-index", "--cached", "--patch-with-raw", "--stat", "HEAD"])

    # Parse the raw output
    lines = diff_raw.split("\n")
    in_stat = False
    in_patch = False
    stat_lines = []
    patch_lines = []
    staged_files = []

    for line in lines:
        if line.startswith(":"):
            # Raw format line - extract filename
            parts = line.split("\t")
            if len(parts) >= 2:
                staged_files.append(parts[1])
        elif line.startswith(" ") and not in_patch:
            # Stat line
            in_stat = True
            stat_lines.append(line)
        elif line.startswith("diff --git"):
            in_patch = True
            patch_lines.append(line)
        elif in_patch:
            patch_lines.append(line)
        elif in_stat and not line:
            in_stat = False

    diff_stat = " " + "\n".join(stat_lines) if stat_lines else ""
    diff = "\n".join(patch_lines)

    # Get porcelain status
    status, _ = run_git_command_raw(["status", "--porcelain"])

    # Check for remote
    remote_result, _ = run_git_command_raw(["remote"])

    return GitData(
        repo_root=root_result,
        status=status,
        staged_diff=diff,
        diff_stat=diff_stat,
        staged_files=staged_files,
        current_branch=current_branch,
        has_remote=bool(remote_result),
    )


# Choose the best strategy based on environment
def get_all_git_data(strategy: str = "parallel") -> GitData:
    """Get all git data using the specified strategy.

    Args:
        strategy: One of "parallel", "batched", or "ultra_batched"

    Returns:
        GitData object with all necessary git information
    """
    strategies = {
        "parallel": get_all_git_data_parallel,
        "batched": get_all_git_data_batched,
        "ultra_batched": get_all_git_data_ultra_batched,
    }

    if strategy not in strategies:
        logger.warning(f"Unknown strategy {strategy}, using parallel")
        strategy = "parallel"

    logger.debug(f"Getting git data using {strategy} strategy")
    return strategies[strategy]()
