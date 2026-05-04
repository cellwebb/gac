"""Tests for ChatGPT OAuth public flow functions (perform_oauth_flow, authenticate_and_save)."""

from unittest.mock import MagicMock, patch

from gac.oauth.chatgpt import authenticate_and_save, perform_oauth_flow


def _mock_server(exit_code=0):
    """Create a mock OAuth server."""
    mock_server = MagicMock()
    mock_server.exit_code = exit_code
    mock_server.redirect_uri = "http://localhost:1455/callback"
    mock_server.auth_url.return_value = "https://auth.openai.com/oauth/authorize?test=1"
    return mock_server


class TestPerformOAuthFlow:
    """Test perform_oauth_flow function."""

    @patch("gac.oauth.chatgpt.load_stored_tokens", return_value={"access_token": "new"})
    @patch("gac.oauth.chatgpt.webbrowser.open")
    @patch("gac.oauth.chatgpt.time.sleep")
    @patch("gac.oauth.chatgpt._OAuthServer")
    @patch("gac.oauth.chatgpt.load_stored_token", return_value={"access_token": "existing"})
    def test_existing_token_quiet_mode(
        self, mock_load_token, mock_server_cls, mock_sleep, mock_webbrowser, mock_load_tokens
    ):
        """In quiet mode, don't warn about existing tokens."""
        mock_server_cls.return_value = _mock_server(exit_code=0)

        # Mock threading by making the Thread constructor a no-op
        with patch("threading.Thread") as MockThread:
            mock_thread = MagicMock()
            MockThread.return_value = mock_thread

            result = perform_oauth_flow(quiet=True)

        assert result == {"access_token": "new"}

    @patch("gac.oauth.chatgpt.load_stored_tokens", return_value={"access_token": "new"})
    @patch("gac.oauth.chatgpt.webbrowser.open")
    @patch("gac.oauth.chatgpt.time.sleep")
    @patch("gac.oauth.chatgpt._OAuthServer")
    @patch("gac.oauth.chatgpt.load_stored_token", return_value={"access_token": "existing"})
    def test_existing_token_verbose_mode(
        self, mock_load_token, mock_server_cls, mock_sleep, mock_webbrowser, mock_load_tokens, capsys
    ):
        """In verbose mode, warn about existing tokens."""
        mock_server_cls.return_value = _mock_server(exit_code=0)

        with patch("threading.Thread") as MockThread:
            mock_thread = MagicMock()
            MockThread.return_value = mock_thread

            result = perform_oauth_flow(quiet=False)

        assert result == {"access_token": "new"}
        assert "Existing ChatGPT OAuth tokens will be overwritten" in capsys.readouterr().out

    def test_server_os_error_quiet(self):
        """When server can't start, return None (quiet)."""
        with patch("gac.oauth.chatgpt._OAuthServer", side_effect=OSError("port in use")):
            result = perform_oauth_flow(quiet=True)
        assert result is None

    def test_server_os_error_verbose(self, capsys):
        """When server can't start, show error (verbose)."""
        with patch("gac.oauth.chatgpt._OAuthServer", side_effect=OSError("port in use")):
            result = perform_oauth_flow(quiet=False)
        assert result is None
        output = capsys.readouterr().out
        assert "Could not start OAuth server" in output

    @patch("gac.oauth.chatgpt.load_stored_tokens", return_value={"access_token": "new"})
    @patch("gac.oauth.chatgpt.webbrowser.open", side_effect=Exception("no browser"))
    @patch("gac.oauth.chatgpt.time.sleep")
    @patch("gac.oauth.chatgpt._OAuthServer")
    def test_webbrowser_open_failure_quiet(self, mock_server_cls, mock_sleep, mock_webbrowser, mock_load_tokens):
        """When browser can't open, continue gracefully (quiet)."""
        mock_server_cls.return_value = _mock_server(exit_code=0)

        with patch("threading.Thread") as MockThread:
            MockThread.return_value = MagicMock()
            result = perform_oauth_flow(quiet=True)

        assert result == {"access_token": "new"}

    @patch("gac.oauth.chatgpt.load_stored_tokens", return_value={"access_token": "new"})
    @patch("gac.oauth.chatgpt.webbrowser.open", side_effect=Exception("no browser"))
    @patch("gac.oauth.chatgpt.time.sleep")
    @patch("gac.oauth.chatgpt._OAuthServer")
    def test_webbrowser_open_failure_verbose(
        self, mock_server_cls, mock_sleep, mock_webbrowser, mock_load_tokens, capsys
    ):
        """When browser can't open, show warning (verbose)."""
        mock_server_cls.return_value = _mock_server(exit_code=0)

        with patch("threading.Thread") as MockThread:
            MockThread.return_value = MagicMock()
            result = perform_oauth_flow(quiet=False)

        assert result == {"access_token": "new"}
        output = capsys.readouterr().out
        assert "Failed to open browser" in output

    @patch("gac.oauth.chatgpt.webbrowser.open")
    @patch("gac.oauth.chatgpt.time.sleep")
    @patch("gac.oauth.chatgpt._OAuthServer")
    def test_oauth_flow_timeout(self, mock_server_cls, mock_sleep, mock_webbrowser, capsys):
        """When server times out (exit_code != 0), return None."""
        mock_server_cls.return_value = _mock_server(exit_code=1)

        with patch("threading.Thread") as MockThread:
            MockThread.return_value = MagicMock()
            result = perform_oauth_flow(quiet=False)

        assert result is None
        output = capsys.readouterr().out
        assert "authentication failed or timed out" in output

    @patch("gac.oauth.chatgpt.webbrowser.open")
    @patch("gac.oauth.chatgpt.time.sleep")
    @patch("gac.oauth.chatgpt._OAuthServer")
    def test_oauth_flow_timeout_quiet(self, mock_server_cls, mock_sleep, mock_webbrowser):
        """When server times out (exit_code != 0), return None (quiet)."""
        mock_server_cls.return_value = _mock_server(exit_code=1)

        with patch("threading.Thread") as MockThread:
            MockThread.return_value = MagicMock()
            result = perform_oauth_flow(quiet=True)

        assert result is None

    @patch("gac.oauth.chatgpt.load_stored_tokens", return_value=None)
    @patch("gac.oauth.chatgpt.webbrowser.open")
    @patch("gac.oauth.chatgpt.time.sleep")
    @patch("gac.oauth.chatgpt._OAuthServer")
    def test_tokens_not_loadable_after_flow(
        self, mock_server_cls, mock_sleep, mock_webbrowser, mock_load_tokens, capsys
    ):
        """When server succeeds but tokens can't be loaded, return None."""
        mock_server_cls.return_value = _mock_server(exit_code=0)

        with patch("threading.Thread") as MockThread:
            MockThread.return_value = MagicMock()
            result = perform_oauth_flow(quiet=False)

        assert result is None
        output = capsys.readouterr().out
        assert "Tokens saved during OAuth flow could not be loaded" in output

    @patch("gac.oauth.chatgpt.load_stored_tokens", return_value={"access_token": "new"})
    @patch("gac.oauth.chatgpt.webbrowser.open")
    @patch("gac.oauth.chatgpt.time.sleep")
    @patch("gac.oauth.chatgpt._OAuthServer")
    def test_successful_flow_verbose(self, mock_server_cls, mock_sleep, mock_webbrowser, mock_load_tokens, capsys):
        """Successful flow shows success message."""
        mock_server_cls.return_value = _mock_server(exit_code=0)

        with patch("threading.Thread") as MockThread:
            MockThread.return_value = MagicMock()
            result = perform_oauth_flow(quiet=False)

        assert result == {"access_token": "new"}
        output = capsys.readouterr().out
        assert "ChatGPT OAuth authentication successful" in output


class TestAuthenticateAndSave:
    """Test authenticate_and_save function."""

    def test_success_verbose(self, capsys):
        """Successful auth and save."""
        with patch("gac.oauth.chatgpt.perform_oauth_flow", return_value={"access_token": "new_tok"}):
            result = authenticate_and_save(quiet=False)

        assert result is True
        output = capsys.readouterr().out
        assert "Access token saved" in output

    def test_success_quiet(self):
        """Successful auth and save (quiet)."""
        with patch("gac.oauth.chatgpt.perform_oauth_flow", return_value={"access_token": "new_tok"}):
            result = authenticate_and_save(quiet=True)

        assert result is True

    def test_no_tokens_returned(self, capsys):
        """When perform_oauth_flow returns None, return False."""
        with patch("gac.oauth.chatgpt.perform_oauth_flow", return_value=None):
            result = authenticate_and_save(quiet=False)

        assert result is False

    def test_no_access_token_in_response(self, capsys):
        """When tokens returned but no access_token, return False."""
        with patch("gac.oauth.chatgpt.perform_oauth_flow", return_value={"refresh_token": "rt"}):
            result = authenticate_and_save(quiet=False)

        assert result is False
        output = capsys.readouterr().out
        assert "No access token returned" in output

    def test_no_access_token_quiet(self):
        """When tokens returned but no access_token, return False (quiet)."""
        with patch("gac.oauth.chatgpt.perform_oauth_flow", return_value={"refresh_token": "rt"}):
            result = authenticate_and_save(quiet=True)

        assert result is False
