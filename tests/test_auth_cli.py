"""Tests for auth_cli module."""

import unittest.mock as mock

from click.testing import CliRunner

from gac.auth_cli import auth, qwen


class TestAuthCli:
    """Test the auth CLI command."""

    def test_auth_command_exists(self):
        """Test that the auth command is properly defined."""
        assert auth is not None
        assert auth.name == "auth"

    def test_auth_is_group(self):
        """Test that auth is a group command."""
        assert hasattr(auth, "commands")
        assert "claude-code" in auth.commands
        assert "qwen" in auth.commands

    @mock.patch("gac.auth_cli.authenticate_and_save")
    @mock.patch("gac.auth_cli.load_stored_token")
    @mock.patch("gac.auth_cli.click.echo")
    @mock.patch("gac.auth_cli.setup_logging")
    def test_auth_claude_code_success_with_existing_token(
        self, mock_setup_logging, mock_echo, mock_load_token, mock_auth
    ):
        """Test successful Claude Code authentication when token already exists."""
        mock_load_token.return_value = "existing_token"
        mock_auth.return_value = True

        runner = CliRunner()
        result = runner.invoke(auth, ["claude-code"])

        assert result.exit_code == 0
        mock_load_token.assert_called_once()
        mock_auth.assert_called_once_with(quiet=False)

    @mock.patch("gac.auth_cli.authenticate_and_save")
    @mock.patch("gac.auth_cli.load_stored_token")
    @mock.patch("gac.auth_cli.click.echo")
    @mock.patch("gac.auth_cli.setup_logging")
    def test_auth_claude_code_success_no_existing_token(
        self, mock_setup_logging, mock_echo, mock_load_token, mock_auth
    ):
        """Test successful Claude Code authentication when no token exists."""
        mock_load_token.return_value = None
        mock_auth.return_value = True

        runner = CliRunner()
        result = runner.invoke(auth, ["claude-code"])

        assert result.exit_code == 0
        mock_load_token.assert_called_once()
        mock_auth.assert_called_once_with(quiet=False)

    @mock.patch("gac.auth_cli.authenticate_and_save")
    @mock.patch("gac.auth_cli.load_stored_token")
    @mock.patch("gac.auth_cli.click.echo")
    @mock.patch("gac.auth_cli.setup_logging")
    def test_auth_claude_code_failure(self, mock_setup_logging, mock_echo, mock_load_token, mock_auth):
        """Test failed Claude Code authentication."""
        mock_load_token.return_value = "existing_token"
        mock_auth.return_value = False

        runner = CliRunner()
        result = runner.invoke(auth, ["claude-code"])

        assert result.exit_code != 0
        mock_load_token.assert_called_once()
        mock_auth.assert_called_once_with(quiet=False)

    @mock.patch("gac.auth_cli.authenticate_and_save")
    @mock.patch("gac.auth_cli.load_stored_token")
    @mock.patch("gac.auth_cli.click.echo")
    @mock.patch("gac.auth_cli.setup_logging")
    def test_auth_claude_code_quiet_mode(self, mock_setup_logging, mock_echo, mock_load_token, mock_auth):
        """Test Claude Code authentication in quiet mode."""
        mock_load_token.return_value = "existing_token"
        mock_auth.return_value = True

        runner = CliRunner()
        result = runner.invoke(auth, ["claude-code", "--quiet"])

        assert result.exit_code == 0
        mock_setup_logging.assert_called_once_with("ERROR")
        mock_auth.assert_called_once_with(quiet=True)

    @mock.patch("gac.auth_cli.authenticate_and_save")
    @mock.patch("gac.auth_cli.load_stored_token")
    @mock.patch("gac.auth_cli.click.echo")
    @mock.patch("gac.auth_cli.setup_logging")
    def test_auth_claude_code_custom_log_level(self, mock_setup_logging, mock_echo, mock_load_token, mock_auth):
        """Test Claude Code authentication with custom log level."""
        mock_load_token.return_value = None
        mock_auth.return_value = True

        runner = CliRunner()
        result = runner.invoke(auth, ["claude-code", "--log-level", "DEBUG"])

        assert result.exit_code == 0
        mock_setup_logging.assert_called_once_with("DEBUG")
        mock_auth.assert_called_once_with(quiet=False)

    @mock.patch("gac.auth_cli.TokenStore")
    @mock.patch("gac.auth_cli.load_stored_token")
    def test_auth_status_no_auth(self, mock_load_token, mock_token_store):
        """Test auth status when no providers are authenticated."""
        mock_load_token.return_value = None
        mock_store_instance = mock.Mock()
        mock_store_instance.get_token.return_value = None
        mock_token_store.return_value = mock_store_instance

        runner = CliRunner()
        result = runner.invoke(auth)

        assert result.exit_code == 0
        assert "Claude Code: ✗ Not authenticated" in result.output
        assert "Qwen:        ✗ Not authenticated" in result.output


class TestQwenAuthCli:
    """Test the Qwen auth CLI commands."""

    def test_qwen_command_exists(self):
        """Test that the qwen command is properly defined."""
        assert qwen is not None
        assert qwen.name == "qwen"

    def test_qwen_has_subcommands(self):
        """Test that qwen has expected subcommands."""
        assert hasattr(qwen, "commands")
        assert "login" in qwen.commands
        assert "logout" in qwen.commands
        assert "status" in qwen.commands

    @mock.patch("gac.auth_cli.QwenOAuthProvider")
    def test_qwen_status_not_authenticated(self, mock_provider_class):
        """Test qwen status when not authenticated."""
        mock_provider = mock.Mock()
        mock_provider.get_token.return_value = None
        mock_provider_class.return_value = mock_provider

        runner = CliRunner()
        result = runner.invoke(auth, ["qwen", "status"])

        assert result.exit_code == 0
        assert "Not authenticated" in result.output

    @mock.patch("gac.auth_cli.QwenOAuthProvider")
    def test_qwen_status_authenticated(self, mock_provider_class):
        """Test qwen status when authenticated."""
        mock_provider = mock.Mock()
        mock_provider.get_token.return_value = {
            "access_token": "test_token",
            "expiry": 9999999999,
            "resource_url": "https://api.qwen.ai",
        }
        mock_provider_class.return_value = mock_provider

        runner = CliRunner()
        result = runner.invoke(auth, ["qwen", "status"])

        assert result.exit_code == 0
        assert "Authenticated" in result.output
        assert "https://api.qwen.ai" in result.output

    @mock.patch("gac.auth_cli.QwenOAuthProvider")
    def test_qwen_logout_not_authenticated(self, mock_provider_class):
        """Test qwen logout when not authenticated."""
        mock_provider = mock.Mock()
        mock_provider.is_authenticated.return_value = False
        mock_provider_class.return_value = mock_provider

        runner = CliRunner()
        result = runner.invoke(auth, ["qwen", "logout"])

        assert result.exit_code == 0
        assert "Not currently authenticated" in result.output
        mock_provider.logout.assert_not_called()

    @mock.patch("gac.auth_cli.QwenOAuthProvider")
    def test_qwen_logout_success(self, mock_provider_class):
        """Test successful qwen logout."""
        mock_provider = mock.Mock()
        mock_provider.is_authenticated.return_value = True
        mock_provider_class.return_value = mock_provider

        runner = CliRunner()
        result = runner.invoke(auth, ["qwen", "logout"])

        assert result.exit_code == 0
        assert "Successfully logged out" in result.output
        mock_provider.logout.assert_called_once()

    @mock.patch("gac.auth_cli.setup_logging")
    @mock.patch("gac.auth_cli.QwenOAuthProvider")
    def test_qwen_login_already_authenticated(self, mock_provider_class, mock_setup_logging):
        """Test qwen login when already authenticated (declined re-auth)."""
        mock_provider = mock.Mock()
        mock_provider.is_authenticated.return_value = True
        mock_provider_class.return_value = mock_provider

        runner = CliRunner()
        result = runner.invoke(auth, ["qwen", "login"], input="n\n")

        assert result.exit_code == 0
        assert "Already authenticated" in result.output
        mock_provider.initiate_auth.assert_not_called()

    @mock.patch("gac.auth_cli.setup_logging")
    @mock.patch("gac.auth_cli.QwenOAuthProvider")
    def test_qwen_login_success(self, mock_provider_class, mock_setup_logging):
        """Test successful qwen login."""
        mock_provider = mock.Mock()
        mock_provider.is_authenticated.return_value = False
        mock_provider_class.return_value = mock_provider

        runner = CliRunner()
        result = runner.invoke(auth, ["qwen", "login"])

        assert result.exit_code == 0
        mock_provider.initiate_auth.assert_called_once_with(open_browser=True)

    @mock.patch("gac.auth_cli.setup_logging")
    @mock.patch("gac.auth_cli.QwenOAuthProvider")
    def test_qwen_login_no_browser(self, mock_provider_class, mock_setup_logging):
        """Test qwen login with --no-browser flag."""
        mock_provider = mock.Mock()
        mock_provider.is_authenticated.return_value = False
        mock_provider_class.return_value = mock_provider

        runner = CliRunner()
        result = runner.invoke(auth, ["qwen", "login", "--no-browser"])

        assert result.exit_code == 0
        mock_provider.initiate_auth.assert_called_once_with(open_browser=False)

    @mock.patch("gac.auth_cli.setup_logging")
    @mock.patch("gac.auth_cli.QwenOAuthProvider")
    def test_qwen_login_failure(self, mock_provider_class, mock_setup_logging):
        """Test qwen login failure."""
        mock_provider = mock.Mock()
        mock_provider.is_authenticated.return_value = False
        mock_provider.initiate_auth.side_effect = Exception("Auth failed")
        mock_provider_class.return_value = mock_provider

        runner = CliRunner()
        result = runner.invoke(auth, ["qwen", "login"])

        assert result.exit_code != 0
        assert "failed" in result.output.lower()
