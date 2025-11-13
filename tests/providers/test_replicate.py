"""Tests for Replicate provider."""

import os
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from gac.errors import AIError
from gac.providers.replicate import call_replicate_api
from tests.provider_test_utils import assert_missing_api_key_error, temporarily_remove_env_var
from tests.providers.conftest import BaseProviderTest


class TestReplicateImports:
    """Test that Replicate provider can be imported."""

    def test_import_provider(self):
        """Test that Replicate provider module can be imported."""
        from gac.providers import replicate  # noqa: F401

    def test_import_api_function(self):
        """Test that Replicate API function can be imported."""
        from gac.providers.replicate import call_replicate_api  # noqa: F401


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
        return call_replicate_api

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

                assert result == "feat: Add new feature"
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
        assert isinstance(response, str)
        assert len(response) > 0
