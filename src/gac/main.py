#!/usr/bin/env python3
"""Business logic for gac: orchestrates the commit workflow, including git state, formatting,
prompt building, AI generation, and commit/push operations. This module contains no CLI wiring.
"""

import logging
import sys
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel

from gac.ai import count_tokens, generate_commit_message
from gac.config import load_config
from gac.constants import EnvDefaults, Utility
from gac.errors import AIError, GitError, handle_error
from gac.git import get_staged_files, get_unstaged_files, push_changes, run_git_command, run_pre_commit_hooks
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
) -> None:
    """Main application logic for gac."""
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

    # Check for any changes first
    staged_files = get_staged_files(existing_only=False)
    unstaged_files = get_unstaged_files(include_untracked=True)

    if not staged_files and not unstaged_files:
        console = Console()
        console.print("[yellow]No changes (staged or unstaged) found. Nothing to commit.[/yellow]")
        sys.exit(0)

    # Stage all changes if requested
    if stage_all:
        if unstaged_files:
            if not dry_run:
                logger.info("Staging all changes")
                run_git_command(["add", "--all"])
                # Update staged files after staging
                staged_files = get_staged_files(existing_only=False)
            else:
                # For dry run, simulate staging by combining staged and unstaged
                logger.info("Dry run: Would stage all changes")
                staged_files = staged_files + unstaged_files

    # Check if we have staged files
    if not staged_files:
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

    status = run_git_command(["status"])
    diff = run_git_command(["diff", "--staged"])
    diff_stat = " " + run_git_command(["diff", "--stat", "--cached"])

    # Preprocess the diff before passing to build_prompt
    logger.debug(f"Preprocessing diff ({len(diff)} characters)")
    model_id = model or config["model"]
    processed_diff = preprocess_diff(diff, token_limit=Utility.DEFAULT_DIFF_TOKEN_LIMIT, model=model_id)
    logger.debug(f"Processed diff ({len(processed_diff)} characters)")

    prompt = build_prompt(
        status=status,
        processed_diff=processed_diff,
        diff_stat=diff_stat,
        one_liner=one_liner,
        hint=hint,
        scope=scope,
        repo_path=git_dir.strip(),
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
        prompt_tokens = count_tokens(prompt, model)

        warning_limit = config.get("warning_limit_tokens", EnvDefaults.WARNING_LIMIT_TOKENS)
        if warning_limit and prompt_tokens > warning_limit:
            console = Console()
            console.print(
                f"[yellow]⚠️  Warning: Prompt contains {prompt_tokens} tokens, which exceeds the warning limit of "
                f"{warning_limit} tokens.[/yellow]"
            )
            if require_confirmation:
                proceed = click.confirm("Do you want to continue anyway?", default=True)
                if not proceed:
                    console.print("[yellow]Aborted due to token limit.[/yellow]")
                    sys.exit(0)

        commit_message = generate_commit_message(
            model=model,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_output_tokens,
            max_retries=max_retries,
            quiet=quiet,
        )
        commit_message = clean_commit_message(commit_message)

        logger.info("Generated commit message:")
        logger.info(commit_message)

        console = Console()

        # Reroll loop
        while True:
            console.print("[bold green]Generated commit message:[/bold green]")
            console.print(Panel(commit_message, title="Commit Message", border_style="cyan"))

            if not quiet:
                completion_tokens = count_tokens(commit_message, model)
                total_tokens = prompt_tokens + completion_tokens
                console.print(
                    f"[dim]Token usage: {prompt_tokens} prompt + {completion_tokens} completion = {total_tokens} "
                    "total[/dim]"
                )

            if require_confirmation:
                # Custom prompt that accepts y/n/r
                while True:
                    response = (
                        click.prompt("Proceed with commit above? [y/n/r]", type=str, show_default=False).lower().strip()
                    )

                    if response in ["y", "yes"]:
                        break  # Exit both loops and proceed with commit
                    elif response in ["n", "no"]:
                        console.print("[yellow]Prompt not accepted. Exiting...[/yellow]")
                        sys.exit(0)
                    elif response in ["r", "reroll"]:
                        console.print("[cyan]Regenerating commit message...[/cyan]\n")
                        # Generate new message
                        commit_message = generate_commit_message(
                            model=model,
                            prompt=prompt,
                            temperature=temperature,
                            max_tokens=max_output_tokens,
                            max_retries=max_retries,
                            quiet=quiet,
                        )
                        commit_message = clean_commit_message(commit_message)
                        break  # Exit inner loop, continue outer loop
                    else:
                        console.print("[red]Invalid response. Please enter y (yes), n (no), or r (reroll).[/red]")

                # If we got here with 'y', break the outer loop
                if response in ["y", "yes"]:
                    break
            else:
                # No confirmation required, exit loop
                break

        if dry_run:
            console.print("[yellow]Dry run: Commit message generated but not applied[/yellow]")
            console.print("Would commit with message:")
            console.print(Panel(commit_message, title="Commit Message", border_style="cyan"))
            staged_files = get_staged_files(existing_only=False)
            console.print(f"Would commit {len(staged_files)} files")
            logger.info(f"Would commit {len(staged_files)} files")
        else:
            commit_args = ["commit", "-m", commit_message]
            if no_verify:
                commit_args.append("--no-verify")
            run_git_command(commit_args)
            logger.info("Commit created successfully")
            console.print("[green]Commit created successfully[/green]")
    except AIError as e:
        logger.error(str(e))
        console.print(f"[red]Failed to generate commit message: {str(e)}[/red]")
        sys.exit(1)

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
