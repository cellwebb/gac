"""Additional Gemini provider tests for improved coverage."""

from unittest.mock import MagicMock, patch

from gac.providers import PROVIDER_REGISTRY
from gac.providers.gemini import GeminiProvider

call_gemini_api = PROVIDER_REGISTRY["gemini"]


class TestGeminiParseResponseCoverage:
    """Test _parse_response edge cases for coverage."""

    def test_usage_metadata_with_thoughts(self):
        """Test response with usageMetadata including thoughtsTokenCount."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "candidates": [{"content": {"parts": [{"text": "response"}]}}],
                    "usageMetadata": {
                        "promptTokenCount": 100,
                        "candidatesTokenCount": 50,
                        "thoughtsTokenCount": 20,
                    },
                }
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                result = call_gemini_api("gemini-2.5-flash-lite", [{"role": "user", "content": "hi"}], 0.7, 1000)
                assert result[0] == "response"
                assert result[2] == 30  # 50 - 20 = 30 (normalized)
                assert result[4] == 20  # reasoning_tokens

    def test_usage_metadata_non_int_tokens(self):
        """Test usageMetadata with non-integer token counts."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "candidates": [{"content": {"parts": [{"text": "response"}]}}],
                    "usageMetadata": {
                        "promptTokenCount": "not-int",
                        "candidatesTokenCount": "not-int",
                        "thoughtsTokenCount": "not-int",
                    },
                }
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                result = call_gemini_api("gemini-2.5-flash-lite", [{"role": "user", "content": "hi"}], 0.7, 1000)
                assert result[0] == "response"
                # Non-int -> -1 from _parse_response, generate() fallback counts tokens
                assert result[1] >= 0  # prompt_tokens (fallback)
                assert result[4] == 0  # reasoning_tokens

    def test_no_usage_metadata(self):
        """Test response without usageMetadata."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "candidates": [{"content": {"parts": [{"text": "response"}]}}],
                }
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                result = call_gemini_api("gemini-2.5-flash-lite", [{"role": "user", "content": "hi"}], 0.7, 1000)
                assert result[0] == "response"
                assert result[1] >= 0  # prompt_tokens (fallback from count_tokens)
                assert result[2] >= 0  # completion_tokens (fallback from count_tokens)

    def test_usage_metadata_negative_candidates_tokens(self):
        """Test normalization with negative candidatesTokenCount."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "candidates": [{"content": {"parts": [{"text": "response"}]}}],
                    "usageMetadata": {
                        "promptTokenCount": 100,
                        "candidatesTokenCount": -1,
                    },
                }
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                result = call_gemini_api("gemini-2.5-flash-lite", [{"role": "user", "content": "hi"}], 0.7, 1000)
                assert result[0] == "response"
                assert result[2] >= 0  # Should use fallback

    def test_gemini_build_headers_removes_authorization(self):
        """Test that _build_headers removes Authorization header."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            provider = GeminiProvider(GeminiProvider.config)
            headers = provider._build_headers()
            assert "x-goog-api-key" in headers
            assert "Authorization" not in headers
