"""Additional tests for ai_utils.py to increase coverage from 81% to 95%+."""

import os
from unittest.mock import MagicMock, patch

import pytest

from gac.ai_utils import generate_with_retries
from gac.errors import AIError
from gac.providers import SUPPORTED_PROVIDERS


class TestAIUtilsMissingCoverage:
    """Tests for uncovered lines in ai_utils.py."""

    @patch("gac.ai_utils.TokenStore")
    @patch("gac.ai_utils.refresh_token_if_expired")
    def test_claude_code_token_refresh_failure(self, mock_refresh, mock_token_store):
        """Test Claude Code token refresh failure path."""
        mock_refresh.return_value = False
        mock_token_instance = MagicMock()
        mock_token_store.return_value = mock_token_instance

        provider_func = MagicMock(return_value="success")
        provider_funcs = {"claude-code": provider_func}

        with pytest.raises(AIError) as exc_info:
            generate_with_retries(
                provider_funcs=provider_funcs,
                model="claude-code:claude-3-sonnet-20240229",
                messages=[{"role": "user", "content": "test"}],
                temperature=0.7,
                max_tokens=1000,
                max_retries=1,
                quiet=True,
            )

        assert "Please authenticate with 'gac auth claude-code login'" in str(exc_info.value)

    @patch("gac.ai_utils.TokenStore")
    @patch("gac.ai_utils.refresh_token_if_expired", return_value=True)
    def test_claude_code_token_missing_access_token(self, mock_refresh, mock_token_store):
        """Test Claude Code token missing access token."""
        mock_token_instance = MagicMock()
        mock_token_instance.get_token.return_value = {}  # No access_token
        mock_token_store.return_value = mock_token_instance

        provider_func = MagicMock(return_value="success")
        provider_funcs = {"claude-code": provider_func}

        with pytest.raises(AIError) as exc_info:
            generate_with_retries(
                provider_funcs=provider_funcs,
                model="claude-code:claude-3-sonnet-20240229",
                messages=[{"role": "user", "content": "test"}],
                temperature=0.7,
                max_tokens=1000,
                max_retries=1,
                quiet=True,
            )

        assert "Please authenticate with 'gac auth claude-code login'" in str(exc_info.value)

    @patch("gac.ai_utils.QwenOAuthProvider")
    def test_qwen_auth_flow_success(self, mock_oauth_provider):
        """Test Qwen OAuth flow success path."""
        mock_provider_instance = MagicMock()
        mock_provider_instance.get_token.return_value = "valid_token"
        mock_oauth_provider.return_value = mock_provider_instance

        provider_func = MagicMock(return_value="success")
        provider_funcs = {"qwen": provider_func}

        result = generate_with_retries(
            provider_funcs=provider_funcs,
            model="qwen:qwen-max",
            messages=[{"role": "user", "content": "test"}],
            temperature=0.7,
            max_tokens=1000,
            max_retries=1,
            quiet=True,
        )

        assert result == "success"
        mock_provider_instance.get_token.assert_called()

    @patch("gac.ai_utils.QwenOAuthProvider")
    def test_qwen_auth_flow_initiate_success(self, mock_oauth_provider):
        """Test Qwen OAuth flow that needs to initiate auth."""
        mock_provider_instance = MagicMock()
        mock_provider_instance.get_token.side_effect = [None, "valid_token"]
        mock_oauth_provider.return_value = mock_provider_instance

        provider_func = MagicMock(return_value="success")
        provider_funcs = {"qwen": provider_func}

        result = generate_with_retries(
            provider_funcs=provider_funcs,
            model="qwen:qwen-max",
            messages=[{"role": "user", "content": "test"}],
            temperature=0.7,
            max_tokens=1000,
            max_retries=1,
            quiet=True,
        )

        assert result == "success"
        mock_provider_instance.initiate_auth.assert_called_once_with(open_browser=True)
        assert mock_provider_instance.get_token.call_count == 2

    @patch("gac.ai_utils.QwenOAuthProvider")
    def test_qwen_auth_flow_ai_error(self, mock_oauth_provider):
        """Test Qwen OAuth flow with AIError during initiation."""
        mock_provider_instance = MagicMock()
        mock_provider_instance.get_token.return_value = None
        mock_provider_instance.initiate_auth.side_effect = AIError.authentication_error("Auth failed")
        mock_oauth_provider.return_value = mock_provider_instance

        provider_func = MagicMock()
        provider_funcs = {"qwen": provider_func}

        with pytest.raises(AIError) as exc_info:
            generate_with_retries(
                provider_funcs=provider_funcs,
                model="qwen:qwen-max",
                messages=[{"role": "user", "content": "test"}],
                temperature=0.7,
                max_tokens=1000,
                max_retries=1,
                quiet=True,
            )

        assert "Auth failed" in str(exc_info.value)

    @patch("gac.ai_utils.QwenOAuthProvider")
    def test_qwen_auth_flow_connection_error(self, mock_oauth_provider):
        """Test Qwen OAuth flow with connection error."""
        mock_provider_instance = MagicMock()
        mock_provider_instance.get_token.return_value = None
        mock_provider_instance.initiate_auth.side_effect = ConnectionError("Network error")
        mock_oauth_provider.return_value = mock_provider_instance

        provider_func = MagicMock()
        provider_funcs = {"qwen": provider_func}

        with pytest.raises(AIError) as exc_info:
            generate_with_retries(
                provider_funcs=provider_funcs,
                model="qwen:qwen-max",
                messages=[{"role": "user", "content": "test"}],
                temperature=0.7,
                max_tokens=1000,
                max_retries=1,
                quiet=True,
            )

        assert "Network error" in str(exc_info.value)
        assert "Run 'gac auth qwen login' to authenticate manually" in str(exc_info.value)

    def test_invalid_model_format(self):
        """Test invalid model format error path."""
        provider_func = MagicMock(return_value="success")
        provider_funcs = {"openai": provider_func}

        with pytest.raises(AIError) as exc_info:
            generate_with_retries(
                provider_funcs=provider_funcs,
                model="invalid-format",  # Missing colon
                messages=[{"role": "user", "content": "test"}],
                temperature=0.7,
                max_tokens=1000,
                max_retries=1,
                quiet=True,
            )

        assert "Expected 'provider:model'" in str(exc_info.value)

    def test_unsupported_provider(self):
        """Test unsupported provider error path."""
        provider_func = MagicMock(return_value="success")
        provider_funcs = {"fake-provider": provider_func}

        with pytest.raises(AIError) as exc_info:
            generate_with_retries(
                provider_funcs=provider_funcs,
                model="fake-provider:model",
                messages=[{"role": "user", "content": "test"}],
                temperature=0.7,
                max_tokens=1000,
                max_retries=1,
                quiet=True,
            )

        assert "Unsupported provider" in str(exc_info.value)
        assert str(SUPPORTED_PROVIDERS) in str(exc_info.value)

    @patch("gac.ai_utils.TokenStore")
    @patch("gac.ai_utils.refresh_token_if_expired")
    def test_claude_code_token_set_environment(self, mock_refresh, mock_token_store):
        """Test Claude Code token sets environment variable."""
        mock_refresh.return_value = True
        mock_token_instance = MagicMock()
        mock_token_instance.get_token.return_value = {"access_token": "test_token_123"}
        mock_token_store.return_value = mock_token_instance

        # Clear any existing environment variable
        if "CLAUDE_CODE_ACCESS_TOKEN" in os.environ:
            del os.environ["CLAUDE_CODE_ACCESS_TOKEN"]

        provider_func = MagicMock(return_value="success")
        provider_funcs = {"claude-code": provider_func}

        try:
            result = generate_with_retries(
                provider_funcs=provider_funcs,
                model="claude-code:claude-3-sonnet-20240229",
                messages=[{"role": "user", "content": "test"}],
                temperature=0.7,
                max_tokens=1000,
                max_retries=1,
                quiet=True,
            )

            assert result == "success"
            assert os.environ.get("CLAUDE_CODE_ACCESS_TOKEN") == "test_token_123"
        finally:
            # Clean up environment variable
            if "CLAUDE_CODE_ACCESS_TOKEN" in os.environ:
                del os.environ["CLAUDE_CODE_ACCESS_TOKEN"]
