"""Centralized error handling decorator for AI providers."""

from collections.abc import Callable
from functools import wraps
from typing import Any

import httpx

from gac.errors import AIError


def handle_provider_errors(provider_name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to standardize error handling across all AI providers.

    Args:
        provider_name: Name of the AI provider for error messages

    Returns:
        Decorator function that wraps provider functions with standardized error handling
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except AIError:
                # Re-raise AIError exceptions as-is without wrapping
                raise
            except httpx.ConnectError as e:
                raise AIError.connection_error(f"{provider_name}: {e}") from e
            except httpx.TimeoutException as e:
                raise AIError.timeout_error(f"{provider_name}: {e}") from e
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    raise AIError.authentication_error(
                        f"{provider_name}: Invalid API key or authentication failed"
                    ) from e
                elif e.response.status_code == 429:
                    raise AIError.rate_limit_error(
                        f"{provider_name}: Rate limit exceeded. Please try again later."
                    ) from e
                elif e.response.status_code == 404:
                    raise AIError.model_error(f"{provider_name}: Model not found or endpoint not available") from e
                elif e.response.status_code >= 500:
                    raise AIError.connection_error(
                        f"{provider_name}: Server error (HTTP {e.response.status_code})"
                    ) from e
                else:
                    raise AIError.model_error(
                        f"{provider_name}: HTTP {e.response.status_code}: {e.response.text}"
                    ) from e
            except Exception as e:
                # Handle any other unexpected exceptions
                if "authentication" in str(e).lower() or "unauthorized" in str(e).lower():
                    raise AIError.authentication_error(f"Error calling {provider_name} API: {e}") from e
                elif "rate limit" in str(e).lower() or "quota" in str(e).lower():
                    raise AIError.rate_limit_error(f"Error calling {provider_name} API: {e}") from e
                elif "timeout" in str(e).lower():
                    raise AIError.timeout_error(f"Error calling {provider_name} API: {e}") from e
                elif "connection" in str(e).lower():
                    raise AIError.connection_error(f"Error calling {provider_name} API: {e}") from e
                else:
                    # Handle all other exceptions with the standard format
                    raise AIError.model_error(f"Error calling {provider_name} API: {e}") from e

        return wrapper

    return decorator


__all__ = ["handle_provider_errors"]
