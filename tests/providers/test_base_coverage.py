"""Tests to close coverage gaps in base provider classes.

Targeting uncovered lines:
- Line 77: api_key property with empty api_key_env
- Lines 249-251: _build_headers with no api_key (OpenAI-compatible)
- Line 257: _parse_response with empty content string
- Lines 260, 262, 268-275: _parse_response usage details and reasoning tokens
- Lines 303-305: Anthropic _get_api_url with trailing / and ending in "messages"
- Lines 332, 336, 338, 343-346: Anthropic _parse_response edge cases
- Line 357: GenericHTTPProvider choices with falsy content
- Lines 366-373: GenericHTTPProvider ollama-style and fallback paths
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from gac.errors import AIError
from gac.providers.base import (
    AnthropicCompatibleProvider,
    BaseConfiguredProvider,
    GenericHTTPProvider,
    OpenAICompatibleProvider,
    ParsedResponse,
    ProviderConfig,
    _normalize_completion_tokens,
)

# ── Concrete test providers ──────────────────────────────────────────


class _OpenAI(OpenAICompatibleProvider):
    config = ProviderConfig(
        name="TestOpenAI",
        api_key_env="TEST_OPENAI_KEY",
        base_url="https://api.test.com/v1/chat/completions",
    )


class _Anthropic(AnthropicCompatibleProvider):
    config = ProviderConfig(
        name="TestAnthropic",
        api_key_env="TEST_ANTHROPIC_KEY",
        base_url="https://api.test.com/v1",
    )


class _NoKeyProvider(BaseConfiguredProvider):
    """Provider with empty api_key_env — should return empty string for api_key."""

    config = ProviderConfig(name="NoKey", api_key_env="", base_url="https://api.test.com")

    def _build_request_body(self, messages, temperature, max_tokens, model, **kwargs):
        return {}

    def _parse_response(self, response):
        return ParsedResponse(content="ok")


# ── Line 77: api_key property with empty api_key_env ──────────────────


class TestApiKeyPropertyEmptyEnv:
    """Test api_key property when api_key_env is empty string."""

    def test_api_key_returns_empty_string_when_env_is_empty(self):
        """When api_key_env is '', the property should return '' without calling _get_api_key."""
        provider = _NoKeyProvider(_NoKeyProvider.config)
        assert provider.api_key == ""


# ── Lines 249-251: OpenAI _build_headers when api_key is empty ───────


class TestOpenAIBuildHeadersNoKey:
    """Test OpenAI-compatible _build_headers when api_key is empty/falsy."""

    def test_no_auth_header_when_api_key_empty(self):
        """When api_key is empty string, Authorization header should NOT be added."""
        provider = _OpenAI(
            ProviderConfig(
                name="TestOpenAI",
                api_key_env="",  # empty env
                base_url="https://api.test.com/v1/chat/completions",
            )
        )
        headers = provider._build_headers()
        assert "Authorization" not in headers

    def test_auth_header_present_when_key_set(self):
        """When api_key is available, Authorization header should be present."""
        provider = _OpenAI(_OpenAI.config)
        with patch.dict(os.environ, {"TEST_OPENAI_KEY": "sk-test123"}):
            headers = provider._build_headers()
            assert headers["Authorization"] == "Bearer sk-test123"


# ── Line 257: _parse_response empty content string ──────────────────


class TestOpenAIParseResponseNullContent:
    """Test OpenAI _parse_response with null and empty string content."""

    def test_missing_choices_raises(self):
        """Response without 'choices' should raise AIError."""
        provider = _OpenAI(_OpenAI.config)
        response = {"data": "nope"}
        with pytest.raises(AIError, match="missing choices"):
            provider._parse_response(response)

    def test_choices_not_list_raises(self):
        """Response where choices is not a list should raise AIError."""
        provider = _OpenAI(_OpenAI.config)
        response = {"choices": "not a list"}
        with pytest.raises(AIError, match="missing choices"):
            provider._parse_response(response)

    def test_null_content_raises_model_error(self):
        """Null content should raise AIError."""
        provider = _OpenAI(_OpenAI.config)
        response = {"choices": [{"message": {"content": None}}]}
        with pytest.raises(AIError, match="null content"):
            provider._parse_response(response)

    def test_empty_string_content_raises_model_error(self):
        """Empty string content should raise AIError."""
        provider = _OpenAI(_OpenAI.config)
        response = {"choices": [{"message": {"content": ""}}]}
        with pytest.raises(AIError, match="empty content"):
            provider._parse_response(response)


# ── Lines 260, 262, 268-275: usage details and reasoning tokens ─────


class TestOpenAIParseResponseUsageDetails:
    """Test OpenAI _parse_response with various usage details."""

    def test_usage_with_reasoning_tokens(self):
        """Usage with completion_tokens_details containing reasoning_tokens."""
        provider = _OpenAI(_OpenAI.config)
        response = {
            "choices": [{"message": {"content": "hello"}}],
            "usage": {
                "prompt_tokens": 50,
                "completion_tokens": 100,
                "completion_tokens_details": {"reasoning_tokens": 30},
            },
        }
        parsed = provider._parse_response(response)
        assert parsed.prompt_tokens == 50
        # completion_tokens should be 100 - 30 = 70 (reasoning subtracted)
        assert parsed.completion_tokens == 70
        assert parsed.reasoning_tokens == 30

    def test_usage_with_non_int_prompt_tokens(self):
        """Non-integer prompt_tokens should default to -1."""
        provider = _OpenAI(_OpenAI.config)
        response = {
            "choices": [{"message": {"content": "hello"}}],
            "usage": {"prompt_tokens": "many", "completion_tokens": 50},
        }
        parsed = provider._parse_response(response)
        assert parsed.prompt_tokens == -1

    def test_usage_with_non_int_completion_tokens(self):
        """Non-integer completion_tokens should default to -1."""
        provider = _OpenAI(_OpenAI.config)
        response = {
            "choices": [{"message": {"content": "hello"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": "lots"},
        }
        parsed = provider._parse_response(response)
        assert parsed.completion_tokens == -1

    def test_usage_details_with_non_int_reasoning_tokens(self):
        """Non-integer reasoning_tokens should default to 0."""
        provider = _OpenAI(_OpenAI.config)
        response = {
            "choices": [{"message": {"content": "hello"}}],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 50,
                "completion_tokens_details": {"reasoning_tokens": "many"},
            },
        }
        parsed = provider._parse_response(response)
        assert parsed.reasoning_tokens == 0
        assert parsed.completion_tokens == 50  # 50 - 0 = 50

    def test_no_usage_dict(self):
        """Missing usage dict should return -1 for tokens."""
        provider = _OpenAI(_OpenAI.config)
        response = {"choices": [{"message": {"content": "hello"}}]}
        parsed = provider._parse_response(response)
        assert parsed.prompt_tokens == -1
        assert parsed.completion_tokens == -1
        assert parsed.reasoning_tokens == 0

    def test_usage_with_reasoning_tokens_exceeds_completion(self):
        """When reasoning > completion, the API already excluded reasoning from
        completion_tokens, so we should NOT subtract.  Keep completion_tokens
        as-is (5, not 0)."""
        provider = _OpenAI(_OpenAI.config)
        response = {
            "choices": [{"message": {"content": "think"}}],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "completion_tokens_details": {"reasoning_tokens": 10},
            },
        }
        parsed = provider._parse_response(response)
        # 5 < 10 → API already excluded reasoning, keep 5 as-is
        assert parsed.completion_tokens == 5
        assert parsed.reasoning_tokens == 10


# ── Lines 303-305: Anthropic _get_api_url edge cases ─────────────────


class TestAnthropicGetApiUrl:
    """Test Anthropic _get_api_url with different base_url formats."""

    def test_base_url_already_ends_with_messages(self):
        """base_url ending in 'messages' should be returned as-is."""
        config = ProviderConfig(
            name="TestAnthropic",
            api_key_env="TEST_ANTHROPIC_KEY",
            base_url="https://api.test.com/v1/messages",
        )
        provider = _Anthropic(config)
        assert provider._get_api_url() == "https://api.test.com/v1/messages"

    def test_base_url_ends_with_slash(self):
        """base_url ending in '/' should append 'messages'."""
        config = ProviderConfig(
            name="TestAnthropic",
            api_key_env="TEST_ANTHROPIC_KEY",
            base_url="https://api.test.com/v1/",
        )
        provider = _Anthropic(config)
        assert provider._get_api_url() == "https://api.test.com/v1/messages"

    def test_base_url_without_trailing_slash(self):
        """base_url without trailing slash should append '/messages'."""
        config = ProviderConfig(
            name="TestAnthropic",
            api_key_env="TEST_ANTHROPIC_KEY",
            base_url="https://api.test.com/v1",
        )
        provider = _Anthropic(config)
        assert provider._get_api_url() == "https://api.test.com/v1/messages"


# ── Lines 332, 336, 338, 343-346: Anthropic _parse_response edge cases ──


class TestAnthropicParseResponseEdgeCases:
    """Test Anthropic _parse_response edge cases."""

    def test_null_text_content_raises(self):
        """Null text content should raise AIError."""
        provider = _Anthropic(_Anthropic.config)
        response = {"content": [{"text": None}]}
        with pytest.raises(AIError, match="null content"):
            provider._parse_response(response)

    def test_empty_string_text_content_raises(self):
        """Empty string text content should raise AIError."""
        provider = _Anthropic(_Anthropic.config)
        response = {"content": [{"text": ""}]}
        with pytest.raises(AIError, match="empty content"):
            provider._parse_response(response)

    def test_usage_non_int_input_tokens(self):
        """Non-integer input_tokens should default to -1."""
        provider = _Anthropic(_Anthropic.config)
        response = {
            "content": [{"text": "hello"}],
            "usage": {"input_tokens": "lots", "output_tokens": 50},
        }
        parsed = provider._parse_response(response)
        assert parsed.prompt_tokens == -1

    def test_usage_non_int_output_tokens(self):
        """Non-integer output_tokens should default to -1."""
        provider = _Anthropic(_Anthropic.config)
        response = {
            "content": [{"text": "hello"}],
            "usage": {"input_tokens": 10, "output_tokens": "lots"},
        }
        parsed = provider._parse_response(response)
        assert parsed.completion_tokens == -1

    def test_no_usage_returns_negative_tokens(self):
        """Missing usage dict should return -1 for both tokens."""
        provider = _Anthropic(_Anthropic.config)
        response = {"content": [{"text": "hello"}]}
        parsed = provider._parse_response(response)
        assert parsed.prompt_tokens == -1
        assert parsed.completion_tokens == -1

    def test_missing_content_key_raises(self):
        """Response without 'content' key should raise AIError."""
        provider = _Anthropic(_Anthropic.config)
        response = {"data": "something"}
        with pytest.raises(AIError, match="missing content"):
            provider._parse_response(response)

    def test_content_not_list_raises(self):
        """Response where content is a string (not list) should raise AIError."""
        provider = _Anthropic(_Anthropic.config)
        response = {"content": "not a list"}
        with pytest.raises(AIError, match="missing content"):
            provider._parse_response(response)

    def test_content_empty_list_raises(self):
        """Response where content is empty list should raise AIError."""
        provider = _Anthropic(_Anthropic.config)
        response = {"content": []}
        with pytest.raises(AIError, match="missing content"):
            provider._parse_response(response)


class TestGenericHTTPEmptyChoicesContent:
    """Test GenericHTTPProvider with choices but falsy content."""

    def test_choices_with_none_content_falls_through(self):
        """Choices entry with None content should fall through to next format."""
        provider = GenericHTTPProvider(ProviderConfig(name="Gen", api_key_env="KEY", base_url="http://test.url"))
        response = {"choices": [{"message": {"content": None}}], "message": {"content": "fallback"}}
        parsed = provider._parse_response(response)
        assert parsed.content == "fallback"

    def test_choices_with_empty_content_falls_through(self):
        """Choices entry with empty string content should fall through."""
        provider = GenericHTTPProvider(ProviderConfig(name="Gen", api_key_env="KEY", base_url="http://test.url"))
        response = {"choices": [{"message": {"content": ""}}], "content": [{"text": "anthropic fallback"}]}
        parsed = provider._parse_response(response)
        assert parsed.content == "anthropic fallback"


# ── Lines 366-373: GenericHTTP ollama-style and fallback ────────────


class TestGenericHTTPExtended:
    """Test GenericHTTPProvider ollama-style responses and fallback paths."""

    def test_ollama_style_with_token_counts(self):
        """Ollama-style response with prompt_eval_count and eval_count."""
        provider = GenericHTTPProvider(ProviderConfig(name="Gen", api_key_env="KEY", base_url="http://test.url"))
        response = {
            "message": {"content": "ollama says hi"},
            "prompt_eval_count": 42,
            "eval_count": 13,
        }
        parsed = provider._parse_response(response)
        assert parsed.content == "ollama says hi"
        assert parsed.prompt_tokens == 42
        assert parsed.completion_tokens == 13

    def test_ollama_style_with_non_int_token_counts(self):
        """Ollama-style response with non-integer token counts should default to -1."""
        provider = GenericHTTPProvider(ProviderConfig(name="Gen", api_key_env="KEY", base_url="http://test.url"))
        response = {
            "message": {"content": "ollama says hi"},
            "prompt_eval_count": "many",
            "eval_count": "few",
        }
        parsed = provider._parse_response(response)
        assert parsed.content == "ollama says hi"
        assert parsed.prompt_tokens == -1
        assert parsed.completion_tokens == -1

    def test_fallback_long_string_value(self):
        """Response with a long string value as fallback."""
        provider = GenericHTTPProvider(ProviderConfig(name="Gen", api_key_env="KEY", base_url="http://test.url"))
        response = {"result": "this is a really long string that should be picked up as a fallback response"}
        parsed = provider._parse_response(response)
        assert "long string" in parsed.content

    def test_usage_with_reasoning_tokens_normalization(self):
        """GenericHTTP usage with reasoning_tokens should normalize completion_tokens."""
        provider = GenericHTTPProvider(ProviderConfig(name="Gen", api_key_env="KEY", base_url="http://test.url"))
        response = {
            "choices": [{"message": {"content": "reasoned response"}}],
            "usage": {
                "prompt_tokens": 20,
                "completion_tokens": 80,
                "completion_tokens_details": {"reasoning_tokens": 20},
            },
        }
        parsed = provider._parse_response(response)
        # 80 - 20 = 60 (OpenAI convention: completion includes reasoning)
        assert parsed.completion_tokens == 60
        assert parsed.reasoning_tokens == 20

    def test_usage_with_input_tokens_fallback(self):
        """GenericHTTP usage with input_tokens instead of prompt_tokens."""
        provider = GenericHTTPProvider(ProviderConfig(name="Gen", api_key_env="KEY", base_url="http://test.url"))
        response = {
            "choices": [{"message": {"content": "anthropic style"}}],
            "usage": {"input_tokens": 15, "output_tokens": 35},
        }
        parsed = provider._parse_response(response)
        assert parsed.prompt_tokens == 15
        assert parsed.completion_tokens == 35


# ── _normalize_completion_tokens helper ──────────────────────────────


class TestNormalizeCompletionTokens:
    """Test the _normalize_completion_tokens helper that fixes the Crof.ai
    GLM bug where completion_tokens already excludes reasoning."""

    def test_openai_convention_subtracts_reasoning(self):
        """When completion >= reasoning (OpenAI convention), subtract reasoning."""
        assert _normalize_completion_tokens(100, 30) == 70

    def test_openai_convention_exact_equal(self):
        """When completion == reasoning, result is 0 (all output was reasoning)."""
        assert _normalize_completion_tokens(30, 30) == 0

    def test_crof_glm_convention_no_subtract(self):
        """When completion < reasoning, API already excluded reasoning — don't subtract."""
        assert _normalize_completion_tokens(81, 559) == 81

    def test_zero_reasoning_no_subtract(self):
        """When reasoning_tokens is 0, no subtraction needed."""
        assert _normalize_completion_tokens(100, 0) == 100

    def test_negative_reasoning_no_subtract(self):
        """When reasoning_tokens is negative (shouldn't happen), no subtraction."""
        assert _normalize_completion_tokens(100, -1) == 100

    def test_negative_completion_passthrough(self):
        """When completion_tokens is -1 (unknown), pass through as-is."""
        assert _normalize_completion_tokens(-1, 30) == -1

    def test_zero_completion_with_reasoning(self):
        """When completion is 0 and reasoning > 0, keep 0 (API already excluded)."""
        assert _normalize_completion_tokens(0, 559) == 0

    def test_zero_completion_zero_reasoning(self):
        """Both zero: keep 0."""
        assert _normalize_completion_tokens(0, 0) == 0


# ── Lines 214-217: generate() with model not in body ────────────────


class TestGenerateModelInjection:
    """Test that generate() injects model into body when not present."""

    def test_model_injected_when_missing_from_body(self):
        """When _build_request_body doesn't include 'model', generate should add it."""
        provider = _OpenAI(_OpenAI.config)
        with (
            patch("gac.providers.base.httpx.post") as mock_post,
            patch.dict(os.environ, {"TEST_OPENAI_KEY": "sk-test"}),
        ):
            mock_post.return_value.json.return_value = {
                "choices": [{"message": {"content": "test"}}],
                "usage": {"prompt_tokens": 5, "completion_tokens": 10},
            }
            mock_post.return_value.raise_for_status = MagicMock()

            provider.generate(
                model="gpt-4o",
                messages=[{"role": "user", "content": "hi"}],
                temperature=0.7,
                max_tokens=100,
            )

            call_kwargs = mock_post.call_args[1]
            body = call_kwargs["json"]
            assert body["model"] == "gpt-4o"

    def test_model_preserved_when_already_in_body(self):
        """When _build_request_body includes 'model', generate should not overwrite."""

        # Use a custom provider that puts model in body
        class ModelInBody(OpenAICompatibleProvider):
            config = ProviderConfig(
                name="ModelInBody",
                api_key_env="TEST_KEY_MIB",
                base_url="https://api.test.com/v1/chat/completions",
            )

            def _build_request_body(self, messages, temperature, max_tokens, model, **kwargs):
                return {
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "model": "custom-model",
                }

        provider = ModelInBody(ModelInBody.config)
        with (
            patch("gac.providers.base.httpx.post") as mock_post,
            patch.dict(os.environ, {"TEST_KEY_MIB": "sk-test"}),
        ):
            mock_post.return_value.json.return_value = {
                "choices": [{"message": {"content": "test"}}],
                "usage": {"prompt_tokens": 5, "completion_tokens": 10},
            }
            mock_post.return_value.raise_for_status = MagicMock()

            provider.generate(
                model="gpt-4o",
                messages=[{"role": "user", "content": "hi"}],
                temperature=0.7,
                max_tokens=100,
            )

            call_kwargs = mock_post.call_args[1]
            body = call_kwargs["json"]
            # Should keep the model from _build_request_body, not overwrite
            assert body["model"] == "custom-model"


# ── Token estimation fallback in generate() ──────────────────────────


class TestGenericHTTPBuildRequestBody:
    """Test GenericHTTPProvider._build_request_body is covered."""

    def test_build_request_body_returns_standard_format(self):
        """GenericHTTPProvider should build a standard request body."""
        provider = GenericHTTPProvider(ProviderConfig(name="Gen", api_key_env="KEY", base_url="http://test.url"))
        messages = [{"role": "user", "content": "hello"}]
        body = provider._build_request_body(messages, 0.7, 100, "test-model", extra_key="extra_val")
        assert body["messages"] == messages
        assert body["temperature"] == 0.7
        assert body["max_tokens"] == 100
        assert body["extra_key"] == "extra_val"


class TestGenerateTokenEstimationFallback:
    """Test that generate() falls back to count_tokens when usage is -1."""

    def test_fallback_to_count_tokens_for_prompt_tokens(self):
        """When parsed.prompt_tokens is -1, should call count_tokens for estimation."""
        provider = _OpenAI(_OpenAI.config)
        with (
            patch("gac.providers.base.httpx.post") as mock_post,
            patch("gac.providers.base.count_tokens") as mock_count,
            patch.dict(os.environ, {"TEST_OPENAI_KEY": "sk-test"}),
        ):
            mock_post.return_value.json.return_value = {
                "choices": [{"message": {"content": "hello world"}}],
                # No usage dict -> prompt_tokens = -1, completion_tokens = -1
            }
            mock_post.return_value.raise_for_status = MagicMock()
            mock_count.return_value = 42

            result = provider.generate(
                model="gpt-4o",
                messages=[{"role": "user", "content": "hi"}],
                temperature=0.7,
                max_tokens=100,
            )

            # count_tokens should have been called for both prompt and completion estimation
            assert mock_count.call_count == 2
            content, prompt_tokens, completion_tokens, duration_ms, reasoning_tokens = result
            assert prompt_tokens == 42
            assert completion_tokens == 42
