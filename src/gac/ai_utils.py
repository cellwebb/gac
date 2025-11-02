"""Utilities for AI provider integration for gac.

This module provides utility functions that support the AI provider implementations.
"""

import logging
import time
from functools import lru_cache
from typing import Any

import tiktoken
from halo import Halo

from gac.constants import Utility
from gac.errors import AIError

logger = logging.getLogger(__name__)


def count_tokens(content: str | list[dict[str, str]] | dict[str, Any], model: str) -> int:
    """Count tokens in content using the model's tokenizer."""
    text = extract_text_content(content)
    if not text:
        return 0

    try:
        encoding = get_encoding(model)
        return len(encoding.encode(text))
    except Exception as e:
        logger.error(f"Error counting tokens: {e}")
        return len(text) // 4


def extract_text_content(content: str | list[dict[str, str]] | dict[str, Any]) -> str:
    """Extract text content from various input formats."""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        return "\n".join(msg["content"] for msg in content if isinstance(msg, dict) and "content" in msg)
    elif isinstance(content, dict) and "content" in content:
        return content["content"]  # type: ignore[no-any-return]
    return ""


@lru_cache(maxsize=1)
def get_encoding(model: str) -> tiktoken.Encoding:
    """Get the appropriate encoding for a given model."""
    model_name = model.split(":")[-1] if ":" in model else model
    try:
        return tiktoken.encoding_for_model(model_name)
    except KeyError:
        return tiktoken.get_encoding(Utility.DEFAULT_ENCODING)


def _classify_error(error_str: str) -> str:
    """Classify error types based on error message content."""
    error_str = error_str.lower()

    if (
        "api key" in error_str
        or "unauthorized" in error_str
        or "authentication" in error_str
        or "invalid api key" in error_str
    ):
        return "authentication"
    elif "timeout" in error_str or "timed out" in error_str or "request timeout" in error_str:
        return "timeout"
    elif "rate limit" in error_str or "too many requests" in error_str or "rate limit exceeded" in error_str:
        return "rate_limit"
    elif "connect" in error_str or "network" in error_str or "network connection failed" in error_str:
        return "connection"
    elif "model" in error_str or "not found" in error_str or "model not found" in error_str:
        return "model"
    else:
        return "unknown"


def generate_with_retries(
    provider_funcs: dict,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
    max_retries: int,
    quiet: bool = False,
    is_group: bool = False,
    skip_success_message: bool = False,
) -> str:
    """Generate content with retry logic using direct API calls."""
    # Parse model string to determine provider and actual model
    if ":" not in model:
        raise AIError.model_error(f"Invalid model format. Expected 'provider:model', got '{model}'")

    provider, model_name = model.split(":", 1)

    # Validate provider
    supported_providers = [
        "anthropic",
        "cerebras",
        "chutes",
        "deepseek",
        "fireworks",
        "gemini",
        "groq",
        "lm-studio",
        "minimax",
        "mistral",
        "ollama",
        "openai",
        "openrouter",
        "streamlake",
        "synthetic",
        "together",
        "zai",
        "zai-coding",
        "custom-anthropic",
        "custom-openai",
    ]
    if provider not in supported_providers:
        raise AIError.model_error(f"Unsupported provider: {provider}. Supported providers: {supported_providers}")

    if not messages:
        raise AIError.model_error("No messages provided for AI generation")

    # Set up spinner
    message_type = "commit messages" if is_group else "commit message"
    if quiet:
        spinner = None
    else:
        spinner = Halo(text=f"Generating {message_type} with {provider} {model_name}...", spinner="dots")
        spinner.start()

    last_exception = None
    last_error_type = "unknown"

    for attempt in range(max_retries):
        try:
            if not quiet and not skip_success_message and attempt > 0:
                if spinner:
                    spinner.text = f"Retry {attempt + 1}/{max_retries} with {provider} {model_name}..."
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
                    spinner.succeed(f"Generated {message_type} with {provider} {model_name}")

            if content is not None and content.strip():
                return content.strip()  # type: ignore[no-any-return]
            else:
                logger.warning(f"Empty or None content received from {provider} {model_name}: {repr(content)}")
                raise AIError.model_error("Empty response from AI model")

        except Exception as e:
            last_exception = e
            error_type = _classify_error(str(e))
            last_error_type = error_type

            # For authentication and model errors, don't retry
            if error_type in ["authentication", "model"]:
                if spinner and not skip_success_message:
                    spinner.fail(f"Failed to generate {message_type} with {provider} {model_name}")

                # Create the appropriate error type based on classification
                if error_type == "authentication":
                    raise AIError.authentication_error(f"AI generation failed: {str(e)}") from e
                elif error_type == "model":
                    raise AIError.model_error(f"AI generation failed: {str(e)}") from e

            if attempt < max_retries - 1:
                # Exponential backoff
                wait_time = 2**attempt
                if not quiet and not skip_success_message:
                    if attempt == 0:
                        logger.warning(f"AI generation failed, retrying in {wait_time}s: {str(e)}")
                    else:
                        logger.warning(
                            f"AI generation failed (attempt {attempt + 1}), retrying in {wait_time}s: {str(e)}"
                        )

                if spinner and not skip_success_message:
                    for i in range(wait_time, 0, -1):
                        spinner.text = f"Retry {attempt + 1}/{max_retries} in {i}s..."
                        time.sleep(1)
                else:
                    time.sleep(wait_time)
            else:
                num_retries = max_retries
                retry_word = "retry" if num_retries == 1 else "retries"
                logger.error(f"AI generation failed after {num_retries} {retry_word}: {str(e)}")

    if spinner and not skip_success_message:
        spinner.fail(f"Failed to generate {message_type} with {provider} {model_name}")

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
