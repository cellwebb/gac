"""Utilities for standardizing AI provider tests.

This module provides common utilities and test patterns to reduce duplication
across provider test files.
"""

import os
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass

import pytest

from gac.errors import AIError


@dataclass
class ProviderTestCase:
    """Test configuration for an AI provider."""

    name: str
    module_name: str
    env_var: str | None
    function_name: str
    test_model: str
    import_function: Callable
    api_function: Callable | None = None
    error_message_pattern: str | None = None
    requires_api_key: bool = True
    has_secondary_function: bool = False
    secondary_function_name: str | None = None
    secondary_api_function: Callable | None = None


@contextmanager
def temporarily_remove_env_var(env_var: str):
    """Temporarily remove an environment variable and restore it after the test.

    Args:
        env_var: The environment variable name to remove
    """
    original_key = os.getenv(env_var)
    if original_key:
        del os.environ[env_var]

    try:
        yield
    finally:
        if original_key:
            os.environ[env_var] = original_key


@contextmanager
def temporarily_set_env_var(env_var: str, value: str):
    """Temporarily set an environment variable and restore it after the test.

    Args:
        env_var: The environment variable name to set
        value: The value to set
    """
    original_value = os.getenv(env_var)
    os.environ[env_var] = value

    try:
        yield
    finally:
        if original_value is not None:
            os.environ[env_var] = original_value
        else:
            del os.environ[env_var]


def assert_missing_api_key_error(exc_info: pytest.ExceptionInfo, provider_name: str, env_var: str):
    """Assert that the exception is a missing API key error.

    Args:
        exc_info: The pytest exception info
        provider_name: Name of the provider for error message
        env_var: Environment variable name for error message
    """
    assert exc_info.type is AIError
    assert exc_info.value.error_type == "authentication", (
        f"Expected authentication error for {provider_name}, got {exc_info.value.error_type} error"
    )


def assert_import_success(function: Callable):
    """Assert that a provider function can be imported and is callable.

    Args:
        function: The imported function to check
    """
    assert callable(function), f"Function {function} is not callable"


def create_provider_test_cases() -> list[ProviderTestCase]:
    """Create test case configurations for all providers."""
    # Import all provider functions
    from gac.providers.anthropic import call_anthropic_api
    from gac.providers.cerebras import call_cerebras_api
    from gac.providers.gemini import call_gemini_api
    from gac.providers.groq import call_groq_api
    from gac.providers.lmstudio import call_lmstudio_api
    from gac.providers.ollama import call_ollama_api
    from gac.providers.openai import call_openai_api
    from gac.providers.openrouter import call_openrouter_api
    from gac.providers.replicate import call_replicate_api
    from gac.providers.streamlake import call_streamlake_api
    from gac.providers.zai import call_zai_api, call_zai_coding_api

    return [
        ProviderTestCase(
            name="openai",
            module_name="openai",
            env_var="OPENAI_API_KEY",
            function_name="call_openai_api",
            test_model="gpt-4",
            import_function=call_openai_api,
            api_function=call_openai_api,
        ),
        ProviderTestCase(
            name="anthropic",
            module_name="anthropic",
            env_var="ANTHROPIC_API_KEY",
            function_name="call_anthropic_api",
            test_model="claude-3",
            import_function=call_anthropic_api,
            api_function=call_anthropic_api,
        ),
        ProviderTestCase(
            name="groq",
            module_name="groq",
            env_var="GROQ_API_KEY",
            function_name="call_groq_api",
            test_model="llama-3.1-70b",
            import_function=call_groq_api,
            api_function=call_groq_api,
        ),
        ProviderTestCase(
            name="cerebras",
            module_name="cerebras",
            env_var="CEREBRAS_API_KEY",
            function_name="call_cerebras_api",
            test_model="llama3.1-8b",
            import_function=call_cerebras_api,
            api_function=call_cerebras_api,
        ),
        ProviderTestCase(
            name="openrouter",
            module_name="openrouter",
            env_var="OPENROUTER_API_KEY",
            function_name="call_openrouter_api",
            test_model="mistralai/mistral-7b-instruct",
            import_function=call_openrouter_api,
            api_function=call_openrouter_api,
        ),
        ProviderTestCase(
            name="replicate",
            module_name="replicate",
            env_var="REPLICATE_API_TOKEN",
            function_name="call_replicate_api",
            test_model="openai/gpt-oss-20b",
            import_function=call_replicate_api,
            api_function=call_replicate_api,
        ),
        ProviderTestCase(
            name="streamlake",
            module_name="streamlake",
            env_var="STREAMLAKE_API_KEY",
            function_name="call_streamlake_api",
            test_model="ep-gmlysa-1760118602179985967",
            import_function=call_streamlake_api,
            api_function=call_streamlake_api,
        ),
        ProviderTestCase(
            name="gemini",
            module_name="gemini",
            env_var="GEMINI_API_KEY",
            function_name="call_gemini_api",
            test_model="gemini-1.5-pro",
            import_function=call_gemini_api,
            api_function=call_gemini_api,
        ),
        ProviderTestCase(
            name="zai",
            module_name="zai",
            env_var="ZAI_API_KEY",
            function_name="call_zai_api",
            test_model="model",
            import_function=call_zai_api,
            api_function=call_zai_api,
            has_secondary_function=True,
            secondary_function_name="call_zai_coding_api",
            secondary_api_function=call_zai_coding_api,
        ),
        ProviderTestCase(
            name="ollama",
            module_name="ollama",
            env_var="OLLAMA_API_KEY",  # Optional API key for remote Ollama
            function_name="call_ollama_api",
            test_model="llama2",
            import_function=call_ollama_api,
            api_function=call_ollama_api,
            requires_api_key=False,  # API key is optional, not required
        ),
        ProviderTestCase(
            name="lmstudio",
            module_name="lmstudio",
            env_var="LMSTUDIO_API_KEY",  # Optional API key for remote LM Studio
            function_name="call_lmstudio_api",
            test_model="model",
            import_function=call_lmstudio_api,
            api_function=call_lmstudio_api,
            requires_api_key=False,  # API key is optional, not required
        ),
    ]


def get_provider_test_cases() -> list[ProviderTestCase]:
    """Get all provider test case configurations."""
    return create_provider_test_cases()


def get_api_key_providers() -> list[ProviderTestCase]:
    """Get only providers that require API keys."""
    return [tc for tc in create_provider_test_cases() if tc.requires_api_key]


def get_local_providers() -> list[ProviderTestCase]:
    """Get only local providers (no API key required)."""
    return [tc for tc in create_provider_test_cases() if not tc.requires_api_key]
