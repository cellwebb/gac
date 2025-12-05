"""Tests for Cerebras provider."""

import os
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from gac.errors import AIError
from gac.providers.cerebras import call_cerebras_api
from tests.provider_test_utils import assert_missing_api_key_error, temporarily_remove_env_var
from tests.providers.conftest import BaseProviderTest


class TestCerebrasImports:
    """Test that Cerebras provider can be imported."""

    def test_import_provider(self):
        """Test that Cerebras provider module can be imported."""
        from gac.providers import cerebras  # noqa: F401

    def test_import_api_function(self):
        """Test that Cerebras API function can be imported."""
        from gac.providers.cerebras import call_cerebras_api  # noqa: F401


class TestCerebrasAPIKeyValidation:
    """Test Cerebras API key validation."""

    def test_missing_api_key_error(self):
        """Test that Cerebras raises error when API key is missing."""
        with temporarily_remove_env_var("CEREBRAS_API_KEY"):
            with pytest.raises(AIError) as exc_info:
                call_cerebras_api("zai-glm-4.6", [], 0.7, 1000)

            assert_missing_api_key_error(exc_info, "cerebras", "CEREBRAS_API_KEY")


class TestCerebrasProviderMocked(BaseProviderTest):
    """Mocked tests for Cerebras provider."""

    @property
    def provider_name(self) -> str:
        return "cerebras"

    @property
    def provider_module(self) -> str:
        return "gac.providers.cerebras"

    @property
    def api_function(self) -> Callable:
        return call_cerebras_api

    @property
    def api_key_env_var(self) -> str | None:
        return "CEREBRAS_API_KEY"

    @property
    def model_name(self) -> str:
        return "zai-glm-4.6"

    @property
    def success_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": "feat: Add new feature"}}]}

    @property
    def empty_content_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": ""}}]}


class TestCerebrasEdgeCases:
    """Test edge cases for Cerebras provider."""

    def test_cerebras_null_content(self):
        """Test handling of null content."""
        with patch.dict("os.environ", {"CEREBRAS_API_KEY": "test-key"}):
            with patch("gac.providers.base.httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"choices": [{"message": {"content": None}}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    call_cerebras_api("zai-glm-4.6", [], 0.7, 1000)

                assert "null content" in str(exc_info.value).lower()


@pytest.mark.integration
class TestCerebrasIntegration:
    """Integration tests for Cerebras provider."""

    def test_real_api_call(self):
        """Test actual Cerebras API call with valid credentials."""
        api_key = os.getenv("CEREBRAS_API_KEY")
        if not api_key:
            pytest.skip("CEREBRAS_API_KEY not set - skipping real API test")

        messages = [{"role": "user", "content": "Say 'test success' and nothing else."}]
        try:
            response = call_cerebras_api(model="zai-glm-4.6", messages=messages, temperature=1.0, max_tokens=50)

            assert response is not None
            assert isinstance(response, str)
            assert len(response) > 0
        except AIError as e:
            error_str = str(e).lower()
            if "429" in error_str or "rate limit" in error_str or "quota" in error_str:
                pytest.skip(f"Cerebras API rate limit exceeded - skipping real API test: {e}")
            raise
