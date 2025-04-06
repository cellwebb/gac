#!/usr/bin/env python3
"""Main entry point for GAC."""

import logging
import os
import sys
from typing import Optional

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from gac import __about__
from gac.ai import generate_commit_message
from gac.constants import DEFAULT_LOG_LEVEL, LOGGING_LEVELS, MAX_OUTPUT_TOKENS, MAX_RETRIES, TEMPERATURE
from gac.errors import AIError, GitError, handle_error
from gac.format import format_files
from gac.git import get_staged_files, run_git_command
from gac.prompt import build_prompt
from gac.utils import print_message, setup_logging

logger = logging.getLogger(__name__)

load_dotenv(".gac.env")


@click.command()
@click.option("--add-all", "-a", is_flag=True, help="Stage all changes before committing")
@click.option(
    "--log-level",
    default=DEFAULT_LOG_LEVEL,
    type=click.Choice(LOGGING_LEVELS, case_sensitive=False),
    help=f"Set log level (default: {DEFAULT_LOG_LEVEL})",
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
@click.option("--config", is_flag=True, help="Run the interactive configuration wizard and save settings to ~/.gac.env")
@click.option("--dry-run", is_flag=True, help="Dry run the commit workflow")
def cli(
    add_all: bool = False,
    config: bool = False,
    log_level: str = DEFAULT_LOG_LEVEL,
    no_format: bool = False,
    one_liner: bool = False,
    push: bool = False,
    show_prompt: bool = False,
    quiet: bool = False,
    yes: bool = False,
    hint: str = "",
    model: str = None,
    version: bool = False,
    template: str = None,
    dry_run: bool = False,
):
    """Git Auto Commit - Generate commit messages with AI."""
    if version:
        print(f"Git Auto Commit (GAC) version: {__about__.__version__}")
        sys.exit(0)

    if config:
        from gac.config import run_config_wizard

        result = run_config_wizard()
        if result:
            print_message("Configuration saved successfully!", "notification")
        return

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
        handle_error(GitError("Not in a git repository"), exit_program=True)
        return  # This line won't be reached due to exit_program=True, but it's good practice

    if model is None:
        model = os.getenv("GAC_MODEL")
        if model is None:
            handle_error(
                AIError.model_error(
                    "No model specified. Please set the GAC_MODEL environment variable or use --model."
                ),
                exit_program=True,
            )
            return  # This line won't be reached due to exit_program=True
    if should_format_files is None:
        format_files_env = os.getenv("GAC_FORMAT_FILES")
        should_format_files = format_files_env.lower() == "true" if format_files_env else True

    backup_model = os.getenv("GAC_BACKUP_MODEL", None)

    if stage_all and (not dry_run):
        print_message("Staging all changes", "info")
        run_git_command(["add", "--all"])

    if not get_staged_files(existing_only=False):
        handle_error(
            GitError("No staged changes found. Stage your changes with git add first or use --add-all"),
            exit_program=True,
        )
        return  # This line won't be reached due to exit_program=True

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
            temperature=TEMPERATURE,
            max_tokens=MAX_OUTPUT_TOKENS,
            max_retries=MAX_RETRIES,
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
                temperature=TEMPERATURE,
                max_tokens=MAX_OUTPUT_TOKENS,
                max_retries=MAX_RETRIES,
                quiet=quiet,
            )
        except AIError as e:
            print_message(str(e), level="error")
            print_message("Backup model unsuccessful. Exiting...", level="error")
            sys.exit(1)

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

    if push:
        try:
            from gac.git import push_changes

            if not push_changes():
                handle_error(
                    GitError("Failed to push changes. Check your remote configuration."),
                    exit_program=True,
                )
                return  # This line won't be reached due to exit_program=True
        except Exception as e:
            handle_error(
                GitError(f"Error pushing changes: {e}"),
                exit_program=True,
            )
            return  # This line won't be reached due to exit_program=True

    if not quiet:
        print_message("Successfully committed changes with message:", "notification")
        print(commit_message)
        if push:
            print_message("Changes pushed to remote.", "notification")
    sys.exit(0)


if __name__ == "__main__":
    cli()
