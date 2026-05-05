"""Tests for Custom Anthropic provider."""

import os
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, patch

import httpx
import pytest

from gac.errors import AIError
from gac.providers import PROVIDER_REGISTRY
from tests.provider_test_utils import assert_missing_api_key_error, temporarily_remove_env_var
from tests.providers.conftest import BaseProviderTest

call_custom_anthropic_api = PROVIDER_REGISTRY["custom-anthropic"]


class TestCustomAnthropicImports:
    """Test that Custom Anthropic provider can be imported."""

    def test_import_provider(self):
        """Test that Custom Anthropic provider module can be imported."""

    def test_provider_in_registry(self):
        """Test that Custom Anthropic provider is in the registry."""
        assert "custom-anthropic" in PROVIDER_REGISTRY


class TestCustomAnthropicAPIKeyValidation:
    """Test Custom Anthropic API key validation."""

    def test_missing_api_key_error(self):
        """Test that Custom Anthropic raises error when API key is missing."""
        with temporarily_remove_env_var("CUSTOM_ANTHROPIC_API_KEY"):
            with patch.dict(os.environ, {"CUSTOM_ANTHROPIC_BASE_URL": "https://api.example.com"}):
                with pytest.raises(AIError) as exc_info:
                    call_custom_anthropic_api("claude-haiku-4-5", [], 0.7, 1000)

                assert_missing_api_key_error(exc_info, "custom anthropic", "CUSTOM_ANTHROPIC_API_KEY")

    def test_missing_base_url_error(self):
        """Test that Custom Anthropic raises error when base URL is missing."""
        with temporarily_remove_env_var("CUSTOM_ANTHROPIC_BASE_URL"):
            with patch.dict(os.environ, {"CUSTOM_ANTHROPIC_API_KEY": "test-key"}):
                with pytest.raises(AIError) as exc_info:
                    call_custom_anthropic_api("claude-haiku-4-5", [], 0.7, 1000)

                assert exc_info.value.error_type == "model"
                assert "CUSTOM_ANTHROPIC_BASE_URL" in str(exc_info.value)


class TestCustomAnthropicProviderMocked(BaseProviderTest):
    """Mocked tests for Custom Anthropic provider."""

    @property
    def provider_name(self) -> str:
        return "custom-anthropic"

    @property
    def provider_module(self) -> str:
        return "gac.providers.custom_anthropic"

    @property
    def api_function(self) -> Callable:
        return PROVIDER_REGISTRY["custom-anthropic"]

    @property
    def api_key_env_var(self) -> str | None:
        return "CUSTOM_ANTHROPIC_API_KEY"

    @property
    def model_name(self) -> str:
        return "claude-haiku-4-5"

    @property
    def success_response(self) -> dict[str, Any]:
        return {"content": [{"text": "feat: Add new feature"}]}

    @property
    def empty_content_response(self) -> dict[str, Any]:
        return {"content": [{"text": ""}]}

    def test_successful_api_call(self):
        """Test that the provider successfully processes a valid API response."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_post.return_value = self._create_mock_response(self.success_response)

            messages = [{"role": "user", "content": "Generate a commit message"}]

            with patch.dict(
                os.environ,
                {"CUSTOM_ANTHROPIC_API_KEY": "test-key", "CUSTOM_ANTHROPIC_BASE_URL": "https://api.example.com"},
            ):
                result = self.api_function(model=self.model_name, messages=messages, temperature=0.7, max_tokens=100)

            assert isinstance(result, tuple)
            assert len(result) == 5
            content, prompt_tokens, completion_tokens, duration_ms, reasoning_tokens = result
            assert content == "feat: Add new feature"
            assert isinstance(duration_ms, int) and duration_ms >= 0
            assert isinstance(reasoning_tokens, int) and reasoning_tokens >= 0
            mock_post.assert_called_once()

    def test_empty_content_handling(self):
        """Test that the provider raises an error for empty content."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_post.return_value = self._create_mock_response(self.empty_content_response)

            messages = [{"role": "user", "content": "Generate a commit message"}]

            with patch.dict(
                os.environ,
                {"CUSTOM_ANTHROPIC_API_KEY": "test-key", "CUSTOM_ANTHROPIC_BASE_URL": "https://api.example.com"},
            ):
                with pytest.raises(Exception) as exc_info:
                    self.api_function(model=self.model_name, messages=messages, temperature=0.7, max_tokens=100)

                error_msg = str(exc_info.value).lower()
                assert "empty content" in error_msg or "missing" in error_msg

    def test_http_401_authentication_error(self):
        """Test that the provider handles HTTP 401 authentication errors."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"
            mock_post.side_effect = httpx.HTTPStatusError(
                "401 Unauthorized", request=MagicMock(), response=mock_response
            )

            messages = [{"role": "user", "content": "Generate a commit message"}]

            with patch.dict(
                os.environ,
                {"CUSTOM_ANTHROPIC_API_KEY": "test-key", "CUSTOM_ANTHROPIC_BASE_URL": "https://api.example.com"},
            ):
                with pytest.raises(AIError):
                    self.api_function(model=self.model_name, messages=messages, temperature=0.7, max_tokens=100)

    def test_http_429_rate_limit_error(self):
        """Test that the provider handles HTTP 429 rate limit errors."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_response.text = "Rate limit exceeded"
            mock_post.side_effect = httpx.HTTPStatusError(
                "429 Rate limit exceeded", request=MagicMock(), response=mock_response
            )

            messages = [{"role": "user", "content": "Generate a commit message"}]

            with patch.dict(
                os.environ,
                {"CUSTOM_ANTHROPIC_API_KEY": "test-key", "CUSTOM_ANTHROPIC_BASE_URL": "https://api.example.com"},
            ):
                with pytest.raises(AIError):
                    self.api_function(model=self.model_name, messages=messages, temperature=0.7, max_tokens=100)

    def test_http_500_server_error(self):
        """Test that the provider handles HTTP 500 server errors."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal server error"
            mock_post.side_effect = httpx.HTTPStatusError(
                "500 Internal server error", request=MagicMock(), response=mock_response
            )

            messages = [{"role": "user", "content": "Generate a commit message"}]

            with patch.dict(
                os.environ,
                {"CUSTOM_ANTHROPIC_API_KEY": "test-key", "CUSTOM_ANTHROPIC_BASE_URL": "https://api.example.com"},
            ):
                with pytest.raises(AIError):
                    self.api_function(model=self.model_name, messages=messages, temperature=0.7, max_tokens=100)

    def test_http_503_service_unavailable(self):
        """Test that the provider handles HTTP 503 service unavailable errors."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 503
            mock_response.text = "Service unavailable"
            mock_post.side_effect = httpx.HTTPStatusError(
                "503 Service unavailable", request=MagicMock(), response=mock_response
            )

            messages = [{"role": "user", "content": "Generate a commit message"}]

            with patch.dict(
                os.environ,
                {"CUSTOM_ANTHROPIC_API_KEY": "test-key", "CUSTOM_ANTHROPIC_BASE_URL": "https://api.example.com"},
            ):
                with pytest.raises(AIError):
                    self.api_function(model=self.model_name, messages=messages, temperature=0.7, max_tokens=100)

    def test_connection_error(self):
        """Test that the provider handles connection errors."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_post.side_effect = httpx.ConnectError("Connection failed")

            messages = [{"role": "user", "content": "Generate a commit message"}]

            with patch.dict(
                os.environ,
                {"CUSTOM_ANTHROPIC_API_KEY": "test-key", "CUSTOM_ANTHROPIC_BASE_URL": "https://api.example.com"},
            ):
                with pytest.raises(AIError):
                    self.api_function(model=self.model_name, messages=messages, temperature=0.7, max_tokens=100)

    def test_timeout_error(self):
        """Test that the provider handles timeout errors."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_post.side_effect = httpx.TimeoutException("Request timed out")

            messages = [{"role": "user", "content": "Generate a commit message"}]

            with patch.dict(
                os.environ,
                {"CUSTOM_ANTHROPIC_API_KEY": "test-key", "CUSTOM_ANTHROPIC_BASE_URL": "https://api.example.com"},
            ):
                with pytest.raises(AIError):
                    self.api_function(model=self.model_name, messages=messages, temperature=0.7, max_tokens=100)

    def test_malformed_json_response(self):
        """Test that the provider handles malformed JSON responses."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            messages = [{"role": "user", "content": "Generate a commit message"}]

            with patch.dict(
                os.environ,
                {"CUSTOM_ANTHROPIC_API_KEY": "test-key", "CUSTOM_ANTHROPIC_BASE_URL": "https://api.example.com"},
            ):
                with pytest.raises((AIError, ValueError, KeyError, TypeError)):
                    self.api_function(model=self.model_name, messages=messages, temperature=0.7, max_tokens=100)


class TestCustomAnthropicEdgeCases:
    """Test edge cases for Custom Anthropic provider."""

    def test_custom_anthropic_null_content(self):
        """Test handling of null content."""
        with patch.dict(
            "os.environ",
            {"CUSTOM_ANTHROPIC_API_KEY": "test-key", "CUSTOM_ANTHROPIC_BASE_URL": "https://api.example.com"},
        ):
            with patch("gac.providers.base.httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"content": [{"text": None}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    call_custom_anthropic_api("claude-haiku-4-5", [], 0.7, 1000)

                assert "null content" in str(exc_info.value).lower()

    def test_thinking_blocks_estimate_reasoning_tokens(self):
        """Thinking blocks in Custom Anthropic response estimate reasoning tokens."""
        thinking_text = "I need to analyze the diff carefully" * 10  # ~350 chars
        with patch.dict(
            "os.environ",
            {"CUSTOM_ANTHROPIC_API_KEY": "test-key", "CUSTOM_ANTHROPIC_BASE_URL": "https://api.example.com"},
        ):
            with patch("gac.providers.base.httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "content": [
                        {"type": "thinking", "thinking": thinking_text},
                        {"type": "text", "text": "feat: add new feature"},
                    ],
                    "usage": {"input_tokens": 100, "output_tokens": 200},
                }
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                content, pt, ct, dur, rt = call_custom_anthropic_api("claude-haiku-4-5", [], 0.7, 1000)
                assert content == "feat: add new feature"
                assert rt > 0  # Estimated from thinking text
                assert ct == 200 - rt  # output_tokens minus reasoning

    def test_no_thinking_blocks_no_reasoning_estimate(self):
        """No thinking blocks → reasoning_tokens stays 0."""
        with patch.dict(
            "os.environ",
            {"CUSTOM_ANTHROPIC_API_KEY": "test-key", "CUSTOM_ANTHROPIC_BASE_URL": "https://api.example.com"},
        ):
            with patch("gac.providers.base.httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "content": [{"text": "just a response"}],
                    "usage": {"input_tokens": 50, "output_tokens": 30},
                }
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                content, pt, ct, dur, rt = call_custom_anthropic_api("claude-haiku-4-5", [], 0.7, 1000)
                assert rt == 0
                assert ct == 30

    def test_redacted_thinking_block_not_estimated(self):
        """redacted_thinking blocks should not contribute to token estimation."""
        with patch.dict(
            "os.environ",
            {"CUSTOM_ANTHROPIC_API_KEY": "test-key", "CUSTOM_ANTHROPIC_BASE_URL": "https://api.example.com"},
        ):
            with patch("gac.providers.base.httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "content": [
                        {"type": "redacted_thinking", "data": "..."},
                        {"type": "text", "text": "clean response"},
                    ],
                    "usage": {"input_tokens": 50, "output_tokens": 30},
                }
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                content, pt, ct, dur, rt = call_custom_anthropic_api("claude-haiku-4-5", [], 0.7, 1000)
                assert rt == 0  # redacted_thinking is not type="thinking"
                assert ct == 30

    def test_base_url_trailing_slash_handling(self):
        """Test that trailing slashes in base URL are handled correctly."""
        with patch.dict(
            "os.environ",
            {"CUSTOM_ANTHROPIC_API_KEY": "test-key", "CUSTOM_ANTHROPIC_BASE_URL": "https://api.example.com/"},
        ):
            with patch("gac.providers.base.httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"content": [{"text": "test"}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                call_custom_anthropic_api("claude-haiku-4-5", [], 0.7, 1000)

                called_url = mock_post.call_args[0][0]
                assert called_url == "https://api.example.com/v1/messages"

    def test_base_url_with_full_path_included(self):
        """Test that full endpoint path in base URL is preserved."""
        with patch.dict(
            "os.environ",
            {
                "CUSTOM_ANTHROPIC_API_KEY": "test-key",
                "CUSTOM_ANTHROPIC_BASE_URL": "https://proxy.example.com/anthropic/v1/messages",
            },
        ):
            with patch("gac.providers.base.httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"content": [{"text": "test"}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                call_custom_anthropic_api("claude-haiku-4-5", [], 0.7, 1000)

                called_url = mock_post.call_args[0][0]
                assert called_url == "https://proxy.example.com/anthropic/v1/messages"

    def test_base_url_already_ends_with_messages(self):
        """Test that base URL ending with /messages uses the URL as-is (line 44)."""
        with patch.dict(
            "os.environ",
            {
                "CUSTOM_ANTHROPIC_API_KEY": "test-key",
                "CUSTOM_ANTHROPIC_BASE_URL": "https://api.example.com/messages",
            },
        ):
            with patch("gac.providers.base.httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"content": [{"text": "test"}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                call_custom_anthropic_api("claude-haiku-4-5", [], 0.7, 1000)

                called_url = mock_post.call_args[0][0]
                # Should use the URL as-is, not add any suffix
                assert called_url == "https://api.example.com/messages"

    def test_custom_anthropic_system_message_handling(self):
        """Test system message extraction and formatting."""
        with patch.dict(
            "os.environ",
            {"CUSTOM_ANTHROPIC_API_KEY": "test-key", "CUSTOM_ANTHROPIC_BASE_URL": "https://api.example.com"},
        ):
            with patch("gac.providers.base.httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"content": [{"text": "test response"}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                messages = [
                    {"role": "system", "content": "System instruction"},
                    {"role": "user", "content": "User message"},
                ]

                result = call_custom_anthropic_api("claude-haiku-4-5", messages, 0.7, 1000)

                call_args = mock_post.call_args
                payload = call_args.kwargs["json"]
                assert "system" in payload
                assert payload["system"] == "System instruction"
                assert len(payload["messages"]) == 1
                assert payload["messages"][0]["role"] == "user"
                assert result[0] == "test response"

    def test_custom_anthropic_custom_version_header(self):
        """Test that custom API version header can be set."""
        with patch.dict(
            "os.environ",
            {
                "CUSTOM_ANTHROPIC_API_KEY": "test-key",
                "CUSTOM_ANTHROPIC_BASE_URL": "https://api.example.com",
                "CUSTOM_ANTHROPIC_VERSION": "2024-01-01",
            },
        ):
            with patch("gac.providers.base.httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"content": [{"text": "test"}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                call_custom_anthropic_api("claude-haiku-4-5", [], 0.7, 1000)

                call_args = mock_post.call_args
                headers = call_args.kwargs["headers"]
                assert headers["anthropic-version"] == "2024-01-01"

    def test_custom_anthropic_default_version_header(self, clean_env_state):
        """Test that default API version header is used when not specified."""
        with patch.dict(
            "os.environ",
            {"CUSTOM_ANTHROPIC_API_KEY": "test-key", "CUSTOM_ANTHROPIC_BASE_URL": "https://api.example.com"},
        ):
            with patch("gac.providers.base.httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"content": [{"text": "test"}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                call_custom_anthropic_api("claude-haiku-4-5", [], 0.7, 1000)

                call_args = mock_post.call_args
                headers = call_args.kwargs["headers"]
                assert headers["anthropic-version"] == "2023-06-01"

    def test_custom_anthropic_extended_format_with_thinking(self):
        """Test handling of extended format with thinking traces (e.g., MiniMax)."""
        with patch.dict(
            "os.environ",
            {"CUSTOM_ANTHROPIC_API_KEY": "test-key", "CUSTOM_ANTHROPIC_BASE_URL": "https://api.example.com"},
        ):
            with patch("gac.providers.base.httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "content": [
                        {"thinking": "thinking content here", "type": "thinking", "signature": "abc123"},
                        {"text": "actual response text", "type": "text"},
                    ]
                }
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                result = call_custom_anthropic_api("claude-haiku-4-5", [], 0.7, 1000)

                assert result[0] == "actual response text"

    def test_base_url_with_v1_suffix(self):
        """Test that base URL ending with /v1 gets /messages appended."""
        with patch.dict(
            "os.environ",
            {"CUSTOM_ANTHROPIC_API_KEY": "test-key", "CUSTOM_ANTHROPIC_BASE_URL": "https://api.example.com/v1"},
        ):
            with patch("gac.providers.base.httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"content": [{"text": "test"}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                call_custom_anthropic_api("claude-haiku-4-5", [], 0.7, 1000)

                called_url = mock_post.call_args[0][0]
                assert called_url == "https://api.example.com/v1/messages"

    def test_parse_response_empty_content_array(self):
        """Test that empty content array raises AIError."""
        with patch.dict(
            "os.environ",
            {"CUSTOM_ANTHROPIC_API_KEY": "test-key", "CUSTOM_ANTHROPIC_BASE_URL": "https://api.example.com"},
        ):
            with patch("gac.providers.base.httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"content": []}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    call_custom_anthropic_api("claude-haiku-4-5", [], 0.7, 1000)

                assert "empty content" in str(exc_info.value).lower()

    def test_parse_response_no_text_in_extended_format(self):
        """Test that extended format without text item raises AIError."""
        with patch.dict(
            "os.environ",
            {"CUSTOM_ANTHROPIC_API_KEY": "test-key", "CUSTOM_ANTHROPIC_BASE_URL": "https://api.example.com"},
        ):
            with patch("gac.providers.base.httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"content": [{"type": "thinking", "thinking": "some thinking"}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    call_custom_anthropic_api("claude-haiku-4-5", [], 0.7, 1000)

                assert "unexpected format" in str(exc_info.value).lower()

    def test_parse_response_key_error(self):
        """Test that KeyError in response parsing raises AIError."""
        with patch.dict(
            "os.environ",
            {"CUSTOM_ANTHROPIC_API_KEY": "test-key", "CUSTOM_ANTHROPIC_BASE_URL": "https://api.example.com"},
        ):
            with patch("gac.providers.base.httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    call_custom_anthropic_api("claude-haiku-4-5", [], 0.7, 1000)

                assert "empty content" in str(exc_info.value).lower() or "unexpected" in str(exc_info.value).lower()

    def test_parse_response_type_error_in_content(self):
        """Test that TypeError from bad content structure raises AIError."""
        with patch.dict(
            "os.environ",
            {"CUSTOM_ANTHROPIC_API_KEY": "test-key", "CUSTOM_ANTHROPIC_BASE_URL": "https://api.example.com"},
        ):
            with patch("gac.providers.base.httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"content": [None]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    call_custom_anthropic_api("claude-haiku-4-5", [], 0.7, 1000)

                assert "unexpected" in str(exc_info.value).lower() or "TypeError" in str(exc_info.value)


@pytest.mark.integration
class TestCustomAnthropicIntegration:
    """Integration tests for Custom Anthropic provider."""

    def test_real_api_call(self):
        """Test actual Custom Anthropic API call with valid credentials."""
        api_key = os.getenv("CUSTOM_ANTHROPIC_API_KEY")
        base_url = os.getenv("CUSTOM_ANTHROPIC_BASE_URL")

        if not api_key or not base_url:
            pytest.skip("CUSTOM_ANTHROPIC_API_KEY and CUSTOM_ANTHROPIC_BASE_URL not set - skipping real API test")

        messages = [{"role": "user", "content": "Say 'test success' and nothing else."}]
        # Use synthetic.new endpoint with GLM-4.6 model
        response = call_custom_anthropic_api(
            model="hf:zai-org/GLM-4.6", messages=messages, temperature=1.0, max_tokens=1024
        )

        assert response is not None
        assert isinstance(response, tuple)
        assert len(response[0]) > 0
