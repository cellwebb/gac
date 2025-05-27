#!/usr/bin/env python3
"""Business logic for GAC: orchestrates the commit workflow, including git state, formatting,
prompt building, AI generation, and commit/push operations. This module contains no CLI wiring.
"""

import logging
import sys
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel

from gac.ai import generate_commit_message
from gac.config import load_config
from gac.errors import AIError, GitError, handle_error
from gac.git import get_staged_files, push_changes, run_git_command
from gac.prompt import build_prompt, clean_commit_message

logger = logging.getLogger(__name__)

config = load_config()


def main(
    stage_all: bool = False,
    model: Optional[str] = None,
    hint: str = "",
    one_liner: bool = False,
    show_prompt: bool = False,
    scope: Optional[str] = None,
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

    status = run_git_command(["status"])
    diff = run_git_command(["diff", "--staged"])

    prompt = build_prompt(
        status=status,
        diff=diff,
        one_liner=one_liner,
        hint=hint,
        model=model or config["model"],
        scope=scope,
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
            model=model,
            prompt=prompt,
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
        console.print(f"[red]Failed to generate commit message: {str(e)}[/red]")
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
    main()
