"""Retry / feedback-loop logic for grouped-commit generation.

When the AI returns invalid JSON or a file-coverage mismatch, this
module provides the machinery to feed corrective messages back into
the conversation and decide whether to retry or give up.
"""

from __future__ import annotations

import logging

from rich.panel import Panel

from gac.utils import console

logger = logging.getLogger(__name__)


def should_exit_or_retry(
    *,
    attempts: int,
    budget: int,
    raw_response: str,
    feedback_message: str,
    error_message: str,
    conversation_messages: list[dict[str, str]],
    quiet: bool,
    retry_context: str,
) -> bool:
    """Decide whether to exit or continue retrying after a validation failure.

    Appends the model's raw response and the corrective feedback to
    ``conversation_messages`` so the next AI call sees the correction.

    Args:
        attempts: Current attempt count (1-based after the failure).
        budget: Maximum number of attempts allowed.
        raw_response: The model's most recent raw output.
        feedback_message: Corrective prompt to send back to the model.
        error_message: Human-readable error for logging if budget exceeded.
        conversation_messages: Conversation history (mutated in place).
        quiet: Suppress retry progress messages.
        retry_context: Short label describing what kind of retry this is.

    Returns:
        ``True`` if the caller should exit (budget exhausted),
        ``False`` if it should retry.
    """
    conversation_messages.append({"role": "assistant", "content": raw_response})
    conversation_messages.append({"role": "user", "content": feedback_message})

    if attempts >= budget:
        logger.error(error_message)
        logger.error("Raw model output:")
        console.print(f"\n[red]{error_message}[/red]")
        console.print("\n[yellow]Raw model output:[/yellow]")
        console.print(Panel(raw_response, title="Model Output", border_style="yellow"))
        return True

    if not quiet:
        logger.info(f"Retry {attempts} of {budget - 1}: {retry_context}")
        console.print(f"[yellow]Retry {attempts} of {budget - 1}: {retry_context}[/yellow]")
    return False
