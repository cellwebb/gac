#!/usr/bin/env python3
"""Main entry point for GAC."""

import logging
import os
import sys
from pathlib import Path
from typing import Dict, Optional, Union

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from gac import __version__
from gac.ai import generate_commit_message
from gac.constants import (
    DEFAULT_LOG_LEVEL,
    DEFAULT_MAX_OUTPUT_TOKENS,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TEMPERATURE,
    LOGGING_LEVELS,
)
from gac.errors import AIError, GitError, handle_error
from gac.format import format_files
from gac.git import get_staged_files, push_changes, run_git_command
from gac.prompt import build_prompt, clean_commit_message
from gac.utils import print_message, setup_logging

logger = logging.getLogger(__name__)


def load_config() -> Dict[str, Union[str, int, float, bool]]:
    """Load configuration from environment files with precedence.

    Order of precedence (lowest to highest):
    1. Package-level _config.env
    2. User-specific ~/.gac.env
    3. Project-level ./.env
    4. Project-level ./.gac.env
    5. Environment variables (highest priority)

    Returns:
        Dict with configuration values.
    """
    # (lowest priority) Package-level _config.env
    package_config = Path(__file__).parent / "_config.env"
    if package_config.exists():
        load_dotenv(package_config)
    # User-specific configuration
    user_config = Path.home() / ".gac.env"
    if user_config.exists():
        load_dotenv(user_config)
    # Project-level ./.env
    env_config = Path(".env")
    if env_config.exists():
        load_dotenv(env_config)
    # (highest priority) Project-level .gac.env
    project_config = Path(".gac.env")
    if project_config.exists():
        load_dotenv(project_config)

    # Return config with defaults from constants
    return {
        "model": os.getenv("GAC_MODEL"),
        "backup_model": os.getenv("GAC_BACKUP_MODEL"),
        "format_files": os.getenv("GAC_FORMAT_FILES", "true").lower() == "true",
        "temperature": float(os.getenv("GAC_TEMPERATURE", DEFAULT_TEMPERATURE)),
        "max_output_tokens": int(os.getenv("GAC_MAX_OUTPUT_TOKENS", DEFAULT_MAX_OUTPUT_TOKENS)),
        "max_retries": int(os.getenv("GAC_RETRIES", DEFAULT_MAX_RETRIES)),
        "log_level": os.getenv("GAC_LOG_LEVEL", DEFAULT_LOG_LEVEL),
    }


# Load configuration
config = load_config()


@click.command()
@click.option("--add-all", "-a", is_flag=True, help="Stage all changes before committing")
@click.option(
    "--log-level",
    default=config["log_level"],
    type=click.Choice(LOGGING_LEVELS, case_sensitive=False),
    help=f"Set log level (default: {config['log_level']})",
)
@click.option("--no-format", "-nf", is_flag=True, help="Skip formatting of staged files")
@click.option("--one-liner", "-o", is_flag=True, help="Generate a single-line commit message")
@click.option("--push", "-p", is_flag=True, help="Push changes to remote after committing")
@click.option("--show-prompt", "-s", is_flag=True, help="Show the prompt sent to the LLM")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-error output")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
@click.option("--hint", "-h", default="", help="Additional context to include in the prompt")
@click.option("--model", "-m", help="Override the default model (format: 'provider:model_name')")
@click.option("--version", is_flag=True, help="Show the version of the Git Auto Commit (GAC) tool")
@click.option("--dry-run", is_flag=True, help="Dry run the commit workflow")
def cli(
    add_all: bool = False,
    log_level: str = config["log_level"],
    no_format: bool = False,
    one_liner: bool = False,
    push: bool = False,
    show_prompt: bool = False,
    quiet: bool = False,
    yes: bool = False,
    hint: str = "",
    model: str = None,
    version: bool = False,
    dry_run: bool = False,
):
    """Git Auto Commit - Generate commit messages with AI."""
    if version:
        print(f"Git Auto Commit (GAC) version: {__version__}")
        sys.exit(0)

    numeric_log_level = getattr(logging, log_level.upper(), logging.WARNING)
    setup_logging(numeric_log_level, quiet=quiet, force=True)

    main(
        stage_all=add_all,
        should_format_files=not no_format,
        model=model,
        hint=hint,
        one_liner=one_liner,
        show_prompt=show_prompt,
        require_confirmation=not yes,
        push=push,
        quiet=quiet,
        dry_run=dry_run,
    )


def main(
    stage_all: bool = False,
    should_format_files: Optional[bool] = None,
    model: Optional[str] = None,
    hint: str = "",
    one_liner: bool = False,
    show_prompt: bool = False,
    require_confirmation: bool = True,
    push: bool = False,
    quiet: bool = False,
    dry_run: bool = False,
) -> None:
    """Main application logic for GAC."""
    # Check if in a git repository

    try:
        git_dir = run_git_command(["rev-parse", "--show-toplevel"])
        if not git_dir:
            raise GitError("Not in a git repository")
    except Exception as e:
        logger.error(f"Error checking git repository: {e}")
        handle_error(GitError("Not in a git repository"), exit_program=True)
        raise Exception("Failed to exit program after git repository check failure")

    if model is None:
        model = config["model"]
        if model is None:
            handle_error(
                AIError.model_error(
                    "No model specified. Please set the GAC_MODEL environment variable or use --model."
                ),
                exit_program=True,
            )
            raise Exception("Failed to exit program after model error")
    if should_format_files is None:
        should_format_files = config["format_files"]

    backup_model = config["backup_model"]

    # Get environment variables from loaded config
    temperature = config["temperature"]
    max_output_tokens = config["max_output_tokens"]
    max_retries = config["max_retries"]

    if stage_all and (not dry_run):
        print_message("Staging all changes", "info")
        run_git_command(["add", "--all"])

    if not get_staged_files(existing_only=False):
        handle_error(
            GitError("No staged changes found. Stage your changes with git add first or use --add-all"),
            exit_program=True,
        )
        raise Exception("Failed to exit program after no staged changes found")

    if should_format_files:
        # TODO: Add logic for files that have both staged and unstaged changes
        files_to_format = get_staged_files(existing_only=True)
        formatted_files = format_files(files_to_format, dry_run=dry_run)
        if formatted_files and not dry_run:
            run_git_command(["add"] + formatted_files)

    prompt = build_prompt(
        status=run_git_command(["status"]), diff=run_git_command(["diff", "--staged"]), one_liner=one_liner, hint=hint
    )

    if show_prompt:
        console = Console()
        console.print(
            Panel(
                prompt,
                title="Prompt for LLM",
                border_style="bright_blue",
            )
        )

    try:
        commit_message = generate_commit_message(
            model,
            prompt,
            temperature=temperature,
            max_tokens=max_output_tokens,
            max_retries=max_retries,
            quiet=quiet,
        )
    except AIError as e:
        print_message(str(e), level="error")
        if not backup_model:
            print_message("No backup model specified in environment variables. Exiting...", level="error")
            sys.exit(1)

        print_message("Trying backup model...", level="info")
        try:
            commit_message = generate_commit_message(
                backup_model,
                prompt,
                temperature=temperature,
                max_tokens=max_output_tokens,
                max_retries=max_retries,
                quiet=quiet,
            )
        except AIError as e:
            print_message(str(e), level="error")
            print_message("Backup model unsuccessful. Exiting...", level="error")
            sys.exit(1)

    commit_message = clean_commit_message(commit_message)

    if dry_run:
        print_message("Dry run: would commit with message:", "notification")
        print(commit_message)
        staged_files = get_staged_files(existing_only=False)
        print_message(f"Dry run: would commit {len(staged_files)} files", "info")
        sys.exit(0)

    try:
        run_git_command(["commit", "-m", commit_message])
    except Exception as e:
        handle_error(
            GitError(f"Error committing changes: {e}"),
            exit_program=True,
        )
        return  # This line won't be reached due to exit_program=True

    # Verify that all changes were committed by checking for staged files
    staged_files = get_staged_files()
    if staged_files:
        handle_error(
            GitError("Commit failed: There are still staged changes after commit attempt"),
            exit_program=True,
        )
        return  # This line won't be reached due to exit_program=True

    if push:
        try:
            if not push_changes():
                handle_error(
                    GitError("Failed to push changes. Check your remote configuration."),
                    exit_program=True,
                )
                raise Exception("Failed to exit program after push failure")
        except Exception as e:
            handle_error(
                GitError(f"Error pushing changes: {e}"),
                exit_program=True,
            )
            raise Exception("Failed to exit program after push failure")

    if not quiet:
        print_message("Successfully committed changes with message:", "notification")
        print(commit_message)
        if push:
            print_message("Changes pushed to remote.", "notification")
    sys.exit(0)


if __name__ == "__main__":
    cli()
