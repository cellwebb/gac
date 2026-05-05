"""Shared OAuth PKCE infrastructure for browser-based authentication flows.

Provides reusable components that both ChatGPT and Claude Code OAuth flows
depend on: PKCE helpers, callback server, token CRUD, JWT parsing, and
full flow orchestration.
"""

from __future__ import annotations

import base64
import hashlib
import json
import logging
import os
import secrets
import threading
import time
import webbrowser
from collections.abc import Callable
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

import httpx

from gac.oauth.token_store import OAuthToken, TokenStore
from gac.utils import get_ssl_verify

logger = logging.getLogger(__name__)

# Type alias for provider-specific code exchange callbacks.
ExchangeFn = Callable[[str, "OAuthContext"], dict[str, Any] | None]


# ---------------------------------------------------------------------------
# PKCE helpers
# ---------------------------------------------------------------------------


def urlsafe_b64encode(data: bytes) -> str:
    """Base64url encode without padding."""
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def generate_code_verifier() -> str:
    """Generate a PKCE code verifier (43-128 chars of unreserved characters)."""
    return urlsafe_b64encode(secrets.token_bytes(64))


def compute_code_challenge(code_verifier: str) -> str:
    """Compute PKCE S256 code challenge from a verifier."""
    return urlsafe_b64encode(hashlib.sha256(code_verifier.encode("utf-8")).digest())


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
        threshold = self.expires_at or (self.created_at + 300)
        return time.time() > threshold


def prepare_oauth_context() -> OAuthContext:
    """Create a fresh OAuth PKCE context."""
    verifier = generate_code_verifier()
    return OAuthContext(
        state=secrets.token_hex(32),
        code_verifier=verifier,
        code_challenge=compute_code_challenge(verifier),
        created_at=time.time(),
        expires_at=time.time() + 240,
    )


# ---------------------------------------------------------------------------
# HTML pages
# ---------------------------------------------------------------------------


def get_success_html(provider_name: str) -> str:
    """Return HTML page shown after successful authentication."""
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<title>{provider_name} OAuth Successful</title>"
        "<style>body{font-family:system-ui;text-align:center;padding:50px;"
        "background:linear-gradient(135deg,#0f172a,#1e293b);color:#e2e8f0;}"
        "h1{color:#10b981;font-size:2.5em;}p{font-size:1.2em;color:#94a3b8;}</style>"
        "</head><body>"
        f"<h1>✓ {provider_name} OAuth Complete!</h1>"
        "<p>You can close this window and return to your terminal.</p>"
        "</body></html>"
    )


def get_failure_html(provider_name: str, reason: str = "Missing authorization code") -> str:
    """Return HTML page shown after failed authentication."""
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<title>{provider_name} OAuth Failed</title>"
        "<style>body{font-family:system-ui;text-align:center;padding:50px;"
        "background:linear-gradient(135deg,#0f172a,#1e293b);color:#e2e8f0;}"
        "h1{color:#ef4444;font-size:2.5em;}p{font-size:1.2em;color:#94a3b8;}</style>"
        "</head><body>"
        f"<h1>✗ {provider_name} OAuth Failed</h1>"
        f"<p>{reason}</p>"
        "<p>Please try again from your terminal.</p>"
        "</body></html>"
    )


# ---------------------------------------------------------------------------
# Callback server — tries a port range if the preferred port is occupied
# ---------------------------------------------------------------------------


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
    _provider_name: str

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        params: dict[str, list[str]] = parse_qs(parsed.query)

        code = params.get("code", [None])[0]
        state = params.get("state", [None])[0]

        if code:
            self.result.code = code
            self.result.state = state
            self._write_response(200, get_success_html(self._provider_name))
        else:
            self.result.error = "Missing authorization code"
            self._write_response(400, get_failure_html(self._provider_name))

        self.received_event.set()

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return

    def _write_response(self, status: int, body: str) -> None:
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def start_callback_server(
    config: dict[str, Any],
    provider_name: str,
) -> tuple[HTTPServer, _OAuthResult, threading.Event, OAuthContext] | None:
    """Start a local callback server on the first available port.

    Returns ``(server, result, event, context)`` or ``None`` when all ports
    in the configured range are occupied.
    """
    context = prepare_oauth_context()
    port_range = config["callback_port_range"]
    host = config["redirect_host"].rstrip("/")
    path = config["redirect_path"].lstrip("/")

    for port in range(port_range[0], port_range[1] + 1):
        try:
            server = HTTPServer(("localhost", port), _CallbackHandler)
            context.redirect_uri = f"{host}:{port}/{path}"

            result = _OAuthResult()
            event = threading.Event()
            _CallbackHandler.result = result
            _CallbackHandler.received_event = event
            _CallbackHandler._provider_name = provider_name

            def _serve(srv: HTTPServer = server) -> None:
                with srv:
                    srv.serve_forever()

            threading.Thread(target=_serve, daemon=True).start()
            return server, result, event, context
        except OSError:
            continue

    logger.error("Could not start OAuth callback server; all candidate ports are in use")
    return None


# ---------------------------------------------------------------------------
# JWT parsing
# ---------------------------------------------------------------------------


def parse_jwt_claims(token: str) -> dict[str, Any] | None:
    """Parse JWT token to extract claims (no signature verification)."""
    if not token or token.count(".") != 2:
        return None
    try:
        _, payload, _ = token.split(".")
        padded = payload + "=" * (-len(payload) % 4)
        data = base64.urlsafe_b64decode(padded.encode())
        result = json.loads(data.decode())
        return result if isinstance(result, dict) else None
    except Exception as exc:
        logger.error("Failed to parse JWT: %s", exc)
    return None


# ---------------------------------------------------------------------------
# Token CRUD
# ---------------------------------------------------------------------------


def save_token(
    provider_key: str,
    env_var: str,
    access_token: str,
    token_data: dict[str, Any] | None = None,
    extra_keys: tuple[str, ...] = (),
) -> bool:
    """Save access token to TokenStore.

    Args:
        provider_key: Key for TokenStore (e.g. ``"chatgpt-oauth"``).
        env_var: Environment variable name to set with the access token.
        access_token: The OAuth access token string.
        token_data: Optional full token response data.
        extra_keys: Keys to extract from *token_data* into the ``extra`` dict.
    """
    store = TokenStore()
    try:
        token: OAuthToken = {
            "access_token": access_token,
            "token_type": "Bearer",
        }

        if token_data:
            if "refresh_token" in token_data:
                token["refresh_token"] = token_data["refresh_token"]
            if "expires_at" in token_data:
                token["expiry"] = int(token_data["expires_at"])
            elif "expires_in" in token_data:
                token["expiry"] = int(time.time() + token_data["expires_in"])

            extra: dict[str, Any] = {}
            for key in extra_keys:
                if key in token_data and token_data[key]:
                    extra[key] = token_data[key]
            if extra:
                token["extra"] = extra

        # Fall back to JWT claims for expiry
        if "expiry" not in token:
            claims = parse_jwt_claims(access_token)
            if claims and "exp" in claims:
                token["expiry"] = int(claims["exp"])

        store.save_token(provider_key, token)
        os.environ[env_var] = access_token
        return True
    except Exception as exc:
        logger.error("Failed to save %s OAuth token: %s", provider_key, exc)
    return False


def load_stored_token(provider_key: str) -> str | None:
    """Load stored access token from TokenStore."""
    store = TokenStore()
    token = store.get_token(provider_key)
    return token.get("access_token") if token else None


def load_stored_tokens(provider_key: str) -> dict[str, Any] | None:
    """Load all stored token data including extra metadata."""
    store = TokenStore()
    token = store.get_token(provider_key)
    if not token:
        return None
    result: dict[str, Any] = dict(token)
    extra = token.get("extra")
    if extra and isinstance(extra, dict):
        result.update(extra)
    return result


def remove_token(provider_key: str, env_var: str) -> bool:
    """Remove stored access token from TokenStore and clear env var."""
    store = TokenStore()
    try:
        store.remove_token(provider_key)
        os.environ.pop(env_var, None)
        return True
    except Exception as exc:
        logger.error("Failed to remove %s OAuth token: %s", provider_key, exc)
    return False


def is_token_expired(provider_key: str, margin_seconds: int = 30) -> bool:
    """Check if the stored OAuth token has expired.

    Returns ``True`` when the token is expired *or* within *margin_seconds*
    of expiring.  Returns ``False`` when no expiry info is available (assumed
    still valid).
    """
    store = TokenStore()
    token = store.get_token(provider_key)
    if not token:
        return True

    expiry = token.get("expiry")
    if not expiry:
        access_token = token.get("access_token", "")
        claims = parse_jwt_claims(access_token)
        if claims and "exp" in claims:
            exp_value = claims["exp"]
            if isinstance(exp_value, (int, float)):
                return time.time() > exp_value - margin_seconds
        return False

    return time.time() >= (expiry - margin_seconds)


# ---------------------------------------------------------------------------
# Token refresh — shared helper for providers with HTTP refresh support
# ---------------------------------------------------------------------------


def refresh_oauth_token(
    token_url: str,
    client_id: str,
    provider_key: str,
    env_var: str,
    extra_keys: tuple[str, ...] = (),
    *,
    client_secret: str = "",
    save_fn: Callable[[str, dict[str, Any] | None], bool] | None = None,
) -> str | None:
    """Refresh an OAuth access token using a stored refresh token.

    Shared between OAuth providers — both use the same pattern:
    load refresh token → POST to token endpoint → merge new tokens → save.

    Args:
        token_url: The OAuth token endpoint URL.
        client_id: The OAuth client ID.
        provider_key: Key for TokenStore (e.g. ``"chatgpt-oauth"``).
        env_var: Environment variable name to set with the new access token.
        extra_keys: Keys to preserve across refresh (e.g. ``"project_id"``).
        client_secret: Optional client secret (Google requires it; OpenAI doesn't).
        save_fn: Optional custom save function. If ``None``, uses :func:`save_token`.

    Returns:
        The new access token on success, ``None`` otherwise.
    """
    tokens = load_stored_tokens(provider_key)
    if not tokens:
        return None

    refresh_token = tokens.get("refresh_token")
    if not refresh_token:
        logger.debug("No refresh_token available for %s OAuth", provider_key)
        return None

    data: dict[str, str] = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
    }
    if client_secret:
        data["client_secret"] = client_secret

    try:
        response = httpx.post(
            token_url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
            verify=get_ssl_verify(),
        )

        if response.status_code == 200:
            new_tokens = response.json()
            new_access_token = new_tokens.get("access_token")
            if not new_access_token:
                logger.error("No access_token in refresh response for %s", provider_key)
                return None

            # Merge with existing token data, preserving extra fields
            merged: dict[str, Any] = dict(tokens)
            merged["access_token"] = new_access_token
            merged["refresh_token"] = new_tokens.get("refresh_token", refresh_token)
            if "expires_in" in new_tokens:
                merged["expires_at"] = time.time() + new_tokens["expires_in"]

            if save_fn:
                saved = save_fn(merged["access_token"], merged)
            else:
                saved = save_token(
                    provider_key, env_var, merged["access_token"], token_data=merged, extra_keys=extra_keys
                )
            if saved:
                logger.info("Successfully refreshed %s OAuth token", provider_key)
                return str(merged["access_token"])
        else:
            logger.error(
                "Token refresh failed for %s: %s - %s",
                provider_key,
                response.status_code,
                response.text[:200],
            )

    except Exception as exc:
        logger.error("Token refresh error for %s: %s", provider_key, exc)
    return None


# ---------------------------------------------------------------------------
# OAuth flow orchestration
# ---------------------------------------------------------------------------


def build_auth_url(
    config: dict[str, Any],
    context: OAuthContext,
    extra_params: dict[str, str] | None = None,
) -> str:
    """Build the authorization URL with PKCE parameters."""
    if not context.redirect_uri:
        raise RuntimeError("Redirect URI has not been assigned for this OAuth context")

    params: dict[str, str] = {
        "response_type": "code",
        "client_id": config["client_id"],
        "redirect_uri": context.redirect_uri,
        "scope": config["scope"],
        "code_challenge": context.code_challenge,
        "code_challenge_method": "S256",
        "state": context.state,
    }
    if extra_params:
        params.update(extra_params)

    auth_url = config.get("auth_url", "")
    if not auth_url:
        issuer = config.get("issuer", "")
        auth_url = f"{issuer}/oauth/authorize"

    return f"{auth_url}?{urlencode(params)}"


def perform_oauth_flow(
    config: dict[str, Any],
    provider_name: str,
    exchange_fn: ExchangeFn,
    *,
    extra_auth_params: dict[str, str] | None = None,
    quiet: bool = False,
) -> dict[str, Any] | None:
    """Perform full OAuth flow and return tokens.

    1. Starts a local callback server
    2. Opens the browser for user authentication
    3. Waits for the callback
    4. Exchanges the authorization code for tokens via *exchange_fn*
    """
    existing = load_stored_token(config["provider_key"])
    if existing and not quiet:
        print(f"⚠️  Existing {provider_name} OAuth tokens will be overwritten.")

    started = start_callback_server(config, provider_name)
    if not started:
        if not quiet:
            port_range = config["callback_port_range"]
            print(f"❌ Could not start OAuth server on ports {port_range[0]}-{port_range[1]}")
            print(f"   Use `lsof -ti:{port_range[0]} | xargs kill` to free ports.")
        return None

    server, result, event, context = started

    auth_url = build_auth_url(config, context, extra_auth_params)

    timeout = config["callback_timeout"]
    if not quiet:
        print(f"\n🔐 Opening browser for {provider_name} OAuth authentication...")
        print(f"   If it doesn't open automatically, visit: {auth_url}")
        print(f"   Listening for callback on {context.redirect_uri}")
        print(f"   (Waiting up to {timeout // 60} minutes for callback)\n")

    try:
        webbrowser.open(auth_url)
    except Exception as exc:
        logger.warning("Failed to open browser: %s", exc)
        if not quiet:
            print(f"⚠️  Failed to open browser: {exc}")
            print(f"   Please open: {auth_url}\n")

    if not event.wait(timeout=timeout):
        if not quiet:
            print("❌ OAuth authentication timed out.")
        server.shutdown()
        return None

    server.shutdown()

    if result.error:
        if not quiet:
            print(f"❌ OAuth callback error: {result.error}")
        return None

    if result.state != context.state:
        if not quiet:
            print("❌ State mismatch detected; aborting for security")
        return None

    if not result.code:
        if not quiet:
            print("❌ No authorization code received")
        return None

    tokens = exchange_fn(result.code, context)
    if not tokens:
        if not quiet:
            print("❌ Token exchange failed.")
        return None

    if not quiet:
        print(f"✓ {provider_name} OAuth authentication successful!")

    return tokens


def authenticate_and_save(
    config: dict[str, Any],
    provider_name: str,
    exchange_fn: ExchangeFn,
    *,
    extra_auth_params: dict[str, str] | None = None,
    extra_token_keys: tuple[str, ...] = (),
    quiet: bool = False,
) -> bool:
    """Perform OAuth flow and save token.  Returns ``True`` on success."""
    tokens = perform_oauth_flow(
        config,
        provider_name,
        exchange_fn,
        extra_auth_params=extra_auth_params,
        quiet=quiet,
    )
    if not tokens:
        return False

    access_token = tokens.get("access_token")
    if not access_token:
        if not quiet:
            print(f"❌ No access token returned from {provider_name} authentication")
        return False

    if not save_token(
        config["provider_key"],
        config["api_key_env_var"],
        access_token,
        tokens,
        extra_token_keys,
    ):
        if not quiet:
            print("❌ Failed to save access token")
        return False

    if not quiet:
        print(f"✓ Access token saved to ~/.gac/oauth/{config['provider_key']}.json")

    return True
