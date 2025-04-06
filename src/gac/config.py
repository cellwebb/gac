"""Configuration settings for gac."""

import logging
import os
import pathlib
import sys
from typing import Any, List, Optional

import questionary
from dotenv import load_dotenv
from pydantic import BaseModel, model_validator

from gac.utils import is_ollama_available

logger = logging.getLogger(__name__)

# Define configuration file paths
# 1. Package-level configuration (installed with the module)
try:
    # Get the package installation directory
    if getattr(sys, "frozen", False):
        # For PyInstaller or similar packaging
        PACKAGE_DIR = pathlib.Path(sys.executable).parent
    else:
        # For pip/pipx installations
        import gac

        PACKAGE_DIR = pathlib.Path(gac.__file__).parent
    PACKAGE_CONFIG_FILE = PACKAGE_DIR / "config.env"
except (ImportError, AttributeError):
    # Fallback to current directory if can't determine package path
    PACKAGE_DIR = pathlib.Path(__file__).parent
    PACKAGE_CONFIG_FILE = PACKAGE_DIR / "config.env"

# 2. User-level configuration (in home directory)
USER_ENV_FILE = pathlib.Path.home() / ".gac.env"

# 3. Project-level configuration (in current directory)
PROJECT_ENV_FILE = pathlib.Path.cwd() / ".gac.env"

# Load configurations with increasing precedence
# 1. Package config (installed with the module)
if PACKAGE_CONFIG_FILE.exists():
    logger.debug(f"Loading package configuration from {PACKAGE_CONFIG_FILE}")
    load_dotenv(PACKAGE_CONFIG_FILE)
    logger.debug("Package-level config loaded")

# 2. User-specific config (in home directory)
if USER_ENV_FILE.exists():
    logger.debug(f"Loading user configuration from {USER_ENV_FILE}")
    load_dotenv(USER_ENV_FILE)
    logger.debug("User-level config loaded")
else:
    USER_ENV_FILE.touch()
    logger.debug(f"Created user config file at {USER_ENV_FILE}")

# 3. Project-specific config (in current directory)
if PROJECT_ENV_FILE.exists():
    logger.debug(f"Loading project configuration from {PROJECT_ENV_FILE}")
    load_dotenv(PROJECT_ENV_FILE)
    logger.debug("Project-level config loaded (highest precedence)")

DEFAULT_CONFIG = {
    "model": "anthropic:claude-3-5-haiku-latest",
    "backup_model": None,
    "use_formatting": True,
    "max_output_tokens": 256,
    "warning_limit_input_tokens": 16000,
    "temperature": 0.7,
}

ENV_VARS = {
    "model": "GAC_MODEL",
    "backup_model": "GAC_BACKUP_MODEL",
    "use_formatting": "GAC_USE_FORMATTING",
    "max_output_tokens": "GAC_MAX_OUTPUT_TOKENS",
    "warning_limit_input_tokens": "GAC_WARNING_LIMIT_INPUT_TOKENS",
}

API_KEY_ENV_VARS = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "groq": "GROQ_API_KEY",
    "mistral": "MISTRAL_API_KEY",
    "ollama": None,
}


class ConfigError(Exception):
    pass


class Config(BaseModel):
    """Immutable configuration for Git Auto Commit."""

    model: str
    backup_model: Optional[str] = None
    use_formatting: bool
    max_output_tokens: int
    warning_limit_input_tokens: int
    api_key: Optional[str] = None
    temperature: float = 0.7

    # Make the model immutable (like dataclass with frozen=True)
    model_config = {
        "frozen": True,
    }

    @property
    def provider(self) -> str:
        """Get the provider part of the model string."""
        if ":" not in self.model:
            return "anthropic"  # Default provider
        return self.model.split(":")[0]

    @property
    def model_name(self) -> str:
        """Get the model name part of the model string."""
        if ":" not in self.model:
            return self.model  # Full model name
        return self.model.split(":", 1)[1]

    @model_validator(mode="after")
    def validate_config(self) -> "Config":
        """Validate the configuration.

        Raises:
            ConfigError: If the configuration is invalid
        """
        # Check model format
        if not self.model:
            raise ConfigError("Model configuration is required")

        if ":" not in self.model:
            raise ConfigError(
                f"Invalid model format: '{self.model}'. "
                f"Model must be in format 'provider:model_name'"
            )

        # Check provider
        provider = self.provider
        if provider not in API_KEY_ENV_VARS:
            raise ConfigError(
                f"Invalid provider: '{provider}'. "
                f"Supported: {', '.join(API_KEY_ENV_VARS.keys())}"
            )

        # Validate backup model if specified
        if self.backup_model:
            if ":" not in self.backup_model:
                raise ConfigError(
                    f"Invalid backup model format: '{self.backup_model}'. "
                    f"Backup model must be in format 'provider:model_name'"
                )

            backup_provider = self.backup_model.split(":")[0]
            if backup_provider not in API_KEY_ENV_VARS:
                raise ConfigError(
                    f"Invalid backup provider: '{backup_provider}'. "
                    f"Supported: {', '.join(API_KEY_ENV_VARS.keys())}"
                )

        # Check token limits
        if self.max_output_tokens <= 0:
            raise ConfigError(f"max_output_tokens must be positive (got {self.max_output_tokens})")

        if self.warning_limit_input_tokens <= 0:
            raise ConfigError(
                f"warning_limit_input_tokens must be positive "
                f"(got {self.warning_limit_input_tokens})"
            )

        if self.warning_limit_input_tokens > 32000:
            logger.warning(
                "warning_limit_input_tokens is very high (>32000). "
                "This might cause issues with some models"
            )

        # Check if API key is required and available
        if provider != "ollama" and not self.api_key:
            api_key_env = API_KEY_ENV_VARS[provider]
            if not os.environ.get(api_key_env):
                raise ConfigError(f"API key not set: {api_key_env}")

        return self

    # Dictionary-compatible access methods for testing compatibility
    def get(self, key: str, default: Any = None) -> Any:
        """Dictionary-style get method with default value.

        Args:
            key: Attribute name
            default: Default value to return if key doesn't exist

        Returns:
            Value of the attribute or default if not found
        """
        if hasattr(self, key):
            return getattr(self, key)
        return default

    def items(self):
        """Dictionary-style items() method.

        Returns:
            Iterator of (key, value) pairs
        """
        return self.model_dump().items()


def get_config() -> Config:
    """Load configuration from environment variables or use defaults.

    The function checks for several environment variables and applies them
    to the configuration in the following precedence (highest to lowest):
    1. Environment variables
    2. Project-level .gac.env file (in current directory)
    3. User-level .gac.env file (in home directory)
    4. Package-level config.env file (installed with the module)
    5. Default values from DEFAULT_CONFIG

    Returns:
        Config: The immutable configuration object with all settings
    """
    # Start with default values
    model = DEFAULT_CONFIG["model"]
    backup_model = DEFAULT_CONFIG["backup_model"]
    use_formatting = DEFAULT_CONFIG["use_formatting"]
    max_output_tokens = DEFAULT_CONFIG["max_output_tokens"]
    warning_limit_input_tokens = DEFAULT_CONFIG["warning_limit_input_tokens"]
    api_key = None
    temperature = 0.7  # Default temperature

    logger.debug("Loading configuration...")

    # Check which config files exist and log their paths
    config_files = []
    if PACKAGE_CONFIG_FILE.exists():
        config_files.append(f"Package config: {PACKAGE_CONFIG_FILE}")
    if USER_ENV_FILE.exists():
        config_files.append(f"User config: {USER_ENV_FILE}")
    if PROJECT_ENV_FILE.exists():
        config_files.append(f"Project config: {PROJECT_ENV_FILE}")

    if config_files:
        logger.debug(
            f"Config files found (in order of increasing precedence): {', '.join(config_files)}"
        )
    else:
        logger.debug("No config files found, using defaults and environment variables")

    # Handle model selection with precedence
    model_source = "DEFAULT_CONFIG"
    if os.environ.get(ENV_VARS["model"]):
        model = os.environ[ENV_VARS["model"]]
        # Try to determine source of this environment variable
        if PROJECT_ENV_FILE.exists() and is_var_in_file(PROJECT_ENV_FILE, ENV_VARS["model"]):
            model_source = f"project config ({PROJECT_ENV_FILE})"
        elif USER_ENV_FILE.exists() and is_var_in_file(USER_ENV_FILE, ENV_VARS["model"]):
            model_source = f"user config ({USER_ENV_FILE})"
        elif PACKAGE_CONFIG_FILE.exists() and is_var_in_file(
            PACKAGE_CONFIG_FILE, ENV_VARS["model"]
        ):
            model_source = f"package config ({PACKAGE_CONFIG_FILE})"
        else:
            model_source = "environment variable"

        # Ensure model has provider prefix
        if ":" not in model:
            logger.warning(
                f"{ENV_VARS['model']} '{model}' does not include provider prefix, "
                f"assuming 'anthropic:'"
            )
            model = f"anthropic:{model}"
        logger.debug(f"Using model from {model_source}: {model}")

    # Handle backup model configuration
    backup_model_source = "not configured"
    if os.environ.get(ENV_VARS["backup_model"]):
        backup_model = os.environ[ENV_VARS["backup_model"]]
        # Try to determine source of this environment variable
        if PROJECT_ENV_FILE.exists() and is_var_in_file(PROJECT_ENV_FILE, ENV_VARS["backup_model"]):
            backup_model_source = f"project config ({PROJECT_ENV_FILE})"
        elif USER_ENV_FILE.exists() and is_var_in_file(USER_ENV_FILE, ENV_VARS["backup_model"]):
            backup_model_source = f"user config ({USER_ENV_FILE})"
        elif PACKAGE_CONFIG_FILE.exists() and is_var_in_file(
            PACKAGE_CONFIG_FILE, ENV_VARS["backup_model"]
        ):
            backup_model_source = f"package config ({PACKAGE_CONFIG_FILE})"
        else:
            backup_model_source = "environment variable"

        # Ensure backup model has provider prefix
        if ":" not in backup_model:
            logger.warning(
                f"{ENV_VARS['backup_model']} '{backup_model}' does not include provider prefix, "
                f"assuming 'anthropic:'"
            )
            backup_model = f"anthropic:{backup_model}"
        logger.debug(f"Using backup model from {backup_model_source}: {backup_model}")

    # Extract provider from model setting
    provider = model.split(":")[0] if ":" in model else "anthropic"
    api_key_env = API_KEY_ENV_VARS.get(provider)

    # Get API key if needed
    if api_key_env:
        api_key = os.environ.get(api_key_env)
        if api_key:
            masked_key = api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else "****"
            logger.debug(f"Found API key for {provider}: {masked_key}")

    # Handle formatting preference
    if os.environ.get(ENV_VARS["use_formatting"]) is not None:
        use_formatting = os.environ[ENV_VARS["use_formatting"]].lower() == "true"
        logger.debug(f"Code formatting {'enabled' if use_formatting else 'disabled'}")

    # Handle token limits
    if os.environ.get(ENV_VARS["max_output_tokens"]):
        try:
            max_output_tokens = int(os.environ[ENV_VARS["max_output_tokens"]])
        except ValueError:
            logger.warning(f"Invalid {ENV_VARS['max_output_tokens']} value, using default")

    if os.environ.get(ENV_VARS["warning_limit_input_tokens"]):
        try:
            warning_limit_input_tokens = int(os.environ[ENV_VARS["warning_limit_input_tokens"]])
        except ValueError:
            logger.warning(f"Invalid {ENV_VARS['warning_limit_input_tokens']} value, using default")

    # Handle temperature from environment variable
    if os.environ.get("GAC_TEMPERATURE"):
        try:
            temperature = float(os.environ["GAC_TEMPERATURE"])
        except ValueError:
            logger.warning("Invalid GAC_TEMPERATURE value, using default")

    # Create the config object
    try:
        config = Config(
            model=model,
            backup_model=backup_model,
            use_formatting=use_formatting,
            max_output_tokens=max_output_tokens,
            warning_limit_input_tokens=warning_limit_input_tokens,
            api_key=api_key,
            temperature=temperature,
        )
        return config
    except Exception as e:
        logger.error(f"Error creating configuration: {e}")
        # Fallback to minimal valid configuration
        return Config(
            model="anthropic:claude-3-5-haiku-latest",
            use_formatting=True,
            max_output_tokens=256,
            warning_limit_input_tokens=16000,
        )


def run_config_wizard() -> Optional[Config]:
    """Run an interactive configuration wizard to set up GAC.

    Returns:
        Config if successful, None otherwise
    """
    print("Git Auto Commit Configuration Wizard")
    print("-------------------------------------")
    print("This wizard will help you set up GAC by creating a configuration file.")
    print("The configuration will be saved to ~/.gac.env")
    print()

    # Choose a model provider
    provider_choices = list(API_KEY_ENV_VARS.keys())
    if not is_ollama_available() and "ollama" in provider_choices:
        provider_choices.remove("ollama")

    provider = questionary.select(
        "Select your primary AI provider:",
        choices=provider_choices,
        default="anthropic" if "anthropic" in provider_choices else provider_choices[0],
    ).ask()

    if not provider:
        print("Cancelled.")
        return None

    # Get API key if needed
    api_key = None
    api_key_env = API_KEY_ENV_VARS.get(provider)
    if provider != "ollama" and api_key_env:
        # Check if API key is already set in environment
        existing_key = os.environ.get(api_key_env)
        if existing_key:
            use_existing = questionary.confirm(
                f"{api_key_env} is already set. Use this value?", default=True
            ).ask()
            if use_existing:
                api_key = existing_key

        if not api_key:
            api_key = questionary.password(f"Enter your {provider.capitalize()} API key:").ask()
            if not api_key:
                print("Cancelled.")
                return None

    # Choose model for the selected provider
    models = get_models_for_provider(provider)
    model_name = questionary.select(
        "Select your primary model:",
        choices=models,
        default=models[0] if models else None,
    ).ask()

    if not model_name:
        print("Cancelled.")
        return None

    # Ask about backup model
    use_backup = questionary.confirm(
        "Would you like to configure a backup model?", default=True
    ).ask()

    backup_provider = None
    backup_model_name = None
    backup_api_key = None

    if use_backup:
        # Choose backup provider
        remaining_providers = [p for p in provider_choices if p != provider] + [provider]
        backup_provider = questionary.select(
            "Select your backup AI provider:",
            choices=remaining_providers,
            default=remaining_providers[0] if remaining_providers else None,
        ).ask()

        if not backup_provider:
            print("No backup model will be configured.")
        else:
            # Get backup API key if needed and different from primary
            backup_api_key_env = API_KEY_ENV_VARS.get(backup_provider)
            if backup_provider != "ollama" and backup_api_key_env and backup_provider != provider:
                # Check if API key is already set in environment
                existing_key = os.environ.get(backup_api_key_env)
                if existing_key:
                    use_existing = questionary.confirm(
                        f"{backup_api_key_env} is already set. Use this value?", default=True
                    ).ask()
                    if use_existing:
                        backup_api_key = existing_key

                if not backup_api_key:
                    backup_api_key = questionary.password(
                        f"Enter your {backup_provider.capitalize()} API key:"
                    ).ask()
                    if not backup_api_key:
                        print("No backup API key provided. Continuing without backup model.")
                        backup_provider = None

            # Choose backup model if provider was selected
            if backup_provider:
                backup_models = get_models_for_provider(backup_provider)
                backup_model_name = questionary.select(
                    "Select your backup model:",
                    choices=backup_models,
                    default=backup_models[0] if backup_models else None,
                ).ask()

                if not backup_model_name:
                    print("No backup model selected.")
                    backup_provider = None

    # Get other configuration options
    use_formatting = questionary.confirm("Enable automatic code formatting?", default=True).ask()

    # Create the .gac.env file
    try:
        with open(USER_ENV_FILE, "w") as f:
            f.write("# GAC Configuration - generated by setup wizard\n")
            f.write("# See documentation for all available options\n\n")

            # Primary model
            f.write(f"{ENV_VARS['model']}={provider}:{model_name}\n")

            # Backup model if configured
            if backup_provider and backup_model_name:
                f.write(f"{ENV_VARS['backup_model']}={backup_provider}:{backup_model_name}\n")

            # API keys
            if api_key and api_key_env:
                f.write(f"{api_key_env}={api_key}\n")

            # Backup API key if different from primary
            if backup_api_key and backup_api_key_env and backup_api_key_env != api_key_env:
                f.write(f"{backup_api_key_env}={backup_api_key}\n")

            # Other settings
            f.write(f"{ENV_VARS['use_formatting']}={'true' if use_formatting else 'false'}\n")
            f.write(f"{ENV_VARS['max_output_tokens']}={DEFAULT_CONFIG['max_output_tokens']}\n")
            f.write(
                f"{ENV_VARS['warning_limit_input_tokens']}="
                f"{DEFAULT_CONFIG['warning_limit_input_tokens']}\n"
            )

        # Reload the dotenv file
        load_dotenv(USER_ENV_FILE, override=True)

        # Return the new configuration
        return get_config()

    except Exception as e:
        print(f"Error saving configuration: {e}")
        return None


def get_models_for_provider(provider: str) -> List[str]:
    """Get a list of models available for a given provider.

    Args:
        provider: The AI provider name

    Returns:
        List of model names supported by the provider
    """
    if provider == "anthropic":
        return [
            "claude-3-5-sonnet-20240620",
            "claude-3-5-haiku-20240307",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-2.1",
            "claude-2.0",
        ]
    elif provider == "openai":
        return [
            "gpt-4o",
            "gpt-4-turbo",
            "gpt-4-0613",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-0613",
        ]
    elif provider == "groq":
        return [
            "meta-llama/llama-4-scout-17b-16e-instruct",
            "meta-llama/llama-3-70b-instruct",
            "meta-llama/llama-3-8b-instruct",
            "gemma-7b-it",
            "mistral-7b-instruct",
        ]
    elif provider == "mistral":
        return [
            "mistral-large-latest",
            "mistral-medium-latest",
            "mistral-small-latest",
        ]
    elif provider == "ollama":
        try:
            import ollama

            models = ollama.list()
            return [model["name"] for model in models.get("models", [])]
        except (ImportError, Exception):
            return ["llama2", "mistral", "gemma"]

    return ["model-name"]  # Generic fallback


def is_var_in_file(file_path: pathlib.Path, var_name: str) -> bool:
    """Check if a variable is defined in a .env file.

    Args:
        file_path: Path to the .env file
        var_name: Name of the environment variable to check

    Returns:
        True if the variable is defined in the file, False otherwise
    """
    try:
        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if line.startswith(f"{var_name}="):
                        return True
        return False
    except Exception as e:
        logger.debug(f"Error checking var {var_name} in {file_path}: {e}")
        return False
