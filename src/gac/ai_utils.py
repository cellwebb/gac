"""Utilities for AI provider integration for gac.

This module provides utility functions that support the AI provider implementations.
"""

import json
import logging
import os
import time
from collections.abc import Callable
from typing import Any, cast

from rich.console import Console
from rich.status import Status

from gac.errors import AIError
from gac.oauth import QwenOAuthProvider, refresh_token_if_expired
from gac.oauth.token_store import TokenStore
from gac.providers import SUPPORTED_PROVIDERS

logger = logging.getLogger(__name__)
console = Console()


def count_tokens(content: str | list[dict[str, str]] | dict[str, Any], model: str) -> int:
    """Count tokens in content using character-based estimation (1 token per 3.4 characters)."""
    text = extract_text_content(content)
    if not text:
        return 0

    # Use simple character-based estimation: 1 token per 3.4 characters (rounded)
    result = round(len(text) / 3.4)
    # Ensure at least 1 token for non-empty text
    return result if result > 0 else 1


def extract_text_content(content: str | list[dict[str, str]] | dict[str, Any]) -> str:
    """Extract text content from various input formats."""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        return "\n".join(msg["content"] for msg in content if isinstance(msg, dict) and "content" in msg)
    elif isinstance(content, dict) and "content" in content:
        return cast(str, content["content"])
    return ""


def generate_with_retries(
    provider_funcs: dict[str, Callable[..., str]],
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
    max_retries: int,
    quiet: bool = False,
    is_group: bool = False,
    skip_success_message: bool = False,
    task_description: str = "commit message",
) -> str:
    """Generate content with retry logic using direct API calls."""
    # Parse model string to determine provider and actual model
    if ":" not in model:
        raise AIError.model_error(f"Invalid model format. Expected 'provider:model', got '{model}'")

    provider, model_name = model.split(":", 1)

    # Validate provider
    if provider not in SUPPORTED_PROVIDERS:
        raise AIError.model_error(f"Unsupported provider: {provider}. Supported providers: {SUPPORTED_PROVIDERS}")

    if not messages:
        raise AIError.model_error("No messages provided for AI generation")

    # Load Claude Code token from TokenStore if needed
    if provider == "claude-code":
        # Check token expiry and refresh if needed
        if not refresh_token_if_expired(quiet=True):
            raise AIError.authentication_error(
                "Claude Code token not found or expired. Please authenticate with 'gac auth claude-code login'."
            )

        # Load the (possibly refreshed) token
        token_store = TokenStore()
        token_data = token_store.get_token("claude-code")
        if token_data and "access_token" in token_data:
            os.environ["CLAUDE_CODE_ACCESS_TOKEN"] = token_data["access_token"]
        else:
            raise AIError.authentication_error(
                "Claude Code token not found. Please authenticate with 'gac auth claude-code login'."
            )

    # Check Qwen OAuth token expiry and refresh if needed
    if provider == "qwen":
        oauth_provider = QwenOAuthProvider(TokenStore())
        token = oauth_provider.get_token()
        if not token:
            if not quiet:
                console.print("[yellow]⚠ Qwen authentication not found or expired[/yellow]")
                console.print("[cyan]🔐 Starting automatic authentication...[/cyan]")
            try:
                oauth_provider.initiate_auth(open_browser=True)
                token = oauth_provider.get_token()
                if not token:
                    raise AIError.authentication_error(
                        "Qwen authentication failed. Run 'gac auth qwen login' to authenticate manually."
                    )
                if not quiet:
                    console.print("[green]✓ Authentication successful![/green]\n")
            except AIError:
                raise
            except (ValueError, KeyError, json.JSONDecodeError, ConnectionError, OSError) as e:
                raise AIError.authentication_error(
                    f"Qwen authentication failed: {e}. Run 'gac auth qwen login' to authenticate manually."
                ) from e

    # Set up spinner
    if is_group:
        message_type = f"grouped {task_description}s"
    else:
        message_type = task_description

    if quiet:
        spinner = None
    else:
        spinner = Status(f"Generating {message_type} with {provider} {model_name}...")
        spinner.start()

    last_exception: Exception | None = None
    last_error_type = "unknown"

    for attempt in range(max_retries):
        try:
            if not quiet and not skip_success_message and attempt > 0:
                if spinner:
                    spinner.update(f"Retry {attempt + 1}/{max_retries} with {provider} {model_name}...")
                logger.info(f"Retry attempt {attempt + 1}/{max_retries}")

            # Call the appropriate provider function
            provider_func = provider_funcs.get(provider)
            if not provider_func:
                raise AIError.model_error(f"Provider function not found for: {provider}")

            content = provider_func(model=model_name, messages=messages, temperature=temperature, max_tokens=max_tokens)

            if spinner:
                if skip_success_message:
                    spinner.stop()  # Stop spinner without showing success/failure
                else:
                    spinner.stop()
                    console.print(f"✓ Generated {message_type} with {provider} {model_name}")

            if content is not None and content.strip():
                return content.strip()
            else:
                logger.warning(f"Empty or None content received from {provider} {model_name}: {repr(content)}")
                raise AIError.model_error("Empty response from AI model")

        except AIError as e:
            last_exception = e
            error_type = e.error_type
            last_error_type = error_type

            # For authentication and model errors, don't retry
            if error_type in ["authentication", "model"]:
                if spinner and not skip_success_message:
                    spinner.stop()
                    console.print(f"✗ Failed to generate {message_type} with {provider} {model_name}")
                raise

            if attempt < max_retries - 1:
                # Exponential backoff
                wait_time = 2**attempt
                if not quiet and not skip_success_message:
                    if attempt == 0:
                        logger.warning(f"AI generation failed, retrying in {wait_time}s: {e}")
                    else:
                        logger.warning(f"AI generation failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}")

                if spinner and not skip_success_message:
                    for i in range(wait_time, 0, -1):
                        spinner.update(f"Retry {attempt + 1}/{max_retries} in {i}s...")
                        time.sleep(1)
                else:
                    time.sleep(wait_time)
            else:
                num_retries = max_retries
                retry_word = "retry" if num_retries == 1 else "retries"
                logger.error(f"AI generation failed after {num_retries} {retry_word}: {e}")

    if spinner and not skip_success_message:
        spinner.stop()
        console.print(f"✗ Failed to generate {message_type} with {provider} {model_name}")

    # If we get here, all retries failed - use the last classified error type
    num_retries = max_retries
    retry_word = "retry" if num_retries == 1 else "retries"
    error_message = f"Failed to generate {message_type} after {num_retries} {retry_word}"
    if last_error_type == "authentication":
        raise AIError.authentication_error(error_message) from last_exception
    elif last_error_type == "rate_limit":
        raise AIError.rate_limit_error(error_message) from last_exception
    elif last_error_type == "timeout":
        raise AIError.timeout_error(error_message) from last_exception
    elif last_error_type == "connection":
        raise AIError.connection_error(error_message) from last_exception
    elif last_error_type == "model":
        raise AIError.model_error(error_message) from last_exception
    else:
        raise AIError.unknown_error(error_message) from last_exception
