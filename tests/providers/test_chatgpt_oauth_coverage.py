"""Coverage tests for providers/chatgpt_oauth.py — targeting _make_http_request, _parse_response, and generate."""

from unittest.mock import MagicMock, patch

import pytest

from gac.errors import AIError
from gac.providers.base import ParsedResponse
from gac.providers.chatgpt_oauth import ChatGPTOAuthProvider


def _make_provider(api_key="test_token"):
    """Create a ChatGPTOAuthProvider with a mocked _get_api_key."""
    provider = ChatGPTOAuthProvider.__new__(ChatGPTOAuthProvider)
    provider.config = ChatGPTOAuthProvider.config
    provider._api_key = None
    provider._get_api_key = lambda: api_key  # type: ignore[assignment]
    return provider


# ---------------------------------------------------------------------------
# _parse_response edge cases
# ---------------------------------------------------------------------------


class TestParseResponseEdgeCases:
    def test_invalid_internal_format(self):
        """_parse_response raises AIError for invalid format."""
        provider = _make_provider()
        with pytest.raises(AIError, match="Invalid internal response format"):
            provider._parse_response({"not_parsed_response": "garbage"})

    def test_valid_parsed_response(self):
        """_parse_response returns the ParsedResponse when valid."""
        provider = _make_provider()
        parsed = ParsedResponse(content="test", prompt_tokens=5, completion_tokens=2, reasoning_tokens=0)
        result = provider._parse_response({"_parsed_response": parsed})
        assert result.content == "test"


# ---------------------------------------------------------------------------
# _make_http_request
# ---------------------------------------------------------------------------


class TestMakeHttpRequest:
    @patch("gac.providers.chatgpt_oauth.httpx.stream")
    def test_non_200_raises_model_error(self, mock_stream):
        """Non-200 response raises AIError.model_error."""
        provider = _make_provider()
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.read.return_value = b"Rate limited"
        mock_response.headers = {"content-type": "application/json"}
        mock_stream.return_value.__enter__ = MagicMock(return_value=mock_response)
        mock_stream.return_value.__exit__ = MagicMock(return_value=False)

        with patch("gac.providers.chatgpt_oauth.get_ssl_verify", return_value=True):
            with pytest.raises(AIError, match="HTTP 429"):
                provider._make_http_request("https://example.com", {}, {})

    @patch("gac.providers.chatgpt_oauth.httpx.stream")
    def test_cloudflare_block_raises_auth_error(self, mock_stream):
        """HTML content type raises AIError.authentication_error (Cloudflare)."""
        provider = _make_provider()
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.read.return_value = b"<html>Cloudflare</html>"
        mock_response.headers = {"content-type": "text/html; charset=utf-8"}
        mock_stream.return_value.__enter__ = MagicMock(return_value=mock_response)
        mock_stream.return_value.__exit__ = MagicMock(return_value=False)

        with patch("gac.providers.chatgpt_oauth.get_ssl_verify", return_value=True):
            with pytest.raises(AIError, match="Cloudflare"):
                provider._make_http_request("https://example.com", {}, {})

    @patch("gac.providers.chatgpt_oauth.httpx.stream")
    def test_success_returns_parsed_response(self, mock_stream):
        """Successful request returns _parsed_response dict."""
        provider = _make_provider()

        # Create mock lines for SSE parsing
        lines = [
            "event: response.output_text.delta",
            'data: {"type":"response.output_text.delta","delta":"Hello"}',
            "",
            "event: response.completed",
            'data: {"type":"response.completed","response":{"usage":{"input_tokens":5,"output_tokens":2}}}',
            "",
        ]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = iter(lines)
        mock_stream.return_value.__enter__ = MagicMock(return_value=mock_response)
        mock_stream.return_value.__exit__ = MagicMock(return_value=False)

        with patch("gac.providers.chatgpt_oauth.get_ssl_verify", return_value=True):
            result = provider._make_http_request("https://example.com", {}, {})
        assert "_parsed_response" in result
        assert isinstance(result["_parsed_response"], ParsedResponse)


# ---------------------------------------------------------------------------
# generate method
# ---------------------------------------------------------------------------


class TestGenerateMethod:
    @patch("gac.providers.chatgpt_oauth.get_ssl_verify", return_value=True)
    @patch("gac.providers.chatgpt_oauth.load_stored_tokens", return_value=None)
    @patch("gac.ai_utils.count_tokens", return_value=10)
    @patch("gac.providers.chatgpt_oauth.httpx.stream")
    def test_generate_with_missing_prompt_tokens(self, mock_stream, mock_count, mock_tokens, mock_ssl):
        """generate() falls back to count_tokens when prompt_tokens < 0."""
        provider = _make_provider()

        lines = [
            "event: response.output_text.delta",
            'data: {"type":"response.output_text.delta","delta":"Result"}',
            "",
            "event: response.completed",
            'data: {"type":"response.completed","response":{"usage":{"input_tokens":-1,"output_tokens":-1}}}',
            "",
        ]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = iter(lines)
        mock_stream.return_value.__enter__ = MagicMock(return_value=mock_response)
        mock_stream.return_value.__exit__ = MagicMock(return_value=False)

        result = provider.generate(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test"}],
            temperature=0.7,
            max_tokens=100,
        )
        assert result[0] == "Result"  # content
        # Falls back to count_tokens for both prompt and completion
        assert result[1] == 10  # prompt_tokens from count_tokens
        assert result[2] == 10  # completion_tokens from count_tokens

    @patch("gac.providers.chatgpt_oauth.get_ssl_verify", return_value=True)
    @patch("gac.providers.chatgpt_oauth.load_stored_tokens", return_value=None)
    @patch("gac.providers.chatgpt_oauth.httpx.stream")
    def test_generate_success(self, mock_stream, mock_tokens, mock_ssl):
        """generate() returns correct tuple on success."""
        provider = _make_provider()

        lines = [
            "event: response.output_text.delta",
            'data: {"type":"response.output_text.delta","delta":"Hello world"}',
            "",
            "event: response.completed",
            'data: {"type":"response.completed","response":{"usage":{"input_tokens":10,"output_tokens":5}}}',
            "",
        ]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = iter(lines)
        mock_stream.return_value.__enter__ = MagicMock(return_value=mock_response)
        mock_stream.return_value.__exit__ = MagicMock(return_value=False)

        result = provider.generate(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test"}],
            temperature=0.7,
            max_tokens=100,
        )
        content, prompt_tokens, completion_tokens, duration_ms, reasoning_tokens = result
        assert content == "Hello world"
        assert prompt_tokens == 10
        assert completion_tokens == 5
        assert duration_ms >= 0
        assert reasoning_tokens == 0


class TestSSEEdgeCases:
    """Test SSE parsing edge cases for coverage."""

    def test_sse_done_breaks_loop(self):
        """[DONE] marker breaks the SSE parsing loop."""
        lines = [
            "event: response.output_text.delta",
            'data: {"type":"response.output_text.delta","delta":"Partial"}',
            "",
            "data: [DONE]",
            "event: response.output_text.delta",
            'data: {"type":"response.output_text.delta","delta":"Should not appear"}',
            "",
            "event: response.completed",
            'data: {"type":"response.completed","response":{"usage":{"input_tokens":5,"output_tokens":1}}}',
            "",
        ]
        result = ChatGPTOAuthProvider._parse_sse_stream_from_lines(lines)
        assert result.content == "Partial"
        # The "Should not appear" text after [DONE] should NOT be included

    def test_sse_non_data_non_event_line_skipped(self):
        """Lines that are neither 'event:' nor 'data:' are skipped."""
        lines = [
            ": this is a comment",
            "event: response.output_text.delta",
            'data: {"type":"response.output_text.delta","delta":"Hello"}',
            "",
            "event: response.completed",
            'data: {"type":"response.completed","response":{"usage":{"input_tokens":3,"output_tokens":1}}}',
            "",
        ]
        result = ChatGPTOAuthProvider._parse_sse_stream_from_lines(lines)
        assert result.content == "Hello"


class TestGenerateModelNotInBody:
    """Test generate() when model key is missing from body."""

    @patch("gac.providers.chatgpt_oauth.get_ssl_verify", return_value=True)
    @patch("gac.providers.chatgpt_oauth.load_stored_tokens", return_value=None)
    @patch("gac.providers.chatgpt_oauth.httpx.stream")
    def test_model_added_when_missing(self, mock_stream, mock_tokens, mock_ssl):
        """generate() adds model to body when _build_request_body omits it."""
        provider = _make_provider()

        # Override _build_request_body to omit model
        original_build = provider._build_request_body

        def build_without_model(messages, temperature, max_tokens, model, **kwargs):
            body = original_build(messages, temperature, max_tokens, model, **kwargs)
            del body["model"]
            return body

        provider._build_request_body = build_without_model

        lines = [
            "event: response.output_text.delta",
            'data: {"type":"response.output_text.delta","delta":"Result"}',
            "",
            "event: response.completed",
            'data: {"type":"response.completed","response":{"usage":{"input_tokens":5,"output_tokens":2}}}',
            "",
        ]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = iter(lines)
        mock_stream.return_value.__enter__ = MagicMock(return_value=mock_response)
        mock_stream.return_value.__exit__ = MagicMock(return_value=False)

        result = provider.generate(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test"}],
        )
        assert result[0] == "Result"
