"""Tests for Kimi Coding provider."""

import os
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from gac.errors import AIError
from gac.providers.kimi_coding import call_kimi_coding_api
from tests.providers.conftest import BaseProviderTest


class TestKimiImports:
    """Test that Kimi Coding provider can be imported."""

    def test_import_provider(self):
        """Test that Kimi Coding provider module can be imported."""
        from gac.providers import kimi_coding  # noqa: F401

    def test_import_api_function(self):
        """Test that Kimi Coding API function can be imported."""
        from gac.providers.kimi_coding import call_kimi_coding_api  # noqa: F401


class TestKimiAPIKeyValidation:
    """Test Kimi for Coding API key validation."""

    def test_missing_api_key_error(self):
        """Test that Kimi for Coding raises error when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(AIError) as exc_info:
                call_kimi_coding_api("kimi-coding", [], 0.7, 1000)

            assert exc_info.value.error_type == "authentication"
            assert "KIMI_CODING_API_KEY" in str(exc_info.value)


class TestKimiProviderMocked(BaseProviderTest):
    """Mocked tests for Kimi Coding provider."""

    @property
    def provider_name(self) -> str:
        return "kimi-coding"

    @property
    def provider_module(self) -> str:
        return "gac.providers.kimi_coding"

    @property
    def api_function(self) -> Callable:
        return call_kimi_coding_api

    @property
    def api_key_env_var(self) -> str | None:
        return "KIMI_CODING_API_KEY"

    @property
    def model_name(self) -> str:
        return "kimi-coding"

    @property
    def success_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": "feat: Add new feature"}}]}

    @property
    def empty_content_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": ""}}]}


class TestKimiEdgeCases:
    """Test edge cases for Kimi Coding provider."""

    def test_kimi_missing_choices(self):
        """Test handling of response without choices field."""
        with patch.dict("os.environ", {"KIMI_CODING_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"some_other_field": "value"}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    call_kimi_coding_api("kimi-coding", [], 0.7, 1000)

                # Should raise a model error for missing choices
                assert exc_info.value.error_type == "model"

    def test_kimi_empty_choices_array(self):
        """Test handling of empty choices array."""
        with patch.dict("os.environ", {"KIMI_CODING_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"choices": []}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    call_kimi_coding_api("kimi-coding", [], 0.7, 1000)

                # Should raise an error for empty choices array
                assert exc_info.value.error_type == "model"

    def test_kimi_missing_message_field(self):
        """Test handling of choices without message field."""
        with patch.dict("os.environ", {"KIMI_CODING_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"choices": [{"no_message": "here"}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    call_kimi_coding_api("kimi-coding", [], 0.7, 1000)

                # Should raise an error for missing message field
                assert exc_info.value.error_type == "model"

    def test_kimi_missing_content_field(self):
        """Test handling of message without content field."""
        with patch.dict("os.environ", {"KIMI_CODING_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"choices": [{"message": {"no_content": "here"}}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    call_kimi_coding_api("kimi-coding", [], 0.7, 1000)

                # Should raise an error for missing content field
                assert exc_info.value.error_type == "model"

    def test_kimi_null_content(self):
        """Test handling of null content in message."""
        with patch.dict("os.environ", {"KIMI_CODING_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"choices": [{"message": {"content": None}}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    call_kimi_coding_api("kimi-coding", [], 0.7, 1000)

                assert "null content" in str(exc_info.value).lower()

    def test_kimi_system_message_handling(self):
        """Test that system messages are passed through naturally (OpenAI format)."""
        with patch.dict("os.environ", {"KIMI_CODING_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"choices": [{"message": {"content": "test response"}}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                messages = [
                    {"role": "system", "content": "System instruction"},
                    {"role": "user", "content": "User message"},
                ]

                result = call_kimi_coding_api("kimi-coding", messages, 0.7, 1000)

                # Verify the payload structure - OpenAI format passes system messages as-is
                call_args = mock_post.call_args
                payload = call_args.kwargs["json"]
                # All messages should be included, system handled naturally by OpenAI
                assert len(payload["messages"]) == 2
                assert payload["messages"][0]["role"] == "system"
                assert payload["messages"][0]["content"] == "System instruction"
                assert payload["messages"][1]["role"] == "user"
                assert payload["messages"][1]["content"] == "User message"
                assert result == "test response"

    def test_kimi_no_system_message(self):
        """Test that messages work without system message."""
        with patch.dict("os.environ", {"KIMI_CODING_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"choices": [{"message": {"content": "test response"}}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                messages = [{"role": "user", "content": "User message"}]

                result = call_kimi_coding_api("kimi-coding", messages, 0.7, 1000)

                # Verify the payload structure
                call_args = mock_post.call_args
                payload = call_args.kwargs["json"]
                # Only user message should be included
                assert len(payload["messages"]) == 1
                assert payload["messages"][0]["role"] == "user"
                assert payload["messages"][0]["content"] == "User message"
                assert result == "test response"


@pytest.mark.integration
class TestKimiIntegration:
    """Integration tests for Kimi Coding provider."""

    def test_real_api_call(self):
        """Test actual Kimi Coding API call with valid credentials."""
        api_key = os.getenv("KIMI_CODING_API_KEY")
        if not api_key:
            pytest.skip("KIMI_CODING_API_KEY not set - skipping real API test")

        messages = [{"role": "user", "content": "Say 'test success' and nothing else."}]
        response = call_kimi_coding_api(model="kimi-coding", messages=messages, temperature=1.0, max_tokens=50)

        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
