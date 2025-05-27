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
    model = questionary.text(f"Enter the main model (default: {model_suggestion}):", default=model_suggestion).ask()
    model_to_save = model.strip() if model.strip() else model_suggestion
    set_key(str(GAC_ENV_PATH), "GAC_MODEL", f"{provider_key}:{model_to_save}")
    click.echo(f"Set GAC_MODEL={provider_key}:{model_to_save}")

    # API key (hidden input)
    api_key = questionary.password("Enter your API key (input hidden, can be set later):").ask()
    if api_key:
        set_key(str(GAC_ENV_PATH), f"{provider_key.upper()}_API_KEY", api_key)
        click.echo(f"Set {provider_key.upper()}_API_KEY (hidden)")

    # Backup model setup
    setup_backup = questionary.confirm("Would you like to set up a backup model?", default=False).ask()
    if setup_backup:
        backup_provider = questionary.select("Select your backup provider:", choices=provider_names).ask()
        if not backup_provider:
            click.echo("Backup provider selection cancelled.")
        else:
            backup_provider_key = backup_provider.lower()
            backup_model_suggestion = dict(providers)[backup_provider]
            backup_model = questionary.text(
                f"Enter the backup model (default: {backup_model_suggestion}):", default=backup_model_suggestion
            ).ask()
            backup_model_to_save = backup_model.strip() if backup_model.strip() else backup_model_suggestion
            set_key(str(GAC_ENV_PATH), "GAC_BACKUP_MODEL", f"{backup_provider_key}:{backup_model_to_save}")
            click.echo(f"Set GAC_BACKUP_MODEL={backup_provider_key}:{backup_model_to_save}")

            # Ask for backup provider API key if different from main
            if backup_provider_key != provider_key:
                backup_api_key = questionary.password(
                    f"Enter your API key for {backup_provider} (input hidden, can be set later):"
                ).ask()
                if backup_api_key:
                    set_key(str(GAC_ENV_PATH), f"{backup_provider_key.upper()}_API_KEY", backup_api_key)
                    click.echo(f"Set {backup_provider_key.upper()}_API_KEY (hidden)")

    click.echo(f"\nGAC environment setup complete. You can edit {GAC_ENV_PATH} to update values later.")
