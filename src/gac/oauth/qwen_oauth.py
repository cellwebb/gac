"""Qwen OAuth device flow implementation.

Implements OAuth 2.0 Device Authorization Grant (RFC 8628) with PKCE.
"""

import base64
import hashlib
import logging
import os
import secrets
import time
import webbrowser
from dataclasses import dataclass, field

import httpx

from gac import __version__
from gac.errors import AIError
from gac.oauth.token_store import OAuthToken, TokenStore
from gac.utils import get_ssl_verify

logger = logging.getLogger(__name__)

QWEN_CLIENT_ID = "f0304373b74a44d2b584a3fb70ca9e56"
USER_AGENT = f"gac/{__version__}"
QWEN_DEVICE_CODE_ENDPOINT = "https://chat.qwen.ai/api/v1/oauth2/device/code"
QWEN_TOKEN_ENDPOINT = "https://chat.qwen.ai/api/v1/oauth2/token"
QWEN_SCOPES = ["openid", "profile", "email", "model.completion"]


@dataclass
class DeviceCodeResponse:
    """Response from the device authorization endpoint."""

    device_code: str
    user_code: str
    verification_uri: str
    verification_uri_complete: str | None
    expires_in: int
    interval: int = 5


@dataclass
class QwenDeviceFlow:
    """Qwen OAuth device flow implementation with PKCE."""

    client_id: str = QWEN_CLIENT_ID
    authorization_endpoint: str = QWEN_DEVICE_CODE_ENDPOINT
    token_endpoint: str = QWEN_TOKEN_ENDPOINT
    scopes: list[str] = field(default_factory=lambda: QWEN_SCOPES.copy())
    _pkce_verifier: str = field(default="", init=False)

    def _generate_pkce(self) -> tuple[str, str]:
        """Generate PKCE code verifier and challenge.

        Returns:
            Tuple of (verifier, challenge) strings.
        """
        verifier = secrets.token_urlsafe(32)
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
        return verifier, challenge

    def initiate_device_flow(self) -> DeviceCodeResponse:
        """Initiate the device authorization flow.

        Returns:
            DeviceCodeResponse with device code and verification URIs.
        """
        verifier, challenge = self._generate_pkce()
        self._pkce_verifier = verifier

        params = {
            "client_id": self.client_id,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }

        if self.scopes:
            params["scope"] = " ".join(self.scopes)

        response = httpx.post(
            self.authorization_endpoint,
            data=params,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "User-Agent": USER_AGENT,
            },
            timeout=30,
            verify=get_ssl_verify(),
        )

        if not response.is_success:
            raise AIError.connection_error(f"Failed to initiate device flow: HTTP {response.status_code}")

        data = response.json()
        return DeviceCodeResponse(
            device_code=data["device_code"],
            user_code=data["user_code"],
            verification_uri=data["verification_uri"],
            verification_uri_complete=data.get("verification_uri_complete"),
            expires_in=data["expires_in"],
            interval=data.get("interval", 5),
        )

    def poll_for_token(self, device_code: str, max_duration: int = 900) -> OAuthToken:
        """Poll the authorization server for an access token.

        Args:
            device_code: Device code from initiation response.
            max_duration: Maximum polling duration in seconds (default 15 minutes).

        Returns:
            OAuthToken with access token and metadata.
        """
        start_time = time.time()
        interval = 5

        while time.time() - start_time < max_duration:
            params = {
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "device_code": device_code,
                "client_id": self.client_id,
                "code_verifier": self._pkce_verifier,
            }

            try:
                response = httpx.post(
                    self.token_endpoint,
                    data=params,
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Accept": "application/json",
                        "User-Agent": USER_AGENT,
                    },
                    timeout=30,
                    verify=get_ssl_verify(),
                )

                if response.is_success:
                    data = response.json()
                    now = int(time.time())
                    expires_in = data.get("expires_in", 3600)

                    return OAuthToken(
                        access_token=data["access_token"],
                        token_type="Bearer",
                        expiry=now + expires_in,
                        refresh_token=data.get("refresh_token"),
                        scope=data.get("scope"),
                        resource_url=data.get("resource_url"),
                    )

                error_data = response.json()
                error = error_data.get("error", "")

                if error == "authorization_pending":
                    time.sleep(interval)
                    continue
                elif error == "slow_down":
                    interval += 5
                    time.sleep(interval)
                    continue
                elif error == "access_denied":
                    raise AIError.authentication_error("Authorization was denied by user")
                elif error == "expired_token":
                    raise AIError.authentication_error("Device code expired. Please try again.")

                raise AIError.connection_error(f"Token request failed: {response.status_code}")

            except httpx.RequestError as e:
                interval = int(min(interval * 1.5, 60))
                logger.debug(f"Network error during polling, retrying in {interval}s: {e}")
                time.sleep(interval)
                continue

        raise AIError.timeout_error("Authorization timeout exceeded. Please try again.")

    def refresh_token(self, refresh_token: str) -> OAuthToken:
        """Refresh an expired access token.

        Args:
            refresh_token: Valid refresh token.

        Returns:
            New OAuthToken with refreshed access token.
        """
        params = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
        }

        response = httpx.post(
            self.token_endpoint,
            data=params,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "User-Agent": USER_AGENT,
            },
            timeout=30,
            verify=get_ssl_verify(),
        )

        if not response.is_success:
            raise AIError.authentication_error(f"Token refresh failed: HTTP {response.status_code}")

        data = response.json()
        now = int(time.time())
        expires_in = data.get("expires_in", 3600)

        return OAuthToken(
            access_token=data["access_token"],
            token_type="Bearer",
            expiry=now + expires_in - 30,
            refresh_token=data.get("refresh_token") or refresh_token,
            scope=data.get("scope"),
            resource_url=data.get("resource_url"),
        )


class QwenOAuthProvider:
    """Qwen OAuth provider for authentication management."""

    name = "qwen"

    def __init__(self, token_store: TokenStore | None = None):
        self.token_store = token_store or TokenStore()
        self.device_flow = QwenDeviceFlow()

    def _is_token_expired(self, token: OAuthToken) -> bool:
        """Check if token is expired or near expiry (30-second buffer)."""
        now = time.time()
        buffer = 30
        return token["expiry"] <= now + buffer

    def initiate_auth(self, open_browser: bool = True) -> None:
        """Initiate the OAuth authentication flow.

        Args:
            open_browser: Whether to automatically open the browser.
        """
        device_response = self.device_flow.initiate_device_flow()

        auth_url = device_response.verification_uri_complete or (
            f"{device_response.verification_uri}?user_code={device_response.user_code}"
        )

        print("\nQwen OAuth Authentication")
        print("-" * 40)
        print("Please visit the following URL to authorize:")
        print(auth_url)
        print(f"\nUser code: {device_response.user_code}")

        if open_browser and self._should_launch_browser():
            print("Opening browser for authentication...")
            try:
                webbrowser.open(auth_url)
            except Exception as e:
                logger.debug(f"Failed to open browser: {e}")
                print("Failed to open browser automatically. Please open the URL manually.")

        print("-" * 40)
        print("Waiting for authorization...\n")

        token = self.device_flow.poll_for_token(device_response.device_code)
        self.token_store.save_token("qwen", token)

        print("Authentication successful!")

    def _should_launch_browser(self) -> bool:
        """Check if we should launch a browser."""
        if os.getenv("SSH_CLIENT") or os.getenv("SSH_TTY"):
            return False
        if not os.getenv("DISPLAY") and os.name != "nt":
            if os.uname().sysname != "Darwin":
                return False
        return True

    def get_token(self) -> OAuthToken | None:
        """Get the current access token, refreshing if needed."""
        token = self.token_store.get_token("qwen")
        if not token:
            return None

        if self._is_token_expired(token):
            return self.refresh_if_needed()

        return token

    def refresh_if_needed(self) -> OAuthToken | None:
        """Refresh the token if expired.

        Returns:
            Refreshed token or None if refresh fails.
        """
        current_token = self.token_store.get_token("qwen")
        if not current_token:
            return None

        if self._is_token_expired(current_token):
            refresh_token = current_token.get("refresh_token")
            if refresh_token:
                try:
                    refreshed_token = self.device_flow.refresh_token(refresh_token)
                    self.token_store.save_token("qwen", refreshed_token)
                    return refreshed_token
                except Exception as e:
                    logger.debug(f"Token refresh failed: {e}")
                    self.token_store.remove_token("qwen")
                    return None
            else:
                self.token_store.remove_token("qwen")
                return None

        return current_token

    def logout(self) -> None:
        """Log out by removing stored tokens."""
        self.token_store.remove_token("qwen")
        print("Successfully logged out from Qwen")

    def is_authenticated(self) -> bool:
        """Check if we have a valid token."""
        token = self.get_token()
        return token is not None
