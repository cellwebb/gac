"""Auto-registration system for AI providers."""

from collections.abc import Callable

# Global registry for all providers
PROVIDER_REGISTRY: dict[str, Callable] = {}
PROVIDER_ENV_VARS: dict[str, list[str]] = {}


def register_provider(name: str, env_vars: list[str], api_function: Callable):
    """Register a provider with its API function.

    Args:
        name: Provider name (e.g., "groq", "openai")
        env_vars: List of required environment variables
        api_function: The API call function for the provider

    Returns:
        Decorator function that registers the class
    """

    def decorator(cls):
        """Decorator that registers the class and returns it unchanged."""
        PROVIDER_REGISTRY[name] = api_function
        PROVIDER_ENV_VARS[name] = env_vars
        return cls

    return decorator


def get_all_provider_names() -> list[str]:
    """Get list of all registered provider names.

    Returns:
        Sorted list of provider names
    """
    return sorted(PROVIDER_REGISTRY.keys())


def get_all_env_vars() -> list[str]:
    """Get list of all environment variables used by providers.

    Returns:
        Sorted list of unique environment variable names
    """
    return sorted({var for vars_list in PROVIDER_ENV_VARS.values() for var in vars_list})


__all__ = [
    "PROVIDER_ENV_VARS",
    "PROVIDER_REGISTRY",
    "get_all_env_vars",
    "get_all_provider_names",
    "register_provider",
]
