#!/usr/bin/env python3
"""Business logic for gac: orchestrates the commit workflow, including git state, formatting,
prompt building, AI generation, and commit/push operations. This module contains no CLI wiring.
"""

import logging
import sys

import click
from rich.console import Console
from rich.panel import Panel

from gac.ai import generate_commit_message
from gac.ai_utils import count_tokens
from gac.config import load_config
from gac.constants import EnvDefaults, Utility
from gac.errors import AIError, GitError, handle_error
from gac.git import (
    get_staged_files,
    push_changes,
    run_git_command,
    run_lefthook_hooks,
    run_pre_commit_hooks,
)
from gac.preprocess import preprocess_diff
from gac.prompt import build_prompt, clean_commit_message
from gac.security import get_affected_files, scan_staged_diff
from gac.utils import edit_commit_message_inplace

logger = logging.getLogger(__name__)

config = load_config()
console = Console()  # Initialize console globally to prevent undefined access


def main(
    stage_all: bool = False,
    model: str | None = None,
    hint: str = "",
    one_liner: bool = False,
    show_prompt: bool = False,
    infer_scope: bool = False,
    require_confirmation: bool = True,
    push: bool = False,
    quiet: bool = False,
    dry_run: bool = False,
    verbose: bool = False,
    no_verify: bool = False,
    skip_secret_scan: bool = False,
    language: str | None = None,
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
        model_from_config = config["model"]
        if model_from_config is None:
            handle_error(
                AIError.model_error(
                    "gac init hasn't been run yet. Please run 'gac init' to set up your configuration, then try again."
                ),
                exit_program=True,
            )
        model = str(model_from_config)

    temperature_val = config["temperature"]
    assert temperature_val is not None
    temperature = float(temperature_val)

    max_tokens_val = config["max_output_tokens"]
    assert max_tokens_val is not None
    max_output_tokens = int(max_tokens_val)

    max_retries_val = config["max_retries"]
    assert max_retries_val is not None
    max_retries = int(max_retries_val)

    if stage_all and (not dry_run):
        logger.info("Staging all changes")
        run_git_command(["add", "--all"])

    # Check for staged files
    staged_files = get_staged_files(existing_only=False)
    if not staged_files:
        console.print(
            "[yellow]No staged changes found. Stage your changes with git add first or use --add-all.[/yellow]"
        )
        sys.exit(0)

    # Run pre-commit and lefthook hooks before doing expensive operations
    if not no_verify and not dry_run:
        # Run lefthook hooks
        if not run_lefthook_hooks():
            console.print("[red]Lefthook hooks failed. Please fix the issues and try again.[/red]")
            console.print("[yellow]You can use --no-verify to skip pre-commit and lefthook hooks.[/yellow]")
            sys.exit(1)

        # Run pre-commit hooks
        if not run_pre_commit_hooks():
            console.print("[red]Pre-commit hooks failed. Please fix the issues and try again.[/red]")
            console.print("[yellow]You can use --no-verify to skip pre-commit and lefthook hooks.[/yellow]")
            sys.exit(1)

    status = run_git_command(["status"])
    diff = run_git_command(["diff", "--staged"])
    diff_stat = " " + run_git_command(["diff", "--stat", "--cached"])

    # Security scan for secrets
    if not skip_secret_scan:
        logger.info("Scanning staged changes for potential secrets...")
        secrets = scan_staged_diff(diff)
        if secrets:
            if not quiet:
                console.print("\n[bold red]⚠️  SECURITY WARNING: Potential secrets detected![/bold red]")
                console.print("[red]The following sensitive information was found in your staged changes:[/red]\n")

            for secret in secrets:
                location = f"{secret.file_path}:{secret.line_number}" if secret.line_number else secret.file_path
                if not quiet:
                    console.print(f"  • [yellow]{secret.secret_type}[/yellow] in [cyan]{location}[/cyan]")
                    console.print(f"    Match: [dim]{secret.matched_text}[/dim]\n")

            if not quiet:
                console.print("\n[bold]Options:[/bold]")
                console.print("  \\[a] Abort commit (recommended)")
                console.print("  \\[c] [yellow]Continue anyway[/yellow] (not recommended)")
                console.print("  \\[r] Remove affected file(s) and continue")

            try:
                choice = (
                    click.prompt(
                        "\nChoose an option",
                        type=click.Choice(["a", "c", "r"], case_sensitive=False),
                        default="a",
                        show_choices=True,
                        show_default=True,
                    )
                    .strip()
                    .lower()
                )
            except (EOFError, KeyboardInterrupt):
                console.print("\n[red]Aborted by user.[/red]")
                sys.exit(0)

            if choice == "a":
                console.print("[yellow]Commit aborted.[/yellow]")
                sys.exit(0)
            elif choice == "c":
                console.print("[bold yellow]⚠️  Continuing with potential secrets in commit...[/bold yellow]")
                logger.warning("User chose to continue despite detected secrets")
            elif choice == "r":
                affected_files = get_affected_files(secrets)
                for file_path in affected_files:
                    try:
                        run_git_command(["reset", "HEAD", file_path])
                        console.print(f"[green]Unstaged: {file_path}[/green]")
                    except GitError as e:
                        console.print(f"[red]Failed to unstage {file_path}: {e}[/red]")

                # Check if there are still staged files
                remaining_staged = get_staged_files(existing_only=False)
                if not remaining_staged:
                    console.print("[yellow]No files remain staged. Commit aborted.[/yellow]")
                    sys.exit(0)

                console.print(f"[green]Continuing with {len(remaining_staged)} staged file(s)...[/green]")
                # Refresh all git state variables after removing files
                status = run_git_command(["status"])
                diff = run_git_command(["diff", "--staged"])
                diff_stat = " " + run_git_command(["diff", "--stat", "--cached"])
        else:
            logger.info("No secrets detected in staged changes")

    # Preprocess the diff before passing to build_prompt
    logger.debug(f"Preprocessing diff ({len(diff)} characters)")
    assert model is not None
    processed_diff = preprocess_diff(diff, token_limit=Utility.DEFAULT_DIFF_TOKEN_LIMIT, model=model)
    logger.debug(f"Processed diff ({len(processed_diff)} characters)")

    system_template_path_value = config.get("system_prompt_path")
    system_template_path: str | None = (
        system_template_path_value if isinstance(system_template_path_value, str) else None
    )

    # Use language parameter if provided, otherwise fall back to config
    if language is None:
        language_value = config.get("language")
        language = language_value if isinstance(language_value, str) else None

    translate_prefixes_value = config.get("translate_prefixes")
    translate_prefixes: bool = bool(translate_prefixes_value) if isinstance(translate_prefixes_value, bool) else False

    system_prompt, user_prompt = build_prompt(
        status=status,
        processed_diff=processed_diff,
        diff_stat=diff_stat,
        one_liner=one_liner,
        hint=hint,
        infer_scope=infer_scope,
        verbose=verbose,
        system_template_path=system_template_path,
        language=language,
        translate_prefixes=translate_prefixes,
    )

    if show_prompt:
        # Show both system and user prompts
        full_prompt = f"SYSTEM PROMPT:\n{system_prompt}\n\nUSER PROMPT:\n{user_prompt}"
        console.print(
            Panel(
                full_prompt,
                title="Prompt for LLM",
                border_style="bright_blue",
            )
        )

    conversation_messages: list[dict[str, str]] = []
    if system_prompt:
        conversation_messages.append({"role": "system", "content": system_prompt})
    conversation_messages.append({"role": "user", "content": user_prompt})

    try:
        first_iteration = True

        while True:
            prompt_tokens = count_tokens(conversation_messages, model)

            if first_iteration:
                warning_limit_val = config.get("warning_limit_tokens", EnvDefaults.WARNING_LIMIT_TOKENS)
                assert warning_limit_val is not None
                warning_limit = int(warning_limit_val)
                if warning_limit and prompt_tokens > warning_limit:
                    console.print(
                        f"[yellow]⚠️  WARNING: Prompt contains {prompt_tokens} tokens, which exceeds the warning limit of "
                        f"{warning_limit} tokens.[/yellow]"
                    )
                    if require_confirmation:
                        proceed = click.confirm("Do you want to continue anyway?", default=True)
                        if not proceed:
                            console.print("[yellow]Aborted due to token limit.[/yellow]")
                            sys.exit(0)

            first_iteration = False

            raw_commit_message = generate_commit_message(
                model=model,
                prompt=conversation_messages,
                temperature=temperature,
                max_tokens=max_output_tokens,
                max_retries=max_retries,
                quiet=quiet,
            )
            # Clean the commit message (no automatic prefix enforcement)
            commit_message = clean_commit_message(raw_commit_message)

            logger.info("Generated commit message:")
            logger.info(commit_message)

            conversation_messages.append({"role": "assistant", "content": commit_message})

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
                while True:
                    response = click.prompt(
                        "Proceed with commit above? [y/n/r/e/<feedback>]",
                        type=str,
                        show_default=False,
                    ).strip()
                    response_lower = response.lower()

                    if response_lower in ["y", "yes"]:
                        break
                    if response_lower in ["n", "no"]:
                        console.print("[yellow]Prompt not accepted. Exiting...[/yellow]")
                        sys.exit(0)
                    if response == "":
                        continue
                    if response_lower in ["e", "edit"]:
                        edited_message = edit_commit_message_inplace(commit_message)
                        if edited_message:
                            commit_message = edited_message
                            conversation_messages[-1] = {"role": "assistant", "content": commit_message}
                            logger.info("Commit message edited by user")
                            console.print("\n[bold green]Edited commit message:[/bold green]")
                            console.print(Panel(commit_message, title="Commit Message", border_style="cyan"))
                        else:
                            console.print("[yellow]Using previous message.[/yellow]")
                            console.print(Panel(commit_message, title="Commit Message", border_style="cyan"))
                        continue
                    if response_lower in ["r", "reroll"]:
                        feedback_message = (
                            "Please provide an alternative commit message using the same repository context."
                        )
                        console.print("[cyan]Regenerating commit message...[/cyan]")
                        conversation_messages.append({"role": "user", "content": feedback_message})
                        console.print()
                        break

                    feedback_message = f"Please revise the commit message based on this feedback: {response}"
                    console.print(f"[cyan]Regenerating commit message with feedback: {response}[/cyan]")
                    conversation_messages.append({"role": "user", "content": feedback_message})
                    console.print()
                    break

                if response_lower in ["y", "yes"]:
                    break
            else:
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
