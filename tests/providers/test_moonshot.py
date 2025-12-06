"""Tests for Moonshot AI provider."""

import os
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from gac.errors import AIError
from gac.providers import PROVIDER_REGISTRY
from tests.provider_test_utils import assert_missing_api_key_error, temporarily_remove_env_var
from tests.providers.conftest import BaseProviderTest


class TestMoonshotImports:
    """Test that Moonshot AI provider can be imported."""

    def test_import_provider(self):
        """Test that Moonshot AI provider module can be imported."""
        from gac.providers import moonshot  # noqa: F401

    def test_provider_in_registry(self):
        """Test that provider is registered."""
        from gac.providers import PROVIDER_REGISTRY

        assert "moonshot" in PROVIDER_REGISTRY


class TestMoonshotAPIKeyValidation:
    """Test Moonshot AI API key validation."""

    def test_missing_api_key_error(self):
        """Test that Moonshot AI raises error when API key is missing."""
        with temporarily_remove_env_var("MOONSHOT_API_KEY"):
            with pytest.raises(AIError) as exc_info:
                PROVIDER_REGISTRY["moonshot"]("kimi-k2-turbo-preview", [], 0.7, 1000)

            assert_missing_api_key_error(exc_info, "moonshot", "MOONSHOT_API_KEY")


class TestMoonshotProviderMocked(BaseProviderTest):
    """Mocked tests for Moonshot AI provider."""

    @property
    def provider_name(self) -> str:
        return "moonshot"

    @property
    def provider_module(self) -> str:
        return "gac.providers.moonshot"

    @property
    def api_function(self) -> Callable:
        return PROVIDER_REGISTRY["moonshot"]

    @property
    def api_key_env_var(self) -> str | None:
        return "MOONSHOT_API_KEY"

    @property
    def model_name(self) -> str:
        return "kimi-k2-turbo-preview"

    @property
    def success_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": "feat: Add new feature"}}]}

    @property
    def empty_content_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": ""}}]}


class TestMoonshotEdgeCases:
    """Test edge cases for Moonshot AI provider."""

    def test_moonshot_null_content(self):
        """Test handling of null content."""
        with patch.dict("os.environ", {"MOONSHOT_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"choices": [{"message": {"content": None}}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    PROVIDER_REGISTRY["moonshot"]("kimi-k2-turbo-preview", [], 0.7, 1000)

                assert "null content" in str(exc_info.value).lower()


@pytest.mark.integration
class TestMoonshotIntegration:
    """Integration tests for Moonshot AI provider."""

    def test_real_api_call(self):
        """Test actual Moonshot AI API call with valid credentials."""
        api_key = os.getenv("MOONSHOT_API_KEY")
        if not api_key:
            pytest.skip("MOONSHOT_API_KEY not set - skipping real API test")

        messages = [{"role": "user", "content": "Say 'test success' and nothing else."}]
        response = PROVIDER_REGISTRY["moonshot"](
            model="kimi-k2-turbo-preview",
            messages=messages,
            temperature=1.0,
            max_tokens=512,
        )

        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
