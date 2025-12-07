"""Comprehensive tests for OAuth retry handling.

These tests mock all OAuth functionality to avoid actual authentication calls
during testing. All external OAuth providers and authentication flows are mocked.
"""

import os
import sys
from unittest.mock import MagicMock, patch

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

from gac.errors import AIError, ConfigError
from gac.oauth_retry import (
    OAUTH_PROVIDERS,
    OAuthProviderConfig,
    _attempt_reauth_and_retry,
    _claude_code_extra_check,
    _create_claude_code_authenticator,
    _create_qwen_authenticator,
    _find_oauth_provider,
    handle_oauth_retry,
)


class TestOAuthProviderConfig:
    """Test OAuth provider configuration dataclass."""

    def test_oauth_provider_config_creation(self):
        """Test creating provider config with all fields."""

        def mock_auth(quiet):
            return True

        def mock_check(error):
            return True

        config = OAuthProviderConfig(
            provider_prefix="test:",
            display_name="Test Provider",
            manual_auth_hint="Run 'test auth'",
            authenticate=mock_auth,
            extra_error_check=mock_check,
        )

        assert config.provider_prefix == "test:"
        assert config.display_name == "Test Provider"
        assert config.manual_auth_hint == "Run 'test auth'"
        assert config.authenticate == mock_auth
        assert config.extra_error_check == mock_check

    def test_oauth_provider_config_without_extra_check(self):
        """Test creating provider config without extra error check."""

        def mock_auth(quiet):
            return True

        config = OAuthProviderConfig(
            provider_prefix="test:",
            display_name="Test Provider",
            manual_auth_hint="Run 'test auth'",
            authenticate=mock_auth,
        )

        assert config.provider_prefix == "test:"
        assert config.display_name == "Test Provider"
        assert config.manual_auth_hint == "Run 'test auth'"
        assert config.authenticate == mock_auth
        assert config.extra_error_check is None


class TestClaudeCodeExtraCheck:
    """Test Claude Code specific error checking."""

    def test_claude_code_extra_check_expired(self):
        """Test detection of 'expired' in error message."""
        error = AIError("Token has expired for claude-code", "authentication")
        assert _claude_code_extra_check(error) is True

    def test_claude_code_extra_check_oauth(self):
        """Test detection of 'oauth' in error message."""
        error = AIError("OAuth authentication failed", "authentication")
        assert _claude_code_extra_check(error) is True

    def test_claude_code_extra_check_case_insensitive(self):
        """Test that error checking is case insensitive."""
        error = AIError("Token has EXPIRED", "authentication")
        assert _claude_code_extra_check(error) is True

        error = AIError("OAUTH failed", "authentication")
        assert _claude_code_extra_check(error) is True

    def test_claude_code_extra_check_no_match(self):
        """Test that non-matching errors return False."""
        error = AIError("Invalid API key", "authentication")
        assert _claude_code_extra_check(error) is False

    def test_claude_code_extra_check_empty_error(self):
        """Test empty error message returns False."""
        error = AIError("", "authentication")
        assert _claude_code_extra_check(error) is False


class TestCreateAuthenticators:
    """Test authenticator creation functions."""

    def test_create_claude_code_authenticator(self):
        """Test Claude Code authenticator creation."""
        # This just verifies the function can be called
        # The actual OAuth calls are mocked in integration tests
        authenticator = _create_claude_code_authenticator()
        assert callable(authenticator)

    def test_create_qwen_authenticator(self):
        """Test Qwen authenticator creation."""
        # This just verifies the function can be called
        # The actual OAuth calls are mocked in integration tests
        authenticator = _create_qwen_authenticator()
        assert callable(authenticator)


class TestFindOAuthProvider:
    """Test OAuth provider discovery logic."""

    def test_find_oauth_provider_claude_code_success(self):
        """Test finding Claude Code provider with matching model and error."""
        model = "claude-code:gpt-4"
        error = AIError("Token has expired", "authentication")

        provider = _find_oauth_provider(model, error)

        assert provider is not None
        assert provider.provider_prefix == "claude-code:"
        assert provider.display_name == "Claude Code"
        assert "Run 'gac model'" in provider.manual_auth_hint

    def test_find_oauth_provider_qwen_success(self):
        """Test finding Qwen provider with matching model and error."""
        model = "qwen:qwen-codet"
        error = AIError("Authentication failed", "authentication")

        provider = _find_oauth_provider(model, error)

        assert provider is not None
        assert provider.provider_prefix == "qwen:"
        assert provider.display_name == "Qwen"
        assert "Run 'gac auth qwen login'" in provider.manual_auth_hint

    def test_find_oauth_provider_claude_code_extra_check_fails(self):
        """Test Claude Code provider rejected when extra check fails."""
        model = "claude-code:gpt-4"
        error = AIError("Invalid API key format", "authentication")  # No 'expired' or 'oauth'

        provider = _find_oauth_provider(model, error)

        assert provider is None

    def test_find_oauth_provider_wrong_error_type(self):
        """Test that non-authentication errors return None."""
        model = "claude-code:gpt-4"
        error = AIError("Rate limit exceeded", "rate_limit")

        provider = _find_oauth_provider(model, error)

        assert provider is None

    def test_find_oauth_provider_unknown_model(self):
        """Test that unknown models return None."""
        model = "unknown-provider:gpt-4"
        error = AIError("Token has expired", "authentication")

        provider = _find_oauth_provider(model, error)

        assert provider is None

    def test_find_oauth_provider_empty_model(self):
        """Test that empty model returns None."""
        model = ""
        error = AIError("Token has expired", "authentication")

        provider = _find_oauth_provider(model, error)

        assert provider is None

    def test_find_oauth_provider_multiple_providers_check(self):
        """Test that provider matching prioritizes correctly."""
        # Test with claude-code model
        model = "claude-code:sonnet"
        error = AIError("OAuth token expired", "authentication")

        provider = _find_oauth_provider(model, error)
        assert provider is not None
        assert provider.provider_prefix == "claude-code:"


class TestAttemptReauthAndRetry:
    """Test re-authentication and retry logic."""

    @patch("gac.oauth_retry.console")
    def test_reauth_success_and_retry_success(self, mock_console):
        """Test successful re-authentication and successful retry."""
        # Create mock provider
        mock_auth = MagicMock(return_value=True)
        mock_retry = MagicMock(return_value=0)

        provider = OAuthProviderConfig(
            provider_prefix="test:",
            display_name="Test Provider",
            manual_auth_hint="Run 'test auth'",
            authenticate=mock_auth,
        )

        result = _attempt_reauth_and_retry(provider, quiet=False, retry_workflow=mock_retry)

        assert result == 0
        mock_auth.assert_called_once_with(False)
        mock_retry.assert_called_once()

        # Verify console output
        assert mock_console.print.call_count == 4  # Includes "Retrying commit..." message
        call_args = [call[0][0] for call in mock_console.print.call_args_list]
        assert "Test Provider OAuth token has expired" in call_args[0]
        assert "Starting automatic re-authentication" in call_args[1]
        assert "Re-authentication successful" in call_args[2]
        assert "Retrying commit" in call_args[3]

    @patch("gac.oauth_retry.console")
    def test_reauth_success_and_retry_failure(self, mock_console):
        """Test successful re-authentication but retry fails."""
        mock_auth = MagicMock(return_value=True)
        mock_retry = MagicMock(return_value=1)  # Retry fails

        provider = OAuthProviderConfig(
            provider_prefix="test:",
            display_name="Test Provider",
            manual_auth_hint="Run 'test auth'",
            authenticate=mock_auth,
        )

        result = _attempt_reauth_and_retry(provider, quiet=False, retry_workflow=mock_retry)

        assert result == 1
        mock_auth.assert_called_once_with(False)
        mock_retry.assert_called_once()

    @patch("gac.oauth_retry.console")
    def test_reauth_failure(self, mock_console):
        """Test failed re-authentication."""
        mock_auth = MagicMock(return_value=False)
        mock_retry = MagicMock()

        provider = OAuthProviderConfig(
            provider_prefix="test:",
            display_name="Test Provider",
            manual_auth_hint="Run 'test auth'",
            authenticate=mock_auth,
        )

        result = _attempt_reauth_and_retry(provider, quiet=False, retry_workflow=mock_retry)

        assert result == 1
        mock_auth.assert_called_once_with(False)
        mock_retry.assert_not_called()

        # Verify console output includes manual hint
        call_args = [call[0][0] for call in mock_console.print.call_args_list]
        assert any("Run 'test auth'" in arg for arg in call_args)

    @patch("gac.oauth_retry.console")
    def test_reauth_with_auth_error(self, mock_console):
        """Test re-authentication throws authentication error."""
        mock_auth = MagicMock(side_effect=AIError("Auth failed", "authentication"))
        mock_retry = MagicMock()

        provider = OAuthProviderConfig(
            provider_prefix="test:",
            display_name="Test Provider",
            manual_auth_hint="Run 'test auth'",
            authenticate=mock_auth,
        )

        result = _attempt_reauth_and_retry(provider, quiet=False, retry_workflow=mock_retry)

        assert result == 1
        mock_auth.assert_called_once_with(False)
        mock_retry.assert_not_called()

        # Verify console output includes error message and manual hint
        call_args = [call[0][0] for call in mock_console.print.call_args_list]
        assert any("Re-authentication error: Auth failed" in arg for arg in call_args)
        assert any("Run 'test auth'" in arg for arg in call_args)

    @patch("gac.oauth_retry.console")
    def test_reauth_with_config_error(self, mock_console):
        """Test re-authentication throws config error."""
        from gac.errors import ConfigError

        mock_auth = MagicMock(side_effect=ConfigError("Invalid config"))
        mock_retry = MagicMock()

        provider = OAuthProviderConfig(
            provider_prefix="test:",
            display_name="Test Provider",
            manual_auth_hint="Run 'test auth'",
            authenticate=mock_auth,
        )

        result = _attempt_reauth_and_retry(provider, quiet=False, retry_workflow=mock_retry)

        assert result == 1
        mock_auth.assert_called_once_with(False)
        mock_retry.assert_not_called()

    @patch("gac.oauth_retry.console")
    def test_reauth_with_os_error(self, mock_console):
        """Test re-authentication throws OS error."""
        mock_auth = MagicMock(side_effect=OSError("Network error"))
        mock_retry = MagicMock()

        provider = OAuthProviderConfig(
            provider_prefix="test:",
            display_name="Test Provider",
            manual_auth_hint="Run 'test auth'",
            authenticate=mock_auth,
        )

        result = _attempt_reauth_and_retry(provider, quiet=False, retry_workflow=mock_retry)

        assert result == 1
        mock_auth.assert_called_once_with(False)
        mock_retry.assert_not_called()

    @patch("gac.oauth_retry.console")
    def test_reauth_quiet_mode(self, mock_console):
        """Test re-authentication in quiet mode."""
        mock_auth = MagicMock(return_value=True)
        mock_retry = MagicMock(return_value=0)

        provider = OAuthProviderConfig(
            provider_prefix="test:",
            display_name="Test Provider",
            manual_auth_hint="Run 'test auth'",
            authenticate=mock_auth,
        )

        result = _attempt_reauth_and_retry(provider, quiet=True, retry_workflow=mock_retry)

        assert result == 0
        mock_auth.assert_called_once_with(True)  # Called with quiet=True


class TestHandleOAuthRetry:
    """Test main OAuth retry handler function."""

    @patch("gac.oauth_retry.console")
    @patch("gac.oauth_retry._find_oauth_provider")
    @patch("gac.oauth_retry.logger.error")
    def test_handle_oauth_retry_no_provider_found(self, mock_log_error, mock_find_provider, mock_console):
        """Test when no matching OAuth provider is found."""
        mock_find_provider.return_value = None
        mock_ctx = MagicMock()
        mock_ctx.model = "unknown:model"
        error = AIError("Auth failed", "authentication")

        result = handle_oauth_retry(error, mock_ctx)

        assert result == 1
        mock_log_error.assert_called_once_with(str(error))
        mock_find_provider.assert_called_once_with(mock_ctx.model, error)

        # Verify console shows generic error
        mock_console.print.assert_called_once()
        call_arg = mock_console.print.call_args[0][0]
        assert "Failed to generate commit message" in call_arg
        assert "Auth failed" in call_arg

    @patch("gac.oauth_retry._attempt_reauth_and_retry")
    @patch("gac.oauth_retry._find_oauth_provider")
    @patch("gac.oauth_retry.logger.error")
    def test_handle_oauth_retry_provider_found(self, mock_log_error, mock_find_provider, mock_attempt_retry):
        """Test when OAuth provider is found and retry attempted."""
        # Mock provider
        mock_provider = MagicMock()
        mock_provider.provider_prefix = "test:"
        mock_provider.display_name = "Test Provider"
        mock_provider.manual_auth_hint = "Run 'test auth'"

        mock_find_provider.return_value = mock_provider
        mock_attempt_retry.return_value = 0  # Success

        mock_ctx = MagicMock()
        mock_ctx.model = "test:model"
        mock_ctx.quiet = False
        error = AIError("Token expired", "authentication")

        result = handle_oauth_retry(error, mock_ctx)

        assert result == 0
        mock_log_error.assert_called_once_with(str(error))
        mock_find_provider.assert_called_once_with(mock_ctx.model, error)
        mock_attempt_retry.assert_called_once()

        # Verify the retry was called with correct parameters
        call_args = mock_attempt_retry.call_args[0]
        assert call_args[0] == mock_provider  # provider
        assert not call_args[1]  # quiet
        assert callable(call_args[2])  # retry_workflow

    @patch("gac.oauth_retry._attempt_reauth_and_retry")
    @patch("gac.oauth_retry._find_oauth_provider")
    @patch("gac.oauth_retry.logger.error")
    def test_handle_oauth_retry_quiet_mode(self, mock_log_error, mock_find_provider, mock_attempt_retry):
        """Test OAuth retry in quiet mode."""
        mock_provider = MagicMock()
        mock_find_provider.return_value = mock_provider
        mock_attempt_retry.return_value = 1  # Failure

        mock_ctx = MagicMock()
        mock_ctx.model = "test:model"
        mock_ctx.quiet = True  # Quiet mode
        error = AIError("Token expired", "authentication")

        result = handle_oauth_retry(error, mock_ctx)

        assert result == 1
        call_args = mock_attempt_retry.call_args[0]
        assert call_args[1]  # quiet=True

    @patch("gac.main._execute_single_commit_workflow")
    @patch("gac.oauth_retry._attempt_reauth_and_retry")
    @patch("gac.oauth_retry._find_oauth_provider")
    @patch("gac.oauth_retry.logger.error")
    def test_handle_oauth_retry_workflow_execution(
        self, mock_log_error, mock_find_provider, mock_attempt_retry, mock_execute_workflow
    ):
        """Test that the retry workflow executes correctly."""
        mock_provider = MagicMock()
        mock_find_provider.return_value = mock_provider
        mock_attempt_retry.return_value = 0
        mock_execute_workflow.return_value = 0

        mock_ctx = MagicMock()
        mock_ctx.model = "test:model"
        mock_ctx.quiet = False
        error = AIError("Token expired", "authentication")

        result = handle_oauth_retry(error, mock_ctx)

        assert result == 0

        # Get the retry_workflow function that was passed to _attempt_reauth_and_retry
        retry_workflow = mock_attempt_retry.call_args[0][2]
        assert callable(retry_workflow)

        # Test the retry_workflow function
        retry_result = retry_workflow()
        assert retry_result == 0
        mock_execute_workflow.assert_called_once_with(mock_ctx)


class TestOAuthProvidersConstant:
    """Test the OAUTH_PROVIDERS constant list."""

    def test_oauth_providers_list_structure(self):
        """Test that OAUTH_PROVIDERS has correct structure."""
        assert isinstance(OAUTH_PROVIDERS, list)
        assert len(OAUTH_PROVIDERS) == 2  # Claude Code and Qwen

        for provider in OAUTH_PROVIDERS:
            assert isinstance(provider, OAuthProviderConfig)
            assert provider.provider_prefix
            assert provider.display_name
            assert provider.manual_auth_hint
            assert callable(provider.authenticate)

    def test_claude_code_provider_config(self):
        """Test Claude Code provider configuration."""
        claude_provider = OAUTH_PROVIDERS[0]

        assert claude_provider.provider_prefix == "claude-code:"
        assert claude_provider.display_name == "Claude Code"
        assert "Run 'gac model'" in claude_provider.manual_auth_hint
        assert claude_provider.extra_error_check is not None
        assert callable(claude_provider.authenticate)

    def test_qwen_provider_config(self):
        """Test Qwen provider configuration."""
        qwen_provider = OAUTH_PROVIDERS[1]

        assert qwen_provider.provider_prefix == "qwen:"
        assert qwen_provider.display_name == "Qwen"
        assert "Run 'gac auth qwen login'" in qwen_provider.manual_auth_hint
        assert qwen_provider.extra_error_check is None
        assert callable(qwen_provider.authenticate)


class TestOAuthRetryIntegration:
    """Integration tests for OAuth retry functionality."""

    @patch("gac.oauth_retry.console")
    @patch("gac.oauth_retry._find_oauth_provider")
    @patch("gac.oauth_retry.logger.error")
    def test_full_retry_flow_success(self, mock_log_error, mock_find_provider, mock_console):
        """Test complete retry flow from start to finish."""
        # Mock provider that successfully authenticates and retries
        mock_provider = MagicMock()
        mock_provider.provider_prefix = "claude-code:"
        mock_provider.display_name = "Claude Code"
        mock_provider.manual_auth_hint = "Run 'gac model'"
        mock_provider.authenticate.return_value = True

        mock_find_provider.return_value = mock_provider

        mock_ctx = MagicMock()
        mock_ctx.model = "claude-code:gpt-4"
        mock_ctx.quiet = False
        error = AIError("OAuth token has expired", "authentication")

        # Mock the workflow execution
        with patch("gac.main._execute_single_commit_workflow", return_value=0):
            result = handle_oauth_retry(error, mock_ctx)

        assert result == 0
        mock_find_provider.assert_called_once_with("claude-code:gpt-4", error)

    @patch("gac.oauth_retry.console")
    @patch("gac.oauth_retry._find_oauth_provider")
    @patch("gac.oauth_retry.logger.error")
    def test_full_retry_flow_auth_failure(self, mock_log_error, mock_find_provider, mock_console):
        """Test complete retry flow where authentication fails."""
        mock_provider = MagicMock()
        mock_provider.provider_prefix = "qwen:"
        mock_provider.display_name = "Qwen"
        mock_provider.manual_auth_hint = "Run 'gac auth qwen login'"
        mock_provider.authenticate.return_value = False  # Auth fails

        mock_find_provider.return_value = mock_provider

        mock_ctx = MagicMock()
        mock_ctx.model = "qwen:qwen-codet"
        mock_ctx.quiet = False
        error = AIError("Authentication failed", "authentication")

        result = handle_oauth_retry(error, mock_ctx)

        assert result == 1
        mock_provider.authenticate.assert_called_once_with(False)

    @patch("gac.oauth_retry.console")
    def test_reauth_and_retry_with_various_quiet_settings(self, mock_console):
        """Test re-authentication with different quiet settings."""
        mock_retry = MagicMock(return_value=0)

        provider = OAuthProviderConfig(
            provider_prefix="test:",
            display_name="Test Provider",
            manual_auth_hint="Run 'test auth'",
            authenticate=lambda quiet: True,
        )

        # Test loud mode
        result_loud = _attempt_reauth_and_retry(provider, quiet=False, retry_workflow=mock_retry)
        assert result_loud == 0

        mock_console.reset_mock()
        mock_retry.reset_mock()

        # Test quiet mode
        result_quiet = _attempt_reauth_and_retry(provider, quiet=True, retry_workflow=mock_retry)
        assert result_quiet == 0

    def test_error_edge_cases(self):
        """Test various error edge cases."""
        # Test None error
        with pytest.raises(AttributeError):
            _find_oauth_provider("claude-code:gpt-4", None)

        # Test empty error message
        error = AIError("", "authentication")
        provider = _find_oauth_provider("claude-code:gpt-4", error)
        # Should still find provider if error_type matches
        # But claude_code_extra_check should reject empty message
        assert provider is None

    @patch("gac.oauth_retry.console")
    def test_provider_authentication_various_errors(self, mock_console):
        """Test provider authentication with various exception types."""
        test_cases = [
            AIError("Auth failed", "authentication"),
            ConfigError("Config invalid"),
            OSError("Network down"),
        ]

        for test_error in test_cases:
            mock_console.reset_mock()

            mock_auth = MagicMock(side_effect=test_error)
            mock_retry = MagicMock()

            provider = OAuthProviderConfig(
                provider_prefix="test:",
                display_name="Test Provider",
                manual_auth_hint="Run 'test auth'",
                authenticate=mock_auth,
            )

            result = _attempt_reauth_and_retry(provider, quiet=False, retry_workflow=mock_retry)

            assert result == 1
            mock_retry.assert_not_called()

            # Verify error is displayed and manual hint is shown
            call_args = [str(call[0][0]) for call in mock_console.print.call_args_list]
            assert any("Re-authentication error" in arg for arg in call_args)
            assert any("Run 'test auth'" in arg for arg in call_args)
