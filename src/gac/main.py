#!/usr/bin/env python3
"""Main entry point for GAC."""

import logging
import sys
from typing import Optional

import click

from gac import __about__
from gac.git import commit_workflow, get_git_status_summary
from gac.utils import print_message, setup_logging

logger = logging.getLogger(__name__)

# Flag to track whether main() is being called directly from entry point
# or through cli()
_CALLED_FROM_CLI = False


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
def cli(
    add_all: bool = False,
    config: bool = False,
    log_level: str = "WARNING",
    format: bool = False,
    no_format: bool = False,
    one_liner: bool = False,
    push: bool = False,
    show_prompt: bool = False,
    show_prompt_full: bool = False,
    template: str = None,
    quiet: bool = False,
    yes: bool = False,
    hint: str = "",
    model: str = None,
    version: bool = False,
):
    """Git Auto Commit - Generate commit messages with AI."""
    global _CALLED_FROM_CLI
    _CALLED_FROM_CLI = True

    ctx = click.get_current_context()
    params = ctx.params

    if params.get("version"):
        print(f"Git Auto Commit (GAC) version: {__about__.__version__}")
        sys.exit(0)

    if params.get("config"):
        from gac.config import run_config_wizard

        result = run_config_wizard()
        if result:
            print_message("Configuration saved successfully!", "notification")
        return

    if params.get("format") and params.get("no_format"):
        print_message("Error: --format and --no-format cannot be used together", "error")
        sys.exit(1)

    log_level = params.get("log_level", "WARNING").upper()
    numeric_log_level = logging.WARNING
    if log_level == "DEBUG":
        numeric_log_level = logging.DEBUG
    elif log_level == "INFO":
        numeric_log_level = logging.INFO
    elif log_level == "WARNING":
        numeric_log_level = logging.WARNING
    elif log_level == "ERROR":
        numeric_log_level = logging.ERROR

    quiet = params.get("quiet", False)
    setup_logging(numeric_log_level, quiet=quiet, force=True)

    # Call main directly with the parameters from Click
    main(
        stage_all=params.get("add_all", False),
        format_files=params.get("format", False) or not params.get("no_format", False),
        model=params.get("model"),
        hint=params.get("hint", ""),
        one_liner=params.get("one_liner", False),
        show_prompt=params.get("show_prompt", False) or params.get("show_prompt_full", False),
        require_confirmation=not params.get("yes", False),
        push=params.get("push", False),
        quiet=quiet or params.get("q", False),
        template=params.get("template"),
    )


def main(
    stage_all: bool = False,
    format_files: bool = True,
    model: Optional[str] = None,
    hint: str = "",
    one_liner: bool = False,
    show_prompt: bool = False,
    require_confirmation: bool = True,
    push: bool = False,
    quiet: bool = False,
    template: Optional[str] = None,
) -> None:
    """Main application logic for GAC."""
    # When called directly as a script entry point, we need to parse command line arguments
    # using Click's cli() function
    global _CALLED_FROM_CLI
    if not _CALLED_FROM_CLI:
        # We're being called directly from the entry point script
        cli(standalone_mode=True)
        return

    # Check if we're in a git repository
    git_status = get_git_status_summary()
    if not git_status.get("valid"):
        print_message("Error: Not in a git repository", "error")
        sys.exit(1)

    # Handle combined short flags (like -pya) which Click doesn't parse correctly when combined
    # This ensures flags like -a will be recognized even in combined options like -pya
    has_add_all_flag = False
    for arg in sys.argv:
        if (
            arg == "-a"
            or arg == "--add-all"
            or (arg.startswith("-") and "a" in arg and not arg.startswith("--"))
        ):
            has_add_all_flag = True
            break

    # Check for push flag in combined options as well
    has_push_flag = push
    if not has_push_flag:
        for arg in sys.argv:
            if (
                arg == "-p"
                or arg == "--push"
                or (arg.startswith("-") and "p" in arg and not arg.startswith("--"))
            ):
                has_push_flag = True
                break

    # Check for yes flag in combined options as well
    has_yes_flag = not require_confirmation
    if require_confirmation:
        for arg in sys.argv:
            if (
                arg == "-y"
                or arg == "--yes"
                or (arg.startswith("-") and "y" in arg and not arg.startswith("--"))
            ):
                has_yes_flag = True
                break

    # If we're using add-all flag or via stage_all parameter, skip the staged files check
    if (has_add_all_flag or stage_all) and not git_status.get("has_staged"):
        # We'll continue because the add-all flag will stage all files in the commit workflow
        pass
    elif not git_status.get("has_staged"):
        print_message(
            "Error: No staged changes found. "
            "Stage your changes with git add first or use --add-all",
            "error",
        )
        sys.exit(1)

    # Run the commit workflow with the correctly identified flags
    result = commit_workflow(
        message=None,
        stage_all=stage_all or has_add_all_flag,
        format_files=format_files,
        model=model,
        hint=hint,
        one_liner=one_liner,
        show_prompt=show_prompt,
        require_confirmation=not has_yes_flag,
        push=has_push_flag,
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
        if result.get("pushed", False) is True:
            print_message("Changes pushed to remote.", "notification")
    sys.exit(0)


if __name__ == "__main__":
    # Reset the flag when running as a script
    _CALLED_FROM_CLI = False
    cli()
