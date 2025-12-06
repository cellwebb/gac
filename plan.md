# GAC Refactoring Plan

Issues ordered by effort (lowest hanging fruit first).

---

## Tier 1: Quick Wins (< 30 min each)

### 1.1 Fix model parsing edge case ✅

**File:** `src/gac/main.py:77-99`
**Issue:** `"openai:"` (trailing colon) produces empty `model_name`

- [x] Locate model parsing logic in `main.py` - already exists at lines 90-97
- [x] Add validation: `if not model_name: raise ConfigError(...)` - already implemented
- [x] Add test case for trailing colon input - added `test_trailing_colon_model_exits_with_message`
- [x] Add test case for leading colon input - added `test_leading_colon_model_exits_with_message`
- [x] Run `uv run -- pytest` to verify existing tests pass

### 1.2 Add type annotation to provider_funcs ✅

**File:** `src/gac/ai_utils.py:102`
**Current:** `provider_funcs: dict`

- [x] Add import for `Callable` from `collections.abc`
- [x] Change annotation to `dict[str, Callable[..., str]]`
- [x] Run tests to verify

### 1.3 Document error classification rules ✅

**File:** `src/gac/ai_utils.py:78-98`

- [x] Add docstring to `_classify_error()` function
- [x] Document each keyword category and why it maps to its error type
- [x] Explain priority/matching order
- [x] Note known limitations of string matching approach

---

## Tier 2: Small Refactors (1-2 hours each)

### 2.1 Replace broad exception handling with specific exceptions ✅✅

**Files:**

- `src/gac/git.py` (all locations)
- `src/gac/main.py` (all locations)
- `src/gac/ai_utils.py` (all locations)

- [x] **COMPLETE AUDIT**: Found and fixed ALL `except Exception` in target files
- [x] **git.py**: Replaced with `subprocess.SubprocessError`, `OSError`, `FileNotFoundError`, `PermissionError`, `ConnectionError`
- [x] **main.py**: Replaced with `AIError`, `ConfigError`, `GitError`, `subprocess.SubprocessError`, `OSError`, `ConnectionError`
- [x] **ai_utils.py**:
  - Token counting: `KeyError`, `UnicodeError`, `ValueError`
  - Encoding detection: `KeyError`, `OSError`, `ConnectionError`
  - Qwen auth: `ValueError`, `KeyError`, `json.JSONDecodeError`, `ConnectionError`, `OSError`
  - Retry loop: Kept `Exception` as comprehensive catch-all (appropriate for retry logic)
- [x] **Updated ALL breaking tests** to use realistic exception types
- [x] **Final verification**: Confirmed zero `except Exception` in git.py and main.py
- [x] All tests pass (1087 passed)
- [x] Full mypy compliance (55 source files, no issues)

**Notes:**

- **Systematic approach**: Found ALL remaining `except Exception` handlers in target files
- **Realistic exception types**: Tests now use exceptions that would actually occur in practice
- **Comprehensive coverage**: No broad exception handling left in git.py or main.py
- **Only remaining**: One intentional `except Exception` in ai_utils.py retry loop (appropriate)
- Tested with mock exceptions used in unit tests

### 2.2 Add TypedDict for configuration ✅

**File:** `src/gac/config.py`

- [x] Define `GACConfig` TypedDict with all config fields
- [x] Add proper types for each field (str | None, float, int, bool, etc.)
- [x] Update `load_config()` return type
- [x] Update all call sites to use typed config
- [x] Run `uv run -- mypy` to verify (55 source files, no issues)

**Notes:**

- Created TypedDict with 16 configuration fields including optional fields
- Used `total=False` to allow omitting optional
- Updated function signatures:
  - `validate_config(config: GACConfig) -> None`
  - `load_config() -> GACConfig`
- Updated call sites in `main.py` and `cli.py` with proper type annotations
- All files pass mypy type checking

### 2.3 Sanitize API responses in error messages ✅

**File:** `src/gac/providers/base.py:173`

- [x] Create `sanitize_error_response(text: str) -> str` function
- [x] Truncate to max 200 characters
- [x] Add regex patterns to redact potential API keys/tokens
- [x] Update error message construction to use sanitizer
- [x] Add tests for sanitization logic

**Notes:**

- Added `sanitize_error_response()` function with 9 sensitive patterns (OpenAI, Anthropic, GitHub, Google, Stripe, Slack, JWT, Bearer, generic alphanumeric)
- Truncates to 200 characters after redaction
- Updated `_make_http_request()` to sanitize HTTP error responses
- Added 17 comprehensive tests covering all patterns and edge cases
- All 1104 tests pass

---

## Tier 3: Medium Refactors (half day each)

### 3.1 Consolidate error handling layers ✅

**Files:**

- `src/gac/providers/error_handler.py`
- `src/gac/providers/base.py`
- `src/gac/ai_utils.py`

- [x] Map current error flow through all three locations
- [x] Decide on single authoritative location (recommend: decorator)
- [x] Remove duplicate catching in `_make_http_request()`
- [x] Simplify retry loop to only handle `AIError` types
- [x] Update all providers to use consolidated approach
- [x] Add tests verifying error propagation
- [x] Document the error handling strategy

**Notes:**

- **Single authoritative location**: `@handle_provider_errors` decorator in `error_handler.py`
- **Removed duplicate catching**: `_make_http_request()` now lets exceptions propagate to decorator
- **Simplified generate()**: Removed try/except blocks that duplicated decorator logic
- **Retry loop cleanup**: Removed `except Exception` fallback, now only catches `AIError`
- **Error classification**: Decorator handles HTTP status codes (401→auth, 429→rate_limit, 404→model, 5xx→connection)
- **Sanitization**: Added `sanitize_error_response()` call in decorator for HTTP errors
- **Tests updated**: All tests now use AIError instead of generic exceptions (13 new/updated tests)
- **All 1105 tests pass**

### 3.2 Simplify provider registration pattern

**Files:** All providers in `src/gac/providers/`

- [ ] Decide: Option A (registry stores classes) or Option B (remove helpers)
- [ ] If Option A:
  - [ ] Update `PROVIDER_REGISTRY` to store provider classes
  - [ ] Update `get_provider()` to instantiate and call `.generate()`
  - [ ] Remove wrapper functions from all providers
- [ ] If Option B:
  - [ ] Inline `_get_*_provider()` calls into wrapper functions
  - [ ] Remove all `_get_*_provider()` helper functions
- [ ] Update tests accordingly
- [ ] Verify all providers still work

### 3.3 Add missing integration tests

**File:** `tests/providers/test_integration.py` (new)

- [ ] Create new test file with `@pytest.mark.integration` decorator
- [ ] Add test for retry logic with simulated rate limits
- [ ] Add test for OAuth token refresh flow
- [ ] Add test for connection timeout recovery
- [ ] Add test for actual API call success path
- [ ] Document how to run integration tests
- [ ] Add to CI as optional job

---

## Tier 4: Major Refactors (1+ days each)

### 4.1 Break down main() function

**File:** `src/gac/main.py`

- [ ] Analyze `main()` and identify logical sections
- [ ] Extract `GitStateValidator` class/function
  - [ ] Validate repo state
  - [ ] Check staged changes
  - [ ] Return structured git state
- [ ] Extract `PromptBuilder` class/function
  - [ ] Build system prompt
  - [ ] Build user prompt from git state
  - [ ] Handle verbose/one-liner modes
- [ ] Extract `CommitExecutor` class/function
  - [ ] Handle commit creation
  - [ ] Handle amend logic
  - [ ] Handle dry-run mode
- [ ] Extract `GroupedCommitWorkflow` class/function
  - [ ] Handle multi-file grouping logic
  - [ ] Handle per-group AI calls
- [ ] Extract `InteractiveMode` class/function
  - [ ] Handle user prompts
  - [ ] Handle edit/regenerate flows
- [ ] Refactor `main()` to be thin orchestrator
- [ ] Add unit tests for each extracted component
- [ ] Verify integration tests still pass

### 4.2 Replace string-based error classification

**File:** `src/gac/ai_utils.py:78-98`

- [ ] Create exception hierarchy in `errors.py`:
  - [ ] `AIAuthError(AIError)` - API key issues
  - [ ] `AIRateLimitError(AIError)` - rate limits
  - [ ] `AIConnectionError(AIError)` - network issues
  - [ ] `AIModelError(AIError)` - model not found/invalid
  - [ ] `AIContentError(AIError)` - content policy violations
- [ ] Update `error_handler.py` decorator to raise specific types
- [ ] Update each provider to raise appropriate exception types
- [ ] Remove `_classify_error()` function
- [ ] Update retry logic to use `isinstance()` checks
- [ ] Update all error handling call sites
- [ ] Add comprehensive tests for each error type
- [ ] Document exception hierarchy

### 4.3 Complete type annotation coverage

**Files:** All files in `src/gac/`

- [ ] Run `uv run -- mypy --strict` and collect all errors
- [ ] Fix annotations in `ai_utils.py`
- [ ] Fix annotations in `main.py`
- [ ] Fix annotations in `config.py`
- [ ] Fix annotations in `prompt.py`
- [ ] Fix annotations in `git.py`
- [ ] Fix annotations in `preprocess.py`
- [ ] Fix annotations in all provider files
- [ ] Remove all `# type: ignore` comments
- [ ] Add `py.typed` marker file
- [ ] Enable strict mypy in CI (`uv run -- mypy --strict`)
- [ ] Add type checking to pre-commit hooks
