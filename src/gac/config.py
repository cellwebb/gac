"""Configuration settings for gac."""

import logging
import os
from typing import Any, Optional

import questionary
from pydantic import BaseModel, model_validator

logger = logging.getLogger(__name__)


DEFAULT_CONFIG = {
    "model": "anthropic:claude-3-5-haiku-latest",
    "use_formatting": True,
    "max_output_tokens": 512,
    "warning_limit_input_tokens": 16000,
    "temperature": 0.7,
}

ENV_VARS = {
    "model": "GAC_MODEL",
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

    def with_updates(self, **kwargs) -> "Config":
        """Create a new Config instance with updated values.

        Args:
            **kwargs: Key-value pairs to update

        Returns:
            Config: A new Config instance with updated values
        """
        # Get current values as a dictionary
        current_values = self.model_dump()

        # Update with new values
        current_values.update(kwargs)

        # Create and return a new instance
        return Config(**current_values)

    # Dictionary-compatible access methods for testing compatibility
    def __getitem__(self, key: str) -> Any:
        """Dictionary-style access to config attributes.

        Args:
            key: Attribute name

        Returns:
            Value of the attribute

        Raises:
            KeyError: If key is not a valid attribute
        """
        if not hasattr(self, key):
            raise KeyError(f"Config has no attribute '{key}'")
        return getattr(self, key)

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
    to the configuration in the following order of precedence:
    1. GAC_MODEL (full provider:model)
    2. Default values from DEFAULT_CONFIG

    Returns:
        Config: The immutable configuration object with all settings
    """
    # Start with default values
    model = DEFAULT_CONFIG["model"]
    use_formatting = DEFAULT_CONFIG["use_formatting"]
    max_output_tokens = DEFAULT_CONFIG["max_output_tokens"]
    warning_limit_input_tokens = DEFAULT_CONFIG["warning_limit_input_tokens"]
    api_key = None
    temperature = 0.7  # Default temperature

    logger.debug("Loading configuration...")

    # Handle model selection with precedence
    if os.environ.get(ENV_VARS["model"]):
        model = os.environ[ENV_VARS["model"]]
        # Ensure model has provider prefix
        if ":" not in model:
            logger.warning(
                f"{ENV_VARS['model']} '{model}' does not include provider prefix, "
                f"assuming 'anthropic:'"
            )
            model = f"anthropic:{model}"
        logger.debug(f"Using model from {ENV_VARS['model']}: {model}")

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
    config = Config(
        model=model,
        use_formatting=use_formatting,
        max_output_tokens=max_output_tokens,
        warning_limit_input_tokens=warning_limit_input_tokens,
        api_key=api_key,
        temperature=temperature,
    )

    return config


def run_config_wizard() -> Optional[Config]:
    """Interactive configuration wizard for GAC.

    Guides the user through setting up their preferred AI provider and model.

    Returns:
        Optional[Config]: Configured settings or None if wizard is cancelled
    """
    # These are the only cloud AI providers we support - no plans to add more
    # Ollama is handled separately as it's for local models only
    supported_providers = ["anthropic", "openai", "groq", "mistral"]

    # Welcome message
    print("\n🚀 Git Auto Commit (GAC) Configuration Wizard")
    print("-------------------------------------------")

    # Provider selection
    provider = questionary.select(
        "Select your preferred AI provider:", choices=supported_providers
    ).ask()

    if not provider:
        print("Configuration wizard cancelled.")
        return None

    # Model selection based on provider
    models = {
        "anthropic": [
            "claude-3-5-haiku-latest",
            "claude-3-sonnet-20240229",
            "claude-3-opus-20240229",
        ],
        "openai": ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
        "groq": ["llama3-70b-8192", "mixtral-8x7b-32768"],
        "mistral": ["mistral-large-latest", "mistral-medium-latest"],
    }

    model_name = questionary.select(f"Select a {provider} model:", choices=models[provider]).ask()

    if not model_name:
        print("Configuration wizard cancelled.")
        return None

    # Formatting preference
    use_formatting = questionary.confirm(
        "Would you like to automatically format Python files?", default=True
    ).ask()

    # Construct full model configuration
    full_model = f"{provider}:{model_name}"

    # Confirm configuration
    print("\n📋 Configuration Summary:")
    print(f"Provider: {provider}")
    print(f"Model: {model_name}")
    print(f"Auto-formatting: {'Enabled' if use_formatting else 'Disabled'}")

    confirm = questionary.confirm("Do you want to save these settings?", default=True).ask()

    if not confirm:
        print("Configuration wizard cancelled.")
        return None

    # Create configuration object
    config = Config(
        model=full_model,
        use_formatting=use_formatting,
        max_output_tokens=DEFAULT_CONFIG["max_output_tokens"],
        warning_limit_input_tokens=DEFAULT_CONFIG["warning_limit_input_tokens"],
    )

    try:
        config.validate_config()
        print("\n✅ Configuration validated successfully!")
        return config
    except ConfigError as e:
        print(f"❌ Configuration validation failed: {e}")
        return None
