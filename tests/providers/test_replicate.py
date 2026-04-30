"""Tests for Replicate provider."""

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

call_replicate_api = PROVIDER_REGISTRY["replicate"]


class TestReplicateImports:
    """Test that Replicate provider can be imported."""

    def test_import_provider(self):
        """Test that Replicate provider module can be imported."""
        from gac.providers import replicate  # noqa: F401

    def test_provider_in_registry(self):
        """Test that Replicate provider is in the registry."""
        assert "replicate" in PROVIDER_REGISTRY


class TestReplicateAPIKeyValidation:
    """Test Replicate API key validation."""

    def test_missing_api_key_error(self):
        """Test that Replicate raises error when API key is missing."""
        with temporarily_remove_env_var("REPLICATE_API_TOKEN"):
            with pytest.raises(AIError) as exc_info:
                call_replicate_api("openai/gpt-oss-20b", [], 0.7, 1000)

            assert_missing_api_key_error(exc_info, "replicate", "REPLICATE_API_TOKEN")


class TestReplicateProviderMocked(BaseProviderTest):
    """Mocked tests for Replicate provider."""

    @property
    def provider_name(self) -> str:
        return "replicate"

    @property
    def provider_module(self) -> str:
        return "gac.providers.replicate"

    @property
    def api_function(self) -> Callable:
        return PROVIDER_REGISTRY["replicate"]

    @property
    def api_key_env_var(self) -> str | None:
        return "REPLICATE_API_TOKEN"

    @property
    def model_name(self) -> str:
        return "openai/gpt-oss-20b"

    @property
    def success_response(self) -> dict[str, Any]:
        return {"id": "test-prediction-id", "status": "starting", "output": "feat: Add new feature"}

    @property
    def empty_content_response(self) -> dict[str, Any]:
        return {"id": "test-prediction-id", "status": "succeeded", "output": ""}

    def test_successful_api_call(self):
        """Test successful Replicate API call with async polling."""
        with patch.dict("os.environ", {"REPLICATE_API_TOKEN": "test-token"}):
            mock_create_response = MagicMock()
            mock_create_response.json.return_value = {"id": "test-prediction-id"}
            mock_create_response.raise_for_status = MagicMock()

            mock_status_response = MagicMock()
            mock_status_response.json.return_value = {
                "id": "test-prediction-id",
                "status": "succeeded",
                "output": "feat: Add new feature",
            }
            mock_status_response.raise_for_status = MagicMock()

            with patch("httpx.post") as mock_post, patch("httpx.get") as mock_get, patch("time.sleep") as _mock_sleep:
                mock_post.return_value = mock_create_response
                mock_get.return_value = mock_status_response

                messages = [{"role": "user", "content": "Add user authentication"}]
                result = call_replicate_api(
                    model="openai/gpt-oss-20b", messages=messages, temperature=0.7, max_tokens=1000
                )

                assert isinstance(result, tuple)
                assert len(result) == 4
                content, prompt_tokens, completion_tokens, duration_ms = result
                assert content == "feat: Add new feature"
                assert isinstance(duration_ms, int) and duration_ms >= 0
                mock_post.assert_called_once()
                mock_get.assert_called_once()

    def test_replicate_prediction_failed(self):
        """Test handling of failed Replicate prediction."""
        with patch.dict("os.environ", {"REPLICATE_API_TOKEN": "test-token"}):
            mock_create_response = MagicMock()
            mock_create_response.json.return_value = {"id": "test-prediction-id"}
            mock_create_response.raise_for_status = MagicMock()

            mock_status_response = MagicMock()
            mock_status_response.json.return_value = {
                "id": "test-prediction-id",
                "status": "failed",
                "error": "Model execution failed",
            }
            mock_status_response.raise_for_status = MagicMock()

            with patch("httpx.post") as mock_post, patch("httpx.get") as mock_get, patch("time.sleep") as _mock_sleep:
                mock_post.return_value = mock_create_response
                mock_get.return_value = mock_status_response

                with pytest.raises(AIError) as exc_info:
                    call_replicate_api(
                        model="openai/gpt-oss-20b",
                        messages=[{"role": "user", "content": "test"}],
                        temperature=0.7,
                        max_tokens=1000,
                    )

                assert "prediction failed" in str(exc_info.value).lower()

    def test_replicate_empty_content(self):
        """Test handling of empty content from Replicate."""
        with patch.dict("os.environ", {"REPLICATE_API_TOKEN": "test-token"}):
            mock_create_response = MagicMock()
            mock_create_response.json.return_value = {"id": "test-prediction-id"}
            mock_create_response.raise_for_status = MagicMock()

            mock_status_response = MagicMock()
            mock_status_response.json.return_value = {"id": "test-prediction-id", "status": "succeeded", "output": ""}
            mock_status_response.raise_for_status = MagicMock()

            with patch("httpx.post") as mock_post, patch("httpx.get") as mock_get, patch("time.sleep") as _mock_sleep:
                mock_post.return_value = mock_create_response
                mock_get.return_value = mock_status_response

                with pytest.raises(AIError) as exc_info:
                    call_replicate_api(
                        model="openai/gpt-oss-20b",
                        messages=[{"role": "user", "content": "test"}],
                        temperature=0.7,
                        max_tokens=1000,
                    )

                assert "empty content" in str(exc_info.value).lower()

    def test_replicate_timeout(self):
        """Test handling of Replicate prediction timeout."""
        with patch.dict("os.environ", {"REPLICATE_API_TOKEN": "test-token"}):
            mock_create_response = MagicMock()
            mock_create_response.json.return_value = {"id": "test-prediction-id"}
            mock_create_response.raise_for_status = MagicMock()

            mock_status_response = MagicMock()
            mock_status_response.json.return_value = {"id": "test-prediction-id", "status": "processing"}
            mock_status_response.raise_for_status = MagicMock()

            with patch("httpx.post") as mock_post, patch("httpx.get") as mock_get, patch("time.sleep") as _mock_sleep:
                mock_post.return_value = mock_create_response
                mock_get.return_value = mock_status_response

                with pytest.raises(AIError) as exc_info:
                    call_replicate_api(
                        model="openai/gpt-oss-20b",
                        messages=[{"role": "user", "content": "test"}],
                        temperature=0.7,
                        max_tokens=1000,
                    )

                assert "timed out" in str(exc_info.value).lower()

    def test_empty_content_handling(self):
        """Test that the provider raises an error for empty content."""
        with patch.dict("os.environ", {"REPLICATE_API_TOKEN": "test-token"}):
            mock_create_response = MagicMock()
            mock_create_response.json.return_value = {"id": "test-prediction-id"}
            mock_create_response.raise_for_status = MagicMock()

            mock_status_response = MagicMock()
            mock_status_response.json.return_value = {"id": "test-prediction-id", "status": "succeeded", "output": ""}
            mock_status_response.raise_for_status = MagicMock()

            with patch("httpx.post") as mock_post, patch("httpx.get") as mock_get, patch("time.sleep") as _mock_sleep:
                mock_post.return_value = mock_create_response
                mock_get.return_value = mock_status_response

                with pytest.raises(AIError) as exc_info:
                    call_replicate_api(
                        model="openai/gpt-oss-20b",
                        messages=[{"role": "user", "content": "Generate a commit message"}],
                        temperature=0.7,
                        max_tokens=100,
                    )

                error_msg = str(exc_info.value).lower()
                assert "empty content" in error_msg or "missing" in error_msg


class TestReplicateErrorHandling:
    """Test Replicate provider error handling edge cases."""

    def test_build_headers_token_format(self):
        """Test that _build_headers uses Token format instead of Bearer."""
        with patch.dict("os.environ", {"REPLICATE_API_TOKEN": "test-token"}):
            from gac.providers.replicate import ReplicateProvider

            provider = ReplicateProvider(ReplicateProvider.config)
            headers = provider._build_headers()
            assert headers["Authorization"] == "Token test-token"

    def test_unknown_prediction_status(self):
        """Test handling of unknown prediction status."""
        with patch.dict("os.environ", {"REPLICATE_API_TOKEN": "test-token"}):
            mock_create_response = MagicMock()
            mock_create_response.json.return_value = {"id": "test-prediction-id"}
            mock_create_response.raise_for_status = MagicMock()

            mock_status_response = MagicMock()
            mock_status_response.json.return_value = {
                "id": "test-prediction-id",
                "status": "cancelled",
            }
            mock_status_response.raise_for_status = MagicMock()

            with patch("httpx.post") as mock_post, patch("httpx.get") as mock_get:
                mock_post.return_value = mock_create_response
                mock_get.return_value = mock_status_response

                with pytest.raises(AIError) as exc_info:
                    call_replicate_api(
                        model="openai/gpt-oss-20b",
                        messages=[{"role": "user", "content": "test"}],
                        temperature=0.7,
                        max_tokens=1000,
                    )

                assert "unknown status" in str(exc_info.value).lower()

    def test_polling_http_429_rate_limit(self):
        """Test rate limit error during polling."""
        with patch.dict("os.environ", {"REPLICATE_API_TOKEN": "test-token"}):
            mock_create_response = MagicMock()
            mock_create_response.json.return_value = {"id": "test-prediction-id"}
            mock_create_response.raise_for_status = MagicMock()

            mock_get_response = MagicMock()
            mock_get_response.status_code = 429
            mock_get_response.text = "Rate limit exceeded"

            with patch("httpx.post") as mock_post, patch("httpx.get") as mock_get:
                mock_post.return_value = mock_create_response
                mock_get.side_effect = httpx.HTTPStatusError(
                    "429 Rate limit exceeded", request=MagicMock(), response=mock_get_response
                )

                with pytest.raises(AIError) as exc_info:
                    call_replicate_api(
                        model="openai/gpt-oss-20b",
                        messages=[{"role": "user", "content": "test"}],
                        temperature=0.7,
                        max_tokens=1000,
                    )

                assert "rate limit" in str(exc_info.value).lower()

    def test_polling_http_500_error(self):
        """Test HTTP 500 error during polling."""
        with patch.dict("os.environ", {"REPLICATE_API_TOKEN": "test-token"}):
            mock_create_response = MagicMock()
            mock_create_response.json.return_value = {"id": "test-prediction-id"}
            mock_create_response.raise_for_status = MagicMock()

            mock_get_response = MagicMock()
            mock_get_response.status_code = 500
            mock_get_response.text = "Internal server error"

            with patch("httpx.post") as mock_post, patch("httpx.get") as mock_get:
                mock_post.return_value = mock_create_response
                mock_get.side_effect = httpx.HTTPStatusError(
                    "500 error", request=MagicMock(), response=mock_get_response
                )

                with pytest.raises(AIError) as exc_info:
                    call_replicate_api(
                        model="openai/gpt-oss-20b",
                        messages=[{"role": "user", "content": "test"}],
                        temperature=0.7,
                        max_tokens=1000,
                    )

                assert "500" in str(exc_info.value)

    def test_polling_timeout_error(self):
        """Test timeout error during polling."""
        with patch.dict("os.environ", {"REPLICATE_API_TOKEN": "test-token"}):
            mock_create_response = MagicMock()
            mock_create_response.json.return_value = {"id": "test-prediction-id"}
            mock_create_response.raise_for_status = MagicMock()

            with patch("httpx.post") as mock_post, patch("httpx.get") as mock_get:
                mock_post.return_value = mock_create_response
                mock_get.side_effect = httpx.TimeoutException("Request timed out")

                with pytest.raises(AIError) as exc_info:
                    call_replicate_api(
                        model="openai/gpt-oss-20b",
                        messages=[{"role": "user", "content": "test"}],
                        temperature=0.7,
                        max_tokens=1000,
                    )

                assert "timed out" in str(exc_info.value).lower()

    def test_polling_generic_exception(self):
        """Test generic exception during polling."""
        with patch.dict("os.environ", {"REPLICATE_API_TOKEN": "test-token"}):
            mock_create_response = MagicMock()
            mock_create_response.json.return_value = {"id": "test-prediction-id"}
            mock_create_response.raise_for_status = MagicMock()

            with patch("httpx.post") as mock_post, patch("httpx.get") as mock_get:
                mock_post.return_value = mock_create_response
                mock_get.side_effect = RuntimeError("Unexpected error")

                with pytest.raises(AIError) as exc_info:
                    call_replicate_api(
                        model="openai/gpt-oss-20b",
                        messages=[{"role": "user", "content": "test"}],
                        temperature=0.7,
                        max_tokens=1000,
                    )

                assert "polling" in str(exc_info.value).lower() or "Unexpected" in str(exc_info.value)

    def test_get_api_url_exception_wrapping(self):
        """Test exception wrapping in _get_api_url."""
        with patch.dict("os.environ", {"REPLICATE_API_TOKEN": "test-token"}):
            from gac.providers.replicate import ReplicateProvider

            provider = ReplicateProvider(ReplicateProvider.config)

            with patch.object(provider, "_get_api_url", side_effect=RuntimeError("url error")):
                with pytest.raises(AIError) as exc_info:
                    provider.generate(
                        model="test-model",
                        messages=[{"role": "user", "content": "test"}],
                    )

                assert "url error" in str(exc_info.value)

    def test_build_headers_exception_wrapping(self):
        """Test exception wrapping in _build_headers."""
        with patch.dict("os.environ", {"REPLICATE_API_TOKEN": "test-token"}):
            from gac.providers.replicate import ReplicateProvider

            provider = ReplicateProvider(ReplicateProvider.config)

            with patch.object(provider, "_build_headers", side_effect=RuntimeError("header error")):
                with pytest.raises(AIError) as exc_info:
                    provider.generate(
                        model="test-model",
                        messages=[{"role": "user", "content": "test"}],
                    )

                assert "header error" in str(exc_info.value)

    def test_build_request_body_exception_wrapping(self):
        """Test exception wrapping in _build_request_body."""
        with patch.dict("os.environ", {"REPLICATE_API_TOKEN": "test-token"}):
            from gac.providers.replicate import ReplicateProvider

            provider = ReplicateProvider(ReplicateProvider.config)

            with patch.object(provider, "_build_request_body", side_effect=RuntimeError("body error")):
                with pytest.raises(AIError) as exc_info:
                    provider.generate(
                        model="test-model",
                        messages=[{"role": "user", "content": "test"}],
                    )

                assert "body error" in str(exc_info.value)

    def test_create_prediction_http_401(self):
        """Test HTTP 401 during prediction creation."""
        with patch.dict("os.environ", {"REPLICATE_API_TOKEN": "test-token"}):
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"

            with patch("httpx.post") as mock_post:
                mock_post.side_effect = httpx.HTTPStatusError(
                    "401 Unauthorized", request=MagicMock(), response=mock_response
                )

                with pytest.raises(AIError) as exc_info:
                    call_replicate_api(
                        model="openai/gpt-oss-20b",
                        messages=[{"role": "user", "content": "test"}],
                        temperature=0.7,
                        max_tokens=1000,
                    )

                assert exc_info.value.error_type == "authentication"

    def test_create_prediction_http_429(self):
        """Test HTTP 429 during prediction creation."""
        with patch.dict("os.environ", {"REPLICATE_API_TOKEN": "test-token"}):
            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_response.text = "Rate limit"

            with patch("httpx.post") as mock_post:
                mock_post.side_effect = httpx.HTTPStatusError(
                    "429 Rate limit", request=MagicMock(), response=mock_response
                )

                with pytest.raises(AIError) as exc_info:
                    call_replicate_api(
                        model="openai/gpt-oss-20b",
                        messages=[{"role": "user", "content": "test"}],
                        temperature=0.7,
                        max_tokens=1000,
                    )

                assert "rate limit" in str(exc_info.value).lower()

    def test_create_prediction_timeout(self):
        """Test timeout during prediction creation."""
        with patch.dict("os.environ", {"REPLICATE_API_TOKEN": "test-token"}):
            with patch("httpx.post") as mock_post:
                mock_post.side_effect = httpx.TimeoutException("Timed out")

                with pytest.raises(AIError) as exc_info:
                    call_replicate_api(
                        model="openai/gpt-oss-20b",
                        messages=[{"role": "user", "content": "test"}],
                        temperature=0.7,
                        max_tokens=1000,
                    )

                assert "timed out" in str(exc_info.value).lower()

    def test_create_prediction_generic_exception(self):
        """Test generic exception during prediction creation."""
        with patch.dict("os.environ", {"REPLICATE_API_TOKEN": "test-token"}):
            with patch("httpx.post") as mock_post:
                mock_post.side_effect = RuntimeError("Network failure")

                with pytest.raises(AIError) as exc_info:
                    call_replicate_api(
                        model="openai/gpt-oss-20b",
                        messages=[{"role": "user", "content": "test"}],
                        temperature=0.7,
                        max_tokens=1000,
                    )

                assert "Network failure" in str(exc_info.value)


class TestReplicateMessageFormatting:
    """Test Replicate-specific message formatting."""

    def test_system_message_handling(self):
        """Test that system messages are properly formatted."""
        with patch.dict("os.environ", {"REPLICATE_API_TOKEN": "test-token"}):
            mock_create_response = MagicMock()
            mock_create_response.json.return_value = {"id": "test-prediction-id"}
            mock_create_response.raise_for_status = MagicMock()

            mock_status_response = MagicMock()
            mock_status_response.json.return_value = {
                "id": "test-prediction-id",
                "status": "succeeded",
                "output": "test response",
            }
            mock_status_response.raise_for_status = MagicMock()

            with patch("httpx.post") as mock_post, patch("httpx.get") as mock_get, patch("time.sleep") as _mock_sleep:
                mock_post.return_value = mock_create_response
                mock_get.return_value = mock_status_response

                messages = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi there!"},
                    {"role": "user", "content": "How are you?"},
                ]

                call_replicate_api(model="openai/gpt-oss-20b", messages=messages, temperature=0.7, max_tokens=1000)

                call_args = mock_post.call_args
                prompt = call_args[1]["json"]["input"]["prompt"]

                assert "System: You are a helpful assistant." in prompt
                assert "Human: Hello" in prompt
                assert "Assistant: Hi there!" in prompt
                assert "Human: How are you?" in prompt
                assert prompt.endswith("\n\nAssistant:")


@pytest.mark.integration
class TestReplicateIntegration:
    """Integration tests for Replicate provider."""

    def test_real_api_call(self):
        """Test actual Replicate API call with valid credentials."""
        api_token = os.getenv("REPLICATE_API_TOKEN")
        if not api_token:
            pytest.skip("REPLICATE_API_TOKEN not set - skipping real API test")

        messages = [{"role": "user", "content": "Say 'test success' and nothing else."}]
        model = "openai/gpt-oss-20b"

        response = call_replicate_api(model=model, messages=messages, temperature=1.0, max_tokens=50)

        assert response is not None
        assert isinstance(response, tuple)
        assert len(response[0]) > 0
