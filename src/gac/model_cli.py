"""CLI for managing gac model configuration in $HOME/.gac.env."""

import os
from pathlib import Path
from typing import cast

import click
import questionary
from dotenv import dotenv_values, load_dotenv, set_key

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
        return True
    else:
        click.echo("RTL language setup cancelled.")
        return False


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


def _configure_model(existing_env: dict[str, str]) -> bool:
    """Run the provider/model/API key configuration flow."""
    providers = [
        ("Anthropic", "claude-haiku-4-5"),
        ("Azure OpenAI", "gpt-5-mini"),
        ("Cerebras", "zai-glm-4.7"),
        ("Chutes", "zai-org/GLM-4.7-TEE"),
        ("Claude Code (OAuth)", "claude-sonnet-4-5"),
        ("Custom (Anthropic)", ""),
        ("Custom (OpenAI)", ""),
        ("DeepSeek", "deepseek-chat"),
        ("Fireworks", "fireworks/glm-4p7"),
        ("Gemini", "gemini-3-flash-preview"),
        ("Groq", "openai/gpt-oss-120b"),
        ("Kimi for Coding", "kimi-for-coding"),
        ("LM Studio", "gemma3"),
        ("MiniMax.io", "MiniMax-M2.1"),
        ("Mistral", "devstral-2512"),
        ("Moonshot AI", "kimi-k2-thinking-turbo"),
        ("Ollama", "gemma3"),
        ("OpenAI", "gpt-5-mini"),
        ("OpenRouter", "openrouter/auto"),
        ("Qwen.ai (OAuth)", "qwen3-coder-plus"),
        ("Replicate", "openai/gpt-oss-120b"),
        ("Streamlake", ""),
        ("Synthetic.new", "hf:zai-org/GLM-4.7"),
        ("Together AI", "openai/gpt-oss-120B"),
        ("Z.AI", "glm-4.7"),
        ("Z.AI Coding", "glm-4.7"),
    ]
    provider_names = [p[0] for p in providers]
    provider = questionary.select(
        "Select your provider:", choices=provider_names, use_shortcuts=True, use_arrow_keys=True, use_jk_keys=False
    ).ask()
    if not provider:
        click.echo("Provider selection cancelled. Exiting.")
        return False
    provider_key = provider.lower().replace(".", "").replace(" ", "-").replace("(", "").replace(")", "")

    is_azure_openai = provider_key == "azure-openai"
    is_claude_code = provider_key == "claude-code-oauth"
    is_custom_anthropic = provider_key == "custom-anthropic"
    is_custom_openai = provider_key == "custom-openai"
    is_lmstudio = provider_key == "lm-studio"
    is_ollama = provider_key == "ollama"
    is_qwen = provider_key == "qwenai-oauth"
    is_streamlake = provider_key == "streamlake"
    is_zai = provider_key in ("zai", "zai-coding")

    if provider_key == "claude-code-oauth":
        provider_key = "claude-code"
    elif provider_key == "kimi-for-coding":
        provider_key = "kimi-coding"
    elif provider_key == "minimaxio":
        provider_key = "minimax"
    elif provider_key == "moonshot-ai":
        provider_key = "moonshot"
    elif provider_key == "qwenai-oauth":
        provider_key = "qwen"
    elif provider_key == "syntheticnew":
        provider_key = "synthetic"

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
    elif is_azure_openai:
        # Check for existing endpoint
        existing_endpoint = existing_env.get("AZURE_OPENAI_ENDPOINT")
        if existing_endpoint:
            click.echo(f"\nAZURE_OPENAI_ENDPOINT is already configured: {existing_endpoint}")
            endpoint_action = questionary.select(
                "What would you like to do?",
                choices=[
                    "Keep existing endpoint",
                    "Enter new endpoint",
                ],
                use_shortcuts=True,
                use_arrow_keys=True,
                use_jk_keys=False,
            ).ask()

            if endpoint_action == "Enter new endpoint":
                endpoint = _prompt_required_text("Enter the Azure OpenAI endpoint (required):")
                if endpoint is None:
                    click.echo("Azure OpenAI endpoint entry cancelled. Exiting.")
                    return False
                set_key(str(GAC_ENV_PATH), "AZURE_OPENAI_ENDPOINT", endpoint)
                click.echo(f"Set AZURE_OPENAI_ENDPOINT={endpoint}")
            else:
                endpoint = existing_endpoint
                click.echo(f"Keeping existing AZURE_OPENAI_ENDPOINT={endpoint}")
        else:
            endpoint = _prompt_required_text("Enter the Azure OpenAI endpoint (required):")
            if endpoint is None:
                click.echo("Azure OpenAI endpoint entry cancelled. Exiting.")
                return False
            set_key(str(GAC_ENV_PATH), "AZURE_OPENAI_ENDPOINT", endpoint)
            click.echo(f"Set AZURE_OPENAI_ENDPOINT={endpoint}")

        # Check for existing API version
        existing_api_version = existing_env.get("AZURE_OPENAI_API_VERSION")
        if existing_api_version:
            click.echo(f"\nAZURE_OPENAI_API_VERSION is already configured: {existing_api_version}")
            version_action = questionary.select(
                "What would you like to do?",
                choices=[
                    "Keep existing version",
                    "Enter new version",
                ],
                use_shortcuts=True,
                use_arrow_keys=True,
                use_jk_keys=False,
            ).ask()

            if version_action == "Enter new version":
                api_version = questionary.text(
                    "Enter the Azure OpenAI API version (required, e.g., 2025-01-01-preview):",
                    default="2025-01-01-preview",
                ).ask()
                if api_version is None or not api_version.strip():
                    click.echo("Azure OpenAI API version entry cancelled. Exiting.")
                    return False
                api_version = api_version.strip()
                set_key(str(GAC_ENV_PATH), "AZURE_OPENAI_API_VERSION", api_version)
                click.echo(f"Set AZURE_OPENAI_API_VERSION={api_version}")
            else:
                api_version = existing_api_version
                click.echo(f"Keeping existing AZURE_OPENAI_API_VERSION={api_version}")
        else:
            api_version = questionary.text(
                "Enter the Azure OpenAI API version (required, e.g., 2025-01-01-preview):", default="2025-01-01-preview"
            ).ask()
            if api_version is None or not api_version.strip():
                click.echo("Azure OpenAI API version entry cancelled. Exiting.")
                return False
            api_version = api_version.strip()
            set_key(str(GAC_ENV_PATH), "AZURE_OPENAI_API_VERSION", api_version)
            click.echo(f"Set AZURE_OPENAI_API_VERSION={api_version}")
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

    # Handle Claude Code OAuth separately
    if is_claude_code:
        from gac.oauth.claude_code import authenticate_and_save
        from gac.oauth.token_store import TokenStore

        token_store = TokenStore()
        existing_token_data = token_store.get_token("claude-code")
        if existing_token_data:
            click.echo("\n✓ Claude Code access token already configured.")
            action = questionary.select(
                "What would you like to do?",
                choices=[
                    "Keep existing token",
                    "Re-authenticate (get new token)",
                ],
                use_shortcuts=True,
                use_arrow_keys=True,
                use_jk_keys=False,
            ).ask()

            if action is None or action.startswith("Keep existing"):
                if action is None:
                    click.echo("Claude Code configuration cancelled. Keeping existing token.")
                else:
                    click.echo("Keeping existing Claude Code token")
                return True
            else:
                click.echo("\n🔐 Starting Claude Code OAuth authentication...")
                if not authenticate_and_save(quiet=False):
                    click.echo("❌ Claude Code authentication failed. Keeping existing token.")
                    return False
                return True
        else:
            click.echo("\n🔐 Starting Claude Code OAuth authentication...")
            click.echo("   (Your browser will open automatically)\n")
            if not authenticate_and_save(quiet=False):
                click.echo("\n❌ Claude Code authentication failed. Exiting.")
                return False
            return True

    # Handle Qwen OAuth separately
    if is_qwen:
        from gac.oauth import QwenOAuthProvider, TokenStore

        token_store = TokenStore()
        qwen_token = token_store.get_token("qwen")
        if qwen_token:
            click.echo("\n✓ Qwen access token already configured.")
            action = questionary.select(
                "What would you like to do?",
                choices=[
                    "Keep existing token",
                    "Re-authenticate (get new token)",
                ],
                use_shortcuts=True,
                use_arrow_keys=True,
                use_jk_keys=False,
            ).ask()

            if action is None or action.startswith("Keep existing"):
                if action is None:
                    click.echo("Qwen configuration cancelled. Keeping existing token.")
                else:
                    click.echo("Keeping existing Qwen token")
                return True
            else:
                click.echo("\n🔐 Starting Qwen OAuth authentication...")
                provider = QwenOAuthProvider(token_store)
                try:
                    provider.initiate_auth(open_browser=True)
                    click.echo("✅ Qwen authentication completed successfully!")
                    return True
                except Exception as e:
                    click.echo(f"❌ Qwen authentication failed: {e}")
                    return False
        else:
            click.echo("\n🔐 Starting Qwen OAuth authentication...")
            click.echo("   (Your browser will open automatically)\n")
            provider = QwenOAuthProvider(token_store)
            try:
                provider.initiate_auth(open_browser=True)
                click.echo("\n✅ Qwen authentication completed successfully!")
                return True
            except Exception as e:
                click.echo(f"\n❌ Qwen authentication failed: {e}")
                return False

    # Determine API key name based on provider
    if is_lmstudio:
        api_key_name = "LMSTUDIO_API_KEY"
    elif is_zai:
        api_key_name = "ZAI_API_KEY"
    else:
        api_key_name = f"{provider_key.upper().replace('-', '_')}_API_KEY"

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
            use_shortcuts=True,
            use_arrow_keys=True,
            use_jk_keys=False,
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


@click.command()
def model() -> None:
    """Interactively update provider/model/API key without language prompts."""
    click.echo("Welcome to gac model configuration!\n")

    existing_env = _load_existing_env()
    if not _configure_model(existing_env):
        return

    click.echo(f"\nModel configuration complete. You can edit {GAC_ENV_PATH} to update values later.")
