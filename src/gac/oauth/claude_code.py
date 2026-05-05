"""Claude Code OAuth authentication utilities.

Implements PKCE OAuth flow for Claude Code subscriptions.
Shared infrastructure lives in :mod:`gac.oauth.base`.
"""

from __future__ import annotations

import logging
import time
from typing import Any

import httpx

from gac.oauth.base import (
    OAuthContext,
)
from gac.oauth.base import (
    authenticate_and_save as _base_authenticate,
)
from gac.oauth.base import (
    is_token_expired as _base_is_expired,
)
from gac.oauth.base import (
    load_stored_token as _base_load,
)
from gac.oauth.base import (
    perform_oauth_flow as _base_flow,
)
from gac.oauth.base import (
    remove_token as _base_remove,
)
from gac.oauth.base import (
    save_token as _base_save,
)
from gac.utils import get_ssl_verify

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CLAUDE_CODE_CONFIG: dict[str, Any] = {
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
    "provider_key": "claude-code",
    "api_key_env_var": "CLAUDE_CODE_ACCESS_TOKEN",
}

# Extra params for Claude's authorization URL
_EXTRA_AUTH_PARAMS: dict[str, str] = {
    "code": "true",
}

_PROVIDER_KEY = CLAUDE_CODE_CONFIG["provider_key"]
_ENV_VAR = CLAUDE_CODE_CONFIG["api_key_env_var"]


# ---------------------------------------------------------------------------
# Claude Code-specific code exchange
# ---------------------------------------------------------------------------


def _exchange_code(code: str, context: OAuthContext) -> dict[str, Any] | None:
    """Exchange authorization code for access tokens via Anthropic's endpoint."""
    if not context.redirect_uri:
        return None

    payload = {
        "grant_type": "authorization_code",
        "client_id": CLAUDE_CODE_CONFIG["client_id"],
        "code": code,
        "state": context.state,
        "code_verifier": context.code_verifier,
        "redirect_uri": context.redirect_uri,
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "anthropic-beta": "oauth-2025-04-20",
    }

    try:
        response = httpx.post(
            CLAUDE_CODE_CONFIG["token_url"],
            json=payload,
            headers=headers,
            timeout=30,
            verify=get_ssl_verify(),
        )
        if response.status_code == 200:
            tokens: dict[str, Any] = response.json()
            if "expires_at" not in tokens and "expires_in" in tokens:
                tokens["expires_at"] = time.time() + tokens["expires_in"]
            return tokens
        logger.error("Token exchange failed: %s - %s", response.status_code, response.text)
    except Exception as exc:
        logger.error("Token exchange error: %s", exc)
    return None


# ---------------------------------------------------------------------------
# Public API — thin wrappers around base functions
# ---------------------------------------------------------------------------


def save_token(access_token: str, token_data: dict[str, Any] | None = None) -> bool:
    """Save Claude Code access token to TokenStore."""
    return _base_save(_PROVIDER_KEY, _ENV_VAR, access_token, token_data)


def load_stored_token() -> str | None:
    """Load stored Claude Code access token from TokenStore."""
    return _base_load(_PROVIDER_KEY)


def remove_token() -> bool:
    """Remove stored Claude Code access token from TokenStore."""
    return _base_remove(_PROVIDER_KEY, _ENV_VAR)


def is_token_expired() -> bool:
    """Check if the stored Claude Code token has expired (5-minute margin)."""
    return _base_is_expired(_PROVIDER_KEY, margin_seconds=300)


def perform_oauth_flow(quiet: bool = False) -> dict[str, Any] | None:
    """Perform full Claude Code OAuth flow and return tokens."""
    return _base_flow(
        CLAUDE_CODE_CONFIG,
        "Claude Code",
        _exchange_code,
        extra_auth_params=_EXTRA_AUTH_PARAMS,
        quiet=quiet,
    )


def refresh_token_if_expired(quiet: bool = True) -> bool:
    """Re-authenticate the Claude Code token if it has expired.

    ⚠️  Unlike ChatGPT, Claude Code has no HTTP refresh token endpoint.
    This function **opens a browser** and performs a full re-login when
    the token is expired.
    """
    if not is_token_expired():
        return True

    if not quiet:
        logger.info("Claude Code token expired, attempting to refresh...")

    success = authenticate_and_save(quiet=quiet)
    if not success and not quiet:
        logger.error("Failed to refresh Claude Code token")
    return success


def authenticate_and_save(quiet: bool = False) -> bool:
    """Perform OAuth flow and save token.  Returns ``True`` on success."""
    return _base_authenticate(
        CLAUDE_CODE_CONFIG,
        "Claude Code",
        _exchange_code,
        extra_auth_params=_EXTRA_AUTH_PARAMS,
        quiet=quiet,
    )
