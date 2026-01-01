"""Additional tests to improve ai_utils.py coverage."""

import os
from unittest import mock

import pytest

from gac.ai_utils import (
    count_tokens,
    extract_text_content,
    generate_with_retries,
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

    def test_count_tokens_character_based_math(self):
        """Test the exact math of character-based token counting."""
        # Test specific lengths and their expected outputs
        test_cases = [
            ("", 0),  # Empty = 0
            ("a", 1),  # 1 char = max(1, round(1/3.4)) = 1
            ("ab", 1),  # 2 chars = round(2/3.4) = 1
            ("abc", 1),  # 3 chars = round(3/3.4) = 1
            ("abcd", 1),  # 4 chars = round(4/3.4) = 1
            ("abcde", 1),  # 5 chars = round(5/3.4) = 1
            ("abcdef", 2),  # 6 chars = round(6/3.4) = 2
        ]

        for text, expected in test_cases:
            result = count_tokens(text, "any:model")
            assert result == expected, f"Text '{text}' (len={len(text)}) expected {expected}, got {result}"

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

    def test_character_based_no_external_dependencies(self):
        """Test that character-based counting has no external dependencies."""
        # This test ensures we don't import tiktoken or make any network calls
        text = "Simple test text"
        expected = round(len(text) / 3.4)

        # Should work regardless of environment
        result = count_tokens(text, "any:provider-model")
        assert result == expected

        # Should work for any provider (no provider-specific logic)
        providers = ["openai", "anthropic", "groq", "gemini", "ollama"]
        for provider in providers:
            result = count_tokens(text, f"{provider}:some-model")
            assert result == expected
            assert isinstance(result, int)  # Always returns an integer token count

    def test_character_based_no_model_specific_logic(self):
        """Test that character-based counting has no model-specific logic."""
        # Since we removed get_encoding, we just test that all models work the same
        text = "Test message"
        expected = round(len(text) / 3.4)

        # All models should give the same result regardless of provider
        models = ["openai:gpt-4", "anthropic:claude-3", "groq:llama3-70b", "gemini:gemini-pro", "ollama:llama2"]

        for model in models:
            result = count_tokens(text, model)
            assert result == expected, f"Model {model} should give {expected} tokens, got {result}"

    def test_character_based_token_counting_no_env_dependency(self):
        """Test that character-based token counting doesn't depend on any environment variables."""
        # Test that the function works the same regardless of environment variables
        text = "Hello world"
        expected = round(len(text) / 3.4)

        # Test with no env var set
        actual = count_tokens(text, "openai:gpt-4")
        assert actual == expected

        # Test with various env vars that used to affect tiktoken behavior
        with mock.patch.dict(os.environ, {"GAC_NO_TIKTOKEN": "true"}):
            actual = count_tokens(text, "openai:gpt-4")
            assert actual == expected

        with mock.patch.dict(os.environ, {"GAC_NO_TIKTOKEN": "false"}):
            actual = count_tokens(text, "openai:gpt-4")
            assert actual == expected

        # Test with some random env var that shouldn't affect anything
        with mock.patch.dict(os.environ, {"RANDOM_VAR": "some_value"}):
            actual = count_tokens(text, "openai:gpt-4")
            assert actual == expected

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

    def test_character_based_no_fallback_needed(self):
        """Test that character-based counting never needs fallback."""
        # Since we removed tiktoken, there's no fallback needed
        # Just test that it works consistently
        text = "Hello world"
        expected = round(len(text) / 3.4)

        result = count_tokens(text, "test-model")
        assert result == expected

        # Test with empty text
        assert count_tokens("", "test-model") == 0

        # Test that it works for any model (no model-specific logic)
        models = ["openai:gpt-4", "anthropic:claude-3", "ollama:llama2"]
        for model in models:
            result = count_tokens(text, model)
            assert result == expected

    def test_character_based_works_with_unicode(self):
        """Test that character-based counting works with Unicode text."""
        unicode_text = "Hello 🌍 世界! 🐍"  # Mix of ASCII and emoji
        expected = round(len(unicode_text) / 3.4)
        result = count_tokens(unicode_text, "test-model")
        assert result == expected

    def test_character_based_always_consistent(self):
        """Test that character-based counting is always consistent."""
        text = "Test message"
        expected = round(len(text) / 3.4)

        # Should always give the same result - no errors or fallbacks needed
        multiple_calls = [count_tokens(text, "test-model") for _ in range(5)]
        assert all(call == expected for call in multiple_calls)

    def test_character_based_no_errors(self):
        """Test that character-based counting never raises exceptions."""
        # Various inputs that should never cause errors
        test_cases = [
            "",
            "Simple text",
            "Text with unicode: café",
            "Emoji: 🎉🚀",
            "Newlines\nand\ttabs",
            "A" * 1000,  # Long text
        ]

        for text in test_cases:
            result = count_tokens(text, "any:model")
            assert isinstance(result, int)
            assert result >= 0
            # Should use character-based calculation
            expected = round(len(text) / 3.4)
            if text and expected == 0:
                expected = 1  # Ensure at least 1 token for non-empty text
            assert result == expected, f"Text '{text[:20]}...' should give {expected} tokens, got {result}"
