"""Git operations for GAC."""

import logging
import os
from enum import Enum
from typing import Any, Dict, List, Optional

from rich.panel import Panel

from gac.ai import count_tokens, generate_commit_message
from gac.errors import AIError, GACError, GitError, handle_error, with_error_handling
from gac.prompt import build_prompt, clean_commit_message, create_abbreviated_prompt
from gac.utils import console, file_matches_pattern, run_subprocess

logger = logging.getLogger(__name__)


class FileStatus(Enum):
    """File status for Git operations."""

    MODIFIED = "M"
    ADDED = "A"
    DELETED = "D"
    RENAMED = "R"
    COPIED = "C"
    UNTRACKED = "?"


MAX_DIFF_TOKENS = 2500
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
    command = ["git"] + args
    return run_subprocess(
        command, silent=silent, timeout=timeout, raise_on_error=False, strip_output=True
    )


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
    # First check if there's a configured remote repository
    remote_exists = run_git_command(["remote"])
    if not remote_exists:
        logger.error("No configured remote repository.")
        return False

    # Attempt to push changes
    result = run_git_command(["push"])
    if "fatal: No configured push destination" in result:
        logger.error("No configured push destination.")
        return False

    return "error" not in result.lower() and "fatal" not in result.lower()


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
    template: Optional[str] = None,
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
        template: Path to a custom prompt template file

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
        "template": template,
    }


@with_error_handling(GitError, "Failed to commit changes", exit_on_error=False)
def commit_changes_with_options(options: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Generate commit message and commit staged changes using an options dictionary.

    This is the preferred function for committing changes, as it uses a
    dictionary of options instead of numerous individual parameters.

    Args:
        options: Dictionary with commit options

    Returns:
        Dictionary with commit result or None if failed
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

    # Always display the suggested commit message panel, even in quiet mode
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
    pushed = False
    if options.get("push") and success:
        pushed = push_changes()
        if not pushed:
            handle_error(
                GACError("Failed to push changes"), quiet=options.get("quiet"), exit_program=False
            )

    return {"message": message, "pushed": pushed}


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
        token_count = count_tokens(diff, "anthropic:claude-3-5-haiku-latest")

        # Consider large if token count exceeds threshold
        return token_count > MAX_DIFF_TOKENS
    except Exception as e:
        logger.debug(f"Error checking file size: {e}")
        return False


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
    template: Optional[str] = None,
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
        template: Path to a custom prompt template file

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
        "template": template,
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
        template_path=options.get("template"),
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

    # Ensure model has provider prefix
    if ":" not in model_to_use:
        model_to_use = f"anthropic:{model_to_use}"
        logger.debug(f"Added provider prefix to model: {model_to_use}")

    # Get backup model from config if available
    backup_model = config.get("backup_model")

    # Ensure backup model has provider prefix if it exists
    if backup_model and ":" not in backup_model:
        backup_model = f"anthropic:{backup_model}"
        logger.debug(f"Added provider prefix to backup model: {backup_model}")

    # Only show model info when not in quiet mode
    if not options.get("quiet"):
        # Split provider:model if applicable
        if ":" in model_to_use:
            provider, model_name = model_to_use.split(":", 1)
            print(f"Using model: {model_name} with provider: {provider}")
        else:
            print(f"Using model: {model_to_use}")

        # Show backup model info if configured
        if backup_model:
            if ":" in backup_model:
                backup_provider, backup_model_name = backup_model.split(":", 1)
                print(
                    f"Backup model configured: {backup_model_name} with provider: {backup_provider}"
                )
            else:
                print(f"Backup model configured: {backup_model}")

    # Call the AI to generate the commit message
    temperature = float(config.get("temperature", 0.7))
    try:
        message = generate_commit_message(
            prompt=prompt,
            model=model_to_use,
            temperature=temperature,
            show_spinner=not options.get("no_spinner", False) and not options.get("quiet", False),
        )

        if message:
            return clean_commit_message(message)
        return None
    except AIError as e:
        if "Invalid model format" in str(e):
            logger.error(
                f"Invalid model format. Check your model configuration. "
                f"Model should be in format 'provider:model_name'. Got: '{model_to_use}'"
            )
            return None
        elif backup_model:
            # Primary model failed, try with backup model
            logger.info(
                f"Primary model failed with error: {e}. Trying backup model: {backup_model}"
            )
            if not options.get("quiet"):
                print(f"Primary model failed. Trying backup model: {backup_model}")

            try:
                # Reset and create new spinner for backup attempt
                show_spinner = not options.get("no_spinner", False) and not options.get(
                    "quiet", False
                )
                backup_message = generate_commit_message(
                    prompt=prompt,
                    model=backup_model,
                    temperature=temperature,
                    show_spinner=show_spinner,
                )

                if backup_message:
                    return clean_commit_message(backup_message)
                return None
            except AIError as backup_error:
                logger.error(f"Backup model also failed: {backup_error}")
                if not options.get("quiet"):
                    print("Backup model also failed.")
                return None
        else:
            logger.error(f"AI error: {e}")
            return None


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

    # Get staged files first to determine if there are staged changes
    staged_files = get_staged_files()

    # Get status and additional info
    return {
        "valid": True,
        "repo_dir": repo_dir,
        "status": get_status(),
        "has_staged": bool(staged_files),
        "staged_files": staged_files,
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
    template: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run the git commit workflow operations.

    This function handles the core git operations for the commit process.
    Application-level concerns should be handled in main.py.

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
        template: Path to a custom prompt template file

    Returns:
        Dictionary with the commit result
    """
    # Check if in a git repository
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
        template=template,
    )

    # Execute the commit operation
    commit_result = commit_changes_with_options(options)

    # Return the result
    if commit_result:
        return {
            "success": True,
            "message": commit_result["message"],
            "repository": status["repo_dir"],
            "branch": status["branch"],
            "pushed": commit_result.get("pushed", False),
        }

    return {"success": False, "error": "Failed to commit changes"}
