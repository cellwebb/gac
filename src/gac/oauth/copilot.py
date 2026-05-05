"""GitHub Copilot OAuth — Device Flow authentication and session token management.

Implements GitHub's Device Flow for browser-based authentication (no callback
server needed), then exchanges the long-lived OAuth token for short-lived
Copilot session tokens (~30 min) that grant access to the Copilot API.

This is fundamentally different from the PKCE-based flows in ``base.py``:
instead of binding a local HTTP server, we post a device code to GitHub
and poll until the user authorizes in their browser.
"""

from __future__ import annotations

import json
import logging
import re
import time
from pathlib import Path
from typing import Any

import httpx

from gac.oauth.base import (
    load_stored_token as _base_load,
)
from gac.oauth.base import (
    load_stored_tokens as _base_load_all,
)
from gac.oauth.base import (
    remove_token as _base_remove,
)
from gac.oauth.base import (
    save_token as _base_save,
)
from gac.oauth.token_store import TokenStore
from gac.utils import get_ssl_verify

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

COPILOT_OAUTH_CONFIG: dict[str, Any] = {
    # Copilot session-token endpoint (github.com)
    "github_token_url": "https://api.github.com/copilot_internal/v2/token",
    # GHE template: {host} is replaced at runtime
    "ghe_token_url_template": "https://{host}/api/v3/copilot_internal/v2/token",
    # Default Copilot API base
    "api_base_url": "https://api.githubcopilot.com",
    # GHE API base template — used when the session response doesn't include endpoints.api
    "ghe_api_base_template": "https://{host}",
    # Headers expected by the Copilot API
    "editor_version": "JetBrains-IU/2024.3",
    "editor_plugin_version": "copilot/2.0.0",
    "copilot_integration_id": "vscode-chat",
    "openai_intent": "conversation-panel",
}

DEVICE_FLOW_CONFIG: dict[str, Any] = {
    "client_id": "Iv1.b507a08c87ecfe98",
    "scope": "read:user",
    # {host} is replaced at runtime
    "device_code_url": "https://{host}/login/device/code",
    "access_token_url": "https://{host}/login/oauth/access_token",
    "default_poll_interval": 5,
    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
}

# Known Copilot models — informational only (shown after login).
# This list will go stale; new Copilot models appear frequently.
_PROVIDER_KEY = "copilot"
_ENV_VAR = "COPILOT_OAUTH_TOKEN"

# Strict hostname validation: labels of alphanumeric + hyphens, separated by dots.
_HOSTNAME_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*$")

# Blocked hostnames that are structurally valid but unsafe for URL interpolation.
# Covers loopback, link-local, and RFC 1918 private ranges.
_BLOCKED_HOSTNAMES: set[str] = {"localhost"}
_PRIVATE_IP_RE = re.compile(
    r"^(?:"
    r"127\."  # loopback
    r"|10\."  # 10.0.0.0/8
    r"|172\.(1[6-9]|2\d|3[01])\."  # 172.16.0.0/12
    r"|192\.168\."  # 192.168.0.0/16
    r"|0\."  # 0.0.0.0/8
    r")"
)


# ---------------------------------------------------------------------------
# Host validation — defense-in-depth against SSRF / URL injection
# ---------------------------------------------------------------------------


def _normalize_host(raw_host: str) -> str | None:
    """Validate and normalize a GitHub hostname for safe URL interpolation.

    Returns the cleaned lowercase hostname, or ``None`` if invalid.
    Rejects ports, URL-structural characters, CRLF, percent-encoding,
    private/loopback IP addresses, ``localhost``, and any input that
    doesn't look like a valid DNS hostname.
    """
    host = raw_host.strip().lower()
    if not host:
        return "github.com"
    # Reject any character that could break out of the hostname slot
    for marker in ("://", "/", "\\", "@", "?", "#", ":", "%", "\t", "\r", "\n"):
        if marker in host:
            return None
    host = host.rstrip(".")
    if not _HOSTNAME_RE.match(host):
        return None
    # Reject known-dangerous hostnames (loopback, private IPs)
    if host in _BLOCKED_HOSTNAMES or _PRIVATE_IP_RE.match(host):
        return None
    return host


def _require_valid_host(host: str) -> str:
    """Validate *host* and return it, or raise ``ValueError``."""
    normalized = _normalize_host(host)
    if normalized is None:
        raise ValueError(f"Invalid or unsafe hostname: {host!r}")
    return normalized


# ---------------------------------------------------------------------------
# Session cache path
# ---------------------------------------------------------------------------


def _session_cache_path(base_dir: Path) -> Path:
    """Path for caching short-lived Copilot session tokens."""
    return base_dir / "copilot_session.json"


# ---------------------------------------------------------------------------
# Token storage — wraps base.py where possible, Copilot-specific otherwise
# ---------------------------------------------------------------------------


def save_token(oauth_token: str, host: str = "github.com", user: str = "") -> bool:
    """Persist a Device Flow OAuth token to TokenStore."""
    token_data: dict[str, Any] = {"host": host}
    if user:
        token_data["user"] = user
    return _base_save(_PROVIDER_KEY, _ENV_VAR, oauth_token, token_data, extra_keys=("host", "user"))


def load_stored_token() -> str | None:
    """Load stored Copilot OAuth token from TokenStore."""
    return _base_load(_PROVIDER_KEY)


def load_stored_tokens() -> dict[str, Any] | None:
    """Load all stored Copilot token data including host."""
    return _base_load_all(_PROVIDER_KEY)


def remove_token() -> bool:
    """Remove stored Copilot tokens and session cache."""
    if not _base_remove(_PROVIDER_KEY, _ENV_VAR):
        return False
    # Also clear the session cache file (Copilot-specific)
    try:
        cache_path = _session_cache_path(TokenStore().base_dir)
        if cache_path.exists():
            cache_path.unlink()
    except Exception as exc:
        logger.debug("Could not remove session cache: %s", exc)
    return True


def is_token_expired() -> bool:
    """Check if the stored Copilot token is missing.

    Unlike ChatGPT/Claude Code, GitHub OAuth tokens don't carry a JWT
    expiry — they remain valid until revoked.  This function only checks
    for presence, not actual validity.
    """
    return load_stored_token() is None


# ---------------------------------------------------------------------------
# Device Flow — browser-based GitHub OAuth
# ---------------------------------------------------------------------------


def start_device_flow(host: str = "github.com") -> dict[str, Any] | None:
    """Initiate the GitHub Device Flow.

    Returns a dict with ``device_code``, ``user_code``, ``verification_uri``,
    ``expires_in``, and ``interval`` on success, or ``None`` on failure.
    """
    try:
        host = _require_valid_host(host)
    except ValueError:
        logger.warning("Invalid host for Device Flow: %s", host)
        return None

    url = DEVICE_FLOW_CONFIG["device_code_url"].format(host=host)
    payload = {
        "client_id": DEVICE_FLOW_CONFIG["client_id"],
        "scope": DEVICE_FLOW_CONFIG["scope"],
    }
    try:
        response = httpx.post(
            url,
            data=payload,
            headers={"Accept": "application/json"},
            timeout=30,
            verify=get_ssl_verify(),
        )
        if response.status_code == 200:
            data: dict[str, Any] = response.json()
            if data.get("device_code") and data.get("user_code"):
                return data
            logger.warning("Device flow response missing required fields: %s", data)
        else:
            logger.warning("Device flow initiation failed: %s %s", response.status_code, response.text[:300])
    except Exception as exc:
        logger.warning("Device flow error: %s", exc)
    return None


def poll_for_token(
    device_code: str,
    host: str = "github.com",
    interval: int = 5,
    expires_in: int = 900,
) -> str | None:
    """Poll GitHub until the user completes the Device Flow authorization.

    Returns the OAuth ``access_token`` on success, or ``None``.
    """
    try:
        host = _require_valid_host(host)
    except ValueError:
        logger.warning("Invalid host for token poll: %s", host)
        return None

    url = DEVICE_FLOW_CONFIG["access_token_url"].format(host=host)
    payload = {
        "client_id": DEVICE_FLOW_CONFIG["client_id"],
        "device_code": device_code,
        "grant_type": DEVICE_FLOW_CONFIG["grant_type"],
    }
    headers = {"Accept": "application/json"}

    deadline = time.time() + expires_in
    poll_interval = max(interval, DEVICE_FLOW_CONFIG["default_poll_interval"])

    while time.time() < deadline:
        time.sleep(poll_interval)
        try:
            response = httpx.post(
                url,
                data=payload,
                headers=headers,
                timeout=30,
                verify=get_ssl_verify(),
            )
            data = response.json() if response.status_code == 200 else {}
        except Exception as exc:
            logger.warning("Device flow poll error: %s", exc)
            continue

        token: str | None = data.get("access_token")
        if token:
            return token

        error = data.get("error", "")
        if error == "authorization_pending":
            continue
        if error == "slow_down":
            poll_interval += 5
            continue
        if error in ("expired_token", "access_denied", "unsupported_grant_type"):
            logger.warning("Device flow denied or expired: %s", error)
            return None
        logger.debug("Device flow poll returned: %s", data)

    return None


# ---------------------------------------------------------------------------
# Session token exchange — OAuth token → short-lived Copilot API token
# ---------------------------------------------------------------------------

# In-memory session cache keyed by (host, oauth_token[:16])
_session_cache: dict[str, dict[str, Any]] = {}

# API endpoint discovered during token exchange per host
_host_api_endpoints: dict[str, str] = {}


def _session_endpoint(host: str) -> str:
    """Return the Copilot session-token endpoint for the given host."""
    if host == "github.com":
        return str(COPILOT_OAUTH_CONFIG["github_token_url"])
    return str(COPILOT_OAUTH_CONFIG["ghe_token_url_template"].format(host=host))


def _session_headers(oauth_token: str) -> dict[str, str]:
    """Build headers for the Copilot session-token endpoint."""
    return {
        "Authorization": f"token {oauth_token}",
        "Accept": "application/json",
        "Editor-Version": COPILOT_OAUTH_CONFIG["editor_version"],
        "Editor-Plugin-Version": COPILOT_OAUTH_CONFIG["editor_plugin_version"],
        "Copilot-Integration-Id": COPILOT_OAUTH_CONFIG["copilot_integration_id"],
    }


def _derive_api_endpoint(host: str, endpoints: dict[str, Any] | None) -> str:
    """Derive the Copilot API base URL from the session response.

    For github.com the session response includes ``endpoints.api``.
    For GHE the response may omit it, in which case we fall back to the
    GHE host itself rather than the github.com cloud API.
    """
    if endpoints:
        api = str(endpoints.get("api", "")).rstrip("/")
        if api:
            return api
    if host == "github.com":
        return str(COPILOT_OAUTH_CONFIG["api_base_url"])
    return str(COPILOT_OAUTH_CONFIG["ghe_api_base_template"].format(host=host))


def exchange_for_session_token(oauth_token: str, host: str = "github.com") -> dict[str, Any] | None:
    """Exchange a GitHub OAuth token for a short-lived Copilot session token.

    Returns a dict with ``token``, ``expires_at``, and ``api_endpoint``,
    or ``None`` on failure.
    """
    url = _session_endpoint(host)
    headers = _session_headers(oauth_token)
    try:
        response = httpx.get(url, headers=headers, timeout=30, verify=get_ssl_verify())
        if response.status_code == 200:
            data = response.json()
            token_str = data.get("token")
            expires_at = data.get("expires_at", 0)
            if token_str:
                endpoints = data.get("endpoints") or {}
                api_endpoint = _derive_api_endpoint(host, endpoints)
                _host_api_endpoints[host] = api_endpoint
                result = {
                    "token": token_str,
                    "expires_at": float(expires_at),
                    "api_endpoint": api_endpoint,
                }
                _persist_session(result, host, oauth_token)
                return result
            logger.warning("Token endpoint returned 200 but no 'token' field")
        elif response.status_code == 401:
            logger.warning("Copilot token exchange returned 401 — OAuth token may be revoked.")
        else:
            logger.warning("Copilot token exchange failed: %s %s", response.status_code, response.text[:200])
    except Exception as exc:
        logger.warning("Copilot token exchange error: %s", exc)
    return None


def _persist_session(session: dict[str, Any], host: str, oauth_token: str = "") -> None:
    """Write session token to disk for reuse after restarts."""
    try:
        path = _session_cache_path(TokenStore().base_dir)
        data: dict[str, Any] = {}
        if path.exists():
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        data[host] = {
            "token": session["token"],
            "expires_at": session["expires_at"],
            "api_endpoint": session.get("api_endpoint", ""),
            "oauth_fingerprint": oauth_token[:16] if oauth_token else "",
        }
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
        path.chmod(0o600)
    except Exception as exc:
        logger.debug("Could not persist session token: %s", exc)


def _load_persisted_session(host: str, oauth_token: str = "") -> dict[str, Any] | None:
    """Load a previously persisted session token from disk."""
    try:
        path = _session_cache_path(TokenStore().base_dir)
        if not path.exists():
            return None
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        entry = data.get(host)
        if entry:
            stored_fp = entry.get("oauth_fingerprint", "")
            if oauth_token and stored_fp and stored_fp != oauth_token[:16]:
                return None
            api_endpoint = entry.get("api_endpoint", "")
            if not api_endpoint:
                api_endpoint = _derive_api_endpoint(host, None)
            if api_endpoint:
                _host_api_endpoints[host] = api_endpoint
            return {
                "token": entry["token"],
                "expires_at": float(entry["expires_at"]),
                "api_endpoint": api_endpoint,
            }
    except Exception as exc:
        logger.debug("Could not load persisted session: %s", exc)
    return None


def get_valid_session_token(oauth_token: str, host: str = "github.com") -> str | None:
    """Return a valid Copilot session token, refreshing if needed.

    Checks in-memory cache → on-disk cache → exchanges for a new one.
    Returns the raw bearer token string or ``None``.
    """
    cache_key = f"{host}:{oauth_token[:16]}"

    # 1) In-memory cache
    cached = _session_cache.get(cache_key)
    if cached and cached.get("expires_at", 0) > time.time() + 60:
        return str(cached["token"])

    # 2) On-disk cache
    persisted = _load_persisted_session(host, oauth_token)
    if persisted and persisted.get("expires_at", 0) > time.time() + 60:
        _session_cache[cache_key] = persisted
        return str(persisted["token"])

    # 3) Exchange
    new_session = exchange_for_session_token(oauth_token, host)
    if new_session:
        _session_cache[cache_key] = new_session
        return str(new_session["token"])

    return None


def get_api_endpoint(host: str = "github.com") -> str:
    """Return the Copilot API base URL for the given host."""
    return _host_api_endpoints.get(host, _derive_api_endpoint(host, None))


def clear_caches() -> None:
    """Reset all in-memory session and endpoint caches."""
    _session_cache.clear()
    _host_api_endpoints.clear()


# ---------------------------------------------------------------------------
# Public API — perform full login/logout
# ---------------------------------------------------------------------------


def perform_oauth_flow(host: str = "github.com", quiet: bool = False) -> str | None:
    """Perform the full Device Flow login and return the OAuth token.

    Returns the OAuth ``access_token`` on success, or ``None``.
    """
    import webbrowser

    try:
        host = _require_valid_host(host)
    except ValueError:
        if not quiet:
            print(f"❌ Invalid hostname: {host!r}")
        return None

    device_resp = start_device_flow(host)
    if not device_resp:
        if not quiet:
            print("❌ Failed to start Device Flow. Check your network connection.")
        return None

    user_code = device_resp["user_code"]
    # Use the validated host to construct fallback URI (never raw input)
    verification_uri = device_resp.get("verification_uri", f"https://{host}/login/device")
    expires_in = int(device_resp.get("expires_in", 900))
    interval = int(device_resp.get("interval", 5))

    if not quiet:
        print(f"\n🔑 Your one-time code:  {user_code}")
        print(f"   Open {verification_uri} and enter the code above.\n")

    try:
        webbrowser.open(verification_uri)
    except Exception:
        if not quiet:
            print(f"   Please open: {verification_uri}\n")

    if not quiet:
        print("⏳ Waiting for authorization in the browser…")

    oauth_token = poll_for_token(
        device_code=device_resp["device_code"],
        host=host,
        interval=interval,
        expires_in=expires_in,
    )

    if not oauth_token:
        if not quiet:
            print("❌ Authorization not completed in time, or was denied.")
        return None

    if not quiet:
        print("✅ GitHub authorization successful!")
    return oauth_token


def authenticate_and_save(host: str = "github.com", quiet: bool = False) -> bool:
    """Perform Device Flow login, exchange for session token, and save.

    Returns ``True`` on success.
    """
    try:
        host = _require_valid_host(host)
    except ValueError:
        if not quiet:
            print(f"❌ Invalid hostname: {host!r}")
        return False

    oauth_token = perform_oauth_flow(host=host, quiet=quiet)
    if not oauth_token:
        return False

    if not save_token(oauth_token, host=host):
        if not quiet:
            print("⚠️  Token obtained but could not be saved.")
        return False

    # Verify we can get a Copilot session token
    if not quiet:
        print("   Exchanging for Copilot session token…")

    session = get_valid_session_token(oauth_token, host)
    if not session:
        if not quiet:
            print("⚠️  Got a GitHub token but could not obtain a Copilot session token.")
            print("   Your GitHub account may not have Copilot access.")
        return False

    if not quiet:
        print("✅ Copilot session token obtained!")
        print("   Use: gac -m copilot:gpt-4o-mini")

    return True


def refresh_token_if_expired(quiet: bool = True) -> bool:
    """Check if Copilot auth is valid by attempting a session token exchange.

    Unlike ChatGPT, Copilot tokens don't expire in the traditional sense —
    the session token is auto-refreshed via :func:`get_valid_session_token`.
    This function just verifies the OAuth token is still valid.
    """
    tokens = load_stored_tokens()
    if not tokens:
        return False

    oauth_token = tokens.get("access_token")
    host = tokens.get("host", "github.com")

    if not oauth_token:
        return False

    session = get_valid_session_token(oauth_token, host)
    return session is not None
