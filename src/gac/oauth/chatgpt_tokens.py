"""ChatGPT OAuth token storage, refresh, and JWT parsing."""

from __future__ import annotations

import base64
import json
import logging
import os
import time
from typing import Any

import httpx

from gac.oauth.chatgpt_config import CHATGPT_OAUTH_CONFIG
from gac.oauth.token_store import OAuthToken, TokenStore
from gac.utils import get_ssl_verify

logger = logging.getLogger(__name__)


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
        if isinstance(result, dict):
            return result
        return None
    except Exception as exc:
        logger.error("Failed to parse JWT: %s", exc)
    return None


# ---------------------------------------------------------------------------
# Token storage — uses OAuthToken.extra dict instead of sidecar files
# ---------------------------------------------------------------------------


def _provider_key() -> str:
    return str(CHATGPT_OAUTH_CONFIG["provider_key"])


def save_token(access_token: str, token_data: dict[str, Any] | None = None) -> bool:
    """Save access token to TokenStore.

    Extra metadata (account_id, org_id, id_token, etc.) is stored in the
    ``extra`` field of the ``OAuthToken`` TypedDict — no sidecar files.
    """
    store = TokenStore()
    try:
        token: OAuthToken = {
            "access_token": access_token,
            "token_type": "Bearer",
        }

        # Extract expiry from JWT claims if available
        claims = parse_jwt_claims(access_token)
        if claims and "exp" in claims:
            token["expiry"] = int(claims["exp"])

        if token_data:
            if "refresh_token" in token_data:
                token["refresh_token"] = token_data["refresh_token"]
            if "expires_at" in token_data:
                token["expiry"] = int(token_data["expires_at"])
            elif "expires_in" in token_data:
                token["expiry"] = int(time.time() + token_data["expires_in"])

            # Pack non-standard fields into the extra dict
            extra: dict[str, Any] = {}
            for key in ("id_token", "account_id", "org_id", "plan_type"):
                if key in token_data and token_data[key]:
                    extra[key] = token_data[key]
            if extra:
                token["extra"] = extra

        store.save_token(_provider_key(), token)
        os.environ[CHATGPT_OAUTH_CONFIG["api_key_env_var"]] = access_token
        return True
    except Exception as exc:
        logger.error("Failed to save ChatGPT OAuth token: %s", exc)
    return False


def load_stored_token() -> str | None:
    """Load stored access token from TokenStore."""
    store = TokenStore()
    token = store.get_token(_provider_key())
    if token:
        return token.get("access_token")
    return None


def load_stored_tokens() -> dict[str, Any] | None:
    """Load all stored token data including extra metadata."""
    store = TokenStore()
    token = store.get_token(_provider_key())
    if not token:
        return None
    result: dict[str, Any] = dict(token)
    # Flatten the extra dict into the top-level result
    extra = token.get("extra")
    if extra and isinstance(extra, dict):
        result.update(extra)
    return result


def remove_token() -> bool:
    """Remove stored access token from TokenStore."""
    store = TokenStore()
    try:
        store.remove_token(_provider_key())
        os.environ.pop(CHATGPT_OAUTH_CONFIG["api_key_env_var"], None)
        return True
    except Exception as exc:
        logger.error("Failed to remove ChatGPT OAuth token: %s", exc)
    return False


# ---------------------------------------------------------------------------
# Token expiry & refresh
# ---------------------------------------------------------------------------


def is_token_expired() -> bool:
    """Check if the stored ChatGPT OAuth token has expired.

    Returns True if the token is expired or close to expiring (within 30 sec).
    """
    store = TokenStore()
    token = store.get_token(_provider_key())
    if not token:
        return True

    expiry = token.get("expiry")
    if not expiry:
        # Check JWT claims directly
        access_token = token.get("access_token", "")
        claims = parse_jwt_claims(access_token)
        if claims and "exp" in claims:
            exp_value = claims["exp"]
            if isinstance(exp_value, (int, float)):
                return time.time() > exp_value - 30
        # No expiry info, assume still valid
        return False

    return time.time() >= (expiry - 30)


def refresh_access_token() -> str | None:
    """Refresh the access token using the refresh token.

    Returns new access token if refresh succeeded, None otherwise.
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
            # Merge with existing tokens
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

    Returns True if token is valid (or was successfully refreshed), False otherwise.
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
