#!/usr/bin/env python3
"""Business logic for gac: orchestrates the commit workflow, including git state, formatting,
prompt building, AI generation, and commit/push operations. This module contains no CLI wiring.
"""

import logging
import sys

import click
from rich.console import Console
from rich.panel import Panel

from gac.ai import count_tokens, generate_commit_message
from gac.config import load_config
from gac.constants import EnvDefaults, Utility
from gac.errors import AIError, GitError, handle_error
from gac.git import (
    get_staged_files,
    push_changes,
    run_git_command,
    run_pre_commit_hooks,
)
from gac.preprocess import preprocess_diff
from gac.prompt import build_prompt, clean_commit_message

logger = logging.getLogger(__name__)

config = load_config()


def main(
    stage_all: bool = False,
    model: str | None = None,
    hint: str = "",
    one_liner: bool = False,
    show_prompt: bool = False,
    scope: str | None = None,
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

    if stage_all and (not dry_run):
        logger.info("Staging all changes")
        run_git_command(["add", "--all"])

    # Check for staged files
    staged_files = get_staged_files(existing_only=False)
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

    system_prompt, user_prompt = build_prompt(
        status=status,
        processed_diff=processed_diff,
        diff_stat=diff_stat,
        one_liner=one_liner,
        hint=hint,
        scope=scope,
    )

    if show_prompt:
        console = Console()
        # Show both system and user prompts
        full_prompt = f"SYSTEM PROMPT:\n{system_prompt}\n\nUSER PROMPT:\n{user_prompt}"
        console.print(
            Panel(
                full_prompt,
                title="Prompt for LLM",
                border_style="bright_blue",
            )
        )

    try:
        # Count tokens for both prompts
        prompt_tokens = count_tokens(system_prompt, model) + count_tokens(user_prompt, model)

        warning_limit = config.get("warning_limit_tokens", EnvDefaults.WARNING_LIMIT_TOKENS)
        if warning_limit and prompt_tokens > warning_limit:
            console = Console()
            console.print(
                f"[yellow]⚠️  WARNING: Prompt contains {prompt_tokens} tokens, which exceeds the warning limit of "
                f"{warning_limit} tokens.[/yellow]"
            )
            if require_confirmation:
                proceed = click.confirm("Do you want to continue anyway?", default=True)
                if not proceed:
                    console.print("[yellow]Aborted due to token limit.[/yellow]")
                    sys.exit(0)

        commit_message = generate_commit_message(
            model=model,
            prompt=(system_prompt, user_prompt),
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
                # Custom prompt that accepts y/n/r or "r <feedback (optional)>"
                while True:
                    response = click.prompt(
                        "Proceed with commit above? [y/n/r <feedback>]", type=str, show_default=False
                    ).strip()

                    if response.lower() in ["y", "yes"]:
                        break  # Exit both loops and proceed with commit
                    elif response.lower() in ["n", "no"]:
                        console.print("[yellow]Prompt not accepted. Exiting...[/yellow]")
                        sys.exit(0)
                    elif response.lower() == "r" or response.lower().startswith("r ") or response.lower() == "reroll":
                        # Parse the reroll command for optional feedback
                        if response.lower() == "r" or response.lower() == "reroll":
                            # Simple reroll without feedback
                            reroll_feedback = ""
                            console.print("[cyan]Regenerating commit message...[/cyan]")
                        else:
                            # Extract feedback from "r <feedback>"
                            reroll_feedback = response[2:].strip()  # Remove "r " prefix
                            console.print(f"[cyan]Regenerating commit message with feedback: {reroll_feedback}[/cyan]")

                        # Combine hints if reroll feedback provided
                        combined_hint = hint
                        if reroll_feedback:
                            # Create conversational prompt with previous attempt and feedback
                            conversational_hint = f"Previous attempt: '{commit_message}'. User feedback: {reroll_feedback}. Please revise accordingly."

                            if hint:
                                combined_hint = f"{hint}. {conversational_hint}"
                            else:
                                combined_hint = conversational_hint

                            # Regenerate prompt with conversational feedback
                            reroll_system_prompt, reroll_user_prompt = build_prompt(
                                status=status,
                                processed_diff=processed_diff,
                                diff_stat=diff_stat,
                                one_liner=one_liner,
                                hint=combined_hint,
                                scope=scope,
                            )
                        else:
                            # No hint given, just reroll with same prompts
                            reroll_system_prompt, reroll_user_prompt = system_prompt, user_prompt

                        console.print()  # Add blank line for readability

                        # Generate new message
                        commit_message = generate_commit_message(
                            model=model,
                            prompt=(reroll_system_prompt, reroll_user_prompt),
                            temperature=temperature,
                            max_tokens=max_output_tokens,
                            max_retries=max_retries,
                            quiet=quiet,
                        )
                        commit_message = clean_commit_message(commit_message)
                        break  # Exit inner loop, continue outer loop
                    else:
                        console.print(
                            "[red]Invalid response. Please enter y (yes), n (no), r (reroll), or r <feedback>.[/red]"
                        )

                # If we got here with 'y', break the outer loop
                if response.lower() in ["y", "yes"]:
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
        console = Console()
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
                console.print(
                    "[red]Failed to push changes. Check your remote configuration and network connection.[/red]"
                )
                sys.exit(1)
        except Exception as e:
            console.print(f"[red]Error pushing changes: {e}[/red]")
            sys.exit(1)

    if not quiet:
        logger.info("Successfully committed changes with message:")
        logger.info(commit_message)
        if push:
            logger.info("Changes pushed to remote.")
    sys.exit(0)


if __name__ == "__main__":
    main()
