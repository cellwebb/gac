"""AI provider integration for gac.

This module provides core functionality for AI provider interaction.
It consolidates all AI-related functionality including token counting and commit message generation.
"""

import logging

from gac.ai_utils import generate_with_retries
from gac.constants import EnvDefaults
from gac.errors import AIError
from gac.providers import PROVIDER_REGISTRY

logger = logging.getLogger(__name__)


def generate_commit_message(
    model: str,
    prompt: str | tuple[str, str] | list[dict[str, str]],
    temperature: float = EnvDefaults.TEMPERATURE,
    max_tokens: int = EnvDefaults.MAX_OUTPUT_TOKENS,
    max_retries: int = EnvDefaults.MAX_RETRIES,
    quiet: bool = False,
    is_group: bool = False,
    skip_success_message: bool = False,
    task_description: str = "commit message",
) -> str:
    """Generate a commit message using direct API calls to AI providers.

    Args:
        model: The model to use in provider:model_name format (e.g., 'anthropic:claude-haiku-4-5')
        prompt: Either a string prompt (for backward compatibility) or tuple of (system_prompt, user_prompt)
        temperature: Controls randomness (0.0-1.0), lower values are more deterministic
        max_tokens: Maximum tokens in the response
        max_retries: Number of retry attempts if generation fails
        quiet: If True, suppress progress indicators

    Returns:
        A formatted commit message string

    Raises:
        AIError: If generation fails after max_retries attempts

    Example:
        >>> model = "anthropic:claude-haiku-4-5"
        >>> system_prompt, user_prompt = build_prompt("On branch main", "diff --git a/README.md b/README.md")
        >>> generate_commit_message(model, (system_prompt, user_prompt))
        'docs: Update README with installation instructions'
    """
    # Handle both old (string) and new (tuple) prompt formats
    if isinstance(prompt, list):
        messages = [{**msg} for msg in prompt]
    elif isinstance(prompt, tuple):
        system_prompt, user_prompt = prompt
        messages = [
            {"role": "system", "content": system_prompt or ""},
            {"role": "user", "content": user_prompt},
        ]
    else:
        # Backward compatibility: treat string as user prompt with empty system prompt
        user_prompt = str(prompt)
        messages = [
            {"role": "system", "content": ""},
            {"role": "user", "content": user_prompt},
        ]

    # Generate the commit message using centralized retry logic
    try:
        return generate_with_retries(
            provider_funcs=PROVIDER_REGISTRY,
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            max_retries=max_retries,
            quiet=quiet,
            is_group=is_group,
            skip_success_message=skip_success_message,
            task_description=task_description,
        )
    except AIError:
        # Re-raise AIError exceptions as-is to preserve error classification
        raise
    except Exception as e:
        logger.error(f"Failed to generate commit message: {e}")
        raise AIError.model_error(f"Failed to generate commit message: {e}") from e


def generate_grouped_commits(
    model: str,
    prompt: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
    max_retries: int,
    quiet: bool = False,
    skip_success_message: bool = False,
) -> str:
    """Generate grouped commits JSON response."""
    return generate_commit_message(
        model=model,
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        max_retries=max_retries,
        quiet=quiet,
        is_group=True,
        skip_success_message=skip_success_message,
        task_description="commit message",
    )
