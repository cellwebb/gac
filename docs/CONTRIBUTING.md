# Contributing to gac

Thank you for your interest in contributing to this project! Your help is appreciated. Please follow these guidelines to
make the process smooth for everyone.

## Table of Contents

- [Contributing to gac](#contributing-to-gac)
  - [Table of Contents](#table-of-contents)
  - [How to Contribute](#how-to-contribute)
  - [Coding Standards](#coding-standards)
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
  5. Submit a pull request with a clear description of your changes.

If you have questions or want to discuss ideas before contributing, please open an issue or start a discussion on
GitHub.

## Coding Standards

- Target Python 3.13
- Use type hints for all function parameters and return values
- Keep code clean, compact, and readable
- Avoid unnecessary complexity
- Use logging instead of print statements
- Formatting is handled by `black`, `isort`, and `flake8` (max line length: 120)
- Write minimal, effective tests with `pytest`

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
