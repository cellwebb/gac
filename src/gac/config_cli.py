"""CLI for managing gac configuration in $HOME/.gac.env."""

import os
from pathlib import Path

import click
from dotenv import load_dotenv, set_key

GAC_ENV_PATH = Path.home() / ".gac.env"


@click.group()
def config() -> None:
    """Manage gac configuration."""
    pass


@config.command()
def show() -> None:
    """Show all current config values."""
    from dotenv import dotenv_values

    project_env_path = Path(".gac.env")
    user_exists = GAC_ENV_PATH.exists()
    project_exists = project_env_path.exists()

    if not user_exists and not project_exists:
        click.echo("No $HOME/.gac.env found.")
        click.echo("No project-level .gac.env found.")
        return

    if user_exists:
        click.echo(f"User config ({GAC_ENV_PATH}):")
        user_config = dotenv_values(str(GAC_ENV_PATH))
        for key, value in sorted(user_config.items()):
            if value is not None:
                if any(sensitive in key.lower() for sensitive in ["key", "token", "secret"]):
                    display_value = "***hidden***"
                else:
                    display_value = value
                click.echo(f"  {key}={display_value}")
    else:
        click.echo("No $HOME/.gac.env found.")

    if project_exists:
        if user_exists:
            click.echo("")
        click.echo("Project config (./.gac.env):")
        project_config = dotenv_values(str(project_env_path))
        for key, value in sorted(project_config.items()):
            if value is not None:
                if any(sensitive in key.lower() for sensitive in ["key", "token", "secret"]):
                    display_value = "***hidden***"
                else:
                    display_value = value
                click.echo(f"  {key}={display_value}")
        click.echo("")
        click.echo("Note: Project-level .gac.env overrides $HOME/.gac.env values for any duplicated variables.")
    else:
        click.echo("No project-level .gac.env found.")


@config.command()
@click.argument("key")
@click.argument("value")
def set(key: str, value: str) -> None:
    """Set a config KEY to VALUE in $HOME/.gac.env."""
    GAC_ENV_PATH.touch(exist_ok=True)
    set_key(str(GAC_ENV_PATH), key, value)
    click.echo(f"Set {key} in $HOME/.gac.env")


@config.command()
@click.argument("key")
def get(key: str) -> None:
    """Get a config value by KEY."""
    load_dotenv(GAC_ENV_PATH, override=True)
    value = os.getenv(key)
    if value is None:
        click.echo(f"{key} not set.")
    else:
        click.echo(value)


@config.command()
@click.argument("key")
def unset(key: str) -> None:
    """Remove a config KEY from $HOME/.gac.env."""
    if not GAC_ENV_PATH.exists():
        click.echo("No $HOME/.gac.env found.")
        return
    lines = GAC_ENV_PATH.read_text().splitlines()
    new_lines = [line for line in lines if not line.strip().startswith(f"{key}=")]
    GAC_ENV_PATH.write_text("\n".join(new_lines) + "\n")
    click.echo(f"Unset {key} in $HOME/.gac.env")
