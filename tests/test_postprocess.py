"""Tests for postprocess module."""

from gac.postprocess import (
    _truncate_at_word_boundary,
    clean_commit_message,
    enforce_fifty_seventy_two,
)


class TestTruncateAtWordBoundary:
    """Tests for the _truncate_at_word_boundary helper function."""

    def test_no_truncation_needed(self):
        """Test that short text is returned unchanged."""
        result = _truncate_at_word_boundary("hello", 10)
        assert result == "hello"

    def test_exact_fit_no_truncation(self):
        """Test that text exactly fitting max_len is returned unchanged."""
        result = _truncate_at_word_boundary("hello world", 11)
        assert result == "hello world"

    def test_truncation_at_word_boundary(self):
        """Test truncation finds word boundary."""
        result = _truncate_at_word_boundary("this is a very long sentence that needs truncation", 20)
        assert result == "this is a very..."
        assert len(result) <= 20

    def test_truncation_respects_spaces(self):
        """Test that truncation respects word boundaries (spaces)."""
        result = _truncate_at_word_boundary("one two three four five", 15)
        # With max_len=15 and suffix="..." (3 chars), available=12
        # "one two three" is 13 chars, exceeds available
        # "one two" is 7 chars, which is > 50% of 12, so good boundary
        assert result == "one two..."
        assert len(result) <= 15

    def test_truncation_no_good_boundary(self):
        """Test fallback when no good word boundary exists."""
        # Very long word at start, no good place to break
        result = _truncate_at_word_boundary("supercalifragilisticexpialidocious is here", 20)
        # Should hard truncate since no good boundary > 50% of available
        assert result == "supercalifragilis..."
        assert len(result) <= 20

    def test_custom_suffix(self):
        """Test custom suffix option."""
        result = _truncate_at_word_boundary("hello world this is long", 20, suffix="[...]")
        assert result.endswith("[...]")
        assert len(result) <= 20

    def test_single_long_word(self):
        """Test with a single word longer than max_len."""
        result = _truncate_at_word_boundary("supercalifragilisticexpialidocious", 20)
        # No spaces, so hard truncate
        assert result == "supercalifragilis..."
        assert len(result) <= 20

    def test_empty_string(self):
        """Test with empty string."""
        result = _truncate_at_word_boundary("", 10)
        assert result == ""

    def test_suffix_longer_than_max_len(self):
        """Test when suffix itself doesn't fit."""
        result = _truncate_at_word_boundary("hello", 2)
        # Should just truncate without suffix if suffix doesn't fit
        assert result == "he"


class TestEnforceFiftySeventyTwo:
    """Tests for the enforce_fifty_seventy_two function."""

    def test_short_subject_unchanged(self):
        """Test that short subject lines are unchanged."""
        message = "feat(auth): add login"
        result = enforce_fifty_seventy_two(message)
        assert result == message

    def test_long_subject_with_prefix_truncated(self):
        """Test long subject with conventional commit prefix."""
        message = "feat(authentication): implement user authentication with multi-factor support"
        result = enforce_fifty_seventy_two(message)
        # Should preserve prefix and truncate description at word boundary
        assert result.startswith("feat(authentication):")
        assert len(result.split("\n")[0]) <= 50
        assert result.endswith("...")

    def test_long_subject_no_prefix_truncated(self):
        """Test long subject without conventional commit prefix."""
        message = "implement user authentication with multi-factor support and session management"
        result = enforce_fifty_seventy_two(message)
        # Should truncate at word boundary
        assert len(result.split("\n")[0]) <= 50
        assert result.endswith("...")

    def test_very_long_prefix_fallback(self):
        """Test when prefix itself is too long."""
        message = "feat(extremelylongscopenameherewow): some description here"
        result = enforce_fifty_seventy_two(message)
        # Prefix is 38 chars, only 12 left, which is < 10 threshold
        # Should fall back to truncating whole thing
        assert len(result.split("\n")[0]) <= 50

    def test_body_wrapped_at_72(self):
        """Test body lines are wrapped at 72 characters."""
        long_line = "This is a line that is definitely longer than seventy two characters and should be wrapped properly at word boundaries."
        message = f"feat: short subject\n\n{long_line}\nShort line."
        result = enforce_fifty_seventy_two(message)
        lines = result.split("\n")
        # Check that no line exceeds 72 chars
        for line in lines:
            assert len(line) <= 72, f"Line exceeds 72 chars: {line!r}"

    def test_blank_line_after_subject(self):
        """Test that blank line is added after subject."""
        message = "feat: subject\nBody line here."
        result = enforce_fifty_seventy_two(message)
        lines = result.split("\n")
        assert lines[0] == "feat: subject"
        assert lines[1] == ""
        assert lines[2] == "Body line here."

    def test_empty_message(self):
        """Test empty message handling."""
        result = enforce_fifty_seventy_two("")
        assert result == ""

    def test_single_line_message(self):
        """Test single line message."""
        message = "feat: short subject"
        result = enforce_fifty_seventy_two(message)
        assert result == message

    def test_subject_already_has_blank_line(self):
        """Test message that already has blank line after subject."""
        message = "feat: subject\n\nBody line."
        result = enforce_fifty_seventy_two(message)
        lines = result.split("\n")
        assert lines[0] == "feat: subject"
        assert lines[1] == ""
        assert lines[2] == "Body line."

    def test_multiple_body_lines_wrapped(self):
        """Test multiple long body lines are all wrapped."""
        # Lines with spaces so they can be wrapped
        line1 = "word " * 20  # 100 chars with spaces
        line2 = "another " * 15  # 120 chars with spaces
        message = f"feat: test\n\n{line1}\n{line2}"
        result = enforce_fifty_seventy_two(message)
        lines = result.split("\n")
        for line in lines:
            assert len(line) <= 72, f"Line exceeds 72: {line!r}"


class TestCleanCommitMessageWithFiftySeventyTwo:
    """Tests for clean_commit_message with fifty_seventy_two flag."""

    def test_enforces_50_72_when_enabled(self):
        """Test that 50/72 rule is applied when flag is True."""
        long_subject = "feat: " + "x" * 100
        result = clean_commit_message(long_subject, fifty_seventy_two=True)
        first_line = result.split("\n")[0]
        assert len(first_line) <= 50

    def test_no_50_72_when_disabled(self):
        """Test that 50/72 rule is not applied when flag is False."""
        long_subject = "feat: " + "x" * 100
        result = clean_commit_message(long_subject, fifty_seventy_two=False)
        first_line = result.split("\n")[0]
        # Without flag, no truncation happens
        assert len(first_line) > 50

    def test_preserves_other_cleaning_with_50_72(self):
        """Test that other cleaning still happens with 50/72 enabled."""
        message = "```\nfeat: test\n```"
        result = clean_commit_message(message, fifty_seventy_two=False)
        assert "```" not in result

    def test_combines_think_tags_and_50_72(self):
        """Test think tag removal combined with 50/72 enforcement."""
        message = "<think>Some reasoning</think>\nfeat: " + "x" * 100
        result = clean_commit_message(message, fifty_seventy_two=True)
        assert "<think>" not in result
        first_line = result.split("\n")[0]
        assert len(first_line) <= 50
