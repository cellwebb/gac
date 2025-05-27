<!-- markdownlint-disable MD024 -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.13.1] - 2025-05-26

### Fixed

- Fixed filtered file handling to show summaries instead of hiding them completely
  - Binary files now display as `[Binary file change]`
  - Lockfiles and generated files show as `[Lockfile/generated file change]`
  - Minified files show as `[Minified file change]`
  - Affects both `gac diff` command output and the context sent to LLMs for commit message generation by `gac`
  - This ensures users and LLMs are aware of all file changes while keeping output clean

## [v0.13.0] - 2025-05-25

### Added

- Implemented `--scope` / `-s` command-line flag to allow specifying a scope for commit messages.
  - Supports providing a specific scope.
  - Supports requesting AI to determine the scope.
  - Supports omitting scope.
- Enhanced `gac diff` command:
  - Displays diffs for staged or unstaged changes.
  - Allows comparison between specific commits.
- Added extensive tests for new scope and diff functionalities, and increased overall test coverage.

### Changed

- Refactored `diff_cli.py` for improved command handling and new display options.
- Improved overall CLI command structure in `gac/cli.py` and `gac/main.py`.
- Enhanced repository context extraction mechanism in `gac/prompt.py`.
- Improved diff preprocessing logic for more accurate and relevant diffs.
- Updated `README.md` extensively with detailed usage for `--scope` and `gac diff`, new examples, screenshots, and a new
  usage image.
- Updated `CONTRIBUTING.md` with more information on testing.

## [v0.12.0] - 2025-05-07

### Added

- New `gac preview` command to generate commit messages for diffs without committing
  - Preview changes against HEAD or between specific commits
  - Supports all message generation options (one-liner, hint, model selection)
  - Displays formatted commit message preview
- Integration test script for preview functionality (`scripts/test_gac_preview.sh`)
- Improved installation instructions with step-by-step commands in README.md
- Unit tests for the preview command in `tests/test_cli.py`

### Changed

- Reorganized documentation files into `docs/` directory for better organization
  - Moved `INSTALLATION.md`, `USAGE.md`, `CONTRIBUTING.md`, and `TROUBLESHOOTING.md`
  - Updated all cross-references in README.md and other files
- Improved prompt handling in `prompt.py`:
  - Renamed `add_repository_context` to `extract_repository_context` for clarity
  - Better handling of hints and empty repository context
  - Fixed placeholder in prompt template (`<hint_text>` instead of `<context>`)
- Removed codecov.yml in favor of GitHub default settings

### Fixed

- Corrected links to documentation files in README.md
- Enhanced error handling in preview functionality for invalid git refs

## [v0.11.0] - 2025-04-18

### Added

- Interactive `gac init` command for guided provider/model/API key configuration.
- Improved documentation for installation, configuration, and troubleshooting (`INSTALLATION.md`, `TROUBLESHOOTING.md`,
  `README.md`)
- Registration links for Groq, Anthropic, OpenAI, and Mistral in docs
- Clearer explanation of environment variable usage and config file precedence

### Changed

- Provider API key environment variables now use standard names (`GROQ_API_KEY`, `ANTHROPIC_API_KEY`, etc.)
- `gac init` and documentation updated to reserve `GAC_` prefix for internal config (e.g., `GAC_MODEL`)
- Roadmap simplified to focus on next updates and historical milestones
- Troubleshooting guide now distinguishes project-level and user-level `.gac.env` issues, with OS-specific guidance

### Fixed

- Test for `gac init` updated to expect new environment variable naming
- Minor formatting and consistency improvements in documentation and CLI output

## [v0.10.0] - 2025-04-18

### Added

- Dedicated `config_cli.py` for managing user-level configuration via CLI subcommands
- `gac config` subcommands: `show`, `set`, `get`, `unset` for easy config management in `$HOME/.gac.env`
- Unified CLI: now supports both top-level flags and subcommands (no more `gac run` wrapper)
- `scripts/test_gac_sandbox.sh` to test the GAC CLI in a sandboxed environment
- `tests/test_config_cli.py` to test the config CLI using Click's testing utilities

### Changed

- Refactored CLI entry point and wiring for greater extensibility
- Simplified configuration precedence: user-level `$HOME/.gac.env` and project-level `.env` (with env vars always taking
  precedence)
- Updated documentation to reflect new configuration workflow and CLI usage (README.md, USAGE.md, ROADMAP.md)

### Removed

- Old project-level `.gac.env` and package-level `_config.env` from config precedence
- Obsolete test code for CLI (see `tests/test_cli.py`)
- Outdated or redundant configuration documentation in roadmap and docs

### Fixed

- Minor formatting and lint issues in test and preprocess modules

## [v0.9.3] - 2025-04-17

### Changed

- Refined CI workflow to ignore additional files and directories, reducing unnecessary runs and noise
- Improved consistency in documentation and configuration management

### Documentation

- Updated roadmap to reflect completed and in-progress tasks
- Preparation for advanced configuration system implementation

## [v0.9.2] - 2025-04-17

### Added

- `test_cli.py` to test the command line interface
- `test_config.py` to test configuration loading
- Additional test cases in `test_preprocess.py`
- Additional test cases in `test_utils.py`

### Changed

- Documentation for Windows compatibility (see [docs/WINDOWS_COMPATIBILITY_PLAN.md](docs/WINDOWS_COMPATIBILITY_PLAN.md))
- Updated `README.md`, `INSTALLATION.md`, `USAGE.md`, and `ROADMAP.md` to reflect Python 3.10+ and Windows support
- Modified `cli.py` to print version information instead of logging it
- Updated `conftest.py` to silence noisy loggers during testing
- Improved code coverage by adding new test files and cases

## [v0.9.1] - 2025-04-17

### Changed

- Relocated CLI entry point from `src/gac/main.py` to `src/gac/cli.py` to improve modularity and separation of concerns
- Updated `pyproject.toml` to point at the new CLI entry location
- Simplified `main.py` to focus solely on business logic by removing CLI wiring
- Improved overall code organization and maintainability by isolating CLI-specific code

## [v0.9.0] - 2025-04-17

### Added

- Introduced configuration management via a dedicated config.py module for improved organization and reusability.
- Implemented hierarchical configuration loading with support for environment files and variables.
- Enhanced logging setup with customizable log levels, quiet mode, and suppression of noisy loggers.

### Changed

- Updated main entry point to leverage the new configuration and logging features.

### Refactored

- Removed unnecessary pytest import from test_git.py.

## [v0.8.0] - 2025-04-14

### Added

- Git utility functions for repository root, current branch, and commit hash
- Code formatting functions with Black integration
- New test cases for git utilities and code formatting
- Coverage configuration to exclude main.py
- CONTRIBUTING.md with guidelines for project contributions
- LICENSE file with MIT license
- Verbose logging option to CLI

### Changed

- Improved test parameterization in test_format.py
- Updated import statements for better organization
- Enhanced code formatting validation logic
- Improved push change handling with enhanced logging and user feedback
- Updated installation documentation for clearer configuration instructions
- Updated README with project badges and contributing information
- Refined linting commands to use check mode for black, isort, and prettier
- Updated VSCode settings to exclude more files from file explorer

### Documentation

- Enhanced dry run logging for push changes
- Improved installation and configuration guide clarity
- Updated project documentation with more precise instructions
- Added comprehensive troubleshooting guide

### CI/Build

- Improved lint and format commands with silent logging and check modes

## [0.7.2] - 2025-04-13

### Added

- **Repository Context Enrichment**:

  - Intelligent repository context extraction
  - File purpose extraction from docstrings
  - Recent commit history for modified files
  - Repository structure and branch info
  - Example script in `examples/repo_context_example.py`
  - Comprehensive unit tests

- **Configuration Management**:
  - Package-level `config.env` with default model
  - Multi-level config loading:
    1. Project-level `.gac.env`
    2. User-level `~/.gac.env`
    3. Package-level `config.env`
  - New test files for constants and utils

### Changed

- **AI Model Integration**:

  - Robust fallback mechanism for AI model generation
  - Multi-model support with intelligent selection
  - Improved token counting and diff preprocessing

- **Error Handling**:

  - Simplified error paths and recovery mechanisms
  - Enhanced error message display

- **CI/Build**:

  - Updated nightly workflow to 5am Los Angeles
  - Refined workflow triggers
  - Python 3.10 support
  - Improved release and tagging

- **Performance**:
  - Optimized git diff preprocessing
  - Enhanced token counting efficiency

### Removed

- Unnecessary type annotations
- Complex error handling patterns
- Simplified imports

### Documentation

- Comprehensive docstrings
- Repository context enrichment example
- Updated project roadmap

### Security

- Enhanced error handling
- Improved input validation

## [0.6.1]

### Added

- **Code Quality**:

  - Markdown linting configuration
  - Prettier configuration
  - VSCode launch configuration
  - Example for diff truncation

- **Testing**:
  - Main module tests
  - AI utility tests
  - Enhanced test coverage

### Changed

- **Code Organization**:

  - Reintroduced AI utilities module
  - Updated test structure
  - Improved error handling

- **Dependencies**:
  - Updated package.json and lock
  - Improved pre-commit hooks

### Fixed

- **Git Operations**:
  - Improved git diff handling
  - Enhanced error recovery

## [0.5.0]

### Added

- **Core Architecture**:

  - New AI module
  - Error handling system
  - File handling utilities
  - Formatting system
  - Prompt template system

- **Testing**:
  - Comprehensive test suite
  - Test fixtures and mocks
  - Error handling tests

### Changed

- **Code Structure**:

  - Major refactoring of core modules
  - Improved error handling
  - Enhanced formatting system

- **Documentation**:
  - Added development guide
  - Added refactoring guide
  - Updated installation guide

### Removed

- Legacy multi-provider examples
- Old changelog preparation scripts
- Old formatting system

## [0.4.3]

### Added

- **Nightly Builds**:

  - GitHub Actions workflow
  - Automated release process

- **Formatting**:

  - New formatting system
  - Support for multiple file types
  - Code formatter integration

- **Testing**:
  - Configuration tests
  - Core module tests
  - Git module tests

### Changed

- **Configuration**:

  - Enhanced config loading
  - Improved environment handling
  - Added constants module

- **Core Functionality**:
  - Improved AI utilities
  - Enhanced git integration
  - Better error handling

## [0.3.0]

### Added

- **Release Automation**:

  - Auto-release script
  - Improved CI workflow

- **Testing**:
  - Enhanced test coverage
  - Improved test fixtures
  - Better test organization

### Changed

- **Code Quality**:
  - Improved error handling
  - Better module organization
  - Enhanced git integration

## [0.2.0]

### Added

- **Core Features**:

  - AI utilities module
  - Configuration system
  - Git integration
  - Comprehensive tests

- **Documentation**:
  - Installation guide
  - How-it-works guide
  - Examples directory

### Changed

- **Project Structure**:
  - Improved module organization
  - Better test structure
  - Enhanced README

## [0.1.0] - Initial Release

## [TODO]

- Key redaction: Add key redaction to sensitive data in logs and error messages.
- Large repo optimization: Optimize handling of large repositories with many files and directories.
- Error handling enhancement: Improve error messages and classification logic.
- Choose a commit to git diff against
- Add recent git commit messages as context? If so, probably need to add a flag to control the number of commits to
  include
