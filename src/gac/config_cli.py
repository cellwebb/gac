"""CLI for managing GAC configuration in $HOME/.gac.env."""

import os
from pathlib import Path

import click
from dotenv import load_dotenv, set_key

GAC_ENV_PATH = Path.home() / ".gac.env"


@click.group()
def config():
    """Manage GAC configuration."""
    pass


@config.command()
def show() -> None:
    """Show all current config values."""
    if not GAC_ENV_PATH.exists():
        click.echo("No $HOME/.gac.env found.")
        return
    load_dotenv(GAC_ENV_PATH, override=True)
    with open(GAC_ENV_PATH) as f:
        for line in f:
            click.echo(line.rstrip())


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
