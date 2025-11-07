"""Tests for auth_cli module."""

import unittest.mock as mock

import click
import pytest

from gac.auth_cli import auth


class TestAuthCli:
    """Test the auth CLI command."""

    def test_auth_command_exists(self):
        """Test that the auth command is properly defined."""
        assert auth is not None
        assert hasattr(auth, "callback")
        assert auth.name == "auth"

    @mock.patch("gac.auth_cli.authenticate_and_save")
    @mock.patch("gac.auth_cli.load_stored_token")
    @mock.patch("gac.auth_cli.click.echo")
    @mock.patch("gac.auth_cli.setup_logging")
    def test_auth_success_with_existing_token(self, mock_setup_logging, mock_echo, mock_load_token, mock_auth):
        """Test successful authentication when token already exists."""
        # Setup mocks
        mock_load_token.return_value = "existing_token"
        mock_auth.return_value = True

        # Create a mock context for the click command
        ctx = mock.Mock()
        ctx.params = {"quiet": False, "log_level": "INFO"}

        # Call the command
        auth.callback(quiet=False, log_level="INFO")

        # Verify calls
        mock_setup_logging.assert_called_once_with("INFO")
        mock_load_token.assert_called_once()
        mock_auth.assert_called_once_with(quiet=False)

        # Check that success messages were printed
        echo_messages = [call[0][0] if len(call[0]) > 0 else "" for call in mock_echo.call_args_list]
        assert any("Found existing Claude Code access token" in msg for msg in echo_messages)
        assert any("authentication completed successfully" in msg for msg in echo_messages)

    @mock.patch("gac.auth_cli.authenticate_and_save")
    @mock.patch("gac.auth_cli.load_stored_token")
    @mock.patch("gac.auth_cli.click.echo")
    @mock.patch("gac.auth_cli.setup_logging")
    def test_auth_success_no_existing_token(self, mock_setup_logging, mock_echo, mock_load_token, mock_auth):
        """Test successful authentication when no token exists."""
        # Setup mocks
        mock_load_token.return_value = None
        mock_auth.return_value = True

        # Call the command
        auth.callback(quiet=False, log_level="INFO")

        # Verify calls
        mock_setup_logging.assert_called_once_with("INFO")
        mock_load_token.assert_called_once()
        mock_auth.assert_called_once_with(quiet=False)

        # Check that success messages were printed
        echo_messages = [call[0][0] if len(call[0]) > 0 else "" for call in mock_echo.call_args_list]
        assert not any("Found existing Claude Code access token" in msg for msg in echo_messages)
        assert any("authentication completed successfully" in msg for msg in echo_messages)

    @mock.patch("gac.auth_cli.authenticate_and_save")
    @mock.patch("gac.auth_cli.load_stored_token")
    @mock.patch("gac.auth_cli.click.echo")
    @mock.patch("gac.auth_cli.setup_logging")
    def test_auth_failure(self, mock_setup_logging, mock_echo, mock_load_token, mock_auth):
        """Test failed authentication."""
        # Setup mocks
        mock_load_token.return_value = "existing_token"
        mock_auth.return_value = False

        # Call the command and expect it to raise an exception
        with pytest.raises(click.ClickException):
            auth.callback(quiet=False, log_level="INFO")

        # Verify calls
        mock_setup_logging.assert_called_once_with("INFO")
        mock_load_token.assert_called_once()
        mock_auth.assert_called_once_with(quiet=False)

        # Check that failure messages were printed
        echo_messages = [call[0][0] if len(call[0]) > 0 else "" for call in mock_echo.call_args_list]
        assert any("authentication failed" in msg for msg in echo_messages)

    @mock.patch("gac.auth_cli.authenticate_and_save")
    @mock.patch("gac.auth_cli.load_stored_token")
    @mock.patch("gac.auth_cli.click.echo")
    @mock.patch("gac.auth_cli.setup_logging")
    def test_auth_quiet_mode(self, mock_setup_logging, mock_echo, mock_load_token, mock_auth):
        """Test authentication in quiet mode."""
        # Setup mocks
        mock_load_token.return_value = "existing_token"
        mock_auth.return_value = True

        # Call the command in quiet mode
        auth.callback(quiet=True, log_level="INFO")

        # Verify logging setup with ERROR level in quiet mode
        mock_setup_logging.assert_called_once_with("ERROR")
        mock_load_token.assert_called_once()
        mock_auth.assert_called_once_with(quiet=True)

        # In quiet mode, only error messages should be printed
        echo_messages = [call[0][0] if len(call[0]) > 0 else "" for call in mock_echo.call_args_list]
        # Should not have informational messages in quiet mode
        assert not any("Found existing" in msg for msg in echo_messages)
        assert not any("Starting Claude Code" in msg for msg in echo_messages)

    @mock.patch("gac.auth_cli.authenticate_and_save")
    @mock.patch("gac.auth_cli.load_stored_token")
    @mock.patch("gac.auth_cli.click.echo")
    @mock.patch("gac.auth_cli.setup_logging")
    def test_auth_custom_log_level(self, mock_setup_logging, mock_echo, mock_load_token, mock_auth):
        """Test authentication with custom log level."""
        # Setup mocks
        mock_load_token.return_value = None
        mock_auth.return_value = True

        # Call the command with custom log level
        auth.callback(quiet=False, log_level="DEBUG")

        # Verify custom log level was used
        mock_setup_logging.assert_called_once_with("DEBUG")
        mock_auth.assert_called_once_with(quiet=False)
