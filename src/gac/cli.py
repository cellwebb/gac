# flake8: noqa: E304

"""CLI entry point for gac.

Defines the Click-based command-line interface and delegates execution to the main workflow.
"""

import logging
import os
import sys
from typing import Any

import click
from rich.console import Console

from gac import __version__
from gac.auth_cli import auth as auth_cli
from gac.config import GACConfig, load_config
from gac.config_cli import config as config_cli
from gac.constants import Languages, Logging
from gac.diff_cli import diff as diff_cli
from gac.errors import handle_error
from gac.init_cli import init as init_cli
from gac.language_cli import language as language_cli
from gac.main import main
from gac.model_cli import model as model_cli
from gac.prompt_cli import prompt as prompt_cli
from gac.utils import setup_logging
from gac.workflow_context import CLIOptions

config: GACConfig = load_config()
logger = logging.getLogger(__name__)
console = Console()


@click.group(invoke_without_command=True, context_settings={"ignore_unknown_options": True})
# Git workflow options
@click.option("--add-all", "-a", is_flag=True, help="Stage all changes before committing")
@click.option("--group", "-g", is_flag=True, help="Group changes into multiple logical commits")
@click.option(
    "--interactive", "-i", is_flag=True, help="Ask interactive questions to gather more context for the commit message"
)
@click.option("--push", "-p", is_flag=True, help="Push changes to remote after committing")
@click.option("--dry-run", is_flag=True, help="Dry run the commit workflow")
@click.option("--message-only", is_flag=True, help="Output only the generated commit message without committing")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
# Commit message options
@click.option("--one-liner", "-o", is_flag=True, help="Generate a single-line commit message")
@click.option("--show-prompt", is_flag=True, help="Show the prompt sent to the LLM")
@click.option(
    "--scope",
    "-s",
    is_flag=True,
    default=False,
    help="Infer an appropriate scope for the commit message",
)
@click.option("--hint", "-h", default="", help="Additional context to include in the prompt")
# Model options
@click.option("--model", "-m", help="Override the default model (format: 'provider:model_name')")
@click.option(
    "--language", "-l", help="Override the language for commit messages (e.g., 'Spanish', 'es', 'zh-CN', 'ja')"
)
# Output options
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-error output")
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Generate detailed commit messages with motivation, architecture, and impact sections",
)
@click.option(
    "--log-level",
    default=config["log_level"],
    type=click.Choice(Logging.LEVELS, case_sensitive=False),
    help=f"Set log level (default: {config['log_level']})",
)
# Advanced options
@click.option("--no-verify", is_flag=True, help="Skip pre-commit and lefthook hooks when committing")
@click.option("--skip-secret-scan", is_flag=True, help="Skip security scan for secrets in staged changes")
@click.option(
    "--no-verify-ssl",
    is_flag=True,
    help="Skip SSL certificate verification (useful for corporate proxies)",
)
@click.option(
    "--hook-timeout",
    type=int,
    default=0,
    help="Timeout for pre-commit and lefthook hooks in seconds (0 to use configuration)",
)
# Other options
@click.option("--version", is_flag=True, help="Show the version of the Git Auto Commit (gac) tool")
@click.pass_context
def cli(
    ctx: click.Context,
    add_all: bool = False,
    group: bool = False,
    interactive: bool = False,
    log_level: str = str(config["log_level"]),
    one_liner: bool = False,
    push: bool = False,
    show_prompt: bool = False,
    scope: bool = False,
    quiet: bool = False,
    yes: bool = False,
    hint: str = "",
    model: str | None = None,
    language: str | None = None,
    version: bool = False,
    dry_run: bool = False,
    message_only: bool = False,
    verbose: bool = False,
    no_verify: bool = False,
    skip_secret_scan: bool = False,
    no_verify_ssl: bool = False,
    hook_timeout: int = 0,
) -> None:
    """Git Auto Commit - Generate commit messages with AI."""
    if ctx.invoked_subcommand is None:
        if version:
            print(f"Git Auto Commit (gac) version: {__version__}")
            sys.exit(0)
        effective_log_level = log_level
        if quiet:
            effective_log_level = "ERROR"
        setup_logging(effective_log_level)
        logger.info("Starting gac")

        # Set SSL verification environment variable if flag is used or config is set
        if no_verify_ssl or config["no_verify_ssl"]:
            os.environ["GAC_NO_VERIFY_SSL"] = "true"
            logger.info("SSL certificate verification disabled")

        # Validate incompatible flag combinations
        if message_only and group:
            console.print("[red]Error: --message-only and --group options are mutually exclusive[/red]")
            console.print("[yellow]--message-only is for generating a single commit message for external use[/yellow]")
            console.print("[yellow]--group is for organizing multiple commits within the current workflow[/yellow]")
            sys.exit(1)

        # Determine if we should infer scope based on -s flag or always_include_scope setting
        infer_scope = bool(scope or config["always_include_scope"])

        # Determine if verbose mode should be enabled based on -v flag or verbose config setting
        use_verbose = bool(verbose or config["verbose"])

        # Resolve language code to full name if provided
        resolved_language = Languages.resolve_code(language) if language else None

        try:
            opts = CLIOptions(
                stage_all=add_all,
                group=group,
                interactive=interactive,
                model=model,
                hint=hint,
                one_liner=one_liner,
                show_prompt=show_prompt,
                infer_scope=bool(infer_scope),
                require_confirmation=not yes,
                push=push,
                quiet=quiet,
                dry_run=dry_run,
                message_only=message_only,
                verbose=use_verbose,
                no_verify=no_verify,
                skip_secret_scan=skip_secret_scan or config["skip_secret_scan"],
                language=resolved_language,
                hook_timeout=hook_timeout if hook_timeout > 0 else config["hook_timeout"],
            )
            exit_code = main(opts)
            sys.exit(exit_code)
        except Exception as e:
            handle_error(e, exit_program=True)
    else:
        # Determine if we should infer scope based on -s flag or always_include_scope setting
        infer_scope = bool(scope or config["always_include_scope"])

        ctx.obj = {
            "add_all": add_all,
            "group": group,
            "interactive": interactive,
            "log_level": log_level,
            "one_liner": one_liner,
            "push": push,
            "show_prompt": show_prompt,
            "scope": infer_scope,
            "quiet": quiet,
            "yes": yes,
            "hint": hint,
            "model": model,
            "language": language,
            "version": version,
            "dry_run": dry_run,
            "message_only": message_only,
            "verbose": verbose,
            "no_verify": no_verify,
            "skip_secret_scan": skip_secret_scan,
            "no_verify_ssl": no_verify_ssl,
            "hook_timeout": hook_timeout,
        }


cli.add_command(auth_cli)
cli.add_command(config_cli)
cli.add_command(diff_cli)
cli.add_command(init_cli)
cli.add_command(language_cli)
cli.add_command(model_cli)
cli.add_command(prompt_cli)


@click.command(context_settings=language_cli.context_settings)
@click.pass_context
def lang(ctx: Any) -> None:
    """Set the language for commit messages interactively. (Alias for 'language')"""
    ctx.forward(language_cli)


cli.add_command(lang)  # Add the lang alias

if __name__ == "__main__":
    cli()
