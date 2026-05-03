#!/usr/bin/env python3
"""Business logic for gac: orchestrates the commit workflow, including git state, formatting,
prompt building, AI generation, and commit/push operations. This module contains no CLI wiring.
"""

import logging

from gac.ai import generate_commit_message
from gac.ai_utils import count_tokens
from gac.commit_executor import CommitExecutor
from gac.config import GACConfig
from gac.errors import AIError, ConfigError, handle_error
from gac.git import run_lefthook_hooks, run_pre_commit_hooks
from gac.git_state_validator import GitStateValidator
from gac.grouped_commit_workflow import GroupedCommitWorkflow
from gac.interactive_mode import InteractiveMode
from gac.oauth_retry import handle_oauth_retry
from gac.postprocess import clean_commit_message
from gac.prompt_builder import PromptBuilder
from gac.stats import record_commit, record_gac, record_tokens, reset_gac_token_accumulator
from gac.utils import console
from gac.workflow_context import CLIOptions, GenerationConfig, WorkflowContext, WorkflowFlags, WorkflowState
from gac.workflow_utils import check_token_warning, display_commit_message

logger = logging.getLogger(__name__)


def _execute_single_commit_workflow(ctx: WorkflowContext, config: GACConfig) -> int:
    """Execute single commit workflow using extracted components.

    Args:
        ctx: WorkflowContext containing all configuration, flags, and state
        config: Application configuration

    Returns:
        Exit code: 0 for success, non-zero for failure/abort
    """
    conversation_messages: list[dict[str, str]] = []
    if ctx.system_prompt:
        conversation_messages.append({"role": "system", "content": ctx.system_prompt})
    conversation_messages.append({"role": "user", "content": ctx.user_prompt})

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

    # Generate commit message
    first_iteration = True
    while True:
        # Reset the per-gac token accumulator so that user-initiated
        # regenerations don't inflate biggest_gac_tokens.  Only the
        # final successful call's tokens should count toward the
        # "biggest gac" record.
        reset_gac_token_accumulator()

        prompt_tokens = count_tokens(conversation_messages, ctx.model)
        if first_iteration:
            warning_limit = config["warning_limit_tokens"]
            if not check_token_warning(prompt_tokens, warning_limit, ctx.flags.require_confirmation):
                return 0  # User declined due to token warning
        first_iteration = False

        raw_commit_message, prov_prompt_tokens, prov_completion_tokens, duration_ms, reasoning_tokens = (
            generate_commit_message(
                model=ctx.model,
                prompt=conversation_messages,
                temperature=ctx.temperature,
                max_tokens=ctx.max_output_tokens,
                max_retries=ctx.max_retries,
                quiet=ctx.quiet or ctx.message_only,
            )
        )
        commit_message = clean_commit_message(raw_commit_message, fifty_seventy_two=ctx.flags.fifty_seventy_two)
        logger.info("Generated commit message:")
        logger.info(commit_message)
        record_tokens(
            prov_prompt_tokens,
            prov_completion_tokens,
            model=ctx.model,
            duration_ms=duration_ms,
            reasoning_tokens=reasoning_tokens,
        )
        conversation_messages.append({"role": "assistant", "content": commit_message})

        if ctx.message_only:
            print(commit_message)
            reset_gac_token_accumulator()  # Don't leak tokens into next request
            return 0

        # Display commit message panel (always show, regardless of confirmation mode)
        if not ctx.quiet:
            display_commit_message(
                commit_message,
                prov_prompt_tokens,
                ctx.model,
                completion_tokens=prov_completion_tokens,
                reasoning_tokens=reasoning_tokens,
            )

        # Handle confirmation
        if ctx.flags.require_confirmation:
            final_message, decision = ctx.state.interactive_mode.handle_single_commit_confirmation(
                model=ctx.model,
                commit_message=commit_message,
                conversation_messages=conversation_messages,
                quiet=ctx.quiet,
            )
            if decision == "yes":
                commit_message = final_message
                break
            elif decision == "no":
                console.print("[yellow]Commit aborted.[/yellow]")
                reset_gac_token_accumulator()  # Don't leak tokens into next request
                return 0  # User aborted
            # decision == "regenerate": continue the loop
        else:
            break

    # Execute the commit
    ctx.state.commit_executor.create_commit(commit_message)

    # Record successful commit and gac (only when commit actually happened)
    if not ctx.flags.dry_run:
        record_commit()
        record_gac(model=ctx.model)

    # Push if requested
    if ctx.flags.push:
        ctx.state.commit_executor.push_to_remote()

    if not ctx.quiet:
        logger.info("Successfully committed changes with message:")
        logger.info(commit_message)
        if ctx.flags.push:
            logger.info("Changes pushed to remote.")
    return 0


def main(opts: CLIOptions, config: GACConfig | None = None) -> int:
    """Main application logic for gac.

    Args:
        opts: CLI options bundled in a dataclass
        config: Application configuration. If None, loaded via load_config().

    Returns:
        Exit code: 0 for success, non-zero for failure
    """
    if config is None:
        from gac.config import load_config

        config = load_config()

    # Initialize components
    git_validator = GitStateValidator(config)
    prompt_builder = PromptBuilder(config)
    commit_executor = CommitExecutor(
        dry_run=opts.dry_run,
        quiet=opts.quiet,
        no_verify=opts.no_verify,
        hook_timeout=opts.hook_timeout,
        signoff=opts.signoff,
    )
    interactive_mode = InteractiveMode(config)
    grouped_workflow = GroupedCommitWorkflow(config)

    # Validate and get model configuration
    model = opts.model
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
    if temperature_val is None:
        raise ConfigError("temperature configuration missing")
    temperature = float(temperature_val)

    max_tokens_val = config["max_output_tokens"]
    if max_tokens_val is None:
        raise ConfigError("max_output_tokens configuration missing")
    max_output_tokens = int(max_tokens_val)

    max_retries_val = config["max_retries"]
    if max_retries_val is None:
        raise ConfigError("max_retries configuration missing")
    max_retries = int(max_retries_val)

    # Get git state and handle hooks
    git_state = git_validator.get_git_state(
        stage_all=opts.stage_all,
        dry_run=opts.dry_run,
        skip_secret_scan=opts.skip_secret_scan,
        quiet=opts.quiet,
        model=model,
    )

    # No staged changes found
    if git_state is None:
        return 0

    # Run pre-commit hooks
    if not opts.no_verify and not opts.dry_run:
        if not run_lefthook_hooks(opts.hook_timeout):
            console.print("[red]Lefthook hooks failed. Please fix the issues and try again.[/red]")
            console.print("[yellow]You can use --no-verify to skip pre-commit and lefthook hooks.[/yellow]")
            return 1

        if not run_pre_commit_hooks(opts.hook_timeout):
            console.print("[red]Pre-commit hooks failed. Please fix the issues and try again.[/red]")
            console.print("[yellow]You can use --no-verify to skip pre-commit and lefthook hooks.[/yellow]")
            return 1

    # Handle secret detection
    if git_state.has_secrets:
        secret_decision = git_validator.handle_secret_detection(git_state.secrets, opts.quiet)
        if secret_decision is None:
            # User chose to abort
            return 0
        if not secret_decision:
            # Secrets were removed, we need to refresh the git state
            git_state = git_validator.get_git_state(
                stage_all=False,
                dry_run=opts.dry_run,
                skip_secret_scan=True,
                quiet=opts.quiet,
                model=model,
            )
            # After removing secret files, no staged changes may remain
            if git_state is None:
                return 0

    # Adjust max_output_tokens for grouped mode
    if opts.group:
        num_files = len(git_state.staged_files)
        multiplier = min(5, 2 + (num_files // 10))
        max_output_tokens *= multiplier
        logger.debug(f"Grouped mode: scaling max_output_tokens by {multiplier}x for {num_files} files")

    # Build prompts
    prompts = prompt_builder.build_prompts(
        git_state=git_state,
        group=opts.group,
        one_liner=opts.one_liner,
        hint=opts.hint,
        infer_scope=opts.infer_scope,
        verbose=opts.verbose,
        language=opts.language,
        fifty_seventy_two=opts.fifty_seventy_two,
    )

    # Display prompts if requested
    if opts.show_prompt:
        prompt_builder.display_prompts(prompts.system_prompt, prompts.user_prompt)

    def _build_context() -> WorkflowContext:
        """Build WorkflowContext for the single-commit path."""
        gen_config = GenerationConfig(
            model=model,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            max_retries=max_retries,
        )
        flags = WorkflowFlags(
            require_confirmation=opts.require_confirmation,
            quiet=opts.quiet,
            no_verify=opts.no_verify,
            dry_run=opts.dry_run,
            message_only=opts.message_only,
            push=opts.push,
            show_prompt=opts.show_prompt,
            interactive=opts.interactive,
            hook_timeout=opts.hook_timeout,
            fifty_seventy_two=opts.fifty_seventy_two,
            signoff=opts.signoff,
        )
        state = WorkflowState(
            prompts=prompts,
            git_state=git_state,
            hint=opts.hint,
            commit_executor=commit_executor,
            interactive_mode=interactive_mode,
        )
        return WorkflowContext(config=gen_config, flags=flags, state=state)

    try:
        if opts.group:
            # Execute grouped workflow using the same WorkflowContext
            return grouped_workflow.execute_workflow(_build_context(), config)
        else:
            # Execute single commit workflow
            return _execute_single_commit_workflow(_build_context(), config)
    except AIError as e:
        return handle_oauth_retry(e=e, ctx=_build_context(), config=config)


if __name__ == "__main__":
    from gac.config import load_config

    raise SystemExit(main(CLIOptions(), load_config()))
