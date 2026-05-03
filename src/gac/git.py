"""Git operations for gac.

This module provides a simplified interface to Git commands.
It focuses on the core operations needed for commit generation.
"""

import logging
import os
import subprocess

from gac.errors import GitError
from gac.utils import run_subprocess

logger = logging.getLogger(__name__)


def run_subprocess_with_encoding_fallback(
    command: list[str], silent: bool = False, timeout: int = 60
) -> subprocess.CompletedProcess[str]:
    """Run subprocess with encoding fallback, returning full CompletedProcess object.

    This is used for cases where we need both stdout and stderr separately,
    like pre-commit and lefthook hook execution.

    Args:
        command: List of command arguments
        silent: If True, suppress debug logging
        timeout: Command timeout in seconds

    Returns:
        CompletedProcess object with stdout, stderr, and returncode
    """
    from gac.utils import get_safe_encodings

    encodings = get_safe_encodings()
    last_exception: Exception | None = None

    for encoding in encodings:
        try:
            if not silent:
                logger.debug(f"Running command: {' '.join(command)} (encoding: {encoding})")

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout,
                encoding=encoding,
                errors="replace",
            )
            return result
        except UnicodeError as e:
            last_exception = e
            if not silent:
                logger.debug(f"Failed to decode with {encoding}: {e}")
            continue
        except subprocess.TimeoutExpired:
            raise
        except (subprocess.SubprocessError, OSError, FileNotFoundError) as e:
            if not silent:
                logger.debug(f"Command error: {e}")
            # Try next encoding for non-timeout errors
            last_exception = e
            continue

    # If we get here, all encodings failed
    if last_exception:
        raise subprocess.CalledProcessError(1, command, "", f"Encoding error: {last_exception}") from last_exception
    else:
        raise subprocess.CalledProcessError(1, command, "", "All encoding attempts failed")


def run_git_command(args: list[str], silent: bool = False, timeout: int = 30) -> str:
    """Run a git command and return the output."""
    command = ["git"] + args
    return run_subprocess(command, silent=silent, timeout=timeout, raise_on_error=False, strip_output=True)


def get_staged_files(file_type: str | None = None, existing_only: bool = False) -> list[str]:
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


def get_staged_status() -> str:
    """Get formatted status of staged files only, excluding unstaged/untracked files.

    Returns:
        Formatted status string with M/A/D/R indicators
    """
    try:
        output = run_git_command(["diff", "--name-status", "--staged"])
        if not output:
            return "No changes staged for commit."

        status_map = {
            "M": "modified",
            "A": "new file",
            "D": "deleted",
            "R": "renamed",
            "C": "copied",
            "T": "typechange",
        }

        status_lines = ["Changes to be committed:"]
        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue

            # Parse status line (e.g., "M\tfile.py" or "R100\told.py\tnew.py")
            parts = line.split("\t")
            if len(parts) < 2:
                continue

            change_type = parts[0][0]  # First char is the status (M, A, D, R, etc.)
            file_path = parts[-1]  # Last part is the new/current file path

            status_label = status_map.get(change_type, "modified")
            status_lines.append(f"\t{status_label}:   {file_path}")

        return "\n".join(status_lines)
    except GitError:
        return "No changes staged for commit."


def get_diff(staged: bool = True, color: bool = True, commit1: str | None = None, commit2: str | None = None) -> str:
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
    except (subprocess.SubprocessError, OSError, FileNotFoundError) as e:
        logger.error(f"Failed to get diff: {str(e)}")
        raise GitError(f"Failed to get diff: {str(e)}") from e


def get_repo_root() -> str:
    """Get absolute path of repository root."""
    result = run_git_command(["rev-parse", "--show-toplevel"])
    return result


def get_current_branch() -> str:
    """Get name of current git branch."""
    result = run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])
    return result


def get_commit_hash() -> str:
    """Get SHA-1 hash of current commit."""
    result = run_git_command(["rev-parse", "HEAD"])
    return result


def _run_hook_runner(
    *,
    name: str,
    display_name: str,
    config_files: list[str],
    run_args: list[str],
    hook_timeout: int = 120,
) -> bool:
    """Run a hook runner (pre-commit or lefthook) if configured.

    Args:
        name: Binary name (e.g. "pre-commit", "lefthook")
        display_name: Human-readable name for log messages (e.g. "Pre-commit", "Lefthook")
        config_files: List of possible config filenames to check for
        run_args: Full command to run the hooks
        hook_timeout: Timeout in seconds

    Returns:
        True if hooks passed or don't exist, False if they failed.
    """
    # Check if any config file exists
    if not any(os.path.exists(f) for f in config_files):
        logger.debug(f"No {display_name} configuration found, skipping {display_name} hooks")
        return True

    # Check if the binary is installed
    try:
        version_check = run_subprocess([name, "--version"], silent=True, raise_on_error=False)
        if not version_check:
            logger.debug(f"{display_name} not installed, skipping hooks")
            return True

        # Run the hooks
        logger.info(f"Running {display_name} hooks with {hook_timeout}s timeout...")
        result = run_subprocess_with_encoding_fallback(run_args, timeout=hook_timeout)

        if result.returncode == 0:
            return True
        else:
            output = result.stdout or ""
            error = result.stderr or ""
            full_output = output + ("\n" + error if error else "")

            if full_output.strip():
                logger.error(f"{display_name} hooks failed:\n{full_output}")
            else:
                logger.error(f"{display_name} hooks failed with exit code {result.returncode}")
            return False
    except (subprocess.SubprocessError, OSError, FileNotFoundError, PermissionError) as e:
        logger.debug(f"Error running {display_name}: {e}")
        return True


def run_pre_commit_hooks(hook_timeout: int = 120) -> bool:
    """Run pre-commit hooks if they exist.

    Returns:
        True if pre-commit hooks passed or don't exist, False if they failed.
    """
    return _run_hook_runner(
        name="pre-commit",
        display_name="Pre-commit",
        config_files=[".pre-commit-config.yaml"],
        run_args=["pre-commit", "run"],
        hook_timeout=hook_timeout,
    )


def run_lefthook_hooks(hook_timeout: int = 120) -> bool:
    """Run Lefthook hooks if they exist.

    Returns:
        True if Lefthook hooks passed or don't exist, False if they failed.
    """
    return _run_hook_runner(
        name="lefthook",
        display_name="Lefthook",
        config_files=[".lefthook.yml", "lefthook.yml", ".lefthook.yaml", "lefthook.yaml"],
        run_args=["lefthook", "run", "pre-commit"],
        hook_timeout=hook_timeout,
    )


def push_changes() -> bool:
    """Push committed changes to the remote repository."""
    remote_exists = run_git_command(["remote"])
    if not remote_exists:
        logger.error("No configured remote repository.")
        return False

    try:
        # Use raise_on_error=True to properly catch push failures
        run_subprocess(["git", "push"], raise_on_error=True, strip_output=True)
        return True
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else str(e)
        if "fatal: No configured push destination" in error_msg:
            logger.error("No configured push destination.")
        else:
            logger.error(f"Failed to push changes: {error_msg}")
        return False
    except (subprocess.SubprocessError, OSError, ConnectionError) as e:
        logger.error(f"Failed to push changes: {e}")
        return False


def detect_rename_mappings(staged_diff: str) -> dict[str, str]:
    """Detect file rename mappings from a staged diff.

    Args:
        staged_diff: The output of 'git diff --cached --binary'

    Returns:
        Dictionary mapping new_file_path -> old_file_path for rename operations
    """
    rename_mappings = {}
    lines = staged_diff.split("\n")

    i = 0
    while i < len(lines):
        line = lines[i]

        if line.startswith("diff --git a/"):
            # Scan following lines for rename markers and path lines.
            # Prefer "rename from"/"rename to" lines for path extraction —
            # they are unambiguous even when paths contain " a/" or " b/".
            # Fall back to header parsing only when those lines are absent.
            j = i + 1
            is_rename = False
            rename_from = None
            rename_to = None

            while j < len(lines) and not lines[j].startswith("diff --git"):
                if lines[j].startswith("similarity index "):
                    is_rename = True
                elif lines[j].startswith("rename from "):
                    is_rename = True
                    rename_from = lines[j][len("rename from ") :]
                elif lines[j].startswith("rename to "):
                    rename_to = lines[j][len("rename to ") :]
                j += 1

            if is_rename:
                if rename_from and rename_to:
                    # Only use rename-from/to lines — they are unambiguous.
                    # Header parsing (split on " a/" or " b/") is fundamentally
                    # ambiguous when paths contain those substrings, so we
                    # produce no mapping when rename lines are absent.
                    if rename_from != rename_to:
                        rename_mappings[rename_to] = rename_from

        i += 1

    return rename_mappings
