"""Tests for Azure OpenAI provider."""

import os
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, patch

import httpx
import pytest

from gac.errors import AIError
from gac.providers import PROVIDER_REGISTRY
from tests.provider_test_utils import assert_missing_api_key_error, temporarily_remove_env_var
from tests.providers.conftest import BaseProviderTest

call_azure_openai_api = PROVIDER_REGISTRY["azure-openai"]


class TestAzureOpenAIImports:
    """Test that Azure OpenAI provider can be imported."""

    def test_import_provider(self):
        """Test that Azure OpenAI provider module can be imported."""

    def test_provider_in_registry(self):
        """Test that Azure OpenAI provider is in the registry."""
        assert "azure-openai" in PROVIDER_REGISTRY


class TestAzureOpenAIAPIKeyValidation:
    """Test Azure OpenAI API key validation."""

    def test_missing_api_key_error(self):
        """Test that Azure OpenAI raises error when API key is missing."""
        with temporarily_remove_env_var("AZURE_OPENAI_API_KEY"):
            with patch.dict(
                os.environ,
                {
                    "AZURE_OPENAI_ENDPOINT": "https://test-resource.openai.azure.com",
                    "AZURE_OPENAI_API_VERSION": "2025-01-01-preview",
                },
            ):
                with pytest.raises(AIError) as exc_info:
                    call_azure_openai_api("gpt-4o", [], 0.7, 1000)

                assert_missing_api_key_error(exc_info, "azure openai", "AZURE_OPENAI_API_KEY")

    def test_missing_endpoint_error(self):
        """Test that Azure OpenAI raises error when endpoint is missing."""
        with temporarily_remove_env_var("AZURE_OPENAI_ENDPOINT"):
            with patch.dict(
                os.environ, {"AZURE_OPENAI_API_KEY": "test-key", "AZURE_OPENAI_API_VERSION": "2025-01-01-preview"}
            ):
                with pytest.raises(AIError) as exc_info:
                    call_azure_openai_api("gpt-4o", [], 0.7, 1000)

                assert exc_info.value.error_type == "model"
                assert "AZURE_OPENAI_ENDPOINT" in str(exc_info.value)

    def test_missing_api_version_error(self):
        """Test that Azure OpenAI raises error when API version is missing."""
        with temporarily_remove_env_var("AZURE_OPENAI_API_VERSION"):
            with patch.dict(
                os.environ,
                {"AZURE_OPENAI_API_KEY": "test-key", "AZURE_OPENAI_ENDPOINT": "https://test-resource.openai.azure.com"},
            ):
                with pytest.raises(AIError) as exc_info:
                    call_azure_openai_api("gpt-4o", [], 0.7, 1000)

                assert exc_info.value.error_type == "model"
                assert "AZURE_OPENAI_API_VERSION" in str(exc_info.value)


class TestAzureOpenAIProviderMocked(BaseProviderTest):
    """Mocked HTTP tests inheriting standard test suite."""

    @property
    def provider_name(self) -> str:
        return "azure-openai"

    @property
    def provider_module(self) -> str:
        return "gac.providers.azure_openai"

    @property
    def api_function(self) -> Callable:
        return PROVIDER_REGISTRY["azure-openai"]

    @property
    def api_key_env_var(self) -> str:
        return "AZURE_OPENAI_API_KEY"

    @property
    def model_name(self) -> str:
        return "gpt-4o"  # Azure OpenAI deployment name

    @property
    def success_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": "feat: Add new Azure feature"}}]}

    @property
    def empty_content_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": ""}}]}

    def test_successful_api_call(self):
        """Test that the provider successfully processes a valid API response."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_post.return_value = self._create_mock_response(self.success_response)

            messages = [{"role": "user", "content": "Generate a commit message"}]

            with patch.dict(
                os.environ,
                {
                    "AZURE_OPENAI_API_KEY": "test-key",
                    "AZURE_OPENAI_ENDPOINT": "https://test-resource.openai.azure.com",
                    "AZURE_OPENAI_API_VERSION": "2025-01-01-preview",
                },
            ):
                result = self.api_function(model=self.model_name, messages=messages, temperature=0.7, max_tokens=100)

            assert result == "feat: Add new Azure feature"
            mock_post.assert_called_once()

            # Verify URL construction
            called_url = mock_post.call_args[0][0]
            expected_url = "https://test-resource.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2025-01-01-preview"
            assert called_url == expected_url

            # Verify headers
            headers = mock_post.call_args[1]["headers"]
            assert headers["api-key"] == "test-key"
            assert headers["Content-Type"] == "application/json"

    def test_empty_content_handling(self):
        """Test that the provider raises an error for empty content."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_post.return_value = self._create_mock_response(self.empty_content_response)

            messages = [{"role": "user", "content": "Generate a commit message"}]

            with patch.dict(
                os.environ,
                {
                    "AZURE_OPENAI_API_KEY": "test-key",
                    "AZURE_OPENAI_ENDPOINT": "https://test-resource.openai.azure.com",
                    "AZURE_OPENAI_API_VERSION": "2025-01-01-preview",
                },
            ):
                with pytest.raises(Exception) as exc_info:
                    self.api_function(model=self.model_name, messages=messages, temperature=0.7, max_tokens=100)

                error_msg = str(exc_info.value).lower()
                assert "empty content" in error_msg or "missing" in error_msg

    def test_http_401_authentication_error(self):
        """Test that the provider handles HTTP 401 authentication errors."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"
            mock_post.side_effect = httpx.HTTPStatusError(
                "401 Unauthorized", request=MagicMock(), response=mock_response
            )

            messages = [{"role": "user", "content": "Generate a commit message"}]

            with patch.dict(
                os.environ,
                {
                    "AZURE_OPENAI_API_KEY": "test-key",
                    "AZURE_OPENAI_ENDPOINT": "https://test-resource.openai.azure.com",
                    "AZURE_OPENAI_API_VERSION": "2025-01-01-preview",
                },
            ):
                with pytest.raises(AIError):
                    self.api_function(model=self.model_name, messages=messages, temperature=0.7, max_tokens=100)

    def test_http_429_rate_limit_error(self):
        """Test that the provider handles HTTP 429 rate limit errors."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_response.text = "Rate limit exceeded"
            mock_post.side_effect = httpx.HTTPStatusError(
                "429 Too Many Requests", request=MagicMock(), response=mock_response
            )

            messages = [{"role": "user", "content": "Generate a commit message"}]

            with patch.dict(
                os.environ,
                {
                    "AZURE_OPENAI_API_KEY": "test-key",
                    "AZURE_OPENAI_ENDPOINT": "https://test-resource.openai.azure.com",
                    "AZURE_OPENAI_API_VERSION": "2025-01-01-preview",
                },
            ):
                with pytest.raises(AIError):
                    self.api_function(model=self.model_name, messages=messages, temperature=0.7, max_tokens=100)

    def test_http_500_server_error(self):
        """Test that the provider handles HTTP 500 server errors."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal server error"
            mock_post.side_effect = httpx.HTTPStatusError(
                "500 Internal server error", request=MagicMock(), response=mock_response
            )

            messages = [{"role": "user", "content": "Generate a commit message"}]

            with patch.dict(
                os.environ,
                {
                    "AZURE_OPENAI_API_KEY": "test-key",
                    "AZURE_OPENAI_ENDPOINT": "https://test-resource.openai.azure.com",
                    "AZURE_OPENAI_API_VERSION": "2025-01-01-preview",
                },
            ):
                with pytest.raises(AIError):
                    self.api_function(model=self.model_name, messages=messages, temperature=0.7, max_tokens=100)

    def test_http_503_service_unavailable(self):
        """Test that the provider handles HTTP 503 service unavailable errors."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 503
            mock_response.text = "Service unavailable"
            mock_post.side_effect = httpx.HTTPStatusError(
                "503 Service unavailable", request=MagicMock(), response=mock_response
            )

            messages = [{"role": "user", "content": "Generate a commit message"}]

            with patch.dict(
                os.environ,
                {
                    "AZURE_OPENAI_API_KEY": "test-key",
                    "AZURE_OPENAI_ENDPOINT": "https://test-resource.openai.azure.com",
                    "AZURE_OPENAI_API_VERSION": "2025-01-01-preview",
                },
            ):
                with pytest.raises(AIError):
                    self.api_function(model=self.model_name, messages=messages, temperature=0.7, max_tokens=100)

    def test_connection_error(self):
        """Test that the provider handles connection errors."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_post.side_effect = httpx.ConnectError("Connection failed")

            messages = [{"role": "user", "content": "Generate a commit message"}]

            with patch.dict(
                os.environ,
                {
                    "AZURE_OPENAI_API_KEY": "test-key",
                    "AZURE_OPENAI_ENDPOINT": "https://test-resource.openai.azure.com",
                    "AZURE_OPENAI_API_VERSION": "2025-01-01-preview",
                },
            ):
                with pytest.raises(AIError):
                    self.api_function(model=self.model_name, messages=messages, temperature=0.7, max_tokens=100)

    def test_timeout_error(self):
        """Test that the provider handles timeout errors."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_post.side_effect = httpx.TimeoutException("Request timed out")

            messages = [{"role": "user", "content": "Generate a commit message"}]

            with patch.dict(
                os.environ,
                {
                    "AZURE_OPENAI_API_KEY": "test-key",
                    "AZURE_OPENAI_ENDPOINT": "https://test-resource.openai.azure.com",
                    "AZURE_OPENAI_API_VERSION": "2025-01-01-preview",
                },
            ):
                with pytest.raises(AIError):
                    self.api_function(model=self.model_name, messages=messages, temperature=0.7, max_tokens=100)

    def test_malformed_json_response(self):
        """Test that the provider handles malformed JSON responses."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            messages = [{"role": "user", "content": "Generate a commit message"}]

            with patch.dict(
                os.environ,
                {
                    "AZURE_OPENAI_API_KEY": "test-key",
                    "AZURE_OPENAI_ENDPOINT": "https://test-resource.openai.azure.com",
                    "AZURE_OPENAI_API_VERSION": "2025-01-01-preview",
                },
            ):
                with pytest.raises((AIError, ValueError, KeyError, TypeError)):
                    self.api_function(model=self.model_name, messages=messages, temperature=0.7, max_tokens=100)


class TestAzureOpenAIURLConstruction:
    """Test Azure OpenAI specific URL construction and parameter handling."""

    def test_azure_url_construction_with_deployment(self):
        """Test that Azure OpenAI URL is constructed correctly with deployment name."""
        with patch.dict(
            "os.environ",
            {
                "AZURE_OPENAI_API_KEY": "test-key",
                "AZURE_OPENAI_ENDPOINT": "https://test-resource.openai.azure.com",
                "AZURE_OPENAI_API_VERSION": "2025-01-01-preview",
            },
        ):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"choices": [{"message": {"content": "test"}}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                call_azure_openai_api("gpt-35-turbo", [], 0.7, 1000)

                called_url = mock_post.call_args[0][0]
                expected_url = "https://test-resource.openai.azure.com/openai/deployments/gpt-35-turbo/chat/completions?api-version=2025-01-01-preview"
                assert called_url == expected_url

    def test_azure_get_api_url_without_model(self):
        """Test _get_api_url method with model=None (line 41)."""
        from gac.providers.azure_openai import AzureOpenAIProvider
        from gac.providers.base import ProviderConfig

        with patch.dict(
            "os.environ",
            {
                "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
                "AZURE_OPENAI_API_VERSION": "2025-01-01-preview",
            },
        ):
            config = ProviderConfig(
                name="Azure OpenAI",
                api_key_env="AZURE_OPENAI_API_KEY",
                base_url="https://test.openai.azure.com",
            )
            provider = AzureOpenAIProvider(config)

        # Test with model=None to hit the first branch
        url_without_model = provider._get_api_url(None)
        # Should call parent implementation
        assert url_without_model is not None
        assert isinstance(url_without_model, str)

    def test_azure_endpoint_trailing_slash_handling(self):
        """Test that trailing slashes in Azure endpoint are handled correctly."""
        with patch.dict(
            "os.environ",
            {
                "AZURE_OPENAI_API_KEY": "test-key",
                "AZURE_OPENAI_ENDPOINT": "https://test-resource.openai.azure.com/",
                "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
            },
        ):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"choices": [{"message": {"content": "test"}}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                call_azure_openai_api("my-gpt4-deployment", [], 0.7, 1000)

                called_url = mock_post.call_args[0][0]
                expected_url = "https://test-resource.openai.azure.com/openai/deployments/my-gpt4-deployment/chat/completions?api-version=2024-02-15-preview"
                assert called_url == expected_url


@pytest.mark.integration
class TestAzureOpenAIIntegration:
    """Integration tests for Azure OpenAI provider."""

    def test_real_api_call(self):
        """Test actual Azure OpenAI API call with valid credentials."""
        if not all(
            os.getenv(var) for var in ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_VERSION"]
        ):
            pytest.skip("Azure OpenAI environment variables not set")

        # Make real API call...
        pass  # Implementation would go here if needed
