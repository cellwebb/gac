#!/usr/bin/env python3
"""Grouped commit workflow handling for gac.

This module orchestrates the grouped-commit workflow by composing three
smaller, focused helpers:

- **grouped_response_parser** – JSON parsing, structural validation,
  and file-coverage validation.
- **grouped_retry_loop** – retry / feedback-loop logic.
- **grouped_commit_executor** – committing, staging restoration, and
  push with rollback.

The ``GroupedCommitWorkflow`` class ties them together into the full
generate → validate → retry → confirm → execute cycle.
"""
# mypy: warn-unreachable=false

import logging
from typing import Any, NamedTuple

import click
from rich.panel import Panel

from gac.ai import generate_grouped_commits
from gac.ai_utils import count_tokens
from gac.config import GACConfig
from gac.grouped_commit_executor import GroupedCommitResult, execute_grouped_commits
from gac.grouped_response_parser import parse_json_response, validate_file_coverage
from gac.grouped_retry_loop import should_exit_or_retry
from gac.model_identifier import ModelIdentifier
from gac.prompt_builder import PromptBuilder
from gac.stats import record_tokens, reset_gac_token_accumulator
from gac.utils import console
from gac.workflow_context import WorkflowContext
from gac.workflow_utils import PromptFn, check_token_warning, format_token_usage

logger = logging.getLogger(__name__)


# Re-export symbols that were moved to submodules during the refactor.
# This keeps in-repo imports working without churn.
__all__ = [
    "GroupedCommitResult",
    "GroupedCommitWorkflow",
    "WorkflowResult",
]


class WorkflowResult(NamedTuple):
    """Tagged result from generate_grouped_commits_with_retry."""

    success: bool
    result: GroupedCommitResult | None = None
    exit_code: int = 0


class GroupedCommitWorkflow:
    """Handles multi-file grouping logic and per-group AI calls.

    Delegates parsing/validation, retry, and execution to focused helper
    modules while retaining the high-level orchestration here.
    """

    def __init__(self, config: GACConfig):
        self.config = config

    # ── Validation helpers (delegated) ────────────────────────────────

    def validate_grouped_files_or_feedback(
        self, staged: set[str], grouped_result: dict[str, Any]
    ) -> tuple[bool, str, str]:
        """Validate that grouped commits cover all staged files correctly.

        Delegates to :func:`gac.grouped_response_parser.validate_file_coverage`.
        """
        return validate_file_coverage(staged, grouped_result)

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
        """Handle validation retry logic.

        Delegates to :func:`gac.grouped_retry_loop.should_exit_or_retry`.
        Returns ``True`` if should exit, ``False`` if should retry.
        """
        return should_exit_or_retry(
            attempts=attempts,
            budget=content_retry_budget,
            raw_response=raw_response,
            feedback_message=feedback_message,
            error_message=error_message,
            conversation_messages=conversation_messages,
            quiet=quiet,
            retry_context=retry_context,
        )

    def parse_and_validate_json_response(self, raw_response: str) -> dict[str, Any] | None:
        """Parse and validate JSON response from AI.

        Delegates to :func:`gac.grouped_response_parser.parse_json_response`.
        """
        return parse_json_response(raw_response)

    # ── Generate-with-retry loop ─────────────────────────────────────

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
    ) -> WorkflowResult:
        """Generate grouped commits with validation and retry logic.

        Returns:
            WorkflowResult: success=True with result, or success=False with exit_code.
        """
        first_iteration = True
        content_retry_budget = max(3, int(max_retries))
        attempts = 0

        warning_limit = self.config["warning_limit_tokens"]

        while True:
            reset_gac_token_accumulator()

            prompt_tokens = count_tokens(conversation_messages, model)

            if first_iteration:
                if not check_token_warning(prompt_tokens, warning_limit, require_confirmation):
                    return WorkflowResult(success=True, exit_code=0)
            first_iteration = False

            raw_response, prov_prompt_tokens, prov_completion_tokens, duration_ms, reasoning_tokens = (
                generate_grouped_commits(
                    model=model,
                    prompt=conversation_messages,
                    temperature=temperature,
                    max_tokens=max_output_tokens,
                    max_retries=max_retries,
                    quiet=quiet,
                    skip_success_message=True,
                )
            )

            record_tokens(
                prov_prompt_tokens,
                prov_completion_tokens,
                model=model,
                duration_ms=duration_ms,
                reasoning_tokens=reasoning_tokens,
            )

            # ── Structural validation ────────────────────────────────
            try:
                parsed = parse_json_response(raw_response)
            except ValueError as e:
                attempts += 1
                feedback = (
                    f"Invalid response structure: {e}. "
                    "Please return ONLY valid JSON following the schema with a non-empty "
                    "'commits' array of objects containing 'files' and 'message'."
                )
                error_msg = f"Invalid grouped commits structure after {attempts} retries: {e}"
                if should_exit_or_retry(
                    attempts=attempts,
                    budget=content_retry_budget,
                    raw_response=raw_response,
                    feedback_message=feedback,
                    error_message=error_msg,
                    conversation_messages=conversation_messages,
                    quiet=quiet,
                    retry_context="Structure validation failed, asking model to fix...",
                ):
                    return WorkflowResult(success=False, exit_code=1)
                continue

            # ── File-coverage validation ──────────────────────────────
            ok, feedback, detail_msg = validate_file_coverage(staged_files_set, parsed)
            if not ok:
                attempts += 1
                error_msg = f"Grouped commits file set mismatch after {attempts} retries"
                if detail_msg:
                    error_msg += f": {detail_msg}"
                if should_exit_or_retry(
                    attempts=attempts,
                    budget=content_retry_budget,
                    raw_response=raw_response,
                    feedback_message=feedback,
                    error_message=error_msg,
                    conversation_messages=conversation_messages,
                    quiet=quiet,
                    retry_context="File coverage mismatch, asking model to fix...",
                ):
                    return WorkflowResult(success=False, exit_code=1)
                continue

            conversation_messages.append({"role": "assistant", "content": raw_response})
            return WorkflowResult(
                success=True,
                result=GroupedCommitResult(
                    commits=parsed["commits"],
                    raw_response=raw_response,
                    prompt_tokens=prov_prompt_tokens,
                    completion_tokens=prov_completion_tokens,
                    reasoning_tokens=reasoning_tokens,
                ),
            )

    # ── Display ───────────────────────────────────────────────────────

    def display_grouped_commits(
        self,
        result: GroupedCommitResult,
        model: str,
        prompt_tokens: int,
        quiet: bool,
        completion_tokens: int = 0,
        reasoning_tokens: int = 0,
    ) -> None:
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

            if completion_tokens == 0:
                completion_tokens = count_tokens(result.raw_response, model)
            console.print(
                f"[dim]Token usage: {format_token_usage(prompt_tokens, completion_tokens, reasoning_tokens)}[/dim]"
            )

    # ── Confirmation ─────────────────────────────────────────────────

    def handle_grouped_commit_confirmation(
        self,
        result: GroupedCommitResult,
        conversation_messages: list[dict[str, str]],
        prompt_fn: PromptFn | None = None,
    ) -> str:
        """Handle user confirmation for grouped commits.

        Mutates ``conversation_messages`` to append a regenerate or
        feedback instruction so the next AI call has guidance.

        Returns:
            "accept", "reject", or "regenerate"
        """
        num_commits = len(result.commits)
        _prompt = prompt_fn or (lambda msg, **kw: click.prompt(msg, **kw))
        while True:
            response = _prompt(
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
                conversation_messages.append(
                    {
                        "role": "user",
                        "content": "Please provide an alternative grouping of these commits using the same repository context.",
                    }
                )
                console.print("[cyan]Regenerating commit groups...[/cyan]")
                return "regenerate"

            conversation_messages.append(
                {
                    "role": "user",
                    "content": f"Please revise the grouped commits based on this feedback: {response}",
                }
            )
            console.print(f"[cyan]Regenerating commit groups with feedback: {response}[/cyan]")
            return "regenerate"

    # ── Execution ─────────────────────────────────────────────────────

    def execute_grouped_commits(
        self,
        result: GroupedCommitResult,
        dry_run: bool,
        push: bool,
        no_verify: bool,
        hook_timeout: int,
        fifty_seventy_two: bool = False,
        signoff: bool = False,
        model: str | None = None,
    ) -> int:
        """Execute the grouped commits.

        Delegates to :func:`gac.grouped_commit_executor.execute_grouped_commits`.
        """
        return execute_grouped_commits(
            result=result,
            dry_run=dry_run,
            push=push,
            no_verify=no_verify,
            hook_timeout=hook_timeout,
            fifty_seventy_two=fifty_seventy_two,
            signoff=signoff,
            model=model,
        )

    # ── Top-level workflow ────────────────────────────────────────────

    def execute_workflow(
        self,
        ctx: WorkflowContext,
        config: GACConfig,
    ) -> int:
        """Execute the complete grouped commit workflow.

        Args:
            ctx: WorkflowContext containing all configuration, flags, and state.
            config: Application configuration (GACConfig).

        Returns:
            Exit code: 0 for success, non-zero for failure.
        """
        from gac.git import get_staged_files

        if ctx.flags.show_prompt:
            PromptBuilder.display_prompts(ctx.system_prompt, ctx.user_prompt)

        conversation_messages: list[dict[str, str]] = []
        if ctx.system_prompt:
            conversation_messages.append({"role": "system", "content": ctx.system_prompt})
        conversation_messages.append({"role": "user", "content": ctx.user_prompt})

        # Get staged files for validation
        staged_files_set = set(get_staged_files(existing_only=False))

        # Handle interactive questions if enabled
        if ctx.interactive and not ctx.message_only:
            ctx.state.interactive_mode.handle_interactive_flow(
                model=ctx.model,
                user_prompt=ctx.user_prompt,
                git_state=ctx.git_state,
                hint=ctx.hint,
                conversation_messages=conversation_messages,
                temperature=ctx.temperature,
                max_tokens=ctx.max_output_tokens,
                max_retries=ctx.max_retries,
                quiet=ctx.quiet,
            )

        while True:
            result = self.generate_grouped_commits_with_retry(
                model=ctx.model,
                conversation_messages=conversation_messages,
                temperature=ctx.temperature,
                max_output_tokens=ctx.max_output_tokens,
                max_retries=ctx.max_retries,
                quiet=ctx.quiet,
                staged_files_set=staged_files_set,
                require_confirmation=ctx.flags.require_confirmation,
            )

            if not result.success:
                return result.exit_code
            if result.result is None:
                return result.exit_code

            commit_result = result.result

            self.display_grouped_commits(
                commit_result,
                ctx.model,
                commit_result.prompt_tokens,
                ctx.quiet,
                completion_tokens=commit_result.completion_tokens,
                reasoning_tokens=commit_result.reasoning_tokens,
            )

            if ctx.flags.require_confirmation:
                decision = self.handle_grouped_commit_confirmation(commit_result, conversation_messages)
                if decision == "accept":
                    return self.execute_grouped_commits(
                        result=commit_result,
                        dry_run=ctx.dry_run,
                        push=ctx.flags.push,
                        no_verify=ctx.flags.no_verify,
                        hook_timeout=ctx.flags.hook_timeout,
                        fifty_seventy_two=ctx.flags.fifty_seventy_two,
                        signoff=ctx.flags.signoff,
                        model=ctx.model,
                    )
                elif decision == "reject":
                    return 0
                else:
                    continue
            else:
                return self.execute_grouped_commits(
                    result=commit_result,
                    dry_run=ctx.dry_run,
                    push=ctx.flags.push,
                    no_verify=ctx.flags.no_verify,
                    hook_timeout=ctx.flags.hook_timeout,
                    fifty_seventy_two=ctx.flags.fifty_seventy_two,
                    signoff=ctx.flags.signoff,
                    model=ctx.model,
                )
