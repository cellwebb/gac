import sys
from typing import List, Optional

import click

from gac.errors import GitError, with_error_handling
from gac.git import get_diff, get_staged_files, run_git_command
from gac.preprocess import (
    filter_binary_and_minified,
    preprocess_diff,
    smart_truncate_diff,
)
from gac.utils import print_message, setup_logging


@click.command()
@click.option(
    "--filter/--no-filter",
    default=True,
    help="Filter out binary files, minified files, and lockfiles",
)
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
@click.option(
    "--staged/--unstaged",
    default=True,
    help="Show staged changes (default) or unstaged changes",
)
@click.option(
    "--color/--no-color",
    default=True,
    help="Show colored diff output",
)
@with_error_handling(GitError, "Failed to display diff")
def diff(
    filter: bool,
    truncate: bool,
    max_tokens: Optional[int],
    staged: bool,
    color: bool,
) -> None:
    """
    Display the diff of staged or unstaged changes.

    This command shows the raw diff without generating a commit message.
    """
    logger = setup_logging()
    logger.debug("Running diff command")

    # Check if there are staged changes
    staged_files = get_staged_files()
    if not staged_files and staged:
        print_message("No staged changes found. Use 'git add' to stage changes.", error=True)
        sys.exit(1)

    # Get the diff
    try:
        diff_text = get_diff(staged=staged)
        if not diff_text:
            print_message("No changes to display.", error=True)
            sys.exit(1)
    except GitError as e:
        print_message(f"Error getting diff: {str(e)}", error=True)
        sys.exit(1)

    # Process the diff
    if filter:
        diff_text = filter_binary_and_minified(diff_text)
        if not diff_text:
            print_message("No changes to display after filtering.", error=True)
            sys.exit(1)

    if truncate:
        diff_text = smart_truncate_diff(diff_text, max_tokens=max_tokens)

    # Display the diff
    if color:
        # Use git's colored diff output
        print(diff_text)
    else:
        # Strip ANSI color codes if color is disabled
        # This is a simple approach - a more robust solution would use a library like 'strip-ansi'
        import re

        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        print(ansi_escape.sub("", diff_text))
