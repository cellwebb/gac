"""Tests for ChatGPT OAuth provider (chatgpt_oauth.py)."""

from unittest.mock import patch

import pytest

from gac.errors import AIError
from gac.providers.chatgpt_oauth import ChatGPTOAuthProvider


def _make_provider(api_key="test_token"):
    """Create a ChatGPTOAuthProvider with a mocked _get_api_key."""
    provider = ChatGPTOAuthProvider.__new__(ChatGPTOAuthProvider)
    provider.config = ChatGPTOAuthProvider.config
    provider._api_key = None
    provider._get_api_key = lambda: api_key  # type: ignore[assignment]
    return provider


class TestChatGPTOAuthProviderAPIKey:
    """Test _get_api_key method."""

    def test_get_api_key_refresh_fails(self):
        """When refresh fails, raise authentication error."""
        with patch("gac.providers.chatgpt_oauth.refresh_token_if_expired", return_value=False):
            provider = ChatGPTOAuthProvider.__new__(ChatGPTOAuthProvider)
            provider.config = ChatGPTOAuthProvider.config
            with pytest.raises(AIError, match="ChatGPT OAuth token not found or expired"):
                provider._get_api_key()

    def test_get_api_key_refresh_succeeds_no_stored_token(self):
        """When refresh succeeds but no stored token, raise error."""
        with patch("gac.providers.chatgpt_oauth.refresh_token_if_expired", return_value=True):
            with patch("gac.providers.chatgpt_oauth.load_stored_token", return_value=None):
                provider = ChatGPTOAuthProvider.__new__(ChatGPTOAuthProvider)
                provider.config = ChatGPTOAuthProvider.config
                with pytest.raises(AIError, match="ChatGPT OAuth authentication not found"):
                    provider._get_api_key()

    def test_get_api_key_success(self):
        """When refresh and load succeed, return token."""
        with patch("gac.providers.chatgpt_oauth.refresh_token_if_expired", return_value=True):
            with patch("gac.providers.chatgpt_oauth.load_stored_token", return_value="test_token_123"):
                provider = ChatGPTOAuthProvider.__new__(ChatGPTOAuthProvider)
                provider.config = ChatGPTOAuthProvider.config
                result = provider._get_api_key()
                assert result == "test_token_123"


class TestChatGPTOAuthProviderHeaders:
    """Test _build_headers method."""

    def test_build_headers_with_account_id(self):
        """Headers include ChatGPT-Account-Id when available."""
        with patch("gac.providers.chatgpt_oauth.load_stored_tokens", return_value={"account_id": "acc-123"}):
            provider = _make_provider("test_token")
            headers = provider._build_headers()

            assert "ChatGPT-Account-Id" in headers
            assert headers["ChatGPT-Account-Id"] == "acc-123"
            assert "x-api-key" not in headers
            assert "originator" in headers
            assert "User-Agent" in headers

    def test_build_headers_without_account_id(self):
        """Headers omit ChatGPT-Account-Id when not available."""
        with patch("gac.providers.chatgpt_oauth.load_stored_tokens", return_value=None):
            provider = _make_provider("test_token")
            headers = provider._build_headers()

            assert "ChatGPT-Account-Id" not in headers
            assert "originator" in headers

    def test_build_headers_authorization_bearer(self):
        """Authorization header uses Bearer token."""
        with patch("gac.providers.chatgpt_oauth.load_stored_tokens", return_value=None):
            provider = _make_provider("my_token")
            headers = provider._build_headers()

            assert "Authorization" in headers
            assert headers["Authorization"] == "Bearer my_token"

    def test_build_headers_accept_sse(self):
        """Headers include Accept: text/event-stream."""
        with patch("gac.providers.chatgpt_oauth.load_stored_tokens", return_value=None):
            provider = _make_provider("my_token")
            headers = provider._build_headers()
            assert headers["Accept"] == "text/event-stream"

    def test_build_headers_removes_x_api_key(self):
        """x-api-key header is removed if present from parent."""
        with patch("gac.providers.chatgpt_oauth.load_stored_tokens", return_value=None):
            provider = _make_provider("my_token")
            headers = provider._build_headers()
            assert "x-api-key" not in headers


class TestChatGPTOAuthProviderAPIUrl:
    """Test _get_api_url method."""

    def test_api_url_uses_responses_endpoint(self):
        """API URL uses /responses endpoint (Codex Responses API)."""
        provider = _make_provider()
        url = provider._get_api_url("gpt-5.4")
        assert url.endswith("/responses")
        assert "chatgpt.com" in url


class TestChatGPTOAuthProviderRequestBody:
    """Test _build_request_body method."""

    def test_request_body_uses_responses_format(self):
        """Request body uses Responses API format with instructions and input."""
        provider = _make_provider()

        body = provider._build_request_body(
            messages=[
                {"role": "system", "content": "You are a helper."},
                {"role": "user", "content": "test"},
            ],
            temperature=0.7,
            max_tokens=1000,
            model="gpt-5.4",
        )

        assert body["model"] == "gpt-5.4"
        assert body["instructions"] == "You are a helper."
        assert body["input"] == [{"role": "user", "content": "test"}]
        assert body["stream"] is True
        assert body["store"] is False

    def test_request_body_no_system_message(self):
        """Request body with no system message has empty instructions."""
        provider = _make_provider()

        body = provider._build_request_body(
            messages=[{"role": "user", "content": "hello"}],
            temperature=0.7,
            max_tokens=100,
            model="gpt-5.4",
        )

        assert body["instructions"] == ""
        assert body["input"] == [{"role": "user", "content": "hello"}]


class TestChatGPTOAuthProviderSSEParsing:
    """Test _parse_sse_stream method."""

    def test_parse_basic_sse_stream(self):
        """Parse a basic SSE stream with text deltas and completion."""
        lines = [
            "event: response.output_text.delta",
            'data: {"type":"response.output_text.delta","delta":"Hello"}',
            "",
            "event: response.output_text.delta",
            'data: {"type":"response.output_text.delta","delta":" world"}',
            "",
            "event: response.completed",
            'data: {"type":"response.completed","response":{"usage":{"input_tokens":10,"output_tokens":5}}}',
            "",
        ]
        result = ChatGPTOAuthProvider._parse_sse_stream_from_lines(lines)
        assert result.content == "Hello world"
        assert result.prompt_tokens == 10
        assert result.completion_tokens == 5

    def test_parse_sse_with_reasoning_tokens(self):
        """Parse SSE stream that includes reasoning tokens."""
        lines = [
            "event: response.output_text.delta",
            'data: {"type":"response.output_text.delta","delta":"Thinking..."}',
            "",
            "event: response.completed",
            'data: {"type":"response.completed","response":{"usage":{"input_tokens":100,"output_tokens":50,"output_tokens_details":{"reasoning_tokens":20}}}}',
            "",
        ]
        result = ChatGPTOAuthProvider._parse_sse_stream_from_lines(lines)
        assert result.content == "Thinking..."
        assert result.prompt_tokens == 100
        assert result.completion_tokens == 30  # 50 - 20 reasoning
        assert result.reasoning_tokens == 20

    def test_parse_sse_empty_content_raises(self):
        """Empty SSE content raises AIError."""
        lines = [
            "event: response.completed",
            'data: {"type":"response.completed","response":{"usage":{}}}',
            "",
        ]
        with pytest.raises(AIError, match="Empty response"):
            ChatGPTOAuthProvider._parse_sse_stream_from_lines(lines)

    def test_parse_sse_text_done_overrides_deltas(self):
        """response.output_text.done event overrides accumulated deltas."""
        lines = [
            "event: response.output_text.delta",
            'data: {"type":"response.output_text.delta","delta":"partial"}',
            "",
            "event: response.output_text.done",
            'data: {"type":"response.output_text.done","text":"Final answer"}',
            "",
            "event: response.completed",
            'data: {"type":"response.completed","response":{"usage":{"input_tokens":5,"output_tokens":2}}}',
            "",
        ]
        result = ChatGPTOAuthProvider._parse_sse_stream_from_lines(lines)
        assert result.content == "Final answer"

    def test_parse_sse_ignores_unknown_events(self):
        """Unknown SSE event types are ignored."""
        lines = [
            "event: response.created",
            'data: {"type":"response.created"}',
            "",
            "event: response.output_text.delta",
            'data: {"type":"response.output_text.delta","delta":"Hello"}',
            "",
            "event: response.completed",
            'data: {"type":"response.completed","response":{"usage":{"input_tokens":3,"output_tokens":1}}}',
            "",
        ]
        result = ChatGPTOAuthProvider._parse_sse_stream_from_lines(lines)
        assert result.content == "Hello"

    def test_parse_sse_ignores_malformed_json(self):
        """Malformed JSON in SSE data is ignored."""
        lines = [
            "event: response.output_text.delta",
            'data: {"type":"response.output_text.delta","delta":"valid"}',
            "",
            "event: response.output_text.delta",
            "data: not json at all",
            "",
            "event: response.completed",
            'data: {"type":"response.completed","response":{"usage":{"input_tokens":2,"output_tokens":1}}}',
            "",
        ]
        result = ChatGPTOAuthProvider._parse_sse_stream_from_lines(lines)
        assert result.content == "valid"

    def test_parse_sse_reasoning_delta_events(self):
        """Reasoning delta events are captured for token estimation."""
        lines = [
            "event: response.reasoning.delta",
            'data: {"type":"response.reasoning.delta","delta":"Let me think about this"}',
            "",
            "event: response.reasoning.delta",
            'data: {"type":"response.reasoning.delta","delta":" carefully..."}',
            "",
            "event: response.output_text.delta",
            'data: {"type":"response.output_text.delta","delta":"Here is the commit"}',
            "",
            "event: response.completed",
            'data: {"type":"response.completed","response":{"usage":{"input_tokens":100,"output_tokens":50}}}',
            "",
        ]
        result = ChatGPTOAuthProvider._parse_sse_stream_from_lines(lines)
        assert result.content == "Here is the commit"
        # No explicit reasoning_tokens in usage, but we estimated from text
        assert result.reasoning_tokens > 0
        # completion_tokens should be 50 minus the estimated reasoning
        assert result.completion_tokens < 50

    def test_parse_sse_reasoning_done_overrides_deltas(self):
        """response.reasoning.done event overrides accumulated reasoning deltas."""
        long_thinking = "A" * 340  # ~100 tokens at 3.4 chars/token
        lines = [
            "event: response.reasoning.delta",
            'data: {"type":"response.reasoning.delta","delta":"partial thinking"}',
            "",
            "event: response.reasoning.done",
            f'data: {{"type":"response.reasoning.done","text":"{long_thinking}"}}',
            "",
            "event: response.output_text.delta",
            'data: {"type":"response.output_text.delta","delta":"Final answer"}',
            "",
            "event: response.completed",
            'data: {"type":"response.completed","response":{"usage":{"input_tokens":200,"output_tokens":150}}}',
            "",
        ]
        result = ChatGPTOAuthProvider._parse_sse_stream_from_lines(lines)
        assert result.content == "Final answer"
        # reasoning.done text (340 chars) should override delta ("partial thinking")
        assert result.reasoning_tokens == 100  # 340 / 3.4 = 100
        assert result.completion_tokens == 50  # 150 - 100

    def test_parse_sse_reasoning_delta_but_explicit_tokens_win(self):
        """When API reports reasoning_tokens explicitly, that wins over estimation."""
        lines = [
            "event: response.reasoning.delta",
            'data: {"type":"response.reasoning.delta","delta":"Some thinking"}',
            "",
            "event: response.output_text.delta",
            'data: {"type":"response.output_text.delta","delta":"Result"}',
            "",
            "event: response.completed",
            'data: {"type":"response.completed","response":{"usage":{"input_tokens":100,"output_tokens":50,"output_tokens_details":{"reasoning_tokens":15}}}}',
            "",
        ]
        result = ChatGPTOAuthProvider._parse_sse_stream_from_lines(lines)
        # Explicit reasoning_tokens=15 should win over character estimation
        assert result.reasoning_tokens == 15
        assert result.completion_tokens == 35  # 50 - 15

    def test_parse_sse_explicit_zero_reasoning_tokens_no_estimate(self):
        """When API explicitly reports reasoning_tokens=0, don't estimate."""
        lines = [
            "event: response.reasoning.delta",
            'data: {"type":"response.reasoning.delta","delta":"Some thinking"}',
            "",
            "event: response.output_text.delta",
            'data: {"type":"response.output_text.delta","delta":"Result"}',
            "",
            "event: response.completed",
            'data: {"type":"response.completed","response":{"usage":{"input_tokens":100,"output_tokens":50,"output_tokens_details":{"reasoning_tokens":0}}}}',
            "",
        ]
        result = ChatGPTOAuthProvider._parse_sse_stream_from_lines(lines)
        # Explicit reasoning_tokens=0 means "API says zero" — no estimation
        assert result.reasoning_tokens == 0
        assert result.completion_tokens == 50

    def test_parse_sse_no_reasoning_events_no_estimate(self):
        """No reasoning events → reasoning_tokens stays 0."""
        lines = [
            "event: response.output_text.delta",
            'data: {"type":"response.output_text.delta","delta":"Plain response"}',
            "",
            "event: response.completed",
            'data: {"type":"response.completed","response":{"usage":{"input_tokens":10,"output_tokens":5}}}',
            "",
        ]
        result = ChatGPTOAuthProvider._parse_sse_stream_from_lines(lines)
        assert result.reasoning_tokens == 0
        assert result.completion_tokens == 5

    def test_parse_sse_reasoning_done_empty_text_falls_back_to_deltas(self):
        """reasoning.done with empty text → fall back to accumulated deltas."""
        lines = [
            "event: response.reasoning.delta",
            'data: {"type":"response.reasoning.delta","delta":"partial thought"}',
            "",
            "event: response.reasoning.done",
            'data: {"type":"response.reasoning.done","text":""}',
            "",
            "event: response.output_text.delta",
            'data: {"type":"response.output_text.delta","delta":"Answer"}',
            "",
            "event: response.completed",
            'data: {"type":"response.completed","response":{"usage":{"input_tokens":100,"output_tokens":50}}}',
            "",
        ]
        result = ChatGPTOAuthProvider._parse_sse_stream_from_lines(lines)
        # reasoning.done had empty text, so deltas are used
        assert result.reasoning_tokens > 0  # Estimated from "partial thought"

    def test_parse_sse_event_type_from_data_payload(self):
        """SSE without 'event:' line falls back to data.type field."""
        lines = [
            # No 'event:' line — type encoded in JSON payload
            'data: {"type":"response.output_text.delta","delta":"Hello"}',
            "",
            'data: {"type":"response.completed","response":{"usage":{"input_tokens":5,"output_tokens":2}}}',
            "",
        ]
        result = ChatGPTOAuthProvider._parse_sse_stream_from_lines(lines)
        assert result.content == "Hello"
        assert result.prompt_tokens == 5
