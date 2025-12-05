"""Tests for StreamLake provider."""

import os
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from gac.errors import AIError
from gac.providers.streamlake import call_streamlake_api
from tests.provider_test_utils import assert_missing_api_key_error, temporarily_remove_env_var
from tests.providers.conftest import BaseProviderTest


class TestStreamLakeImports:
    """Test that StreamLake provider can be imported."""

    def test_import_provider(self):
        """Test that StreamLake provider module can be imported."""
        from gac.providers import streamlake  # noqa: F401

    def test_import_api_function(self):
        """Test that StreamLake API function can be imported."""
        from gac.providers.streamlake import call_streamlake_api  # noqa: F401


class TestStreamLakeAPIKeyValidation:
    """Test StreamLake API key validation."""

    def test_missing_api_key_error(self):
        """Test that StreamLake raises error when API key is missing."""
        with temporarily_remove_env_var("STREAMLAKE_API_KEY"):
            with temporarily_remove_env_var("VC_API_KEY"):
                with pytest.raises(AIError) as exc_info:
                    call_streamlake_api("ep-gmlysa-1760118602179985967", [], 0.7, 1000)

                assert_missing_api_key_error(exc_info, "streamlake", "STREAMLAKE_API_KEY")


class TestStreamLakeProviderMocked(BaseProviderTest):
    """Mocked tests for StreamLake provider."""

    @property
    def provider_name(self) -> str:
        return "streamlake"

    @property
    def provider_module(self) -> str:
        return "gac.providers.streamlake"

    @property
    def api_function(self) -> Callable:
        return call_streamlake_api

    @property
    def api_key_env_var(self) -> str | None:
        return "STREAMLAKE_API_KEY"

    @property
    def model_name(self) -> str:
        return "streamlake-test-model"

    @property
    def success_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": "feat: Add new feature"}}]}

    @property
    def empty_content_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": ""}}]}

    def test_supports_streamlake_api_key_alias(self):
        """Ensure VC_API_KEY alias works when STREAMLAKE_API_KEY is absent."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_post.return_value = self._create_mock_response(self.success_response)
            messages = [{"role": "user", "content": "Generate a commit message"}]
            with patch.dict(os.environ, {"VC_API_KEY": "alias-key"}, clear=True):
                result = self.api_function(model=self.model_name, messages=messages, temperature=0.7, max_tokens=100)
        assert result == "feat: Add new feature"
        headers = mock_post.call_args.kwargs.get("headers", {})
        assert headers.get("Authorization") == "Bearer alias-key"


class TestStreamLakeEdgeCases:
    """Test edge cases for StreamLake provider."""

    def test_streamlake_missing_choices(self):
        """Test handling of response without choices field."""
        with patch.dict("os.environ", {"STREAMLAKE_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"some_other_field": "value"}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    call_streamlake_api("test-model", [], 0.7, 1000)

                assert "invalid response" in str(exc_info.value).lower() or "missing" in str(exc_info.value).lower()

    def test_streamlake_empty_choices(self):
        """Test handling of empty choices array."""
        with patch.dict("os.environ", {"STREAMLAKE_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"choices": []}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    call_streamlake_api("test-model", [], 0.7, 1000)

                assert "invalid response" in str(exc_info.value).lower() or "missing" in str(exc_info.value).lower()

    def test_streamlake_missing_message(self):
        """Test handling of choice without message field."""
        with patch.dict("os.environ", {"STREAMLAKE_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"choices": [{"no_message": "here"}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    call_streamlake_api("test-model", [], 0.7, 1000)

                assert "null content" in str(exc_info.value).lower()

    def test_streamlake_null_content(self):
        """Test handling of null content."""
        with patch.dict("os.environ", {"STREAMLAKE_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"choices": [{"message": {"content": None}}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    call_streamlake_api("test-model", [], 0.7, 1000)

                assert "null content" in str(exc_info.value).lower()

    def test_streamlake_vc_api_key_alias(self):
        """Test VC_API_KEY alias when STREAMLAKE_API_KEY not set."""
        with patch("httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"choices": [{"message": {"content": "test response"}}]}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            # Remove STREAMLAKE_API_KEY if it exists
            env_vars = {}
            if "STREAMLAKE_API_KEY" in os.environ:
                env_vars = dict(os.environ)
                del env_vars["STREAMLAKE_API_KEY"]
            env_vars["VC_API_KEY"] = "vc-test-key"

            with patch.dict(os.environ, env_vars, clear=True):
                result = call_streamlake_api("test-model", [], 0.7, 1000)

            # Verify VC_API_KEY was used
            call_args = mock_post.call_args
            headers = call_args.kwargs["headers"]
            assert headers["Authorization"] == "Bearer vc-test-key"
            assert result == "test response"


@pytest.mark.integration
class TestStreamLakeIntegration:
    """Integration tests for StreamLake provider."""

    def test_real_api_call(self):
        """Test actual StreamLake API call with valid credentials."""
        api_key = os.getenv("STREAMLAKE_API_KEY") or os.getenv("VC_API_KEY")
        if not api_key:
            pytest.skip("STREAMLAKE_API_KEY not set - skipping real API test (VC_API_KEY alias also missing)")

        messages = [{"role": "user", "content": "Say 'test success' and nothing else."}]
        try:
            response = call_streamlake_api(
                model="ep-gmlysa-1760118602179985967",
                messages=messages,
                temperature=1.0,
                max_tokens=50,
            )

            assert response is not None
            assert isinstance(response, str)
            assert len(response) > 0
        except AIError as e:
            error_str = str(e).lower()
            if "429" in error_str or "rate limit" in error_str or "quota" in error_str:
                pytest.skip(f"StreamLake API rate limit exceeded - skipping real API test: {e}")
            elif "401" in error_str or "unauthorized" in error_str or "auth" in error_str:
                pytest.skip(f"StreamLake API authentication failed - skipping real API test: {e}")
            raise
