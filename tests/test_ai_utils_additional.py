"""Additional tests to improve ai_utils.py coverage."""

import os
from unittest import mock

import pytest
import tiktoken

from gac.ai_utils import (
    _should_skip_tiktoken_counting,
    count_tokens,
    extract_text_content,
    generate_with_retries,
    get_encoding,
)
from gac.errors import AIError


class TestAIUtilsMissingCoverage:
    """Test missing coverage areas in ai_utils.py."""

    def test_count_tokens_empty_content(self):
        """Test count_tokens with empty content."""
        result = count_tokens("", "test-model")
        assert result == 0

    def test_count_tokens_none_content(self):
        """Test count_tokens with None content."""
        result = count_tokens(None, "test-model")  # type: ignore
        assert result == 0

    def test_count_tokens_list_content(self):
        """Test count_tokens with list content."""
        content = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
        ]
        result = count_tokens(content, "test-model")
        assert result > 0

    def test_count_tokens_dict_content(self):
        """Test count_tokens with dict content."""
        content = {"role": "user", "content": "Hello world"}
        result = count_tokens(content, "test-model")
        assert result > 0

    def test_count_tokens_invalid_dict(self):
        """Test count_tokens with dict without content."""
        content = {"role": "user", "message": "Hello"}  # No "content" key
        result = count_tokens(content, "test-model")
        assert result == 0

    def test_extract_text_content_string(self):
        """Test extract_text_content with string."""
        result = extract_text_content("Hello world")
        assert result == "Hello world"

    def test_extract_text_content_list(self):
        """Test extract_text_content with list."""
        content = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
        ]
        result = extract_text_content(content)
        assert "Hello" in result
        assert "Hi" in result

    def test_extract_text_content_dict(self):
        """Test extract_text_content with dict."""
        content = {"role": "user", "content": "Hello"}
        result = extract_text_content(content)
        assert result == "Hello"

    def test_extract_text_content_invalid_list(self):
        """Test extract_text_content with invalid list items."""
        content = [
            {"role": "user"},  # No content
            "invalid item",  # Not a dict
        ]
        result = extract_text_content(content)
        assert result == ""

    def test_extract_text_content_invalid_dict(self):
        """Test extract_text_content with dict without content."""
        content = {"role": "user", "message": "Hello"}
        result = extract_text_content(content)
        assert result == ""

    def test_get_encoding_keyerror_fallback(self):
        """Test get_encoding with KeyError fallback (line 138, 142)."""
        with mock.patch("tiktoken.encoding_for_model", side_effect=KeyError("Model not found")):
            result = get_encoding("openai:unknown-model")
            assert isinstance(result, tiktoken.Encoding)

    def test_get_encoding_oserror_fallback(self):
        """Test get_encoding with OSError fallback (line 142)."""
        with mock.patch("tiktoken.encoding_for_model", side_effect=OSError("Network error")):
            result = get_encoding("openai:gpt-4o")
            assert isinstance(result, tiktoken.Encoding)

    def test_get_encoding_connection_error_fallback(self):
        """Test get_encoding with ConnectionError fallback."""
        with mock.patch("tiktoken.encoding_for_model", side_effect=ConnectionError("Connection failed")):
            result = get_encoding("openai:gpt-4o")
            assert isinstance(result, tiktoken.Encoding)

    def test_get_encoding_non_openai_provider(self):
        """Test get_encoding with non-OpenAI provider."""
        result = get_encoding("anthropic:claude-3")
        assert isinstance(result, tiktoken.Encoding)

    def test_should_skip_tiktoken_counting_env_true(self):
        """Test _should_skip_tiktoken_counting with GAC_NO_TIKTOKEN=true."""
        with mock.patch.dict(os.environ, {"GAC_NO_TIKTOKEN": "true"}):
            # Clear the cache to pick up the new environment variable
            _should_skip_tiktoken_counting.cache_clear()
            result = _should_skip_tiktoken_counting()
            assert result is True

    def test_should_skip_tiktoken_counting_env_false(self):
        """Test _should_skip_tiktoken_counting with GAC_NO_TIKTOKEN=false."""
        with mock.patch.dict(os.environ, {"GAC_NO_TIKTOKEN": "false"}):
            # Clear the cache to pick up the new environment variable
            _should_skip_tiktoken_counting.cache_clear()
            result = _should_skip_tiktoken_counting()
            assert result is False

    def test_should_skip_tiktoken_counting_default(self):
        """Test _should_skip_tiktoken_counting with default."""
        with mock.patch.dict(os.environ, {}, clear=True):
            # Clear the cache to pick up the new environment variable
            _should_skip_tiktoken_counting.cache_clear()
            result = _should_skip_tiktoken_counting()
            assert result is False  # Default should be False

    def test_generate_with_retries_invalid_model_format(self):
        """Test generate_with_retries with invalid model format."""
        with pytest.raises(AIError) as exc_info:
            generate_with_retries(
                provider_funcs={},
                model="invalid-model-format",  # No colon
                messages=[{"role": "user", "content": "Hello"}],
                temperature=0.7,
                max_tokens=100,
                max_retries=1,
            )
        assert "Invalid model format" in str(exc_info.value)

    def test_generate_with_retries_unsupported_provider(self):
        """Test generate_with_retries with unsupported provider."""
        with pytest.raises(AIError) as exc_info:
            generate_with_retries(
                provider_funcs={},
                model="unsupported:model",
                messages=[{"role": "user", "content": "Hello"}],
                temperature=0.7,
                max_tokens=100,
                max_retries=1,
            )
        assert "Unsupported provider" in str(exc_info.value)

    def test_generate_with_retries_no_messages(self):
        """Test generate_with_retries with no messages."""
        with pytest.raises(AIError) as exc_info:
            generate_with_retries(
                provider_funcs={},
                model="openai:gpt-4o",
                messages=[],  # Empty messages
                temperature=0.7,
                max_tokens=100,
                max_retries=1,
            )
        assert "No messages provided" in str(exc_info.value)

    def test_generate_with_retries_provider_function_not_found(self):
        """Test generate_with_retries when provider function not found."""
        provider_funcs = {"openai": lambda **kwargs: "response"}  # Only openai available

        with pytest.raises(AIError) as exc_info:
            generate_with_retries(
                provider_funcs=provider_funcs,
                model="anthropic:claude-3",
                messages=[{"role": "user", "content": "Hello"}],
                temperature=0.7,
                max_tokens=100,
                max_retries=1,
            )
        assert "Provider function not found" in str(exc_info.value)

    def test_generate_with_retries_empty_response(self):
        """Test generate_with_retries with empty response."""
        provider_funcs = {"openai": lambda **kwargs: ""}  # Empty response

        with pytest.raises(AIError) as exc_info:
            generate_with_retries(
                provider_funcs=provider_funcs,
                model="openai:gpt-4o",
                messages=[{"role": "user", "content": "Hello"}],
                temperature=0.7,
                max_tokens=100,
                max_retries=1,
            )
        assert "Empty response from AI model" in str(exc_info.value)

    def test_generate_with_retries_none_response(self):
        """Test generate_with_retries with None response."""
        provider_funcs = {"openai": lambda **kwargs: None}  # None response

        with pytest.raises(AIError) as exc_info:
            generate_with_retries(
                provider_funcs=provider_funcs,
                model="openai:gpt-4o",
                messages=[{"role": "user", "content": "Hello"}],
                temperature=0.7,
                max_tokens=100,
                max_retries=1,
            )
        assert "Empty response from AI model" in str(exc_info.value)

    def test_generate_with_retries_whitespace_only_response(self):
        """Test generate_with_retries with whitespace-only response."""
        provider_funcs = {"openai": lambda **kwargs: "   \n  "}  # Whitespace only

        with pytest.raises(AIError) as exc_info:
            generate_with_retries(
                provider_funcs=provider_funcs,
                model="openai:gpt-4o",
                messages=[{"role": "user", "content": "Hello"}],
                temperature=0.7,
                max_tokens=100,
                max_retries=1,
            )
        assert "Empty response from AI model" in str(exc_info.value)

    def test_generate_with_retries_authentication_error_no_retry(self):
        """Test generate_with_retries with authentication error (should not retry)."""

        def auth_error_provider(**kwargs):
            raise AIError.authentication_error("Auth failed")

        provider_funcs = {"openai": auth_error_provider}

        with pytest.raises(AIError) as exc_info:
            generate_with_retries(
                provider_funcs=provider_funcs,
                model="openai:gpt-4o",
                messages=[{"role": "user", "content": "Hello"}],
                temperature=0.7,
                max_tokens=100,
                max_retries=3,
            )
        assert "Auth failed" in str(exc_info.value)

    def test_generate_with_retries_model_error_no_retry(self):
        """Test generate_with_retries with model error (should not retry)."""

        def model_error_provider(**kwargs):
            raise AIError.model_error("Model error")

        provider_funcs = {"openai": model_error_provider}

        with pytest.raises(AIError) as exc_info:
            generate_with_retries(
                provider_funcs=provider_funcs,
                model="openai:gpt-4o",
                messages=[{"role": "user", "content": "Hello"}],
                temperature=0.7,
                max_tokens=100,
                max_retries=3,
            )
        assert "Model error" in str(exc_info.value)

    def test_generate_with_retries_rate_limit_error_with_retry(self):
        """Test generate_with_retries with rate limit error (should retry)."""
        call_count = 0

        def rate_limit_provider(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise AIError.rate_limit_error("Rate limited")
            return "Success"

        provider_funcs = {"openai": rate_limit_provider}

        with mock.patch("time.sleep"):  # Mock sleep to speed up test
            result = generate_with_retries(
                provider_funcs=provider_funcs,
                model="openai:gpt-4o",
                messages=[{"role": "user", "content": "Hello"}],
                temperature=0.7,
                max_tokens=100,
                max_retries=2,
                quiet=True,  # Quiet mode for cleaner output
            )
            assert result == "Success"
            assert call_count == 2  # Should have been called twice

    def test_generate_with_retries_timeout_error_with_retry(self):
        """Test generate_with_retries with timeout error (should retry)."""
        call_count = 0

        def timeout_provider(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise AIError.timeout_error("Timeout")
            return "Success"

        provider_funcs = {"openai": timeout_provider}

        with mock.patch("time.sleep"):
            result = generate_with_retries(
                provider_funcs=provider_funcs,
                model="openai:gpt-4o",
                messages=[{"role": "user", "content": "Hello"}],
                temperature=0.7,
                max_tokens=100,
                max_retries=2,
                quiet=True,
            )
            assert result == "Success"
            assert call_count == 2

    def test_generate_with_retries_connection_error_with_retry(self):
        """Test generate_with_retries with connection error (should retry)."""
        call_count = 0

        def connection_provider(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise AIError.connection_error("Connection failed")
            return "Success"

        provider_funcs = {"openai": connection_provider}

        with mock.patch("time.sleep"):
            result = generate_with_retries(
                provider_funcs=provider_funcs,
                model="openai:gpt-4o",
                messages=[{"role": "user", "content": "Hello"}],
                temperature=0.7,
                max_tokens=100,
                max_retries=2,
                quiet=True,
            )
            assert result == "Success"
            assert call_count == 2

    def test_generate_with_retries_all_retries_failed_unknown_error(self):
        """Test generate_with_retries when all retries fail with unknown error."""

        def always_error_provider(**kwargs):
            raise AIError.unknown_error("Unknown error")

        provider_funcs = {"openai": always_error_provider}

        with pytest.raises(AIError) as exc_info:
            generate_with_retries(
                provider_funcs=provider_funcs,
                model="openai:gpt-4o",
                messages=[{"role": "user", "content": "Hello"}],
                temperature=0.7,
                max_tokens=100,
                max_retries=2,
                quiet=True,
            )
        assert "Failed to generate commit message after 2 retries" in str(exc_info.value)

    def test_count_tokens_tiktoken_error_fallback(self):
        """Test count_tokens falls back when tiktoken fails."""
        with mock.patch("gac.ai_utils.get_encoding", side_effect=KeyError("Encoding not found")):
            with mock.patch("gac.ai_utils._should_skip_tiktoken_counting", return_value=False):
                result = count_tokens("Hello world", "test-model")
                # Should fallback to rough estimation: len(text) // 4
                assert result == len("Hello world") // 4

    def test_count_tokens_unicode_error_fallback(self):
        """Test count_tokens falls back on UnicodeError."""
        with mock.patch("tiktoken.encoding_for_model", side_effect=UnicodeError("Unicode error")):
            with mock.patch("gac.ai_utils._should_skip_tiktoken_counting", return_value=False):
                result = count_tokens("Hello world", "test-model")
                assert result == len("Hello world") // 4

    def test_count_tokens_value_error_fallback(self):
        """Test count_tokens falls back on ValueError."""
        with mock.patch("tiktoken.encoding_for_model", side_effect=ValueError("Value error")):
            with mock.patch("gac.ai_utils._should_skip_tiktoken_counting", return_value=False):
                result = count_tokens("Hello world", "test-model")
                assert result == len("Hello world") // 4

    def test_count_tokens_skip_tiktoken(self):
        """Test count_tokens when tiktoken counting is skipped."""
        with mock.patch("gac.ai_utils._should_skip_tiktoken_counting", return_value=True):
            result = count_tokens("Hello world", "test-model")
            # Should use rough estimation
            assert result == len("Hello world") // 4
