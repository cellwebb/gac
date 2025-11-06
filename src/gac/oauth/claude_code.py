"""Claude Code OAuth authentication utilities.

Implements PKCE OAuth flow for Claude Code subscriptions.
"""

import base64
import hashlib
import logging
import secrets
import threading
import time
import webbrowser
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, TypedDict
from urllib.parse import parse_qs, urlencode, urlparse

import httpx

logger = logging.getLogger(__name__)


class ClaudeCodeConfig(TypedDict):
    """Type definition for Claude Code OAuth configuration."""

    auth_url: str
    token_url: str
    api_base_url: str
    client_id: str
    scope: str
    redirect_host: str
    redirect_path: str
    callback_port_range: tuple[int, int]
    callback_timeout: int
    anthropic_version: str


# Claude Code OAuth configuration
CLAUDE_CODE_CONFIG: ClaudeCodeConfig = {
    "auth_url": "https://claude.ai/oauth/authorize",
    "token_url": "https://console.anthropic.com/v1/oauth/token",
    "api_base_url": "https://api.anthropic.com",
    "client_id": "9d1c250a-e61b-44d9-88ed-5944d1962f5e",
    "scope": "org:create_api_key user:profile user:inference",
    "redirect_host": "http://localhost",
    "redirect_path": "callback",
    "callback_port_range": (8765, 8795),
    "callback_timeout": 180,
    "anthropic_version": "2023-06-01",
}


@dataclass
class OAuthContext:
    """Runtime state for an in-progress OAuth flow."""

    state: str
    code_verifier: str
    code_challenge: str
    created_at: float
    redirect_uri: str | None = None


class _OAuthResult:
    """Stores OAuth callback results."""

    def __init__(self) -> None:
        self.code: str | None = None
        self.state: str | None = None
        self.error: str | None = None


class _CallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth callback."""

    result: _OAuthResult
    received_event: threading.Event

    def do_GET(self) -> None:  # noqa: N802
        """Handle GET request from OAuth redirect."""
        logger.info("OAuth callback received: path=%s", self.path)
        parsed = urlparse(self.path)
        params: dict[str, list[str]] = parse_qs(parsed.query)

        code = params.get("code", [None])[0]
        state = params.get("state", [None])[0]

        if code and state:
            self.result.code = code
            self.result.state = state
            success_html = _get_success_html()
            self._write_response(200, success_html)
        else:
            self.result.error = "Missing code or state"
            failure_html = _get_failure_html()
            self._write_response(400, failure_html)

        self.received_event.set()

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        """Suppress HTTP server logs."""
        return

    def _write_response(self, status: int, body: str) -> None:
        """Write HTTP response."""
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))


def _get_success_html() -> str:
    """Return HTML for successful authentication."""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Authentication Successful</title>
    <style>
        body { font-family: system-ui; text-align: center; padding: 50px; }
        h1 { color: #10a37f; }
    </style>
</head>
<body>
    <h1>✓ Authentication Successful!</h1>
    <p>You can close this window and return to your terminal.</p>
</body>
</html>
"""


def _get_failure_html() -> str:
    """Return HTML for failed authentication."""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Authentication Failed</title>
    <style>
        body { font-family: system-ui; text-align: center; padding: 50px; }
        h1 { color: #ef4444; }
    </style>
</head>
<body>
    <h1>✗ Authentication Failed</h1>
    <p>Missing authorization code. Please try again.</p>
</body>
</html>
"""


def _urlsafe_b64encode(data: bytes) -> str:
    """Base64url encode without padding."""
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _generate_code_verifier() -> str:
    """Generate PKCE code verifier."""
    return _urlsafe_b64encode(secrets.token_bytes(64))


def _compute_code_challenge(code_verifier: str) -> str:
    """Compute PKCE code challenge from verifier."""
    digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    return _urlsafe_b64encode(digest)


def prepare_oauth_context() -> OAuthContext:
    """Create a new OAuth PKCE context."""
    state = secrets.token_urlsafe(32)
    code_verifier = _generate_code_verifier()
    code_challenge = _compute_code_challenge(code_verifier)
    return OAuthContext(
        state=state,
        code_verifier=code_verifier,
        code_challenge=code_challenge,
        created_at=time.time(),
    )


def build_authorization_url(context: OAuthContext) -> str:
    """Build the Claude authorization URL with PKCE parameters."""
    if not context.redirect_uri:
        raise RuntimeError("Redirect URI has not been assigned for this OAuth context")

    params = {
        "response_type": "code",
        "client_id": CLAUDE_CODE_CONFIG["client_id"],
        "redirect_uri": context.redirect_uri,
        "scope": CLAUDE_CODE_CONFIG["scope"],
        "state": context.state,
        "code": "true",
        "code_challenge": context.code_challenge,
        "code_challenge_method": "S256",
    }
    return f"{CLAUDE_CODE_CONFIG['auth_url']}?{urlencode(params)}"


def _start_callback_server(context: OAuthContext) -> tuple[HTTPServer, _OAuthResult, threading.Event] | None:
    """Start local HTTP server to receive OAuth callback."""
    port_range = CLAUDE_CODE_CONFIG["callback_port_range"]

    for port in range(port_range[0], port_range[1] + 1):
        try:
            server = HTTPServer(("localhost", port), _CallbackHandler)
            context.redirect_uri = f"{CLAUDE_CODE_CONFIG['redirect_host']}:{port}/{CLAUDE_CODE_CONFIG['redirect_path']}"
            result = _OAuthResult()
            event = threading.Event()
            _CallbackHandler.result = result
            _CallbackHandler.received_event = event

            def run_server(srv: HTTPServer = server) -> None:
                with srv:
                    srv.serve_forever()

            threading.Thread(target=run_server, daemon=True).start()
            return server, result, event
        except OSError:
            continue

    logger.error("Could not start OAuth callback server; all candidate ports are in use")
    return None


def exchange_code_for_tokens(auth_code: str, context: OAuthContext) -> dict[str, Any] | None:
    """Exchange authorization code for access tokens."""
    if not context.redirect_uri:
        raise RuntimeError("Redirect URI missing from OAuth context")

    payload = {
        "grant_type": "authorization_code",
        "client_id": CLAUDE_CODE_CONFIG["client_id"],
        "code": auth_code,
        "state": context.state,
        "code_verifier": context.code_verifier,
        "redirect_uri": context.redirect_uri,
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "anthropic-beta": "oauth-2025-04-20",
    }

    logger.info("Exchanging code for tokens: %s", CLAUDE_CODE_CONFIG["token_url"])
    try:
        response = httpx.post(
            CLAUDE_CODE_CONFIG["token_url"],
            json=payload,
            headers=headers,
            timeout=30,
        )
        logger.info("Token exchange response: %s", response.status_code)
        if response.status_code == 200:
            tokens: dict[str, Any] = response.json()
            # Add expiry timestamp if not present
            if "expires_at" not in tokens and "expires_in" in tokens:
                tokens["expires_at"] = time.time() + tokens["expires_in"]
            return tokens
        logger.error("Token exchange failed: %s - %s", response.status_code, response.text)
    except Exception as exc:
        logger.error("Token exchange error: %s", exc)
    return None


def perform_oauth_flow(quiet: bool = False) -> dict[str, Any] | None:
    """Perform full OAuth flow and return tokens."""
    context = prepare_oauth_context()

    # Start callback server
    started = _start_callback_server(context)
    if not started:
        if not quiet:
            print("❌ Could not start OAuth callback server; all ports are in use")
        return None

    server, result, event = started
    redirect_uri = context.redirect_uri

    if not redirect_uri:
        if not quiet:
            print("❌ Failed to assign redirect URI for OAuth flow")
        server.shutdown()
        return None

    # Build auth URL and open browser
    auth_url = build_authorization_url(context)

    if not quiet:
        print("\n🔐 Opening browser for Claude Code OAuth authentication...")
        print(f"   If it doesn't open automatically, visit: {auth_url}\n")
        print(f"   Listening for callback on {redirect_uri}")
        print("   (Waiting up to 3 minutes...)\n")

    try:
        webbrowser.open(auth_url)
    except Exception as exc:
        logger.warning("Failed to open browser automatically: %s", exc)
        if not quiet:
            print(f"⚠️  Failed to open browser automatically: {exc}")
            print(f"   Please open the URL manually: {auth_url}\n")

    # Wait for callback
    timeout = CLAUDE_CODE_CONFIG["callback_timeout"]
    if not event.wait(timeout=timeout):
        if not quiet:
            print("❌ OAuth callback timed out. Please try again.")
        server.shutdown()
        return None

    server.shutdown()

    # Check for errors
    if result.error:
        if not quiet:
            print(f"❌ OAuth callback error: {result.error}")
        return None

    # Validate state
    if result.state != context.state:
        if not quiet:
            print("❌ State mismatch detected; aborting authentication for security")
        return None

    # Exchange code for tokens
    if not quiet:
        print("✓ Authorization code received")
        print("  Exchanging for access token...\n")

    tokens = exchange_code_for_tokens(result.code, context)  # type: ignore[arg-type]
    if not tokens:
        if not quiet:
            print("❌ Token exchange failed. Please try again.")
        return None

    if not quiet:
        print("✓ Claude Code authentication successful!")

    return tokens


def get_token_storage_path() -> Path:
    """Get path for storing OAuth tokens."""
    return Path.home() / ".gac.env"


def load_stored_token() -> str | None:
    """Load stored access token from .gac.env."""
    from dotenv import dotenv_values

    env_path = get_token_storage_path()
    if not env_path.exists():
        return None

    env_vars = dotenv_values(str(env_path))
    return env_vars.get("CLAUDE_CODE_ACCESS_TOKEN")


def save_token(access_token: str) -> bool:
    """Save access token to .gac.env and update environment."""
    import os

    from dotenv import set_key

    env_path = get_token_storage_path()
    try:
        set_key(str(env_path), "CLAUDE_CODE_ACCESS_TOKEN", access_token)
        # Also update the current environment so the token is immediately available
        os.environ["CLAUDE_CODE_ACCESS_TOKEN"] = access_token
        return True
    except Exception as exc:
        logger.error("Failed to save token: %s", exc)
        return False


def authenticate_and_save(quiet: bool = False) -> bool:
    """Perform OAuth flow and save token."""
    tokens = perform_oauth_flow(quiet=quiet)
    if not tokens:
        return False

    access_token = tokens.get("access_token")
    if not access_token:
        if not quiet:
            print("❌ No access token returned from authentication")
        return False

    if not save_token(access_token):
        if not quiet:
            print("❌ Failed to save access token")
        return False

    if not quiet:
        print(f"✓ Access token saved to {get_token_storage_path()}")

    return True
