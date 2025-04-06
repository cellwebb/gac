"""Tests for the prompt module."""

import unittest
from unittest.mock import patch

from gac.prompt import build_prompt, clean_commit_message

# fmt: off
# flake8: noqa: E501
# Sample template content for testing
TEST_TEMPLATE = """Write a concise and meaningful git commit message based on the staged changes shown below.

<format_section>
  <one_liner>
  Format it as a single line.
  </one_liner>

  <multi_line>
  Format it with a concise summary line followed by details.
  </multi_line>
</format_section>

<hint_section>
Please consider this context from the user: <hint></hint>
</hint_section>

Git status:
<git-status>
<status></status>
</git-status>

Changes to be committed:
<git-diff>
<diff></diff>
</git-diff>"""
# fmt: on


class TestPrompts:
    """Tests for the prompt module."""

    @patch("gac.prompt.load_prompt_template")
    def test_build_prompt(self, mock_load_template):
        """Test building a prompt from a template."""
        # Setup mock
        mock_load_template.return_value = TEST_TEMPLATE

        # Test with one-liner format
        result = build_prompt("status text", "diff text", one_liner=True, hint="hint text")
        assert "status text" in result
        assert "diff text" in result
        assert "hint text" in result
        assert "Format it as a single line" in result
        assert "Format it with a concise summary line" not in result

        # Test with multi-line format
        result = build_prompt("status text", "diff text", one_liner=False, hint="hint text")
        assert "status text" in result
        assert "diff text" in result
        assert "hint text" in result
        assert "Format it as a single line" not in result
        assert "Format it with a concise summary line" in result

        # Test without hint
        result = build_prompt("status text", "diff text", one_liner=False, hint="")
        assert "status text" in result
        assert "diff text" in result
        assert "Please consider this context from the user" not in result

    def test_clean_commit_message(self):
        """Test cleaning up generated commit messages."""
        # Test basic message
        message = "This is a test message"
        result = clean_commit_message(message)
        assert result == "chore: This is a test message"

        # Test message with conventional prefix
        message = "feat: Add new feature"
        result = clean_commit_message(message)
        assert result == "feat: Add new feature"

        # Test message with code block markers
        message = "```\nfeat: Add new feature\n```"
        result = clean_commit_message(message)
        assert result == "feat: Add new feature"

        # Test message with XML tags
        message = "fix: Bug fix"
        result = clean_commit_message(message)
        assert result == "fix: Bug fix"


if __name__ == "__main__":
    unittest.main()
