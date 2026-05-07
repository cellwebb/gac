"""Tests for Crof.ai provider."""

import os
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from gac.errors import AIError
from gac.providers import PROVIDER_REGISTRY
from tests.provider_test_utils import assert_missing_api_key_error, temporarily_remove_env_var
from tests.providers.conftest import BaseProviderTest

call_crof_api = PROVIDER_REGISTRY["crof"]


class TestCrofImports:
    """Test that Crof.ai provider can be imported."""

    def test_import_provider(self):
        """Test that Crof.ai provider module can be imported."""
        from gac.providers import crof  # noqa: F401

    def test_provider_in_registry(self):
        """Test that Crof.ai provider is in the registry."""
        assert "crof" in PROVIDER_REGISTRY


class TestCrofAPIKeyValidation:
    """Test Crof.ai API key validation."""

    def test_missing_api_key_error(self):
        """Test that Crof.ai raises error when API key is missing."""
        with temporarily_remove_env_var("CROF_API_KEY"):
            with pytest.raises(AIError) as exc_info:
                call_crof_api("deepseek-v3.2", [], 0.7, 1000)

            assert_missing_api_key_error(exc_info, "crof", "CROF_API_KEY")


class TestCrofProviderMocked(BaseProviderTest):
    """Mocked tests for Crof.ai provider."""

    @property
    def provider_name(self) -> str:
        return "crof"

    @property
    def provider_module(self) -> str:
        return "gac.providers.crof"

    @property
    def api_function(self) -> Callable:
        return PROVIDER_REGISTRY["crof"]

    @property
    def api_key_env_var(self) -> str | None:
        return "CROF_API_KEY"

    @property
    def model_name(self) -> str:
        return "deepseek-v3.2"

    @property
    def success_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": "feat: Add new feature"}}]}

    @property
    def empty_content_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": ""}}]}


class TestCrofEdgeCases:
    """Test edge cases for Crof provider."""

    def test_crof_null_content(self):
        """Test handling of null content."""
        with patch.dict("os.environ", {"CROF_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"choices": [{"message": {"content": None}}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    call_crof_api("deepseek-v3.2", [], 0.7, 1000)

                assert "null content" in str(exc_info.value).lower()


@pytest.mark.integration
class TestCrofIntegration:
    """Integration tests for Crof.ai provider."""

    def test_real_api_call(self):
        """Test actual Crof.ai API call with valid credentials."""
        api_key = os.getenv("CROF_API_KEY")
        if not api_key:
            pytest.skip("CROF_API_KEY not set - skipping real API test")

        messages = [{"role": "user", "content": "Say 'test success' and nothing else."}]
        try:
            response = call_crof_api(
                model="deepseek-v3.2",
                messages=messages,
                temperature=1.0,
                max_tokens=1024,
            )

            assert response is not None
            assert isinstance(response, tuple)
            assert len(response[0]) > 0
        except AIError as e:
            error_str = str(e).lower()
            if "401" in error_str or "unauthorized" in error_str or "auth" in error_str:
                pytest.skip(f"Crof.ai API authentication failed - skipping real API test: {e}")
            elif "429" in error_str or "rate limit" in error_str:
                pytest.skip(f"Crof.ai API rate limit exceeded - skipping real API test: {e}")
            elif (
                "502" in error_str
                or "503" in error_str
                or "service unavailable" in error_str
                or "connection error" in error_str
            ):
                pytest.skip(f"Crof.ai API service unavailable - skipping real API test: {e}")
            raise
