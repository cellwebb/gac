"""Additional LM Studio provider tests for improved coverage."""

import os
from unittest.mock import MagicMock, patch

import pytest

from gac.errors import AIError
from gac.providers import PROVIDER_REGISTRY

call_lmstudio_api = PROVIDER_REGISTRY["lm-studio"]


class TestLMStudioParseResponse:
    """Test _parse_response edge cases for coverage."""

    def test_usage_with_reasoning_tokens(self):
        """Test response with usage including reasoning_tokens details."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "test response"}}],
                "usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 50,
                    "completion_tokens_details": {"reasoning_tokens": 20},
                },
            }
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            result = call_lmstudio_api("local-model", [], 0.7, 1000)
            assert result[0] == "test response"
            # completion_tokens should be normalized (50 - 20 = 30)
            assert result[2] == 30  # completion_tokens
            assert result[4] == 20  # reasoning_tokens

    def test_usage_non_int_prompt_tokens(self):
        """Test usage with non-integer prompt_tokens."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "test response"}}],
                "usage": {"prompt_tokens": "not-an-int", "completion_tokens": 50},
            }
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            result = call_lmstudio_api("local-model", [], 0.7, 1000)
            assert result[0] == "test response"
            # Non-int prompt_tokens results in -1 from _parse_response,
            # then generate() fallback counts tokens from messages
            assert result[1] >= 0  # prompt_tokens (fallback from count_tokens)

    def test_usage_non_int_completion_tokens(self):
        """Test usage with non-integer completion_tokens."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "test response"}}],
                "usage": {"prompt_tokens": 100, "completion_tokens": "not-an-int"},
            }
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            result = call_lmstudio_api("local-model", [], 0.7, 1000)
            assert result[0] == "test response"
            # Non-int results in -1 from _parse_response, then generate() fallback counts
            assert result[2] >= 0  # completion_tokens (fallback from count_tokens)

    def test_text_field_empty_content(self):
        """Test text field with empty content raises error."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"choices": [{"text": ""}]}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            with pytest.raises(AIError, match="empty content"):
                call_lmstudio_api("local-model", [], 0.7, 1000)

    def test_no_usage_at_all(self):
        """Test response without usage field at all."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "test response"}}],
            }
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            result = call_lmstudio_api("local-model", [], 0.7, 1000)
            assert result[0] == "test response"
            # No usage field -> -1 from _parse_response, then fallback token count
            assert result[1] >= 0  # prompt_tokens
            assert result[2] >= 0  # completion_tokens

    def test_reasoning_tokens_non_int(self):
        """Test reasoning_tokens with non-integer value."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "test response"}}],
                "usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 50,
                    "completion_tokens_details": {"reasoning_tokens": "not-int"},
                },
            }
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            result = call_lmstudio_api("local-model", [], 0.7, 1000)
            assert result[0] == "test response"
            assert result[4] == 0  # reasoning_tokens should default to 0

    def test_negative_completion_tokens(self):
        """Test normalization with negative completion_tokens."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "test response"}}],
                "usage": {"prompt_tokens": 100, "completion_tokens": -1},
            }
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            result = call_lmstudio_api("local-model", [], 0.7, 1000)
            assert result[0] == "test response"
            # -1 completion_tokens triggers fallback token counting
            assert result[2] >= 0  # Should use fallback

    def test_lmstudio_api_url_trailing_slash(self):
        """Test that LMSTUDIO_API_URL trailing slash is stripped."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"choices": [{"message": {"content": "ok"}}]}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            with patch.dict(os.environ, {"LMSTUDIO_API_URL": "http://custom:8080/"}):
                call_lmstudio_api("local-model", [], 0.7, 1000)
                call_url = mock_post.call_args[0][0]
                # Should not have double slashes
                assert "custom:8080/v1/chat/completions" in call_url
