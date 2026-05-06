"""Tests for auth_cli module."""

import unittest.mock as mock

from click.testing import CliRunner

from gac.auth_cli import auth, claude_code


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

    @mock.patch("gac.auth_cli.TokenStore")
    def test_auth_status_no_auth(self, mock_token_store):
        """Test auth status when no providers are authenticated."""
        mock_store_instance = mock.Mock()
        mock_store_instance.get_token.return_value = None
        mock_token_store.return_value = mock_store_instance

        runner = CliRunner()
        result = runner.invoke(auth)

        assert result.exit_code == 0
        assert "Claude Code: ✗ Not authenticated" in result.output

    @mock.patch("gac.auth_cli.TokenStore")
    def test_auth_status_with_auth(self, mock_token_store):
        """Test auth status when providers are authenticated."""
        mock_store_instance = mock.Mock()
        mock_store_instance.get_token.return_value = {"access_token": "claude_token", "token_type": "Bearer"}
        mock_token_store.return_value = mock_store_instance

        runner = CliRunner()
        result = runner.invoke(auth)

        assert result.exit_code == 0
        assert "Claude Code: ✓ Authenticated" in result.output


class TestClaudeCodeAuthCli:
    """Test the Claude Code auth CLI commands."""

    def test_claude_code_command_exists(self):
        """Test that the claude-code command is properly defined."""
        assert claude_code is not None
        assert claude_code.name == "claude-code"

    def test_claude_code_has_subcommands(self):
        """Test that claude-code has expected subcommands."""
        assert hasattr(claude_code, "commands")
        assert "login" in claude_code.commands
        assert "logout" in claude_code.commands
        assert "status" in claude_code.commands

    @mock.patch("gac.auth_cli.authenticate_and_save")
    @mock.patch("gac.auth_cli.TokenStore")
    @mock.patch("gac.auth_cli.setup_logging")
    def test_claude_code_login_success_no_existing_token(self, mock_setup_logging, mock_token_store, mock_auth):
        """Test successful Claude Code login when no token exists."""
        mock_store_instance = mock.Mock()
        mock_store_instance.get_token.return_value = None
        mock_token_store.return_value = mock_store_instance
        mock_auth.return_value = True

        runner = CliRunner()
        result = runner.invoke(auth, ["claude-code", "login"])

        assert result.exit_code == 0
        mock_store_instance.get_token.assert_called_with("claude-code")
        mock_auth.assert_called_once_with(quiet=False)

    @mock.patch("gac.auth_cli.authenticate_and_save")
    @mock.patch("gac.auth_cli.TokenStore")
    @mock.patch("gac.auth_cli.setup_logging")
    def test_claude_code_login_already_authenticated(self, mock_setup_logging, mock_token_store, mock_auth):
        """Test Claude Code login when already authenticated (declined re-auth)."""
        mock_store_instance = mock.Mock()
        mock_store_instance.get_token.return_value = {"access_token": "existing_token"}
        mock_token_store.return_value = mock_store_instance
        mock_auth.return_value = True

        runner = CliRunner()
        result = runner.invoke(auth, ["claude-code", "login"], input="n\n")

        assert result.exit_code == 0
        assert "Already authenticated" in result.output
        mock_auth.assert_not_called()

    @mock.patch("gac.auth_cli.authenticate_and_save")
    @mock.patch("gac.auth_cli.TokenStore")
    @mock.patch("gac.auth_cli.setup_logging")
    def test_claude_code_login_failure(self, mock_setup_logging, mock_token_store, mock_auth):
        """Test failed Claude Code login."""
        mock_store_instance = mock.Mock()
        mock_store_instance.get_token.return_value = None
        mock_token_store.return_value = mock_store_instance
        mock_auth.return_value = False

        runner = CliRunner()
        result = runner.invoke(auth, ["claude-code", "login"])

        assert result.exit_code != 0
        mock_auth.assert_called_once_with(quiet=False)

    @mock.patch("gac.auth_cli.authenticate_and_save")
    @mock.patch("gac.auth_cli.TokenStore")
    def test_claude_code_login_quiet_mode(self, mock_token_store, mock_auth):
        """Test Claude Code login in quiet mode."""
        mock_store_instance = mock.Mock()
        mock_store_instance.get_token.return_value = None
        mock_token_store.return_value = mock_store_instance
        mock_auth.return_value = True

        runner = CliRunner()
        result = runner.invoke(auth, ["claude-code", "login", "--quiet"])

        assert result.exit_code == 0
        mock_auth.assert_called_once_with(quiet=True)

    @mock.patch("gac.auth_cli.TokenStore")
    def test_claude_code_status_not_authenticated(self, mock_token_store):
        """Test Claude Code status when not authenticated."""
        mock_store_instance = mock.Mock()
        mock_store_instance.get_token.return_value = None
        mock_token_store.return_value = mock_store_instance

        runner = CliRunner()
        result = runner.invoke(auth, ["claude-code", "status"])

        assert result.exit_code == 0
        assert "Not authenticated" in result.output

    @mock.patch("gac.auth_cli.TokenStore")
    def test_claude_code_status_authenticated(self, mock_token_store):
        """Test Claude Code status when authenticated."""
        mock_store_instance = mock.Mock()
        mock_store_instance.get_token.return_value = {"access_token": "test_token"}
        mock_token_store.return_value = mock_store_instance

        runner = CliRunner()
        result = runner.invoke(auth, ["claude-code", "status"])

        assert result.exit_code == 0
        assert "Authenticated" in result.output

    @mock.patch("gac.auth_cli.remove_token")
    @mock.patch("gac.auth_cli.TokenStore")
    def test_claude_code_logout_not_authenticated(self, mock_token_store, mock_remove):
        """Test Claude Code logout when not authenticated."""
        mock_store_instance = mock.Mock()
        mock_store_instance.get_token.return_value = None
        mock_token_store.return_value = mock_store_instance

        runner = CliRunner()
        result = runner.invoke(auth, ["claude-code", "logout"])

        assert result.exit_code == 0
        assert "Not currently authenticated" in result.output
        mock_remove.assert_not_called()

    @mock.patch("gac.auth_cli.remove_token")
    @mock.patch("gac.auth_cli.TokenStore")
    def test_claude_code_logout_success(self, mock_token_store, mock_remove):
        """Test successful Claude Code logout."""
        mock_store_instance = mock.Mock()
        mock_store_instance.get_token.return_value = {"access_token": "existing_token"}
        mock_token_store.return_value = mock_store_instance
        mock_remove.return_value = None

        runner = CliRunner()
        result = runner.invoke(auth, ["claude-code", "logout"])

        assert result.exit_code == 0
        assert "Successfully logged out" in result.output
        mock_remove.assert_called_once()

    @mock.patch("gac.auth_cli.remove_token")
    @mock.patch("gac.auth_cli.TokenStore")
    def test_claude_code_logout_failure(self, mock_token_store, mock_remove):
        """Test Claude Code logout failure."""
        mock_store_instance = mock.Mock()
        mock_store_instance.get_token.return_value = {"access_token": "existing_token"}
        mock_token_store.return_value = mock_store_instance
        mock_remove.side_effect = Exception("Token removal failed")

        runner = CliRunner()
        result = runner.invoke(auth, ["claude-code", "logout"])

        assert result.exit_code != 0
        assert "Failed to remove" in result.output


class TestChatGPTAuthCli:
    """Test the ChatGPT auth CLI commands."""

    def test_chatgpt_command_exists(self):
        """Test that the chatgpt command is properly defined."""
        from gac.auth_cli import chatgpt

        assert chatgpt is not None
        assert chatgpt.name == "chatgpt"

    def test_chatgpt_has_subcommands(self):
        """Test that chatgpt has expected subcommands."""
        from gac.auth_cli import chatgpt

        assert hasattr(chatgpt, "commands")
        assert "login" in chatgpt.commands
        assert "logout" in chatgpt.commands
        assert "status" in chatgpt.commands

    @mock.patch("gac.auth_cli.chatgpt_authenticate_and_save")
    @mock.patch("gac.auth_cli.TokenStore")
    @mock.patch("gac.auth_cli.setup_logging")
    def test_chatgpt_login_success_no_existing_token(self, mock_setup_logging, mock_token_store, mock_auth):
        """Test successful ChatGPT login when no token exists."""
        mock_store_instance = mock.Mock()
        mock_store_instance.get_token.return_value = None
        mock_token_store.return_value = mock_store_instance
        mock_auth.return_value = True

        runner = CliRunner()
        result = runner.invoke(auth, ["chatgpt", "login"])

        assert result.exit_code == 0
        assert "ChatGPT authentication completed successfully" in result.output

    @mock.patch("gac.auth_cli.chatgpt_authenticate_and_save")
    @mock.patch("gac.auth_cli.TokenStore")
    @mock.patch("gac.auth_cli.setup_logging")
    def test_chatgpt_login_already_authenticated_decline(self, mock_setup_logging, mock_token_store, mock_auth):
        """Test ChatGPT login when already authenticated (decline re-auth)."""
        mock_store_instance = mock.Mock()
        mock_store_instance.get_token.return_value = {"access_token": "existing_token"}
        mock_token_store.return_value = mock_store_instance

        runner = CliRunner()
        result = runner.invoke(auth, ["chatgpt", "login"], input="n\n")

        assert result.exit_code == 0
        assert "Already authenticated" in result.output
        mock_auth.assert_not_called()

    @mock.patch("gac.auth_cli.chatgpt_authenticate_and_save")
    @mock.patch("gac.auth_cli.TokenStore")
    @mock.patch("gac.auth_cli.setup_logging")
    def test_chatgpt_login_failure(self, mock_setup_logging, mock_token_store, mock_auth):
        """Test failed ChatGPT login."""
        mock_store_instance = mock.Mock()
        mock_store_instance.get_token.return_value = None
        mock_token_store.return_value = mock_store_instance
        mock_auth.return_value = False

        runner = CliRunner()
        result = runner.invoke(auth, ["chatgpt", "login"])

        assert result.exit_code != 0
        assert "ChatGPT authentication failed" in result.output

    @mock.patch("gac.auth_cli.chatgpt_authenticate_and_save")
    @mock.patch("gac.auth_cli.TokenStore")
    def test_chatgpt_login_quiet_mode(self, mock_token_store, mock_auth):
        """Test ChatGPT login in quiet mode."""
        mock_store_instance = mock.Mock()
        mock_store_instance.get_token.return_value = None
        mock_token_store.return_value = mock_store_instance
        mock_auth.return_value = True

        runner = CliRunner()
        result = runner.invoke(auth, ["chatgpt", "login", "--quiet"])

        assert result.exit_code == 0
        mock_auth.assert_called_once_with(quiet=True)

    @mock.patch("gac.auth_cli.TokenStore")
    def test_chatgpt_status_not_authenticated(self, mock_token_store):
        """Test ChatGPT status when not authenticated."""
        mock_store_instance = mock.Mock()
        mock_store_instance.get_token.return_value = None
        mock_token_store.return_value = mock_store_instance

        runner = CliRunner()
        result = runner.invoke(auth, ["chatgpt", "status"])

        assert result.exit_code == 0
        assert "Not authenticated" in result.output

    @mock.patch("gac.auth_cli.chatgpt_is_token_expired", return_value=False)
    @mock.patch("gac.auth_cli.TokenStore")
    def test_chatgpt_status_authenticated(self, mock_token_store, mock_expired):
        """Test ChatGPT status when authenticated and not expired."""
        mock_store_instance = mock.Mock()
        mock_store_instance.get_token.return_value = {"access_token": "test_token"}
        mock_token_store.return_value = mock_store_instance

        runner = CliRunner()
        result = runner.invoke(auth, ["chatgpt", "status"])

        assert result.exit_code == 0
        assert "Authenticated" in result.output

    @mock.patch("gac.auth_cli.chatgpt_is_token_expired", return_value=True)
    @mock.patch("gac.auth_cli.TokenStore")
    def test_chatgpt_status_token_expired(self, mock_token_store, mock_expired):
        """Test ChatGPT status when token is expired."""
        mock_store_instance = mock.Mock()
        mock_store_instance.get_token.return_value = {"access_token": "test_token"}
        mock_token_store.return_value = mock_store_instance

        runner = CliRunner()
        result = runner.invoke(auth, ["chatgpt", "status"])

        assert result.exit_code == 0
        assert "Token expired" in result.output

    @mock.patch("gac.auth_cli.chatgpt_remove_token")
    @mock.patch("gac.auth_cli.TokenStore")
    def test_chatgpt_logout_not_authenticated(self, mock_token_store, mock_remove):
        """Test ChatGPT logout when not authenticated."""
        mock_store_instance = mock.Mock()
        mock_store_instance.get_token.return_value = None
        mock_token_store.return_value = mock_store_instance

        runner = CliRunner()
        result = runner.invoke(auth, ["chatgpt", "logout"])

        assert result.exit_code == 0
        assert "Not currently authenticated" in result.output
        mock_remove.assert_not_called()

    @mock.patch("gac.auth_cli.chatgpt_remove_token")
    @mock.patch("gac.auth_cli.TokenStore")
    def test_chatgpt_logout_success(self, mock_token_store, mock_remove):
        """Test successful ChatGPT logout."""
        mock_store_instance = mock.Mock()
        mock_store_instance.get_token.return_value = {"access_token": "existing_token"}
        mock_token_store.return_value = mock_store_instance
        mock_remove.return_value = None

        runner = CliRunner()
        result = runner.invoke(auth, ["chatgpt", "logout"])

        assert result.exit_code == 0
        assert "Successfully logged out" in result.output
        mock_remove.assert_called_once()

    @mock.patch("gac.auth_cli.chatgpt_remove_token")
    @mock.patch("gac.auth_cli.TokenStore")
    def test_chatgpt_logout_failure(self, mock_token_store, mock_remove):
        """Test ChatGPT logout failure."""
        mock_store_instance = mock.Mock()
        mock_store_instance.get_token.return_value = {"access_token": "existing_token"}
        mock_token_store.return_value = mock_store_instance
        mock_remove.side_effect = Exception("Token removal failed")

        runner = CliRunner()
        result = runner.invoke(auth, ["chatgpt", "logout"])

        assert result.exit_code != 0
        assert "Failed to remove" in result.output

    @mock.patch("gac.auth_cli.TokenStore")
    def test_auth_status_chatgpt_not_authenticated(self, mock_token_store):
        """Test auth status shows ChatGPT not authenticated."""
        mock_store_instance = mock.Mock()
        mock_store_instance.get_token.return_value = None
        mock_token_store.return_value = mock_store_instance

        runner = CliRunner()
        result = runner.invoke(auth)

        assert result.exit_code == 0
        assert "ChatGPT:      ✗ Not authenticated" in result.output

    @mock.patch("gac.auth_cli.TokenStore")
    def test_auth_status_chatgpt_authenticated(self, mock_token_store):
        """Test auth status shows ChatGPT authenticated."""

        def get_token_side_effect(provider):
            if provider == "chatgpt-oauth":
                return {"access_token": "chatgpt_token"}
            return None

        mock_store_instance = mock.Mock()
        mock_store_instance.get_token.side_effect = get_token_side_effect
        mock_token_store.return_value = mock_store_instance

        runner = CliRunner()
        result = runner.invoke(auth)

        assert result.exit_code == 0
        assert "ChatGPT:      ✓ Authenticated" in result.output


class TestCopilotAuth:
    """Tests for Copilot auth subcommands."""

    @mock.patch("gac.auth_cli.TokenStore")
    @mock.patch("gac.auth_cli.copilot_remove_token")
    def test_copilot_logout_not_authenticated(self, mock_remove, mock_token_store):
        mock_store_instance = mock.Mock()
        mock_store_instance.get_token.return_value = None
        mock_token_store.return_value = mock_store_instance

        runner = CliRunner()
        result = runner.invoke(auth, ["copilot", "logout"])
        assert result.exit_code == 0
        assert "Not currently authenticated" in result.output
        mock_remove.assert_not_called()

    @mock.patch("gac.auth_cli.TokenStore")
    @mock.patch("gac.auth_cli.copilot_remove_token")
    def test_copilot_logout_success(self, mock_remove, mock_token_store):
        mock_store_instance = mock.Mock()
        mock_store_instance.get_token.return_value = {"access_token": "token"}
        mock_token_store.return_value = mock_store_instance

        runner = CliRunner()
        result = runner.invoke(auth, ["copilot", "logout"])
        assert result.exit_code == 0
        assert "Successfully logged out" in result.output
        mock_remove.assert_called_once()

    @mock.patch("gac.auth_cli.TokenStore")
    @mock.patch("gac.auth_cli.copilot_remove_token", side_effect=Exception("boom"))
    def test_copilot_logout_failure(self, mock_remove, mock_token_store):
        mock_store_instance = mock.Mock()
        mock_store_instance.get_token.return_value = {"access_token": "token"}
        mock_token_store.return_value = mock_store_instance

        runner = CliRunner()
        result = runner.invoke(auth, ["copilot", "logout"])
        assert result.exit_code != 0

    @mock.patch("gac.auth_cli.TokenStore")
    @mock.patch("gac.auth_cli.copilot_refresh_token_if_expired", return_value=True)
    def test_copilot_status_authenticated(self, mock_refresh, mock_token_store):
        mock_store_instance = mock.Mock()
        mock_store_instance.get_token.return_value = {"access_token": "token"}
        mock_token_store.return_value = mock_store_instance

        runner = CliRunner()
        result = runner.invoke(auth, ["copilot", "status"])
        assert result.exit_code == 0
        assert "Authenticated" in result.output

    @mock.patch("gac.auth_cli.TokenStore")
    def test_copilot_status_not_authenticated(self, mock_token_store):
        mock_store_instance = mock.Mock()
        mock_store_instance.get_token.return_value = None
        mock_token_store.return_value = mock_store_instance

        runner = CliRunner()
        result = runner.invoke(auth, ["copilot", "status"])
        assert result.exit_code == 0
        assert "Not authenticated" in result.output

    @mock.patch("gac.auth_cli.TokenStore")
    @mock.patch("gac.auth_cli.copilot_refresh_token_if_expired", return_value=False)
    def test_copilot_status_expired(self, mock_refresh, mock_token_store):
        mock_store_instance = mock.Mock()
        mock_store_instance.get_token.return_value = {"access_token": "token"}
        mock_token_store.return_value = mock_store_instance

        runner = CliRunner()
        result = runner.invoke(auth, ["copilot", "status"])
        assert result.exit_code == 0
        assert "expired" in result.output.lower()

    @mock.patch("gac.auth_cli.setup_logging")
    @mock.patch("gac.auth_cli.TokenStore")
    @mock.patch("gac.auth_cli.copilot_authenticate_and_save", return_value=True)
    def test_copilot_login_success(self, mock_auth, mock_token_store, mock_logging):
        mock_store_instance = mock.Mock()
        mock_store_instance.get_token.return_value = None
        mock_token_store.return_value = mock_store_instance

        runner = CliRunner()
        result = runner.invoke(auth, ["copilot", "login"])
        assert result.exit_code == 0
        assert "successfully" in result.output.lower()

    @mock.patch("gac.auth_cli.setup_logging")
    @mock.patch("gac.auth_cli.TokenStore")
    @mock.patch("gac.auth_cli.copilot_authenticate_and_save", return_value=False)
    def test_copilot_login_failure(self, mock_auth, mock_token_store, mock_logging):
        mock_store_instance = mock.Mock()
        mock_store_instance.get_token.return_value = None
        mock_token_store.return_value = mock_store_instance

        runner = CliRunner()
        result = runner.invoke(auth, ["copilot", "login"])
        assert result.exit_code != 0

    @mock.patch("gac.auth_cli.setup_logging")
    @mock.patch("gac.auth_cli.TokenStore")
    @mock.patch("gac.auth_cli.copilot_authenticate_and_save", return_value=True)
    def test_copilot_login_already_authenticated_decline(self, mock_auth, mock_token_store, mock_logging):
        mock_store_instance = mock.Mock()
        mock_store_instance.get_token.return_value = {"access_token": "existing"}
        mock_token_store.return_value = mock_store_instance

        runner = CliRunner()
        result = runner.invoke(auth, ["copilot", "login"], input="n\n")
        assert result.exit_code == 0
        mock_auth.assert_not_called()
