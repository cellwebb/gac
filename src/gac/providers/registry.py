"""Provider registry for AI providers."""

from collections.abc import Callable
from functools import wraps
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from gac.providers.base import BaseConfiguredProvider

# Global registry for provider functions
PROVIDER_REGISTRY: dict[str, Callable[..., str]] = {}


def create_provider_func(provider_class: type["BaseConfiguredProvider"]) -> Callable[..., str]:
    """Create a provider function from a provider class.

    This function creates a callable that:
    1. Instantiates the provider class
    2. Calls generate() with the provided arguments
    3. Is wrapped with @handle_provider_errors for consistent error handling

    Args:
        provider_class: A provider class with a `config` class attribute

    Returns:
        A callable function that can be used to generate text
    """
    from gac.providers.error_handler import handle_provider_errors

    provider_name = provider_class.config.name

    @handle_provider_errors(provider_name)
    @wraps(provider_class.generate)
    def provider_func(model: str, messages: list[dict[str, Any]], temperature: float, max_tokens: int) -> str:
        provider = provider_class(provider_class.config)
        return provider.generate(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)

    # Add metadata for introspection
    provider_func.__name__ = f"call_{provider_name.lower().replace(' ', '_').replace('.', '_')}_api"
    provider_func.__doc__ = f"Call {provider_name} API to generate text."

    return provider_func


def register_provider(name: str, provider_class: type["BaseConfiguredProvider"]) -> None:
    """Register a provider class and auto-generate its function.

    Args:
        name: Provider name (e.g., "openai", "anthropic")
        provider_class: The provider class to register
    """
    PROVIDER_REGISTRY[name] = create_provider_func(provider_class)


__all__ = [
    "PROVIDER_REGISTRY",
    "register_provider",
]
