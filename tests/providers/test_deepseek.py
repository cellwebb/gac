"""Tests for DeepSeek provider."""

import os
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from gac.errors import AIError
from gac.providers import PROVIDER_REGISTRY
from tests.provider_test_utils import assert_missing_api_key_error, temporarily_remove_env_var
from tests.providers.conftest import BaseProviderTest


class TestDeepSeekImports:
    """Test that DeepSeek provider can be imported."""

    def test_import_provider(self):
        """Test that DeepSeek provider module can be imported."""
        from gac.providers import deepseek  # noqa: F401

    def test_provider_in_registry(self):
        """Test that provider is registered."""
        from gac.providers import PROVIDER_REGISTRY

        assert "deepseek" in PROVIDER_REGISTRY


class TestDeepSeekAPIKeyValidation:
    """Test DeepSeek API key validation."""

    def test_missing_api_key_error(self):
        """Test that DeepSeek raises error when API key is missing."""
        with temporarily_remove_env_var("DEEPSEEK_API_KEY"):
            with pytest.raises(AIError) as exc_info:
                PROVIDER_REGISTRY["deepseek"]("deepseek-chat", [], 0.7, 1000)

            assert_missing_api_key_error(exc_info, "deepseek", "DEEPSEEK_API_KEY")


class TestDeepSeekProviderMocked(BaseProviderTest):
    """Mocked tests for DeepSeek provider."""

    @property
    def provider_name(self) -> str:
        return "deepseek"

    @property
    def provider_module(self) -> str:
        return "gac.providers.deepseek"

    @property
    def api_function(self) -> Callable:
        return PROVIDER_REGISTRY["deepseek"]

    @property
    def api_key_env_var(self) -> str | None:
        return "DEEPSEEK_API_KEY"

    @property
    def model_name(self) -> str:
        return "deepseek-chat"

    @property
    def success_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": "feat: Add new feature"}}]}

    @property
    def empty_content_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": ""}}]}


class TestDeepSeekEdgeCases:
    """Test edge cases for DeepSeek provider."""

    def test_deepseek_null_content(self):
        """Test handling of null content."""
        with patch.dict("os.environ", {"DEEPSEEK_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"choices": [{"message": {"content": None}}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    PROVIDER_REGISTRY["deepseek"]("deepseek-chat", [], 0.7, 1000)

                assert "null content" in str(exc_info.value).lower()


@pytest.mark.integration
class TestDeepSeekIntegration:
    """Integration tests for DeepSeek provider."""

    def test_real_api_call(self):
        """Test actual DeepSeek API call with valid credentials."""
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            pytest.skip("DEEPSEEK_API_KEY not set - skipping real API test")

        messages = [{"role": "user", "content": "Say 'test success' and nothing else."}]
        response = PROVIDER_REGISTRY["deepseek"](
            model="deepseek-chat",
            messages=messages,
            temperature=1.0,
            max_tokens=512,
        )

        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
