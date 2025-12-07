"""Unit tests for grouped_commit_workflow.py core functionality."""

import json
import logging

import pytest

from gac.config import GACConfig
from gac.grouped_commit_workflow import GroupedCommitWorkflow


class TestValidateGroupedFilesOrFeedback:
    """Tests for the validate_grouped_files_or_feedback method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = GACConfig()
        self.workflow = GroupedCommitWorkflow(self.config)

    def test_validate_grouped_files_perfect_match(self):
        """Test validation with perfect file match."""
        staged = {"file1.py", "file2.py", "file3.py"}
        grouped_result = {
            "commits": [
                {"files": ["file1.py"], "message": "First commit"},
                {"files": ["file2.py", "file3.py"], "message": "Second commit"},
            ]
        }

        is_valid, feedback, detail_msg = self.workflow.validate_grouped_files_or_feedback(staged, grouped_result)

        assert is_valid is True
        assert feedback == ""
        assert detail_msg == ""

    def test_validate_grouped_files_missing_files(self):
        """Test validation with missing files."""
        staged = {"file1.py", "file2.py", "file3.py"}
        grouped_result = {
            "commits": [
                {"files": ["file1.py"], "message": "First commit"},
                {"files": ["file2.py"], "message": "Second commit"},  # file3.py missing
            ]
        }

        is_valid, feedback, detail_msg = self.workflow.validate_grouped_files_or_feedback(staged, grouped_result)

        assert is_valid is False
        assert "Missing: file3.py" in feedback
        assert "Missing: file3.py" in detail_msg

    def test_validate_grouped_files_unexpected_files(self):
        """Test validation with unexpected files."""
        staged = {"file1.py", "file2.py"}
        grouped_result = {
            "commits": [
                {"files": ["file1.py"], "message": "First commit"},
                {"files": ["file2.py", "file3.py"], "message": "Second commit"},  # file3.py unexpected
            ]
        }

        is_valid, feedback, detail_msg = self.workflow.validate_grouped_files_or_feedback(staged, grouped_result)

        assert is_valid is False
        assert "Not staged: file3.py" in feedback
        assert "Not staged: file3.py" in detail_msg

    def test_validate_grouped_files_duplicate_files(self):
        """Test validation with duplicate files."""
        staged = {"file1.py", "file2.py"}
        grouped_result = {
            "commits": [
                {"files": ["file1.py"], "message": "First commit"},
                {"files": ["file1.py", "file2.py"], "message": "Second commit"},  # file1.py duplicate
            ]
        }

        is_valid, feedback, detail_msg = self.workflow.validate_grouped_files_or_feedback(staged, grouped_result)

        assert is_valid is False
        assert "Duplicates: file1.py" in feedback
        assert "Duplicates: file1.py" in detail_msg

    def test_validate_grouped_files_multiple_problems(self):
        """Test validation with multiple problems."""
        staged = {"file1.py", "file2.py"}
        grouped_result = {
            "commits": [
                {"files": ["file1.py"], "message": "First commit"},
                {
                    "files": ["file1.py", "file3.py"],
                    "message": "Second commit",
                },  # file1.py duplicate, file3.py unexpected
            ]
        }

        is_valid, feedback, detail_msg = self.workflow.validate_grouped_files_or_feedback(staged, grouped_result)

        assert is_valid is False
        assert "Duplicates: file1.py" in feedback
        assert "Not staged: file3.py" in feedback
        assert "file1.py" in detail_msg
        assert "file3.py" in detail_msg

    def test_validate_grouped_files_empty_commits(self):
        """Test validation with empty commits array."""
        staged = {"file1.py"}
        grouped_result = {"commits": []}

        is_valid, feedback, detail_msg = self.workflow.validate_grouped_files_or_feedback(staged, grouped_result)

        assert is_valid is True  # Empty commits means no files covered, which is valid but will be caught elsewhere
        assert feedback == ""
        assert detail_msg == ""

    def test_validate_grouped_files_invalid_structure(self):
        """Test validation with invalid grouped result structure."""
        staged = {"file1.py"}
        grouped_result = {"commits": [{"message": "No files key"}]}  # Missing files

        is_valid, feedback, detail_msg = self.workflow.validate_grouped_files_or_feedback(staged, grouped_result)

        assert is_valid is True  # Will be handled in JSON validation, not here
        assert feedback == ""

    def test_validate_grouped_files_not_dict(self):
        """Test validation with non-dict grouped result."""
        staged = {"file1.py"}
        grouped_result = "invalid"  # Not a dict

        is_valid, feedback, detail_msg = self.workflow.validate_grouped_files_or_feedback(staged, grouped_result)

        assert is_valid is True  # Invalid structure will be caught in JSON validation
        assert feedback == ""


class TestParseAndValidateJsonResponse:
    """Tests for the parse_and_validate_json_response method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = GACConfig()
        self.workflow = GroupedCommitWorkflow(self.config)

    def test_parse_and_validate_valid_json(self):
        """Test parsing and validating valid JSON response."""
        raw_response = '{"commits": [{"files": ["file1.py"], "message": "First commit"}]}'
        result = self.workflow.parse_and_validate_json_response(raw_response)

        expected = {"commits": [{"files": ["file1.py"], "message": "First commit"}]}
        assert result == expected

    def test_parse_and_validate_json_with_extra_text(self):
        """Test parsing JSON with text before and after braces."""
        raw_response = (
            'Here\'s the JSON: {"commits": [{"files": ["file1.py"], "message": "First commit"}]}\n\nThat\'s it!'
        )
        result = self.workflow.parse_and_validate_json_response(raw_response)

        expected = {"commits": [{"files": ["file1.py"], "message": "First commit"}]}
        assert result == expected

    def test_parse_and_validate_json_missing_commits_key(self):
        """Test validation failure when commits key is missing."""
        raw_response = '{"other_key": "value"}'

        with pytest.raises(ValueError, match="Response missing 'commits' array"):
            self.workflow.parse_and_validate_json_response(raw_response)

    def test_parse_and_validate_json_commits_not_list(self):
        """Test validation failure when commits is not a list."""
        raw_response = '{"commits": "not_a_list"}'

        with pytest.raises(ValueError, match="Response missing 'commits' array"):
            self.workflow.parse_and_validate_json_response(raw_response)

    def test_parse_and_validate_json_empty_commits_array(self):
        """Test validation failure when commits array is empty."""
        raw_response = '{"commits": []}'

        with pytest.raises(ValueError, match="No commits in response"):
            self.workflow.parse_and_validate_json_response(raw_response)

    def test_parse_and_validate_json_commit_missing_files(self):
        """Test validation failure when commit missing files."""
        raw_response = '{"commits": [{"message": "No files key"}]}'

        with pytest.raises(ValueError, match="Commit 1 missing 'files' array"):
            self.workflow.parse_and_validate_json_response(raw_response)

    def test_parse_and_validate_json_commit_files_not_list(self):
        """Test validation failure when commit files is not a list."""
        raw_response = '{"commits": [{"files": "not_a_list", "message": "Test"}]}'

        with pytest.raises(ValueError, match="Commit 1 missing 'files' array"):
            self.workflow.parse_and_validate_json_response(raw_response)

    def test_parse_and_validate_json_commit_missing_message(self):
        """Test validation failure when commit missing message."""
        raw_response = '{"commits": [{"files": ["file1.py"]}]}'

        with pytest.raises(ValueError, match="Commit 1 missing 'message' string"):
            self.workflow.parse_and_validate_json_response(raw_response)

    def test_parse_and_validate_json_commit_message_not_string(self):
        """Test validation failure when commit message is not a string."""
        raw_response = '{"commits": [{"files": ["file1.py"], "message": 123}]}'

        with pytest.raises(ValueError, match="Commit 1 missing 'message' string"):
            self.workflow.parse_and_validate_json_response(raw_response)

    def test_parse_and_validate_json_commit_empty_files_array(self):
        """Test validation failure when commit has empty files array."""
        raw_response = '{"commits": [{"files": [], "message": "Test"}]}'

        with pytest.raises(ValueError, match="Commit 1 has empty files list"):
            self.workflow.parse_and_validate_json_response(raw_response)

    def test_parse_and_validate_json_commit_empty_message(self):
        """Test validation failure when commit has empty message."""
        raw_response = '{"commits": [{"files": ["file1.py"], "message": "   "}]}'

        with pytest.raises(ValueError, match="Commit 1 has empty message"):
            self.workflow.parse_and_validate_json_response(raw_response)

    def test_parse_and_validate_json_multiple_commits(self):
        """Test validation with multiple valid commits."""
        raw_response = json.dumps(
            {
                "commits": [
                    {"files": ["file1.py"], "message": "First commit"},
                    {"files": ["file2.py", "file3.py"], "message": "Second commit"},
                ]
            }
        )

        result = self.workflow.parse_and_validate_json_response(raw_response)

        assert len(result["commits"]) == 2
        assert result["commits"][0]["files"] == ["file1.py"]
        assert result["commits"][1]["files"] == ["file2.py", "file3.py"]

    def test_parse_and_validate_malformed_json(self):
        """Test handling of malformed JSON."""
        raw_response = '{"commits": [{"files": ["file1.py"], "message": "Incomplete'

        with pytest.raises(ValueError, match="Invalid JSON response"):
            self.workflow.parse_and_validate_json_response(raw_response)

    def test_parse_and_validate_no_braces(self):
        """Test handling when no braces found."""
        raw_response = "This is not JSON at all"

        with pytest.raises(ValueError, match="Invalid JSON response"):
            self.workflow.parse_and_validate_json_response(raw_response)


class TestHandleValidationRetry:
    """Tests for the handle_validation_retry method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = GACConfig()
        self.workflow = GroupedCommitWorkflow(self.config)

    def test_handle_validation_retry_max_retries_reached(self, caplog):
        """Test when max retries are reached."""
        caplog.set_level(logging.ERROR)
        conversation_messages = []
        attempts = 3
        content_retry_budget = 3
        raw_response = "invalid json"
        feedback_message = "Please fix the JSON"
        error_message = "Validation failed after retries"
        retry_context = "Structure validation"

        should_exit = self.workflow.handle_validation_retry(
            attempts,
            content_retry_budget,
            raw_response,
            feedback_message,
            error_message,
            conversation_messages,
            False,
            retry_context,
        )

        assert should_exit is True
        assert error_message in caplog.text
        assert "Raw model output:" in caplog.text
        # Conversation should have been updated
        assert len(conversation_messages) == 2
        assert conversation_messages[0]["role"] == "assistant"
        assert conversation_messages[1]["role"] == "user"

    def test_handle_validation_retry_continue_retrying(self, caplog):
        """Test when retries should continue."""
        caplog.set_level(logging.INFO)
        conversation_messages = []
        attempts = 1
        content_retry_budget = 3
        raw_response = "invalid json"
        feedback_message = "Please fix the JSON"
        error_message = "Validation failed"
        retry_context = "Structure validation"

        should_exit = self.workflow.handle_validation_retry(
            attempts,
            content_retry_budget,
            raw_response,
            feedback_message,
            error_message,
            conversation_messages,
            False,
            retry_context,
        )

        assert should_exit is False
        assert "Retry 1 of 2" in caplog.text
        assert retry_context in caplog.text
        # Conversation should have been updated
        assert len(conversation_messages) == 2

    def test_handle_validation_retry_quiet_mode(self, caplog):
        """Test retry handling in quiet mode."""
        conversation_messages = []
        attempts = 1
        content_retry_budget = 3
        raw_response = "invalid json"
        feedback_message = "Please fix the JSON"
        error_message = "Validation failed"
        retry_context = "Structure validation"

        should_exit = self.workflow.handle_validation_retry(
            attempts,
            content_retry_budget,
            raw_response,
            feedback_message,
            error_message,
            conversation_messages,
            True,
            retry_context,
        )

        assert should_exit is False
        # In quiet mode, retry message should not be logged
        assert "Retry" not in caplog.text

    def test_handle_validation_retry_conversation_persistence(self):
        """Test that conversation messages persist across retries."""
        conversation_messages = [{"role": "user", "content": "Generate commits"}]
        attempts = 2
        content_retry_budget = 3
        raw_response = "invalid json"
        feedback_message = "Please fix the JSON"
        error_message = "Validation failed"
        retry_context = "Structure validation"

        should_exit = self.workflow.handle_validation_retry(
            attempts,
            content_retry_budget,
            raw_response,
            feedback_message,
            error_message,
            conversation_messages,
            True,
            retry_context,
        )

        assert should_exit is False
        # Original message should be preserved
        assert conversation_messages[0]["role"] == "user"
        assert conversation_messages[0]["content"] == "Generate commits"
        # Retry messages should be appended
        assert conversation_messages[1]["role"] == "assistant"
        assert conversation_messages[2]["role"] == "user"
