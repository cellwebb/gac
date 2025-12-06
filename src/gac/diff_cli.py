# flake8: noqa: E304

"""Git diff display command for gac.

This module implements the 'gac diff' subcommand which displays git diffs with various
filtering and formatting options. It provides a convenient way to view staged or unstaged
changes, compare commits, and apply smart filtering to focus on meaningful code changes.

Key features:
- Display staged or unstaged changes
- Compare specific commits or branches
- Filter out binary files, minified files, and lockfiles
- Smart truncation of large diffs based on token limits
- Colored output support for better readability
- Integration with gac's preprocessing logic for cleaner diffs

The diff command is particularly useful for:
- Previewing what changes will be included in the commit message
- Reviewing filtered diffs before committing
- Comparing code changes between branches or commits
- Understanding what files have been modified in the staging area
"""

import logging
import sys

import click

from gac.errors import GitError, with_error_handling
from gac.git import get_diff, get_staged_files
from gac.preprocess import (
    filter_binary_and_minified,
    smart_truncate_diff,
    split_diff_into_sections,
)
from gac.utils import print_message, setup_logging


def _diff_implementation(
    filter: bool,
    truncate: bool,
    max_tokens: int | None,
    staged: bool,
    color: bool,
    commit1: str | None = None,
    commit2: str | None = None,
) -> None:
    """Implementation of the diff command logic for easier testing."""
    setup_logging()
    # Get a logger for this module instead of using the return value of setup_logging
    logger = logging.getLogger(__name__)
    logger.debug("Running diff command")

    # If we're comparing specific commits, don't need to check for staged changes
    if not (commit1 or commit2):
        # Check if there are staged changes
        staged_files = get_staged_files()
        if not staged_files and staged:
            print_message("No staged changes found. Use 'git add' to stage changes.", level="error")
            sys.exit(1)

    try:
        diff_text = get_diff(staged=staged, color=color, commit1=commit1, commit2=commit2)
        if not diff_text:
            print_message("No changes to display.", level="error")
            sys.exit(1)
    except GitError as e:
        print_message(f"Error getting diff: {str(e)}", level="error")
        sys.exit(1)

    if filter:
        diff_text = filter_binary_and_minified(diff_text)
        if not diff_text:
            print_message("No changes to display after filtering.", level="error")
            sys.exit(1)

    if truncate:
        # Convert the diff text to the format expected by smart_truncate_diff
        # (list of tuples with (section, score))
        if isinstance(diff_text, str):
            sections = split_diff_into_sections(diff_text)
            scored_sections = [(section, 1.0) for section in sections]
            diff_text = smart_truncate_diff(scored_sections, max_tokens or 1000, "anthropic:claude-3-haiku-latest")

    if color:
        # Use git's colored diff output
        print(diff_text)
    else:
        # Strip ANSI color codes if color is disabled
        # This is a simple approach - a more robust solution would use a library like 'strip-ansi'
        import re

        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        print(ansi_escape.sub("", diff_text))


@click.command(name="diff")
# Content filtering options
@click.option(
    "--filter/--no-filter",
    default=True,
    help="Filter out binary files, minified files, and lockfiles",
)
# Display options
@click.option(
    "--color/--no-color",
    default=True,
    help="Show colored diff output",
)
# Diff source options
@click.option(
    "--staged/--unstaged",
    default=True,
    help="Show staged changes (default) or unstaged changes",
)
# Size control options
@click.option(
    "--truncate/--no-truncate",
    default=True,
    help="Truncate large diffs to a reasonable size",
)
@click.option(
    "--max-tokens",
    default=None,
    type=int,
    help="Maximum number of tokens to include in the diff",
)
@click.argument("commit1", required=False)
@click.argument("commit2", required=False)
@with_error_handling(GitError, "Failed to display diff")
def diff(
    filter: bool,
    truncate: bool,
    max_tokens: int | None,
    staged: bool,
    color: bool,
    commit1: str | None = None,
    commit2: str | None = None,
) -> None:
    """
    Display the diff of staged or unstaged changes.

    This command shows the raw diff without generating a commit message.

    You can also compare specific commits or branches by providing one or two arguments:
        gac diff <commit1> - Shows diff between working tree and <commit1>
        gac diff <commit1> <commit2> - Shows diff between <commit1> and <commit2>

    Commit references can be commit hashes, branch names, or other Git references.
    """
    _diff_implementation(
        filter=filter,
        truncate=truncate,
        max_tokens=max_tokens,
        staged=staged,
        color=color,
        commit1=commit1,
        commit2=commit2,
    )
