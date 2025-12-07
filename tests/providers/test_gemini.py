"""Tests for Gemini provider."""

from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from gac.errors import AIError
from gac.providers import PROVIDER_REGISTRY
from tests.provider_test_utils import assert_missing_api_key_error, temporarily_remove_env_var
from tests.providers.conftest import BaseProviderTest


class TestGeminiImports:
    """Test that Gemini provider can be imported."""

    def test_import_provider(self):
        """Test that Gemini provider module can be imported."""
        from gac.providers import gemini  # noqa: F401

    def test_provider_in_registry(self):
        """Test that provider is registered."""
        from gac.providers import PROVIDER_REGISTRY

        assert "gemini" in PROVIDER_REGISTRY


class TestGeminiAPIKeyValidation:
    """Test Gemini API key validation."""

    def test_missing_api_key_error(self):
        """Test that Gemini raises error when API key is missing."""
        with temporarily_remove_env_var("GEMINI_API_KEY"):
            with pytest.raises(AIError) as exc_info:
                PROVIDER_REGISTRY["gemini"]("gemini-2.5-flash-lite", [], 0.7, 1000)

            assert_missing_api_key_error(exc_info, "gemini", "GEMINI_API_KEY")


class TestGeminiProviderMocked(BaseProviderTest):
    """Mocked tests for Gemini provider."""

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def provider_module(self) -> str:
        return "gac.providers.gemini"

    @property
    def api_function(self) -> Callable:
        return PROVIDER_REGISTRY["gemini"]

    @property
    def api_key_env_var(self) -> str | None:
        return "GEMINI_API_KEY"

    @property
    def model_name(self) -> str:
        return "gemini-2.5-flash-lite"

    @property
    def success_response(self) -> dict[str, Any]:
        return {"candidates": [{"content": {"parts": [{"text": "feat: Add new feature"}]}}]}

    @property
    def empty_content_response(self) -> dict[str, Any]:
        return {"candidates": [{"content": {"parts": [{"text": ""}]}}]}


class TestGeminiEdgeCases:
    """Test edge cases for Gemini provider."""

    def test_gemini_missing_candidates(self):
        """Test handling of response without candidates field."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"some_other_field": "value"}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    PROVIDER_REGISTRY["gemini"]("gemini-2.5-flash-lite", [], 0.7, 1000)

                assert "missing candidates" in str(exc_info.value).lower()

    def test_gemini_get_api_url(self):
        """Test _get_api_url method builds correct URLs (line 21)."""
        from gac.providers.gemini import GeminiProvider

        # Use the class-level config
        provider = GeminiProvider(GeminiProvider.config)

        # Test with model specified
        url_with_model = provider._get_api_url("gemini-2.5-flash-lite")
        expected_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent"
        assert url_with_model == expected_url

        # Test without model (calls parent)
        url_without_model = provider._get_api_url(None)
        # Should call parent implementation
        assert "generativelanguage.googleapis.com" in url_without_model

    def test_gemini_build_headers(self):
        """Test _build_headers method builds correct headers (line 29)."""
        from gac.providers.gemini import GeminiProvider

        # Mock the API key since we're testing headers, not authentication
        with patch.object(GeminiProvider, "api_key", new_callable=lambda: "test-key"):
            provider = GeminiProvider(GeminiProvider.config)
            headers = provider._build_headers()

            # Should have x-goog-api-key instead of Authorization
            assert "x-goog-api-key" in headers
            assert headers["x-goog-api-key"] == "test-key"
            # Should not have Authorization header
            assert "Authorization" not in headers
            # Should have other common headers from parent
            assert "Content-Type" in headers

    def test_gemini_empty_candidates(self):
        """Test handling of empty candidates array."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"candidates": []}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    PROVIDER_REGISTRY["gemini"]("gemini-2.5-flash-lite", [], 0.7, 1000)

                assert "missing candidates" in str(exc_info.value).lower()

    def test_gemini_missing_content(self):
        """Test handling of candidate without content field."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"candidates": [{"no_content": "here"}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    PROVIDER_REGISTRY["gemini"]("gemini-2.5-flash-lite", [], 0.7, 1000)

                assert "invalid content structure" in str(exc_info.value).lower()

    def test_gemini_missing_parts(self):
        """Test handling of content without parts field."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"candidates": [{"content": {"no_parts": []}}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    PROVIDER_REGISTRY["gemini"]("gemini-2.5-flash-lite", [], 0.7, 1000)

                assert "invalid content structure" in str(exc_info.value).lower()

    def test_gemini_empty_parts(self):
        """Test handling of empty parts array."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"candidates": [{"content": {"parts": []}}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    PROVIDER_REGISTRY["gemini"]("gemini-2.5-flash-lite", [], 0.7, 1000)

                assert "invalid content structure" in str(exc_info.value).lower()

    def test_gemini_null_text_content(self):
        """Test handling of null text in parts."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"candidates": [{"content": {"parts": [{"text": None}]}}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    PROVIDER_REGISTRY["gemini"]("gemini-2.5-flash-lite", [], 0.7, 1000)

                assert "missing text content" in str(exc_info.value).lower()

    def test_gemini_system_message_handling(self):
        """Test system message conversion to Gemini format."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"candidates": [{"content": {"parts": [{"text": "test response"}]}}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                messages = [
                    {"role": "system", "content": "System instruction"},
                    {"role": "user", "content": "User message"},
                ]

                result = PROVIDER_REGISTRY["gemini"]("gemini-2.5-flash-lite", messages, 0.7, 1000)

                # Verify the payload structure
                call_args = mock_post.call_args
                payload = call_args.kwargs["json"]
                assert len(payload["contents"]) == 1
                assert payload["contents"][0]["role"] == "user"
                assert payload["systemInstruction"]["role"] == "system"
                assert payload["systemInstruction"]["parts"][0]["text"] == "System instruction"
                assert result == "test response"

    def test_gemini_blank_system_message_ignored(self):
        """Ensure blank system instructions are omitted from payload."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                messages = [
                    {"role": "system", "content": "   "},
                    {"role": "user", "content": "User message"},
                ]

                PROVIDER_REGISTRY["gemini"]("gemini-2.5-flash-lite", messages, 0.7, 1000)

                payload = mock_post.call_args.kwargs["json"]
                assert "systemInstruction" not in payload
                assert len(payload["contents"]) == 1
                assert payload["contents"][0]["role"] == "user"

    def test_gemini_unsupported_role(self):
        """Ensure unsupported roles raise a model error."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with pytest.raises(AIError) as exc_info:
                PROVIDER_REGISTRY["gemini"](
                    "gemini-2.5-flash-lite",
                    [
                        {"role": "tool", "content": "Tool output"},
                        {"role": "user", "content": "User message"},
                    ],
                    temperature=0.7,
                    max_tokens=1000,
                )

            assert "unsupported message role" in str(exc_info.value).lower()

    def test_gemini_assistant_message_conversion(self):
        """Test assistant message converted to model role."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"candidates": [{"content": {"parts": [{"text": "test response"}]}}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                messages = [
                    {"role": "user", "content": "First message"},
                    {"role": "assistant", "content": "Assistant reply"},
                    {"role": "user", "content": "Second message"},
                ]

                result = PROVIDER_REGISTRY["gemini"]("gemini-2.5-flash-lite", messages, 0.7, 1000)

                # Verify the payload structure
                call_args = mock_post.call_args
                payload = call_args.kwargs["json"]
                assert len(payload["contents"]) == 3
                assert payload["contents"][0]["role"] == "user"
                assert payload["contents"][1]["role"] == "model"  # assistant -> model
                assert payload["contents"][2]["role"] == "user"
                assert result == "test response"

    def test_gemini_ignores_empty_text_parts(self):
        """Ensure empty parts are skipped when extracting model text."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "candidates": [
                        {
                            "content": {
                                "parts": [
                                    {"text": ""},
                                    {"text": "final answer"},
                                ]
                            }
                        }
                    ]
                }
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                result = PROVIDER_REGISTRY["gemini"](
                    "gemini-2.5-flash-lite",
                    [{"role": "user", "content": "hi"}],
                    temperature=0.7,
                    max_tokens=1000,
                )

                assert result == "final answer"

    def test_gemini_non_dict_parts_are_skipped(self):
        """Ensure non-dict parts are ignored while still returning valid text."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "candidates": [
                        {
                            "content": {
                                "parts": [
                                    "not a dict",
                                    {"text": ""},
                                    {"text": "use this"},
                                ]
                            }
                        }
                    ]
                }
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                result = PROVIDER_REGISTRY["gemini"](
                    "gemini-2.5-flash-lite", [{"role": "user", "content": "hi"}], 0.7, 1000
                )

                assert result == "use this"

    def test_gemini_none_content_converted_to_empty_string(self):
        """Ensure None content values are converted to empty strings in payload."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"candidates": [{"content": {"parts": [{"text": "response"}]}}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                PROVIDER_REGISTRY["gemini"](
                    "gemini-2.5-flash-lite",
                    [
                        {"role": "user", "content": None},
                        {"role": "user", "content": "second message"},
                    ],
                    temperature=0.7,
                    max_tokens=1000,
                )

                payload = mock_post.call_args.kwargs["json"]
                assert payload["contents"][0]["parts"][0]["text"] == ""
                assert payload["contents"][1]["parts"][0]["text"] == "second message"


@pytest.mark.integration
class TestGeminiIntegration:
    """Integration tests for Gemini provider."""

    def test_real_api_call(self):
        """Test actual Gemini API call with valid credentials."""
        import os

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            pytest.skip("GEMINI_API_KEY not set - skipping real API test")

        messages = [{"role": "user", "content": "Say 'test success' and nothing else."}]
        response = PROVIDER_REGISTRY["gemini"](
            model="gemini-2.5-flash-lite",
            messages=messages,
            temperature=1.0,
            max_tokens=50,
        )

        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
