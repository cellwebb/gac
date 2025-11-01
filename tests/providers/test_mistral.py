"""Tests for Mistral AI provider."""

import os
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from gac.errors import AIError
from gac.providers.mistral import call_mistral_api
from tests.provider_test_utils import assert_missing_api_key_error, temporarily_remove_env_var
from tests.providers.conftest import BaseProviderTest


class TestMistralImports:
    """Test that Mistral provider can be imported."""

    def test_import_provider(self):
        """Test that Mistral provider module can be imported."""
        from gac.providers import mistral  # noqa: F401

    def test_import_api_function(self):
        """Test that Mistral API function can be imported."""
        from gac.providers.mistral import call_mistral_api  # noqa: F401


class TestMistralAPIKeyValidation:
    """Test Mistral API key validation."""

    def test_missing_api_key_error(self):
        """Mistral should raise an error when API key is missing."""
        with temporarily_remove_env_var("MISTRAL_API_KEY"):
            with pytest.raises(AIError) as exc_info:
                call_mistral_api("mistral-tiny", [], 0.7, 100)

            assert_missing_api_key_error(exc_info, "mistral", "MISTRAL_API_KEY")


class TestMistralProviderMocked(BaseProviderTest):
    """Mocked HTTP tests for Mistral provider."""

    @property
    def provider_name(self) -> str:
        return "mistral"

    @property
    def provider_module(self) -> str:
        return "gac.providers.mistral"

    @property
    def api_function(self) -> Callable:
        return call_mistral_api

    @property
    def api_key_env_var(self) -> str | None:
        return "MISTRAL_API_KEY"

    @property
    def model_name(self) -> str:
        return "mistral-tiny"

    @property
    def success_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": "feat: Add new feature"}}]}

    @property
    def empty_content_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": ""}}]}

    # Inherits 9 standard tests from BaseProviderTest:
    # - test_successful_api_call
    # - test_empty_content_handling
    # - test_http_401_authentication_error
    # - test_http_429_rate_limit_error
    # - test_http_500_server_error
    # - test_http_503_service_unavailable
    # - test_connection_error
    # - test_timeout_error
    # - test_malformed_json_response


class TestMistralEdgeCases:
    """Edge case tests for Mistral provider."""

    def test_mistral_null_content(self):
        """Ensure null content responses raise an AIError."""
        with patch.dict("os.environ", {"MISTRAL_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"choices": [{"message": {"content": None}}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    call_mistral_api("mistral-tiny", [], 0.7, 100)

                assert "null content" in str(exc_info.value).lower()


class TestMistralProviderIntegration:
    """Integration tests with real Mistral API."""

    @pytest.mark.integration
    def test_real_api_call(self):
        """Test actual Mistral API call with valid credentials."""
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            pytest.skip("MISTRAL_API_KEY not set")

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello, Mistral!'"},
        ]

        try:
            response = call_mistral_api(
                model="mistral-tiny",  # Use their smallest model for testing
                messages=messages,
                temperature=0.7,
                max_tokens=10,
            )
            assert isinstance(response, str)
            assert len(response) > 0
            # Should contain some form of greeting
            assert any(word.lower() in response.lower() for word in ["hello", "mistral", "hi"])
        except Exception as e:
            pytest.fail(f"Real Mistral API call failed: {str(e)}")
