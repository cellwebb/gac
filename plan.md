# GAC Refactoring Plan

Ordered by effort (low → high) and impact.

---

## Phase 1: Quick Wins (Low Effort, High Value)

### 1.1 Extract Duplicate OAuth Retry Logic

**File:** `main.py:170-283`

The Claude Code and Qwen OAuth retry blocks are nearly identical. Extract to a generic function:

```python
def _retry_with_oauth(
    provider_prefix: str,
    auth_module: str,
    auth_function: str,
    manual_auth_hint: str,
    prompts: PromptResult,
    workflow_params: dict,
) -> None:
    """Generic OAuth retry handler."""
    ...
```

**Effort:** ~30 min
**Impact:** Removes ~50 lines of duplication, easier to add new OAuth providers

---

### 1.2 Create `ModelIdentifier` Dataclass

**File:** `main.py:31-53`

Replace string parsing with a proper value object:

```python
@dataclass(frozen=True)
class ModelIdentifier:
    provider: str
    model_name: str

    @classmethod
    def parse(cls, model_string: str) -> "ModelIdentifier":
        if ":" not in model_string:
            raise ConfigError(f"Invalid model format: '{model_string}'...")
        provider, model_name = model_string.split(":", 1)
        if not provider or not model_name:
            raise ConfigError(...)
        return cls(provider=provider, model_name=model_name)

    def __str__(self) -> str:
        return f"{self.provider}:{self.model_name}"
```

**Effort:** ~20 min
**Impact:** Type safety, reusable parsing, cleaner code

---

### 1.3 Move Lazy Imports to Module Top

**Files:** `main.py:107`, `main.py:133`, `main.py:203`

Move these to the top of the file:

```python
from gac.workflow_utils import check_token_warning, display_commit_message
from gac.oauth.claude_code import authenticate_and_save
from gac.oauth import QwenOAuthProvider, TokenStore
```

If there are circular import issues, document why the lazy import is necessary.

**Effort:** ~10 min
**Impact:** Clearer dependencies, slightly faster execution

---

### 1.4 Split `constants.py` into Logical Modules

**File:** `constants.py` (328 lines)

Create a `constants/` package:

```text
src/gac/constants/
├── __init__.py          # Re-exports for backward compatibility
├── defaults.py          # EnvDefaults, ProviderDefaults, Logging, Utility
├── file_patterns.py     # FilePatterns, FileTypeImportance, CodePatternImportance
├── languages.py         # Languages class
└── commit.py            # CommitMessageConstants, FileStatus
```

The `__init__.py` re-exports everything for backward compatibility:

```python
from gac.constants.defaults import EnvDefaults, ProviderDefaults, ...
from gac.constants.file_patterns import FilePatterns, ...
# etc.
```

**Effort:** ~45 min
**Impact:** Better organization, easier to find/edit specific constants

---

## Phase 2: Moderate Effort

### 2.1 Create `WorkflowContext` Dataclass

**Files:** `main.py`, `grouped_commit_workflow.py`

Bundle the 17+ parameters into a context object:

```python
@dataclass
class WorkflowContext:
    model: ModelIdentifier
    temperature: float
    max_output_tokens: int
    max_retries: int
    require_confirmation: bool
    quiet: bool
    no_verify: bool
    dry_run: bool
    message_only: bool
    push: bool
    show_prompt: bool
    hook_timeout: int
    interactive: bool
    hint: str

@dataclass
class WorkflowState:
    system_prompt: str
    user_prompt: str
    git_state: GitState
    commit_executor: CommitExecutor
    interactive_mode: InteractiveMode
```

Then:

```python
def _execute_single_commit_workflow(
    ctx: WorkflowContext,
    state: WorkflowState,
) -> None:
```

**Effort:** ~2 hours
**Impact:** Dramatically cleaner function signatures, easier testing

---

### 2.2 Move `sys.exit()` to CLI Layer

**Files:** `main.py`, `cli.py`

Replace `sys.exit()` calls in `main.py` with exceptions or return values:

```python
# Before (main.py)
if not check_token_warning(...):
    sys.exit(0)

# After (main.py)
class UserAbortError(GACError):
    """User chose to abort the operation."""
    pass

if not check_token_warning(...):
    raise UserAbortError("Token limit exceeded")

# CLI layer catches and exits
try:
    main(...)
except UserAbortError:
    sys.exit(0)
```

**Effort:** ~1.5 hours
**Impact:** Testable business logic, reusable as a library

---

### 2.3 Externalize Prompt Templates

**File:** `prompt.py`

Move templates to external files:

```text
src/gac/templates/
├── system_prompt.txt
├── user_prompt.txt
└── question_generation.txt
```

Load with:

```python
from importlib.resources import files

def load_system_template(custom_path: str | None = None) -> str:
    if custom_path:
        return Path(custom_path).read_text()
    return files("gac.templates").joinpath("system_prompt.txt").read_text()
```

**Effort:** ~1 hour
**Impact:** Templates editable with proper syntax highlighting, `prompt.py` shrinks to ~300 lines

---

## Phase 3: Larger Refactors

### 3.1 Simplify Template Selection with Jinja2

**File:** `prompt.py`

Replace the manual `_select_*_section` functions with Jinja2:

```jinja
{% if infer_scope %}
<conventions>
You MUST write a conventional commit message with EXACTLY ONE type and an inferred scope.
...
</conventions>
{% else %}
<conventions>
You MUST start your commit message with the most appropriate conventional commit prefix.
...
</conventions>
{% endif %}
```

**Effort:** ~3 hours
**Impact:** More maintainable templates, standard tooling, easier to add new variants
**Trade-off:** Adds Jinja2 dependency

---

### 3.2 Lazy Config Loading

**Files:** `main.py:27`, `cli.py`

Replace module-level config with lazy loading:

```python
from functools import lru_cache

@lru_cache(maxsize=1)
def get_config() -> GACConfig:
    return load_config()

# Or use a context variable for testing
_config_override: ContextVar[GACConfig | None] = ContextVar("config", default=None)

def get_config() -> GACConfig:
    override = _config_override.get()
    if override is not None:
        return override
    return load_config()
```

**Effort:** ~1 hour
**Impact:** Easier testing, no side effects at import time

---

### 3.3 Define Provider Protocol

**File:** `providers/base.py` or new `providers/protocol.py`

Add explicit interface:

```python
from typing import Protocol

class CommitMessageProvider(Protocol):
    """Protocol for AI providers that generate commit messages."""

    def generate(
        self,
        prompt: str | list[dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Generate a commit message from the given prompt."""
        ...

    @property
    def requires_api_key(self) -> bool:
        """Whether this provider requires an API key."""
        ...
```

**Effort:** ~1 hour
**Impact:** Clear contract, better IDE support, easier to verify new providers

---

## Phase 4: Optional / Future

### 4.1 Simplify Think Tag Removal

**File:** `prompt.py:730-759`

The 7-regex approach is fragile. Options:

1. Ask AI to use a simpler delimiter (e.g., `---`)
2. Use a proper XML parser for structured responses
3. Consolidate to fewer, well-tested regexes

**Effort:** Variable
**Impact:** More robust message cleaning

---

### 4.2 Reconsider Workflow Class Granularity

**Files:** `commit_executor.py`, `interactive_mode.py`, `git_state_validator.py`

Evaluate whether these need to be classes or could be modules with functions. Classes that:

- Have no state between calls
- Are instantiated fresh each time
- Have single methods

...might be better as plain functions.

**Effort:** ~2 hours
**Impact:** Simpler code, less indirection

---

## Checklist

| Task                            | Effort | Status |
| ------------------------------- | ------ | ------ |
| 1.1 Extract OAuth retry logic   | 30 min | [x]    |
| 1.2 Create ModelIdentifier      | 20 min | [x]    |
| 1.3 Move lazy imports           | 10 min | [x]    |
| 1.4 Split constants.py          | 45 min | [x]    |
| 2.1 Create WorkflowContext      | 2 hr   | [x]    |
| 2.1b Fix test git mocking leaks | 15 min | [x]    |
| 2.2 Move sys.exit() to CLI      | 1.5 hr | [x]    |
| 2.3 Externalize templates       | 1 hr   | [ ]    |
| 3.1 Jinja2 templates            | 3 hr   | [ ]    |
| 3.2 Lazy config loading         | 1 hr   | [ ]    |
| 3.3 Provider Protocol           | 1 hr   | [ ]    |
| 4.1 Simplify think tag removal  | TBD    | [ ]    |
| 4.2 Reconsider workflow classes | 2 hr   | [ ]    |
