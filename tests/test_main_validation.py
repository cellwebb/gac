import pytest

from gac.errors import ConfigError
from gac.model_identifier import ModelIdentifier


def test_parse_model_identifier_valid_models():
    """Test that valid model identifiers are parsed correctly."""
    result = ModelIdentifier.parse("openai:gpt-4o-mini")
    assert result.provider == "openai"
    assert result.model_name == "gpt-4o-mini"

    result = ModelIdentifier.parse("anthropic:claude-haiku-4-5")
    assert result.provider == "anthropic"
    assert result.model_name == "claude-haiku-4-5"

    result = ModelIdentifier.parse("  openai:gpt-4  ")
    assert result.provider == "openai"
    assert result.model_name == "gpt-4"


def test_parse_model_identifier_no_colon_raises():
    """Test that models without colon raise ConfigError."""
    with pytest.raises(ConfigError) as exc:
        ModelIdentifier.parse("invalid-model")

    assert "Invalid model format" in str(exc.value)
    assert "Expected 'provider:model'" in str(exc.value)


def test_trailing_colon_model_raises():
    """Test that 'openai:' (trailing colon, empty model name) is rejected."""
    with pytest.raises(ConfigError) as exc:
        ModelIdentifier.parse("openai:")

    assert "Invalid model format" in str(exc.value)
    assert "provider and model name" in str(exc.value)


def test_leading_colon_model_raises():
    """Test that ':gpt-4' (leading colon, empty provider) is rejected."""
    with pytest.raises(ConfigError) as exc:
        ModelIdentifier.parse(":gpt-4")

    assert "Invalid model format" in str(exc.value)
    assert "provider and model name" in str(exc.value)


def test_model_identifier_str():
    """Test string representation of ModelIdentifier."""
    model_id = ModelIdentifier.parse("openai:gpt-4o-mini")
    assert str(model_id) == "openai:gpt-4o-mini"


def test_model_identifier_is_immutable():
    """Test that ModelIdentifier is immutable (frozen dataclass)."""
    model_id = ModelIdentifier.parse("openai:gpt-4o-mini")
    with pytest.raises(AttributeError):
        model_id.provider = "anthropic"  # type: ignore[misc]


def test_model_identifier_starts_with_provider():
    """Test the starts_with_provider helper method."""
    model_id = ModelIdentifier.parse("claude-code:claude-3-opus")
    assert model_id.starts_with_provider("claude-code") is True
    assert model_id.starts_with_provider("openai") is False

    model_id = ModelIdentifier.parse("qwen:qwen-max")
    assert model_id.starts_with_provider("qwen") is True
    assert model_id.starts_with_provider("claude-code") is False
