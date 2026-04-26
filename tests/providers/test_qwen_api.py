"""Tests for Qwen Cloud API providers (qwen-api intl and qwen-api-cn mainland)."""

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

call_qwen_api = PROVIDER_REGISTRY["qwen-api"]
call_qwen_api_cn = PROVIDER_REGISTRY["qwen-api-cn"]


class TestQwenAPIImports:
    """Test that Qwen API providers can be imported and registered."""

    def test_import_provider(self):
        """Test that qwen provider module can be imported."""
        from gac.providers import qwen  # noqa: F401

    def test_providers_in_registry(self):
        """Test that qwen-api providers are in the registry."""
        assert "qwen-api" in PROVIDER_REGISTRY
        assert "qwen-api-cn" in PROVIDER_REGISTRY


class TestQwenAPIKeyValidation:
    """Test Qwen API key validation."""

    def test_qwen_api_missing_api_key_error(self):
        """Test that qwen-api raises error when API key is missing."""
        with temporarily_remove_env_var("QWEN_API_KEY"):
            with pytest.raises(AIError) as exc_info:
                call_qwen_api("qwen3-max", [], 0.7, 1000)

            assert_missing_api_key_error(exc_info, "qwen", "QWEN_API_KEY")

    def test_qwen_api_cn_missing_api_key_error(self):
        """Test that qwen-api-cn raises error when API key is missing."""
        with temporarily_remove_env_var("QWEN_API_KEY"):
            with pytest.raises(AIError) as exc_info:
                call_qwen_api_cn("qwen3-max", [], 0.7, 1000)

            assert_missing_api_key_error(exc_info, "qwen", "QWEN_API_KEY")


class TestQwenAPIProviderMocked(BaseProviderTest):
    """Mocked tests for Qwen API (international) provider."""

    @property
    def provider_name(self) -> str:
        return "qwen-api"

    @property
    def provider_module(self) -> str:
        return "gac.providers.qwen"

    @property
    def api_function(self) -> Callable:
        return PROVIDER_REGISTRY["qwen-api"]

    @property
    def api_key_env_var(self) -> str | None:
        return "QWEN_API_KEY"

    @property
    def model_name(self) -> str:
        return "qwen3-max"

    @property
    def success_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": "feat: Add new feature"}}]}

    @property
    def empty_content_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": ""}}]}


class TestQwenAPICNProviderMocked(BaseProviderTest):
    """Mocked tests for Qwen API (mainland China) provider."""

    @property
    def provider_name(self) -> str:
        return "qwen-api-cn"

    @property
    def provider_module(self) -> str:
        return "gac.providers.qwen"

    @property
    def api_function(self) -> Callable:
        return PROVIDER_REGISTRY["qwen-api-cn"]

    @property
    def api_key_env_var(self) -> str | None:
        return "QWEN_API_KEY"

    @property
    def model_name(self) -> str:
        return "qwen3-max"

    @property
    def success_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": "feat: Add new feature"}}]}

    @property
    def empty_content_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": ""}}]}


class TestQwenAPIEndpointURLs:
    """Verify each provider hits its region-specific endpoint."""

    @pytest.fixture(autouse=True)
    def _set_api_key(self):
        with temporarily_set_env_var("QWEN_API_KEY", "test-key"):
            yield

    def test_qwen_api_uses_intl_endpoint(self):
        """qwen-api should POST to the dashscope-intl endpoint."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"choices": [{"message": {"content": "ok"}}]}
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            call_qwen_api("qwen3-max", [{"role": "user", "content": "hi"}], 0.7, 100)

            url = mock_post.call_args[0][0]
            assert url == "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions"

    def test_qwen_api_cn_uses_mainland_endpoint(self):
        """qwen-api-cn should POST to the dashscope (CN) endpoint."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"choices": [{"message": {"content": "ok"}}]}
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            call_qwen_api_cn("qwen3-max", [{"role": "user", "content": "hi"}], 0.7, 100)

            url = mock_post.call_args[0][0]
            assert url == "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"


class TestQwenAPIEdgeCases:
    """Test edge cases for Qwen API providers."""

    @pytest.fixture(autouse=True)
    def _set_api_key(self):
        with temporarily_set_env_var("QWEN_API_KEY", "test-key"):
            yield

    def test_qwen_api_missing_choices(self):
        """Test handling of response without choices field."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"some_other_field": "value"}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            with pytest.raises(AIError) as exc_info:
                call_qwen_api("qwen3-max", [], 0.7, 1000)

            assert "invalid response" in str(exc_info.value).lower() or "missing" in str(exc_info.value).lower()

    def test_qwen_api_empty_choices(self):
        """Test handling of empty choices array."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"choices": []}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            with pytest.raises(AIError) as exc_info:
                call_qwen_api("qwen3-max", [], 0.7, 1000)

            assert "invalid response" in str(exc_info.value).lower() or "missing" in str(exc_info.value).lower()

    def test_qwen_api_missing_message(self):
        """Test handling of choice without message field."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"choices": [{"no_message": "here"}]}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            with pytest.raises(AIError) as exc_info:
                call_qwen_api("qwen3-max", [], 0.7, 1000)

            assert "invalid response" in str(exc_info.value).lower() or "missing" in str(exc_info.value).lower()

    def test_qwen_api_missing_content(self):
        """Test handling of message without content field."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"choices": [{"message": {"no_content": "here"}}]}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            with pytest.raises(AIError) as exc_info:
                call_qwen_api("qwen3-max", [], 0.7, 1000)

            assert "invalid response" in str(exc_info.value).lower() or "missing" in str(exc_info.value).lower()

    def test_qwen_api_null_content(self):
        """Test handling of null content."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"choices": [{"message": {"content": None}}]}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            with pytest.raises(AIError) as exc_info:
                call_qwen_api("qwen3-max", [], 0.7, 1000)

            assert "null content" in str(exc_info.value).lower()

    def test_qwen_api_cn_edge_case(self):
        """Test that CN endpoint also handles edge cases correctly."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"choices": []}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            with pytest.raises(AIError) as exc_info:
                call_qwen_api_cn("qwen3-max", [], 0.7, 1000)

            assert "invalid response" in str(exc_info.value).lower() or "missing" in str(exc_info.value).lower()


@pytest.mark.integration
class TestQwenAPIIntegration:
    """Integration tests for Qwen Cloud API (international endpoint)."""

    def test_real_api_call(self):
        """Test actual Qwen Cloud API call with valid credentials."""
        api_key = os.getenv("QWEN_API_KEY")
        if not api_key:
            pytest.skip("QWEN_API_KEY not set - skipping real API test")

        messages = [{"role": "user", "content": "Say 'test success' and nothing else."}]
        try:
            response = call_qwen_api(model="qwen3-max", messages=messages, temperature=1.0, max_tokens=50)

            assert response is not None
            assert isinstance(response, str)
            assert len(response) > 0
        except Exception as e:
            if "empty content" in str(e) or "null content" in str(e):
                pytest.skip(f"Qwen API returned empty content - possible configuration issue: {e}")
            else:
                raise
