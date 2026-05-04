"""ChatGPT OAuth authentication — public API.

This package implements PKCE OAuth flow for ChatGPT/Codex API access,
matching OpenAI's Codex CLI auth flow.  Internal implementation is split
across three submodules:

- ``chatgpt_config``  — configuration dict and model list
- ``chatgpt_tokens`` — token storage, refresh, JWT parsing
- ``chatgpt_server`` — PKCE context, callback HTTP server, HTML pages

Consumers should import from this module (``gac.oauth.chatgpt``) rather
than the internal submodules directly.
"""

from __future__ import annotations

import logging
import time
import webbrowser
from typing import Any

from gac.oauth.chatgpt_config import CHATGPT_OAUTH_CONFIG, DEFAULT_CODEX_MODELS
from gac.oauth.chatgpt_server import _OAuthServer
from gac.oauth.chatgpt_tokens import (
    is_token_expired,
    load_stored_token,
    load_stored_tokens,
    parse_jwt_claims,
    refresh_access_token,
    refresh_token_if_expired,
    remove_token,
    save_token,
)

logger = logging.getLogger(__name__)

# Re-export everything so consumers only need ``from gac.oauth.chatgpt import ...``
__all__ = [
    "CHATGPT_OAUTH_CONFIG",
    "DEFAULT_CODEX_MODELS",
    "authenticate_and_save",
    "is_token_expired",
    "load_stored_token",
    "load_stored_tokens",
    "parse_jwt_claims",
    "perform_oauth_flow",
    "refresh_access_token",
    "refresh_token_if_expired",
    "remove_token",
    "save_token",
]


# ---------------------------------------------------------------------------
# Public flow functions
# ---------------------------------------------------------------------------


def perform_oauth_flow(quiet: bool = False) -> dict[str, Any] | None:
    """Perform full ChatGPT OAuth flow and return tokens."""
    existing = load_stored_token()
    if existing and not quiet:
        print("⚠️  Existing ChatGPT OAuth tokens will be overwritten.")

    try:
        server = _OAuthServer(client_id=CHATGPT_OAUTH_CONFIG["client_id"])
    except OSError as exc:
        port_range = CHATGPT_OAUTH_CONFIG["callback_port_range"]
        if not quiet:
            print(f"❌ Could not start OAuth server on ports {port_range[0]}-{port_range[1]}: {exc}")
            print(f"   Use `lsof -ti:{port_range[0]} | xargs kill` to free ports.")
        return None

    auth_url = server.auth_url()

    if not quiet:
        print("\n🔐 Opening browser for ChatGPT OAuth authentication...")
        print(f"   If it doesn't open automatically, visit: {auth_url}")
        print(f"   Listening for callback on {server.redirect_uri}")
        print("   (Waiting up to 2 minutes for callback)\n")

    # Start server in background thread
    import threading

    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    # Open browser
    try:
        webbrowser.open(auth_url)
    except Exception as exc:
        logger.warning("Failed to open browser automatically: %s", exc)
        if not quiet:
            print(f"⚠️  Failed to open browser automatically: {exc}")
            print(f"   Please open the URL manually: {auth_url}\n")

    # Wait for callback
    timeout = CHATGPT_OAUTH_CONFIG["callback_timeout"]
    elapsed = 0.0
    interval = 0.25
    while elapsed < timeout:
        time.sleep(interval)
        elapsed += interval
        if server.exit_code == 0:
            break

    server.shutdown()
    server_thread.join(timeout=5)

    if server.exit_code != 0:
        if not quiet:
            print("❌ ChatGPT OAuth authentication failed or timed out.")
        return None

    tokens = load_stored_tokens()
    if not tokens:
        if not quiet:
            print("❌ Tokens saved during OAuth flow could not be loaded.")
        return None

    if not quiet:
        print("✓ ChatGPT OAuth authentication successful!")

    return tokens


def authenticate_and_save(quiet: bool = False) -> bool:
    """Perform OAuth flow and save token. Returns True on success."""
    tokens = perform_oauth_flow(quiet=quiet)
    if not tokens:
        return False

    access_token = tokens.get("access_token")
    if not access_token:
        if not quiet:
            print("❌ No access token returned from ChatGPT authentication")
        return False

    # Token is already saved by the callback handler
    if not quiet:
        provider_key = CHATGPT_OAUTH_CONFIG["provider_key"]
        print(f"✓ Access token saved to ~/.gac/oauth/{provider_key}.json")

    return True
