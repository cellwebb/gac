# flake8: noqa: E304

"""CLI entry point for GAC.

Defines the Click-based command-line interface and delegates execution to the main workflow.
"""

import logging
import sys

import click

from gac import __version__
from gac.config import load_config
from gac.config_cli import config as config_cli
from gac.constants import Logging
from gac.diff_cli import diff as diff_cli
from gac.errors import handle_error
from gac.init_cli import init as init_cli
from gac.main import main
from gac.preview_cli import preview as preview_cli
from gac.utils import setup_logging

config = load_config()
logger = logging.getLogger(__name__)


@click.group(invoke_without_command=True, context_settings=dict(ignore_unknown_options=True))
# Git workflow options
@click.option("--add-all", "-a", is_flag=True, help="Stage all changes before committing")
@click.option("--no-format", "-nf", is_flag=True, help="Skip formatting of staged files")
@click.option("--push", "-p", is_flag=True, help="Push changes to remote after committing")
@click.option("--dry-run", is_flag=True, help="Dry run the commit workflow")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")

# Commit message options
@click.option("--one-liner", "-o", is_flag=True, help="Generate a single-line commit message")
@click.option("--show-prompt", is_flag=True, help="Show the prompt sent to the LLM")
@click.option(
    "--scope",
    "-s",
    is_flag=False,
    flag_value="",
    default=None,
    help="Add a scope to the commit message. If used without a value, the LLM will determine an appropriate scope.",
)
@click.option("--hint", "-h", default="", help="Additional context to include in the prompt")

# Model options
@click.option("--model", "-m", help="Override the default model (format: 'provider:model_name')")

# Output options
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-error output")
@click.option("--verbose", "-v", is_flag=True, help="Increase output verbosity to INFO")
@click.option(
    "--log-level",
    default=config["log_level"],
    type=click.Choice(Logging.LEVELS, case_sensitive=False),
    help=f"Set log level (default: {config['log_level']})",
)

# Other options
@click.option("--version", is_flag=True, help="Show the version of the Git Auto Commit (GAC) tool")
@click.pass_context
def cli(
    ctx: click.Context,
    add_all: bool = False,
    log_level: str = config["log_level"],
    no_format: bool = False,
    one_liner: bool = False,
    push: bool = False,
    show_prompt: bool = False,
    scope: str = None,
    quiet: bool = False,
    yes: bool = False,
    hint: str = "",
    model: str = None,
    version: bool = False,
    dry_run: bool = False,
    verbose: bool = False,
) -> None:
    """Git Auto Commit - Generate commit messages with AI."""
    if ctx.invoked_subcommand is None:
        if version:
            print(f"Git Auto Commit (GAC) version: {__version__}")
            sys.exit(0)
        effective_log_level = log_level
        if verbose and log_level not in ("DEBUG", "INFO"):
            effective_log_level = "INFO"
        if quiet:
            effective_log_level = "ERROR"
        setup_logging(effective_log_level)
        logger.info("Starting GAC")
        try:
            main(
                stage_all=add_all,
                should_format_files=not no_format,
                model=model,
                hint=hint,
                one_liner=one_liner,
                show_prompt=show_prompt,
                scope=scope,
                require_confirmation=not yes,
                push=push,
                quiet=quiet,
                dry_run=dry_run,
            )
        except Exception as e:
            handle_error(e, exit_program=True)
    else:
        ctx.obj = {
            "add_all": add_all,
            "log_level": log_level,
            "no_format": no_format,
            "one_liner": one_liner,
            "push": push,
            "show_prompt": show_prompt,
            "scope": scope,
            "quiet": quiet,
            "yes": yes,
            "hint": hint,
            "model": model,
            "version": version,
            "dry_run": dry_run,
            "verbose": verbose,
        }


cli.add_command(config_cli)
cli.add_command(init_cli)
cli.add_command(preview_cli)
cli.add_command(diff_cli)

if __name__ == "__main__":
    cli()
