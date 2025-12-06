#!/usr/bin/env python3
"""Business logic for gac: orchestrates the commit workflow, including git state, formatting,
prompt building, AI generation, and commit/push operations. This module contains no CLI wiring.
"""

import logging
import sys

from rich.console import Console

from gac.ai import generate_commit_message
from gac.ai_utils import count_tokens
from gac.commit_executor import CommitExecutor
from gac.config import GACConfig, load_config
from gac.constants import EnvDefaults
from gac.errors import AIError, ConfigError, handle_error
from gac.git import run_lefthook_hooks, run_pre_commit_hooks
from gac.git_state_validator import GitState, GitStateValidator
from gac.grouped_commit_workflow import GroupedCommitWorkflow
from gac.interactive_mode import InteractiveMode
from gac.prompt import clean_commit_message
from gac.prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)

config: GACConfig = load_config()
console = Console()  # Initialize console globally to prevent undefined access


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
            "(example: 'anthropic:claude-haiku-4-5')."
        )
        logger.error(message)
        console.print(f"[red]{message}[/red]")
        sys.exit(1)

    return provider, model_name


def _execute_single_commit_workflow_refactored(
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
    message_only: bool = False,
    push: bool,
    show_prompt: bool,
    hook_timeout: int = 120,
    interactive: bool = False,
    commit_executor: CommitExecutor,
    interactive_mode: InteractiveMode,
    git_state: GitState,
    hint: str,
) -> None:
    """Execute single commit workflow using extracted components."""
    conversation_messages: list[dict[str, str]] = []
    if system_prompt:
        conversation_messages.append({"role": "system", "content": system_prompt})
    conversation_messages.append({"role": "user", "content": user_prompt})

    # Handle interactive questions if enabled
    if interactive and not message_only:
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

    # Generate commit message
    first_iteration = True
    while True:
        prompt_tokens = count_tokens(conversation_messages, model)
        if first_iteration:
            warning_limit_val = config.get("warning_limit_tokens", EnvDefaults.WARNING_LIMIT_TOKENS)
            if warning_limit_val is None:
                raise ConfigError("warning_limit_tokens configuration missing")
            warning_limit = int(warning_limit_val)
            from gac.workflow_utils import check_token_warning

            if not check_token_warning(prompt_tokens, warning_limit, require_confirmation):
                sys.exit(0)
        first_iteration = False

        raw_commit_message = generate_commit_message(
            model=model,
            prompt=conversation_messages,
            temperature=temperature,
            max_tokens=max_output_tokens,
            max_retries=max_retries,
            quiet=quiet or message_only,
        )
        commit_message = clean_commit_message(raw_commit_message)
        logger.info("Generated commit message:")
        logger.info(commit_message)
        conversation_messages.append({"role": "assistant", "content": commit_message})

        if message_only:
            # Output only the commit message without any formatting
            print(commit_message)
            sys.exit(0)

        # Handle confirmation
        if require_confirmation:
            final_message, should_continue = interactive_mode.handle_single_commit_confirmation(
                model=model,
                commit_message=commit_message,
                conversation_messages=conversation_messages,
                quiet=quiet,
            )
            if should_continue:
                commit_message = final_message
                break
            # If user wants to regenerate, continue the loop
        else:
            break

    # Execute the commit
    commit_executor.create_commit(commit_message)

    # Push if requested
    if push:
        commit_executor.push_to_remote()

    if not quiet:
        logger.info("Successfully committed changes with message:")
        logger.info(commit_message)
        if push:
            logger.info("Changes pushed to remote.")
    sys.exit(0)


def _handle_oauth_retry(
    e: AIError,
    prompts,
    model: str,
    temperature: float,
    max_output_tokens: int,
    max_retries: int,
    require_confirmation: bool,
    quiet: bool,
    no_verify: bool,
    dry_run: bool,
    message_only: bool,
    push: bool,
    show_prompt: bool,
    hook_timeout: int,
    interactive: bool,
    commit_executor: CommitExecutor,
    interactive_mode: InteractiveMode,
    git_state: GitState,
    hint: str,
) -> None:
    """Handle OAuth retry logic for expired tokens."""
    logger.error(str(e))

    # Check if this is a Claude Code OAuth token expiration
    if (
        e.error_type == "authentication"
        and model.startswith("claude-code:")
        and ("expired" in str(e).lower() or "oauth" in str(e).lower())
    ):
        console.print("[yellow]⚠ Claude Code OAuth token has expired[/yellow]")
        console.print("[cyan]🔐 Starting automatic re-authentication...[/cyan]")

        try:
            from gac.oauth.claude_code import authenticate_and_save

            if authenticate_and_save(quiet=quiet):
                console.print("[green]✓ Re-authentication successful![/green]")
                console.print("[cyan]Retrying commit...[/cyan]\n")

                # Retry the commit workflow
                _execute_single_commit_workflow_refactored(
                    system_prompt=prompts.system_prompt,
                    user_prompt=prompts.user_prompt,
                    model=model,
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                    max_retries=max_retries,
                    require_confirmation=require_confirmation,
                    quiet=quiet,
                    no_verify=no_verify,
                    dry_run=dry_run,
                    message_only=message_only,
                    push=push,
                    show_prompt=show_prompt,
                    hook_timeout=hook_timeout,
                    interactive=interactive,
                    commit_executor=commit_executor,
                    interactive_mode=interactive_mode,
                    git_state=git_state,
                    hint=hint,
                )
            else:
                console.print("[red]Re-authentication failed.[/red]")
                console.print("[yellow]Run 'gac model' to re-authenticate manually.[/yellow]")
                sys.exit(1)
        except (AIError, ConfigError, OSError) as auth_error:
            console.print(f"[red]Re-authentication error: {auth_error}[/red]")
            console.print("[yellow]Run 'gac model' to re-authenticate manually.[/yellow]")
            sys.exit(1)
    # Check if this is a Qwen OAuth token expiration
    elif e.error_type == "authentication" and model.startswith("qwen:"):
        console.print("[yellow]⚠ Qwen authentication failed[/yellow]")
        console.print("[cyan]🔐 Starting automatic re-authentication...[/cyan]")

        try:
            from gac.oauth import QwenOAuthProvider, TokenStore

            oauth_provider = QwenOAuthProvider(TokenStore())
            oauth_provider.initiate_auth(open_browser=True)
            console.print("[green]✓ Re-authentication successful![/green]")
            console.print("[cyan]Retrying commit...[/cyan]\n")

            # Retry the commit workflow
            _execute_single_commit_workflow_refactored(
                system_prompt=prompts.system_prompt,
                user_prompt=prompts.user_prompt,
                model=model,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                max_retries=max_retries,
                require_confirmation=require_confirmation,
                quiet=quiet,
                no_verify=no_verify,
                dry_run=dry_run,
                message_only=message_only,
                push=push,
                show_prompt=show_prompt,
                hook_timeout=hook_timeout,
                interactive=interactive,
                commit_executor=commit_executor,
                interactive_mode=interactive_mode,
                git_state=git_state,
                hint=hint,
            )
        except (AIError, ConfigError, OSError) as auth_error:
            console.print(f"[red]Re-authentication error: {auth_error}[/red]")
            console.print("[yellow]Run 'gac auth qwen login' to re-authenticate manually.[/yellow]")
            sys.exit(1)
    else:
        # Non-Claude Code/Qwen error or non-auth error
        console.print(f"[red]Failed to generate commit message: {str(e)}[/red]")
        sys.exit(1)


def main(
    stage_all: bool = False,
    group: bool = False,
    interactive: bool = False,
    model: str | None = None,
    hint: str = "",
    one_liner: bool = False,
    show_prompt: bool = False,
    infer_scope: bool = False,
    require_confirmation: bool = True,
    push: bool = False,
    quiet: bool = False,
    dry_run: bool = False,
    message_only: bool = False,
    verbose: bool = False,
    no_verify: bool = False,
    skip_secret_scan: bool = False,
    language: str | None = None,
    hook_timeout: int = 120,
) -> None:
    """Main application logic for gac."""
    # Initialize components
    git_validator = GitStateValidator(config)
    prompt_builder = PromptBuilder(config)
    commit_executor = CommitExecutor(dry_run=dry_run, quiet=quiet, no_verify=no_verify, hook_timeout=hook_timeout)
    interactive_mode = InteractiveMode(config)
    grouped_workflow = GroupedCommitWorkflow(config)

    # Validate and get model configuration
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
        stage_all=stage_all,
        dry_run=dry_run,
        skip_secret_scan=skip_secret_scan,
        quiet=quiet,
        model=model,
        hint=hint,
        one_liner=one_liner,
        infer_scope=infer_scope,
        verbose=verbose,
        language=language,
    )

    # Run pre-commit hooks
    if not no_verify and not dry_run:
        if not run_lefthook_hooks(hook_timeout):
            console.print("[red]Lefthook hooks failed. Please fix the issues and try again.[/red]")
            console.print("[yellow]You can use --no-verify to skip pre-commit and lefthook hooks.[/yellow]")
            sys.exit(1)

        if not run_pre_commit_hooks(hook_timeout):
            console.print("[red]Pre-commit hooks failed. Please fix the issues and try again.[/red]")
            console.print("[yellow]You can use --no-verify to skip pre-commit and lefthook hooks.[/yellow]")
            sys.exit(1)

    # Handle secret detection
    if git_state.has_secrets:
        should_continue = git_validator.handle_secret_detection(git_state.secrets, quiet)
        if not should_continue:
            # If secrets were removed, we need to refresh the git state
            git_state = git_validator.get_git_state(
                stage_all=False,
                dry_run=dry_run,
                skip_secret_scan=True,  # Skip secret scan this time
                quiet=quiet,
                model=model,
                hint=hint,
                one_liner=one_liner,
                infer_scope=infer_scope,
                verbose=verbose,
                language=language,
            )

    # Adjust max_output_tokens for grouped mode
    if group:
        num_files = len(git_state.staged_files)
        multiplier = min(5, 2 + (num_files // 10))
        max_output_tokens *= multiplier
        logger.debug(f"Grouped mode: scaling max_output_tokens by {multiplier}x for {num_files} files")

    # Build prompts
    prompts = prompt_builder.build_prompts(
        git_state=git_state,
        group=group,
        one_liner=one_liner,
        hint=hint,
        infer_scope=infer_scope,
        verbose=verbose,
        language=language,
    )

    # Display prompts if requested
    if show_prompt:
        prompt_builder.display_prompts(prompts.system_prompt, prompts.user_prompt)

    try:
        if group:
            # Execute grouped workflow
            grouped_workflow.execute_workflow(
                system_prompt=prompts.system_prompt,
                user_prompt=prompts.user_prompt,
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
                interactive=interactive,
                message_only=message_only,
                hook_timeout=hook_timeout,
                git_state=git_state,
                hint=hint,
            )
        else:
            # Execute single commit workflow
            _execute_single_commit_workflow_refactored(
                system_prompt=prompts.system_prompt,
                user_prompt=prompts.user_prompt,
                model=model,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                max_retries=max_retries,
                require_confirmation=require_confirmation,
                quiet=quiet,
                no_verify=no_verify,
                dry_run=dry_run,
                message_only=message_only,
                push=push,
                show_prompt=show_prompt,
                hook_timeout=hook_timeout,
                interactive=interactive,
                commit_executor=commit_executor,
                interactive_mode=interactive_mode,
                git_state=git_state,
                hint=hint,
            )
    except AIError as e:
        _handle_oauth_retry(
            e,
            prompts,
            model,
            temperature,
            max_output_tokens,
            max_retries,
            require_confirmation,
            quiet,
            no_verify,
            dry_run,
            message_only,
            push,
            show_prompt,
            hook_timeout,
            interactive,
            commit_executor,
            interactive_mode,
            git_state,
            hint,
        )


if __name__ == "__main__":
    main()
