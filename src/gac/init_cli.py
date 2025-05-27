"""CLI for initializing GAC configuration interactively."""

from pathlib import Path

import click
import questionary
from dotenv import set_key

GAC_ENV_PATH = Path.home() / ".gac.env"


@click.command()
def init() -> None:
    """Interactively set up $HOME/.gac.env for GAC."""
    click.echo("Welcome to GAC initialization!\n")
    if GAC_ENV_PATH.exists():
        click.echo(f"$HOME/.gac.env already exists at {GAC_ENV_PATH}. Values will be updated.")
    else:
        GAC_ENV_PATH.touch()
        click.echo(f"Created $HOME/.gac.env at {GAC_ENV_PATH}.")

    providers = [
        ("Anthropic", "claude-3-5-haiku-latest"),
        ("Groq", "meta-llama/llama-4-scout-17b-16e-instruct"),
        ("OpenAI", "gpt-4.1-mini"),
        ("OpenRouter", "qwen/qwen3-32b"),
    ]
    provider_names = [p[0] for p in providers]
    provider = questionary.select("Select your provider:", choices=provider_names).ask()
    if not provider:
        click.echo("Provider selection cancelled. Exiting.")
        return
    provider_key = provider.lower()
    model_suggestion = dict(providers)[provider]
    model = questionary.text(f"Enter the model (default: {model_suggestion}):", default=model_suggestion).ask()
    model_to_save = model.strip() if model.strip() else model_suggestion
    set_key(str(GAC_ENV_PATH), "GAC_MODEL", f"{provider_key}:{model_to_save}")
    click.echo(f"Set GAC_MODEL={provider_key}:{model_to_save}")

    # API key (hidden input)
    api_key = questionary.password("Enter your API key (input hidden, can be set later):").ask()
    if api_key:
        set_key(str(GAC_ENV_PATH), f"{provider_key.upper()}_API_KEY", api_key)
        click.echo(f"Set {provider_key.upper()}_API_KEY (hidden)")

    click.echo(f"\nGAC environment setup complete. You can edit {GAC_ENV_PATH} to update values later.")
