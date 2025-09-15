# Contributing to gac

Thank you for your interest in contributing to this project! Your help is appreciated. Please follow these guidelines to
make the process smooth for everyone.

## Table of Contents

- [Contributing to gac](#contributing-to-gac)
  - [Table of Contents](#table-of-contents)
  - [How to Contribute](#how-to-contribute)
  - [Version Bumping](#version-bumping)
  - [Coding Standards](#coding-standards)
  - [Pre-commit Hooks](#pre-commit-hooks)
  - [Testing Guidelines](#testing-guidelines)
    - [Running Tests](#running-tests)
  - [Code of Conduct](#code-of-conduct)
  - [License](#license)
  - [Where to Get Help](#where-to-get-help)

## How to Contribute

- **Report Bugs**: Use GitHub Issues to report bugs. Please provide clear steps to reproduce and relevant logs or
  screenshots.
- **Suggest Features**: Open an Issue to propose new features. Describe your idea and its use case.
- **Submit Pull Requests**:
  1. Fork the repository and create your branch from `main`.
  2. Make your changes following the coding standards below.
  3. Add or update tests as needed.
  4. Ensure all tests pass (`pytest`).
  5. Bump the version in `src/gac/__version__.py` if this is a releasable change.
  6. Update `CHANGELOG.md` with your changes.
  7. Submit a pull request with a clear description of your changes.

If you have questions or want to discuss ideas before contributing, please open an issue or start a discussion on
GitHub.

## Version Bumping

**Important**: PRs should include a version bump in `src/gac/__version__.py` when they contain changes that should be released.

### How to bump the version

1. Edit `src/gac/__version__.py` and increment the version number
2. Follow [Semantic Versioning](https://semver.org/):
   - **Patch** (0.0.X): Bug fixes, small improvements
   - **Minor** (0.X.0): New features, backwards-compatible changes
   - **Major** (X.0.0): Breaking changes

### Release Process

Releases are triggered by pushing version tags:

1. Merge PR(s) with version bumps to main
2. Create a tag: `git tag v0.17.3`
3. Push the tag: `git push origin v0.17.3`
4. GitHub Actions automatically publishes to PyPI

Example:

```python
# src/gac/__version__.py
__version__ = "0.17.3"  # Bumped from 0.17.2
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

- Target Python 3.13
- Use type hints for all function parameters and return values
- Keep code clean, compact, and readable
- Avoid unnecessary complexity
- Use logging instead of print statements
- Formatting is handled by `black`, `isort`, and `flake8` (max line length: 120)
- Write minimal, effective tests with `pytest`

## Pre-commit Hooks

This project uses pre-commit to ensure code quality and consistency. The following hooks are configured:

- `black` - Code formatting
- `isort` - Import sorting
- `flake8` - Linting
- `markdownlint-cli2` - Markdown linting
- `prettier` - File formatting (markdown, yaml, json)

### Setup

1. Install pre-commit:

   ```sh
   pip install pre-commit
   ```

2. Install the git hooks:

   ```sh
   pre-commit install
   ```

3. (Optional) Run against all files:

   ```sh
   pre-commit run --all-files
   ```

The hooks will now run automatically on each commit. If any checks fail, you'll need to fix the issues before committing.

### Skipping Pre-commit Hooks

If you need to skip the pre-commit hooks temporarily, use the `--no-verify` flag:

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
# Run all tests
make test

# Run specific test file
python -m pytest tests/test_prompt.py

# Run specific test
python -m pytest tests/test_prompt.py::TestExtractRepositoryContext::test_extract_repository_context_with_docstring
```

## Code of Conduct

Be respectful and constructive. Harassment or abusive behavior will not be tolerated.

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

## Where to Get Help

- For troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- For usage and CLI options, see [USAGE.md](USAGE.md)
- For installation, see [INSTALLATION.md](INSTALLATION.md)
- For license details, see [LICENSE](LICENSE)

Thank you for helping improve gac!
