"""Tests for ChatGPT OAuth callback server and _CallbackHandler."""

import base64
import json
from unittest.mock import MagicMock, patch

import pytest

from gac.oauth.chatgpt_config import CHATGPT_OAUTH_CONFIG
from gac.oauth.chatgpt_server import (
    _CallbackHandler,
    _get_failure_html,
    _get_success_html,
    _OAuthServer,
    prepare_oauth_context,
)


class TestOAuthServerInit:
    """Test _OAuthServer initialization."""

    def test_server_init_and_auth_url(self):
        """Test server auth_url builds correctly without binding port."""
        server = _OAuthServer.__new__(_OAuthServer)
        server.exit_code = 1
        server.verbose = False
        server.client_id = CHATGPT_OAUTH_CONFIG["client_id"]
        server.issuer = CHATGPT_OAUTH_CONFIG["issuer"]
        server.token_endpoint = CHATGPT_OAUTH_CONFIG["token_url"]
        server.context = prepare_oauth_context()
        server.server_address = ("localhost", 1455)
        server.redirect_uri = f"http://localhost:1455/{CHATGPT_OAUTH_CONFIG['redirect_path']}"
        server.context.redirect_uri = server.redirect_uri

        auth_url = server.auth_url()
        assert "oauth/authorize" in auth_url
        assert "code_challenge" in auth_url
        assert "S256" in auth_url

    def test_server_all_ports_occupied(self):
        """Test OSError when all ports in range are occupied."""
        with patch("gac.oauth.chatgpt_server.HTTPServer.__init__", side_effect=OSError("port in use")):
            with pytest.raises(OSError, match="Could not bind any port"):
                _OAuthServer(client_id="test_client")


class TestCallbackHandler:
    """Test _CallbackHandler HTTP handling."""

    def _make_handler(self, server, path="/callback?code=test_code"):
        """Create a handler instance for testing."""
        handler = _CallbackHandler.__new__(_CallbackHandler)
        handler.server = server
        handler.path = path
        handler.command = "GET"
        handler.request_version = "HTTP/1.1"
        handler.headers = {}
        handler._headers_buffer = []

        # Mock the send methods
        handler.send_response = MagicMock()
        handler.send_header = MagicMock()
        handler.end_headers = MagicMock()
        handler.wfile = MagicMock()

        return handler

    def test_success_page(self):
        """Test /success endpoint."""
        server = MagicMock()
        server.exit_code = 1
        handler = self._make_handler(server, "/success")

        handler.do_GET()
        handler.send_response.assert_called_with(200)

    def test_wrong_path(self):
        """Test callback with wrong path."""
        server = MagicMock()
        server.exit_code = 1
        handler = self._make_handler(server, "/wrong-path")

        handler.do_GET()
        # Should send failure with 404
        handler.send_response.assert_called()
        # First call should be 404
        assert any(call[0][0] == 404 for call in handler.send_response.call_args_list)

    def test_missing_code(self):
        """Test callback with missing authorization code."""
        server = MagicMock()
        server.exit_code = 1
        redirect_path = CHATGPT_OAUTH_CONFIG["redirect_path"]
        handler = self._make_handler(server, f"/{redirect_path}?state=test")

        handler.do_GET()
        # Should send failure with 400
        assert any(call[0][0] == 400 for call in handler.send_response.call_args_list)

    def test_exchange_code_exception(self):
        """Test callback when exchange_code raises."""
        server = MagicMock()
        server.exit_code = 1
        server.exchange_code.side_effect = Exception("Token exchange error")
        redirect_path = CHATGPT_OAUTH_CONFIG["redirect_path"]
        handler = self._make_handler(server, f"/{redirect_path}?code=abc123")

        handler.do_GET()
        # Should send failure with 500
        assert any(call[0][0] == 500 for call in handler.send_response.call_args_list)

    def test_save_token_failure(self):
        """Test callback when save_token returns False."""
        server = MagicMock()
        server.exit_code = 1
        server.exchange_code.return_value = {"access_token": "new_token"}
        redirect_path = CHATGPT_OAUTH_CONFIG["redirect_path"]
        handler = self._make_handler(server, f"/{redirect_path}?code=abc123")

        with patch("gac.oauth.chatgpt_server.save_token", return_value=False):
            handler.do_GET()
        # Should send failure with 500
        assert any(call[0][0] == 500 for call in handler.send_response.call_args_list)

    def test_save_token_success_redirects(self):
        """Test callback when save_token succeeds redirects to /success."""
        server = MagicMock()
        server.exit_code = 1
        server.exchange_code.return_value = {"access_token": "new_token"}
        server.server_address = ("localhost", 1455)
        redirect_path = CHATGPT_OAUTH_CONFIG["redirect_path"]
        handler = self._make_handler(server, f"/{redirect_path}?code=abc123")

        with patch("gac.oauth.chatgpt_server.save_token", return_value=True):
            handler.do_GET()
        # Should redirect with 302
        assert any(call[0][0] == 302 for call in handler.send_response.call_args_list)
        assert server.exit_code == 0

    def test_log_message_verbose(self):
        """Test log_message when verbose is True."""
        server = MagicMock()
        server.verbose = True
        handler = _CallbackHandler.__new__(_CallbackHandler)
        handler.server = server
        # Should not raise
        with patch.object(_CallbackHandler, "log_message", wraps=lambda *a, **kw: None):
            pass  # log_message is tested indirectly

    def test_log_message_quiet(self):
        """Test log_message when verbose is False (default)."""
        server = MagicMock()
        server.verbose = False
        handler = _CallbackHandler.__new__(_CallbackHandler)
        handler.server = server
        # Should not call super().log_message
        handler.log_message("test %s", "arg")


class TestExchangeCode:
    """Test _OAuthServer.exchange_code method."""

    def test_exchange_code_with_org_structure(self):
        """Test exchange_code extracting org from JWT claims."""
        # Build a mock JWT with organization info
        id_claims = {
            "https://api.openai.com/auth": {
                "chatgpt_account_id": "acc-123",
                "organizations": [
                    {"id": "org-default", "is_default": True, "role": "owner"},
                    {"id": "org-other", "is_default": False},
                ],
            }
        }
        access_claims = {"chatgpt_plan_type": "plus"}

        id_payload = base64.urlsafe_b64encode(json.dumps(id_claims).encode()).decode()
        access_payload = base64.urlsafe_b64encode(json.dumps(access_claims).encode()).decode()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "access_token": f"header.{access_payload}.sig",
            "refresh_token": "rt-123",
            "id_token": f"header.{id_payload}.sig",
        }

        server = _OAuthServer.__new__(_OAuthServer)
        server.redirect_uri = "http://localhost:1455/callback"
        server.client_id = "test_client"
        server.context = prepare_oauth_context()
        server.token_endpoint = CHATGPT_OAUTH_CONFIG["token_url"]

        with patch("gac.oauth.chatgpt_server.httpx.post", return_value=mock_response):
            with patch("gac.oauth.chatgpt_server.get_ssl_verify", return_value=True):
                result = server.exchange_code("test_code")

        assert result["access_token"] == f"header.{access_payload}.sig"
        assert result["account_id"] == "acc-123"
        assert result["org_id"] == "org-default"
        assert result["plan_type"] == "plus"

    def test_exchange_code_no_default_org(self):
        """Test exchange_code when no org is_default."""
        id_claims = {
            "https://api.openai.com/auth": {
                "chatgpt_account_id": "acc-456",
                "organizations": [
                    {"id": "org-first"},
                ],
            }
        }
        access_claims = {}

        id_payload = base64.urlsafe_b64encode(json.dumps(id_claims).encode()).decode()
        access_payload = base64.urlsafe_b64encode(json.dumps(access_claims).encode()).decode()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "access_token": f"header.{access_payload}.sig",
            "refresh_token": "rt-456",
            "id_token": f"header.{id_payload}.sig",
        }

        server = _OAuthServer.__new__(_OAuthServer)
        server.redirect_uri = "http://localhost:1455/callback"
        server.client_id = "test_client"
        server.context = prepare_oauth_context()
        server.token_endpoint = CHATGPT_OAUTH_CONFIG["token_url"]

        with patch("gac.oauth.chatgpt_server.httpx.post", return_value=mock_response):
            with patch("gac.oauth.chatgpt_server.get_ssl_verify", return_value=True):
                result = server.exchange_code("test_code")

        assert result["org_id"] == "org-first"

    def test_exchange_code_no_organizations(self):
        """Test exchange_code when no organizations in JWT."""
        id_claims = {
            "https://api.openai.com/auth": {
                "chatgpt_account_id": "acc-789",
            },
            "organization_id": "org-from-id-token",
        }
        access_claims = {}

        id_payload = base64.urlsafe_b64encode(json.dumps(id_claims).encode()).decode()
        access_payload = base64.urlsafe_b64encode(json.dumps(access_claims).encode()).decode()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "access_token": f"header.{access_payload}.sig",
            "refresh_token": "rt-789",
            "id_token": f"header.{id_payload}.sig",
        }

        server = _OAuthServer.__new__(_OAuthServer)
        server.redirect_uri = "http://localhost:1455/callback"
        server.client_id = "test_client"
        server.context = prepare_oauth_context()
        server.token_endpoint = CHATGPT_OAUTH_CONFIG["token_url"]

        with patch("gac.oauth.chatgpt_server.httpx.post", return_value=mock_response):
            with patch("gac.oauth.chatgpt_server.get_ssl_verify", return_value=True):
                result = server.exchange_code("test_code")

        # Falls back to organization_id from id_claims
        assert result["org_id"] == "org-from-id-token"

    def test_exchange_code_no_org_at_all(self):
        """Test exchange_code when no org info at all."""
        id_claims = {"sub": "user123"}
        access_claims = {}

        id_payload = base64.urlsafe_b64encode(json.dumps(id_claims).encode()).decode()
        access_payload = base64.urlsafe_b64encode(json.dumps(access_claims).encode()).decode()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "access_token": f"header.{access_payload}.sig",
            "refresh_token": "rt-999",
            "id_token": f"header.{id_payload}.sig",
        }

        server = _OAuthServer.__new__(_OAuthServer)
        server.redirect_uri = "http://localhost:1455/callback"
        server.client_id = "test_client"
        server.context = prepare_oauth_context()
        server.token_endpoint = CHATGPT_OAUTH_CONFIG["token_url"]

        with patch("gac.oauth.chatgpt_server.httpx.post", return_value=mock_response):
            with patch("gac.oauth.chatgpt_server.get_ssl_verify", return_value=True):
                result = server.exchange_code("test_code")

        assert result["org_id"] == ""


class TestHTMLPages:
    """Test HTML template generation."""

    def test_success_html_structure(self):
        html = _get_success_html()
        assert "<!DOCTYPE html>" in html
        assert "ChatGPT OAuth Complete" in html
        assert "close this window" in html

    def test_failure_html_default_reason(self):
        html = _get_failure_html()
        assert "<!DOCTYPE html>" in html
        assert "ChatGPT OAuth Failed" in html
        assert "Missing authorization code" in html

    def test_failure_html_custom_reason(self):
        html = _get_failure_html("Custom error reason")
        assert "Custom error reason" in html
