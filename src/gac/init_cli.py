"""CLI for initializing gac configuration interactively."""

from pathlib import Path
from typing import cast

import click
import questionary
from dotenv import dotenv_values, set_key, unset_key

from gac.language_cli import configure_language_init_workflow
from gac.model_cli import _configure_model

GAC_ENV_PATH = Path.home() / ".gac.env"


def _prompt_required_text(prompt: str) -> str | None:
    """Prompt until a non-empty string is provided or the user cancels."""
    while True:
        response = questionary.text(prompt).ask()
        if response is None:
            return None
        value = response.strip()
        if value:
            return cast(str, value)
        click.echo("A value is required. Please try again.")


def _load_existing_env() -> dict[str, str]:
    """Ensure the env file exists and return its current values."""
    existing_env: dict[str, str] = {}
    if GAC_ENV_PATH.exists():
        click.echo(f"$HOME/.gac.env already exists at {GAC_ENV_PATH}. Values will be updated.")
        existing_env = {k: v for k, v in dotenv_values(str(GAC_ENV_PATH)).items() if v is not None}
    else:
        GAC_ENV_PATH.touch()
        click.echo(f"Created $HOME/.gac.env at {GAC_ENV_PATH}.")
    return existing_env


def _configure_language(existing_env: dict[str, str]) -> None:
    """Run the language configuration flow using consolidated logic."""
    click.echo("\n")

    # Use the consolidated language configuration from language_cli
    success = configure_language_init_workflow(GAC_ENV_PATH)

    if not success:
        click.echo("Language configuration cancelled or failed.")
    else:
        click.echo("Language configuration completed.")


def _configure_stats(existing_env: dict[str, str], env_path: Path = GAC_ENV_PATH) -> None:
    """Ask the user whether to enable local usage statistics.

    Sets or removes GAC_DISABLE_STATS in the env file. Anything set in the
    env file disables stats; absence means enabled.
    """
    click.echo("\n📊 GAC Stats")
    click.echo(
        "GAC can track local usage statistics — total gacs, commits, tokens, streaks,\n"
        "and per-project / per-model breakdowns. View them anytime with `gac stats`."
    )
    click.echo(f"Data stays on your machine in {Path.home() / '.gac_stats.json'}.")
    click.echo("Nothing is uploaded. There is no telemetry.")

    currently_disabled = "GAC_DISABLE_STATS" in existing_env
    if currently_disabled:
        click.echo("\nStats are currently disabled.")

    response = questionary.confirm(
        "Enable gac stats?",
        default=not currently_disabled,
    ).ask()

    if response is None:
        click.echo("Stats configuration cancelled. Leaving setting unchanged.")
        return

    if response:
        if currently_disabled:
            unset_key(str(env_path), "GAC_DISABLE_STATS")
            existing_env.pop("GAC_DISABLE_STATS", None)
            click.echo("Removed GAC_DISABLE_STATS. Stats enabled.")
        else:
            click.echo("Stats enabled.")
    else:
        set_key(str(env_path), "GAC_DISABLE_STATS", "true")
        existing_env["GAC_DISABLE_STATS"] = "true"
        click.echo("Set GAC_DISABLE_STATS='true'. Stats disabled.")


@click.command()
def init() -> None:
    """Interactively set up $HOME/.gac.env for gac."""
    click.echo("Welcome to gac initialization!\n")

    existing_env = _load_existing_env()

    if not _configure_model(existing_env):
        click.echo("Model configuration cancelled. Exiting.")
        return

    _configure_language(existing_env)

    _configure_stats(existing_env)

    click.echo("\ngac environment setup complete 🎉")
    click.echo("Configuration saved to:")
    click.echo(f"  {GAC_ENV_PATH}")
    click.echo("\nYou can now run 'gac' or 'uvx gac' in any Git repository to generate commit messages.")
    click.echo("Run 'gac --help' to see available options.")
