# GAC Refactoring Plan

Ordered by suggested completion sequence. Note: GAC is a CLI tool that runs once
and exits, so runtime performance optimizations are largely irrelevant.

---

## 1. Standardize Configuration Access Pattern ✅ COMPLETED

**Priority:** High | **Effort:** Low | **Impact:** Code consistency

**Problem:**
Mixed patterns for accessing `GACConfig` TypedDict - some used `config["key"]`, others used
`config.get("key", default)`. Since `load_config()` always returns a fully-populated dict,
the `.get()` calls were redundant and misleading.

**Solution Applied:**
Standardized on `config["key"]` access everywhere since config is always fully populated.
Also fixed a bug where `interactive_mode.py` accessed `require_confirmation` which doesn't
exist in `GACConfig` (dead code).

**Files modified:**

- `src/gac/cli.py` - 6 locations changed from `.get()` to direct access
- `src/gac/main.py` - Simplified warning_limit access, removed unused `EnvDefaults` import
- `src/gac/grouped_commit_workflow.py` - Simplified warning_limit access, removed unused import
- `src/gac/interactive_mode.py` - Removed dead code checking non-existent config key

---

## 2. Refactor `main()` to Use Context Dataclass

**Priority:** High | **Effort:** Medium | **Impact:** Maintainability

**Problem:**
`main.py:main()` accepts 17 parameters:

```python
def main(
    stage_all, group, interactive, model, hint, one_liner,
    show_prompt, infer_scope, require_confirmation, push,
    quiet, dry_run, message_only, verbose, no_verify,
    skip_secret_scan, language, hook_timeout
) -> int:
```

**Solution:**
Create `CLIContext` dataclass similar to existing `WorkflowContext`:

```python
@dataclass(frozen=True)
class CLIContext:
    stage_all: bool = False
    group: bool = False
    interactive: bool = False
    model: str | None = None
    hint: str = ""
    # ... etc
```

**Files to modify:**

- `src/gac/workflow_context.py` - Add `CLIContext`
- `src/gac/main.py` - Refactor `main()` signature
- `src/gac/cli.py` - Update call site to construct context

---

## 3. Add Model Validation Per Provider

**Priority:** Medium | **Effort:** Medium | **Impact:** User experience

**Problem:**
No validation that model names are valid for the selected provider. Users get cryptic API errors.

**Solution:**

- Add `KNOWN_MODELS` constant to each provider (or base class)
- Validate model in `_validate_config()` or at call time
- Warn (not error) for unknown models to allow new models

**Files to modify:**

- `src/gac/providers/base.py` - Add validation hook
- `src/gac/constants/` - Add `models.py` with known model lists
- Each provider file - Add provider-specific model lists

---

## 4. Validate OAuth Token File Permissions

**Priority:** Medium | **Effort:** Low | **Impact:** Security

**Problem:**
OAuth tokens stored in local JSON files without verifying permissions are `0600`.

**Solution:**

- Check file permissions on token load
- Set permissions on token write
- Warn user if permissions are too open

**Files to modify:**

- `src/gac/oauth/token_store.py`

---

## 5. Clean Up Lazy Imports in ai_utils.py

**Priority:** Low | **Effort:** Low | **Impact:** Code cleanliness

**Problem:**
Circular dependency avoidance via lazy imports:

```python
if provider == "claude-code":
    from gac.oauth import refresh_token_if_expired
```

**Solution:**

- Extract OAuth retry logic to separate module
- Use `TYPE_CHECKING` guards where appropriate
- Consider dependency injection pattern

**Files to modify:**

- `src/gac/ai_utils.py`
- `src/gac/oauth_retry.py` (may already handle this)

---

## 6. Break Up grouped_commit_workflow.py (Optional)

**Priority:** Low | **Effort:** Medium | **Impact:** Maintainability

**Problem:**
At 448 LOC, this is the largest non-provider module with multiple responsibilities.

**Solution:**
Consider splitting into:

- `grouped_commit_generator.py` - AI interaction for grouped commits
- `grouped_commit_validator.py` - JSON validation and feedback loop
- `grouped_commit_executor.py` - Commit execution logic

**Files to modify:**

- `src/gac/grouped_commit_workflow.py` - Split into multiple modules

---

## Removed Items

The following were removed as irrelevant for a single-run CLI tool:

- ~~HTTP connection pooling~~ - Only 1-3 API calls per invocation; new client overhead is negligible
- ~~Regex optimization in postprocess.py~~ - Running 7 regexes once on a short string is microseconds

---

## Completion Checklist

- [x] 1. Standardize configuration access pattern
- [ ] 2. Refactor `main()` to use context dataclass
- [ ] 3. Add model validation per provider
- [ ] 4. Validate OAuth token file permissions
- [ ] 5. Clean up lazy imports in ai_utils.py
- [ ] 6. Break up grouped_commit_workflow.py (optional)
