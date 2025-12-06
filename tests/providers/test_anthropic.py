"""Tests for Anthropic provider."""

import os
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from gac.errors import AIError
from gac.providers import PROVIDER_REGISTRY
from tests.provider_test_utils import assert_missing_api_key_error, temporarily_remove_env_var
from tests.providers.conftest import BaseProviderTest


class TestAnthropicImports:
    """Test that Anthropic provider can be imported."""

    def test_import_provider(self):
        """Test that Anthropic provider module can be imported."""
        from gac.providers import anthropic  # noqa: F401

    def test_provider_in_registry(self):
        """Test that provider is registered."""
        from gac.providers import PROVIDER_REGISTRY

        assert "anthropic" in PROVIDER_REGISTRY


class TestAnthropicAPIKeyValidation:
    """Test Anthropic API key validation."""

    def test_missing_api_key_error(self):
        """Test that Anthropic raises error when API key is missing."""
        with temporarily_remove_env_var("ANTHROPIC_API_KEY"):
            with pytest.raises(AIError) as exc_info:
                PROVIDER_REGISTRY["anthropic"]("claude-3-haiku-20240307", [], 0.7, 1000)

            assert_missing_api_key_error(exc_info, "anthropic", "ANTHROPIC_API_KEY")


class TestAnthropicProviderMocked(BaseProviderTest):
    """Mocked tests for Anthropic provider."""

    @property
    def provider_name(self) -> str:
        return "anthropic"

    @property
    def provider_module(self) -> str:
        return "gac.providers.anthropic"

    @property
    def api_function(self) -> Callable:
        return PROVIDER_REGISTRY["anthropic"]

    @property
    def api_key_env_var(self) -> str | None:
        return "ANTHROPIC_API_KEY"

    @property
    def model_name(self) -> str:
        return "claude-3"

    @property
    def success_response(self) -> dict[str, Any]:
        return {"content": [{"text": "feat: Add new feature"}]}

    @property
    def empty_content_response(self) -> dict[str, Any]:
        return {"content": [{"text": ""}]}


class TestAnthropicEdgeCases:
    """Test edge cases for Anthropic provider."""

    def test_anthropic_missing_content(self):
        """Test handling of response without content field."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("gac.providers.base.httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"some_other_field": "value"}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    PROVIDER_REGISTRY["anthropic"]("claude-3-haiku-20240307", [], 0.7, 1000)

                # Should raise a model error for missing content
                assert exc_info.value.error_type == "model"

    def test_anthropic_empty_content_array(self):
        """Test handling of empty content array."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("gac.providers.base.httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"content": []}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    PROVIDER_REGISTRY["anthropic"]("claude-3-haiku-20240307", [], 0.7, 1000)

                # Should raise an error for empty content array
                assert exc_info.value.error_type == "model"

    def test_anthropic_missing_text_field(self):
        """Test handling of content without text field."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("gac.providers.base.httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"content": [{"no_text": "here"}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    PROVIDER_REGISTRY["anthropic"]("claude-3-haiku-20240307", [], 0.7, 1000)

                # Should raise an error for missing text field
                assert exc_info.value.error_type == "model"

    def test_anthropic_null_text_content(self):
        """Test handling of null text in content."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("gac.providers.base.httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"content": [{"text": None}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    PROVIDER_REGISTRY["anthropic"]("claude-3-haiku-20240307", [], 0.7, 1000)

                assert "null content" in str(exc_info.value).lower()

    def test_anthropic_system_message_handling(self):
        """Test system message extraction and formatting."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("gac.providers.base.httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"content": [{"text": "test response"}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                messages = [
                    {"role": "system", "content": "System instruction"},
                    {"role": "user", "content": "User message"},
                ]

                result = PROVIDER_REGISTRY["anthropic"]("claude-3-haiku-20240307", messages, 0.7, 1000)

                # Verify the payload structure
                call_args = mock_post.call_args
                payload = call_args.kwargs["json"]
                # System message should be extracted to separate field
                assert "system" in payload
                assert payload["system"] == "System instruction"
                # Messages should only contain non-system messages
                assert len(payload["messages"]) == 1
                assert payload["messages"][0]["role"] == "user"
                assert result == "test response"

    def test_anthropic_no_system_message(self):
        """Test that system field is not included when no system message."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("gac.providers.base.httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"content": [{"text": "test response"}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                messages = [{"role": "user", "content": "User message"}]

                result = PROVIDER_REGISTRY["anthropic"]("claude-3-haiku-20240307", messages, 0.7, 1000)

                # Verify the payload structure
                call_args = mock_post.call_args
                payload = call_args.kwargs["json"]
                # System field should not be present
                assert "system" not in payload
                assert len(payload["messages"]) == 1
                assert result == "test response"


@pytest.mark.integration
class TestAnthropicIntegration:
    """Integration tests for Anthropic provider."""

    def test_real_api_call(self):
        """Test actual Anthropic API call with valid credentials."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            pytest.skip("ANTHROPIC_API_KEY not set - skipping real API test")

        messages = [{"role": "user", "content": "Say 'test success' and nothing else."}]
        response = PROVIDER_REGISTRY["anthropic"](
            model="claude-3-haiku-20240307", messages=messages, temperature=1.0, max_tokens=50
        )

        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
