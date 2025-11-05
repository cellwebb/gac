"""Claude Code provider implementation.

This provider allows users with Claude Code subscriptions to use their OAuth tokens
instead of paying for the expensive Anthropic API.
"""

import os

import httpx

from gac.errors import AIError


def call_claude_code_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call Claude Code API using OAuth token.

    This provider uses the Claude Code subscription OAuth token instead of the Anthropic API key.
    It authenticates using Bearer token authentication with the special anthropic-beta header.

    Environment variables:
        CLAUDE_CODE_ACCESS_TOKEN: OAuth access token from Claude Code authentication

    Args:
        model: Model name (e.g., 'claude-sonnet-4-5')
        messages: List of message dictionaries with 'role' and 'content' keys
        temperature: Sampling temperature (0.0-1.0)
        max_tokens: Maximum tokens in response

    Returns:
        Generated text response

    Raises:
        AIError: If authentication fails or API call fails
    """
    access_token = os.getenv("CLAUDE_CODE_ACCESS_TOKEN")
    if not access_token:
        raise AIError.authentication_error(
            "CLAUDE_CODE_ACCESS_TOKEN not found in environment variables. "
            "Please authenticate with Claude Code and set this token."
        )

    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "anthropic-version": "2023-06-01",
        "anthropic-beta": "oauth-2025-04-20",
        "content-type": "application/json",
    }

    # Convert messages to Anthropic format
    # IMPORTANT: Claude Code OAuth tokens require the system message to be EXACTLY
    # "You are Claude Code, Anthropic's official CLI for Claude." with NO additional content.
    # Any other instructions must be moved to the user message.
    anthropic_messages = []
    system_instructions = ""

    for msg in messages:
        if msg["role"] == "system":
            system_instructions = msg["content"]
        else:
            anthropic_messages.append({"role": msg["role"], "content": msg["content"]})

    # Claude Code requires this exact system message, nothing more
    system_message = "You are Claude Code, Anthropic's official CLI for Claude."

    # Move any system instructions into the first user message
    if system_instructions and anthropic_messages:
        # Prepend system instructions to the first user message
        first_user_msg = anthropic_messages[0]
        first_user_msg["content"] = f"{system_instructions}\n\n{first_user_msg['content']}"

    data = {
        "model": model,
        "messages": anthropic_messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "system": system_message,
    }

    try:
        response = httpx.post(url, headers=headers, json=data, timeout=120)
        response.raise_for_status()
        response_data = response.json()
        content = response_data["content"][0]["text"]
        if content is None:
            raise AIError.model_error("Claude Code API returned null content")
        if content == "":
            raise AIError.model_error("Claude Code API returned empty content")
        return content
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            raise AIError.authentication_error(
                f"Claude Code authentication failed: {e.response.text}. "
                "Your token may have expired. Please re-authenticate."
            ) from e
        if e.response.status_code == 429:
            raise AIError.rate_limit_error(f"Claude Code API rate limit exceeded: {e.response.text}") from e
        raise AIError.model_error(f"Claude Code API error: {e.response.status_code} - {e.response.text}") from e
    except httpx.TimeoutException as e:
        raise AIError.timeout_error(f"Claude Code API request timed out: {str(e)}") from e
    except Exception as e:
        raise AIError.model_error(f"Error calling Claude Code API: {str(e)}") from e
