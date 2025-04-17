#!/usr/bin/env python3
"""Main entry point for GAC."""

import logging
import sys
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel

from gac import __version__
from gac.ai import generate_with_fallback
from gac.config import load_config
from gac.constants import Logging
from gac.errors import AIError, GitError, handle_error
from gac.format import format_files
from gac.git import get_staged_files, push_changes, run_git_command
from gac.prompt import build_prompt, clean_commit_message
from gac.utils import setup_logging

logger = logging.getLogger(__name__)

config = load_config()


@click.command()
@click.option("--add-all", "-a", is_flag=True, help="Stage all changes before committing")
@click.option(
    "--log-level",
    default=config["log_level"],
    type=click.Choice(Logging.LEVELS, case_sensitive=False),
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
@click.option("--verbose", "-v", is_flag=True, help="Increase output verbosity to INFO")
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
    verbose: bool = False,
):
    """Git Auto Commit - Generate commit messages with AI."""
    if version:
        logger.info(f"Git Auto Commit (GAC) version: {__version__}")
        sys.exit(0)

    effective_log_level = log_level
    if verbose and log_level not in ("DEBUG", "INFO"):
        effective_log_level = "INFO"
    if quiet:
        effective_log_level = "ERROR"

    setup_logging(effective_log_level)
    logger.info("Starting GAC")

    try:
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
    except Exception as e:
        handle_error(e, exit_program=True)


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
    try:
        git_dir = run_git_command(["rev-parse", "--show-toplevel"])
        if not git_dir:
            raise GitError("Not in a git repository")
    except Exception as e:
        logger.error(f"Error checking git repository: {e}")
        handle_error(GitError("Not in a git repository"), exit_program=True)

    if model is None:
        model = config["model"]
        if model is None:
            handle_error(
                AIError.model_error(
                    "No model specified. Please set the GAC_MODEL environment variable or use --model."
                ),
                exit_program=True,
            )
    if should_format_files is None:
        should_format_files = config["format_files"]

    backup_model = config["backup_model"]

    temperature = config["temperature"]
    max_output_tokens = config["max_output_tokens"]
    max_retries = config["max_retries"]

    if stage_all and (not dry_run):
        logger.info("Staging all changes")
        run_git_command(["add", "--all"])

    # Check for staged and unstaged files
    staged_files = get_staged_files(existing_only=False)
    unstaged_files = get_staged_files(existing_only=True)
    if not staged_files and not unstaged_files:
        console = Console()
        console.print("[yellow]No changes (staged or unstaged) found. Nothing to commit.[/yellow]")
        sys.exit(0)
    elif not staged_files:
        console = Console()
        console.print(
            "[yellow]No staged changes found. Stage your changes with git add first or use --add-all.[/yellow]"
        )
        sys.exit(0)

    if not get_staged_files(existing_only=False):
        handle_error(
            GitError("No staged changes found. Stage your changes with git add first or use --add-all"),
            exit_program=True,
        )

    if should_format_files:
        # TODO: Add logic for files that have both staged and unstaged changes
        files_to_format = get_staged_files(existing_only=True)
        formatted_files = format_files(files_to_format, dry_run=dry_run)
        if formatted_files and not dry_run:
            run_git_command(["add"] + formatted_files)

    status = run_git_command(["status"])
    diff = run_git_command(["diff", "--staged"])

    prompt = build_prompt(status=status, diff=diff, one_liner=one_liner, hint=hint, model=model or config["model"])

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
        commit_message = generate_with_fallback(
            primary_model=model,
            prompt=prompt,
            backup_model=backup_model,
            temperature=temperature,
            max_tokens=max_output_tokens,
            max_retries=max_retries,
            quiet=quiet,
        )

        logger.info("Generated commit message:")
        logger.info(commit_message)

        console = Console()
        console.print("[bold green]Generated commit message:[/bold green]")
        console.print(Panel(commit_message, title="Commit Message", border_style="cyan"))

        if require_confirmation:
            confirmed = click.confirm("Proceed with commit above?", default=True)
            if not confirmed:
                console.print("[yellow]Prompt not accepted. Exiting...[/yellow]")
                sys.exit(0)

        if dry_run:
            console.print("[yellow]Dry run: Commit message generated but not applied[/yellow]")
            console.print("Would commit with message:")
            console.print(Panel(commit_message, title="Commit Message", border_style="cyan"))
            staged_files = get_staged_files(existing_only=False)
            console.print(f"Would commit {len(staged_files)} files")
            staged_files = get_staged_files(existing_only=False)
            logger.info(f"Would commit {len(staged_files)} files")
        else:
            run_git_command(["commit", "-m", commit_message])
            logger.info("Commit created successfully")
            console.print("[green]Commit created successfully[/green]")
    except AIError as e:
        logger.error(str(e))
        console.print("[red]All available models failed. Exiting...[/red]")
        sys.exit(1)

    commit_message = clean_commit_message(commit_message)

    if push:
        try:
            if dry_run:
                staged_files = get_staged_files(existing_only=False)

                logger.info("Dry run: Would push changes")
                logger.info("Would push with message:")
                logger.info(commit_message)
                logger.info(f"Would push {len(staged_files)} files")

                console.print("[yellow]Dry run: Would push changes[/yellow]")
                console.print("Would push with message:")
                console.print(Panel(commit_message, title="Commit Message", border_style="cyan"))
                console.print(f"Would push {len(staged_files)} files")
                sys.exit(0)

            if push_changes():
                logger.info("Changes pushed successfully")
                console.print("[green]Changes pushed successfully[/green]")
            else:
                handle_error(
                    GitError("Failed to push changes. Check your remote configuration."),
                    exit_program=True,
                )
        except Exception as e:
            handle_error(
                GitError(f"Error pushing changes: {e}"),
                exit_program=True,
            )

    if not quiet:
        logger.info("Successfully committed changes with message:")
        logger.info(commit_message)
        if push:
            logger.info("Changes pushed to remote.")
    sys.exit(0)


if __name__ == "__main__":
    cli()
