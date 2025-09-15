"""Test module for gac.core functionality."""

from unittest.mock import patch

from gac.prompt import build_prompt


def test_build_prompt():
    """Test build_prompt function produces expected output format."""
    # Set up test inputs
    status = "On branch main"
    diff = "diff --git a/file.py b/file.py\n+New line"
    hint = "Test hint"
    one_liner = True

    # Patch count_tokens to avoid dependency on Anthropic internals
    with patch("gac.preprocess.count_tokens", return_value=42):
        system_prompt, user_prompt = build_prompt(status, diff, one_liner=one_liner, hint=hint)

    # Check expected behavior: prompts contain necessary information for the LLM
    assert isinstance(system_prompt, str)
    assert isinstance(user_prompt, str)
    assert len(system_prompt) > 0
    assert len(user_prompt) > 0

    # Verify the user prompt contains the essential components
    # These are behavioral expectations, not implementation details
    assert status in user_prompt
    assert diff in user_prompt
    assert hint in user_prompt

    # Verify one_liner flag affects the system prompt content appropriately
    if one_liner:
        assert "<one_liner>" in system_prompt
        assert "<multi_line>" not in system_prompt
    else:
        assert "<one_liner>" not in system_prompt
        assert "<multi_line>" in system_prompt


def test_build_prompt_without_hint():
    from unittest.mock import patch

    """Test build_prompt works without hint."""
    # Set up test inputs
    status = "On branch main"
    diff = "diff --git a/file.py b/file.py\n+New line"

    # Patch count_tokens to avoid dependency on Anthropic internals
    with patch("gac.preprocess.count_tokens", return_value=42):
        system_prompt, user_prompt = build_prompt(status, diff, one_liner=False)

    # Check expected behavior
    assert isinstance(system_prompt, str)
    assert isinstance(user_prompt, str)
    assert status in user_prompt
    assert diff in user_prompt
    # Check content relevant to multi-line format
    assert "<multi_line>" in system_prompt
    assert "<one_liner>" not in system_prompt
