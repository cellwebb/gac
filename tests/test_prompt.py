"""Tests for the prompt module."""

import unittest
from unittest.mock import patch

from gac.prompt import add_repository_context, build_prompt, clean_commit_message

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

    def test_clean_commit_message_advanced(self):
        """Test cleaning up complex commit messages."""
        # Test with markdown code block - should remove language specifier
        message = "```markdown\nfeat: Add new API endpoint\n```"
        result = clean_commit_message(message)
        assert result == "feat: Add new API endpoint"

        # Test with multiple backtick blocks
        message = "```\nrefactor: Clean up code\n```\n\n```\nMore details\n```"
        result = clean_commit_message(message)
        assert result == "refactor: Clean up code\n\nMore details"

        # Test with XML tags in content
        message = "<git-diff>feat: Update authentication flow</git-diff>"
        result = clean_commit_message(message)
        assert result == "feat: Update authentication flow"

        # Test with leading/trailing whitespace
        message = "\n\n  docs: Update README  \n\n"
        result = clean_commit_message(message)
        assert result == "docs: Update README"

        # Test with multiple conventional prefixes
        message = "chore: feat: Add new component"
        result = clean_commit_message(message)
        assert result == "chore: feat: Add new component"

    @patch("gac.prompt.run_git_command")
    def test_add_repository_context(self, mock_run_git_command):
        """Test repository context extraction and formatting."""
        # Configure the mock to return test data
        mock_responses = {
            # Mock response for docstring extraction
            (
                "show",
                "HEAD:src/example.py",
            ): '"""Example module.\n\nDetailed description here.\n"""\ndef example_function():\n    pass',
            # Mock response for recent commits
            (
                "log",
                "--pretty=format:%h %s",
                "-n",
                "3",
                "--",
                "src/example.py",
            ): "abc123 Fix bug in example\ndef456 Add new feature\nghi789 Initial commit",
            # Mock response for remote URL
            ("config", "--get", "remote.origin.url"): "https://github.com/user/repo.git",
            # Mock response for branch name
            ("rev-parse", "--abbrev-ref", "HEAD"): "main",
            # Mock response for directory listing
            ("ls-tree", "--name-only", "HEAD", "src"): "example.py\nconfig.py\nutils.py",
        }

        def side_effect(args, **kwargs):
            # Create a tuple of the command arguments to match against our mock_responses
            cmd_key = tuple(args)
            if cmd_key in mock_responses:
                return mock_responses[cmd_key]
            return ""

        mock_run_git_command.side_effect = side_effect

        # Test diff containing one Python file
        diff = "diff --git a/src/example.py b/src/example.py\n@@ -1,5 +1,7 @@\n+def new_function():\n+    return True\n def example_function():\n     pass"

        result = add_repository_context(diff)

        # Verify the repository context contains all expected sections
        assert "Repository Context:" in result
        assert "File purposes:" in result
        assert "• src/example.py: Example module." in result
        assert "Recent related commits:" in result
        assert "• abc123 Fix bug in example" in result
        assert "Repository: repo" in result
        assert "Branch: main" in result
        assert "Directory context (src):" in result
        assert "• example.py" in result

    @patch("gac.prompt.add_repository_context")
    @patch("gac.prompt.load_prompt_template")
    @patch("gac.prompt.preprocess_diff")
    def test_build_prompt_with_repo_context(self, mock_preprocess, mock_load_template, mock_add_context):
        """Test that repository context is included in the prompt."""
        # Setup mocks
        mock_load_template.return_value = TEST_TEMPLATE
        mock_preprocess.return_value = "processed diff"
        mock_add_context.return_value = "Repository Context:\nSample context data"

        # Test with repository context
        result = build_prompt("status text", "diff text", one_liner=False)

        # Verify the context is included in the prompt
        assert "Repository Context:" in result
        assert "Sample context data" in result
        assert mock_add_context.called

        # Verify context is placed before the diff
        context_pos = result.find("Repository Context:")
        diff_pos = result.find("processed diff")
        assert context_pos < diff_pos, "Repository context should appear before the diff"


if __name__ == "__main__":
    unittest.main()
