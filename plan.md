# GAC Provider Refactoring Plan

## Overview

This plan documents the migration of GAC's provider system from pure functions with duplicated patterns to kittylog's class-based architecture with shared base classes.

## Goals

1. **Reduce Code Duplication** - Eliminate repeated HTTP handling, error handling, and logging patterns across 25+ providers
2. **Improve Maintainability** - Centralize common logic in base classes
3. **Maintain Backward Compatibility** - Keep existing `call_xxx_api()` function signatures
4. **Add Type Safety** - Implement `ProviderProtocol` for consistent interfaces
5. **Align with Sister Project** - Share patterns with kittylog for easier cross-project contributions

## Architecture Overview

```text
ProviderProtocol (Protocol - type contract)
     ↓
BaseConfiguredProvider (ABC - core logic)
     ↓
├── OpenAICompatibleProvider (OpenAI-style APIs)
├── AnthropicCompatibleProvider (Anthropic-style APIs)
├── NoAuthProvider (Local models like Ollama)
└── GenericHTTPProvider (Fully custom)
     ↓
Concrete Providers (e.g., OpenAIProvider, GeminiProvider)
```

## Key Components to Create

### 1. `src/gac/providers/protocol.py`

- `ProviderProtocol` - Runtime-checkable protocol defining provider interface
- `ProviderFunction` - Type alias for provider function signature
- `validate_provider()` - Validation helper function

### 2. `src/gac/providers/base.py`

- `ProviderConfig` - Dataclass holding provider configuration
- `BaseConfiguredProvider` - Abstract base class with template method pattern
- `OpenAICompatibleProvider` - Base for OpenAI-style APIs
- `AnthropicCompatibleProvider` - Base for Anthropic-style APIs
- `NoAuthProvider` - Base for providers without API keys (Ollama, LM Studio)
- `GenericHTTPProvider` - Base for fully custom providers

### 3. `src/gac/providers/error_handler.py`

- `handle_provider_errors()` - Decorator for centralized error handling

## GAC-Specific Adaptations

1. **SSL Verification Support**

   - Integrate `get_ssl_verify()` from `gac.utils`
   - Add `verify` parameter to HTTP requests

2. **Logging Integration**

   - Use GAC's existing logging patterns
   - Add debug logging for API calls

3. **Error Type Alignment**
   - Use `AIError` class methods: `.authentication_error()`, `.rate_limit_error()`, `.timeout_error()`, `.model_error()`, `.connection_error()`

## Migration Phases

### Phase 1: Foundation [Priority: HIGH]

**Goal**: Create base infrastructure by copying kittylog's implementation with GAC-specific adaptations.

**Source files (kittylog):**

- `../kittylog/src/kittylog/providers/protocol.py`
- `../kittylog/src/kittylog/providers/base_configured.py`
- `../kittylog/src/kittylog/providers/error_handler.py`
- `../kittylog/src/kittylog/providers/registry.py`

**1.1 Create `src/gac/providers/protocol.py`**

- [x] Copy from kittylog's `protocol.py`
- [x] Change imports: `kittylog.errors` → `gac.errors`
- [x] No other changes needed

**1.2 Create `src/gac/providers/base.py`**

- [x] Copy from kittylog's `base_configured.py`
- [x] Change imports: `kittylog.errors` → `gac.errors`
- [x] Change imports: `kittylog.providers.protocol` → `gac.providers.protocol`
- [x] Change imports: `kittylog.providers.registry` → `gac.providers.registry`
- [x] Add import: `from gac.utils import get_ssl_verify`
- [x] Add import: `from gac.constants import ProviderDefaults`
- [x] Modify `ProviderConfig`: change `timeout: int = 120` → `timeout: int = ProviderDefaults.HTTP_TIMEOUT`
- [x] Modify `_make_http_request()`: add `verify=get_ssl_verify()` to httpx.post call
- [x] Add logging: `import logging` and `logger = logging.getLogger(__name__)`
- [x] Add debug logging in `generate()` method

**1.3 Create `src/gac/providers/error_handler.py`**

- [x] Copy from kittylog's `error_handler.py`
- [x] Change imports: `kittylog.errors` → `gac.errors`
- [x] No other changes needed

**1.4 Create `src/gac/providers/registry.py`**

- [x] Copy from kittylog's `registry.py`
- [x] No changes needed (pure Python, no project-specific imports)

### 1.5 Add unit tests

- [x] Create `tests/providers/test_base.py`
- [x] Create `tests/providers/test_protocol.py`
- [x] Create `tests/providers/test_error_handler.py`
- [x] Test SSL verification is passed correctly
- [x] Test timeout uses `ProviderDefaults.HTTP_TIMEOUT`

**Current Test Status**: 434/458 tests passing (94.8%), 24 integration tests skipped

- Phase 1 Foundation: ✅ All tests passing
- Phase 2 OpenAI-compatible: ✅ 100 tests passing
- Phase 3 Anthropic-compatible: ✅ 38 tests passing
- Phase 4 Custom (GROUP A-C): ✅ 96 tests passing
- Phases 5-6: ✅ 160+ tests passing

**Files to create:**

- `src/gac/providers/protocol.py`
- `src/gac/providers/base.py`
- `src/gac/providers/error_handler.py`
- `src/gac/providers/registry.py`
- `tests/providers/test_base.py`
- `tests/providers/test_protocol.py`
- `tests/providers/test_error_handler.py`

### Phase 2: Simple OpenAI-Compatible Providers [Priority: HIGH]

**Goal**: Migrate providers that follow standard OpenAI format

**Template for each provider migration:**

```python
# 1. Create provider class inheriting from OpenAICompatibleProvider
class XxxProvider(OpenAICompatibleProvider):
    config = ProviderConfig(
        name="Xxx",
        api_key_env="XXX_API_KEY",
        base_url="https://api.xxx.com/v1/chat/completions",
    )
    # Override methods only if needed

# 2. Create instance
xxx_provider = XxxProvider(XxxProvider.config)

# 3. Create decorated API function (preserves existing signature)
@handle_provider_errors("Xxx")
def call_xxx_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    return xxx_provider.generate(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
```

**Providers to migrate:**

- [x] `openai.py` - Reference implementation (uses `max_completion_tokens`)
- [x] `deepseek.py` - Simple, no customization needed
- [x] `together.py` - Simple, no customization needed
- [x] `fireworks.py` - Simple, no customization needed
- [x] `cerebras.py` - Simple, no customization needed
- [x] `mistral.py` - Simple, no customization needed
- [x] `minimax.py` - Simple, no customization needed
- [x] `moonshot.py` - Simple, no customization needed
- [x] `groq.py` - Simple, fix empty content bug during migration
- [x] `openrouter.py` - Needs custom `HTTP-Referer` header

### Phase 3: Anthropic-Compatible Providers [Priority: HIGH]

**Goal**: Migrate Anthropic-style providers

Providers to migrate:

- [x] `anthropic.py` - Reference implementation
- [x] `custom_anthropic.py`

### Phase 4: Custom Providers [Priority: MEDIUM]

**Goal**: Migrate providers with unique API formats

**STATUS**: 6 of 9 providers completed (67%)

Providers to migrate:

- [x] `chutes.py` - Custom base URL (GROUP A - simple)
- [x] `kimi_coding.py` - OpenAI-compatible with max_completion_tokens (GROUP A - simple)
- [x] `streamlake.py` - Alternative env vars (GROUP B)
- [x] `synthetic.py` - Alternative env vars + model preprocessing (GROUP B)
- [x] `custom_openai.py` - Custom endpoint support (GROUP C)
- [x] `azure_openai.py` - Azure-specific configuration (GROUP C)
- [ ] `gemini.py` - Google's unique format (GROUP D - complex)
- [ ] `replicate.py` - Prediction-based async API (GROUP D - complex)
- [ ] `zai.py` - Multiple endpoints (GROUP E)

### Phase 5: No-Auth Providers [Priority: MEDIUM]

**Goal**: Migrate providers that don't require API keys

Providers to migrate:

- [ ] `ollama.py`
- [ ] `lmstudio.py`

### Phase 6: OAuth Providers [Priority: LOW]

**Goal**: Migrate OAuth-based providers (most complex)

Providers to migrate:

- [ ] `claude_code.py` - OAuth token refresh
- [ ] `qwen.py` - OAuth token refresh

### Phase 7: Cleanup & Documentation [Priority: LOW]

**Goal**: Finalize migration

- [ ] Update `__init__.py` to export new classes
- [ ] Add provider README documenting patterns
- [ ] Remove any dead code
- [ ] Ensure 100% test coverage
- [ ] Update CONTRIBUTING.md with provider guidelines

## Provider Classification

### OpenAI-Compatible (standard format)

| Provider   | Env Var            | Special Handling      |
| ---------- | ------------------ | --------------------- |
| openai     | OPENAI_API_KEY     | max_completion_tokens |
| deepseek   | DEEPSEEK_API_KEY   | None                  |
| together   | TOGETHER_API_KEY   | None                  |
| fireworks  | FIREWORKS_API_KEY  | None                  |
| cerebras   | CEREBRAS_API_KEY   | None                  |
| mistral    | MISTRAL_API_KEY    | None                  |
| minimax    | MINIMAX_API_KEY    | None                  |
| moonshot   | MOONSHOT_API_KEY   | None                  |
| groq       | GROQ_API_KEY       | Alternative models    |
| openrouter | OPENROUTER_API_KEY | HTTP-Referer header   |

### Anthropic-Compatible

| Provider         | Env Var             | Special Handling   |
| ---------------- | ------------------- | ------------------ |
| anthropic        | ANTHROPIC_API_KEY   | Message conversion |
| custom_anthropic | CUSTOM*ANTHROPIC*\* | Custom base URL    |

### Custom Format

| Provider     | Env Var           | Special Handling            |
| ------------ | ----------------- | --------------------------- |
| gemini       | GEMINI_API_KEY    | Google format, model-in-URL |
| replicate    | REPLICATE_API_KEY | Prediction polling          |
| azure_openai | AZURE*OPENAI*\*   | Azure endpoints             |
| chutes       | CHUTES_API_KEY    | Custom base URL             |

### No Auth Required

| Provider | Config           | Special Handling |
| -------- | ---------------- | ---------------- |
| ollama   | OLLAMA_HOST      | Local server     |
| lmstudio | LMSTUDIO_API_URL | Local server     |

### OAuth-Based

| Provider    | Token Source | Special Handling |
| ----------- | ------------ | ---------------- |
| claude_code | OAuth flow   | Token refresh    |
| qwen        | OAuth flow   | Token refresh    |

## Testing Strategy

1. **Unit Tests for Base Classes**

   - Test `ProviderConfig` dataclass
   - Test `BaseConfiguredProvider` template methods
   - Test each specialized base class
   - Test error handler decorator

2. **Integration Tests per Provider**

   - Mock HTTP responses
   - Verify request format
   - Verify response parsing
   - Verify error handling

3. **Backward Compatibility Tests**
   - Ensure `call_xxx_api()` functions still work
   - Verify function signatures unchanged

## Risks & Mitigations

| Risk                        | Mitigation                                        |
| --------------------------- | ------------------------------------------------- |
| Breaking existing tests     | Run full test suite after each provider migration |
| SSL verification regression | Add explicit tests for `verify` parameter         |
| Logging changes             | Compare log output before/after migration         |
| OAuth flow disruption       | Migrate OAuth providers last, test extensively    |

## Success Criteria

1. All existing tests pass
2. No changes to public API (`call_xxx_api()` functions)
3. Reduced lines of code per provider (~50% reduction)
4. Centralized error handling in `error_handler.py`
5. Type checking passes with `mypy`
6. New provider documentation in `providers/README.md`

## Estimated Timeline

- Phase 1 (Foundation): 2-3 hours
- Phase 2 (OpenAI-Compatible): 2 hours
- Phase 3 (Anthropic-Compatible): 1 hour
- Phase 4 (Custom Providers): 3 hours
- Phase 5 (No-Auth Providers): 1 hour
- Phase 6 (OAuth Providers): 2 hours
- Phase 7 (Cleanup): 1 hour

### Total: ~12-14 hours

## References

- Kittylog's implementation: `../kittylog/src/kittylog/providers/`
- GAC's current providers: `./src/gac/providers/`

## Key Differences from Kittylog

| Aspect           | Kittylog                     | GAC                                            |
| ---------------- | ---------------------------- | ---------------------------------------------- |
| SSL Verification | Not implemented              | `verify=get_ssl_verify()` in all requests      |
| Timeout          | Hardcoded `120`              | `ProviderDefaults.HTTP_TIMEOUT` from constants |
| Error Types      | `AIError.generation_error()` | Same, plus `.model_error()` distinction        |
| Logging          | Minimal                      | Debug logging for API calls                    |

## Sync Strategy

When updating one project, apply the same changes to the other:

1. **Base class changes** → Update both `kittylog/providers/base_configured.py` and `gac/providers/base.py`
2. **New provider** → Create in both projects with same structure
3. **Bug fixes** → Apply to both if applicable
4. **GAC-only features** → Keep SSL verification and timeout constants isolated to GAC's `_make_http_request()`
