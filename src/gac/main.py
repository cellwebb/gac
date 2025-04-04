#!/usr/bin/env python3
"""Main entry point for GAC."""

import logging
import sys
from typing import Optional

import click

from gac import __about__
from gac.git import commit_workflow
from gac.utils import print_message, setup_logging

logger = logging.getLogger(__name__)


@click.command()
@click.option("--add-all", "-a", is_flag=True, help="Stage all changes before committing")
@click.option(
    "--config",
    is_flag=True,
    help="Run the interactive configuration wizard and save settings to ~/.gac.env",
)
@click.option(
    "--log-level",
    default="WARNING",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    help="Set log level (default: WARNING)",
)
@click.option("--format", "-f", is_flag=True, help="Force formatting of staged files")
@click.option("--no-format", "-nf", is_flag=True, help="Skip formatting of staged files")
@click.option("--one-liner", "-o", is_flag=True, help="Generate a single-line commit message")
@click.option("--push", "-p", is_flag=True, help="Push changes to remote after committing")
@click.option(
    "--show-prompt",
    "-s",
    is_flag=True,
    help="Show an abbreviated version of the prompt sent to the LLM",
)
@click.option(
    "--show-prompt-full",
    is_flag=True,
    help="Show the complete prompt sent to the LLM, including full diff",
)
@click.option("--template", help="Path to a custom prompt template file")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-error output")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
@click.option("--hint", "-h", default="", help="Additional context to include in the prompt")
@click.option(
    "--model",
    "-m",
    help="Override the default model (format: 'provider:model_name')",
)
@click.option(
    "--version",
    is_flag=True,
    help="Show the version of the Git Auto Commit (GAC) tool",
)
def main(
    log_level: str,
    quiet: bool,
    yes: bool = False,
    add_all: bool = False,
    format: bool = False,
    no_format: bool = False,
    model: Optional[str] = None,
    one_liner: bool = False,
    show_prompt: bool = False,
    show_prompt_full: bool = False,
    hint: str = "",
    push: bool = False,
    template: Optional[str] = None,
    config: bool = False,
    version: bool = False,
) -> None:
    """Git Auto Commit - Generate commit messages with AI."""
    # Version flag takes precedence over other operations
    if version:
        print(f"Git Auto Commit (GAC) version: {__about__.__version__}")
        sys.exit(0)

    if config:
        from gac.config import run_config_wizard

        result = run_config_wizard()
        if result:
            print_message("Configuration saved successfully!", "notification")
        return

    if format and no_format:
        print_message("Error: --format and --no-format cannot be used together", "error")
        sys.exit(1)

    log_level = log_level.upper()
    numeric_log_level = logging.WARNING
    if log_level == "DEBUG":
        numeric_log_level = logging.DEBUG
    elif log_level == "INFO":
        numeric_log_level = logging.INFO
    elif log_level == "WARNING":
        numeric_log_level = logging.WARNING
    elif log_level == "ERROR":
        numeric_log_level = logging.ERROR

    setup_logging(numeric_log_level, quiet=quiet, force=True)

    result = commit_workflow(
        message=None,
        stage_all=add_all,
        format_files=format or not no_format,
        model=model,
        hint=hint,
        one_liner=one_liner,
        show_prompt=show_prompt or show_prompt_full,
        require_confirmation=not yes,
        push=push,
        quiet=quiet,
        template=template,
    )

    if not result["success"]:
        print_message(result["error"], level="error")
        sys.exit(1)

    # Show success message only when not in quiet mode
    if not quiet:
        print_message("Successfully committed changes with message:", "notification")
        print(result["message"])
        if result.get("pushed"):
            print_message("Changes pushed to remote.", "notification")
    sys.exit(0)


if __name__ == "__main__":
    main()
