"""Tests for Together AI provider."""

import os
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from gac.errors import AIError
from gac.providers import PROVIDER_REGISTRY
from tests.provider_test_utils import assert_missing_api_key_error, temporarily_remove_env_var
from tests.providers.conftest import BaseProviderTest


class TestTogetherAIImports:
    """Test that Together AI provider can be imported."""

    def test_import_provider(self):
        """Test that Together AI provider module can be imported."""
        from gac.providers import together  # noqa: F401

    def test_provider_in_registry(self):
        """Test that provider is registered."""
        from gac.providers import PROVIDER_REGISTRY

        assert "together" in PROVIDER_REGISTRY


class TestTogetherAIAPIKeyValidation:
    """Test Together AI API key validation."""

    def test_missing_api_key_error(self):
        """Test that Together AI raises error when API key is missing."""
        with temporarily_remove_env_var("TOGETHER_API_KEY"):
            with pytest.raises(AIError) as exc_info:
                PROVIDER_REGISTRY["together"]("openai/gpt-oss-20B", [], 0.7, 1000)

            assert_missing_api_key_error(exc_info, "together", "TOGETHER_API_KEY")


class TestTogetherAIProviderMocked(BaseProviderTest):
    """Mocked tests for Together AI provider."""

    @property
    def provider_name(self) -> str:
        return "together"

    @property
    def provider_module(self) -> str:
        return "gac.providers.together"

    @property
    def api_function(self) -> Callable:
        return PROVIDER_REGISTRY["together"]

    @property
    def api_key_env_var(self) -> str | None:
        return "TOGETHER_API_KEY"

    @property
    def model_name(self) -> str:
        return "openai/gpt-oss-20B"

    @property
    def success_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": "feat: Add new feature"}}]}

    @property
    def empty_content_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": ""}}]}


class TestTogetherAIEdgeCases:
    """Test edge cases for Together AI provider."""

    def test_together_null_content(self):
        """Test handling of null content."""
        with patch.dict("os.environ", {"TOGETHER_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"choices": [{"message": {"content": None}}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    PROVIDER_REGISTRY["together"]("openai/gpt-oss-20B", [], 0.7, 1000)

                assert "null content" in str(exc_info.value).lower()


@pytest.mark.integration
class TestTogetherAIIntegration:
    """Integration tests for Together AI provider."""

    def test_real_api_call(self):
        """Test actual Together AI API call with valid credentials."""
        api_key = os.getenv("TOGETHER_API_KEY")
        if not api_key:
            pytest.skip("TOGETHER_API_KEY not set - skipping real API test")

        messages = [{"role": "user", "content": "Say 'test success' and nothing else."}]
        response = PROVIDER_REGISTRY["together"](
            model="openai/gpt-oss-20B",
            messages=messages,
            temperature=1.0,
            max_tokens=512,
        )

        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
