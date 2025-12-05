# AI Provider Architecture

This directory contains AI provider implementations for GAC (Git Auto Commit). All providers follow a class-based architecture with shared base classes to reduce code duplication and improve maintainability.

## Architecture Overview

```text
ProviderProtocol (Protocol - type contract)
     ↓
BaseConfiguredProvider (ABC - core logic)
     ↓
├── OpenAICompatibleProvider (OpenAI-style APIs)
├── AnthropicCompatibleProvider (Anthropic-style APIs)
└── GenericHTTPProvider (Fully custom implementations)
     ↓
Concrete Providers (e.g., OpenAIProvider, GeminiProvider)
```

## Core Components

### BaseConfiguredProvider

Abstract base class implementing the template method pattern. All providers inherit from this class.

**Key Features:**

- Standardized HTTP handling with httpx
- Common error handling patterns
- Flexible configuration via ProviderConfig
- Template methods for customization:
  - `_get_api_key()` - Load API key from environment
  - `_build_headers()` - Build request headers
  - `_build_request_body()` - Build request body
  - `_get_api_url()` - Get API endpoint URL
  - `_parse_response()` - Parse API response
  - `_make_http_request()` - Execute HTTP request
  - `generate()` - Main entry point

### OpenAICompatibleProvider

Specialized base class for OpenAI-compatible APIs (standard format).

**Request Format:**

```json
{
  "model": "gpt-5",
  "messages": [...],
  "temperature": 0.7,
  "max_tokens": 1024
}
```

**Response Format:**

```json
{
  "choices": [
    {
      "message": {
        "content": "..."
      }
    }
  ]
}
```

**Providers Using This Base:**

- OpenAI, DeepSeek, Together, Fireworks, Cerebras, Mistral, Minimax, Moonshot, Groq, OpenRouter
- Custom OpenAI, Azure OpenAI, LM Studio
- Kimi Coding, Streamlake, Synthetic, Z.AI

### AnthropicCompatibleProvider

Specialized base class for Anthropic-style APIs.

**Request Format:**

```json
{
  "model": "claude-sonnet-4-5",
  "messages": [...],
  "system": "You are a helpful assistant",
  "temperature": 0.7,
  "max_tokens": 1024
}
```

**Response Format:**

```json
{
  "content": [
    {
      "type": "text",
      "text": "..."
    }
  ]
}
```

**Providers Using This Base:**

- Anthropic, Custom Anthropic
- Claude Code

### GenericHTTPProvider

Base class for providers with completely custom API formats.

**Providers Using This Base:**

- Gemini (Google's unique format)
- Replicate (async prediction polling)

## Creating a New Provider

### Step 1: Choose the Right Base Class

```python
from gac.providers.base import OpenAICompatibleProvider, ProviderConfig
from gac.providers.error_handler import handle_provider_errors

# Most providers fit one of these patterns:
# 1. OpenAI-compatible format → inherit from OpenAICompatibleProvider
# 2. Anthropic-compatible format → inherit from AnthropicCompatibleProvider
# 3. Custom format → inherit from GenericHTTPProvider
```

### Step 2: Define Provider Configuration

```python
class MyProvider(OpenAICompatibleProvider):
    config = ProviderConfig(
        name="My Provider",
        api_key_env="MY_PROVIDER_API_KEY",
        base_url="https://api.myprovider.com/v1/chat/completions",
    )
```

### Step 3: Override Template Methods (If Needed)

```python
class MyProvider(OpenAICompatibleProvider):
    # Override only what's needed

    def _build_headers(self) -> dict[str, str]:
        """Custom header handling."""
        headers = super()._build_headers()
        # Add provider-specific headers
        return headers

    def _get_api_url(self, model: str | None = None) -> str:
        """Custom URL construction."""
        if model is None:
            return super()._get_api_url(model)
        return f"https://custom.endpoint/{model}/chat"
```

### Step 4: Create Lazy Getter and Decorated Function

```python
def _get_my_provider() -> MyProvider:
    """Lazy getter to initialize provider at call time."""
    return MyProvider(MyProvider.config)

@handle_provider_errors("My Provider")
def call_my_provider_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call My Provider API."""
    provider = _get_my_provider()
    return provider.generate(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
```

### Step 5: Export in `__init__.py`

```python
# In src/gac/providers/__init__.py
from .my_provider import call_my_provider_api

# Add to PROVIDER_REGISTRY
PROVIDER_REGISTRY = {
    ...
    "my-provider": call_my_provider_api,
    ...
}

# Add to __all__
__all__ = [
    ...
    "call_my_provider_api",
    ...
]
```

## Common Customization Patterns

### Pattern 1: Optional API Key (e.g., Ollama, LM Studio)

```python
def _get_api_key(self) -> str:
    """Get optional API key."""
    api_key = os.getenv(self.config.api_key_env)
    if not api_key:
        return ""  # Optional
    return api_key
```

### Pattern 2: Custom URL Construction (e.g., Azure OpenAI)

```python
def _get_api_url(self, model: str | None = None) -> str:
    """Build custom URL with model in path."""
    if model is None:
        return super()._get_api_url(model)
    return f"{self.endpoint}/openai/deployments/{model}/chat/completions?api-version={self.api_version}"
```

### Pattern 3: Alternative Environment Variables (e.g., Streamlake)

```python
def _get_api_key(self) -> str:
    """Try primary key, then fallback."""
    api_key = os.getenv(self.config.api_key_env)
    if api_key:
        return api_key
    # Fallback to alternative
    api_key = os.getenv("ALTERNATIVE_KEY_ENV")
    if api_key:
        return api_key
    raise AIError.authentication_error("No API key found")
```

### Pattern 4: Model Preprocessing (e.g., Synthetic - adding prefixes)

```python
def _build_request_body(self, messages: list[dict], temperature: float, max_tokens: int, model: str, **kwargs) -> dict[str, Any]:
    """Preprocess model name."""
    data = super()._build_request_body(messages, temperature, max_tokens, model, **kwargs)
    # Add "hf:" prefix for HuggingFace models
    data["model"] = f"hf:{model}"
    return data
```

### Pattern 5: Custom Response Parsing (e.g., LM Studio with text field fallback)

```python
def _parse_response(self, response: dict[str, Any]) -> str:
    """Parse response with fallback."""
    # Try standard OpenAI format first
    choices = response.get("choices")
    if choices:
        content = choices[0].get("message", {}).get("content")
        if content:
            return content

    # Fallback to text field
    content = choices[0].get("text")
    if content:
        return content

    raise AIError.model_error("No content found")
```

### Pattern 6: System Message Handling (e.g., Claude Code)

```python
def _build_request_body(self, messages: list[dict], temperature: float, max_tokens: int, model: str, **kwargs) -> dict[str, Any]:
    """Extract and handle system messages."""
    anthropic_messages = []
    system_instructions = ""

    for msg in messages:
        if msg["role"] == "system":
            system_instructions = msg["content"]
        else:
            anthropic_messages.append(msg)

    # Move system instructions to first user message
    if system_instructions and anthropic_messages:
        anthropic_messages[0]["content"] = f"{system_instructions}\n\n{anthropic_messages[0]['content']}"

    return {
        "messages": anthropic_messages,
        "system": "REQUIRED_FIXED_MESSAGE",
        "temperature": temperature,
        "max_tokens": max_tokens,
        **kwargs,
    }
```

### Pattern 7: Async Operations (e.g., Replicate with polling)

```python
def generate(self, model: str, messages: list[dict], temperature: float = 0.7, max_tokens: int = 1024, **kwargs) -> str:
    """Override for async/polling operations."""
    # Create prediction
    response = httpx.post(url, json=body, headers=headers, ...)
    prediction_id = response.json()["id"]

    # Poll for completion
    while elapsed_time < max_wait_time:
        status_response = httpx.get(f"{url}/{prediction_id}", headers=headers, ...)
        status_data = status_response.json()

        if status_data["status"] == "succeeded":
            return status_data["output"]
        elif status_data["status"] == "failed":
            raise AIError.model_error("Prediction failed")

        time.sleep(wait_interval)
        elapsed_time += wait_interval

    raise AIError.timeout_error("Prediction timed out")
```

## Error Handling

All providers use the `@handle_provider_errors` decorator to normalize error handling:

```python
from gac.providers.error_handler import handle_provider_errors

@handle_provider_errors("My Provider")
def call_my_provider_api(...) -> str:
    # Errors are automatically caught and converted to AIError types
    pass
```

**Error Mapping:**

- HTTP 401 → `AIError.authentication_error()`
- HTTP 429 → `AIError.rate_limit_error()`
- Timeout → `AIError.timeout_error()`
- Connection error → `AIError.connection_error()`
- Other → `AIError.model_error()`

## Testing Providers

Each provider has comprehensive tests in `tests/providers/test_<provider>.py`.

### Test Structure

```python
class TestProviderImports:
    """Test imports."""
    def test_import_provider(self): ...

class TestProviderMocked(BaseProviderTest):
    """Standard mocked tests (inherited from BaseProviderTest)."""
    @property
    def provider_name(self) -> str: return "my-provider"

    @property
    def provider_module(self) -> str: return "gac.providers.my_provider"

    @property
    def api_function(self): return call_my_provider_api

    @property
    def api_key_env_var(self) -> str: return "MY_PROVIDER_API_KEY"

class TestProviderEdgeCases:
    """Provider-specific edge cases."""
    def test_custom_behavior(self): ...

@pytest.mark.integration
class TestProviderIntegration:
    """Real API tests (skipped by default)."""
    def test_real_api_call(self): ...
```

## SSL Verification

All HTTP requests use GAC's SSL verification settings via `get_ssl_verify()`:

```python
from gac.utils import get_ssl_verify

response = httpx.post(url, ..., verify=get_ssl_verify())
```

This respects environment configurations for custom certificates.

## Timeout Configuration

All providers use `ProviderDefaults.HTTP_TIMEOUT` for consistency:

```python
from gac.constants import ProviderDefaults

config = ProviderConfig(
    name="My Provider",
    api_key_env="MY_KEY",
    base_url="https://api.example.com",
    timeout=ProviderDefaults.HTTP_TIMEOUT,  # Default: 120 seconds
)
```

## Provider-Specific Documentation

See individual provider files for detailed documentation:

- `openai.py` - OpenAI API reference
- `anthropic.py` - Anthropic API reference
- `azure_openai.py` - Azure OpenAI configuration
- `gemini.py` - Google Gemini custom format
- `replicate.py` - Async prediction handling
- And others...

## Contributing

When adding a new provider:

1. Follow the architecture and patterns above
2. Write comprehensive tests (unit, mocked, integration)
3. Update `__init__.py` exports
4. Document the provider in its docstring
5. Run `mypy` for type checking: `uv run -- mypy src/gac`
6. Run tests: `uv run -- pytest tests/providers/test_<provider>.py -v`
7. Update this README if adding new patterns

## Best Practices

1. **Lazy Initialization**: Use getter functions to initialize providers at call time, not import time. This allows tests to mock environment variables.

2. **Error Preservation**: Always re-raise `AIError` exceptions without wrapping them. The error decorator handles generic exceptions.

3. **Optional Parameters**: Match superclass signatures exactly, especially for `_get_api_url(model: str | None = None)`.

4. **Response Validation**: Always validate responses for null/empty content before returning.

5. **Configuration Over Code**: Use environment variables and `ProviderConfig` rather than hardcoding values.

6. **Documentation**: Include docstrings with API endpoint references and required environment variables.

7. **Test Coverage**: Aim for 100% test coverage of provider logic.
