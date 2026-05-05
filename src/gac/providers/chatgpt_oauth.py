"""ChatGPT OAuth API provider for gac.

This provider allows users with ChatGPT subscriptions to use their OAuth tokens
to access the Codex Responses API (chatgpt.com/backend-api/codex/responses)
instead of paying for the OpenAI API.

The Codex API requires streaming (stream=true) and uses OpenAI's Responses API
format with SSE events, not the legacy /chat/completions endpoint.
"""

import json
import logging
import time
from typing import Any

import httpx

from gac.errors import AIError
from gac.oauth.chatgpt import (
    CHATGPT_OAUTH_CONFIG,
    load_stored_token,
    load_stored_tokens,
    refresh_token_if_expired,
)
from gac.providers.base import BaseConfiguredProvider, ParsedResponse, ProviderConfig
from gac.utils import get_ssl_verify

logger = logging.getLogger(__name__)

# SSE event types we care about from the Responses API
_EVENT_OUTPUT_TEXT_DELTA = "response.output_text.delta"
_EVENT_OUTPUT_TEXT_DONE = "response.output_text.done"
_EVENT_COMPLETED = "response.completed"


class ChatGPTOAuthProvider(BaseConfiguredProvider):
    """ChatGPT OAuth provider using the Codex Responses API.

    The Codex API mandates streaming and uses the Responses API format
    (instructions + input array + SSE events), so we cannot reuse
    OpenAICompatibleProvider — we inherit from BaseConfiguredProvider instead.
    """

    config = ProviderConfig(
        name="ChatGPT OAuth",
        api_key_env="CHATGPT_OAUTH_API_KEY",
        base_url="https://chatgpt.com/backend-api/codex",
    )

    def _get_api_key(self) -> str:
        """Get OAuth token from token store, refreshing if needed."""
        if not refresh_token_if_expired(quiet=True):
            raise AIError.authentication_error(
                "ChatGPT OAuth token not found or expired. Run 'gac auth chatgpt login' to authenticate."
            )

        token = load_stored_token()
        if token:
            return token

        raise AIError.authentication_error(
            "ChatGPT OAuth authentication not found. Run 'gac auth chatgpt login' to authenticate."
        )

    def _get_api_url(self, model: str | None = None) -> str:
        """Get Codex Responses API URL."""
        return f"{self.config.base_url}/responses"

    def _build_headers(self) -> dict[str, str]:
        """Build headers with OAuth Bearer token and Codex-specific headers."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        }

        tokens = load_stored_tokens()
        account_id = tokens.get("account_id", "") if tokens else ""

        originator = CHATGPT_OAUTH_CONFIG.get("originator", "codex_cli_rs")
        client_version = CHATGPT_OAUTH_CONFIG.get("client_version", "0.128.0")

        if account_id:
            headers["ChatGPT-Account-Id"] = account_id
        headers["originator"] = originator
        headers["User-Agent"] = f"{originator}/{client_version}"

        return headers

    def _build_request_body(
        self,
        messages: list[dict[str, Any]],
        temperature: float,
        max_tokens: int,
        model: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Build Codex Responses API request body.

        Converts chat/completions-style messages into the Responses API format:
        - System message → instructions
        - Other messages → input array items
        """
        instructions = ""
        input_items: list[dict[str, Any]] = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                instructions = content
            else:
                input_items.append({"role": role, "content": content})

        return {
            "model": model,
            "instructions": instructions,
            "input": input_items,
            "tools": [],
            "tool_choice": "auto",
            "parallel_tool_calls": False,
            "store": False,
            "stream": True,
            "include": [],
        }

    @staticmethod
    def _parse_sse_stream(response: httpx.Response) -> ParsedResponse:
        """Parse the SSE stream from the Responses API.

        Yields events like:
          - response.output_text.delta  → partial text chunks
          - response.output_text.done   → final complete text
          - response.completed          → usage stats

        We accumulate text deltas and extract usage from the completed event.
        """
        return ChatGPTOAuthProvider._parse_sse_stream_from_lines(response.iter_lines())

    @staticmethod
    def _parse_sse_stream_from_lines(lines: Any) -> ParsedResponse:
        """Parse SSE lines into a ParsedResponse.

        Separated from _parse_sse_stream for testability — accepts any
        iterable of strings (httpx iter_lines or test fixture list).
        """
        text_parts: list[str] = []
        prompt_tokens = -1
        completion_tokens = -1
        reasoning_tokens = 0
        event_type = ""

        for line in lines:
            if not line:
                continue
            # SSE format: "event: <type>" then "data: <json>"
            if line.startswith("event: "):
                event_type = line[len("event: ") :].strip()
                continue
            if line.startswith("data: "):
                data_str = line[len("data: ") :]
                if data_str.strip() == "[DONE]":
                    break
                try:
                    data = json.loads(data_str)
                except json.JSONDecodeError:
                    continue
            else:
                continue

            if event_type == _EVENT_OUTPUT_TEXT_DELTA:
                delta = data.get("delta", "")
                if delta:
                    text_parts.append(delta)
            elif event_type == _EVENT_OUTPUT_TEXT_DONE:
                # Final text — prefer this over accumulated deltas
                final_text = data.get("text", "")
                if final_text:
                    text_parts = [final_text]
            elif event_type == _EVENT_COMPLETED:
                resp = data.get("response", {})
                usage = resp.get("usage", {})
                if isinstance(usage, dict):
                    pt = usage.get("input_tokens", -1)
                    ct = usage.get("output_tokens", -1)
                    prompt_tokens = pt if isinstance(pt, int) else -1
                    completion_tokens = ct if isinstance(ct, int) else -1
                    details = usage.get("output_tokens_details", {})
                    if isinstance(details, dict):
                        rt = details.get("reasoning_tokens", 0)
                        reasoning_tokens = rt if isinstance(rt, int) else 0

        content = "".join(text_parts).strip()
        if not content:
            raise AIError.model_error("Empty response from ChatGPT OAuth")

        return ParsedResponse(
            content=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=max(completion_tokens - reasoning_tokens, 0) if completion_tokens >= 0 else -1,
            reasoning_tokens=reasoning_tokens,
        )

    def _make_http_request(self, url: str, body: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
        """Make a streaming HTTP request and parse SSE events.

        Returns a dict that _parse_response can consume. Since we parse the
        stream here, we return the ParsedResponse directly embedded in a
        wrapper dict for compatibility with the generate() flow.
        """
        with httpx.stream(
            "POST",
            url,
            json=body,
            headers=headers,
            timeout=self.config.timeout,
            verify=get_ssl_verify(),
        ) as response:
            if response.status_code != 200:
                # Read the body for error details
                body_text = response.read().decode("utf-8", errors="replace")
                content_type = response.headers.get("content-type", "")
                if "text/html" in content_type:
                    raise AIError.authentication_error(
                        f"ChatGPT OAuth: HTTP {response.status_code} — Cloudflare block. "
                        "Try re-authenticating with 'gac auth chatgpt login'."
                    )
                raise AIError.model_error(f"ChatGPT OAuth: HTTP {response.status_code}: {body_text[:500]}")
            parsed = self._parse_sse_stream(response)

        # Return in a format that _parse_response can handle
        return {"_parsed_response": parsed}

    def _parse_response(self, response: dict[str, Any]) -> ParsedResponse:
        """Extract the pre-parsed response from the streaming handler."""
        parsed = response.get("_parsed_response")
        if isinstance(parsed, ParsedResponse):
            return parsed
        raise AIError.model_error("Invalid internal response format from ChatGPT OAuth")

    def generate(
        self,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> tuple[str, int, int, int, int]:
        """Generate text using the ChatGPT OAuth Responses API."""
        logger.debug(f"Generating with {self.config.name} provider (model={model})")

        url = self._get_api_url(model)
        headers = self._build_headers()
        body = self._build_request_body(messages, temperature, max_tokens, model, **kwargs)

        if "model" not in body:
            body["model"] = model

        start = time.perf_counter()
        response_data = self._make_http_request(url, body, headers)
        duration_ms = int((time.perf_counter() - start) * 1000)

        parsed = self._parse_response(response_data)
        from gac.ai_utils import count_tokens

        prompt_tokens = parsed.prompt_tokens if parsed.prompt_tokens >= 0 else count_tokens(messages, model)
        completion_tokens = (
            parsed.completion_tokens if parsed.completion_tokens >= 0 else count_tokens(parsed.content, model)
        )

        return (parsed.content, prompt_tokens, completion_tokens, duration_ms, parsed.reasoning_tokens)
