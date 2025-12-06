"""Groq API provider for gac."""

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig


class GroqProvider(OpenAICompatibleProvider):
    config = ProviderConfig(
        name="Groq",
        api_key_env="GROQ_API_KEY",
        base_url="https://api.groq.com/openai/v1",
    )

    def _get_api_url(self, model: str | None = None) -> str:
        """Get Groq API URL with /chat/completions endpoint."""
        return f"{self.config.base_url}/chat/completions"
