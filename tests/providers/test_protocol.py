"""Tests for provider protocol."""

import pytest

from gac.providers.protocol import validate_provider


def sample_provider_function(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Sample provider function for testing."""
    return "test response"


class SampleProvider:
    """Sample provider class for testing."""

    def generate(self, model: str, messages: list[dict], temperature: float, max_tokens: int, **kwargs) -> str:
        """Generate response."""
        return "test response"

    @property
    def name(self) -> str:
        """Get provider name."""
        return "sample"

    @property
    def api_key_env(self) -> str:
        """Get API key env var."""
        return "SAMPLE_KEY"

    @property
    def base_url(self) -> str:
        """Get base URL."""
        return "https://api.sample.com"

    @property
    def timeout(self) -> int:
        """Get timeout."""
        return 120


class TestProviderProtocol:
    """Test provider protocol validation."""

    def test_validate_function_provider(self):
        """Test that function-based providers are validated."""
        assert validate_provider(sample_provider_function) is True

    def test_validate_class_provider(self):
        """Test that class-based providers are validated."""
        assert validate_provider(SampleProvider()) is True

    def test_validate_invalid_function_signature(self):
        """Test that functions with invalid signatures are rejected."""

        def invalid_function():
            pass

        with pytest.raises(TypeError):
            validate_provider(invalid_function)

    def test_validate_invalid_class(self):
        """Test that classes without protocol are rejected."""

        class InvalidClass:
            pass

        with pytest.raises(TypeError):
            validate_provider(InvalidClass())

    def test_validate_partial_function_signature(self):
        """Test that functions with all required parameters pass."""

        def partial_function(model: str, messages: list[dict], temperature: float, max_tokens: int, extra: str = ""):
            pass

        assert validate_provider(partial_function) is True
