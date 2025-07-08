"""Optimized main module using batched/parallel git operations."""

import logging
import sys
from typing import Optional

from rich.console import Console
from rich.panel import Panel

from gac.ai import generate_commit_message
from gac.config import load_config
from gac.constants import Prompts, Utility
from gac.errors import AIError, GitError, handle_error
from gac.git import (
    commit_changes,
    push_changes,
    run_pre_commit_hooks,
    stage_all_changes,
)
from gac.git_optimized import get_all_git_data  # Use optimized version
from gac.preprocess import preprocess_diff
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
    no_verify: bool = False,
    no_readme: bool = False,
) -> None:
    """Main application logic for gac - now with optimized git operations."""

    # Get all git data at once (parallel or batched)
    try:
        git_data = get_all_git_data(strategy="parallel")  # Can switch to "batched" or "ultra_batched"
    except GitError as e:
        handle_error(e, exit_program=True)
        return

    if model is None:
        model = config["model"]
        if model is None:
            handle_error(
                AIError.model_error(
                    "No model specified. Please set the GAC_MODEL environment variable or use --model."
                ),
                exit_program=True,
            )

    # Stage all changes if requested
    if stage_all:
        console = Console()
        if quiet:
            logger.info("Staging all changes")
        else:
            console.print("[blue]Staging all changes...[/blue]")
        stage_all_changes()
        # Re-fetch git data after staging
        git_data = get_all_git_data(strategy="parallel")

    # Check for staged files
    if not git_data.staged_files:
        if quiet:
            logger.error("No staged changes found.")
            sys.exit(1)
        console = Console()
        console.print(
            "[yellow]No staged changes found. Stage your changes with git add first or use --add-all.[/yellow]"
        )
        sys.exit(0)

    # Run pre-commit hooks before doing expensive operations
    if not no_verify and not dry_run:
        if not run_pre_commit_hooks():
            console = Console()
            console.print("[red]Pre-commit hooks failed. Please fix the issues and try again.[/red]")
            console.print("[yellow]You can use --no-verify to skip pre-commit hooks.[/yellow]")
            sys.exit(1)

    # Preprocess the diff before passing to build_prompt
    logger.debug(f"Preprocessing diff ({len(git_data.staged_diff)} characters)")
    model_id = model or config["model"]
    processed_diff = preprocess_diff(git_data.staged_diff, token_limit=Utility.DEFAULT_DIFF_TOKEN_LIMIT, model=model_id)
    logger.debug(f"Processed diff ({len(processed_diff)} characters)")

    # Build prompt using the git data
    prompt = build_prompt(
        status=git_data.status,
        processed_diff=processed_diff,
        diff_stat=git_data.diff_stat,
        one_liner=one_liner,
        hint=hint,
        scope=scope,
        repo_path=git_data.repo_root if not no_readme else None,
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
        return

    # Generate initial commit message
    commit_message = _generate_and_confirm_message(
        prompt=prompt,
        model=model,
        require_confirmation=require_confirmation,
        quiet=quiet,
    )

    if commit_message is None:
        # User cancelled
        return

    # Commit changes
    if not dry_run:
        logger.info(f"Creating commit with message: {commit_message}")
        commit_changes(commit_message, no_verify=no_verify)
    else:
        logger.info(f"[DRY RUN] Would create commit with message: {commit_message}")

    if not quiet:
        console = Console()
        console.print("[green]Commit created successfully[/green]")

    # Push changes if requested
    if push and not dry_run:
        if quiet:
            logger.info("Pushing changes")
        else:
            console.print("[blue]Pushing changes...[/blue]")

        if git_data.has_remote:
            if push_changes():
                if not quiet:
                    console.print("[green]Changes pushed successfully[/green]")
            else:
                if quiet:
                    logger.error("Failed to push changes")
                else:
                    console.print("[red]Failed to push changes[/red]")
        else:
            if quiet:
                logger.error("No remote repository configured")
            else:
                console.print("[yellow]No remote repository configured[/yellow]")
    elif push and dry_run:
        logger.info("[DRY RUN] Would push changes")


def _generate_and_confirm_message(
    prompt: str,
    model: str,
    require_confirmation: bool,
    quiet: bool,
) -> Optional[str]:
    """Generate commit message and get user confirmation if needed."""
    while True:
        # Generate commit message
        try:
            raw_message = generate_commit_message(prompt, model)
            commit_message = clean_commit_message(raw_message)
        except Exception as e:
            handle_error(e, exit_program=True)
            return None

        # Display generated message
        if not quiet:
            console = Console()
            console.print("Generated commit message:")
            console.print(
                Panel(
                    commit_message,
                    title="Commit Message",
                    border_style="green",
                )
            )

        # Auto-confirm if requested
        if not require_confirmation:
            logger.debug("Auto-confirming commit message (no confirmation required)")
            return commit_message

        # Get user confirmation
        console = Console()
        user_input = console.input(f"{Prompts.CONFIRM_COMMIT} ").strip().lower()

        if user_input in ["y", "yes", ""]:
            return commit_message
        elif user_input in ["n", "no"]:
            console.print("[yellow]Commit cancelled.[/yellow]")
            return None
        elif user_input in ["r", "reroll"]:
            console.print("[blue]Regenerating commit message...[/blue]")
            continue
        else:
            console.print(f"[red]Invalid input.[/red] {Prompts.CONFIRM_COMMIT} ")
