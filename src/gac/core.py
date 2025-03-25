#!/usr/bin/env python3
# flake8: noqa: E501
"""Script to automate writing quality commit messages.

This script sends the staged diff to Claude for summarization and suggests a commit message.
It then prompts the user to proceed with the commit, runs pre-commit hooks, and commits the changes.

This script asssumes that your environment has git, black, and isort installed.
It also assumes that your environment has pre-commit installed and configured.

# TODO:
- Remove test mode and just let it connect to Claude?
- Make black and isort optional?
- How to handle pre-commit/git hooks?
- Test coverage
- Add support for custom commit message templates?
- Implement error handling for network failures
- Create a configuration file for user preferences
- Add option to specify commit type (e.g., feat, fix, docs)
- Ask user if they want to commit staged files that have unstaged changes

"""

import logging
import subprocess
from typing import List

import click
from rich.logging import RichHandler

from .config import get_config
from .utils import chat, count_tokens

logger = logging.getLogger(__name__)


def run_subprocess(command: List[str]) -> str:
    logger.debug(f"Running command: `{' '.join(command)}`")
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        error_msg = f"Command failed with exit code {result.returncode}: {result.stderr}"
        logger.error(error_msg)
        raise subprocess.CalledProcessError(
            result.returncode, command, result.stdout, result.stderr
        )
    if result.stdout:
        logger.debug(f"Command output:\n{result.stdout}")
        return result.stdout
    return ""


def get_staged_files() -> List[str]:
    """Get list of filenames of all staged files."""
    logger.debug("Checking staged files...")
    result = run_subprocess(["git", "diff", "--staged", "--name-only"])
    return result.splitlines()


def get_staged_python_files() -> List[str]:
    """Get list of filenames of staged Python files."""
    return [f for f in get_staged_files() if f.endswith(".py")]


def get_existing_staged_python_files() -> List[str]:
    """Get list of filenames of staged Python files that exist on disk."""
    import os

    return [f for f in get_staged_python_files() if os.path.exists(f)]


def commit_changes(message: str) -> None:
    """Commit changes with the given message."""
    try:
        run_subprocess(["git", "commit", "-m", message])
    except subprocess.CalledProcessError as e:
        logger.error(f"Error committing changes: {e}")
        raise


def stage_files(files: List[str]) -> bool:
    """Stage files for commit."""
    result = run_subprocess(["git", "add"] + files)
    logger.info("Files staged.")
    return bool(result)


def run_black() -> bool:
    """Run black code formatter."""
    logger.debug("Identifying Python files for formatting with black...")
    python_files = get_existing_staged_python_files()
    if not python_files:
        logger.info("No existing Python files to format with black.")
        return False
    n_before = len(python_files)
    run_subprocess(["black"] + python_files)
    logger.debug("Checking which files were modified by black...")
    formatted_files = get_staged_python_files()
    n_formatted = n_before - len(formatted_files)
    logger.info(f"Black formatted {n_formatted} files.")
    return n_formatted > 0


def run_isort() -> bool:
    """Run isort import sorter."""
    logger.debug("Identifying Python files for import sorting with isort...")
    python_files = get_existing_staged_python_files()
    if not python_files:
        logger.info("No existing Python files to format with isort.")
        return False
    n_before = len(python_files)
    run_subprocess(["isort"] + python_files)
    logger.debug("Checking which files were modified by isort...")
    formatted_files = get_staged_python_files()
    n_formatted = n_before - len(formatted_files)
    logger.info(f"isort formatted {n_formatted} files.")
    return n_formatted > 0


def send_to_claude(status: str, diff: str) -> str:
    """Send the git status and staged diff to Claude for summarization."""
    config = get_config()
    model = config["model"]

    prompt = f"""Analyze this git status and git diff and write ONLY a commit message in the following format. Do not include any other text, explanation, or commentary.

Format:
[type]: Short summary of changes (50 chars or less)
 - Bullet point details about the changes
 - Another bullet point if needed

[feat/fix/docs/refactor/test/chore/other]: <description>

For larger changes, include bullet points:
[category]: Main description
 - Change 1
 - Change 2
 - Change 3

Git Status:
```
{status}
```

Git Diff:
```
{diff}
```
"""

    logger.info(f"Prompt:\n{prompt}")
    logger.info(f"Prompt length: {len(prompt)} characters")
    logger.info(f"Prompt token count: {count_tokens(prompt, model):,}")

    messages = [{"role": "user", "content": prompt}]
    response = chat(
        messages=messages,
        model=model,
        system="You are a helpful assistant that writes clear, concise git commit messages. Only output the commit message, nothing else.",
    )

    logger.info(f"Response token count: {count_tokens(response, model):,}")
    return response


def main(
    test_mode: bool = False,
    force: bool = False,
    add_all: bool = False,
    no_format: bool = False,
) -> None:
    config = get_config()

    if add_all:
        stage_files(["."])
        logger.info("All changes staged.")

    logger.debug("Checking for staged files to commit...")
    staged_files = get_staged_files()
    if len(staged_files) == 0:
        logger.info("No staged files to commit.")
        return

    if test_mode:
        logger.info("[TEST MODE ENABLED] Using example commit message")
        commit_message = """[TEST MESSAGE] Example commit format
[feat]: This is a test commit message to demonstrate formatting
 - This is a test bullet point
 - Another test bullet point
 - Final test bullet point for demonstration"""
    else:
        logger.debug("Checking for Python files to format...")
        python_files = get_staged_python_files()
        existing_python_files = get_existing_staged_python_files()

        # Only run formatting if enabled and there are Python files
        if existing_python_files and config["use_formatting"] and not no_format:
            run_black()
            logger.debug("Re-staging Python files after black formatting...")
            existing_python_files = get_existing_staged_python_files()
            if existing_python_files:
                stage_files(existing_python_files)
            else:
                logger.info("No existing Python files to re-stage after black.")
            run_isort()
            logger.debug("Re-staging Python files after isort formatting...")
            existing_python_files = get_existing_staged_python_files()
            if existing_python_files:
                stage_files(existing_python_files)
            else:
                logger.info("No existing Python files to re-stage after isort.")

        logger.info("Generating commit message...")
        status = run_subprocess(["git", "status"])
        diff = run_subprocess(["git", "--no-pager", "diff", "--staged"])
        commit_message = send_to_claude(status=status, diff=diff)

    if not commit_message:
        logger.error("Failed to generate commit message.")
        return

    print("\n=== Suggested Commit Message ===")
    print(f"{commit_message}")
    print("===============================\n")

    if force:
        proceed = "y"
    else:
        prompt = "Do you want to proceed with this commit? (y/n): "
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
        prompt = "Do you want to push these changes? (y/n): "
        push = click.prompt(prompt, type=str, default="y").strip().lower()
    if push and push[0] == "y":
        run_subprocess(["git", "push"])
        logger.info("Push complete.")
    else:
        logger.info("Push aborted.")
    return


@click.command()
@click.option("--test", "-t", is_flag=True, help="Run in test mode")
@click.option(
    "--force",
    "-f",
    "-y",
    is_flag=True,
    help="Force commit without user prompting (yes to all prompts)",
)
@click.option("--add-all", "-a", is_flag=True, help="Stage all changes before committing")
@click.option("--quiet", "-q", is_flag=True, help="Reduce output verbosity")
@click.option("--verbose", "-v", is_flag=True, help="Increase output verbosity")
@click.option("--no-format", "-nf", is_flag=True, help="Disable formatting")
def cli(
    test: bool, force: bool, add_all: bool, quiet: bool, verbose: bool, no_format: bool
) -> None:
    """Commit staged changes with an AI-generated commit message."""
    log_level = logging.WARNING if quiet else (logging.DEBUG if verbose else logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        handlers=[RichHandler(rich_tracebacks=True, markup=True)],
    )
    main(test_mode=test, force=force, add_all=add_all, no_format=no_format)


if __name__ == "__main__":
    cli()
