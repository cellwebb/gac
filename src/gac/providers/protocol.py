"""Provider protocol for type-safe AI provider implementations.

This module defines the contract that all AI providers must follow,
ensuring consistent interface across different provider implementations.
"""

from collections.abc import Callable
from typing import Any, Protocol, runtime_checkable

# Function signature for provider functions
ProviderFunction = Callable[
    [str, list[dict], float, int],  # model, messages, temperature, max_tokens
    str,  # Returns generated content
]


@runtime_checkable
class ProviderProtocol(Protocol):
    """Protocol defining the contract for AI providers.

    All providers must implement this protocol to ensure consistent
    interface and type safety across the codebase.

    This protocol supports both class-based providers (with methods)
    and function-based providers (used in the registry).
    """

    def generate(self, model: str, messages: list[dict], temperature: float, max_tokens: int, **kwargs) -> str:
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


def validate_provider(provider: Any) -> bool:
    """Validate that a provider conforms to the protocol or function signature.

    Args:
        provider: Provider to validate (can be class or function)

    Returns:
        True if provider conforms to protocol or is a valid function

    Raises:
        TypeError: If provider doesn't conform to protocol or function signature
    """
    # Check if it's a callable function (for function-based providers)
    if callable(provider) and hasattr(provider, "__code__"):
        # It's a function, check if it matches the expected signature
        import inspect

        sig = inspect.signature(provider)
        params = list(sig.parameters.keys())

        # Expected parameters: model, messages, temperature, max_tokens
        expected_params = {"model", "messages", "temperature", "max_tokens"}
        if set(params) >= expected_params:
            return True

    # Check if it's a class implementing the protocol
    elif isinstance(provider, ProviderProtocol):
        return True

    raise TypeError(
        f"Provider {provider} does not conform to ProviderProtocol or valid function signature. "
        f"Expected either: 1) Class with generate method and properties, "
        f"or 2) Function with parameters: model, messages, temperature, max_tokens"
    )
