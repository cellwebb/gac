"""Tests for Groq provider."""

import os
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from gac.errors import AIError
from gac.providers.groq import call_groq_api
from tests.provider_test_utils import assert_missing_api_key_error, temporarily_remove_env_var
from tests.providers.conftest import BaseProviderTest


class TestGroqImports:
    """Test that Groq provider can be imported."""

    def test_import_provider(self):
        """Test that Groq provider module can be imported."""
        from gac.providers import groq  # noqa: F401

    def test_import_api_function(self):
        """Test that Groq API function can be imported."""
        from gac.providers.groq import call_groq_api  # noqa: F401


class TestGroqAPIKeyValidation:
    """Test Groq API key validation."""

    def test_missing_api_key_error(self):
        """Test that Groq raises error when API key is missing."""
        with temporarily_remove_env_var("GROQ_API_KEY"):
            with pytest.raises(AIError) as exc_info:
                call_groq_api("llama-3.1-70b", [], 0.7, 1000)

            assert_missing_api_key_error(exc_info, "groq", "GROQ_API_KEY")


class TestGroqProviderMocked(BaseProviderTest):
    """Mocked tests for Groq provider."""

    @property
    def provider_name(self) -> str:
        return "groq"

    @property
    def provider_module(self) -> str:
        return "gac.providers.groq"

    @property
    def api_function(self) -> Callable:
        return call_groq_api

    @property
    def api_key_env_var(self) -> str | None:
        return "GROQ_API_KEY"

    @property
    def model_name(self) -> str:
        return "llama-3.1-70b"

    @property
    def success_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": "feat: Add new feature"}}]}

    @property
    def empty_content_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": ""}}]}


class TestGroqEdgeCases:
    """Test edge cases for Groq provider."""

    def test_groq_null_content_in_choice_text(self):
        """Test handling of null content in choice.text field."""
        with patch("httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"choices": [{"text": None}]}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            # This should return empty string for None in text field
            result = call_groq_api("llama-3.1-70b", [], 0.7, 1000)
            assert result == ""

    def test_groq_text_field_with_content(self):
        """Test handling of valid content in choice.text field."""
        with patch("httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"choices": [{"text": "test content from text field"}]}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            result = call_groq_api("llama-3.1-70b", [], 0.7, 1000)
            assert result == "test content from text field"

    def test_groq_unexpected_choice_structure(self):
        """Test handling of unexpected choice structure without message or text."""
        with patch("httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"choices": [{"unexpected_field": "value"}]}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            with pytest.raises(AIError) as exc_info:
                call_groq_api("llama-3.1-70b", [], 0.7, 1000)

            assert "Unexpected response format" in str(exc_info.value)

    def test_groq_missing_choices(self):
        """Test handling of response without choices field."""
        with patch("httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"some_other_field": "value"}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            with pytest.raises(AIError) as exc_info:
                call_groq_api("llama-3.1-70b", [], 0.7, 1000)

            assert "Unexpected response format" in str(exc_info.value)

    def test_groq_empty_choices_array(self):
        """Test handling of empty choices array."""
        with patch("httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"choices": []}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            with pytest.raises(AIError) as exc_info:
                call_groq_api("llama-3.1-70b", [], 0.7, 1000)

            assert "Unexpected response format" in str(exc_info.value)

    def test_groq_null_content_in_message(self):
        """Test handling of null content in message.content field."""
        with patch("httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"choices": [{"message": {"content": None}}]}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            with pytest.raises(AIError) as exc_info:
                call_groq_api("llama-3.1-70b", [], 0.7, 1000)

            assert "null content" in str(exc_info.value).lower()


@pytest.mark.integration
class TestGroqIntegration:
    """Integration tests for Groq provider."""

    def test_real_api_call(self):
        """Test actual Groq API call with valid credentials."""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            pytest.skip("GROQ_API_KEY not set - skipping real API test")

        messages = [{"role": "user", "content": "Say 'test success' and nothing else."}]
        response = call_groq_api(model="llama-3.3-70b-versatile", messages=messages, temperature=1.0, max_tokens=50)

        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
