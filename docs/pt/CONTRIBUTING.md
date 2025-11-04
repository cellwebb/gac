# Contributing to gac

[English](../en/CONTRIBUTING.md) | [简体中文](../zh-CN/CONTRIBUTING.md) | [繁體中文](../zh-TW/CONTRIBUTING.md) | [日本語](../ja/CONTRIBUTING.md) | [한국어](../ko/CONTRIBUTING.md) | [हिन्दी](../hi/CONTRIBUTING.md) | [Français](../fr/CONTRIBUTING.md) | [Русский](../ru/CONTRIBUTING.md) | [Español](../es/CONTRIBUTING.md) | **Português** | [Deutsch](../de/CONTRIBUTING.md) | [Nederlands](../nl/CONTRIBUTING.md)

Thank you for your interest in contributing to this project! Your help is appreciated. Please follow these guidelines to
make the process smooth for everyone.

## Table of Contents

- [Contributing to gac](#contributing-to-gac)
  - [Table of Contents](#table-of-contents)
  - [Development Environment Setup](#development-environment-setup)
    - [Quick Setup](#quick-setup)
    - [Alternative Setup (if you prefer step-by-step)](#alternative-setup-if-you-prefer-step-by-step)
    - [Available Commands](#available-commands)
  - [Version Bumping](#version-bumping)
    - [How to bump the version](#how-to-bump-the-version)
    - [Release Process](#release-process)
    - [Using bump-my-version (optional)](#using-bump-my-version-optional)
  - [Adding a New AI Provider](#adding-a-new-ai-provider)
    - [Checklist for Adding a New Provider](#checklist-for-adding-a-new-provider)
    - [Example Implementation](#example-implementation)
    - [Key Points](#key-points)
  - [Coding Standards](#coding-standards)
  - [Git Hooks (Lefthook)](#git-hooks-lefthook)
    - [Setup](#setup)
    - [Skipping Git Hooks](#skipping-git-hooks)
  - [Testing Guidelines](#testing-guidelines)
    - [Running Tests](#running-tests)
      - [Provider Integration Tests](#provider-integration-tests)
  - [Code of Conduct](#code-of-conduct)
  - [License](#license)
  - [Where to Get Help](#where-to-get-help)

## Development Environment Setup

This project uses `uv` for dependency management and provides a Makefile for common development tasks:

### Quick Setup

```bash
# One command to set up everything including Lefthook hooks
make dev
```

This command will:

- Install development dependencies
- Install git hooks
- Run Lefthook hooks across all files to fix any existing issues

### Alternative Setup (if you prefer step-by-step)

```bash
# Create virtual environment and install dependencies
make setup

# Install development dependencies
make dev

# Install Lefthook hooks
brew install lefthook  # or see docs below for alternatives
lefthook install
lefthook run pre-commit --all
```

### Available Commands

- `make setup` - Create virtual environment and install all dependencies
- `make dev` - **Complete development setup** - includes Lefthook hooks
- `make test` - Run standard tests (excludes integration tests)
- `make test-integration` - Run only integration tests (requires API keys)
- `make test-all` - Run all tests
- `make test-cov` - Run tests with coverage report
- `make lint` - Check code quality (ruff, prettier, markdownlint)
- `make format` - Auto-fix code formatting issues

## Version Bumping

**Important**: PRs should include a version bump in `src/gac/__version__.py` when they contain changes that should be released.

### How to bump the version

1. Edit `src/gac/__version__.py` and increment the version number
2. Follow [Semantic Versioning](https://semver.org/):
   - **Patch** (1.6.X): Bug fixes, small improvements
   - **Minor** (1.X.0): New features, backwards-compatible changes (e.g., adding a new provider)
   - **Major** (X.0.0): Breaking changes

### Release Process

Releases are triggered by pushing version tags:

1. Merge PR(s) with version bumps to main
2. Create a tag: `git tag v1.6.1`
3. Push the tag: `git push origin v1.6.1`
4. GitHub Actions automatically publishes to PyPI

Example:

```python
# src/gac/__version__.py
__version__ = "1.6.1"  # Bumped from 1.6.0
```

### Using bump-my-version (optional)

If you have `bump-my-version` installed, you can use it locally:

```bash
# For bug fixes:
bump-my-version bump patch

# For new features:
bump-my-version bump minor

# For breaking changes:
bump-my-version bump major
```

## Adding a New AI Provider

When adding a new AI provider, you need to update multiple files across the codebase. Follow this comprehensive checklist:

### Checklist for Adding a New Provider

- [ ] **1. Create Provider Implementation** (`src/gac/providers/<provider_name>.py`)

  - Create a new file named after the provider (e.g., `minimax.py`)
  - Implement `call_<provider>_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str`
  - Use the OpenAI-compatible format if the provider supports it
  - Handle API key from environment variable `<PROVIDER>_API_KEY`
  - Include proper error handling with `AIError` types:
    - `AIError.authentication_error()` for auth issues
    - `AIError.rate_limit_error()` for rate limits (HTTP 429)
    - `AIError.timeout_error()` for timeouts
    - `AIError.model_error()` for model errors and empty/null content
  - Set API endpoint URL
  - Use 120-second timeout for HTTP requests

- [ ] **2. Register Provider in Package** (`src/gac/providers/__init__.py`)

  - Add import: `from .<provider> import call_<provider>_api`
  - Add to `__all__` list: `"call_<provider>_api"`

- [ ] **3. Register Provider in AI Module** (`src/gac/ai.py`)

  - Add import in the `from gac.providers import (...)` section
  - Add to `provider_funcs` dictionary: `"provider-name": call_<provider>_api`

- [ ] **4. Add to Supported Providers List** (`src/gac/ai_utils.py`)

  - Add `"provider-name"` to the `supported_providers` list in `generate_with_retries()`
  - Keep the list alphabetically sorted

- [ ] **5. Add to Interactive Setup** (`src/gac/init_cli.py`)

  - Add tuple to `providers` list: `("Provider Name", "default-model-name")`
  - Keep the list alphabetically sorted
  - Add any special handling if needed (like Ollama/LM Studio for local providers)

- [ ] **6. Update Example Configuration** (`.gac.env.example`)

  - Add example model configuration in the format: `# GAC_MODEL=provider:model-name`
  - Add API key entry: `# <PROVIDER>_API_KEY=your_key_here`
  - Keep entries alphabetically sorted
  - Add comments for optional keys if applicable

- [ ] **7. Update Documentation** (`README.md` and `docs/zh-CN/README.md`)

  - Add provider name to the "Supported Providers" section in both English and Chinese READMEs
  - Keep the list alphabetically sorted within its bullet points

- [ ] **8. Create Comprehensive Tests** (`tests/providers/test_<provider>.py`)

  - Create test file following the naming convention
  - Include these test classes:
    - `Test<Provider>Imports` - Test module and function imports
    - `Test<Provider>APIKeyValidation` - Test missing API key error
    - `Test<Provider>ProviderMocked(BaseProviderTest)` - Inherit from `BaseProviderTest` for 9 standard tests
    - `Test<Provider>EdgeCases` - Test null content and other edge cases
    - `Test<Provider>Integration` - Real API call tests (marked with `@pytest.mark.integration`)
  - Implement required properties in the mocked test class:
    - `provider_name` - Provider name (lowercase)
    - `provider_module` - Full module path
    - `api_function` - The API function reference
    - `api_key_env_var` - Environment variable name for API key (or None for local providers)
    - `model_name` - Default model name for testing
    - `success_response` - Mock successful API response
    - `empty_content_response` - Mock empty content response

- [ ] **9. Bump Version** (`src/gac/__version__.py`)
  - Increment the **minor** version (e.g., 1.10.2 → 1.11.0)
  - Adding a provider is a new feature and requires a minor version bump

### Example Implementation

See the MiniMax provider implementation as a reference:

- Provider: `src/gac/providers/minimax.py`
- Tests: `tests/providers/test_minimax.py`

### Key Points

1. **Error Handling**: Always use the appropriate `AIError` type for different error scenarios
2. **Null/Empty Content**: Always check for both `None` and empty string content in responses
3. **Testing**: The `BaseProviderTest` class provides 9 standard tests that every provider should inherit
4. **Alphabetical Order**: Keep provider lists sorted alphabetically for maintainability
5. **API Key Naming**: Use the format `<PROVIDER>_API_KEY` (all uppercase, underscores for spaces)
6. **Provider Name Format**: Use lowercase with hyphens for multi-word names (e.g., "lm-studio")
7. **Version Bump**: Adding a provider requires a **minor** version bump (new feature)

## Coding Standards

- Target Python 3.10+ (3.10, 3.11, 3.12, 3.13, 3.14)
- Use type hints for all function parameters and return values
- Keep code clean, compact, and readable
- Avoid unnecessary complexity
- Use logging instead of print statements
- Formatting is handled by `ruff` (linting, formatting, and import sorting in one tool; max line length: 120)
- Write minimal, effective tests with `pytest`

## Git Hooks (Lefthook)

This project uses [Lefthook](https://github.com/evilmartians/lefthook) to keep code quality checks fast and consistent. The configured hooks mirror our previous pre-commit setup:

- `ruff` - Python linting and formatting (replaces black, isort, and flake8)
- `markdownlint-cli2` - Markdown linting
- `prettier` - File formatting (markdown, yaml, json)
- `check-upstream` - Custom hook to check for upstream changes

### Setup

**Recommended approach:**

```bash
make dev
```

**Manual setup (if you prefer step-by-step):**

1. Install Lefthook (choose the option that matches your setup):

   ```sh
   brew install lefthook          # macOS (Homebrew)
   # or
   cargo install lefthook         # Rust toolchain
   # or
   asdf plugin add lefthook && asdf install lefthook latest
   ```

2. Install the git hooks:

   ```sh
   lefthook install
   ```

3. (Optional) Run against all files:

   ```sh
   lefthook run pre-commit --all
   ```

The hooks will now run automatically on each commit. If any checks fail, you'll need to fix the issues before committing.

### Skipping Git Hooks

If you need to skip the Lefthook checks temporarily, use the `--no-verify` flag:

```sh
git commit --no-verify -m "Your commit message"
```

Note: This should only be used when absolutely necessary, as it bypasses important code quality checks.

## Testing Guidelines

The project uses pytest for testing. When adding new features or fixing bugs, please include tests that cover your
changes.

Note that the `scripts/` directory contains test scripts for functionality that cannot be easily tested with pytest.
Feel free to add scripts here for testing complex scenarios or integration tests that would be difficult to implement
using the standard pytest framework.

### Running Tests

```sh
# Run standard tests (excludes integration tests with real API calls)
make test

# Run only provider integration tests (requires API keys)
make test-integration

# Run all tests including provider integration tests
make test-all

# Run tests with coverage
make test-cov

# Run specific test file
uv run -- pytest tests/test_prompt.py

# Run specific test
uv run -- pytest tests/test_prompt.py::TestExtractRepositoryContext::test_extract_repository_context_with_docstring
```

#### Provider Integration Tests

Provider integration tests make real API calls to verify that provider implementations work correctly with actual APIs. These tests are marked with `@pytest.mark.integration` and are skipped by default to:

- Avoid consuming API credits during regular development
- Prevent test failures when API keys are not configured
- Keep test execution fast for rapid iteration

To run provider integration tests:

1. **Set up API keys** for the providers you want to test:

   ```sh
   export ANTHROPIC_API_KEY="your-key"
   export CEREBRAS_API_KEY="your-key"
   export GEMINI_API_KEY="your-key"
   export GROQ_API_KEY="your-key"
   export OPENAI_API_KEY="your-key"
   export OPENROUTER_API_KEY="your-key"
   export STREAMLAKE_API_KEY="your-key"
   export ZAI_API_KEY="your-key"
   # LM Studio and Ollama require a local instance running
   # API keys for LM Studio and Ollama are optional unless your deployment enforces authentication
   ```

2. **Run provider tests**:

   ```sh
   make test-integration
   ```

Tests will skip providers where API keys are not configured. These tests help detect API changes early and ensure compatibility with provider APIs.

## Code of Conduct

Be respectful and constructive. Harassment or abusive behavior will not be tolerated.

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

## Where to Get Help

- For troubleshooting, see [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
- For usage and CLI options, see [../USAGE.md](../USAGE.md)
- For license details, see [../LICENSE](../LICENSE)

Thank you for helping improve gac!
