#!/usr/bin/env python3
"""Grouped commit workflow handling for gac."""
# mypy: warn-unreachable=false

import json
import logging
import subprocess
from collections import Counter
from typing import Any, NamedTuple

import click
from rich.console import Console
from rich.panel import Panel

from gac.ai import generate_grouped_commits
from gac.ai_utils import count_tokens
from gac.config import GACConfig
from gac.errors import AIError, ConfigError, GitError
from gac.git import detect_rename_mappings, get_staged_files, run_git_command
from gac.git_state_validator import GitState
from gac.model_identifier import ModelIdentifier
from gac.workflow_utils import check_token_warning, execute_commit, restore_staging

logger = logging.getLogger(__name__)
console = Console()


class GroupedCommitResult(NamedTuple):
    """Result of grouped commit generation."""

    commits: list[dict[str, Any]]
    raw_response: str


class GroupedCommitWorkflow:
    """Handles multi-file grouping logic and per-group AI calls."""

    def __init__(self, config: GACConfig):
        self.config = config

    def validate_grouped_files_or_feedback(
        self, staged: set[str], grouped_result: dict[str, Any]
    ) -> tuple[bool, str, str]:
        """Validate that grouped commits cover all staged files correctly."""
        # Handle edge cases that should be caught elsewhere
        if not isinstance(grouped_result, dict):
            return True, "", ""

        commits = grouped_result.get("commits", [])
        # Handle empty commits case (defensive - unreachable in normal flow)
        if not commits:  # pragma: no cover  # type: ignore[unreachable]
            return True, "", ""  # Empty commits is valid (will be caught elsewhere)

        # Check if any commit has invalid structure - these should be caught in JSON validation
        for commit in commits:
            if not isinstance(commit, dict) or "files" not in commit:
                return True, "", ""  # Invalid structure - let JSON validation handle it

        all_files: list[str] = []
        for commit in commits:
            files = commit.get("files", [])
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

    def handle_validation_retry(
        self,
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
            logger.error("Raw model output:")
            console.print(f"\n[red]{error_message}[/red]")
            console.print("\n[yellow]Raw model output:[/yellow]")
            console.print(Panel(raw_response, title="Model Output", border_style="yellow"))
            return True
        if not quiet:
            logger.info(f"Retry {attempts} of {content_retry_budget - 1}: {retry_context}")
            console.print(f"[yellow]Retry {attempts} of {content_retry_budget - 1}: {retry_context}[/yellow]")
        return False

    def parse_and_validate_json_response(self, raw_response: str) -> dict[str, Any] | None:
        """Parse and validate JSON response from AI."""
        parsed: dict[str, Any] | None = None
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
            raise ValueError("Invalid JSON response")

        # Validate structure
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

        return parsed

    def generate_grouped_commits_with_retry(
        self,
        model: str,
        conversation_messages: list[dict[str, str]],
        temperature: float,
        max_output_tokens: int,
        max_retries: int,
        quiet: bool,
        staged_files_set: set[str],
        require_confirmation: bool = True,
    ) -> GroupedCommitResult | int:
        """Generate grouped commits with validation and retry logic.

        Returns:
            GroupedCommitResult on success, or int exit code on early exit/failure.
        """
        first_iteration = True
        content_retry_budget = max(3, int(max_retries))
        attempts = 0

        warning_limit = self.config["warning_limit_tokens"]

        while True:
            prompt_tokens = count_tokens(conversation_messages, model)

            if first_iteration:
                if not check_token_warning(prompt_tokens, warning_limit, require_confirmation):
                    return 0  # User declined due to token warning
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

            try:
                parsed = self.parse_and_validate_json_response(raw_response)
            except ValueError as e:
                attempts += 1
                feedback = f"Invalid response structure: {e}. Please return ONLY valid JSON following the schema with a non-empty 'commits' array of objects containing 'files' and 'message'."
                error_msg = f"Invalid grouped commits structure after {attempts} retries: {e}"
                if self.handle_validation_retry(
                    attempts,
                    content_retry_budget,
                    raw_response,
                    feedback,
                    error_msg,
                    conversation_messages,
                    quiet,
                    "Structure validation failed, asking model to fix...",
                ):
                    return 1  # Validation failed after retries
                continue

            # Assert parsed is not None for mypy - ValueError would have been raised earlier
            assert parsed is not None
            ok, feedback, detail_msg = self.validate_grouped_files_or_feedback(staged_files_set, parsed)
            if not ok:
                attempts += 1
                error_msg = f"Grouped commits file set mismatch after {attempts} retries{': ' + detail_msg if detail_msg else ''}"
                if self.handle_validation_retry(
                    attempts,
                    content_retry_budget,
                    raw_response,
                    feedback,
                    error_msg,
                    conversation_messages,
                    quiet,
                    "File coverage mismatch, asking model to fix...",
                ):
                    return 1  # File validation failed after retries
                continue

            conversation_messages.append({"role": "assistant", "content": raw_response})
            # Assert parsed is not None for mypy - ValueError would have been raised earlier
            assert parsed is not None
            return GroupedCommitResult(commits=parsed["commits"], raw_response=raw_response)

    def display_grouped_commits(self, result: GroupedCommitResult, model: str, prompt_tokens: int, quiet: bool) -> None:
        """Display the generated grouped commits to the user."""
        model_id = ModelIdentifier.parse(model)

        if not quiet:
            console.print(f"[green]✔ Generated commit messages with {model_id.provider} {model_id.model_name}[/green]")
            num_commits = len(result.commits)
            console.print(f"[bold green]Proposed Commits ({num_commits}):[/bold green]\n")
            for idx, commit in enumerate(result.commits, 1):
                files = commit["files"]
                files_display = ", ".join(files)
                console.print(f"[dim]{files_display}[/dim]")
                commit_msg = commit["message"].strip()
                console.print(Panel(commit_msg, title=f"Commit Message {idx}/{num_commits}", border_style="cyan"))
                console.print()

            completion_tokens = count_tokens(result.raw_response, model)
            total_tokens = prompt_tokens + completion_tokens
            console.print(
                f"[dim]Token usage: {prompt_tokens} prompt + {completion_tokens} completion = {total_tokens} total[/dim]"
            )

    def handle_grouped_commit_confirmation(self, result: GroupedCommitResult) -> str:
        """Handle user confirmation for grouped commits.

        Returns:
            "accept": User accepted commits
            "reject": User rejected commits
            "regenerate": User wants to regenerate
        """
        num_commits = len(result.commits)
        while True:
            response = click.prompt(
                f"Proceed with {num_commits} commits above? [y/n/r/<feedback>]",
                type=str,
                show_default=False,
            ).strip()
            response_lower = response.lower()

            if response_lower in ["y", "yes"]:
                return "accept"
            if response_lower in ["n", "no"]:
                console.print("[yellow]Commits not accepted. Exiting...[/yellow]")
                return "reject"
            if response == "":
                continue
            if response_lower in ["r", "reroll"]:
                console.print("[cyan]Regenerating commit groups...[/cyan]")
                return "regenerate"

    def execute_grouped_commits(
        self,
        result: GroupedCommitResult,
        dry_run: bool,
        push: bool,
        no_verify: bool,
        hook_timeout: int,
    ) -> int:
        """Execute the grouped commits by creating multiple individual commits.

        Returns:
            Exit code: 0 for success, non-zero for failure.
        """
        num_commits = len(result.commits)

        restore_needed = False
        original_staged_files: list[str] | None = None
        original_staged_diff: str | None = None

        if dry_run:
            console.print(f"[yellow]Dry run: Would create {num_commits} commits[/yellow]")
            for idx, commit in enumerate(result.commits, 1):
                console.print(f"\n[cyan]Commit {idx}/{num_commits}:[/cyan]")
                console.print(f"  Files: {', '.join(commit['files'])}")
                console.print(f"  Message: {commit['message'].strip()[:50]}...")
        else:
            original_staged_files = get_staged_files(existing_only=False)
            original_staged_diff = run_git_command(["diff", "--cached", "--binary"], silent=True)
            run_git_command(["reset", "HEAD"])

            try:
                # Detect file renames to handle them properly
                rename_mappings = detect_rename_mappings(original_staged_diff)

                for idx, commit in enumerate(result.commits, 1):
                    try:
                        for file_path in commit["files"]:
                            # Check if this file is the destination of a rename
                            if file_path in rename_mappings:
                                old_file = rename_mappings[file_path]
                                # For renames, stage both the old file (for deletion) and new file
                                # This ensures the complete rename operation is preserved
                                run_git_command(["add", "-A", old_file])
                                run_git_command(["add", "-A", file_path])
                            else:
                                run_git_command(["add", "-A", file_path])
                        execute_commit(commit["message"].strip(), no_verify, hook_timeout)
                        console.print(f"[green]✓ Commit {idx}/{num_commits} created[/green]")
                    except (AIError, ConfigError, GitError, subprocess.SubprocessError, OSError) as e:
                        restore_needed = True
                        console.print(f"[red]✗ Failed at commit {idx}/{num_commits}: {e}[/red]")
                        console.print(f"[yellow]Completed {idx - 1}/{num_commits} commits.[/yellow]")
                        break
            except KeyboardInterrupt:
                restore_needed = True
                console.print("\n[yellow]Interrupted by user. Restoring original staging area...[/yellow]")

            if restore_needed:
                console.print("[yellow]Restoring original staging area...[/yellow]")
                restore_staging(original_staged_files or [], original_staged_diff)
                console.print("[green]Original staging area restored.[/green]")
                return 1

        if push:
            try:
                if dry_run:
                    console.print("[yellow]Dry run: Would push changes[/yellow]")
                    return 0
                from gac.git import push_changes

                if push_changes():
                    logger.info("Changes pushed successfully")
                    console.print("[green]Changes pushed successfully[/green]")
                else:
                    restore_needed = True
                    console.print(
                        "[red]Failed to push changes. Check your remote configuration and network connection.[/red]"
                    )
            except (GitError, OSError) as e:
                restore_needed = True
                console.print(f"[red]Error pushing changes: {e}[/red]")

            if restore_needed:
                console.print("[yellow]Restoring original staging area...[/yellow]")
                if original_staged_files is None or original_staged_diff is None:
                    original_staged_files = get_staged_files(existing_only=False)
                    original_staged_diff = run_git_command(["diff", "--cached", "--binary"])
                restore_staging(original_staged_files, original_staged_diff)
                console.print("[green]Original staging area restored.[/green]")
                return 1

        return 0

    def execute_workflow(
        self,
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
        interactive: bool,
        message_only: bool,
        git_state: GitState,
        hint: str,
        hook_timeout: int = 120,
    ) -> int:
        """Execute the complete grouped commit workflow.

        Returns:
            Exit code: 0 for success, non-zero for failure.
        """
        if show_prompt:
            full_prompt = f"SYSTEM PROMPT:\n{system_prompt}\n\nUSER PROMPT:\n{user_prompt}"
            console.print(Panel(full_prompt, title="Prompt for LLM", border_style="bright_blue"))

        conversation_messages: list[dict[str, str]] = []
        if system_prompt:
            conversation_messages.append({"role": "system", "content": system_prompt})
        conversation_messages.append({"role": "user", "content": user_prompt})

        # Get staged files for validation
        staged_files_set = set(get_staged_files(existing_only=False))

        # Handle interactive questions if enabled
        if interactive and not message_only:
            from gac.interactive_mode import InteractiveMode

            interactive_mode = InteractiveMode(self.config)
            interactive_mode.handle_interactive_flow(
                model=model,
                user_prompt=user_prompt,
                git_state=git_state,
                hint=hint,
                conversation_messages=conversation_messages,
                temperature=temperature,
                max_tokens=max_output_tokens,
                max_retries=max_retries,
                quiet=quiet,
            )

        while True:
            # Generate grouped commits
            result = self.generate_grouped_commits_with_retry(
                model=model,
                conversation_messages=conversation_messages,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                max_retries=max_retries,
                quiet=quiet,
                staged_files_set=staged_files_set,
                require_confirmation=require_confirmation,
            )

            # Check if generation returned an exit code
            if isinstance(result, int):
                return result

            # Display results
            prompt_tokens = count_tokens(conversation_messages, model)
            self.display_grouped_commits(result, model, prompt_tokens, quiet)

            # Handle confirmation
            if require_confirmation:
                decision = self.handle_grouped_commit_confirmation(result)
                if decision == "accept":
                    # User accepted, execute commits
                    return self.execute_grouped_commits(
                        result=result,
                        dry_run=dry_run,
                        push=push,
                        no_verify=no_verify,
                        hook_timeout=hook_timeout,
                    )
                elif decision == "reject":
                    return 0  # User rejected, clean exit
                else:
                    # User wants to regenerate, continue loop
                    continue
            else:
                # No confirmation required, execute directly
                return self.execute_grouped_commits(
                    result=result,
                    dry_run=dry_run,
                    push=push,
                    no_verify=no_verify,
                    hook_timeout=hook_timeout,
                )
