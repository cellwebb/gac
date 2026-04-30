"""Qwen Cloud API providers for gac.

Two variants:
- QwenAPIProvider: API key access via Qwen Cloud (international endpoint)
- QwenAPICNProvider: API key access via Qwen Cloud (mainland China endpoint)

QwenProvider (OAuth-based) is retained as a deprecation stub. Qwen discontinued
Qwen Code plans, including the free tier, on 2026-04-15. See
https://github.com/QwenLM/qwen-code/issues/3203.
"""

from typing import Any

from gac.errors import AIError
from gac.providers.base import BaseConfiguredProvider, OpenAICompatibleProvider, ProviderConfig

QWEN_CLOUD_INTL_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
QWEN_CLOUD_CN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

_QWEN_OAUTH_DEPRECATION_MESSAGE = (
    "Qwen Code (OAuth) is no longer available. Qwen discontinued Qwen Code plans, "
    "including the free tier, on 2026-04-15 "
    "(see https://github.com/QwenLM/qwen-code/issues/3203). "
    "Switch to 'qwen-api' (international) or 'qwen-api-cn' (mainland China) and provide a "
    "QWEN_API_KEY from https://dashscope.aliyuncs.com. Run 'gac model' to reconfigure."
)


class QwenProvider(BaseConfiguredProvider):
    """Deprecation stub for the retired Qwen Code (OAuth) provider."""

    config = ProviderConfig(
        name="Qwen Code (OAuth)",
        api_key_env="",
        base_url="",
    )

    def __init__(self, config: ProviderConfig):
        raise AIError.authentication_error(_QWEN_OAUTH_DEPRECATION_MESSAGE)

    def _build_request_body(
        self, messages: list[dict[str, Any]], temperature: float, max_tokens: int, model: str, **kwargs: Any
    ) -> dict[str, Any]:
        raise AIError.authentication_error(_QWEN_OAUTH_DEPRECATION_MESSAGE)

    def _parse_response(self, response: dict[str, Any]) -> str:
        raise AIError.authentication_error(_QWEN_OAUTH_DEPRECATION_MESSAGE)

    def generate(
        self,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> tuple[str, int, int, int]:
        raise AIError.authentication_error(_QWEN_OAUTH_DEPRECATION_MESSAGE)


class QwenAPIProvider(OpenAICompatibleProvider):
    """Qwen Cloud API provider (international endpoint) with OpenAI-compatible format."""

    config = ProviderConfig(
        name="Qwen API",
        api_key_env="QWEN_API_KEY",
        base_url=QWEN_CLOUD_INTL_BASE_URL,
    )

    def _get_api_url(self, model: str | None = None) -> str:
        """Get Qwen Cloud API URL with /chat/completions endpoint."""
        return f"{self.config.base_url}/chat/completions"


class QwenAPICNProvider(OpenAICompatibleProvider):
    """Qwen Cloud API provider (mainland China endpoint) with OpenAI-compatible format."""

    config = ProviderConfig(
        name="Qwen API CN",
        api_key_env="QWEN_API_KEY",
        base_url=QWEN_CLOUD_CN_BASE_URL,
    )

    def _get_api_url(self, model: str | None = None) -> str:
        """Get Qwen Cloud CN API URL with /chat/completions endpoint."""
        return f"{self.config.base_url}/chat/completions"
