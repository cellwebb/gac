#!/usr/bin/env python3
# flake8: noqa: E501
"""Script to automate writing quality commit messages.

This script sends the staged diff to Claude for summarization and suggests a commit message.
It then prompts the user to proceed with the commit, runs pre-commit hooks, and commits the changes.

This script asssumes that your environment has git, black, and isort installed.
It also assumes that your environment has pre-commit installed and configured.

TODO:
- Remove test mode and just let it connect to Claude?
"""

import logging
import subprocess
from pdb import run
from typing import List

import click
from rich.logging import RichHandler

from .utils import chat, count_tokens

logger = logging.getLogger(__name__)


MODEL = "anthropic:claude-3-5-haiku-latest"


def run_subprocess(command: List[str], quiet: bool = False) -> str:
    logger.info(f"Running command: `{' '.join(command)}`")
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        logger.error(f"Error running command: `{result.stderr}`")
        return ""

    if result.stdout:
        if not quiet:
            logger.info(f"Command output:\n{result.stdout}")
        else:
            logger.debug(f"Command output:\n{result.stdout}")
        return result.stdout

    return ""


def git_status(quiet: bool = False) -> str:
    return run_subprocess(["git", "status"], quiet=quiet)


def git_diff_staged(quiet: bool = False) -> str:
    return run_subprocess(["git", "--no-pager", "diff", "--staged"], quiet=quiet)


def get_staged_filenames(quiet: bool = True) -> List[str]:
    result = run_subprocess(["git", "diff", "--staged", "--name-only"], quiet=quiet)
    return result.splitlines()


def get_staged_python_files(quiet: bool = True) -> List[str]:
    return [f for f in get_staged_filenames(quiet=quiet) if f.endswith(".py")]


def commit_changes(message: str, quiet: bool = False) -> None:
    """Commit changes with the given message."""
    try:
        run_subprocess(["git", "commit", "-m", message], quiet=quiet)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error committing changes: {e}")
        raise


def stage_files(files: List[str], quiet: bool = False) -> bool:
    """Stage files for commit."""
    result = run_subprocess(["git", "add"] + files, quiet=quiet)
    if not quiet:
        logger.info("Files staged.")
    return bool(result)


def run_black(quiet: bool = False) -> bool:
    """Run black code formatter."""
    python_files = get_staged_python_files()
    n_before = len(python_files)
    run_subprocess(["black"] + python_files, quiet=quiet)
    python_files = get_staged_python_files()
    n_formatted = n_before - len(python_files)

    if not quiet:
        logger.info(f"Black formatted {n_formatted} files.")
    return n_formatted > 0


def run_isort(quiet: bool = False) -> bool:
    """Run isort import sorter."""
    python_files = get_staged_python_files()
    n_before = len(python_files)
    run_subprocess(["isort"] + python_files, quiet=quiet)
    formatted_files = get_staged_python_files()
    n_formatted = n_before - len(formatted_files)

    if not quiet:
        logger.info(f"isort formatted {n_formatted} files.")
    return n_formatted > 0


def send_to_claude(status: str, diff: str) -> str:
    """Send the git status and staged diff to Claude for summarization."""
    prompt = f"""Analyze this git status and git diff and write ONLY a commit message in the following format. Do not include any other text, explanation, or commentary.

[feat/fix/docs/refactor/test/chore/other]: <description>

For larger changes, include bullet points:
[category]: Main description
 - Change 1
 - Change 2
 - Change 3

Here is the git status to analyze:

```
{status}
```

Here is the diff to analyze:

```
{diff}
```
"""
    logger.info(f"Prompt:\n{prompt}")
    logger.info(f"Prompt length: {len(prompt)} characters")
    logger.info(f"Prompt token count: {count_tokens(prompt, MODEL):,}")

    messages = [{"role": "user", "content": prompt}]
    response = chat(
        messages,
        model=MODEL,
        system="You are a helpful assistant that writes clear, concise git commit messages. Only output the commit message, nothing else.",
    )
    logger.info(f"Response token count: {count_tokens(response, MODEL):,}")
    return response


def main(test_mode: bool = False, force: bool = False, add_all: bool = False) -> None:
    if add_all:
        stage_files(["."])
        logger.info("All changes staged.")

    staged_files = get_staged_filenames()
    if len(staged_files) == 0:
        logger.info("No staged files to commit.")
        return

    if test_mode:
        logger.info("[TEST MODE ENABLED] Using example commit message")
        commit_message = """[TEST MESSAGE] Example commit format
[feat]: This is a test commit message to demonstrate formatting
 - This is a test bullet point
 - Another test bullet point to show structure
 - Final test bullet point for demonstration"""
    else:
        python_files = get_staged_python_files()

        if python_files:
            run_black()
            stage_files(python_files)
            run_isort()
            stage_files(python_files)

        commit_message = send_to_claude(status=git_status(), diff=git_diff_staged())

    if not commit_message:
        logger.error("Failed to generate commit message.")
        return

    if force:
        proceed = "y"
    else:
        prompt = (
            f"Suggested Commit Message:\n{commit_message}\n\n"
            "Do you want to proceed with this commit? (y/n): "
        )
        proceed = click.prompt(prompt, type=str, default="y").strip().lower()

    if not proceed or proceed[0] != "y":
        logger.info("Commit aborted.")
        return

    if test_mode:
        logger.info("[TEST MODE] Commit simulation completed. No actual commit was made.")
        return

    commit_changes(commit_message)

    if force:
        push = "y"
    else:
        push = (
            click.prompt("Do you want to push these changes? (y/n): ", type=str, default="y")
            .strip()
            .lower()
        )
    if push and push[0] == "y":
        run_subprocess(["git", "push"])
        logger.info("Push complete.")
        logger.debug(git_status())
    else:
        logger.info("Push aborted.")
    return


@click.command()
@click.option("--test", "-t", is_flag=True, help="Run in test mode with example commit messages")
@click.option(
    "--force",
    "-f",
    "-y",
    is_flag=True,
    help="Force commit without user prompting (yes to all prompts)",
)
@click.option("--add-all", "-a", is_flag=True, help="Stage all changes before committing")
def cli(test: bool, force: bool, add_all: bool) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[RichHandler(rich_tracebacks=True, markup=True)],
    )
    main(test_mode=test, force=force, add_all=add_all)


if __name__ == "__main__":
    cli()
