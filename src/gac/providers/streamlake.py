"""StreamLake (Vanchin) API provider for gac."""

import os

from gac.errors import AIError
from gac.providers.base import OpenAICompatibleProvider, ProviderConfig
from gac.providers.error_handler import handle_provider_errors


class StreamlakeProvider(OpenAICompatibleProvider):
    """StreamLake (Vanchin) OpenAI-compatible provider with alternative env vars."""

    config = ProviderConfig(
        name="StreamLake",
        api_key_env="STREAMLAKE_API_KEY",
        base_url="https://vanchin.streamlake.ai/api/gateway/v1/endpoints/chat/completions",
    )

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


def _get_streamlake_provider() -> StreamlakeProvider:
    """Lazy getter to initialize provider at call time."""
    return StreamlakeProvider(StreamlakeProvider.config)


@handle_provider_errors("StreamLake")
def call_streamlake_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call StreamLake (Vanchin) chat completions API."""
    provider = _get_streamlake_provider()
    return provider.generate(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
