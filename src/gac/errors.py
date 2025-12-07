"""Error handling module for gac."""

import logging
import sys
from collections.abc import Callable
from typing import Any, TypeVar

from rich.console import Console

logger = logging.getLogger(__name__)
console = Console()
T = TypeVar("T")


class GacError(Exception):
    """Base exception class for all gac errors."""

    exit_code = 1  # Default exit code

    def __init__(
        self,
        message: str,
        details: str | None = None,
        suggestion: str | None = None,
        exit_code: int | None = None,
    ):
        """
        Initialize a new GacError.

        Args:
            message: The error message
            details: Optional details about the error
            suggestion: Optional suggestion for the user
            exit_code: Optional exit code to override the class default
        """
        super().__init__(message)
        self.message = message
        self.details = details
        self.suggestion = suggestion
        if exit_code is not None:
            self.exit_code = exit_code


class ConfigError(GacError):
    """Error related to configuration issues."""

    exit_code = 2


class GitError(GacError):
    """Error related to Git operations."""

    exit_code = 3


class AIError(GacError):
    """Error related to AI provider or models."""

    exit_code = 4

    def __init__(self, message: str, error_type: str = "unknown", exit_code: int | None = None):
        """Initialize an AIError with a specific error type.

        Args:
            message: The error message
            error_type: The type of AI error (from AI_ERROR_CODES keys)
            exit_code: Optional exit code to override the default
        """
        super().__init__(message, exit_code=exit_code)
        self.error_type = error_type
        self.error_code = AI_ERROR_CODES.get(error_type, AI_ERROR_CODES["unknown"])

    @classmethod
    def authentication_error(cls, message: str) -> "AIError":
        """Create an authentication error."""
        return cls(message, error_type="authentication")

    @classmethod
    def connection_error(cls, message: str) -> "AIError":
        """Create a connection error."""
        return cls(message, error_type="connection")

    @classmethod
    def rate_limit_error(cls, message: str) -> "AIError":
        """Create a rate limit error."""
        return cls(message, error_type="rate_limit")

    @classmethod
    def timeout_error(cls, message: str) -> "AIError":
        """Create a timeout error."""
        return cls(message, error_type="timeout")

    @classmethod
    def model_error(cls, message: str) -> "AIError":
        """Create a model error."""
        return cls(message, error_type="model")

    @classmethod
    def unknown_error(cls, message: str) -> "AIError":
        """Create an unknown error."""
        return cls(message, error_type="unknown")


class FormattingError(GacError):
    """Error related to code formatting."""

    exit_code = 5


class SecurityError(GacError):
    """Error related to security issues (e.g., detected secrets)."""

    exit_code = 6


class HookError(GacError):
    """Error when pre-commit or lefthook hooks fail."""

    exit_code = 1


# Simplified error hierarchy - we use a single AIError class with error codes
# instead of multiple subclasses for better maintainability

# Error codes for AI errors
AI_ERROR_CODES = {
    "authentication": 401,  # Authentication failures
    "connection": 503,  # Connection issues
    "rate_limit": 429,  # Rate limits
    "timeout": 408,  # Timeouts
    "model": 400,  # Model-related errors
    "unknown": 500,  # Unknown errors
}


def handle_error(error: Exception, exit_program: bool = False, quiet: bool = False) -> None:
    """Handle an error with proper logging and user feedback.

    Args:
        error: The error to handle
        exit_program: If True, exit the program after handling the error
        quiet: If True, suppress non-error output
    """
    logger.error(f"Error: {str(error)}")

    if isinstance(error, GitError):
        logger.error("Git operation failed. Please check your repository status.")
    elif isinstance(error, AIError):
        logger.error("AI operation failed. Please check your configuration and API keys.")
    elif isinstance(error, SecurityError):
        logger.error("Security scan detected potential secrets in staged changes.")
    else:
        logger.error("An unexpected error occurred.")

    if exit_program:
        logger.error("Exiting program due to error.")
        sys.exit(error.exit_code if hasattr(error, "exit_code") else 1)


def format_error_for_user(error: Exception) -> str:
    """
    Format an error message for display to the user.

    Args:
        error: The exception to format

    Returns:
        A user-friendly error message with remediation steps if applicable
    """
    base_message = str(error)

    # More specific remediation for AI errors based on error type
    if isinstance(error, AIError):
        if hasattr(error, "error_type"):
            if error.error_type == "authentication":
                return f"{base_message}\n\nPlease check your API key and ensure it is valid."
            elif error.error_type == "connection":
                return f"{base_message}\n\nPlease check your internet connection and try again."
            elif error.error_type == "rate_limit":
                return f"{base_message}\n\nYou've hit the rate limit for this AI provider. Please wait and try again later."  # noqa: E501
            elif error.error_type == "timeout":
                return f"{base_message}\n\nThe request timed out. Please try again or use a different model."
            elif error.error_type == "model":
                return f"{base_message}\n\nPlease check that the specified model exists and is available to you."
        return f"{base_message}\n\nPlease check your API key, model name, and internet connection."

    # Mapping of error types to remediation steps
    remediation_steps = {
        ConfigError: "Please check your configuration settings.",
        GitError: "Please ensure Git is installed and you're in a valid Git repository.",
        FormattingError: "Please check that required formatters are installed.",
        SecurityError: "Please remove or secure any detected secrets before committing.",
    }

    # Generic remediation for unexpected errors
    if not any(isinstance(error, t) for t in remediation_steps.keys()):
        return f"{base_message}\n\nIf this issue persists, please report it as a bug."

    # Get remediation steps for the specific error type
    for error_class, steps in remediation_steps.items():
        if isinstance(error, error_class):
            return f"{base_message}\n\n{steps}"

    # Fallback (though we should never reach this)
    return base_message


def with_error_handling(
    error_type: type[GacError], error_message: str, quiet: bool = False, exit_on_error: bool = True
) -> Callable[[Callable[..., T]], Callable[..., T | None]]:
    """
    A decorator that wraps a function with standardized error handling.

    Args:
        error_type: The specific error type to raise if an exception occurs
        error_message: The error message to use
        quiet: If True, suppress non-error output
        exit_on_error: If True, exit the program on error

    Returns:
        A decorator function that handles errors for the wrapped function
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T | None]:
        def wrapper(*args: Any, **kwargs: Any) -> T | None:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Create a specific error with our message and the original error
                specific_error = error_type(f"{error_message}: {e}")
                # Handle the error using our standardized handler
                handle_error(specific_error, quiet=quiet, exit_program=exit_on_error)
                return None

        return wrapper

    return decorator
