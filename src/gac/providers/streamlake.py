"""StreamLake (Vanchin) API provider for gac."""

import os

from gac.errors import AIError
from gac.providers.base import OpenAICompatibleProvider, ProviderConfig


class StreamlakeProvider(OpenAICompatibleProvider):
    """StreamLake (Vanchin) OpenAI-compatible provider with alternative env vars."""

    config = ProviderConfig(
        name="StreamLake",
        api_key_env="STREAMLAKE_API_KEY",
        base_url="https://vanchin.streamlake.ai/api/gateway/v1/endpoints",
    )

    def _get_api_url(self, model: str | None = None) -> str:
        """Get StreamLake API URL with /chat/completions endpoint."""
        return f"{self.config.base_url}/chat/completions"

    def _get_api_key(self) -> str:
        """Get API key from environment with fallback to VC_API_KEY."""
        api_key = os.getenv(self.config.api_key_env)
        if not api_key:
            api_key = os.getenv("VC_API_KEY")
        if not api_key:
            raise AIError.authentication_error(
                "STREAMLAKE_API_KEY not found in environment variables (VC_API_KEY alias also not set)"
            )
        return api_key
