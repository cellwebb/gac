"""Replicate API provider for gac."""

import os

import httpx

from gac.errors import AIError
from gac.utils import get_ssl_verify


def call_replicate_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call Replicate API directly."""
    api_key = os.getenv("REPLICATE_API_TOKEN")
    if not api_key:
        raise AIError.authentication_error("REPLICATE_API_TOKEN not found in environment variables")

    # Replicate uses a different endpoint for language models
    url = "https://api.replicate.com/v1/predictions"
    headers = {"Authorization": f"Token {api_key}", "Content-Type": "application/json"}

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
    data = {
        "version": model,  # Replicate uses version string as model identifier
        "input": {
            "prompt": full_prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
    }

    try:
        # Create prediction
        response = httpx.post(url, headers=headers, json=data, timeout=120, verify=get_ssl_verify())
        response.raise_for_status()
        prediction_data = response.json()

        # Get the prediction URL to check status
        get_url = f"https://api.replicate.com/v1/predictions/{prediction_data['id']}"

        # Poll for completion (Replicate predictions are async)
        max_wait_time = 120
        wait_interval = 2
        elapsed_time = 0

        while elapsed_time < max_wait_time:
            get_response = httpx.get(get_url, headers=headers, timeout=120, verify=get_ssl_verify())
            get_response.raise_for_status()
            status_data = get_response.json()

            if status_data["status"] == "succeeded":
                content = status_data["output"]
                if not content:
                    raise AIError.model_error("Replicate API returned empty content")
                return content
            elif status_data["status"] == "failed":
                raise AIError.model_error(f"Replicate prediction failed: {status_data.get('error', 'Unknown error')}")
            elif status_data["status"] in ["starting", "processing"]:
                import time

                time.sleep(wait_interval)
                elapsed_time += wait_interval
            else:
                raise AIError.model_error(f"Replicate API returned unknown status: {status_data['status']}")

        raise AIError.timeout_error("Replicate API prediction timed out")

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
