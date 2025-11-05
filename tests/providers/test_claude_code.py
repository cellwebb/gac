"""Tests for Claude Code provider."""

import os
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from gac.errors import AIError
from gac.providers.claude_code import call_claude_code_api
from tests.provider_test_utils import assert_missing_api_key_error, temporarily_remove_env_var
from tests.providers.conftest import BaseProviderTest


class TestClaudeCodeImports:
    """Test that Claude Code provider can be imported."""

    def test_import_provider(self):
        """Test that Claude Code provider module can be imported."""
        from gac.providers import claude_code  # noqa: F401

    def test_import_api_function(self):
        """Test that Claude Code API function can be imported."""
        from gac.providers.claude_code import call_claude_code_api  # noqa: F401


class TestClaudeCodeAPIKeyValidation:
    """Test Claude Code access token validation."""

    def test_missing_access_token_error(self):
        """Test that Claude Code raises error when access token is missing."""
        with temporarily_remove_env_var("CLAUDE_CODE_ACCESS_TOKEN"):
            with pytest.raises(AIError) as exc_info:
                call_claude_code_api("claude-sonnet-4-5", [], 0.7, 1000)

            assert_missing_api_key_error(exc_info, "claude-code", "CLAUDE_CODE_ACCESS_TOKEN")


class TestClaudeCodeProviderMocked(BaseProviderTest):
    """Mocked tests for Claude Code provider."""

    @property
    def provider_name(self) -> str:
        return "claude-code"

    @property
    def provider_module(self) -> str:
        return "gac.providers.claude_code"

    @property
    def api_function(self) -> Callable:
        return call_claude_code_api

    @property
    def api_key_env_var(self) -> str | None:
        return "CLAUDE_CODE_ACCESS_TOKEN"

    @property
    def model_name(self) -> str:
        return "claude-sonnet-4-5"

    @property
    def success_response(self) -> dict[str, Any]:
        return {"content": [{"text": "feat: Add new feature"}]}

    @property
    def empty_content_response(self) -> dict[str, Any]:
        return {"content": [{"text": ""}]}


class TestClaudeCodeEdgeCases:
    """Test edge cases for Claude Code provider."""

    def test_claude_code_missing_content(self):
        """Test handling of response without content field."""
        with patch.dict("os.environ", {"CLAUDE_CODE_ACCESS_TOKEN": "test-token"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"some_other_field": "value"}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    call_claude_code_api("claude-sonnet-4-5", [], 0.7, 1000)

                assert exc_info.value.error_type == "model"

    def test_claude_code_empty_content_array(self):
        """Test handling of empty content array."""
        with patch.dict("os.environ", {"CLAUDE_CODE_ACCESS_TOKEN": "test-token"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"content": []}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    call_claude_code_api("claude-sonnet-4-5", [], 0.7, 1000)

                assert exc_info.value.error_type == "model"

    def test_claude_code_missing_text_field(self):
        """Test handling of content without text field."""
        with patch.dict("os.environ", {"CLAUDE_CODE_ACCESS_TOKEN": "test-token"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"content": [{"no_text": "here"}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    call_claude_code_api("claude-sonnet-4-5", [], 0.7, 1000)

                assert exc_info.value.error_type == "model"

    def test_claude_code_null_text_content(self):
        """Test handling of null text in content."""
        with patch.dict("os.environ", {"CLAUDE_CODE_ACCESS_TOKEN": "test-token"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"content": [{"text": None}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    call_claude_code_api("claude-sonnet-4-5", [], 0.7, 1000)

                assert "null content" in str(exc_info.value).lower()

    def test_claude_code_system_message_handling(self):
        """Test system message must be exact Claude Code string, instructions moved to user message."""
        with patch.dict("os.environ", {"CLAUDE_CODE_ACCESS_TOKEN": "test-token"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"content": [{"text": "test response"}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                messages = [
                    {"role": "system", "content": "System instruction"},
                    {"role": "user", "content": "User message"},
                ]

                result = call_claude_code_api("claude-sonnet-4-5", messages, 0.7, 1000)

                call_args = mock_post.call_args
                payload = call_args.kwargs["json"]
                assert "system" in payload
                # System message must be EXACTLY the Claude Code identifier
                assert payload["system"] == "You are Claude Code, Anthropic's official CLI for Claude."
                # System instructions should be moved to user message
                assert len(payload["messages"]) == 1
                assert payload["messages"][0]["role"] == "user"
                assert "System instruction" in payload["messages"][0]["content"]
                assert "User message" in payload["messages"][0]["content"]
                assert result == "test response"

    def test_claude_code_no_system_message(self):
        """Test that Claude Code identifier is always used as exact system message."""
        with patch.dict("os.environ", {"CLAUDE_CODE_ACCESS_TOKEN": "test-token"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"content": [{"text": "test response"}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                messages = [{"role": "user", "content": "User message"}]

                result = call_claude_code_api("claude-sonnet-4-5", messages, 0.7, 1000)

                call_args = mock_post.call_args
                payload = call_args.kwargs["json"]
                # System field should be EXACTLY the Claude Code identifier
                assert "system" in payload
                assert payload["system"] == "You are Claude Code, Anthropic's official CLI for Claude."
                assert len(payload["messages"]) == 1
                assert payload["messages"][0]["content"] == "User message"
                assert result == "test response"

    def test_claude_code_authentication_header(self):
        """Test that Claude Code uses Bearer token authentication."""
        with patch.dict("os.environ", {"CLAUDE_CODE_ACCESS_TOKEN": "test-token-12345"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"content": [{"text": "test response"}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                messages = [{"role": "user", "content": "Test"}]
                call_claude_code_api("claude-sonnet-4-5", messages, 0.7, 1000)

                call_args = mock_post.call_args
                headers = call_args.kwargs["headers"]
                assert "Authorization" in headers
                assert headers["Authorization"] == "Bearer test-token-12345"
                assert headers["anthropic-beta"] == "oauth-2025-04-20"

    def test_claude_code_401_error_message(self):
        """Test that 401 errors provide helpful message about token expiration."""
        with patch.dict("os.environ", {"CLAUDE_CODE_ACCESS_TOKEN": "expired-token"}):
            with patch("httpx.post") as mock_post:
                from httpx import Response

                mock_response = Response(status_code=401, json={"error": "unauthorized"}, request=MagicMock())
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    call_claude_code_api("claude-sonnet-4-5", [], 0.7, 1000)

                assert exc_info.value.error_type == "authentication"
                error_message = str(exc_info.value).lower()
                assert "expired" in error_message or "authentication" in error_message


@pytest.mark.integration
class TestClaudeCodeIntegration:
    """Integration tests for Claude Code provider."""

    def test_real_api_call(self):
        """Test actual Claude Code API call with valid credentials."""
        access_token = os.getenv("CLAUDE_CODE_ACCESS_TOKEN")
        if not access_token:
            pytest.skip("CLAUDE_CODE_ACCESS_TOKEN not set - skipping real API test")

        messages = [{"role": "user", "content": "Say 'test success' and nothing else."}]
        response = call_claude_code_api(model="claude-sonnet-4-5", messages=messages, temperature=1.0, max_tokens=50)

        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
