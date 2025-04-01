"""Git-related utility functions for GAC."""

import logging
import os
import subprocess
import warnings
from enum import Enum
from typing import Any, Dict, List, Optional

from rich.panel import Panel

from gac.ai import count_tokens, generate_commit_message
from gac.errors import GACError, GitError, handle_error, with_error_handling
from gac.files import file_matches_pattern
from gac.prompt import build_prompt, clean_commit_message, create_abbreviated_prompt
from gac.utils import console

# Set up logger
logger = logging.getLogger(__name__)


class FileStatus(Enum):
    """File status for Git operations."""

    MODIFIED = "M"
    ADDED = "A"
    DELETED = "D"
    RENAMED = "R"
    COPIED = "C"
    UNTRACKED = "?"


# For backward compatibility with tests
def run_subprocess(command: List[str], check: bool = True) -> str:
    """
    Run a subprocess command and return the output.

    Args:
        command: Command to run as a list of strings
        check: Whether to check the return code

    Returns:
        Command output as string
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=check,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e.stderr.strip()}")
        if check:
            raise
        return ""
    except Exception as e:
        logger.error(f"Error running command: {e}")
        if check:
            raise
        return ""


# Global for test mock injection
_git_operations = None


def get_git_operations():
    """Get the current git operations implementation.

    DEPRECATED: This function is deprecated and will be removed in a future version.
    Use the function-based API directly instead.
    """
    warnings.warn(
        "get_git_operations is deprecated and will be removed in a future version. "
        "Use the function-based API directly instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    global _git_operations
    if _git_operations is None:
        _git_operations = RealGitOperations()
    return _git_operations


def set_git_operations(operations):
    """Set the git operations implementation.

    DEPRECATED: This function is deprecated and will be removed in a future version.
    Use the function-based API directly instead.
    """
    warnings.warn(
        "set_git_operations is deprecated and will be removed in a future version. "
        "Use the function-based API directly instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    global _git_operations
    _git_operations = operations


# Constants for file handling
MAX_DIFF_TOKENS = 2500  # Maximum number of tokens to include for large files
# Files that are usually auto-generated or less important for commit context
LARGE_FILE_PATTERNS = [
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "Cargo.lock",
    "poetry.lock",
    "*.lock",
    "node_modules/*",
    "dist/*",
    "build/*",
]


def run_git_command(args: List[str], silent: bool = False, timeout: int = 30) -> str:
    """
    Run a git command and return the output.

    Args:
        args: List of arguments to pass to git
        silent: If True, suppress debug logging
        timeout: Command timeout in seconds

    Returns:
        Command output as string, or empty string on error
    """
    if not silent:
        logger.debug(f"Running git command: git {' '.join(args)}")

    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        if not silent:
            logger.error(f"Git command failed: {e.stderr.strip()}")
        return ""
    except subprocess.TimeoutExpired:
        logger.error(f"Git command timed out: git {' '.join(args)}")
        return ""


@with_error_handling(GitError, "Failed to determine git directory")
def ensure_git_directory() -> Optional[str]:
    """
    Ensure we're in a git repository and change to the root directory if needed.

    Returns:
        The git repository root directory or None if not a git repository
    """
    # Try to get the git root directory
    git_dir = run_git_command(["rev-parse", "--show-toplevel"])
    if not git_dir:
        logger.error("Not in a git repository")
        return None

    # Change to the git repository root if we're not already there
    current_dir = os.getcwd()
    if git_dir and git_dir != current_dir:
        logger.debug(f"Changing directory to git root: {git_dir}")
        os.chdir(git_dir)

    return git_dir


def get_status() -> str:
    """
    Get git status.

    Returns:
        Git status output as string
    """
    return run_git_command(["status"])


def get_staged_files(file_type: Optional[str] = None, existing_only: bool = False) -> List[str]:
    """
    Get list of staged files with optional filtering.

    Args:
        file_type: Optional file extension to filter by (e.g., ".py")
        existing_only: If True, only return files that exist on disk

    Returns:
        List of staged file paths
    """
    # Get list of staged files
    output = run_git_command(["diff", "--name-only", "--cached"])
    if not output:
        return []

    # Parse the output to get files
    files = [line.strip() for line in output.splitlines() if line.strip()]

    # Apply filters if needed
    if file_type:
        files = [f for f in files if f.endswith(file_type)]

    if existing_only:
        files = [f for f in files if os.path.isfile(f)]

    return files


def get_staged_files_with_status() -> Dict[str, str]:
    """
    Get staged files with their status (M, A, D, R, etc.).

    Returns:
        Dictionary mapping file paths to their status
    """
    result = run_git_command(["status", "-s"])
    if not result:
        return {}

    staged_files = {}
    for line in result.splitlines():
        if not line or len(line) < 3:
            continue

        # Parse the status line
        # Format is XY PATH where X is staged status, Y is unstaged status
        staged_status = line[0]
        path = line[3:].strip()

        # Only include files that are staged (status is not space)
        if staged_status != " " and staged_status != "?":
            staged_files[path] = staged_status

    return staged_files


def get_staged_diff() -> str:
    """
    Get the diff of staged changes.

    Returns:
        Git diff output as string
    """
    return run_git_command(["diff", "--staged"])


@with_error_handling(GitError, "Failed to stage files")
def stage_files(files: List[str]) -> bool:
    """
    Stage the specified files.

    Args:
        files: List of files to stage

    Returns:
        True if successful, False otherwise
    """
    if not files:
        return False

    run_git_command(["add"] + files)
    return True


@with_error_handling(GitError, "Failed to stage all files")
def stage_all_files() -> bool:
    """
    Stage all changes.

    Returns:
        True if successful, False otherwise
    """
    run_git_command(["add", "--all"])
    return True


@with_error_handling(GitError, "Failed to commit changes")
def perform_commit(message: str) -> bool:
    """
    Commit staged changes with the given message.

    Args:
        message: Commit message

    Returns:
        True if successful, False otherwise
    """
    if not message:
        return False

    run_git_command(["commit", "-m", message])
    return True


@with_error_handling(GitError, "Failed to push changes")
def push_changes() -> bool:
    """
    Push committed changes to the remote repository.

    Returns:
        True if successful, False otherwise
    """
    run_git_command(["push"])
    return True


def generate_commit(
    staged_files: Optional[List[str]] = None,
    formatting: bool = True,
    model: Optional[str] = None,
    hint: str = "",
    one_liner: bool = False,
    show_prompt: bool = False,
    show_prompt_full: bool = False,
    quiet: bool = False,
    no_spinner: bool = False,
) -> Optional[str]:
    """
    Generate a commit message based on staged changes.

    DEPRECATED: This function is deprecated and will be removed in a future version.
    Use generate_commit_with_options with a dictionary created by create_generate_options
    instead.

    Args:
        staged_files: Optional list of staged files (if None, all staged files are used)
        formatting: Whether to format code
        model: Override model to use
        hint: Additional context for the prompt
        one_liner: Generate a single-line commit message
        show_prompt: Show an abbreviated version of the prompt
        show_prompt_full: Show the complete prompt
        quiet: Suppress non-error output
        no_spinner: Disable progress spinner during API calls

    Returns:
        Generated commit message or None if failed
    """
    warnings.warn(
        "generate_commit with individual parameters is deprecated and will be removed "
        "in a future version. Use generate_commit_with_options with a dictionary "
        "created by create_generate_options instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    # Create options dictionary
    options = create_generate_options(
        staged_files=staged_files,
        formatting=formatting,
        model=model,
        hint=hint,
        one_liner=one_liner,
        show_prompt=show_prompt,
        show_prompt_full=show_prompt_full,
        quiet=quiet,
        no_spinner=no_spinner,
    )

    # Delegate to generate_commit_with_options
    return generate_commit_with_options(options)


def create_commit_options(
    message: Optional[str] = None,
    staged_files: Optional[List[str]] = None,
    force: bool = False,
    add_all: bool = False,
    formatting: bool = True,
    model: Optional[str] = None,
    hint: str = "",
    one_liner: bool = False,
    show_prompt: bool = False,
    show_prompt_full: bool = False,
    quiet: bool = False,
    no_spinner: bool = False,
    push: bool = False,
) -> Dict[str, Any]:
    """
    Create a dictionary with commit options.

    Args:
        message: Optional pre-generated commit message
        staged_files: Optional list of staged files
        force: Skip all confirmation prompts
        add_all: Stage all changes before committing
        formatting: Whether to format code
        model: Override model to use
        hint: Additional context for the prompt
        one_liner: Generate a single-line commit message
        show_prompt: Show an abbreviated version of the prompt
        show_prompt_full: Show the complete prompt
        quiet: Suppress non-error output
        no_spinner: Disable progress spinner during API calls
        push: Push changes to remote after committing

    Returns:
        Dictionary with commit options
    """
    return {
        "message": message,
        "staged_files": staged_files,
        "force": force,
        "add_all": add_all,
        "formatting": formatting,
        "model": model,
        "hint": hint,
        "one_liner": one_liner,
        "show_prompt": show_prompt,
        "show_prompt_full": show_prompt_full,
        "quiet": quiet,
        "no_spinner": no_spinner,
        "push": push,
    }


@with_error_handling(GitError, "Failed to commit changes", exit_on_error=False)
def commit_changes_with_options(options: Dict[str, Any]) -> Optional[str]:
    """
    Generate commit message and commit staged changes using an options dictionary.

    This is the preferred function for committing changes, as it uses a
    dictionary of options instead of numerous individual parameters.

    Args:
        options: Dictionary with commit options

    Returns:
        The generated commit message or None if failed
    """
    logger.debug(f"commit_changes_with_options called with add_all={options.get('add_all')}")

    # Ensure we're in a git repository and prepare for commit
    prep_result = prepare_commit(options)
    if not prep_result.get("success"):
        logger.error(prep_result.get("error", "Failed to prepare commit"))
        return None

    # Use provided message or generate one
    message = options.get("message")
    if not message:
        # Create generation options dictionary for generate_commit
        gen_options = {
            "staged_files": prep_result["staged_files"],
            "formatting": False,  # Formatting already done in prepare_commit
            "model": options.get("model"),
            "hint": options.get("hint", ""),
            "one_liner": options.get("one_liner", False),
            "show_prompt": options.get("show_prompt", False),
            "show_prompt_full": options.get("show_prompt_full", False),
            "quiet": options.get("quiet", False),
            "no_spinner": options.get("no_spinner", False),
        }

        message = generate_commit_with_options(gen_options)

    if not message:
        logger.error("Failed to generate commit message.")
        return None

    # Always display the commit message
    if not options.get("quiet"):
        console.print(Panel(message, title="Suggested Commit Message", border_style="bright_blue"))

    # If force mode is not enabled, prompt for confirmation
    if not options.get("force") and not options.get("quiet"):
        confirm = input("\nProceed with this commit message? (y/n): ").strip().lower()
        if confirm == "n":
            print("Commit cancelled.")
            return None

    # Execute the commit
    success = perform_commit(message)
    if not success:
        handle_error(GACError("Failed to commit changes"), quiet=options.get("quiet"))
        return None

    # Push changes if requested
    if options.get("push") and success:
        push_success = push_changes()
        if not push_success:
            handle_error(
                GACError("Failed to push changes"), quiet=options.get("quiet"), exit_program=False
            )

    return message


@with_error_handling(GitError, "Failed to check for staged changes", exit_on_error=False)
def has_staged_changes() -> bool:
    """
    Check if there are any staged changes.

    Returns:
        True if there are staged changes, False otherwise
    """
    return bool(get_staged_files())


def get_project_description() -> str:
    """Get a description of the current git project.

    Returns:
        A string describing the repository
    """
    try:
        # Try to get the repository URL
        remote_url = run_git_command(["config", "--get", "remote.origin.url"], silent=True)
        if remote_url:
            # Extract repository name from URL
            repo_name = remote_url.split("/")[-1].split(".")[0]
            return f"Repository: {repo_name}"
        else:
            # Fallback to getting the directory name
            git_dir = ensure_git_directory()
            if git_dir:
                repo_name = os.path.basename(git_dir)
                return f"Repository: {repo_name}"

        return "Unknown repository"
    except Exception as e:
        logger.debug(f"Error getting project description: {e}")
        return "Unknown repository"


def is_test_mode() -> bool:
    """Check if we're running in test mode."""
    return os.environ.get("GAC_TEST_MODE", "").lower() == "true"


def is_large_file(file_path: str) -> bool:
    """
    Check if a file is considered large or auto-generated.

    Args:
        file_path: Path to the file

    Returns:
        True if the file is large or auto-generated
    """
    # First check if the file matches known large file patterns
    if any(file_matches_pattern(file_path, pattern) for pattern in LARGE_FILE_PATTERNS):
        return True

    # If not a known pattern, check content size
    try:
        # Get the diff for the specific file
        diff = run_git_command(["diff", "--cached", "--", file_path])
        if not diff:
            return False

        # Count tokens in the diff
        token_count = count_tokens(diff, "test:model")

        # Consider large if token count exceeds threshold
        return token_count > MAX_DIFF_TOKENS
    except Exception as e:
        logger.debug(f"Error checking file size: {e}")
        return False


# Interface for testing with dependency injection
class GitOperations:
    """Interface for git operations.

    DEPRECATED: This class is deprecated and will be removed in a future version.
    Use the function-based API directly instead.
    """

    def __init__(self):
        """Initialize with deprecation warning."""
        warnings.warn(
            "The GitOperations class is deprecated and will be removed in a future version. "
            "Use the function-based API directly instead.",
            DeprecationWarning,
            stacklevel=2,
        )

    def run_git_command(self, args: List[str], silent: bool = False) -> str:
        """Run a git command and return the output."""
        raise NotImplementedError

    def ensure_git_directory(self) -> Optional[str]:
        """Ensure we're in a git repository."""
        raise NotImplementedError

    def get_status(self) -> str:
        """Get git status."""
        raise NotImplementedError

    def get_staged_files(self, file_type: Optional[str] = None) -> List[str]:
        """Get list of staged files."""
        raise NotImplementedError

    def get_staged_diff(self, file_path: Optional[str] = None) -> str:
        """Get the diff of staged changes."""
        raise NotImplementedError

    def stage_files(self, files: List[str]) -> bool:
        """Stage files for commit."""
        raise NotImplementedError

    def stage_all_files(self) -> bool:
        """Stage all files in the repository."""
        raise NotImplementedError

    def commit_changes(self, message: str) -> bool:
        """Commit staged changes with the given message."""
        raise NotImplementedError

    def push_changes(self) -> bool:
        """Push committed changes to the remote repository."""
        raise NotImplementedError

    def has_staged_changes(self) -> bool:
        """Check if there are any staged changes."""
        raise NotImplementedError


# Implementation that delegates to the function-based API
class RealGitOperations(GitOperations):
    """Real implementation of Git operations using the function-based API.

    DEPRECATED: This class is deprecated and will be removed in a future version.
    Use the function-based API directly instead.
    """

    def __init__(self, quiet: bool = False):
        """Initialize with quiet option."""
        super().__init__()  # Call parent to trigger deprecation warning
        self.quiet = quiet

    def run_git_command(self, args: List[str], silent: bool = False) -> str:
        """Run a git command and return the output."""
        return run_git_command(args, silent or self.quiet)

    def ensure_git_directory(self) -> Optional[str]:
        """Ensure we're in a git repository."""
        return ensure_git_directory()

    def get_status(self) -> str:
        """Get git status."""
        return get_status()

    def get_staged_files(self, file_type: Optional[str] = None) -> List[str]:
        """Get list of staged files."""
        return get_staged_files(file_type)

    def get_staged_diff(self, file_path: Optional[str] = None) -> str:
        """Get the diff of staged changes."""
        return get_staged_diff()

    def stage_files(self, files: List[str]) -> bool:
        """Stage files for commit."""
        return stage_files(files)

    def stage_all_files(self) -> bool:
        """Stage all files in the repository."""
        return stage_all_files()

    def commit_changes(self, message: str) -> bool:
        """Commit staged changes with the given message."""
        return perform_commit(message)

    def push_changes(self) -> bool:
        """Push committed changes to the remote repository."""
        return push_changes()

    def has_staged_changes(self) -> bool:
        """Check if there are any staged changes."""
        return has_staged_changes()


# NOTE: The GitOperationsManager is being deprecated in favor of direct function calls
# Tests should use the set_git_operations mechanism instead of this class
# This class will be removed in a future release


def create_generate_options(
    staged_files: Optional[List[str]] = None,
    formatting: bool = True,
    model: Optional[str] = None,
    hint: str = "",
    one_liner: bool = False,
    show_prompt: bool = False,
    show_prompt_full: bool = False,
    quiet: bool = False,
    no_spinner: bool = False,
) -> Dict[str, Any]:
    """
    Create a dictionary with commit message generation options.

    Args:
        staged_files: Optional list of staged files
        formatting: Whether to format code
        model: Override model to use
        hint: Additional context for the prompt
        one_liner: Generate a single-line commit message
        show_prompt: Show an abbreviated version of the prompt
        show_prompt_full: Show the complete prompt
        quiet: Suppress non-error output
        no_spinner: Disable progress spinner during API calls

    Returns:
        Dictionary with generation options
    """
    return {
        "staged_files": staged_files,
        "formatting": formatting,
        "model": model,
        "hint": hint,
        "one_liner": one_liner,
        "show_prompt": show_prompt,
        "show_prompt_full": show_prompt_full,
        "quiet": quiet,
        "no_spinner": no_spinner,
    }


@with_error_handling(GitError, "Failed to generate commit message", exit_on_error=False)
def generate_commit_with_options(options: Dict[str, Any]) -> Optional[str]:
    """
    Generate a commit message based on provided options dictionary.

    This is the preferred function for generating commit messages, as it uses a
    dictionary of options instead of numerous individual parameters.

    Args:
        options: Dictionary with generation settings

    Returns:
        Generated commit message or None if failed
    """
    # Import dependencies to avoid circular imports
    from gac.config import get_config

    # Prepare repository for commit (staging and formatting)
    if options.get("formatting", True):
        prep_result = prepare_commit(options)
        if not prep_result.get("success"):
            logger.error(prep_result.get("error", "Failed to prepare commit"))
            return None

        diff = prep_result["diff"]
        status = prep_result["status"]
    else:
        # Skip formatting, just get staged files and diff
        staged_files = options.get("staged_files")
        if staged_files is None:
            staged_files = get_staged_files()
            if not staged_files:
                logger.error("No staged changes found. Stage your changes with git add first.")
                return None

        diff = get_staged_diff()
        if not diff:
            logger.error("No diff found for staged changes.")
            return None

        status = get_status()

    # Build prompt for the LLM
    prompt = build_prompt(
        status=status,
        diff=diff,
        one_liner=options.get("one_liner", False),
        hint=options.get("hint", ""),
    )

    # Show prompt if requested
    if options.get("show_prompt") or options.get("show_prompt_full"):
        if not options.get("quiet"):
            # Create abbreviated prompt if not showing full prompt
            if options.get("show_prompt") and not options.get("show_prompt_full"):
                display_prompt = create_abbreviated_prompt(prompt)
            else:
                display_prompt = prompt

            console.print(
                Panel(
                    display_prompt,
                    title="Prompt for LLM",
                    border_style="bright_blue",
                )
            )

    # Get configuration
    config = get_config()
    model_override = options.get("model")
    if model_override:
        model_to_use = model_override
    else:
        model_to_use = config.get("model", "anthropic:claude-3-5-haiku-latest")

    # Always show a minimal message when generating the commit message
    if not options.get("quiet"):
        # Split provider:model if applicable
        if ":" in model_to_use:
            provider, model_name = model_to_use.split(":", 1)
            print(f"Using model: {model_name} with provider: {provider}")
        else:
            print(f"Using model: {model_to_use}")

    # Call the AI to generate the commit message
    temperature = float(config.get("temperature", 0.7))
    message = generate_commit_message(
        prompt=prompt,
        model=model_to_use,
        temperature=temperature,
        show_spinner=not options.get("no_spinner", False),
        test_mode="PYTEST_CURRENT_TEST" in os.environ,
    )

    if message:
        return clean_commit_message(message)
    return None


def commit_changes(
    message: Optional[str] = None,
    staged_files: Optional[List[str]] = None,
    force: bool = False,
    add_all: bool = False,
    formatting: bool = True,
    model: Optional[str] = None,
    hint: str = "",
    one_liner: bool = False,
    show_prompt: bool = False,
    show_prompt_full: bool = False,
    quiet: bool = False,
    no_spinner: bool = False,
    push: bool = False,
) -> Optional[str]:
    """
    Generate commit message and commit staged changes.

    DEPRECATED: This function is deprecated and will be removed in a future version.
    Use commit_changes_with_options with an options dictionary created by
    create_commit_options instead.

    Args:
        message: Optional pre-generated commit message
        staged_files: Optional list of staged files (if None, all staged files are used)
        force: Skip all confirmation prompts
        add_all: Stage all changes before committing
        formatting: Whether to format code
        model: Override model to use
        hint: Additional context for the prompt
        one_liner: Generate a single-line commit message
        show_prompt: Show an abbreviated version of the prompt
        show_prompt_full: Show the complete prompt
        quiet: Suppress non-error output
        no_spinner: Disable progress spinner during API calls
        push: Push changes to remote after committing

    Returns:
        The generated commit message or None if failed
    """
    warnings.warn(
        "commit_changes with individual parameters is deprecated and will be removed "
        "in a future version. Use commit_changes_with_options with an options dictionary "
        "created by create_commit_options instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    # Create options dictionary from the individual parameters
    options = create_commit_options(
        message=message,
        staged_files=staged_files,
        force=force,
        add_all=add_all,
        formatting=formatting,
        model=model,
        hint=hint,
        one_liner=one_liner,
        show_prompt=show_prompt,
        show_prompt_full=show_prompt_full,
        quiet=quiet,
        no_spinner=no_spinner,
        push=push,
    )

    # Delegate to commit_changes_with_options
    return commit_changes_with_options(options)


def get_git_status_summary() -> Dict[str, Any]:
    """
    Get a summary of the Git repository status.

    Returns:
        Dictionary with repository status information
    """
    # Ensure we're in a git repository
    repo_dir = ensure_git_directory()
    if not repo_dir:
        return {"valid": False, "repo_dir": None}

    # Get status and additional info
    return {
        "valid": True,
        "repo_dir": repo_dir,
        "status": get_status(),
        "has_staged": has_staged_changes(),
        "staged_files": get_staged_files(),
        "status_short": run_git_command(["status", "-s"], silent=True),
        "branch": run_git_command(["rev-parse", "--abbrev-ref", "HEAD"], silent=True),
    }


def apply_formatting_to_files(files: Dict[str, str]) -> List[str]:
    """
    Apply formatting to files and restage them.

    Args:
        files: Dictionary mapping file paths to their status

    Returns:
        List of formatted and staged files
    """
    # Import here to avoid circular imports
    from gac.format import format_files

    # Format files
    formatted_files = format_files(files)
    if not formatted_files:
        return []

    # Collect all formatted files
    all_formatted = []
    for files_list in formatted_files.values():
        all_formatted.extend(files_list)

    # Restage formatted files
    if all_formatted:
        stage_files(all_formatted)

    return all_formatted


def prepare_commit(options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare repository for commit by handling staging and formatting.

    Args:
        options: Dictionary with commit options

    Returns:
        Dictionary with prepared commit information
    """
    # Stage all files if requested
    if options.get("add_all"):
        stage_all_files()

    # Get staged files
    staged_files = options.get("staged_files") or get_staged_files()
    if not staged_files:
        return {"success": False, "error": "No staged changes found"}

    # Format files if requested
    if options.get("formatting"):
        files_with_status = get_staged_files_with_status()
        if files_with_status:
            formatted_files = apply_formatting_to_files(files_with_status)
            if formatted_files:
                # Update staged files list if any files were formatted
                staged_files = get_staged_files()

    # Get diff for staged files
    diff = get_staged_diff()
    if not diff:
        return {"success": False, "error": "No diff found for staged changes"}

    return {
        "success": True,
        "staged_files": staged_files,
        "diff": diff,
        "status": get_status(),
    }


def commit_workflow(
    message: Optional[str] = None,
    stage_all: bool = False,
    format_files: bool = True,
    model: Optional[str] = None,
    hint: str = "",
    one_liner: bool = False,
    show_prompt: bool = False,
    require_confirmation: bool = True,
    push: bool = False,
    quiet: bool = False,
) -> Dict[str, Any]:
    """
    Run the complete commit workflow in a functional way.

    This function composes the entire commit workflow using a pure functional approach,
    returning a dictionary with the result instead of using side effects.

    Args:
        message: Optional pre-generated commit message
        stage_all: Whether to stage all changes before committing
        format_files: Whether to format code
        model: Override model to use
        hint: Additional context for the prompt
        one_liner: Generate a single-line commit message
        show_prompt: Show the prompt sent to the LLM
        require_confirmation: Require user confirmation before committing
        push: Push changes to remote after committing
        quiet: Suppress non-error output

    Returns:
        Dictionary with the commit result
    """
    # Get repository status first
    status = get_git_status_summary()
    if not status.get("valid"):
        return {"success": False, "error": "Not in a git repository"}

    # Create options dictionary for the commit operation
    options = create_commit_options(
        message=message,
        add_all=stage_all,
        formatting=format_files,
        model=model,
        hint=hint,
        one_liner=one_liner,
        show_prompt=show_prompt,
        force=not require_confirmation,
        quiet=quiet,
        push=push,
    )

    # Execute the commit operation
    commit_message = commit_changes_with_options(options)

    # Return the result
    if commit_message:
        return {
            "success": True,
            "message": commit_message,
            "repository": status["repo_dir"],
            "branch": status["branch"],
            "pushed": push,
        }

    return {"success": False, "error": "Failed to commit changes"}
