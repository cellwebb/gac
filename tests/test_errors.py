"""Tests for the errors module."""

import unittest
from unittest.mock import patch

from gac.errors import (
    AI_ERROR_CODES,
    AIError,
    ConfigError,
    FormattingError,
    GacError,
    GitError,
    SecurityError,
    format_error_for_user,
    handle_error,
    with_error_handling,
)


class TestErrors(unittest.TestCase):
    """Tests for error handling functionality."""

    def test_error_inheritance(self):
        """Test error classes follow the expected inheritance hierarchy."""
        # Verify the behavior: error classes have the expected inheritance structure
        self.assertTrue(issubclass(GacError, Exception))
        self.assertTrue(issubclass(ConfigError, GacError))
        self.assertTrue(issubclass(GitError, GacError))
        self.assertTrue(issubclass(AIError, GacError))
        self.assertTrue(issubclass(FormattingError, GacError))
        self.assertTrue(issubclass(SecurityError, GacError))

    def test_error_exit_codes(self):
        """Test error classes provide appropriate exit codes."""
        # Define expected exit codes for each error type
        exit_codes = {
            GacError: 1,
            ConfigError: 2,
            GitError: 3,
            AIError: 4,
            FormattingError: 5,
            SecurityError: 6,
        }

        # Verify the behavior: error classes have the expected exit codes
        for error_class, expected_code in exit_codes.items():
            self.assertEqual(error_class.exit_code, expected_code)

        # Verify the behavior: error instances inherit the exit code
        for error_class, expected_code in exit_codes.items():
            error = error_class("Test message")
            self.assertEqual(error.exit_code, expected_code)

        # Verify the behavior: exit code can be overridden in constructor
        error = GacError("Test message", exit_code=42)
        self.assertEqual(error.exit_code, 42)

    def test_ai_error_factory_methods(self):
        """Test AIError factory methods create the correct error types."""
        # Test authentication error
        auth_error = AIError.authentication_error("Invalid API key")
        self.assertEqual(auth_error.message, "Invalid API key")
        self.assertEqual(auth_error.error_type, "authentication")
        self.assertEqual(auth_error.error_code, 401)

        # Test connection error
        conn_error = AIError.connection_error("Network issue")
        self.assertEqual(conn_error.message, "Network issue")
        self.assertEqual(conn_error.error_type, "connection")
        self.assertEqual(conn_error.error_code, 503)

        # Test rate limit error
        rate_error = AIError.rate_limit_error("Too many requests")
        self.assertEqual(rate_error.message, "Too many requests")
        self.assertEqual(rate_error.error_type, "rate_limit")
        self.assertEqual(rate_error.error_code, 429)

        # Test timeout error
        timeout_error = AIError.timeout_error("Request timed out")
        self.assertEqual(timeout_error.message, "Request timed out")
        self.assertEqual(timeout_error.error_type, "timeout")
        self.assertEqual(timeout_error.error_code, 408)

        # Test model error
        model_error = AIError.model_error("Model not found")
        self.assertEqual(model_error.message, "Model not found")
        self.assertEqual(model_error.error_type, "model")
        self.assertEqual(model_error.error_code, 400)

    @patch("sys.exit")
    @patch("gac.errors.logger")
    @patch("gac.errors.console.print")
    def test_handle_error(self, mock_print, mock_logger, mock_exit):
        """Test handle_error function processes errors appropriately."""
        # Test with GACError
        error = ConfigError("Configuration error")
        handle_error(error, exit_program=True)

        # Verify the error is logged with the correct messages
        mock_logger.error.assert_any_call("Error: Configuration error")
        mock_logger.error.assert_any_call("An unexpected error occurred.")
        mock_logger.error.assert_any_call("Exiting program due to error.")

        # Verify sys.exit was called with 2 (ConfigError.exit_code)
        mock_exit.assert_called_once_with(2)

        # Reset mocks for next test
        mock_logger.reset_mock()
        mock_print.reset_mock()
        mock_exit.reset_mock()

        # Test with standard Exception
        error = ValueError("Invalid value")
        handle_error(error, exit_program=True)

        # Verify the error is logged with the correct messages
        mock_logger.error.assert_any_call("Error: Invalid value")
        mock_logger.error.assert_any_call("An unexpected error occurred.")
        mock_logger.error.assert_any_call("Exiting program due to error.")

        # Verify sys.exit was called with 1 (default for non-GacError)
        mock_exit.assert_called_once_with(1)

        # Reset mocks for next test
        mock_logger.reset_mock()
        mock_print.reset_mock()
        mock_exit.reset_mock()

        # Test without exit
        error = ConfigError("Configuration error")
        handle_error(error, exit_program=False)

        # Verify the error is logged with the correct messages
        mock_logger.error.assert_any_call("Error: Configuration error")
        mock_logger.error.assert_any_call("An unexpected error occurred.")

        # Verify sys.exit was not called
        mock_exit.assert_not_called()

    def test_format_error_for_user(self):
        """Test format_error_for_user provides helpful error messages."""
        # Test with AI error
        error = AIError("Failed to connect to API")
        message = format_error_for_user(error)

        # Verify the behavior: error message includes the original error
        self.assertIn("Failed to connect to API", message)

        # Verify the behavior: error message includes helpful remediation steps
        self.assertIn("check your API key", message)

        # Test with standard Exception
        error = Exception("Unknown error")
        message = format_error_for_user(error)

        # Verify the behavior: unknown errors include appropriate guidance
        self.assertIn("Unknown error", message)
        self.assertIn("report it as a bug", message)

        # Test all error types to ensure they have remediation steps
        errors = {
            AIError: "AI provider error",
            ConfigError: "Invalid configuration",
            GitError: "Git error",
            FormattingError: "Formatting failed",
        }

        for error_class, msg in errors.items():
            error = error_class(msg)
            formatted = format_error_for_user(error)

            # Verify the behavior: all error types include the original message
            self.assertIn(msg, formatted)

            # Verify the behavior: all error types include remediation steps
            self.assertGreater(len(formatted), len(msg))

    def test_format_error_authentication(self):
        """Test formatting of authentication errors."""
        error = AIError.authentication_error("Invalid API key")
        message = format_error_for_user(error)
        self.assertIn("Invalid API key", message)
        self.assertIn("check your API key", message)
        self.assertIn("ensure it is valid", message)

    def test_format_error_connection(self):
        """Test formatting of connection errors."""
        error = AIError.connection_error("Network unreachable")
        message = format_error_for_user(error)
        self.assertIn("Network unreachable", message)
        self.assertIn("check your internet connection", message)
        self.assertIn("try again", message)

    def test_format_error_rate_limit(self):
        """Test formatting of rate limit errors."""
        error = AIError.rate_limit_error("Too many requests")
        message = format_error_for_user(error)
        self.assertIn("Too many requests", message)
        self.assertIn("rate limit", message)
        self.assertIn("wait", message)

    def test_format_error_timeout(self):
        """Test formatting of timeout errors."""
        error = AIError.timeout_error("Request timed out")
        message = format_error_for_user(error)
        self.assertIn("Request timed out", message)
        self.assertIn("timed out", message)
        self.assertIn("try again", message)

    def test_format_error_model(self):
        """Test formatting of model errors."""
        error = AIError.model_error("Model not found")
        message = format_error_for_user(error)
        self.assertIn("Model not found", message)
        self.assertIn("check that the specified model exists", message)

    def test_unknown_error_factory(self):
        """Test AIError.unknown_error factory method."""
        error = AIError.unknown_error("Unknown issue")
        self.assertEqual(error.message, "Unknown issue")
        self.assertEqual(error.error_type, "unknown")
        self.assertEqual(error.error_code, 500)

    def test_ai_error_codes_mapping(self):
        """Test AI_ERROR_CODES mapping is correct."""
        expected_codes = {
            "authentication": 401,
            "connection": 503,
            "rate_limit": 429,
            "timeout": 408,
            "model": 400,
            "unknown": 500,
        }
        self.assertEqual(AI_ERROR_CODES, expected_codes)

    def test_ai_error_with_exit_code_override(self):
        """Test AIError with exit code override."""
        error = AIError("Test error", error_type="model", exit_code=10)
        self.assertEqual(error.exit_code, 10)
        self.assertEqual(error.error_type, "model")
        self.assertEqual(error.error_code, 400)

    def test_security_error_properties(self):
        """Test SecurityError has correct properties."""
        error = SecurityError("Security issue detected")
        self.assertEqual(error.exit_code, 6)
        self.assertEqual(error.message, "Security issue detected")
        self.assertIsInstance(error, GacError)

    @patch("gac.errors.logger")
    def test_handle_error_quiet_mode(self, mock_logger):
        """Test handle_error in quiet mode."""
        error = AIError("AI error", error_type="authentication")
        handle_error(error, exit_program=False, quiet=True)

        # Should still log the error even in quiet mode
        mock_logger.error.assert_called()

    @patch("gac.errors.logger")
    def test_handle_error_ai_error_specific_logging(self, mock_logger):
        """Test handle_error logs specific messages for AI errors."""
        error = AIError.connection_error("Cannot connect")
        handle_error(error, exit_program=False, quiet=False)

        # Should log AI-specific message
        mock_logger.error.assert_any_call("AI operation failed. Please check your configuration and API keys.")

    @patch("gac.errors.logger")
    def test_handle_error_security_error_specific_logging(self, mock_logger):
        """Test handle_error logs specific messages for Security errors."""
        error = SecurityError("Secret detected")
        handle_error(error, exit_program=False, quiet=False)

        # Should log security-specific message
        mock_logger.error.assert_any_call("Security scan detected potential secrets in staged changes.")

    def test_format_error_for_user_security_error(self):
        """Test format_error_for_user for SecurityError."""
        error = SecurityError("Secret detected")
        message = format_error_for_user(error)
        self.assertIn("Secret detected", message)
        self.assertIn("remove or secure any detected secrets", message)

    def test_format_error_for_user_ai_generic_without_error_type(self):
        """Test format_error_for_user for AI errors without error_type attribute."""
        error = AIError("Generic AI error")
        # Remove error_type to test generic case
        if hasattr(error, "error_type"):
            delattr(error, "error_type")

        message = format_error_for_user(error)
        self.assertIn("Generic AI error", message)
        self.assertIn("check your API key, model name, and internet connection", message)

    def test_with_error_handling_decorator_success(self):
        """Test with_error_handling decorator on successful function."""

        @with_error_handling(ConfigError, "Operation failed")
        def successful_function():
            return "success"

        result = successful_function()
        self.assertEqual(result, "success")

    @patch("gac.errors.handle_error")
    def test_with_error_handling_decorator_exception_no_exit(self, mock_handle):
        """Test with_error_handling decorator with exception, no exit."""

        @with_error_handling(ConfigError, "Operation failed", exit_on_error=False)
        def failing_function():
            raise ValueError("Original error")

        result = failing_function()
        self.assertIsNone(result)
        mock_handle.assert_called_once()
        error_arg = mock_handle.call_args[0][0]
        self.assertIsInstance(error_arg, ConfigError)
        self.assertIn("Operation failed: Original error", str(error_arg))

    @patch("gac.errors.handle_error")
    def test_with_error_handling_decorator_exception_with_exit(self, mock_handle):
        """Test with_error_handling decorator with exception and exit."""

        @with_error_handling(GitError, "Git operation failed", exit_on_error=True)
        def failing_function():
            raise RuntimeError("Git command failed")

        failing_function()
        mock_handle.assert_called_once()
        error_arg = mock_handle.call_args[0][0]
        self.assertIsInstance(error_arg, GitError)
        self.assertIn("Git operation failed: Git command failed", str(error_arg))

    @patch("gac.errors.handle_error")
    def test_with_error_handling_decorator_quiet_mode(self, mock_handle):
        """Test with_error_handling decorator in quiet mode."""

        @with_error_handling(ConfigError, "Operation failed", quiet=True)
        def failing_function():
            raise ValueError("Original error")

        failing_function()
        mock_handle.assert_called_once()
        # Check that quiet parameter was passed
        call_kwargs = mock_handle.call_args[1]
        self.assertTrue(call_kwargs["quiet"])

    @patch("gac.errors.handle_error")
    def test_with_error_handling_decorator_different_error_types(self, mock_handle):
        """Test with_error_handling with different error types."""

        @with_error_handling(SecurityError, "Security issue")
        def security_failing_function():
            raise Exception("Security violation")

        security_failing_function()
        error_arg = mock_handle.call_args[0][0]
        self.assertIsInstance(error_arg, SecurityError)

    def test_gac_error_with_full_constructor(self):
        """Test GacError with all constructor parameters."""
        error = GacError(
            message="Test message",
            details="Additional details",
            suggestion="Try this instead",
            exit_code=42,
        )
        self.assertEqual(error.message, "Test message")
        self.assertEqual(error.details, "Additional details")
        self.assertEqual(error.suggestion, "Try this instead")
        self.assertEqual(error.exit_code, 42)
        self.assertEqual(str(error), "Test message")

    @patch("gac.errors.logger")
    def test_handle_error_git_error_specific_logging(self, mock_logger):
        """Test handle_error logs specific message for Git errors (line 147)."""
        error = GitError("Repository not found")
        handle_error(error, exit_program=False, quiet=False)

        # Should log Git-specific message
        mock_logger.error.assert_any_call("Git operation failed. Please check your repository status.")

    @patch("gac.errors.logger")
    def test_handle_error_generic_exception_logging(self, mock_logger):
        """Test handle_error logs generic message for non-GacErrors (line 147)."""
        error = ValueError("Some random error")
        handle_error(error, exit_program=False, quiet=False)

        # Should log generic message
        mock_logger.error.assert_any_call("An unexpected error occurred.")

    def test_format_error_for_user_unknown_error_type_fallback(self):
        """Test format_error_for_user fallback for unknown error types (line 205)."""

        class CustomError(Exception):
            pass

        error = CustomError("Custom error message")
        message = format_error_for_user(error)

        # Should return base message for unknown error types
        self.assertIn("Custom error message", message)
        # Should include the generic advice
        self.assertIn("please report it as a bug", message.lower())

    def test_format_error_for_user_completely_unknown_error(self):
        """Test format_error_for_user with error that doesn't match any known class (line 205)."""

        class UnknownError(Exception):
            pass

        error = UnknownError("Something went terribly wrong")
        message = format_error_for_user(error)

        # Should fall back to base message since UnknownError doesn't match any keys
        self.assertIn("Something went terribly wrong", message)
        # Should include the fallback remediation advice
        self.assertIn("please report it as a bug", message.lower())
