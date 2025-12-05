"""Tests for Synthetic.new provider."""

import os
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from gac.errors import AIError
from gac.providers.synthetic import call_synthetic_api
from tests.provider_test_utils import assert_missing_api_key_error, temporarily_remove_env_var
from tests.providers.conftest import BaseProviderTest


class TestSyntheticImports:
    """Test that Synthetic provider can be imported."""

    def test_import_provider(self):
        """Test that Synthetic provider module can be imported."""
        from gac.providers import synthetic  # noqa: F401

    def test_import_api_function(self):
        """Test that Synthetic API function can be imported."""
        from gac.providers.synthetic import call_synthetic_api  # noqa: F401


class TestSyntheticAPIKeyValidation:
    """Test Synthetic API key validation."""

    def test_missing_api_key_error(self):
        """Test that Synthetic raises error when API key is missing."""
        with temporarily_remove_env_var("SYNTHETIC_API_KEY"):
            with temporarily_remove_env_var("SYN_API_KEY"):
                with pytest.raises(AIError) as exc_info:
                    call_synthetic_api("hf:meta-llama/Meta-Llama-3-8B-Instruct", [], 0.7, 1000)

                assert_missing_api_key_error(exc_info, "synthetic", "SYNTHETIC_API_KEY")


class TestSyntheticProviderMocked(BaseProviderTest):
    """Mocked tests for Synthetic provider."""

    @property
    def provider_name(self) -> str:
        return "synthetic"

    @property
    def provider_module(self) -> str:
        return "gac.providers.synthetic"

    @property
    def api_function(self) -> Callable:
        return call_synthetic_api

    @property
    def api_key_env_var(self) -> str | None:
        return "SYNTHETIC_API_KEY"

    @property
    def model_name(self) -> str:
        return "hf:zai-org/GLM-4.6"

    @property
    def success_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": "feat: Add new feature"}}]}

    @property
    def empty_content_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": ""}}]}

    def test_supports_syn_api_key_alias(self):
        """Ensure SYN_API_KEY alias works when SYNTHETIC_API_KEY is absent."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_post.return_value = self._create_mock_response(self.success_response)
            messages = [{"role": "user", "content": "Generate a commit message"}]
            with patch.dict(os.environ, {"SYN_API_KEY": "alias-key"}, clear=True):
                result = self.api_function(model="hf:model", messages=messages, temperature=0.7, max_tokens=100)

        assert result == "feat: Add new feature"
        headers = mock_post.call_args.kwargs.get("headers", {})
        assert headers.get("Authorization") == "Bearer alias-key"

    def test_adds_hf_prefix_for_models(self):
        """Verify models without the hf: prefix are automatically corrected."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_post.return_value = self._create_mock_response(self.success_response)
            messages = [{"role": "user", "content": "Generate a commit message"}]
            with patch.dict(os.environ, {"SYNTHETIC_API_KEY": "test-key"}, clear=True):
                result = self.api_function(
                    model="zai-org/GLM-4.6",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=256,
                )

        assert result == "feat: Add new feature"
        payload = mock_post.call_args.kwargs.get("json", {})
        assert payload.get("model") == "hf:zai-org/GLM-4.6"
        assert payload.get("max_completion_tokens") == 256


class TestSyntheticEdgeCases:
    """Test edge cases for Synthetic provider."""

    def test_synthetic_null_content(self):
        """Test handling of null content."""
        with patch.dict("os.environ", {"SYNTHETIC_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"choices": [{"message": {"content": None}}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    call_synthetic_api("hf:zai-org/GLM-4.6", [], 0.7, 1000)

                assert "null content" in str(exc_info.value).lower()


@pytest.mark.integration
class TestSyntheticIntegration:
    """Integration tests for Synthetic provider."""

    def test_real_api_call(self):
        """Test actual Synthetic API call with valid credentials."""
        api_key = os.getenv("SYNTHETIC_API_KEY") or os.getenv("SYN_API_KEY")
        if not api_key:
            pytest.skip("SYNTHETIC_API_KEY not set - skipping real API test (SYN_API_KEY alias also missing)")

        messages = [{"role": "user", "content": "Say 'test success' and nothing else."}]
        try:
            response = call_synthetic_api(
                model="hf:zai-org/GLM-4.6",
                messages=messages,
                temperature=1.0,
                max_tokens=1024,  # glm-4.6 needs extra tokens for reasoning
            )

            assert response is not None
            assert isinstance(response, str)
            assert len(response) > 0
        except AIError as e:
            error_str = str(e).lower()
            if "429" in error_str or "rate limit" in error_str or "quota" in error_str:
                pytest.skip(f"Synthetic API rate limit exceeded - skipping real API test: {e}")
            elif "401" in error_str or "unauthorized" in error_str or "auth" in error_str:
                pytest.skip(f"Synthetic API authentication failed - skipping real API test: {e}")
            raise
