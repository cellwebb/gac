"""Crof.ai API provider for gac."""

import os

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig


class CrofProvider(OpenAICompatibleProvider):
    """Crof.ai OpenAI-compatible provider with custom base URL."""

    config = ProviderConfig(
        name="Crof",
        api_key_env="CROF_API_KEY",
        base_url="",  # Will be set in __init__
    )

    def __init__(self, config: ProviderConfig):
        """Initialize with base URL from environment or default."""
        base_url = os.getenv("CROF_BASE_URL", "https://crof.ai")
        config.base_url = f"{base_url.rstrip('/')}/v1"
        super().__init__(config)

    def _get_api_url(self, model: str | None = None) -> str:
        """Get Crof API URL with /chat/completions endpoint."""
        return f"{self.config.base_url}/chat/completions"
