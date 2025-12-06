"""Unit tests for AI utility functions.

These tests run without any external dependencies and test core logic.
"""

import os
import sys
from unittest.mock import MagicMock, patch

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

import gac.ai_utils as ai_utils  # noqa: E402
from gac.errors import AIError  # noqa: E402


class TestClassifyError:
    """Test _classify_error function."""

    def test_classify_error_authentication(self):
        """Test _classify_error for authentication errors."""
        assert ai_utils._classify_error("Invalid API key") == "authentication"
        assert ai_utils._classify_error("Unauthorized access") == "authentication"
        assert ai_utils._classify_error("Authentication failed") == "authentication"
        assert ai_utils._classify_error("API key is invalid") == "authentication"

    def test_classify_error_rate_limit(self):
        """Test _classify_error for rate limit errors."""
        assert ai_utils._classify_error("Rate limit exceeded") == "rate_limit"
        assert ai_utils._classify_error("Too many requests") == "rate_limit"

    def test_classify_error_timeout(self):
        """Test _classify_error for timeout errors."""
        assert ai_utils._classify_error("Request timed out") == "timeout"
        assert ai_utils._classify_error("Request timeout") == "timeout"
        assert ai_utils._classify_error("Connection timed out") == "timeout"

    def test_classify_error_connection(self):
        """Test _classify_error for connection errors."""
        assert ai_utils._classify_error("Connection failed") == "connection"
        assert ai_utils._classify_error("Network connection failed") == "connection"
        assert ai_utils._classify_error("Connection error") == "connection"

    def test_classify_error_model(self):
        """Test _classify_error for model errors."""
        assert ai_utils._classify_error("Model not found") == "model"
        assert ai_utils._classify_error("Invalid model") == "model"

    def test_classify_error_unknown(self):
        """Test _classify_error for unknown errors."""
        assert ai_utils._classify_error("Some unknown error") == "unknown"
        assert ai_utils._classify_error("Random error") == "unknown"
        assert ai_utils._classify_error("Some other issue") == "unknown"


class TestCountTokens:
    """Test count_tokens function."""

    def test_count_tokens(self):
        """Test token counting functionality."""
        # Test with string content
        text = "Hello, world!"
        token_count = ai_utils.count_tokens(text, "openai:gpt-4")
        assert token_count > 0
        assert isinstance(token_count, int)

    def test_count_tokens_empty_content(self):
        """Test token counting with empty content."""
        assert ai_utils.count_tokens("", "openai:gpt-4") == 0
        assert ai_utils.count_tokens([], "openai:gpt-4") == 0
        assert ai_utils.count_tokens({}, "openai:gpt-4") == 0

    @patch("gac.ai_utils.tiktoken")
    def test_local_providers_use_default_encoding(self, mock_tiktoken):
        """Test that local providers (ollama, lm-studio, custom-openai, custom-anthropic) use default encoding without network calls."""
        import gac.constants

        # Clear the lru_cache
        ai_utils.get_encoding.cache_clear()

        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2, 3, 4]  # 4 tokens for "Hello, world!"
        mock_tiktoken.get_encoding.return_value = mock_encoding

        text = "Hello, world!"

        # Test ollama provider
        token_count = ai_utils.count_tokens(text, "ollama:llama2")
        assert token_count == 4
        mock_tiktoken.get_encoding.assert_called_with(gac.constants.Utility.DEFAULT_ENCODING)
        mock_tiktoken.encoding_for_model.assert_not_called()

        # Reset mock
        mock_tiktoken.reset_mock()
        ai_utils.get_encoding.cache_clear()

        # Test lm-studio provider
        token_count = ai_utils.count_tokens(text, "lm-studio:local-model")
        assert token_count == 4
        mock_tiktoken.get_encoding.assert_called_with(gac.constants.Utility.DEFAULT_ENCODING)
        mock_tiktoken.encoding_for_model.assert_not_called()

        # Reset mock
        mock_tiktoken.reset_mock()
        ai_utils.get_encoding.cache_clear()

        # Test custom-openai provider
        token_count = ai_utils.count_tokens(text, "custom-openai:local-gpt4")
        assert token_count == 4
        mock_tiktoken.get_encoding.assert_called_with(gac.constants.Utility.DEFAULT_ENCODING)
        mock_tiktoken.encoding_for_model.assert_not_called()

        # Reset mock
        mock_tiktoken.reset_mock()
        ai_utils.get_encoding.cache_clear()

        # Test custom-anthropic provider
        token_count = ai_utils.count_tokens(text, "custom-anthropic:local-claude")
        assert token_count == 4
        mock_tiktoken.get_encoding.assert_called_with(gac.constants.Utility.DEFAULT_ENCODING)
        mock_tiktoken.encoding_for_model.assert_not_called()

    @patch("gac.ai_utils.tiktoken")
    def test_cloud_providers_use_model_specific_encoding(self, mock_tiktoken):
        """Test that cloud providers try to use model-specific encoding first."""
        # Clear the lru_cache
        ai_utils.get_encoding.cache_clear()

        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2, 3, 4]  # 4 tokens for "Hello, world!"
        mock_tiktoken.encoding_for_model.return_value = mock_encoding

        text = "Hello, world!"

        # Test openai provider
        token_count = ai_utils.count_tokens(text, "openai:gpt-4")
        assert token_count == 4
        mock_tiktoken.encoding_for_model.assert_called_with("gpt-4")
        mock_tiktoken.get_encoding.assert_not_called()

    @patch("gac.ai_utils.tiktoken")
    def test_fallback_to_default_encoding_on_error(self, mock_tiktoken):
        """Test fallback to default encoding when model-specific encoding fails."""
        import gac.constants

        # Clear the lru_cache
        ai_utils.get_encoding.cache_clear()

        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2, 3, 4]  # 4 tokens for "Hello, world!"
        mock_tiktoken.encoding_for_model.side_effect = ConnectionError("Network error")
        mock_tiktoken.get_encoding.return_value = mock_encoding

        text = "Hello, world!"

        # Test with cloud provider that fails
        token_count = ai_utils.count_tokens(text, "openai:gpt-4")
        assert token_count == 4
        mock_tiktoken.encoding_for_model.assert_called_with("gpt-4")
        mock_tiktoken.get_encoding.assert_called_with(gac.constants.Utility.DEFAULT_ENCODING)

    def test_no_tiktoken_mode_skips_tiktoken(self, monkeypatch):
        """Ensure rough token counting mode bypasses tiktoken entirely."""
        monkeypatch.setenv("GAC_NO_TIKTOKEN", "true")
        ai_utils._should_skip_tiktoken_counting.cache_clear()

        sample_text = "offline token counting"

        with patch("gac.ai_utils.get_encoding") as mock_get_encoding:
            tokens = ai_utils.count_tokens(sample_text, "openai:gpt-4")

        assert tokens == len(sample_text) // 4
        mock_get_encoding.assert_not_called()

        monkeypatch.delenv("GAC_NO_TIKTOKEN", raising=False)
        ai_utils._should_skip_tiktoken_counting.cache_clear()


class TestAIError:
    """Test AIError class."""

    def test_ai_error_class_exists(self):
        """Test that AIError class exists and can be instantiated."""
        error = AIError("Test error")
        assert str(error) == "Test error"

    def test_ai_error_with_type(self):
        """Test AIError with error type."""
        error = AIError("Test error", error_type="model")
        assert error.error_type == "model"


class TestGenerateWithRetries:
    def test_unsupported_provider(self):
        with pytest.raises(AIError) as e:
            ai_utils.generate_with_retries({}, "bad:model", [], 0.7, 100, 1, True)
        assert e.value.error_type == "model"

    def test_empty_messages(self):
        with pytest.raises(AIError) as e:
            ai_utils.generate_with_retries({}, "openai:gpt-4", [], 0.7, 100, 1, True)
        assert e.value.error_type == "model"

    def test_missing_provider_func(self):
        with pytest.raises(AIError) as e:
            ai_utils.generate_with_retries({}, "openai:gpt-4", [{"role": "user", "content": "x"}], 0.7, 100, 1, True)
        assert e.value.error_type == "model"

    @patch("gac.ai_utils.Status")
    def test_skip_success_message(self, mock_status):
        mock_spinner = MagicMock()
        mock_status.return_value = mock_spinner
        funcs = {"openai": lambda **kw: "ok"}
        ai_utils.generate_with_retries(
            funcs, "openai:gpt-4", [{"role": "user", "content": "x"}], 0.7, 100, 1, False, False, True
        )
        mock_spinner.stop.assert_called_once()

    def test_empty_content(self):
        funcs = {"openai": lambda **kw: ""}
        with pytest.raises(AIError) as e:
            ai_utils.generate_with_retries(funcs, "openai:gpt-4", [{"role": "user", "content": "x"}], 0.7, 100, 1, True)
        assert e.value.error_type == "model"

    def test_none_content(self):
        funcs = {"openai": lambda **kw: None}
        with pytest.raises(AIError) as e:
            ai_utils.generate_with_retries(funcs, "openai:gpt-4", [{"role": "user", "content": "x"}], 0.7, 100, 1, True)
        assert e.value.error_type == "model"

    @patch("gac.ai_utils.Status")
    @patch("gac.ai_utils.console")
    def test_auth_error_spinner_fail(self, mock_console, mock_status):
        mock_spinner = MagicMock()
        mock_status.return_value = mock_spinner

        def raise_auth_error(**kw):
            raise AIError.authentication_error("Invalid API key")

        funcs = {"openai": raise_auth_error}
        with pytest.raises(AIError):
            ai_utils.generate_with_retries(
                funcs, "openai:gpt-4", [{"role": "user", "content": "x"}], 0.7, 100, 1, False
            )
        mock_spinner.stop.assert_called()
        mock_console.print.assert_called_once()

    @patch("gac.ai_utils.time.sleep")
    def test_retry_warning(self, mock_sleep):
        call_count = [0]

        def func(**kw):
            call_count[0] += 1
            if call_count[0] < 2:
                raise AIError.connection_error("fail")
            return "ok"

        funcs = {"openai": func}
        ai_utils.generate_with_retries(funcs, "openai:gpt-4", [{"role": "user", "content": "x"}], 0.7, 100, 2, True)
        assert call_count[0] == 2

    def test_final_auth_error(self):
        def raise_auth_error(**kw):
            raise AIError.authentication_error("Invalid API key")

        funcs = {"openai": raise_auth_error}
        with pytest.raises(AIError) as e:
            ai_utils.generate_with_retries(funcs, "openai:gpt-4", [{"role": "user", "content": "x"}], 0.7, 100, 2, True)
        assert e.value.error_type == "authentication"

    def test_final_model_error(self):
        def raise_model_error(**kw):
            raise AIError.model_error("Model not found")

        funcs = {"openai": raise_model_error}
        with pytest.raises(AIError) as e:
            ai_utils.generate_with_retries(funcs, "openai:gpt-4", [{"role": "user", "content": "x"}], 0.7, 100, 2, True)
        assert e.value.error_type == "model"
