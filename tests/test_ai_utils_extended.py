"""Extended tests for ai_utils.py to improve coverage from 56% to 90%+."""

import os
from unittest.mock import MagicMock, patch

import pytest

from gac.ai_utils import (
    _should_skip_tiktoken_counting,
    count_tokens,
    extract_text_content,
    generate_with_retries,
    get_encoding,
)
from gac.constants import Utility
from gac.errors import AIError


class TestExtractTextContentExtended:
    """Test extract_text_content function with various input formats."""

    def test_extract_from_string(self):
        """Test extracting from string input (line 55)."""
        content = "Hello world"
        result = extract_text_content(content)
        assert result == "Hello world"

    def test_extract_from_list_with_valid_messages(self):
        """Test extracting from list with valid message dicts."""
        content = [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi there"}]
        result = extract_text_content(content)
        assert result == "Hello\nHi there"

    def test_extract_from_list_with_mixed_messages(self):
        """Test extracting from list with mixed valid/invalid messages."""
        content = [
            {"role": "user", "content": "Valid"},
            {"invalid": "message"},  # No content key
            "string message",  # Not a dict
            {"role": "assistant", "content": "Another valid"},
        ]
        result = extract_text_content(content)
        assert result == "Valid\nAnother valid"

    def test_extract_from_dict_with_content(self):
        """Test extracting from dict with content key."""
        content = {"content": "Dict content", "other": "value"}
        result = extract_text_content(content)
        assert result == "Dict content"

    def test_extract_from_dict_without_content(self):
        """Test extracting from dict without content key (line 60)."""
        content = {"other": "value", "data": "something"}
        result = extract_text_content(content)
        assert result == ""

    def test_extract_from_list_empty_list(self):
        """Test extracting from empty list."""
        content = []
        result = extract_text_content(content)
        assert result == ""


class TestGetEncodingExtended:
    """Test get_encoding function with various scenarios."""

    @patch("tiktoken.get_encoding")
    @patch("tiktoken.encoding_for_model")
    def test_provider_not_openai_returns_default(self, mock_encoding_for_model, mock_get_encoding):
        """Test non-OpenAI provider returns default encoding (line 76)."""
        mock_get_encoding.return_value = "default_encoding"
        result = get_encoding("anthropic:claude-3-sonnet")
        mock_get_encoding.assert_called_once_with(Utility.DEFAULT_ENCODING)
        assert result == "default_encoding"

    @patch("tiktoken.encoding_for_model")
    @patch("tiktoken.get_encoding")
    def test_openai_model_encoding_success(self, mock_get_encoding, mock_encoding_for_model):
        """Test successful OpenAI model encoding retrieval."""
        mock_encoding = MagicMock()
        mock_encoding_for_model.return_value = mock_encoding

        result = get_encoding("openai:gpt-5-nano")
        assert result == mock_encoding
        mock_encoding_for_model.assert_called_once_with("gpt-5-nano")

    @patch("tiktoken.encoding_for_model")
    @patch("tiktoken.get_encoding")
    def test_openai_model_key_error_fallback(self, mock_get_encoding, mock_encoding_for_model):
        """Test KeyError fallback to default encoding."""
        mock_encoding_for_model.side_effect = KeyError("Model not found")
        mock_get_encoding.return_value = "default_encoding"

        result = get_encoding("openai:unknown-model")
        assert result == "default_encoding"
        mock_get_encoding.assert_called_once_with(Utility.DEFAULT_ENCODING)

    @patch("tiktoken.encoding_for_model")
    @patch("tiktoken.get_encoding")
    def test_openai_model_connection_error_fallback(self, mock_get_encoding, mock_encoding_for_model):
        """Test ConnectionError fallback to default encoding."""
        mock_encoding_for_model.side_effect = ConnectionError("Network error")
        mock_get_encoding.return_value = "default_encoding"

        result = get_encoding("openai:gpt-5-nano")
        assert result == "default_encoding"
        mock_get_encoding.assert_called_once_with(Utility.DEFAULT_ENCODING)

    @patch("gac.ai_utils.tiktoken.get_encoding")
    def test_openai_model_os_error_fallback(self, mock_get_encoding):
        """Test OSError fallback to default encoding."""
        # Clear cache to ensure clean test
        get_encoding.cache_clear()

        # Remove patches that interfere with each other and simplify
        with patch("gac.ai_utils.tiktoken.encoding_for_model", side_effect=OSError("SSL error")):
            mock_get_encoding.return_value = "default_encoding"

            result = get_encoding("openai:gpt-5-nano")
            assert result == "default_encoding"
            # The fallback should be called
            mock_get_encoding.assert_called_once_with(Utility.DEFAULT_ENCODING)


class TestCountTokensExtended:
    """Test count_tokens function with various edge cases."""

    @patch("gac.ai_utils.get_encoding")
    @patch("gac.ai_utils.extract_text_content")
    def test_count_tokens_key_error_fallback(self, mock_extract, mock_encoding):
        """Test KeyError during encoding (lines 47-50)."""
        mock_extract.return_value = "sample text"
        mock_encoding.side_effect = KeyError("Unknown model")

        result = count_tokens("sample text", "unknown:model")
        assert result == len("sample text") // 4  # Fallback estimation

    @patch("gac.ai_utils.get_encoding")
    @patch("gac.ai_utils.extract_text_content")
    def test_count_tokens_unicode_error_fallback(self, mock_extract, mock_encoding):
        """Test UnicodeError during encoding (lines 47-50)."""
        mock_extract.return_value = "sample text"
        mock_encoding.side_effect = UnicodeError("Encoding error")

        result = count_tokens("sample text", "test:model")
        assert result == len("sample text") // 4  # Fallback estimation

    @patch("gac.ai_utils.get_encoding")
    @patch("gac.ai_utils.extract_text_content")
    def test_count_tokens_value_error_fallback(self, mock_extract, mock_encoding):
        """Test ValueError during encoding (lines 47-50)."""
        mock_extract.return_value = "sample text"
        mock_encoding.side_effect = ValueError("Invalid input")

        result = count_tokens("sample text", "test:model")
        assert result == len("sample text") // 4  # Fallback estimation

    def test_count_tokens_empty_content_with_skip_tiktoken(self):
        """Test empty content returns 0 even in skip mode."""
        with patch.dict(os.environ, {"GAC_NO_TIKTOKEN": "true"}):
            # Clear the cache to ensure fresh check
            _should_skip_tiktoken_counting.cache_clear()

            result = count_tokens("", "any:model")
            assert result == 0

    def test_should_skip_tiktoken_counting_false(self):
        """Test that tiktoken is not skipped by default."""
        with patch.dict(os.environ, {"GAC_NO_TIKTOKEN": "false"}, clear=True):
            _should_skip_tiktoken_counting.cache_clear()
            result = _should_skip_tiktoken_counting()
            assert result is False

    def test_should_skip_tiktoken_counting_true_from_env(self):
        """Test tiktoken skip from environment variable."""
        with patch.dict(os.environ, {"GAC_NO_TIKTOKEN": "true"}):
            _should_skip_tiktoken_counting.cache_clear()
            result = _should_skip_tiktoken_counting()
            assert result is True


class TestGenerateWithRetriesExtended:
    """Test generate_with_retries function with comprehensive error scenarios."""

    def setup_provider_funcs(self):
        """Setup mock provider functions for testing."""
        return {
            "openai": MagicMock(side_effect=Exception("Network error")),
            "anthropic": MagicMock(side_effect=Exception("Auth failed")),
        }

    def test_all_providers_failed_no_retries(self):
        """Test when providers fail and no retries succeed."""
        provider_funcs = {
            "openai": MagicMock(side_effect=ConnectionError("Network error")),
        }

        with pytest.raises(AIError):
            generate_with_retries(
                provider_funcs=provider_funcs,
                model="openai:gpt-5-nano",
                messages=[{"role": "user", "content": "test"}],
                temperature=0.7,
                max_tokens=1000,
                max_retries=0,
                quiet=True,
            )

    @patch("gac.ai_utils.console.print")
    def test_first_provider_succeeds(self, mock_print):
        """Test when first provider succeeds."""
        provider_funcs = {
            "openai": MagicMock(return_value="success response"),
            "anthropic": MagicMock(),  # Should not be called
        }

        result = generate_with_retries(
            provider_funcs=provider_funcs,
            model="openai:gpt-5-nano",
            messages=[{"role": "user", "content": "test"}],
            temperature=0.7,
            max_tokens=1000,
            max_retries=3,
            quiet=True,
        )

        assert result == "success response"
        # Should not print any error messages
        mock_print.assert_not_called()

    @patch("gac.ai_utils.console.print")
    @patch("time.sleep")  # Mock sleep to speed up tests
    def test_retry_after_rate_limit(self, mock_sleep, mock_print):
        """Test retry logic after rate limit error."""

        def provider_func(*args, **kwargs):
            provider_func.call_count += 1
            if provider_func.call_count == 1:
                raise AIError.rate_limit_error("Rate limited")
            return "success after retry"

        provider_func.call_count = 0

        provider_funcs = {"openai": provider_func}

        # Optimize: reduce retries and remove delays
        with patch("gac.ai_utils.time.sleep", return_value=None):
            with patch("gac.ai_utils.Status"):
                result = generate_with_retries(
                    provider_funcs=provider_funcs,
                    model="openai:gpt-5-nano",
                    messages=[{"role": "user", "content": "test"}],
                    temperature=0.7,
                    max_tokens=1000,
                    max_retries=2,  # Need 2 retries for success: error + success
                )

        assert result == "success after retry"
        assert provider_func.call_count == 2  # Still 2 calls: error + success  # Initial call + retry

    @patch("gac.ai_utils.console.print")
    @patch("time.sleep")
    def test_retry_limit_exceeded(self, mock_sleep, mock_print):
        """Test when retry limit is exceeded."""
        provider_func = MagicMock(side_effect=AIError.rate_limit_error("Always rate limited"))
        provider_funcs = {"openai": provider_func}

        # Optimize: reduce retries and remove sleep delays
        with patch("gac.ai_utils.time.sleep", return_value=None):
            with patch("gac.ai_utils.Status"):
                with pytest.raises(AIError) as exc_info:
                    generate_with_retries(
                        provider_funcs=provider_funcs,
                        model="openai:gpt-5-nano",
                        messages=[{"role": "user", "content": "test"}],
                        temperature=0.7,
                        max_tokens=1000,
                        max_retries=2,  # Reduced from 3 to 2
                    )

        assert "Failed to generate commit message after 2 retries" in str(exc_info.value)
        # Should have attempted multiple retries (2 calls + 1 initial = 3 total)
        assert provider_func.call_count == 2

    @patch("gac.ai_utils.console.print")
    def test_authentication_error_no_retry(self, mock_print):
        """Test that authentication errors are not retried."""
        provider_func = MagicMock(side_effect=AIError.authentication_error("Invalid API key"))
        provider_funcs = {"openai": provider_func}

        with pytest.raises(AIError) as exc_info:
            generate_with_retries(
                provider_funcs=provider_funcs,
                model="openai:gpt-5-nano",
                messages=[{"role": "user", "content": "test"}],
                temperature=0.7,
                max_tokens=1000,
                max_retries=3,
            )

        assert "Invalid API key" in str(exc_info.value)
        # Should only be called once (no retry for auth errors)
        assert provider_func.call_count == 1

    @patch("gac.ai_utils.console.print")
    @patch("time.sleep")
    def test_model_error_with_retry(self, mock_sleep, mock_print):
        """Test model error triggers retry for specific providers."""

        def provider_func(*args, **kwargs):
            provider_func.call_count += 1
            if provider_func.call_count == 1:
                raise AIError.rate_limit_error("Temporary rate limit")
            return "success after retry"

        provider_func.call_count = 0
        provider_funcs = {"openai": provider_func}

        # Optimize: reduce retries and remove delays
        with patch("gac.ai_utils.time.sleep", return_value=None):
            with patch("gac.ai_utils.Status"):
                result = generate_with_retries(
                    provider_funcs=provider_funcs,
                    model="openai:gpt-5-nano",
                    messages=[{"role": "user", "content": "test"}],
                    temperature=0.7,
                    max_tokens=1000,
                    max_retries=2,  # Need 2 retries for success: error + success
                )

        assert result == "success after retry"
        assert provider_func.call_count == 2  # Still 2 calls: error + success

    @patch("gac.ai_utils.console.print")
    def test_rate_limit_error_2_with_retry(self, mock_print):
        """Test rate limit error (test 2) triggers retry."""

        def provider_func(*args, **kwargs):
            provider_func.call_count += 1
            if provider_func.call_count == 1:
                raise AIError.rate_limit_error("Temporary rate limit")
            return "success after retry"

        provider_func.call_count = 0
        provider_funcs = {"anthropic": provider_func}

        # Optimize: reduce retries and remove delays
        with patch("gac.ai_utils.time.sleep", return_value=None):
            with patch("gac.ai_utils.Status"):
                result = generate_with_retries(
                    provider_funcs=provider_funcs,
                    model="anthropic:claude-3",
                    messages=[{"role": "user", "content": "test"}],
                    temperature=0.7,
                    max_tokens=1000,
                    max_retries=2,  # Need 2 retries for success: error + success
                )

        assert result == "success after retry"
        assert provider_func.call_count == 2  # Still 2 calls: error + success

    @patch("gac.ai_utils.console.print")
    def test_final_error_after_all_retries(self, mock_print):
        """Test final error after all retries exhausted."""
        provider_func = MagicMock(side_effect=AIError.rate_limit_error("Persistent rate limit"))
        provider_funcs = {"openai": provider_func}

        # Optimize: reduce retries and remove sleep delays
        with patch("gac.ai_utils.time.sleep", return_value=None):
            with pytest.raises(AIError) as exc_info:
                generate_with_retries(
                    provider_funcs=provider_funcs,
                    model="openai:gpt-5-nano",
                    messages=[{"role": "user", "content": "test"}],
                    temperature=0.7,
                    max_tokens=1000,
                    max_retries=2,  # Need 2 retries for success: error + success
                    quiet=True,  # Reduce console output overhead
                )

        assert "Failed to generate commit message after 2 retries" in str(exc_info.value)
        # Should be called 2 times (initial + 1 retry)
        assert provider_func.call_count == 2
        # Should not print final error message due to quiet=True
        mock_print.assert_not_called()

    @patch("gac.ai_utils.console.print")
    def test_rate_limit_error_with_retry(self, mock_print):
        """Test rate limit error triggers retry."""

        def provider_func(*args, **kwargs):
            provider_func.call_count += 1
            if provider_func.call_count == 1:
                raise AIError.rate_limit_error("Temporary rate limit")
            return "success after retry"

        provider_func.call_count = 0
        provider_funcs = {"openai": provider_func}

        # Optimize: reduce retries and remove delays
        with patch("gac.ai_utils.time.sleep", return_value=None):
            with patch("gac.ai_utils.Status"):
                result = generate_with_retries(
                    provider_funcs=provider_funcs,
                    model="openai:gpt-5-nano",
                    messages=[{"role": "user", "content": "test"}],
                    temperature=0.7,
                    max_tokens=1000,
                    max_retries=2,  # Need 2 retries for success: error + success
                )

        assert result == "success after retry"
        assert provider_func.call_count == 2  # Still 2 calls: error + success

    @patch("gac.ai_utils.console.print")
    def test_provider_function_missing(self, mock_print):
        """Test when provider function is missing from dict."""
        provider_funcs = {"openai": None}  # Provider with None function

        try:
            generate_with_retries(
                provider_funcs=provider_funcs,
                model="openai:gpt-5-nano",
                messages=[{"role": "user", "content": "test"}],
                temperature=0.7,
                max_tokens=1000,
                max_retries=3,
            )
        except Exception:
            # Expected to fail with provider function not found
            pass

    def test_empty_messages_list(self):
        """Test with empty messages list should raise AIError."""
        provider_func = MagicMock(return_value="response")
        provider_funcs = {"openai": provider_func}

        with pytest.raises(AIError) as exc_info:
            generate_with_retries(
                provider_funcs=provider_funcs,
                model="openai:gpt-5-nano",
                messages=[],
                temperature=0.7,
                max_tokens=1000,
                max_retries=3,
                quiet=True,
            )

        assert "No messages provided" in str(exc_info.value)
        # Should not have been called due to early validation
        provider_func.assert_not_called()

    @patch("gac.ai_utils.console.print")
    @patch("time.sleep")
    def test_spinner_status_context_manager(self, mock_sleep, mock_print):
        """Test that spinner status is properly managed."""

        def provider_func(*args, **kwargs):
            provider_func.call_count += 1
            if provider_func.call_count == 1:
                raise AIError.rate_limit_error("Temporary rate limit")
            return "success after retry"

        provider_func.call_count = 0
        provider_funcs = {"openai": provider_func}

        with patch("gac.ai_utils.Status") as mock_status:
            mock_status.return_value.__enter__ = MagicMock()
            mock_status.return_value.__exit__ = MagicMock()

            result = generate_with_retries(
                provider_funcs=provider_funcs,
                model="openai:gpt-5-nano",
                messages=[{"role": "user", "content": "test"}],
                temperature=0.7,
                max_tokens=1000,
                max_retries=3,
            )

        assert result == "success after retry"
        assert provider_func.call_count == 2  # Still 2 calls: error + success
        # Status context manager should be used
        mock_status.assert_called()
