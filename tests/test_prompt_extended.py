"""Extended tests for prompt.py to improve coverage."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from gac.postprocess import clean_commit_message
from gac.prompt import (
    build_prompt,
    load_custom_system_template,
    load_system_template,
)


def test_load_system_template_with_custom_path():
    """Test loading a custom system template from a specified path."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Custom system template content")
        custom_path = f.name

    try:
        result = load_system_template(custom_path=custom_path)
        assert result == "Custom system template content"
    finally:
        Path(custom_path).unlink()


def test_load_custom_system_template_success():
    """Test successfully loading a custom system template."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Test custom template")
        template_path = f.name

    try:
        result = load_custom_system_template(template_path)
        assert result == "Test custom template"
    finally:
        Path(template_path).unlink()


def test_load_custom_system_template_file_not_found():
    """Test that FileNotFoundError is raised when template file doesn't exist."""
    with pytest.raises(FileNotFoundError):
        load_custom_system_template("/nonexistent/path/template.txt")


def test_load_custom_system_template_permission_error():
    """Test that OSError is raised when there's a read error."""
    # Create a file and then make it unreadable
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        template_path = f.name

    try:
        Path(template_path).chmod(0o000)  # Remove all permissions
        with pytest.raises(OSError):
            load_custom_system_template(template_path)
    finally:
        # Restore permissions and clean up
        Path(template_path).chmod(0o644)
        Path(template_path).unlink()


def test_build_prompt_with_verbose_and_scope():
    """Test building prompt with verbose and scope options together."""
    system_prompt, user_prompt = build_prompt(
        status="M  test.py",
        processed_diff="diff content",
        verbose=True,
        infer_scope=True,
    )

    combined = system_prompt + user_prompt

    # Verbose format should be present
    assert "Motivation" in combined or "Technical Approach" in combined or "MOTIVATION" in combined

    # Scope instructions should be present
    assert "scope" in combined.lower()


def test_build_prompt_exception_handling_in_scope_processing():
    """Test that scope parameter processing handles exceptions gracefully."""
    # Mock the template loading to return a template that will cause issues
    with patch("gac.prompt.load_system_template") as mock_sys, patch("gac.prompt.load_user_template") as mock_user:
        # Set up templates with expected sections
        mock_sys.return_value = """
<conventions_with_scope>With scope</conventions_with_scope>
<conventions_no_scope>No scope</conventions_no_scope>
"""
        mock_user.return_value = "<status></status><diff></diff>"

        # This should handle any exceptions gracefully
        system_prompt, user_prompt = build_prompt(
            status="test",
            processed_diff="test diff",
            infer_scope=True,
        )

        # Should still return valid prompts
        assert system_prompt is not None
        assert user_prompt is not None


def test_clean_commit_message_removes_xml_tags():
    """Test that clean_commit_message removes XML tags."""
    message = "feat: add feature<git-status>status info</git-status>"
    cleaned = clean_commit_message(message)

    # Should remove git-status tags
    assert "<git-status>" not in cleaned
    assert "</git-status>" not in cleaned
    assert "feat: add feature" in cleaned
    assert "status info" in cleaned


def test_clean_commit_message_fixes_double_prefix():
    """Test that clean_commit_message fixes double prefix issues."""
    message = "chore: feat(auth): add login"
    cleaned = clean_commit_message(message)

    # Should fix to single prefix
    assert cleaned.startswith("feat(auth):")
    assert "chore:" not in cleaned


def test_clean_commit_message_preserves_valid_messages():
    """Test that valid commit messages are preserved."""
    valid_messages = [
        "feat: add new feature",
        "fix: resolve bug",
        "docs: update documentation",
    ]

    for message in valid_messages:
        cleaned = clean_commit_message(message)
        assert cleaned == message


def test_build_prompt_with_diff_stat():
    """Test building prompt with diff_stat parameter."""
    diff_stat = " file1.py | 10 ++++------\n file2.py | 5 ++---\n 2 files changed, 6 insertions(+), 9 deletions(-)"

    system_prompt, user_prompt = build_prompt(
        status="M  file1.py\nM  file2.py",
        processed_diff="diff content",
        diff_stat=diff_stat,
    )

    # Diff stat should be included in the prompt
    assert diff_stat in user_prompt
