# flake8: noqa: E501

"""Tests for the prompt module."""

import unittest
from unittest.mock import patch

from gac.prompt import build_prompt, clean_commit_message

TEST_TEMPLATE = """<role>
You are an expert git commit message generator. Your task is to analyze code changes and create a concise, meaningful git commit message. You will receive git status and diff information. Your entire response will be used directly as a git commit message.
</role>

<format>
  <one_liner>
  Create a single-line commit message (50-72 characters if possible).
  Your message should be clear, concise, and descriptive of the core change.
  Use present tense ("Add feature" not "Added feature").
  </one_liner>
  <multi_line>
  Create a commit message with:
  - First line: A concise summary (50-72 characters) that could stand alone
  - Blank line after the summary
  - Detailed body with multiple bullet points explaining the key changes
  - Focus on WHY changes were made, not just WHAT was changed
  - Order points from most important to least important
  </multi_line>
</format>

<conventions>
You MUST start your commit message with the most appropriate conventional commit prefix:
- feat: A new feature or functionality addition
- fix: A bug fix or error correction
- docs: Documentation changes only
- style: Changes to code style/formatting without logic changes
- refactor: Code restructuring without behavior changes
- perf: Performance improvements
- test: Adding/modifying tests
- build: Changes to build system/dependencies
- ci: Changes to CI configuration
- chore: Miscellaneous changes not affecting src/test files

Select the prefix that best matches the primary purpose of the changes.
If multiple prefixes apply, choose the one that represents the most significant change.
If you cannot confidently determine a type, use 'chore'.
</conventions>

<hint>
Additional context provided by the user: <hint_text></hint_text>
</hint>

<git_status>
<status></status>
</git_status>

<repository_context>
</repository_context>

<git_diff>
<diff></diff>
</git_diff>

<instructions>
IMMEDIATELY AFTER ANALYZING THE CHANGES, RESPOND WITH ONLY THE COMMIT MESSAGE.
DO NOT include any preamble, reasoning, explanations or anything other than the commit message itself.
DO NOT use markdown formatting, headers, or code blocks.
The entire response will be passed directly to 'git commit -m'.
</instructions>"""


class TestPrompts:
    """Tests for the prompt module."""

    @patch("gac.prompt.load_prompt_template")
    @patch("gac.preprocess.count_tokens", return_value=42)
    def test_build_prompt(self, mock_count_tokens, mock_load_template):
        """Test building a prompt from a template."""
        # Setup mock
        mock_load_template.return_value = TEST_TEMPLATE

        # Test with one-liner format
        result = build_prompt("status text", "diff text", one_liner=True, hint="hint text")
        assert "status text" in result
        assert "diff text" in result
        assert "hint text" in result
        assert "Create a single-line commit message (50-72 characters if possible)." in result
        assert "Create a commit message with:" not in result

        # Test with multi-line format
        result = build_prompt("status text", "diff text", one_liner=False, hint="hint text")
        assert "status text" in result
        assert "diff text" in result
        assert "hint text" in result
        assert "Create a single-line commit message (50-72 characters if possible)." not in result
        assert "Create a commit message with:" in result

        # Test without hint
        result = build_prompt("status text", "diff text", one_liner=False, hint="")
        assert "status text" in result
        assert "diff text" in result
        assert "<hint>" not in result

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

    def test_clean_commit_message_with_reasoning(self):
        """Test cleaning messages that include reasoning section."""
        # Test with reasoning and commit message marker
        message = "Let me analyze the changes.\n\n1. First change: Modified the API\n2. Second change: Added tests\n\n# Your commit message:\nfeat: Update API and add tests"
        result = clean_commit_message(message)
        assert result == "feat: Update API and add tests"

        # Test with different commit indicator
        message = "The changes modify the authentication flow.\n\nThe commit message is:\nfix: Resolve authentication bug in login flow"
        result = clean_commit_message(message)
        assert result == "fix: Resolve authentication bug in login flow"

        # Test with headers and reasoning steps
        message = "# Analysis\n\n1. This change adds a new feature\n2. It also includes tests\n\n# Commit Message\n\nfeat: Add user profile export feature"
        result = clean_commit_message(message)
        assert result == "feat: Add user profile export feature"

        # Test with CoT thinking but no indicator
        message = (
            "I'm analyzing the changes.\nThese changes refactor the code.\nrefactor: Simplify authentication logic"
        )
        result = clean_commit_message(message)
        assert result == "refactor: Simplify authentication logic"


if __name__ == "__main__":
    unittest.main()
