"""Tests for ZAI provider."""

import os
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from gac.errors import AIError
from gac.providers import PROVIDER_REGISTRY
from tests.provider_test_utils import (
    assert_missing_api_key_error,
    temporarily_remove_env_var,
    temporarily_set_env_var,
)
from tests.providers.conftest import BaseProviderTest

call_zai_api = PROVIDER_REGISTRY["zai"]
call_zai_coding_api = PROVIDER_REGISTRY["zai-coding"]


class TestZAIImports:
    """Test that ZAI provider can be imported."""

    def test_import_provider(self):
        """Test that ZAI provider module can be imported."""
        from gac.providers import zai  # noqa: F401

    def test_providers_in_registry(self):
        """Test that ZAI providers are in the registry."""
        assert "zai" in PROVIDER_REGISTRY
        assert "zai-coding" in PROVIDER_REGISTRY


class TestZAIAPIKeyValidation:
    """Test ZAI API key validation."""

    def test_missing_api_key_error(self):
        """Test that ZAI raises error when API key is missing."""
        with temporarily_remove_env_var("ZAI_API_KEY"):
            with pytest.raises(AIError) as exc_info:
                call_zai_api("glm-4.5-air", [], 0.7, 1000)

            assert_missing_api_key_error(exc_info, "zai", "ZAI_API_KEY")

    def test_coding_function_missing_api_key(self):
        """Test that ZAI's coding function raises error when API key is missing."""
        with temporarily_remove_env_var("ZAI_API_KEY"):
            with pytest.raises(AIError) as exc_info:
                call_zai_coding_api("glm-4.5-air", [], 0.7, 1000)

            assert_missing_api_key_error(exc_info, "zai", "ZAI_API_KEY")


class TestZAIProviderMocked(BaseProviderTest):
    """Mocked tests for ZAI provider."""

    @property
    def provider_name(self) -> str:
        return "zai"

    @property
    def provider_module(self) -> str:
        return "gac.providers.zai"

    @property
    def api_function(self) -> Callable:
        return PROVIDER_REGISTRY["zai"]

    @property
    def api_key_env_var(self) -> str | None:
        return "ZAI_API_KEY"

    @property
    def model_name(self) -> str:
        return "glm-4.5-air"

    @property
    def success_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": "feat: Add new feature"}}]}

    @property
    def empty_content_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": ""}}]}


class TestZAICodingProviderMocked(BaseProviderTest):
    """Mocked tests for ZAI-coding provider."""

    @property
    def provider_name(self) -> str:
        return "zai-coding"

    @property
    def provider_module(self) -> str:
        return "gac.providers.zai"

    @property
    def api_function(self) -> Callable:
        return PROVIDER_REGISTRY["zai-coding"]

    @property
    def api_key_env_var(self) -> str | None:
        return "ZAI_API_KEY"

    @property
    def model_name(self) -> str:
        return "glm-4.5-air"

    @property
    def success_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": "feat: Add new feature"}}]}

    @property
    def empty_content_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": ""}}]}


class TestZAIEdgeCases:
    """Test edge cases for ZAI provider."""

    @pytest.fixture(autouse=True)
    def _set_api_key(self):
        """Ensure ZAI API key is present for edge case tests."""
        with temporarily_set_env_var("ZAI_API_KEY", "test-key"):
            yield

    def test_zai_missing_choices(self):
        """Test handling of response without choices field."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"some_other_field": "value"}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            with pytest.raises(AIError) as exc_info:
                call_zai_api("glm-4.5-air", [], 0.7, 1000)

            assert "invalid response" in str(exc_info.value).lower() or "missing" in str(exc_info.value).lower()

    def test_zai_empty_choices(self):
        """Test handling of empty choices array."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"choices": []}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            with pytest.raises(AIError) as exc_info:
                call_zai_api("glm-4.5-air", [], 0.7, 1000)

            assert "invalid response" in str(exc_info.value).lower() or "missing" in str(exc_info.value).lower()

    def test_zai_missing_message(self):
        """Test handling of choice without message field."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"choices": [{"no_message": "here"}]}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            with pytest.raises(AIError) as exc_info:
                call_zai_api("glm-4.5-air", [], 0.7, 1000)

            assert "invalid response" in str(exc_info.value).lower() or "missing" in str(exc_info.value).lower()

    def test_zai_missing_content(self):
        """Test handling of message without content field."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"choices": [{"message": {"no_content": "here"}}]}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            with pytest.raises(AIError) as exc_info:
                call_zai_api("glm-4.5-air", [], 0.7, 1000)

            assert "invalid response" in str(exc_info.value).lower() or "missing" in str(exc_info.value).lower()

    def test_zai_null_content(self):
        """Test handling of null content."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"choices": [{"message": {"content": None}}]}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            with pytest.raises(AIError) as exc_info:
                call_zai_api("glm-4.5-air", [], 0.7, 1000)

            assert "null content" in str(exc_info.value).lower()

    def test_zai_coding_api_edge_case(self):
        """Test that coding API also handles edge cases correctly."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"choices": []}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            with pytest.raises(AIError) as exc_info:
                call_zai_coding_api("glm-4.5-air", [], 0.7, 1000)

            assert "invalid response" in str(exc_info.value).lower() or "missing" in str(exc_info.value).lower()


@pytest.mark.integration
class TestZAIIntegration:
    """Integration tests for ZAI provider."""

    def test_real_api_call(self):
        """Test actual Z.AI API call with valid credentials."""
        api_key = os.getenv("ZAI_API_KEY")
        if not api_key:
            pytest.skip("ZAI_API_KEY not set - skipping real API test")

        messages = [{"role": "user", "content": "Say 'test success' and nothing else."}]
        try:
            response = call_zai_api(model="glm-4.5-air", messages=messages, temperature=1.0, max_tokens=50)

            assert response is not None
            assert isinstance(response, str)
            assert len(response) > 0
        except Exception as e:
            if "empty content" in str(e) or "null content" in str(e):
                pytest.skip(f"Z.AI API returned empty content - possible configuration issue: {e}")
            else:
                raise
