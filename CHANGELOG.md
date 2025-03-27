<!-- markdownlint-disable MD024-->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- 🔧 Updated CI workflow to use Python 3.13
- 🛠️ Switched from `bumpversion` to `bump-my-version` for version management
- 💡 Enhanced `send_to_llm()` function with optional one-liner commit message generation
- 📊 Updated coverage configuration and test reporting

### Added

- ✅ Added Codecov test results upload to CI workflow
- 📝 Created `conftest.py` to improve test configuration and module importing

### Removed

- 🗑️ Deleted `run_tests.sh` and `run_tests.py` scripts
- 🧹 Removed redundant configuration references

### Fixed

- 🐛 Improved error handling and import configurations in various project files

## [0.3.0] - 2025-03-26

### Added

- 🚀 Logging verbosity and model override options in the CLI
- 🔧 Pre-release test validation in auto_release script
- 🔍 Auto-release script for version management

### Changed

- 🔄 Update Python version requirements from 3.8 to 3.10
- 🚧 Simplify model configuration logic
- 📦 Update project configuration and dependencies
- 💡 Enhance CI workflow to support Python 3.12 and 3.13
- 🔧 Migrate from bump2version to bump-my-version
- 🛠️ Update default provider models and configuration
- 📝 Reorder and update README badges

### Removed

- 🗑️ Remove deprecated setup.cfg and .bumpversion.cfg files
- ❌ Remove Python 3.8 and 3.9 from supported versions

### Fixed

- 🐛 Update test_config.py model tests
- 🔧 Update Flake8 configuration and linting

### Chore

- 📝 Update dependencies and documentation
- 🔍 Enhance project configuration and CI workflows

## [0.2.0] - 2025-03-26

### Added

- Multi-provider support via aisuite integration
- Support for multiple AI providers:
  - Anthropic Claude (default)
  - OpenAI GPT models
  - Groq LLaMA models
  - Mistral AI
  - AWS Bedrock
  - Azure OpenAI
  - Google Vertex AI
- New configuration options via environment variables:
  - `GAC_PROVIDER` - Set provider (anthropic, openai, groq, etc.)
  - `GAC_MODEL_NAME` - Set specific model for selected provider
  - `GAC_MODEL` - Set fully qualified model (provider:model)
- Command-line model selection with `--model` or `-m` flag
- Environment variables loading from .env file
- Provider-agnostic token counting
- Multi-provider example scripts
- GitHub Actions CI workflow with multiple Python versions
- Codecov integration for test coverage reporting

### Changed

- Refactored core logic to support multiple AI providers
- Updated configuration to support dynamic model and provider selection
- Renamed functions for provider neutrality
- Enhanced configuration loading from environment variables
- Improved modularization of project components
- Updated project dependencies in pyproject.toml
- Migrated to aisuite for multi-provider support
- Expanded logging and error handling mechanisms

### Deprecated

- None

### Removed

- Direct dependency on Anthropic library
- Hardcoded references to specific AI providers

### Fixed

- Improved token counting across different providers
- Enhanced error handling in configuration and AI interaction
- Fixed test coverage and added comprehensive test suite

### Security

- Added environment variable support for securely managing API keys
- Enhanced configuration validation

## [0.1.0] - 2025-03-24

### Changed

- Migrated from `hatch` to `uv` for package management.
- Updated development workflow to use `Makefile` for common tasks.
- Improved development environment setup.

## [0.1.0a1] - 2024-12-12

### Added

- Initial release of gac CLI tool
- Core functionality to generate commit messages using Claude AI
- Automatic code formatting with black and isort
- Interactive commit and push workflow
- Command line options:
  - `--test`: Run in test mode
  - `--force, -f`: Skip all prompts
  - `--add-all, -a`: Stage all changes
- Local development environment configuration with hatch
- VSCode integration and settings
- Comprehensive documentation in README.md

[0.3.0]: https://github.com/cellwebb/gac/releases/tag/v0.3.0
[0.2.0]: https://github.com/cellwebb/gac/releases/tag/v0.2.0
[0.1.0]: https://github.com/cellwebb/gac/releases/tag/v0.1.0
