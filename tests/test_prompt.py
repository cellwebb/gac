# flake8: noqa: E501

"""Tests for the prompt module."""

from unittest.mock import patch

from gac.postprocess import clean_commit_message
from gac.prompt import build_prompt

TEST_SYSTEM_TEMPLATE = """<role>
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

<conventions_no_scope>
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
</conventions_no_scope>

<conventions_with_scope>
You MUST start your commit message with a conventional commit prefix with scope.
</conventions_with_scope>"""

TEST_USER_TEMPLATE = """<hint>
Additional context provided by the user: <hint_text></hint_text>
</hint>

<git_status>
<status></status>
</git_status>

<git_diff_stat>
</git_diff_stat>

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

    @patch("gac.prompt.load_user_template")
    @patch("gac.prompt.load_system_template")
    def test_build_prompt(self, mock_load_system, mock_load_user):
        """Test building a prompt from a template."""
        # Setup mocks
        mock_load_system.return_value = TEST_SYSTEM_TEMPLATE
        mock_load_user.return_value = TEST_USER_TEMPLATE

        # Test with one-liner format
        system_prompt, user_prompt = build_prompt(
            "status text", processed_diff="diff text", one_liner=True, hint="hint text"
        )
        result = system_prompt + "\n" + user_prompt
        assert "status text" in result
        assert "diff text" in result
        assert "hint text" in result
        assert "Create a single-line commit message (50-72 characters if possible)." in result
        assert "Create a commit message with:" not in result

        # Test with multi-line format
        system_prompt, user_prompt = build_prompt(
            "status text", processed_diff="diff text", one_liner=False, hint="hint text"
        )
        result = system_prompt + "\n" + user_prompt
        assert "status text" in result
        assert "diff text" in result
        assert "hint text" in result
        assert "Create a single-line commit message (50-72 characters if possible)." not in result
        assert "Create a commit message with:" in result

        # Test without hint
        system_prompt, user_prompt = build_prompt("status text", processed_diff="diff text", one_liner=False, hint="")
        result = system_prompt + "\n" + user_prompt
        assert "status text" in result
        assert "diff text" in result
        assert "<hint>" not in result

    def test_build_prompt_verbose_mode(self):
        """Test building a prompt with verbose mode enabled."""
        # Test verbose mode
        system_prompt, user_prompt = build_prompt(
            "status text", processed_diff="diff text", verbose=True, hint="hint text"
        )
        result = system_prompt + "\n" + user_prompt
        assert "status text" in result
        assert "diff text" in result
        assert "hint text" in result
        # Verbose mode should include detailed sections
        assert "Motivation" in result
        assert "Architecture / Approach" in result or "Architecture/Approach" in result
        assert "Performance / Security Impact" in result or "Performance/Security Impact" in result
        assert "Affected Components" in result
        assert "Compatibility / Testing" in result or "Compatibility/Testing" in result
        # Should not include one-liner or multi-line instructions
        assert "Create a single-line commit message (50-72 characters if possible)." not in result
        assert "Create a commit message with:" not in result or "Create a comprehensive" in result

    def test_build_prompt_with_language(self):
        """Test building a prompt with custom language specified."""
        # Test with Spanish language
        system_prompt, user_prompt = build_prompt(
            "status text", processed_diff="diff text", one_liner=False, language="Spanish"
        )
        result = system_prompt + "\n" + user_prompt
        assert "status text" in result
        assert "diff text" in result
        assert "Spanish" in result
        assert "You MUST write the entire commit message in Spanish" in result
        assert "<language_name>" not in result  # Placeholder should be replaced

        # Test without language (should remove language section entirely)
        system_prompt, user_prompt = build_prompt(
            "status text", processed_diff="diff text", one_liner=False, language=None
        )
        result = system_prompt + "\n" + user_prompt
        assert "status text" in result
        assert "diff text" in result
        assert "<language>" not in result  # Entire language section should be removed
        assert "Spanish" not in result
        assert "You MUST write the entire commit message in" not in result

        # Test with different languages
        for lang in ["French", "Japanese", "German", "Portuguese"]:
            system_prompt, user_prompt = build_prompt("status text", processed_diff="diff text", language=lang)
            result = system_prompt + "\n" + user_prompt
            assert lang in result
            assert f"You MUST write the entire commit message in {lang}" in result
            assert "<language_name>" not in result  # Placeholder should be replaced

    def test_build_prompt_with_translate_prefixes(self):
        """Test building a prompt with translate_prefixes option."""
        # Test with translate_prefixes=False (default) - keeps prefixes in English
        system_prompt, user_prompt = build_prompt(
            "status text", processed_diff="diff text", language="Spanish", translate_prefixes=False
        )
        result = system_prompt + "\n" + user_prompt
        assert "Spanish" in result
        assert "should remain in English" in result
        assert "Translate the entire message including" not in result

        # Test with translate_prefixes=True - translates everything
        system_prompt, user_prompt = build_prompt(
            "status text", processed_diff="diff text", language="Spanish", translate_prefixes=True
        )
        result = system_prompt + "\n" + user_prompt
        assert "Spanish" in result
        assert "CRITICAL: You MUST translate the conventional commit prefix into Spanish" in result
        assert "DO NOT use English prefixes like 'feat:', 'fix:', 'docs:'" in result
        assert "should remain in English" not in result

        # Test with translate_prefixes=True but no language (should not affect anything)
        system_prompt, user_prompt = build_prompt(
            "status text", processed_diff="diff text", language=None, translate_prefixes=True
        )
        result = system_prompt + "\n" + user_prompt
        assert "<language>" not in result

    def test_clean_commit_message(self):
        """Test cleaning up generated commit messages."""
        # Test basic message - no automatic prefix enforcement
        message = "This is a test message"
        result = clean_commit_message(message)
        assert result == "This is a test message"

        # Test message with conventional prefix
        message = "feat: Add new feature"
        result = clean_commit_message(message)
        assert result == "feat: Add new feature"

        # Test collapse of multiple blank lines
        message = "feat: Summary\n\n\nMore details after blank lines"
        result = clean_commit_message(message)
        assert result == "feat: Summary\n\nMore details after blank lines"

        # Test collapse of blank lines containing spaces
        message = "feat: Summary\n   \n \n\nMore details with spaces"
        result = clean_commit_message(message)
        assert result == "feat: Summary\n\nMore details with spaces"

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

        # Test with <think> tags (used by some providers like MiniMax)
        message = "chore: <think>\nLet me analyze the changes carefully.\nThis appears to be a feature addition.\n</think>\n\nfeat(providers): add custom endpoint support"
        result = clean_commit_message(message)
        assert result == "feat(providers): add custom endpoint support"
        assert "<think>" not in result
        assert "</think>" not in result
        assert "analyze the changes" not in result

        # Test with uppercase <THINK> tags (case-insensitive)
        message = "fix: <THINK>Reasoning here</THINK>\n\nfix(auth): resolve session timeout bug"
        result = clean_commit_message(message)
        assert result == "fix(auth): resolve session timeout bug"
        assert "<THINK>" not in result
        assert "Reasoning here" not in result

        # Test with multiple <think> tags (should remove all pairs)
        message = "<think>First reasoning block</think>\n\nfeat(prompt): actual commit message\n\n<think>Second reasoning block</think>"
        result = clean_commit_message(message)
        assert result == "feat(prompt): actual commit message"
        assert "<think>" not in result
        assert "</think>" not in result
        assert "First reasoning block" not in result
        assert "Second reasoning block" not in result

        # Test with orphaned opening <think> tag (no closing tag)
        message = "feat(auth): add OAuth support\n\n<think>\nThis reasoning has no closing tag..."
        result = clean_commit_message(message)
        assert result == "feat(auth): add OAuth support"
        assert "<think>" not in result
        assert "reasoning has no closing" not in result

        # Test with orphaned closing </think> tag after commit message (removes tag)
        # Note: cleaning text after a valid commit is handled by double type prefix fixing and whitespace trimming
        message = "feat(api): resolve endpoint timeout</think>"
        result = clean_commit_message(message)
        assert result == "feat(api): resolve endpoint timeout"
        assert "</think>" not in result

        # Test with orphaned closing </think> tag before commit message (removes everything up to tag)
        message = "Some preamble reasoning\nabout the changes\n</think>\n\nfix(auth): correct authentication flow"
        result = clean_commit_message(message)
        assert result == "fix(auth): correct authentication flow"
        assert "</think>" not in result
        assert "preamble reasoning" not in result

        # Test that inline mentions of <think> tags are preserved (not removed)
        message = "feat(prompt): remove <think> and </think> tags from AI output\n\n- Add regex to strip reasoning blocks\n- Preserve inline mentions of the tags"
        result = clean_commit_message(message)
        assert result == message  # Should be unchanged
        assert "<think>" in result
        assert "</think>" in result
        assert "remove <think> and </think> tags" in result

    def test_clean_commit_message_no_prefix_enforcement(self):
        """Test that clean_commit_message doesn't automatically add prefixes."""
        # Test message without conventional prefix - should not add "chore:"
        message = "🎉 add dark mode support"
        result = clean_commit_message(message)
        assert result == "🎉 add dark mode support"
        assert not result.startswith("chore:")

        # Test message with conventional prefix - should preserve it
        message = "feat: add new feature"
        result = clean_commit_message(message)
        assert result == "feat: add new feature"

        # Test that other cleaning still happens
        message = "```\n♻️ refactor database layer\n```"
        result = clean_commit_message(message)
        assert result == "♻️ refactor database layer"
        assert "```" not in result

        # Test translated prefix is preserved
        message = "功能: 新增深色模式支援"
        result = clean_commit_message(message)
        assert result == "功能: 新增深色模式支援"
