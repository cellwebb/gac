"""Tests for Chutes.ai provider."""

import os
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from gac.errors import AIError
from gac.providers import PROVIDER_REGISTRY
from tests.provider_test_utils import assert_missing_api_key_error, temporarily_remove_env_var
from tests.providers.conftest import BaseProviderTest

call_chutes_api = PROVIDER_REGISTRY["chutes"]


class TestChutesImports:
    """Test that Chutes.ai provider can be imported."""

    def test_import_provider(self):
        """Test that Chutes.ai provider module can be imported."""
        from gac.providers import chutes  # noqa: F401

    def test_provider_in_registry(self):
        """Test that Chutes.ai provider is in the registry."""
        assert "chutes" in PROVIDER_REGISTRY


class TestChutesAPIKeyValidation:
    """Test Chutes.ai API key validation."""

    def test_missing_api_key_error(self):
        """Test that Chutes.ai raises error when API key is missing."""
        with temporarily_remove_env_var("CHUTES_API_KEY"):
            with pytest.raises(AIError) as exc_info:
                call_chutes_api("zai-org/GLM-4.5-Air", [], 0.7, 1000)

            assert_missing_api_key_error(exc_info, "chutes", "CHUTES_API_KEY")


class TestChutesProviderMocked(BaseProviderTest):
    """Mocked tests for Chutes.ai provider."""

    @property
    def provider_name(self) -> str:
        return "chutes"

    @property
    def provider_module(self) -> str:
        return "gac.providers.chutes"

    @property
    def api_function(self) -> Callable:
        return PROVIDER_REGISTRY["chutes"]

    @property
    def api_key_env_var(self) -> str | None:
        return "CHUTES_API_KEY"

    @property
    def model_name(self) -> str:
        return "zai-org/GLM-4.5-Air"

    @property
    def success_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": "feat: Add new feature"}}]}

    @property
    def empty_content_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": ""}}]}


class TestChutesEdgeCases:
    """Test edge cases for Chutes provider."""

    def test_chutes_null_content(self):
        """Test handling of null content."""
        with patch.dict("os.environ", {"CHUTES_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"choices": [{"message": {"content": None}}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    call_chutes_api("zai-org/GLM-4.5-Air", [], 0.7, 1000)

                assert "null content" in str(exc_info.value).lower()


@pytest.mark.integration
class TestChutesIntegration:
    """Integration tests for Chutes.ai provider."""

    def test_real_api_call(self):
        """Test actual Chutes.ai API call with valid credentials."""
        api_key = os.getenv("CHUTES_API_KEY")
        if not api_key:
            pytest.skip("CHUTES_API_KEY not set - skipping real API test")

        messages = [{"role": "user", "content": "Say 'test success' and nothing else."}]
        try:
            response = call_chutes_api(
                model="zai-org/GLM-4.5-Air",
                messages=messages,
                temperature=1.0,
                max_tokens=1024,  # glm-4.5-air needs extra tokens for reasoning
            )

            assert response is not None
            assert isinstance(response, str)
            assert len(response) > 0
        except AIError as e:
            error_str = str(e).lower()
            if "401" in error_str or "unauthorized" in error_str or "auth" in error_str:
                pytest.skip(f"Chutes.ai API authentication failed - skipping real API test: {e}")
            elif "429" in error_str or "rate limit" in error_str:
                pytest.skip(f"Chutes.ai API rate limit exceeded - skipping real API test: {e}")
            elif (
                "502" in error_str
                or "503" in error_str
                or "service unavailable" in error_str
                or "connection error" in error_str
            ):
                pytest.skip(f"Chutes.ai API service unavailable - skipping real API test: {e}")
            raise
