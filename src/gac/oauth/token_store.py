"""Token storage for OAuth authentication."""

import json
import os
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict, cast


class OAuthToken(TypedDict, total=False):
    """OAuth token structure."""

    access_token: str
    refresh_token: str | None
    expiry: int
    token_type: str
    scope: str | None
    resource_url: str | None


@dataclass
class TokenStore:
    """Secure file-based token storage for OAuth tokens."""

    base_dir: Path

    def __init__(self, base_dir: Path | None = None):
        if base_dir is None:
            base_dir = Path.home() / ".gac" / "oauth"
        self.base_dir = base_dir
        self._ensure_directory()

    def _ensure_directory(self) -> None:
        """Create the OAuth directory with secure permissions."""
        if not self.base_dir.exists():
            self.base_dir.mkdir(parents=True, mode=0o700)
        else:
            os.chmod(self.base_dir, stat.S_IRWXU)

    def _get_token_path(self, provider: str) -> Path:
        """Get the path for a provider's token file."""
        return self.base_dir / f"{provider}.json"

    def save_token(self, provider: str, token: OAuthToken) -> None:
        """Save a token to file with secure permissions.

        Uses atomic write (temp file + rename) to prevent partial reads.
        """
        token_path = self._get_token_path(provider)
        temp_path = token_path.with_suffix(".tmp")

        with open(temp_path, "w") as f:
            json.dump(token, f, indent=2)

        os.chmod(temp_path, stat.S_IRUSR | stat.S_IWUSR)
        temp_path.rename(token_path)

    def get_token(self, provider: str) -> OAuthToken | None:
        """Retrieve a token from file."""
        token_path = self._get_token_path(provider)
        if not token_path.exists():
            return None

        with open(token_path) as f:
            token_data = json.load(f)
            if isinstance(token_data, dict) and isinstance(token_data.get("access_token"), str):
                return cast(OAuthToken, token_data)
            return None

    def remove_token(self, provider: str) -> None:
        """Remove a token file."""
        token_path = self._get_token_path(provider)
        if token_path.exists():
            token_path.unlink()

    def list_providers(self) -> list[str]:
        """List all providers with stored tokens."""
        if not self.base_dir.exists():
            return []
        return [f.stem for f in self.base_dir.glob("*.json")]
