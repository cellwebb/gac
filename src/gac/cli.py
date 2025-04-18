"""CLI entry point for GAC.

Defines the Click-based command-line interface and delegates execution to the main workflow.
"""

import logging
import sys

import click

from gac import __version__
from gac.config import load_config
from gac.constants import Logging
from gac.errors import handle_error
from gac.main import main
from gac.utils import setup_logging

config = load_config()
logger = logging.getLogger(__name__)


@click.command()
@click.option("--add-all", "-a", is_flag=True, help="Stage all changes before committing")
@click.option(
    "--log-level",
    default=config["log_level"],
    type=click.Choice(Logging.LEVELS, case_sensitive=False),
    help=f"Set log level (default: {config['log_level']})",
)
@click.option("--no-format", "-nf", is_flag=True, help="Skip formatting of staged files")
@click.option("--one-liner", "-o", is_flag=True, help="Generate a single-line commit message")
@click.option("--push", "-p", is_flag=True, help="Push changes to remote after committing")
@click.option("--show-prompt", "-s", is_flag=True, help="Show the prompt sent to the LLM")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-error output")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
@click.option("--hint", "-h", default="", help="Additional context to include in the prompt")
@click.option("--model", "-m", help="Override the default model (format: 'provider:model_name')")
@click.option("--version", is_flag=True, help="Show the version of the Git Auto Commit (GAC) tool")
@click.option("--dry-run", is_flag=True, help="Dry run the commit workflow")
@click.option("--verbose", "-v", is_flag=True, help="Increase output verbosity to INFO")
def cli(
    add_all: bool = False,
    log_level: str = config["log_level"],
    no_format: bool = False,
    one_liner: bool = False,
    push: bool = False,
    show_prompt: bool = False,
    quiet: bool = False,
    yes: bool = False,
    hint: str = "",
    model: str = None,
    version: bool = False,
    dry_run: bool = False,
    verbose: bool = False,
):
    """Git Auto Commit - Generate commit messages with AI."""
    if version:
        logger.info(f"Git Auto Commit (GAC) version: {__version__}")
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
            require_confirmation=not yes,
            push=push,
            quiet=quiet,
            dry_run=dry_run,
        )
    except Exception as e:
        handle_error(e, exit_program=True)


if __name__ == "__main__":
    cli()
