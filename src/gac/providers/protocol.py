"""Provider protocol for type-safe AI provider implementations."""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ProviderProtocol(Protocol):
    """Protocol defining the contract for AI providers.

    All providers must implement this protocol to ensure consistent
    interface and type safety across the codebase.

    This protocol supports both class-based providers (with methods)
    and function-based providers (used in the registry).
    """

    def generate(
        self, model: str, messages: list[dict[str, Any]], temperature: float, max_tokens: int, **kwargs: Any
    ) -> str:
        """Generate text using the AI model.

        Args:
            model: The model name to use
            messages: List of message dictionaries in chat format
            temperature: Temperature parameter (0.0-2.0)
            max_tokens: Maximum tokens in response
            **kwargs: Additional provider-specific parameters

        Returns:
            Generated text content

        Raises:
            AIError: For any generation-related errors
        """
        ...

    @property
    def name(self) -> str:
        """Get the provider name.

        Returns:
            Provider name identifier
        """
        ...

    @property
    def api_key_env(self) -> str:
        """Get the environment variable name for the API key.

        Returns:
            Environment variable name
        """
        ...

    @property
    def base_url(self) -> str:
        """Get the base URL for the API.

        Returns:
            Base API URL
        """
        ...

    @property
    def timeout(self) -> int:
        """Get the timeout in seconds.

        Returns:
            Timeout in seconds
        """
        ...
