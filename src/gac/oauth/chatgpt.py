"""ChatGPT OAuth authentication — public API.

Implements PKCE OAuth flow for ChatGPT/Codex API access,
matching OpenAI's Codex CLI auth flow.

Consolidates configuration, token management, JWT parsing, HTTP refresh,
and code exchange into a single module.  Shared infrastructure lives in
:mod:`gac.oauth.base`.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from gac.oauth.base import (
    OAuthContext,
    parse_jwt_claims,
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
    load_stored_tokens as _base_load_all,
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

CHATGPT_OAUTH_CONFIG: dict[str, Any] = {
    "issuer": "https://auth.openai.com",
    "auth_url": "https://auth.openai.com/oauth/authorize",
    "token_url": "https://auth.openai.com/oauth/token",
    "api_base_url": "https://chatgpt.com/backend-api/codex",
    "client_id": "app_EMoamEEZ73f0CkXaXp7hrann",
    "scope": "openid profile email offline_access",
    "redirect_host": "http://localhost",
    "redirect_path": "auth/callback",
    # Preferred port is 1455 (matching Codex CLI), but we try a range if occupied
    "callback_port_range": (1455, 1465),
    "callback_timeout": 120,
    "provider_key": "chatgpt-oauth",
    "api_key_env_var": "CHATGPT_OAUTH_API_KEY",
    "client_version": "0.72.0",
    "originator": "codex_cli_rs",
}

# Known Codex-compatible models
DEFAULT_CODEX_MODELS: list[str] = [
    "gpt-5.5",
    "gpt-5.4",
    "gpt-5.3-instant",
    "gpt-5.3-codex-spark",
    "gpt-5.3-codex",
    "gpt-5.2-codex",
    "gpt-5.2",
]

# Extra parameters appended to the authorization URL for ChatGPT
_EXTRA_AUTH_PARAMS: dict[str, str] = {
    "id_token_add_organizations": "true",
    "codex_cli_simplified_flow": "true",
}

# Keys to pack into the ``extra`` dict of the stored token
_EXTRA_TOKEN_KEYS: tuple[str, ...] = ("id_token", "account_id", "org_id", "plan_type")

_PROVIDER_KEY = CHATGPT_OAUTH_CONFIG["provider_key"]
_ENV_VAR = CHATGPT_OAUTH_CONFIG["api_key_env_var"]


# ---------------------------------------------------------------------------
# ChatGPT-specific code exchange
# ---------------------------------------------------------------------------


def _exchange_code(code: str, context: OAuthContext) -> dict[str, Any] | None:
    """Exchange authorization code for tokens using ChatGPT's token endpoint."""
    if not context.redirect_uri:
        return None

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": context.redirect_uri,
        "client_id": CHATGPT_OAUTH_CONFIG["client_id"],
        "code_verifier": context.code_verifier,
    }

    try:
        response = httpx.post(
            CHATGPT_OAUTH_CONFIG["token_url"],
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
    except Exception as exc:
        logger.error("ChatGPT token exchange failed: %s", exc)
    return None


# ---------------------------------------------------------------------------
# Token refresh (ChatGPT supports HTTP refresh tokens)
# ---------------------------------------------------------------------------


def refresh_access_token() -> str | None:
    """Refresh the access token using the stored refresh token.

    Returns the new access token on success, ``None`` otherwise.

    .. note::
        ``load_stored_tokens()`` flattens the ``extra`` dict (account_id,
        org_id, …) into top-level keys.  ``save_token()`` re-extracts those
        same keys back into ``extra`` via ``_EXTRA_TOKEN_KEYS``.  This
        round-trip works as long as the two stay in sync.
    """
    tokens = load_stored_tokens()
    if not tokens:
        return None

    refresh_token = tokens.get("refresh_token")
    if not refresh_token:
        logger.debug("No refresh_token available for ChatGPT OAuth")
        return None

    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CHATGPT_OAUTH_CONFIG["client_id"],
    }

    try:
        response = httpx.post(
            CHATGPT_OAUTH_CONFIG["token_url"],
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
            verify=get_ssl_verify(),
        )
        if response.status_code == 200:
            new_tokens = response.json()
            merged = dict(tokens)
            new_access_token = new_tokens.get("access_token")
            if not new_access_token:
                logger.error("No access_token in refresh response")
                return None
            merged.update(
                {
                    "access_token": new_access_token,
                    "refresh_token": new_tokens.get("refresh_token", refresh_token),
                    "id_token": new_tokens.get("id_token", tokens.get("id_token")),
                }
            )
            if save_token(merged["access_token"], token_data=merged):
                logger.info("Successfully refreshed ChatGPT OAuth token")
                return str(merged["access_token"])
        else:
            logger.error("Token refresh failed: %s - %s", response.status_code, response.text)
    except Exception as exc:
        logger.error("Token refresh error: %s", exc)
    return None


def refresh_token_if_expired(quiet: bool = True) -> bool:
    """Refresh the ChatGPT OAuth token if it has expired.

    Returns ``True`` if the token is valid (or was successfully refreshed).
    """
    if not is_token_expired():
        return True

    if not quiet:
        logger.info("ChatGPT OAuth token expired, attempting to refresh...")

    refreshed = refresh_access_token()
    if refreshed:
        return True

    if not quiet:
        logger.error("Failed to refresh ChatGPT OAuth token")
    return False


# ---------------------------------------------------------------------------
# Public API — thin wrappers around base functions
# ---------------------------------------------------------------------------


def save_token(access_token: str, token_data: dict[str, Any] | None = None) -> bool:
    """Save ChatGPT OAuth access token to TokenStore."""
    return _base_save(_PROVIDER_KEY, _ENV_VAR, access_token, token_data, _EXTRA_TOKEN_KEYS)


def load_stored_token() -> str | None:
    """Load stored ChatGPT access token from TokenStore."""
    return _base_load(_PROVIDER_KEY)


def load_stored_tokens() -> dict[str, Any] | None:
    """Load all stored ChatGPT token data including extra metadata."""
    return _base_load_all(_PROVIDER_KEY)


def remove_token() -> bool:
    """Remove stored ChatGPT access token from TokenStore."""
    return _base_remove(_PROVIDER_KEY, _ENV_VAR)


def is_token_expired() -> bool:
    """Check if the stored ChatGPT OAuth token has expired."""
    return _base_is_expired(_PROVIDER_KEY, margin_seconds=30)


def perform_oauth_flow(quiet: bool = False) -> dict[str, Any] | None:
    """Perform full ChatGPT OAuth flow and return tokens."""
    return _base_flow(
        CHATGPT_OAUTH_CONFIG,
        "ChatGPT",
        _exchange_code,
        extra_auth_params=_EXTRA_AUTH_PARAMS,
        quiet=quiet,
    )


def authenticate_and_save(quiet: bool = False) -> bool:
    """Perform OAuth flow and save token.  Returns ``True`` on success."""
    return _base_authenticate(
        CHATGPT_OAUTH_CONFIG,
        "ChatGPT",
        _exchange_code,
        extra_auth_params=_EXTRA_AUTH_PARAMS,
        extra_token_keys=_EXTRA_TOKEN_KEYS,
        quiet=quiet,
    )
