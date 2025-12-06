from unittest.mock import patch

import pytest

from gac.main import _parse_model_identifier


def test_parse_model_identifier_valid_models():
    """Test that valid model identifiers are parsed correctly."""
    # Test various valid model formats
    assert _parse_model_identifier("openai:gpt-4o-mini") == ("openai", "gpt-4o-mini")
    assert _parse_model_identifier("anthropic:claude-haiku-4-5") == ("anthropic", "claude-haiku-4-5")
    assert _parse_model_identifier("  openai:gpt-4  ") == ("openai", "gpt-4")  # Should trim whitespace


def test_parse_model_identifier_no_colon_exits():
    """Test that models without colon exit with error message."""
    with patch("gac.main.console.print") as mock_print, pytest.raises(SystemExit) as exc:
        _parse_model_identifier("invalid-model")

    assert exc.value.code == 1
    printed = " ".join(str(call) for call in mock_print.call_args_list)
    assert "Invalid model format" in printed
    assert "Expected 'provider:model'" in printed


def test_trailing_colon_model_exits_with_message():
    """Test that 'openai:' (trailing colon, empty model name) is rejected."""
    with patch("gac.main.console.print") as mock_print, pytest.raises(SystemExit) as exc:
        _parse_model_identifier("openai:")

    assert exc.value.code == 1
    printed = " ".join(str(call) for call in mock_print.call_args_list)
    assert "Invalid model format" in printed
    assert "provider and model name are required" in printed


def test_leading_colon_model_exits_with_message():
    """Test that ':gpt-4' (leading colon, empty provider) is rejected."""
    with patch("gac.main.console.print") as mock_print, pytest.raises(SystemExit) as exc:
        _parse_model_identifier(":gpt-4")

    assert exc.value.code == 1
    printed = " ".join(str(call) for call in mock_print.call_args_list)
    assert "Invalid model format" in printed
    assert "provider and model name are required" in printed
