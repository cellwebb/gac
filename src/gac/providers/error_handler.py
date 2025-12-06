"""Centralized error handling decorator for AI providers.

This module provides the single authoritative location for converting exceptions
to AIError types. All provider API functions should be decorated with
@handle_provider_errors to ensure consistent error handling.

Error Classification:
    - httpx.ConnectError -> AIError.connection_error
    - httpx.TimeoutException -> AIError.timeout_error
    - httpx.HTTPStatusError:
        - 401 -> AIError.authentication_error
        - 429 -> AIError.rate_limit_error
        - 404 -> AIError.model_error
        - 5xx -> AIError.connection_error (server issues)
        - other -> AIError.model_error
    - Other exceptions: String-based classification as fallback
"""

from collections.abc import Callable
from functools import wraps
from typing import Any

import httpx

from gac.errors import AIError
from gac.providers.base import sanitize_error_response


def handle_provider_errors(provider_name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to standardize error handling across all AI providers.

    This is the single authoritative location for error handling. Provider
    implementations should not catch httpx exceptions - they will be caught
    and converted to appropriate AIError types by this decorator.

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
                sanitized_response = sanitize_error_response(e.response.text)
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
                        f"{provider_name}: HTTP {e.response.status_code}: {sanitized_response}"
                    ) from e
            except Exception as e:
                # Handle any other unexpected exceptions with string-based classification
                error_str = str(e).lower()
                if "authentication" in error_str or "unauthorized" in error_str:
                    raise AIError.authentication_error(f"Error calling {provider_name} API: {e}") from e
                elif "rate limit" in error_str or "quota" in error_str:
                    raise AIError.rate_limit_error(f"Error calling {provider_name} API: {e}") from e
                elif "timeout" in error_str:
                    raise AIError.timeout_error(f"Error calling {provider_name} API: {e}") from e
                elif "connection" in error_str:
                    raise AIError.connection_error(f"Error calling {provider_name} API: {e}") from e
                else:
                    raise AIError.model_error(f"Error calling {provider_name} API: {e}") from e

        return wrapper

    return decorator


__all__ = ["handle_provider_errors"]
