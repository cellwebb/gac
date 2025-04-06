"""AI provider integration for GAC.

This module provides core functionality for AI provider interaction.
"""

import logging
import time

import aisuite as ai
from halo import Halo

from gac.constants import MAX_OUTPUT_TOKENS, MAX_RETRIES, TEMPERATURE
from gac.errors import AIError

logger = logging.getLogger(__name__)


def generate_commit_message(
    model: str,
    prompt: str,
    temperature: float = TEMPERATURE,
    max_tokens: int = MAX_OUTPUT_TOKENS,
    max_retries: int = MAX_RETRIES,
    quiet: bool = False,
) -> str:
    """Generate a commit message using aisuite."""
    try:
        provider, model_name = model.split(":", 1)
    except ValueError:
        raise AIError(f"Invalid model format: {model}. Please use the format 'provider:model_name'.")

    client = ai.Client()

    if quiet:
        spinner = None
    else:
        spinner = Halo(text=f"Generating commit message with {model}...", spinner="dots")
        spinner.start()

    last_error = None

    retry_count = 0
    while retry_count < max_retries:
        try:
            logger.debug(f"Trying with model {model} " f"(attempt {retry_count + 1}/{max_retries})")
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            message = response.choices[0].message.content if hasattr(response, "choices") else response.content

            if spinner:
                spinner.succeed(f"Generated commit message with {model}")

            return message

        except Exception as e:
            last_error = e
            retry_count += 1

            if retry_count == max_retries:
                logger.warning(f"Error generating commit message: {e}. Giving up.")
                break

            wait_time = 2**retry_count
            logger.warning(f"Error generating commit message: {e}. Retrying in {wait_time}s...")
            if spinner:
                for i in range(wait_time, 0, -1):
                    spinner.text = f"Retry {retry_count}/{max_retries} in {i}s..."
                    time.sleep(1)
            else:
                time.sleep(wait_time)
    if spinner:
        spinner.fail("Failed to generate commit message")
    raise AIError(f"Failed to generate commit message after {max_retries} attempts: {last_error}")
