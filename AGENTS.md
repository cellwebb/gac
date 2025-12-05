# Repository Guidelines

This provides essential guidance for AI coding agents working on this repository.

## 🚨 CRITICAL: AI AGENT COMMAND REQUIREMENTS

**ALWAYS use `uv run` prefix for ALL Python-related commands. NEVER use vanilla commands.**

### CORRECT (Always use these)

```bash
✅ uv run python script.py          # NEVER: python script.py
✅ uv run pytest                    # NEVER: pytest
✅ uv run python -m pytest tests/   # NEVER: python -m pytest tests/
✅ uv run python -c "print('test')" # NEVER: python -c "print('test')"
✅ uv run ruff check .              # NEVER: ruff check .
✅ uv run ruff format .             # NEVER: ruff format .
✅ uv run mypy src/                 # NEVER: mypy src/
✅ uv run pip install package      # NEVER: pip install package
```

### FORBIDDEN (Never use these)

❌ `python` (any form)
❌ `pytest` (any form)
❌ `pip` (any form)
❌ `ruff` (any form)
❌ `mypy` (any form)
❌ `black`, `isort`, `flake8`, or any other Python tools

**Why?** All development tools must go through `uv run` to ensure:

- Proper environment isolation
- Consistent dependency resolution
- No interference with global Python installations
- Reliable tool execution across different systems

**This requirement is NON-NEGOTIABLE for AI agents working with this project.**

## Project Structure

```text
gac/
├── src/gac/                    # Main package
│   ├── cli.py                  # CLI entrypoint
│   ├── main.py                 # Commit workflow orchestration
│   ├── ai.py                   # AI provider integration
│   ├── prompt.py               # Prompt building
│   ├── git.py                  # Git operations
│   ├── security.py             # Secret detection
│   ├── providers/              # 24 AI provider implementations
│   └── oauth/                  # OAuth authentication
├── tests/                      # Test suite (mirrors src/)
│   └── providers/              # Provider tests
├── docs/                       # Documentation
├── scripts/                    # Automation helpers
└── assets/                     # Screenshots and assets
```

**Key Points:**

- Package lives in `src/gac`
- Tests mirror source structure
- Each provider has dedicated implementation and test files
- Build artifacts (`dist/`, `htmlcov/`) are disposable

## Essential Commands

### Environment Setup

```bash
uv venv && uv pip install -e ".[dev]"
```

### Testing

```bash
uv run -- pytest                 # All tests (excludes integration)
uv run -- pytest tests/test_cli.py  # Single file
make test-integration             # Integration tests only (requires API keys)
```

### Code Quality

```bash
make lint                         # Check code quality
make format                       # Auto-fix formatting
make clean                        # Remove artifacts
```

## Development Guidelines

**Requirements:**

- Python 3.10+
- uv (REQUIRED - no exceptions)
- Git
- Node.js (for markdownlint)

**CLI Features:**

```bash
gac -i                            # Interactive mode
gac --add-all                     # Stage all changes
gac --group                       # Group changes into multiple commits
gac --dry-run                     # Preview without committing
gac --message-only                # Output message only
```

**Coding Standards:**

- Type annotations required
- Ruff formatter, 120-char lines
- snake_case for modules/functions, CapWords for classes
- Keep files under 600 lines (refactor when exceeded)

## Testing Structure

**Provider Tests:**
Each provider has three test types:

1. **Unit Tests** - No external dependencies
2. **Mocked Tests** - HTTP calls mocked, inherit from `BaseProviderTest`
3. **Integration Tests** - Real API calls (marked `@pytest.mark.integration`)

**Coverage:**

```bash
make test-cov                     # Generate HTML coverage report
open htmlcov/index.html           # View details
```

## Commit & PR Guidelines

**Format:** Conventional Commits with optional scopes

```bash
feat(ai): implement streaming
fix(providers): handle rate limits
docs: update examples
```

**PR Checklist:**

- [ ] Version bumped in `__version__.py` (if releasable)
- [ ] CHANGELOG.md updated
- [ ] Tests added/updated
- [ ] `make format`, `make lint`, `make type-check`, and `make test` passing
- [ ] No files exceed 600-line limit

**Use `gac` for commits:** `gac -sy`

## Critical Dependencies

- `tiktoken>=0.12.0` - OpenAI's tokenizer (for token counting)
- `httpx>=0.28.0` - HTTP client with async support and proper connection pooling
- `pydantic>=2.12.0` - Data validation and serialization for provider configs
- `click>=8.3.0` - CLI framework with rich formatting integration
- `rich>=14.1.0` - Terminal formatting for beautiful CLI output

**UV HARD REQUIREMENT:**

This project's multi-provider architecture (25+ AI integrations) creates complex dependency trees that only UV can resolve consistently. The dependency lockfile (`uv.lock`) ensures reproducible builds across all environments - development, testing, CI/CD, and production.

**NEVER use vanilla Python tools.** They will:

- Break dependency resolution with the provider ecosystem
- Create environment inconsistencies between contributors
- Fail to reproduce the exact dependency versions tested in CI
- Introduce subtle bugs from version mismatches

**ALWAYS use UV.** It provides:

- Exact dependency locking via `uv.lock`
- 10-100x faster installation and caching
- Consistent behavior across all environments
- Proper handling of the complex provider dependency matrix
