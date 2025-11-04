"""CLI for initializing gac configuration interactively."""

import os
from pathlib import Path

import click
import questionary
from dotenv import dotenv_values, load_dotenv, set_key

from gac.constants import Languages

GAC_ENV_PATH = Path.home() / ".gac.env"


def _should_show_rtl_warning_for_init() -> bool:
    """Check if RTL warning should be shown based on init's GAC_ENV_PATH.

    Returns:
        True if warning should be shown, False if user previously confirmed
    """
    if GAC_ENV_PATH.exists():
        load_dotenv(GAC_ENV_PATH)
        rtl_confirmed = os.getenv("GAC_RTL_CONFIRMED", "false").lower() in ("true", "1", "yes", "on")
        return not rtl_confirmed
    return True  # Show warning if no config exists


def _show_rtl_warning_for_init(language_name: str) -> bool:
    """Show RTL language warning for init command and save preference to GAC_ENV_PATH.

    Args:
        language_name: Name of the RTL language

    Returns:
        True if user wants to proceed, False if they cancel
    """

    terminal_width = 80  # Use default width
    title = "⚠️  RTL Language Detected".center(terminal_width)

    click.echo()
    click.echo(click.style(title, fg="yellow", bold=True))
    click.echo()
    click.echo("Right-to-left (RTL) languages may not display correctly in gac due to terminal limitations.")
    click.echo("However, the commit messages will work fine and should be readable in Git clients")
    click.echo("that properly support RTL text (like most web interfaces and modern tools).\n")

    proceed = questionary.confirm("Do you want to proceed anyway?").ask()
    if proceed:
        # Remember that user has confirmed RTL acceptance
        set_key(str(GAC_ENV_PATH), "GAC_RTL_CONFIRMED", "true")
        click.echo("✓ RTL preference saved - you won't see this warning again")
    return proceed if proceed is not None else False


def _prompt_required_text(prompt: str) -> str | None:
    """Prompt until a non-empty string is provided or the user cancels."""
    while True:
        response = questionary.text(prompt).ask()
        if response is None:
            return None
        value = response.strip()
        if value:
            return value  # type: ignore[no-any-return]
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


def _configure_model(existing_env: dict[str, str]) -> bool:
    """Run the provider/model/API key configuration flow."""
    providers = [
        ("Anthropic", "claude-haiku-4-5"),
        ("Cerebras", "zai-glm-4.6"),
        ("Chutes", "zai-org/GLM-4.6-FP8"),
        ("Custom (Anthropic)", ""),
        ("Custom (OpenAI)", ""),
        ("DeepSeek", "deepseek-chat"),
        ("Fireworks", "accounts/fireworks/models/gpt-oss-20b"),
        ("Gemini", "gemini-2.5-flash"),
        ("Groq", "meta-llama/llama-4-maverick-17b-128e-instruct"),
        ("LM Studio", "gemma3"),
        ("MiniMax", "MiniMax-M2"),
        ("Mistral", "mistral-small-latest"),
        ("Ollama", "gemma3"),
        ("OpenAI", "gpt-4.1-mini"),
        ("OpenRouter", "openrouter/auto"),
        ("Streamlake", ""),
        ("Synthetic", "hf:zai-org/GLM-4.6"),
        ("Together AI", "openai/gpt-oss-20B"),
        ("Z.AI", "glm-4.5-air"),
        ("Z.AI Coding", "glm-4.6"),
    ]
    provider_names = [p[0] for p in providers]
    provider = questionary.select("Select your provider:", choices=provider_names).ask()
    if not provider:
        click.echo("Provider selection cancelled. Exiting.")
        return False
    provider_key = provider.lower().replace(".", "").replace(" ", "-").replace("(", "").replace(")", "")

    is_ollama = provider_key == "ollama"
    is_lmstudio = provider_key == "lm-studio"
    is_streamlake = provider_key == "streamlake"
    is_zai = provider_key in ("zai", "zai-coding")
    is_custom_anthropic = provider_key == "custom-anthropic"
    is_custom_openai = provider_key == "custom-openai"

    if is_streamlake:
        endpoint_id = _prompt_required_text("Enter the Streamlake inference endpoint ID (required):")
        if endpoint_id is None:
            click.echo("Streamlake configuration cancelled. Exiting.")
            return False
        model_to_save = endpoint_id
    else:
        model_suggestion = dict(providers)[provider]
        if model_suggestion == "":
            model_prompt = "Enter the model (required):"
        else:
            model_prompt = f"Enter the model (default: {model_suggestion}):"
        model = questionary.text(model_prompt, default=model_suggestion).ask()
        if model is None:
            click.echo("Model entry cancelled. Exiting.")
            return False
        model_to_save = model.strip() if model.strip() else model_suggestion

    set_key(str(GAC_ENV_PATH), "GAC_MODEL", f"{provider_key}:{model_to_save}")
    click.echo(f"Set GAC_MODEL={provider_key}:{model_to_save}")

    if is_custom_anthropic:
        base_url = _prompt_required_text("Enter the custom Anthropic-compatible base URL (required):")
        if base_url is None:
            click.echo("Custom Anthropic base URL entry cancelled. Exiting.")
            return False
        set_key(str(GAC_ENV_PATH), "CUSTOM_ANTHROPIC_BASE_URL", base_url)
        click.echo(f"Set CUSTOM_ANTHROPIC_BASE_URL={base_url}")

        api_version = questionary.text(
            "Enter the API version (optional, press Enter for default: 2023-06-01):", default="2023-06-01"
        ).ask()
        if api_version and api_version != "2023-06-01":
            set_key(str(GAC_ENV_PATH), "CUSTOM_ANTHROPIC_VERSION", api_version)
            click.echo(f"Set CUSTOM_ANTHROPIC_VERSION={api_version}")
    elif is_custom_openai:
        base_url = _prompt_required_text("Enter the custom OpenAI-compatible base URL (required):")
        if base_url is None:
            click.echo("Custom OpenAI base URL entry cancelled. Exiting.")
            return False
        set_key(str(GAC_ENV_PATH), "CUSTOM_OPENAI_BASE_URL", base_url)
        click.echo(f"Set CUSTOM_OPENAI_BASE_URL={base_url}")
    elif is_ollama:
        url_default = "http://localhost:11434"
        url = questionary.text(f"Enter the Ollama API URL (default: {url_default}):", default=url_default).ask()
        if url is None:
            click.echo("Ollama URL entry cancelled. Exiting.")
            return False
        url_to_save = url.strip() if url.strip() else url_default
        set_key(str(GAC_ENV_PATH), "OLLAMA_API_URL", url_to_save)
        click.echo(f"Set OLLAMA_API_URL={url_to_save}")
    elif is_lmstudio:
        url_default = "http://localhost:1234"
        url = questionary.text(f"Enter the LM Studio API URL (default: {url_default}):", default=url_default).ask()
        if url is None:
            click.echo("LM Studio URL entry cancelled. Exiting.")
            return False
        url_to_save = url.strip() if url.strip() else url_default
        set_key(str(GAC_ENV_PATH), "LMSTUDIO_API_URL", url_to_save)
        click.echo(f"Set LMSTUDIO_API_URL={url_to_save}")

    # Determine API key name based on provider
    if is_lmstudio:
        api_key_name = "LMSTUDIO_API_KEY"
    elif is_zai:
        api_key_name = "ZAI_API_KEY"
    elif is_custom_anthropic:
        api_key_name = "CUSTOM_ANTHROPIC_API_KEY"
    elif is_custom_openai:
        api_key_name = "CUSTOM_OPENAI_API_KEY"
    else:
        api_key_name = f"{provider_key.upper()}_API_KEY"

    # Check if API key already exists
    existing_key = existing_env.get(api_key_name)

    if existing_key:
        # Key exists - offer options
        click.echo(f"\n{api_key_name} is already configured.")
        action = questionary.select(
            "What would you like to do?",
            choices=[
                "Keep existing key",
                "Enter new key",
            ],
        ).ask()

        if action is None:
            click.echo("API key configuration cancelled. Keeping existing key.")
        elif action.startswith("Keep existing"):
            click.echo(f"Keeping existing {api_key_name}")
        elif action.startswith("Enter new"):
            api_key = questionary.password("Enter your new API key (input hidden):").ask()
            if api_key and api_key.strip():
                set_key(str(GAC_ENV_PATH), api_key_name, api_key)
                click.echo(f"Updated {api_key_name} (hidden)")
            else:
                click.echo(f"No key entered. Keeping existing {api_key_name}")
    else:
        # No existing key - prompt for new one
        api_key_prompt = "Enter your API key (input hidden, can be set later):"
        if is_ollama or is_lmstudio:
            click.echo(
                "This provider typically runs locally. API keys are optional unless your instance requires authentication."
            )
            api_key_prompt = "Enter your API key (optional, press Enter to skip):"

        api_key = questionary.password(api_key_prompt).ask()
        if api_key and api_key.strip():
            set_key(str(GAC_ENV_PATH), api_key_name, api_key)
            click.echo(f"Set {api_key_name} (hidden)")
        elif is_ollama or is_lmstudio:
            click.echo("Skipping API key. You can add one later if needed.")
        else:
            click.echo("No API key entered. You can add one later by editing ~/.gac.env")

    return True


def _configure_language(existing_env: dict[str, str]) -> None:
    """Run the language configuration flow."""
    from gac.language_cli import is_rtl_text

    click.echo("\n")
    existing_language = existing_env.get("GAC_LANGUAGE")

    if existing_language:
        # Language already configured - offer options
        existing_translate = existing_env.get("GAC_TRANSLATE_PREFIXES", "false")
        translate_status = "with translated prefixes" if existing_translate == "true" else "with English prefixes"
        click.echo(f"Language is already configured: {existing_language} ({translate_status})")

        action = questionary.select(
            "What would you like to do?",
            choices=[
                "Keep existing language",
                "Select new language",
            ],
        ).ask()

        if action is None or action.startswith("Keep existing"):
            if action is None:
                click.echo("Language configuration cancelled. Keeping existing language.")
            else:
                click.echo(f"Keeping existing language: {existing_language}")
        elif action.startswith("Select new"):
            # Proceed with language selection
            display_names = [lang[0] for lang in Languages.LANGUAGES]
            language_selection = questionary.select(
                "Select a language for commit messages:",
                choices=display_names,
                use_shortcuts=True,
                use_arrow_keys=True,
                use_jk_keys=False,
            ).ask()

            if not language_selection:
                click.echo("Language selection cancelled. Keeping existing language.")
            elif language_selection == "English":
                set_key(str(GAC_ENV_PATH), "GAC_LANGUAGE", "English")
                set_key(str(GAC_ENV_PATH), "GAC_TRANSLATE_PREFIXES", "false")
                click.echo("Set GAC_LANGUAGE=English")
                click.echo("Set GAC_TRANSLATE_PREFIXES=false")
            else:
                # Handle custom input
                if language_selection == "Custom":
                    custom_language = questionary.text(
                        "Enter the language name (e.g., 'Spanish', 'Français', '日本語'):"
                    ).ask()
                    if not custom_language or not custom_language.strip():
                        click.echo("No language entered. Keeping existing language.")
                        language_value = None
                    else:
                        language_value = custom_language.strip()

                        # Check if the custom language appears to be RTL
                        if is_rtl_text(language_value):
                            if not _should_show_rtl_warning_for_init():
                                click.echo(
                                    f"\nℹ️  Using RTL language {language_value} (RTL warning previously confirmed)"
                                )
                            else:
                                if not _show_rtl_warning_for_init(language_value):
                                    click.echo("Language selection cancelled. Keeping existing language.")
                                    language_value = None
                else:
                    # Find the English name for the selected language
                    language_value = next(lang[1] for lang in Languages.LANGUAGES if lang[0] == language_selection)

                    # Check if predefined language is RTL
                    if is_rtl_text(language_value):
                        if not _should_show_rtl_warning_for_init():
                            click.echo(f"\nℹ️  Using RTL language {language_value} (RTL warning previously confirmed)")
                        else:
                            if not _show_rtl_warning_for_init(language_value):
                                click.echo("Language selection cancelled. Keeping existing language.")
                                language_value = None

                if language_value:
                    # Ask about prefix translation
                    prefix_choice = questionary.select(
                        "How should conventional commit prefixes be handled?",
                        choices=[
                            "Keep prefixes in English (feat:, fix:, etc.)",
                            f"Translate prefixes into {language_value}",
                        ],
                    ).ask()

                    if not prefix_choice:
                        click.echo("Prefix translation selection cancelled. Using English prefixes.")
                        translate_prefixes = False
                    else:
                        translate_prefixes = prefix_choice.startswith("Translate prefixes")

                    # Set the language and prefix translation preference
                    set_key(str(GAC_ENV_PATH), "GAC_LANGUAGE", language_value)
                    set_key(str(GAC_ENV_PATH), "GAC_TRANSLATE_PREFIXES", "true" if translate_prefixes else "false")
                    click.echo(f"Set GAC_LANGUAGE={language_value}")
                    click.echo(f"Set GAC_TRANSLATE_PREFIXES={'true' if translate_prefixes else 'false'}")
    else:
        # No existing language - proceed with normal flow
        display_names = [lang[0] for lang in Languages.LANGUAGES]
        language_selection = questionary.select(
            "Select a language for commit messages:",
            choices=display_names,
            use_shortcuts=True,
            use_arrow_keys=True,
            use_jk_keys=False,
        ).ask()

        if not language_selection:
            click.echo("Language selection cancelled. Using English (default).")
        elif language_selection == "English":
            set_key(str(GAC_ENV_PATH), "GAC_LANGUAGE", "English")
            set_key(str(GAC_ENV_PATH), "GAC_TRANSLATE_PREFIXES", "false")
            click.echo("Set GAC_LANGUAGE=English")
            click.echo("Set GAC_TRANSLATE_PREFIXES=false")
        else:
            # Handle custom input
            if language_selection == "Custom":
                custom_language = questionary.text(
                    "Enter the language name (e.g., 'Spanish', 'Français', '日本語'):"
                ).ask()
                if not custom_language or not custom_language.strip():
                    click.echo("No language entered. Using English (default).")
                    language_value = None
                else:
                    language_value = custom_language.strip()

                    # Check if the custom language appears to be RTL
                    if is_rtl_text(language_value):
                        if not _should_show_rtl_warning_for_init():
                            click.echo(f"\nℹ️  Using RTL language {language_value} (RTL warning previously confirmed)")
                        else:
                            if not _show_rtl_warning_for_init(language_value):
                                click.echo("Language selection cancelled. Using English (default).")
                                language_value = None
            else:
                # Find the English name for the selected language
                language_value = next(lang[1] for lang in Languages.LANGUAGES if lang[0] == language_selection)

                # Check if predefined language is RTL
                if is_rtl_text(language_value):
                    if not _should_show_rtl_warning_for_init():
                        click.echo(f"\nℹ️  Using RTL language {language_value} (RTL warning previously confirmed)")
                    else:
                        if not _show_rtl_warning_for_init(language_value):
                            click.echo("Language selection cancelled. Using English (default).")
                            language_value = None

            if language_value:
                # Ask about prefix translation
                prefix_choice = questionary.select(
                    "How should conventional commit prefixes be handled?",
                    choices=[
                        "Keep prefixes in English (feat:, fix:, etc.)",
                        f"Translate prefixes into {language_value}",
                    ],
                ).ask()

                if not prefix_choice:
                    click.echo("Prefix translation selection cancelled. Using English prefixes.")
                    translate_prefixes = False
                else:
                    translate_prefixes = prefix_choice.startswith("Translate prefixes")

                # Set the language and prefix translation preference
                set_key(str(GAC_ENV_PATH), "GAC_LANGUAGE", language_value)
                set_key(str(GAC_ENV_PATH), "GAC_TRANSLATE_PREFIXES", "true" if translate_prefixes else "false")
                click.echo(f"Set GAC_LANGUAGE={language_value}")
                click.echo(f"Set GAC_TRANSLATE_PREFIXES={'true' if translate_prefixes else 'false'}")

    return


@click.command()
def init() -> None:
    """Interactively set up $HOME/.gac.env for gac."""
    click.echo("Welcome to gac initialization!\n")

    existing_env = _load_existing_env()
    if not _configure_model(existing_env):
        return
    _configure_language(existing_env)

    click.echo(f"\ngac environment setup complete. You can edit {GAC_ENV_PATH} to update values later.")


@click.command()
def model() -> None:
    """Interactively update provider/model/API key without language prompts."""
    click.echo("Welcome to gac model configuration!\n")

    existing_env = _load_existing_env()
    if not _configure_model(existing_env):
        return

    click.echo(f"\nModel configuration complete. You can edit {GAC_ENV_PATH} to update values later.")
