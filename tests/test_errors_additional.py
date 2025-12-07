"""Additional tests for errors.py to increase coverage from 97% to 99%+."""

from unittest.mock import patch

from gac.errors import AIError, ConfigError, GitError, format_error_for_user, handle_error


class TestErrorsMissingCoverage:
    """Tests for uncovered lines in errors.py."""

    @patch("gac.errors.logger")
    def test_handle_error_ai_error(self, mock_logger):
        """Test handle_error with AIError."""
        error = AIError.model_error("Test AI error")

        handle_error(error, quiet=True)

        mock_logger.error.assert_called()
        # Check that AI-specific message was logged
        calls = [str(call) for call in mock_logger.error.call_args_list]
        assert any("AI operation failed" in call for call in calls)
        assert any("Please check your configuration and API keys" in call for call in calls)

    def test_format_error_for_user_config_error(self):
        """Test format_error_for_user for ConfigError."""
        error = ConfigError("Invalid config")

        result = format_error_for_user(error)

        assert "Please check your configuration settings" in result
        assert "Invalid config" in result

    def test_format_error_for_user_line_205_fallback(self):
        """Test format_error_for_user fallback path (line 205)."""

        # Create an error that will trigger the final fallback
        class UnexpectedError(Exception):
            pass

        error = UnexpectedError("Some unexpected error")

        # This should go through all the loops and hit the fallback return
        result = format_error_for_user(error)

        # Should include the base message
        assert "Some unexpected error" in result

    @patch("gac.errors.logger")
    def test_handle_error_git_error(self, mock_logger):
        """Test handle_error with GitError to hit line 147."""
        error = GitError("Test git error")

        handle_error(error, quiet=True)

        # Check that Git-specific message was logged
        calls = [str(call) for call in mock_logger.error.call_args_list]
        assert any("Git operation failed" in call for call in calls)
        assert any("Please check your repository status" in call for call in calls)
