# GAC Codebase Improvement Plan

Prioritized by effort vs impact. Low-hanging fruit first.

---

## Phase 1: Quick Wins (Low Effort, High Impact)

### 1.1 Replace Assertions with Proper Validation

**Files**: `main.py` (lines 236, 553, 776, 780, 784, 885)

**Current**:

```python
assert warning_limit_val is not None
warning_limit = int(warning_limit_val)
```

**Change to**:

```python
if warning_limit_val is None:
    raise ConfigError("warning_limit_tokens configuration missing")
warning_limit = int(warning_limit_val)
```

**Effort**: ~30 minutes
**Impact**: Prevents silent failures when Python runs with `-O`

---

### 1.2 Add Consistent Logging to Providers

**Files**: 23 provider files missing logging

**Add to each provider**:

```python
import logging
logger = logging.getLogger(__name__)

# Before API call:
logger.debug(f"Calling {PROVIDER_NAME} API with model={model}")

# After response:
logger.debug(f"{PROVIDER_NAME} response received, status={response.status_code}")
```

**Effort**: ~1 hour
**Impact**: Enables debugging of provider-specific issues

---

### 1.3 Extract Timeout to Constant

**Files**: All 28 provider files, `constants.py`

**Add to `constants.py`**:

```python
class ProviderDefaults:
    HTTP_TIMEOUT = 120  # seconds
```

**Update providers**:

```python
from gac.constants import ProviderDefaults
response = httpx.post(url, headers=headers, json=data, timeout=ProviderDefaults.HTTP_TIMEOUT)
```

**Effort**: ~30 minutes
**Impact**: Single place to tune timeout, enables future per-provider config

---

### 1.4 Validate Configuration at Load Time

**File**: `config.py`

**Add validation function**:

```python
def validate_config(config: dict) -> None:
    """Validate configuration values at load time."""
    if config.get("temperature") is not None:
        temp = config["temperature"]
        if not 0.0 <= temp <= 2.0:
            raise ConfigError(f"temperature must be between 0.0 and 2.0, got {temp}")

    if config.get("max_output_tokens") is not None:
        tokens = config["max_output_tokens"]
        if tokens < 1 or tokens > 100000:
            raise ConfigError(f"max_output_tokens must be between 1 and 100000, got {tokens}")
```

**Effort**: ~30 minutes
**Impact**: Fail fast with clear error messages

---

## Phase 2: Provider Consolidation (Medium Effort, High Impact)

### 2.1 Create Base HTTP Client

**New file**: `src/gac/providers/http_client.py`

```python
import httpx
import logging
from gac.errors import AIError
from gac.constants import ProviderDefaults

logger = logging.getLogger(__name__)

def make_api_request(
    url: str,
    headers: dict,
    data: dict,
    provider_name: str,
    timeout: int = ProviderDefaults.HTTP_TIMEOUT,
) -> dict:
    """Make HTTP request with standardized error handling."""
    logger.debug(f"Calling {provider_name} API: {url}")

    try:
        response = httpx.post(url, headers=headers, json=data, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            raise AIError.rate_limit_error(f"{provider_name} rate limit exceeded") from e
        if e.response.status_code == 401:
            raise AIError.authentication_error(f"{provider_name} authentication failed") from e
        raise AIError.model_error(f"{provider_name} API error: {e.response.status_code}") from e
    except httpx.TimeoutException as e:
        raise AIError.timeout_error(f"{provider_name} request timed out") from e
    except Exception as e:
        raise AIError.model_error(f"{provider_name} error: {e}") from e
```

**Effort**: ~2 hours
**Impact**: Eliminates ~800 lines of duplicated error handling

---

### 2.2 Simplify Provider Implementations

**After 2.1, each provider becomes**:

```python
# openai.py (reduced from 39 to ~20 lines)
from gac.providers.http_client import make_api_request

def generate(model: str, prompt: list[dict], max_tokens: int, temperature: float) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise AIError.authentication_error("OPENAI_API_KEY not set")

    response = make_api_request(
        url="https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        data={"model": model, "messages": prompt, "max_completion_tokens": max_tokens, "temperature": temperature},
        provider_name="OpenAI",
    )

    content = response["choices"][0]["message"]["content"]
    if not content:
        raise AIError.model_error("OpenAI returned empty response")
    return content
```

**Effort**: ~4 hours (28 providers)
**Impact**: ~50% reduction in provider code, consistent behavior

---

### 2.3 Create Response Extractors

**Add to `http_client.py`**:

```python
def extract_openai_content(response: dict) -> str:
    """Extract content from OpenAI-compatible response."""
    return response["choices"][0]["message"]["content"]

def extract_anthropic_content(response: dict) -> str:
    """Extract content from Anthropic response."""
    return response["content"][0]["text"]
```

**Effort**: ~1 hour
**Impact**: Type-safe response handling, single point of change

---

## Phase 3: Module Decomposition (High Effort, High Impact)

### 3.1 Split main.py into Focused Modules

**Current**: 1,059 lines, 2 massive workflow functions

**Target structure**:

```text
src/gac/
├── main.py              # Entry point, orchestration only (~200 lines)
├── workflows/
│   ├── __init__.py
│   ├── single.py        # Single commit workflow (~150 lines)
│   ├── grouped.py       # Grouped commits workflow (~200 lines)
│   └── validation.py    # Response validation, retry logic (~150 lines)
├── interaction/
│   ├── __init__.py
│   ├── confirmation.py  # User confirmation prompts
│   └── feedback.py      # Feedback collection and retry
```

**Effort**: ~8 hours
**Impact**: Testable units, clear responsibilities, reduced cognitive load

---

### 3.2 Split prompt.py by Concern

**Current**: 895 lines, 18+ functions

**Target structure**:

```text
src/gac/
├── prompts/
│   ├── __init__.py
│   ├── templates.py     # System/user prompt templates
│   ├── builder.py       # Prompt construction logic
│   ├── cleaning.py      # Message cleaning/extraction
│   └── readme.py        # README summarization (uses sumy)
```

**Effort**: ~4 hours
**Impact**: Clear API boundaries, easier testing

---

### 3.3 Fix OAuth Token Refresh Timing

**File**: `ai_utils.py`

**Current**: Token refresh happens during `generate_commit_message()`

**Change**: Add early validation in `main.py` before workflow starts:

```python
def validate_provider_auth(provider: str, quiet: bool) -> None:
    """Validate provider authentication before starting workflow."""
    if provider == "qwen":
        oauth_provider = QwenOAuthProvider(TokenStore())
        if not oauth_provider.get_token():
            if not quiet:
                console.print("[yellow]⚠ Qwen authentication required[/yellow]")
            oauth_provider.authenticate()  # Interactive auth here, not mid-workflow
```

**Effort**: ~2 hours
**Impact**: No surprise prompts during generation, cleaner UX

---

## Phase 4: Type Safety (Medium Effort, Medium Impact)

### 4.1 Add Response Type Definitions

**New file**: `src/gac/types.py`

```python
from typing import TypedDict

class OpenAIMessage(TypedDict):
    role: str
    content: str

class OpenAIChoice(TypedDict):
    message: OpenAIMessage

class OpenAIResponse(TypedDict):
    choices: list[OpenAIChoice]

class AnthropicContentBlock(TypedDict):
    type: str
    text: str

class AnthropicResponse(TypedDict):
    content: list[AnthropicContentBlock]
```

**Effort**: ~2 hours
**Impact**: IDE support, catch type errors at development time

---

### 4.2 Add Type Guards for Response Extraction

```python
def is_openai_response(data: dict) -> TypeGuard[OpenAIResponse]:
    return "choices" in data and len(data["choices"]) > 0
```

**Effort**: ~1 hour
**Impact**: Runtime validation with type narrowing

---

## Phase 5: Testing Improvements (Ongoing)

### 5.1 Add Tests for Extracted Modules

As modules are extracted in Phase 3, add focused unit tests:

- `test_validation.py` for response validation
- `test_confirmation.py` for user interaction
- `test_http_client.py` for provider HTTP wrapper

### 5.2 Add Integration Test Coverage

- End-to-end flow with real git repos
- Multi-file commit scenarios
- Token refresh during operations

---

## Summary

| Phase | Effort    | Items                  | Impact                        |
| ----- | --------- | ---------------------- | ----------------------------- |
| 1     | ~3 hours  | 5 quick fixes          | Immediate quality improvement |
| 2     | ~7 hours  | Provider consolidation | ~800 lines removed            |
| 3     | ~14 hours | Module decomposition   | Testability, maintainability  |
| 4     | ~3 hours  | Type safety            | Developer experience          |
| 5     | Ongoing   | Testing                | Confidence in changes         |

**Recommended order**: 1.1 → 1.3 → 1.4 → 2.1 → 2.2 → 1.2 → 3.1 → 3.3 → 3.2 → 4.x → 5.x

Start with assertions and constants (zero-risk), then provider consolidation (high ROI), then the larger refactors.
