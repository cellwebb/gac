"""Model identifier value object for parsing and validating model strings."""

from __future__ import annotations

from dataclasses import dataclass

from gac.errors import ConfigError


@dataclass(frozen=True)
class ModelIdentifier:
    """Represents a parsed model identifier in the format 'provider:model_name'.

    This is an immutable value object that ensures model identifiers are
    properly validated and provides convenient access to the components.

    Attributes:
        provider: The provider name (e.g., 'openai', 'anthropic', 'claude-code')
        model_name: The model name (e.g., 'gpt-4o-mini', 'claude-haiku-4-5')
    """

    provider: str
    model_name: str

    @classmethod
    def parse(cls, model_string: str) -> ModelIdentifier:
        """Parse a model string into a ModelIdentifier.

        Args:
            model_string: A string in the format 'provider:model_name'

        Returns:
            A ModelIdentifier instance

        Raises:
            ConfigError: If the format is invalid or components are empty
        """
        normalized = model_string.strip()

        if ":" not in normalized:
            raise ConfigError(
                f"Invalid model format: '{model_string}'. Expected 'provider:model', "
                "e.g. 'openai:gpt-4o-mini'. Use 'gac config set model <provider:model>' "
                "to update your configuration."
            )

        provider, model_name = normalized.split(":", 1)

        if not provider or not model_name:
            raise ConfigError(
                f"Invalid model format: '{model_string}'. Both provider and model name "
                "are required (example: 'anthropic:claude-haiku-4-5')."
            )

        return cls(provider=provider, model_name=model_name)

    def __str__(self) -> str:
        """Return the canonical string representation."""
        return f"{self.provider}:{self.model_name}"

    def starts_with_provider(self, prefix: str) -> bool:
        """Check if the provider starts with the given prefix.

        Args:
            prefix: The prefix to check (e.g., 'claude-code', 'qwen')

        Returns:
            True if the provider matches or the full identifier starts with prefix
        """
        return self.provider == prefix or str(self).startswith(f"{prefix}:")
