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
    get_staged_status,
    push_changes,
    run_git_command,
    run_lefthook_hooks,
    run_pre_commit_hooks,
)
from gac.preprocess import preprocess_diff
from gac.prompt import build_prompt, clean_commit_message
from gac.security import get_affected_files, scan_staged_diff
from gac.workflow_utils import (
    check_token_warning,
    display_commit_message,
    execute_commit,
    handle_confirmation_loop,
    restore_staging,
)

logger = logging.getLogger(__name__)

config = load_config()
console = Console()  # Initialize console globally to prevent undefined access


def _validate_grouped_files_or_feedback(staged: set[str], grouped_result: dict) -> tuple[bool, str, str]:
    from collections import Counter

    commits = grouped_result.get("commits", []) if isinstance(grouped_result, dict) else []
    all_files: list[str] = []
    for commit in commits:
        files = commit.get("files", []) if isinstance(commit, dict) else []
        all_files.extend([str(p) for p in files])

    counts = Counter(all_files)
    union_set = set(all_files)

    duplicates = sorted([f for f, c in counts.items() if c > 1])
    missing = sorted(staged - union_set)
    unexpected = sorted(union_set - staged)

    if not duplicates and not missing and not unexpected:
        return True, "", ""

    problems: list[str] = []
    if missing:
        problems.append(f"Missing: {', '.join(missing)}")
    if unexpected:
        problems.append(f"Not staged: {', '.join(unexpected)}")
    if duplicates:
        problems.append(f"Duplicates: {', '.join(duplicates)}")

    feedback = f"{'; '.join(problems)}. Required files: {', '.join(sorted(staged))}. Respond with ONLY valid JSON."
    return False, feedback, "; ".join(problems)


def _parse_model_identifier(model: str) -> tuple[str, str]:
    """Validate and split model identifier into provider and model name."""
    normalized = model.strip()
    if ":" not in normalized:
        message = (
            f"Invalid model format: '{model}'. Expected 'provider:model', e.g. 'openai:gpt-4o-mini'. "
            "Use 'gac config set model <provider:model>' to update your configuration."
        )
        logger.error(message)
        console.print(f"[red]{message}[/red]")
        sys.exit(1)

    provider, model_name = normalized.split(":", 1)
    if not provider or not model_name:
        message = (
            f"Invalid model format: '{model}'. Both provider and model name are required "
            "(example: 'anthropic:claude-3-5-haiku-latest')."
        )
        logger.error(message)
        console.print(f"[red]{message}[/red]")
        sys.exit(1)

    return provider, model_name


def _handle_validation_retry(
    attempts: int,
    content_retry_budget: int,
    raw_response: str,
    feedback_message: str,
    error_message: str,
    conversation_messages: list[dict[str, str]],
    quiet: bool,
    retry_context: str,
) -> bool:
    """Handle validation retry logic. Returns True if should exit, False if should retry."""
    conversation_messages.append({"role": "assistant", "content": raw_response})
    conversation_messages.append({"role": "user", "content": feedback_message})
    if attempts >= content_retry_budget:
        logger.error(error_message)
        console.print(f"\n[red]{error_message}[/red]")
        console.print("\n[yellow]Raw model output:[/yellow]")
        console.print(Panel(raw_response, title="Model Output", border_style="yellow"))
        return True
    if not quiet:
        console.print(f"[yellow]Retry {attempts} of {content_retry_budget - 1}: {retry_context}[/yellow]")
    return False


def execute_grouped_commits_workflow(
    *,
    system_prompt: str,
    user_prompt: str,
    model: str,
    temperature: float,
    max_output_tokens: int,
    max_retries: int,
    require_confirmation: bool,
    quiet: bool,
    no_verify: bool,
    dry_run: bool,
    push: bool,
    show_prompt: bool,
    hook_timeout: int = 120,
) -> None:
    """Execute the grouped commits workflow."""
    import json

    from gac.ai import generate_grouped_commits

    provider, model_name = _parse_model_identifier(model)

    if show_prompt:
        full_prompt = f"SYSTEM PROMPT:\n{system_prompt}\n\nUSER PROMPT:\n{user_prompt}"
        console.print(Panel(full_prompt, title="Prompt for LLM", border_style="bright_blue"))

    conversation_messages: list[dict[str, str]] = []
    if system_prompt:
        conversation_messages.append({"role": "system", "content": system_prompt})
    conversation_messages.append({"role": "user", "content": user_prompt})

    _parse_model_identifier(model)

    first_iteration = True
    content_retry_budget = max(3, int(max_retries))
    attempts = 0

    grouped_result: dict | None = None
    raw_response: str = ""

    while True:
        prompt_tokens = count_tokens(conversation_messages, model)

        if first_iteration:
            warning_limit_val = config.get("warning_limit_tokens", EnvDefaults.WARNING_LIMIT_TOKENS)
            assert warning_limit_val is not None
            warning_limit = int(warning_limit_val)
            if not check_token_warning(prompt_tokens, warning_limit, require_confirmation):
                sys.exit(0)
        first_iteration = False

        raw_response = generate_grouped_commits(
            model=model,
            prompt=conversation_messages,
            temperature=temperature,
            max_tokens=max_output_tokens,
            max_retries=max_retries,
            quiet=quiet,
            skip_success_message=True,
        )

        parsed: dict | None = None
        extract = raw_response
        first_brace = raw_response.find("{")
        last_brace = raw_response.rfind("}")
        if first_brace != -1 and last_brace != -1 and first_brace < last_brace:
            extract = raw_response[first_brace : last_brace + 1]

        try:
            parsed = json.loads(extract)
        except json.JSONDecodeError as e:
            parsed = None
            logger.debug(
                f"JSON parsing failed: {e}. Extract length: {len(extract)}, Response length: {len(raw_response)}"
            )

        if parsed is None:
            attempts += 1
            feedback = "Your response was not valid JSON. Respond with ONLY valid JSON matching the expected schema. Do not include any commentary or code fences."
            error_msg = f"Failed to parse LLM response as JSON after {attempts} retries."
            if _handle_validation_retry(
                attempts,
                content_retry_budget,
                raw_response,
                feedback,
                error_msg,
                conversation_messages,
                quiet,
                "JSON parsing failed, asking model to fix...",
            ):
                sys.exit(1)
            continue

        try:
            if "commits" not in parsed or not isinstance(parsed["commits"], list):
                raise ValueError("Response missing 'commits' array")
            if len(parsed["commits"]) == 0:
                raise ValueError("No commits in response")
            for idx, commit in enumerate(parsed["commits"]):
                if "files" not in commit or not isinstance(commit["files"], list):
                    raise ValueError(f"Commit {idx + 1} missing 'files' array")
                if "message" not in commit or not isinstance(commit["message"], str):
                    raise ValueError(f"Commit {idx + 1} missing 'message' string")
                if len(commit["files"]) == 0:
                    raise ValueError(f"Commit {idx + 1} has empty files list")
                if not commit["message"].strip():
                    raise ValueError(f"Commit {idx + 1} has empty message")
        except (ValueError, TypeError) as e:
            attempts += 1
            feedback = f"Invalid response structure: {e}. Please return ONLY valid JSON following the schema with a non-empty 'commits' array of objects containing 'files' and 'message'."
            error_msg = f"Invalid grouped commits structure after {attempts} retries: {e}"
            if _handle_validation_retry(
                attempts,
                content_retry_budget,
                raw_response,
                feedback,
                error_msg,
                conversation_messages,
                quiet,
                "Structure validation failed, asking model to fix...",
            ):
                sys.exit(1)
            continue

        staged_set = set(get_staged_files(existing_only=False))
        ok, feedback, detail_msg = _validate_grouped_files_or_feedback(staged_set, parsed)
        if not ok:
            attempts += 1
            error_msg = (
                f"Grouped commits file set mismatch after {attempts} retries{': ' + detail_msg if detail_msg else ''}"
            )
            if _handle_validation_retry(
                attempts,
                content_retry_budget,
                raw_response,
                feedback,
                error_msg,
                conversation_messages,
                quiet,
                "File coverage mismatch, asking model to fix...",
            ):
                sys.exit(1)
            continue

        grouped_result = parsed
        conversation_messages.append({"role": "assistant", "content": raw_response})

        if not quiet:
            console.print(f"[green]✔ Generated commit messages with {provider} {model_name}[/green]")
            num_commits = len(grouped_result["commits"])
            console.print(f"[bold green]Proposed Commits ({num_commits}):[/bold green]\n")
            for idx, commit in enumerate(grouped_result["commits"], 1):
                files = commit["files"]
                files_display = ", ".join(files)
                console.print(f"[dim]{files_display}[/dim]")
                commit_msg = commit["message"]
                console.print(Panel(commit_msg, title=f"Commit Message {idx}/{num_commits}", border_style="cyan"))
                console.print()

            completion_tokens = count_tokens(raw_response, model)
            total_tokens = prompt_tokens + completion_tokens
            console.print(
                f"[dim]Token usage: {prompt_tokens} prompt + {completion_tokens} completion = {total_tokens} total[/dim]"
            )

        if require_confirmation:
            accepted = False
            num_commits = len(grouped_result["commits"]) if grouped_result else 0
            while True:
                response = click.prompt(
                    f"Proceed with {num_commits} commits above? [y/n/r/<feedback>]",
                    type=str,
                    show_default=False,
                ).strip()
                response_lower = response.lower()

                if response_lower in ["y", "yes"]:
                    accepted = True
                    break
                if response_lower in ["n", "no"]:
                    console.print("[yellow]Commits not accepted. Exiting...[/yellow]")
                    sys.exit(0)
                if response == "":
                    continue
                if response_lower in ["r", "reroll"]:
                    feedback_message = "Please provide alternative commit groupings using the same repository context."
                    console.print("[cyan]Regenerating commit groups...[/cyan]")
                    conversation_messages.append({"role": "user", "content": feedback_message})
                    console.print()
                    attempts = 0
                    break

                feedback_message = f"Please revise the commit groupings based on this feedback: {response}"
                console.print(f"[cyan]Regenerating commit groups with feedback: {response}[/cyan]")
                conversation_messages.append({"role": "user", "content": feedback_message})
                console.print()
                attempts = 0
                break

            if not accepted:
                continue

        num_commits = len(grouped_result["commits"]) if grouped_result else 0
        if dry_run:
            console.print(f"[yellow]Dry run: Would create {num_commits} commits[/yellow]")
            for idx, commit in enumerate(grouped_result["commits"], 1):
                console.print(f"\n[cyan]Commit {idx}/{num_commits}:[/cyan]")
                console.print(f"  Files: {', '.join(commit['files'])}")
                console.print(f"  Message: {commit['message'][:50]}...")
        else:
            original_staged_files = get_staged_files(existing_only=False)
            original_staged_diff = run_git_command(["diff", "--cached", "--binary"], silent=True)
            run_git_command(["reset", "HEAD"])

            try:
                for idx, commit in enumerate(grouped_result["commits"], 1):
                    try:
                        for file_path in commit["files"]:
                            run_git_command(["add", "-A", file_path])
                        execute_commit(commit["message"], no_verify)
                        console.print(f"[green]✓ Commit {idx}/{num_commits} created[/green]")
                    except Exception as e:
                        console.print(f"[red]✗ Failed at commit {idx}/{num_commits}: {e}[/red]")
                        console.print(f"[yellow]Completed {idx - 1}/{num_commits} commits.[/yellow]")
                        if idx == 1:
                            console.print("[yellow]Restoring original staging area...[/yellow]")
                            restore_staging(original_staged_files, original_staged_diff)
                            console.print("[green]Original staging area restored.[/green]")
                        sys.exit(1)
            except KeyboardInterrupt:
                console.print("\n[yellow]Interrupted by user. Restoring original staging area...[/yellow]")
                restore_staging(original_staged_files, original_staged_diff)
                console.print("[green]Original staging area restored.[/green]")
                sys.exit(1)

        if push:
            try:
                if dry_run:
                    console.print("[yellow]Dry run: Would push changes[/yellow]")
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

        sys.exit(0)


def execute_single_commit_workflow(
    *,
    system_prompt: str,
    user_prompt: str,
    model: str,
    temperature: float,
    max_output_tokens: int,
    max_retries: int,
    require_confirmation: bool,
    quiet: bool,
    no_verify: bool,
    dry_run: bool,
    push: bool,
    show_prompt: bool,
    hook_timeout: int = 120,
) -> None:
    if show_prompt:
        full_prompt = f"SYSTEM PROMPT:\n{system_prompt}\n\nUSER PROMPT:\n{user_prompt}"
        console.print(Panel(full_prompt, title="Prompt for LLM", border_style="bright_blue"))

    conversation_messages: list[dict[str, str]] = []
    if system_prompt:
        conversation_messages.append({"role": "system", "content": system_prompt})
    conversation_messages.append({"role": "user", "content": user_prompt})

    _parse_model_identifier(model)

    first_iteration = True
    while True:
        prompt_tokens = count_tokens(conversation_messages, model)
        if first_iteration:
            warning_limit_val = config.get("warning_limit_tokens", EnvDefaults.WARNING_LIMIT_TOKENS)
            assert warning_limit_val is not None
            warning_limit = int(warning_limit_val)
            if not check_token_warning(prompt_tokens, warning_limit, require_confirmation):
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
        commit_message = clean_commit_message(raw_commit_message)
        logger.info("Generated commit message:")
        logger.info(commit_message)
        conversation_messages.append({"role": "assistant", "content": commit_message})
        display_commit_message(commit_message, prompt_tokens, model, quiet)

        if require_confirmation:
            decision, commit_message, conversation_messages = handle_confirmation_loop(
                commit_message, conversation_messages, quiet, model
            )
            if decision == "no":
                console.print("[yellow]Prompt not accepted. Exiting...[/yellow]")
                sys.exit(0)
            elif decision == "yes":
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
        execute_commit(commit_message, no_verify)

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


def main(
    stage_all: bool = False,
    group: bool = False,
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
    hook_timeout: int = 120,
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

    staged_files = get_staged_files(existing_only=False)

    if group:
        num_files = len(staged_files)
        multiplier = min(5, 2 + (num_files // 10))
        max_output_tokens *= multiplier
        logger.debug(f"Grouped mode: scaling max_output_tokens by {multiplier}x for {num_files} files")

    if not staged_files:
        console.print(
            "[yellow]No staged changes found. Stage your changes with git add first or use --add-all.[/yellow]"
        )
        sys.exit(0)

    if not no_verify and not dry_run:
        if not run_lefthook_hooks(hook_timeout):
            console.print("[red]Lefthook hooks failed. Please fix the issues and try again.[/red]")
            console.print("[yellow]You can use --no-verify to skip pre-commit and lefthook hooks.[/yellow]")
            sys.exit(1)

        if not run_pre_commit_hooks(hook_timeout):
            console.print("[red]Pre-commit hooks failed. Please fix the issues and try again.[/red]")
            console.print("[yellow]You can use --no-verify to skip pre-commit and lefthook hooks.[/yellow]")
            sys.exit(1)

    status = get_staged_status()
    diff = run_git_command(["diff", "--staged"])
    diff_stat = " " + run_git_command(["diff", "--stat", "--cached"])

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
                status = get_staged_status()
                diff = run_git_command(["diff", "--staged"])
                diff_stat = " " + run_git_command(["diff", "--stat", "--cached"])
        else:
            logger.info("No secrets detected in staged changes")

    logger.debug(f"Preprocessing diff ({len(diff)} characters)")
    assert model is not None
    processed_diff = preprocess_diff(diff, token_limit=Utility.DEFAULT_DIFF_TOKEN_LIMIT, model=model)
    logger.debug(f"Processed diff ({len(processed_diff)} characters)")

    system_template_path_value = config.get("system_prompt_path")
    system_template_path: str | None = (
        system_template_path_value if isinstance(system_template_path_value, str) else None
    )

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

    if group:
        from gac.prompt import build_group_prompt

        system_prompt, user_prompt = build_group_prompt(
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

        try:
            execute_grouped_commits_workflow(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model=model,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                max_retries=max_retries,
                require_confirmation=require_confirmation,
                quiet=quiet,
                no_verify=no_verify,
                dry_run=dry_run,
                push=push,
                show_prompt=show_prompt,
                hook_timeout=hook_timeout,
            )
        except AIError as e:
            logger.error(str(e))
            console.print(f"[red]Failed to generate grouped commits: {str(e)}[/red]")
            sys.exit(1)
    else:
        try:
            execute_single_commit_workflow(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model=model,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                max_retries=max_retries,
                require_confirmation=require_confirmation,
                quiet=quiet,
                no_verify=no_verify,
                dry_run=dry_run,
                push=push,
                show_prompt=show_prompt,
                hook_timeout=hook_timeout,
            )
        except AIError as e:
            logger.error(str(e))
            console.print(f"[red]Failed to generate commit message: {str(e)}[/red]")
            sys.exit(1)


if __name__ == "__main__":
    main()
