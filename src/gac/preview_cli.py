# flake8: noqa: E304

"""CLI for previewing commit messages based on git diffs."""

from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel

from gac.ai import generate_with_fallback
from gac.config import load_config
from gac.errors import AIError
from gac.git import run_git_command
from gac.prompt import build_prompt, clean_commit_message


@click.command(name="preview")
@click.argument("first_hash")
@click.argument("second_hash", required=False)

# Commit message options
@click.option("--one-liner", "-o", is_flag=True, help="Generate a single-line commit message")
@click.option("--hint", "-h", default="", help="Additional context to include in the prompt")
@click.option("--show-prompt", "-s", is_flag=True, help="Show the prompt sent to the LLM")

# Model options
@click.option("--model", "-m", help="Override the default model (format: 'provider:model_name')")

# Output options
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-error output")
def preview(
    first_hash: str,
    second_hash: Optional[str] = None,
    one_liner: bool = False,
    hint: str = "",
    model: Optional[str] = None,
    quiet: bool = False,
    show_prompt: bool = False,
) -> None:
    """Generate a commit message preview based on diff between commits or working tree."""
    config = load_config()
    if model is None:
        model = config["model"]
        if model is None:
            raise click.ClickException(
                "No model specified. Please set the GAC_MODEL environment variable or use --model."
            )
    backup_model = config["backup_model"]
    temperature = config["temperature"]
    max_output_tokens = config["max_output_tokens"]
    max_retries = config["max_retries"]

    # ensure we're in a git repo
    try:
        run_git_command(["rev-parse", "--show-toplevel"])
    except Exception:
        raise click.ClickException("Not in a git repository")

    status = run_git_command(["status"])
    # compare diff between hashes or commit and working tree
    if second_hash:
        diff = run_git_command(["diff", first_hash, second_hash])
    else:
        diff = run_git_command(["diff", first_hash])

    prompt = build_prompt(
        status=status,
        diff=diff,
        one_liner=one_liner,
        hint=hint,
        model=model,
    )
    if show_prompt:
        console = Console()
        console.print(
            Panel(
                prompt,
                title="Prompt for LLM",
                border_style="bright_blue",
            )
        )
    try:
        commit_message = generate_with_fallback(
            primary_model=model,
            prompt=prompt,
            backup_model=backup_model,
            temperature=temperature,
            max_tokens=max_output_tokens,
            max_retries=max_retries,
            quiet=quiet,
        )
    except AIError as e:
        raise click.ClickException(str(e))

    commit_message = clean_commit_message(commit_message)
    console = Console()
    console.print("[bold green]Preview commit message:[/bold green]")
    console.print(Panel(commit_message, title="Commit Message Preview", border_style="cyan"))
