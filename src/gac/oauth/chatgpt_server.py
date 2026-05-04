"""ChatGPT OAuth callback server and HTML pages."""

from __future__ import annotations

import hashlib
import logging
import secrets
import threading
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

import httpx

from gac.oauth.chatgpt_config import CHATGPT_OAUTH_CONFIG
from gac.oauth.chatgpt_tokens import parse_jwt_claims, save_token
from gac.utils import get_ssl_verify

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# PKCE helpers
# ---------------------------------------------------------------------------


def _urlsafe_b64encode(data: bytes) -> str:
    """Base64url encode without padding."""
    import base64

    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _generate_code_verifier() -> str:
    return secrets.token_hex(64)


def _compute_code_challenge(code_verifier: str) -> str:
    return _urlsafe_b64encode(hashlib.sha256(code_verifier.encode("utf-8")).digest())


# ---------------------------------------------------------------------------
# OAuth context
# ---------------------------------------------------------------------------


@dataclass
class OAuthContext:
    """Runtime state for an in-progress OAuth flow."""

    state: str
    code_verifier: str
    code_challenge: str
    created_at: float
    redirect_uri: str | None = None
    expires_at: float | None = None

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return time.time() - self.created_at > 300
        return time.time() > self.expires_at


def prepare_oauth_context() -> OAuthContext:
    """Create a fresh OAuth PKCE context."""
    verifier = _generate_code_verifier()
    return OAuthContext(
        state=secrets.token_hex(32),
        code_verifier=verifier,
        code_challenge=_compute_code_challenge(verifier),
        created_at=time.time(),
        expires_at=time.time() + 240,
    )


# ---------------------------------------------------------------------------
# HTML pages
# ---------------------------------------------------------------------------


def _get_success_html() -> str:
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        "<title>ChatGPT OAuth Successful</title>"
        "<style>body{font-family:system-ui;text-align:center;padding:50px;"
        "background:linear-gradient(135deg,#0f172a,#1e293b);color:#e2e8f0;}"
        "h1{color:#10b981;font-size:2.5em;}p{font-size:1.2em;color:#94a3b8;}</style>"
        "</head><body>"
        "<h1>✓ ChatGPT OAuth Complete!</h1>"
        "<p>You can close this window and return to your terminal.</p>"
        "</body></html>"
    )


def _get_failure_html(reason: str = "Missing authorization code") -> str:
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        "<title>ChatGPT OAuth Failed</title>"
        "<style>body{font-family:system-ui;text-align:center;padding:50px;"
        "background:linear-gradient(135deg,#0f172a,#1e293b);color:#e2e8f0;}"
        "h1{color:#ef4444;font-size:2.5em;}p{font-size:1.2em;color:#94a3b8;}</style>"
        "</head><body>"
        "<h1>✗ ChatGPT OAuth Failed</h1>"
        f"<p>{reason}</p>"
        "<p>Please try again from your terminal.</p>"
        "</body></html>"
    )


# ---------------------------------------------------------------------------
# Callback server — tries a port range if the preferred port is occupied
# ---------------------------------------------------------------------------


class _CallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth callback."""

    server: _OAuthServer

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/success":
            self._send_html(_get_success_html())
            self._shutdown_after_delay(2.0)
            return

        if path != f"/{CHATGPT_OAUTH_CONFIG['redirect_path']}":
            self._send_failure(404, "Callback endpoint not found.")
            self._shutdown()
            return

        params: dict[str, list[str]] = parse_qs(parsed.query)
        code = params.get("code", [None])[0]
        if not code:
            self._send_failure(400, "Missing auth code.")
            self._shutdown()
            return

        try:
            auth_bundle = self.server.exchange_code(code)
        except Exception as exc:
            self._send_failure(500, f"Token exchange failed: {exc}")
            self._shutdown()
            return

        if save_token(auth_bundle["access_token"], token_data=auth_bundle):
            self.server.exit_code = 0
            port = self.server.server_address[1]
            self._send_redirect(f"http://localhost:{port}/success")
        else:
            self._send_failure(500, "Unable to persist auth file.")
            self._shutdown()
        self._shutdown_after_delay(2.0)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        if getattr(self.server, "verbose", False):
            super().log_message(format, *args)

    def _send_redirect(self, url: str) -> None:
        self.send_response(302)
        self.send_header("Location", url)
        self.end_headers()

    def _send_html(self, body: str, status: int = 200) -> None:
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_failure(self, status: int, reason: str) -> None:
        self._send_html(_get_failure_html(reason), status)

    def _shutdown(self) -> None:
        threading.Thread(target=self.server.shutdown, daemon=True).start()

    def _shutdown_after_delay(self, seconds: float = 2.0) -> None:
        def _later() -> None:
            try:
                time.sleep(seconds)
            finally:
                self._shutdown()

        threading.Thread(target=_later, daemon=True).start()


class _OAuthServer(HTTPServer):
    """Local OAuth callback server with port-range fallback."""

    def __init__(self, *, client_id: str, verbose: bool = False) -> None:
        self.exit_code = 1
        self.verbose = verbose
        self.client_id = client_id
        self.issuer = CHATGPT_OAUTH_CONFIG["issuer"]
        self.token_endpoint = CHATGPT_OAUTH_CONFIG["token_url"]

        # Create fresh OAuth context
        self.context = prepare_oauth_context()

        # Try the port range until we find one that's free
        host = CHATGPT_OAUTH_CONFIG["redirect_host"].rstrip("/")
        path = CHATGPT_OAUTH_CONFIG["redirect_path"].lstrip("/")
        port_range = CHATGPT_OAUTH_CONFIG["callback_port_range"]
        bound_port: int | None = None

        for port in range(port_range[0], port_range[1] + 1):
            try:
                super().__init__(("localhost", port), _CallbackHandler, bind_and_activate=True)
                bound_port = port
                break
            except OSError:
                continue

        if bound_port is None:
            raise OSError(
                f"Could not bind any port in range {port_range[0]}-{port_range[1]}. "
                f"Try freeing ports with: lsof -ti:{port_range[0]}-{port_range[1]} | xargs kill"
            )

        self.redirect_uri = f"{host}:{bound_port}/{path}"
        self.context.redirect_uri = self.redirect_uri

    def auth_url(self) -> str:
        """Build the OpenAI authorization URL with PKCE parameters."""
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": CHATGPT_OAUTH_CONFIG["scope"],
            "code_challenge": self.context.code_challenge,
            "code_challenge_method": "S256",
            "id_token_add_organizations": "true",
            "codex_cli_simplified_flow": "true",
            "state": self.context.state,
        }
        return f"{self.issuer}/oauth/authorize?{urlencode(params)}"

    def exchange_code(self, code: str) -> dict[str, Any]:
        """Exchange authorization code for tokens."""
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "code_verifier": self.context.code_verifier,
        }
        response = httpx.post(
            self.token_endpoint,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
            verify=get_ssl_verify(),
        )
        response.raise_for_status()
        payload = response.json()

        id_token = payload.get("id_token", "")
        access_token = payload.get("access_token", "")
        refresh_token = payload.get("refresh_token", "")

        # Extract account_id and org_id from JWT claims
        id_claims = parse_jwt_claims(id_token) or {}
        access_claims = parse_jwt_claims(access_token) or {}
        auth_claims = id_claims.get("https://api.openai.com/auth") or {}
        chatgpt_account_id = auth_claims.get("chatgpt_account_id", "")

        organizations = auth_claims.get("organizations", [])
        org_id = None
        if organizations:
            default_org = next(
                (o for o in organizations if o.get("is_default")),
                organizations[0],
            )
            org_id = default_org.get("id")
        if not org_id:
            org_id = id_claims.get("organization_id")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "id_token": id_token,
            "account_id": chatgpt_account_id,
            "org_id": org_id or "",
            "plan_type": access_claims.get("chatgpt_plan_type"),
        }
