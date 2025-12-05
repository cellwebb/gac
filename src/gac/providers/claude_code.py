"""Claude Code API provider for gac.

This provider allows users with Claude Code subscriptions to use their OAuth tokens
instead of paying for the expensive Anthropic API.
"""

from typing import Any

from gac.errors import AIError
from gac.oauth.claude_code import load_stored_token
from gac.providers.base import AnthropicCompatibleProvider, ProviderConfig
from gac.providers.error_handler import handle_provider_errors


class ClaudeCodeProvider(AnthropicCompatibleProvider):
    """Claude Code OAuth provider with special system message requirements."""

    config = ProviderConfig(
        name="Claude Code",
        api_key_env="CLAUDE_CODE_ACCESS_TOKEN",
        base_url="https://api.anthropic.com/v1/messages",
    )

    def _get_api_key(self) -> str:
        """Get OAuth token from token store."""
        token = load_stored_token()
        if token:
            return token

        raise AIError.authentication_error(
            "Claude Code authentication not found. Run 'gac auth claude-code login' to authenticate."
        )

    def _build_headers(self) -> dict[str, str]:
        """Build headers with OAuth token and special anthropic-beta."""
        headers = super()._build_headers()
        # Replace x-api-key with Bearer token
        if "x-api-key" in headers:
            del headers["x-api-key"]
        headers["Authorization"] = f"Bearer {self.api_key}"
        # Add special OAuth beta header
        headers["anthropic-beta"] = "oauth-2025-04-20"
        return headers

    def _build_request_body(
        self, messages: list[dict], temperature: float, max_tokens: int, model: str, **kwargs
    ) -> dict[str, Any]:
        """Build Anthropic-style request with fixed system message.

        IMPORTANT: Claude Code OAuth tokens require the system message to be EXACTLY
        "You are Claude Code, Anthropic's official CLI for Claude." with NO additional content.
        Any other instructions must be moved to the first user message.
        """
        # Extract and process messages
        anthropic_messages = []
        system_instructions = ""

        for msg in messages:
            if msg["role"] == "system":
                system_instructions = msg["content"]
            else:
                anthropic_messages.append({"role": msg["role"], "content": msg["content"]})

        # Move any system instructions into the first user message
        if system_instructions and anthropic_messages:
            first_user_msg = anthropic_messages[0]
            first_user_msg["content"] = f"{system_instructions}\n\n{first_user_msg['content']}"

        # Claude Code requires this exact system message
        system_message = "You are Claude Code, Anthropic's official CLI for Claude."

        body = {
            "messages": anthropic_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "system": system_message,
            **kwargs,
        }

        return body


def _get_claude_code_provider() -> ClaudeCodeProvider:
    """Lazy getter to initialize Claude Code provider at call time."""
    return ClaudeCodeProvider(ClaudeCodeProvider.config)


@handle_provider_errors("Claude Code")
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
    provider = _get_claude_code_provider()
    return provider.generate(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
