"""Replicate API provider for gac."""

import time
from typing import Any

import httpx

from gac.errors import AIError
from gac.providers.base import GenericHTTPProvider, ProviderConfig
from gac.utils import get_ssl_verify


class ReplicateProvider(GenericHTTPProvider):
    """Replicate API provider with async prediction polling."""

    config = ProviderConfig(
        name="Replicate",
        api_key_env="REPLICATE_API_TOKEN",
        base_url="https://api.replicate.com/v1",
    )

    def _get_api_url(self, model: str | None = None) -> str:
        """Get Replicate API URL with /predictions endpoint."""
        return f"{self.config.base_url}/predictions"

    def _build_headers(self) -> dict[str, str]:
        """Build headers with Token-based authorization."""
        headers = super()._build_headers()
        # Replace Bearer token with Token format
        if "Authorization" in headers:
            del headers["Authorization"]
        headers["Authorization"] = f"Token {self.api_key}"
        return headers

    def _build_request_body(
        self, messages: list[dict[str, Any]], temperature: float, max_tokens: int, model: str, **kwargs: Any
    ) -> dict[str, Any]:
        """Build Replicate prediction payload with message-to-prompt conversion."""
        # Convert messages to a single prompt for Replicate
        prompt_parts = []
        system_message = None

        for message in messages:
            role = message.get("role")
            content = message.get("content", "")

            if role == "system":
                system_message = content
            elif role == "user":
                prompt_parts.append(f"Human: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")

        # Add system message at the beginning if present
        if system_message:
            prompt_parts.insert(0, f"System: {system_message}")

        # Add final assistant prompt
        prompt_parts.append("Assistant:")
        full_prompt = "\n\n".join(prompt_parts)

        # Replicate prediction payload
        return {
            "version": model,  # Replicate uses version string as model identifier
            "input": {
                "prompt": full_prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
        }

    def generate(
        self,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> str:
        """Override generate to handle Replicate's async polling mechanism."""
        # Build request components
        try:
            url = self._get_api_url(model)
        except AIError:
            raise
        except Exception as e:
            raise AIError.model_error(f"Error calling {self.config.name} AI API: {e!s}") from e

        try:
            headers = self._build_headers()
        except AIError:
            raise
        except Exception as e:
            raise AIError.model_error(f"Error calling {self.config.name} AI API: {e!s}") from e

        try:
            body = self._build_request_body(messages, temperature, max_tokens, model, **kwargs)
        except AIError:
            raise
        except Exception as e:
            raise AIError.model_error(f"Error calling {self.config.name} AI API: {e!s}") from e

        # Create prediction
        try:
            response = httpx.post(url, json=body, headers=headers, timeout=self.config.timeout, verify=get_ssl_verify())
            response.raise_for_status()
            prediction_data = response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise AIError.rate_limit_error(f"Replicate API rate limit exceeded: {e.response.text}") from e
            elif e.response.status_code == 401:
                raise AIError.authentication_error(f"Replicate API authentication failed: {e.response.text}") from e
            raise AIError.model_error(f"Replicate API error: {e.response.status_code} - {e.response.text}") from e
        except httpx.TimeoutException as e:
            raise AIError.timeout_error(f"Replicate API request timed out: {str(e)}") from e
        except Exception as e:
            raise AIError.model_error(f"Error calling Replicate API: {str(e)}") from e

        # Poll for completion
        get_url = f"https://api.replicate.com/v1/predictions/{prediction_data['id']}"
        max_wait_time = 120
        wait_interval = 2
        elapsed_time = 0

        while elapsed_time < max_wait_time:
            try:
                get_response = httpx.get(get_url, headers=headers, timeout=self.config.timeout, verify=get_ssl_verify())
                get_response.raise_for_status()
                status_data = get_response.json()

                if status_data["status"] == "succeeded":
                    content = status_data["output"]
                    if not content:
                        raise AIError.model_error("Replicate API returned empty content")
                    return content
                elif status_data["status"] == "failed":
                    raise AIError.model_error(
                        f"Replicate prediction failed: {status_data.get('error', 'Unknown error')}"
                    )
                elif status_data["status"] in ["starting", "processing"]:
                    time.sleep(wait_interval)
                    elapsed_time += wait_interval
                else:
                    raise AIError.model_error(f"Replicate API returned unknown status: {status_data['status']}")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    raise AIError.rate_limit_error(f"Replicate API rate limit exceeded: {e.response.text}") from e
                raise AIError.model_error(f"Replicate API error: {e.response.status_code} - {e.response.text}") from e
            except httpx.TimeoutException as e:
                raise AIError.timeout_error(f"Replicate API request timed out: {str(e)}") from e
            except AIError:
                raise
            except Exception as e:
                raise AIError.model_error(f"Error polling Replicate API: {str(e)}") from e

        raise AIError.timeout_error("Replicate API prediction timed out")
