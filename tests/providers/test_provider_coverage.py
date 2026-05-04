"""Additional provider tests for improved coverage (Qwen, Custom Anthropic, Ollama)."""

import os
from unittest.mock import MagicMock, patch

import pytest

from gac.errors import AIError


class TestQwenProviderDeprecated:
    """Test QwenProvider deprecation stub."""

    def test_qwen_oauth_init_raises(self):
        """QwenProvider.__init__ raises AIError."""
        from gac.providers.qwen import QwenProvider

        with pytest.raises(AIError, match="no longer available"):
            QwenProvider(QwenProvider.config)

    def test_qwen_oauth_build_request_body_raises(self):
        """QwenProvider._build_request_body raises AIError."""
        from gac.providers.qwen import QwenProvider

        provider = QwenProvider.__new__(QwenProvider)
        with pytest.raises(AIError, match="no longer available"):
            provider._build_request_body([], 0.7, 1000, "model")

    def test_qwen_oauth_parse_response_raises(self):
        """QwenProvider._parse_response raises AIError."""
        from gac.providers.qwen import QwenProvider

        provider = QwenProvider.__new__(QwenProvider)
        with pytest.raises(AIError, match="no longer available"):
            provider._parse_response({})

    def test_qwen_oauth_generate_raises(self):
        """QwenProvider.generate raises AIError."""
        from gac.providers.qwen import QwenProvider

        provider = QwenProvider.__new__(QwenProvider)
        with pytest.raises(AIError, match="no longer available"):
            provider.generate("model", [], 0.7, 1000)


class TestCustomAnthropicProviderEdgeCases:
    """Test CustomAnthropicProvider edge cases."""

    def test_no_base_url_raises(self):
        """Missing CUSTOM_ANTHROPIC_BASE_URL raises AIError."""
        with patch.dict("os.environ", {}, clear=False):
            # Ensure CUSTOM_ANTHROPIC_BASE_URL is not set
            env_copy = dict(os.environ)
            env_copy.pop("CUSTOM_ANTHROPIC_BASE_URL", None)
            with patch.dict("os.environ", env_copy, clear=True):
                from gac.providers.custom_anthropic import CustomAnthropicProvider

                with pytest.raises(AIError, match="CUSTOM_ANTHROPIC_BASE_URL"):
                    CustomAnthropicProvider(CustomAnthropicProvider.config)

    def test_base_url_with_messages_suffix(self):
        """Base URL ending with /messages is used as-is."""
        with patch.dict(
            "os.environ",
            {
                "CUSTOM_ANTHROPIC_BASE_URL": "https://custom.api.com/v1/messages",
                "CUSTOM_ANTHROPIC_API_KEY": "test-key",
            },
        ):
            from gac.providers.custom_anthropic import CustomAnthropicProvider

            provider = CustomAnthropicProvider(CustomAnthropicProvider.config)
            assert provider.config.base_url == "https://custom.api.com/v1/messages"

    def test_base_url_with_v1_suffix(self):
        """Base URL ending with /v1 gets /messages appended."""
        with patch.dict(
            "os.environ",
            {
                "CUSTOM_ANTHROPIC_BASE_URL": "https://custom.api.com/v1",
                "CUSTOM_ANTHROPIC_API_KEY": "test-key",
            },
        ):
            from gac.providers.custom_anthropic import CustomAnthropicProvider

            provider = CustomAnthropicProvider(CustomAnthropicProvider.config)
            assert provider.config.base_url == "https://custom.api.com/v1/messages"

    def test_base_url_generic_gets_v1_messages(self):
        """Generic base URL gets /v1/messages appended."""
        with patch.dict(
            "os.environ",
            {
                "CUSTOM_ANTHROPIC_BASE_URL": "https://custom.api.com",
                "CUSTOM_ANTHROPIC_API_KEY": "test-key",
            },
        ):
            from gac.providers.custom_anthropic import CustomAnthropicProvider

            provider = CustomAnthropicProvider(CustomAnthropicProvider.config)
            assert provider.config.base_url == "https://custom.api.com/v1/messages"

    def test_custom_version_header(self):
        """Custom version is included in headers."""
        with patch.dict(
            "os.environ",
            {
                "CUSTOM_ANTHROPIC_BASE_URL": "https://custom.api.com/v1/messages",
                "CUSTOM_ANTHROPIC_API_KEY": "test-key",
                "CUSTOM_ANTHROPIC_VERSION": "2024-01-01",
            },
        ):
            from gac.providers.custom_anthropic import CustomAnthropicProvider

            provider = CustomAnthropicProvider(CustomAnthropicProvider.config)
            headers = provider._build_headers()
            assert headers["anthropic-version"] == "2024-01-01"

    def test_default_version_header(self):
        """Default version is 2023-06-01 when not set."""
        with patch.dict(
            "os.environ",
            {
                "CUSTOM_ANTHROPIC_BASE_URL": "https://custom.api.com/v1/messages",
                "CUSTOM_ANTHROPIC_API_KEY": "test-key",
            },
        ):
            from gac.providers.custom_anthropic import CustomAnthropicProvider

            provider = CustomAnthropicProvider(CustomAnthropicProvider.config)
            assert provider.custom_version == "2023-06-01"


class TestOllamaProviderEdgeCases:
    """Test OllamaProvider edge cases."""

    def test_ollama_response_in_message_format(self):
        """Test parsing response in message format."""
        from gac.providers import PROVIDER_REGISTRY

        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "message": {"content": "test response"},
                "prompt_eval_count": 10,
                "eval_count": 20,
            }
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            result = PROVIDER_REGISTRY["ollama"]("llama3", [{"role": "user", "content": "hi"}], 0.7, 1000)
            assert result[0] == "test response"

    def test_ollama_response_in_response_format(self):
        """Test parsing response in 'response' format."""
        from gac.providers import PROVIDER_REGISTRY

        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "response": "test response",
            }
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            result = PROVIDER_REGISTRY["ollama"]("llama3", [{"role": "user", "content": "hi"}], 0.7, 1000)
            assert result[0] == "test response"

    def test_ollama_null_content(self):
        """Test Ollama returns null content."""
        from gac.providers import PROVIDER_REGISTRY

        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "message": {"content": None},
            }
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            with pytest.raises(AIError, match="null content"):
                PROVIDER_REGISTRY["ollama"]("llama3", [{"role": "user", "content": "hi"}], 0.7, 1000)

    def test_ollama_empty_content(self):
        """Test Ollama returns empty content."""
        from gac.providers import PROVIDER_REGISTRY

        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "message": {"content": ""},
            }
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            with pytest.raises(AIError, match="empty content"):
                PROVIDER_REGISTRY["ollama"]("llama3", [{"role": "user", "content": "hi"}], 0.7, 1000)

    def test_ollama_custom_api_url(self):
        """Test OLLAMA_API_URL environment variable override."""
        from gac.providers import PROVIDER_REGISTRY

        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "message": {"content": "ok"},
            }
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            with patch.dict(os.environ, {"OLLAMA_API_URL": "http://custom:11434"}):
                PROVIDER_REGISTRY["ollama"]("llama3", [{"role": "user", "content": "hi"}], 0.7, 1000)
                call_url = mock_post.call_args[0][0]
                assert "custom:11434/api/chat" in call_url

    def test_ollama_api_key_header(self):
        """Test that OLLAMA_API_KEY is included in headers when set."""
        from gac.providers import PROVIDER_REGISTRY

        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "message": {"content": "ok"},
            }
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            with patch.dict(os.environ, {"OLLAMA_API_KEY": "test-key"}):
                PROVIDER_REGISTRY["ollama"]("llama3", [{"role": "user", "content": "hi"}], 0.7, 1000)
                headers = mock_post.call_args.kwargs["headers"]
                assert "Authorization" in headers
                assert headers["Authorization"] == "Bearer test-key"

    def test_ollama_non_int_token_counts(self):
        """Test that non-integer token counts default to -1."""
        from gac.providers import PROVIDER_REGISTRY

        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "message": {"content": "ok"},
                "prompt_eval_count": "not-int",
                "eval_count": "not-int",
            }
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            result = PROVIDER_REGISTRY["ollama"]("llama3", [{"role": "user", "content": "hi"}], 0.7, 1000)
            assert result[0] == "ok"
            # Non-int token counts -> -1 from _parse_response, generate() uses fallback
            assert result[1] >= 0  # prompt_tokens (fallback)
            assert result[2] >= 0  # completion_tokens (fallback)
