# Bidra til gac

[English](../en/CONTRIBUTING.md) | [简体中文](../zh-CN/CONTRIBUTING.md) | [繁體中文](../zh-TW/CONTRIBUTING.md) | [日本語](../ja/CONTRIBUTING.md) | [한국어](../ko/CONTRIBUTING.md) | [हिन्दी](../hi/CONTRIBUTING.md) | [Tiếng Việt](../vi/CONTRIBUTING.md) | [Français](../fr/CONTRIBUTING.md) | [Русский](../ru/CONTRIBUTING.md) | [Español](../es/CONTRIBUTING.md) | [Português](../pt/CONTRIBUTING.md) | **Norsk** | [Svenska](../sv/CONTRIBUTING.md) | [Deutsch](../de/CONTRIBUTING.md) | [Nederlands](../nl/CONTRIBUTING.md) | [Italiano](../it/CONTRIBUTING.md)

Takk for din interesse i å bidra til dette prosjektet! Din hjelp blir satt pris på. Vennligst følg disse retningslinjene for å gjøre prosessen smidig for alle.

## Table of Contents

- [Bidra til gac](#bidra-til-gac)
  - [Table of Contents](#table-of-contents)
  - [Development Environment Setup](#development-environment-setup)
    - [Quick Setup](#quick-setup)
    - [Alternative Setup (if you prefer step-by-step)](#alternative-setup-if-you-prefer-step-by-step)
    - [Available Commands](#available-commands)
  - [Version Bumping](#version-bumping)
    - [How to bump the version](#how-to-bump-the-version)
    - [Release Process](#release-process)
    - [Using bump-my-version (optional)](#using-bump-my-version-optional)
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

- For troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- For usage and CLI options, see [USAGE.md](USAGE.md)
- For license details, see [../../LICENSE](../../LICENSE)

Thank you for helping improve gac!
