"""Tests for Fireworks AI provider."""

import os
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from gac.errors import AIError
from gac.providers import PROVIDER_REGISTRY
from tests.provider_test_utils import assert_missing_api_key_error, temporarily_remove_env_var
from tests.providers.conftest import BaseProviderTest


class TestFireworksImports:
    """Test that Fireworks AI provider can be imported."""

    def test_import_provider(self):
        """Test that Fireworks AI provider module can be imported."""
        from gac.providers import fireworks  # noqa: F401

    def test_provider_in_registry(self):
        """Test that provider is registered."""
        from gac.providers import PROVIDER_REGISTRY

        assert "fireworks" in PROVIDER_REGISTRY


class TestFireworksAPIKeyValidation:
    """Test Fireworks AI API key validation."""

    def test_missing_api_key_error(self):
        """Test that Fireworks AI raises error when API key is missing."""
        with temporarily_remove_env_var("FIREWORKS_API_KEY"):
            with pytest.raises(AIError) as exc_info:
                PROVIDER_REGISTRY["fireworks"]("accounts/fireworks/models/gpt-oss-20b", [], 0.7, 1000)

            assert_missing_api_key_error(exc_info, "fireworks", "FIREWORKS_API_KEY")


class TestFireworksProviderMocked(BaseProviderTest):
    """Mocked tests for Fireworks AI provider."""

    @property
    def provider_name(self) -> str:
        return "fireworks"

    @property
    def provider_module(self) -> str:
        return "gac.providers.fireworks"

    @property
    def api_function(self) -> Callable:
        return PROVIDER_REGISTRY["fireworks"]

    @property
    def api_key_env_var(self) -> str | None:
        return "FIREWORKS_API_KEY"

    @property
    def model_name(self) -> str:
        return "accounts/fireworks/models/gpt-oss-20b"

    @property
    def success_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": "feat: Add new feature"}}]}

    @property
    def empty_content_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": ""}}]}


class TestFireworksEdgeCases:
    """Test edge cases for Fireworks provider."""

    def test_fireworks_null_content(self):
        """Test handling of null content."""
        with patch.dict("os.environ", {"FIREWORKS_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"choices": [{"message": {"content": None}}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    PROVIDER_REGISTRY["fireworks"]("accounts/fireworks/models/gpt-oss-20b", [], 0.7, 1000)

                assert "null content" in str(exc_info.value).lower()


@pytest.mark.integration
class TestFireworksIntegration:
    """Integration tests for Fireworks AI provider."""

    def test_real_api_call(self):
        """Test actual Fireworks AI API call with valid credentials."""
        api_key = os.getenv("FIREWORKS_API_KEY")
        if not api_key:
            pytest.skip("FIREWORKS_API_KEY not set - skipping real API test")

        messages = [{"role": "user", "content": "Say 'test success' and nothing else."}]
        response = PROVIDER_REGISTRY["fireworks"](
            model="accounts/fireworks/models/gpt-oss-20b",
            messages=messages,
            temperature=1.0,
            max_tokens=1024,  # gpt-oss-20b needs extra tokens for reasoning
        )

        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
