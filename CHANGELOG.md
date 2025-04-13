<!-- markdownlint-disable MD024 -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added 🚀

- **Configuration Management**:

  - Added package-level configuration file `config.env` in `src/gac` directory with default model
    `anthropic:claude-3-5-haiku-latest`
  - Implemented multi-level configuration loading with precedence:
    1. Project-level `.gac.env`
    2. User-level `~/.gac.env`
    3. Package-level `config.env`
  - Added new test files to improve test coverage:
    - `test_constants.py` with comprehensive tests for project constants
    - `test_utils.py` to validate utility functions

- **Testing Improvements**:
  - Enhanced test suite with more comprehensive test cases
  - Added tests for:
    - File status enums
    - Logging constants
    - Encoding constants
    - Error handling scenarios
    - Prompt message cleaning

### Changed 🔧

- **Release Workflow**:

  - Updated GitHub Actions release workflow to use semantic versioning
  - Modified version bumping to use `minor` instead of `patch`
  - Dynamically extract version and release notes from repository state
  - Use `github.ref_name` for tag and release body generation

- **Configuration and CLI**:

  - Removed non-essential configuration wizard
  - Simplified `main.py` configuration handling
  - Removed `--config` flag from CLI options
  - Streamlined configuration loading process

- **Markdown Linting**:

  - Migrated from `.markdownlint.yaml` to `.markdownlint-cli2.yaml`
  - Updated Makefile to use `markdownlint-cli2` for Markdown linting
  - Added configuration for more consistent markdown formatting

- **Project Structure**:
  - Reorganized `.gitignore` for improved clarity and organization
  - Removed deprecated and unused test files
  - Simplified project configuration files

### Removed 🗑️

- **Deprecated Components**:
  - Removed `SIMPLIFICATION.md` documentation file
  - Deleted unused test files: `test.txt` and `testfile.txt`
  - Removed legacy `.markdownlint.yaml` configuration
  - Eliminated references to non-existent configuration wizard

### Refactored 🛠️

- **Test Suite**:

  - Simplified test cases for better maintainability
  - Streamlined test functions to focus on essential scenarios
  - Improved test coverage for core modules
  - Updated existing test files with more comprehensive test cases

- **Configuration Handling**:
  - Refactored configuration loading to use a more functional approach
  - Improved error handling and configuration validation
  - Removed complex configuration management logic

## [v0.7.0] - 2025-04-06

### Changed 🔧

- Updated default AI model to `groq:meta-llama/llama-4-scout-17b-16e-instruct`
- Added `anthropic:claude-3-5-haiku-latest` as the backup model
- Increased line length limit to 120 characters in markdown linting configurations
- Updated `.gitignore` file to include `.gac.env`
- Refactored `.env.example` to `.gac.env.example` for clarity
- Enhanced configuration management with support for multiple config locations

### Removed 🗑️

- Removed obsolete documentation files (CHANGES.md, DEVELOPMENT.md, REFACTORING.md)
- Removed unused demo script and test-specific functionality
- Removed deprecated model update script and example file
- Removed unused prompt template file

### Fixed 🐛

- Fixed condition to prevent staging when in dry run mode
- Improved remote push validation and error handling
- Improved commit message generation retry logic and error handling
- Updated test.txt to reflect new test case

### Refactored 🛠️

- Improved error handling in `main.py` for git repository checks
- Updated `errors.py` for consistent error messages
- Refactored `format_files` function to return a list instead of dictionary
- Consolidated AI-related functionality into a single cohesive module
- Standardized error handling throughout the application
- Simplified Git module with improved documentation
- Improved CLI option descriptions
- Simplified codebase through consolidation
- Separated CLI logic from main application workflow
- Improved formatter configuration lookup
- Enhanced AI model configuration and error handling

### CI/Build 🏗️

- Updated GitHub Actions workflow and Makefile
- Added Prettier formatting to lint target in Makefile
- Improved nightly release workflow logic

## [v0.6.1] - 2025-04-04

### Added 🚀

- Advanced semantic diff analysis for more contextual commit messages
- Improved git diff parsing for complex repository structures
- Enhanced AI model compatibility layer
- Detailed token usage reporting and optimization
- Added `--version` flag to display the current version of the tool

### Changed 🔧

- Refined functional programming patterns in core modules
- Improved error resilience in AI provider integrations
- Streamlined configuration validation mechanisms

### Fixed 🐛

- Resolved edge cases in multi-file staging scenarios
- Improved handling of large monorepo git diffs
- Enhanced security checks in configuration loading

### Performance ⚡

- Optimized token counting for large diffs
- Reduced memory footprint in AI processing pipeline

### Security 🛡️

- Added additional input sanitization for AI prompts
- Improved environment variable handling for sensitive configurations

## [v0.6.0] - 2025-04-03

### Added 🌟

- Comprehensive markdownlint and Prettier configuration for improved code style consistency
- Node.js project configuration for frontend tooling support
- Enhanced CI/CD workflows with scheduled nightly builds and dependency management

### Changed 🔄

- Simplified print utility functions with direct Rich console usage
- Refactored AI generation and configuration handling for improved modularity
- Updated project architecture to emphasize functional programming principles
- Optimized token counting and diff truncation logic
- Replaced custom spinner implementation with direct Halo usage
- Enhanced error handling and logging mechanisms

### Deprecated 🗑️

- Removed legacy OOP abstractions and wrapper classes
- Discontinued support for multiple CLI subcommands

### Removed 🚫

- Deprecated and unused functions across multiple modules
- Redundant run_subprocess wrapper in git module
- Custom spinner implementation

### Fixed 🐞

- Resolved configuration wizard TypeError in main script
- Improved config module with simplified configuration management
- Enhanced error handling in AI and configuration modules

### Security 🔒

- Updated dependency management to use uv for more secure and reproducible builds
- Improved CI workflow security with virtual environment activation and dependency isolation

## [0.5.0] - 2025-04-01

### Added 🌈

- **Functional Programming**: Complete architectural redesign around functional programming principles
- **Pure Functions**: Refactored core modules to use pure functions with explicit dependencies
- **Function Composition**: New pipeline approach for commit workflow
- **Type Hints**: Comprehensive type annotations throughout the codebase
- Push functionality to commit workflow
- Support for more flexible logging levels
- Pydantic-based configuration management
- Enhanced error handling with improved logging
- Progressive loading of AI responses
- User-configurable prompt templates
- Compatibility layer for existing scripts and workflows

### Changed 🔧

- Simplified project architecture with function-based design
- Simplified CLI with a single main function and no subcommands
- Replaced custom spinner with Halo for progress indication
- Updated dependency management to use uv
- Shifted to more behavior-driven testing approach
- Improved developer experience and contribution workflow
- Enhanced prompt template system with more flexible configuration
- Improved error messages with more actionable guidance
- Consolidated and optimized code structure across modules

### Deprecated 🚫

- Legacy OOP abstractions and wrapper classes
- Custom caching implementation

### Removed 🗑️

- CLI subcommand structure (now using a single direct command)
- cli.py module (merged functionality into main.py)
- Redundant wrapper classes
- Deprecated modules and outdated scripts
- Circular dependencies between modules
- Custom spinner implementation

### Fixed 🐛

- Improved git staging and repository initialization handling
- Enhanced error logging and user interaction
- Resolved issues with prompt template configuration
- Streamlined error recovery mechanisms

## [0.4.4] - 2025-04-01

### Fixed 🐛

- Added missing `questionary` dependency to fix installation issues
- Fixed prompt template not found error by adding default template in package directory

## [0.4.3] - 2025-03-30

### Added 🚀

- New code formatters for JavaScript, TypeScript, Markdown, HTML, CSS, JSON, YAML, Rust, and Go
- Support for splitting simulation mode and test mode with all-caps labeling

### Changed 🔧

- Refactored `ai_utils.py` with improved token counting and encoding detection
- Simplified constants and git module imports
- Enhanced formatting system with optimized file detection and formatter integration
- Removed pytest's `--no-cov` flag in configuration

### Improved 🌟

- Increased test coverage to 94%
- Streamlined configuration and formatting modules

### Refactored 🛠️

- Updated `main()` to support enhanced formatting system for all file types
- Simplified git module functions and added more robust file handling

## [0.4.2] - 2025-03-31

### Added 🚀

- **Tiktoken integration** for advanced token counting and model-specific encoding support
- Enhanced large file handling in git diff processing

### Changed 🔧

- Improved token counting logic using tiktoken for more accurate token estimation
- Refactored git diff handling to manage large files and reduce token usage
- Updated AI utility functions to support better token counting across different models

### Fixed 🐛

- Refined token counting algorithm to handle various input types and models
- Improved subprocess error handling in git diff processing
- Enhanced test coverage for token counting and git utilities

### Refactored 🛠️

- Restructured AI utility functions for more robust token counting
- Simplified git diff processing with better large file detection
- Updated test fixtures to support new token counting methods

## [0.4.1] - 2025-03-29

### Bug Fixes 🐞

- Fix release workflow to use pip install -e ".[dev]" instead of requirements.txt

## [0.4.0] - 2025-03-29

### Added 🌟

- Enhanced project description retrieval for improved commit message context
- Added optional hint context for commit messages
- Added one-liner commit message generation option
- 🔍 Added support for simulated files in test mode
- 🚀 Created changelog preparation script for release management
- 🔧 Added formatting module with code extraction

### Changed 🔄

- 🛠️ Refactored git status detection and file handling methods
- 💡 Updated multi-provider examples with latest model names
- 📊 Reduced default max output tokens from 8192 to 512
- 🔄 Switched from `bumpversion` to `bump-my-version` for version management
- 🧩 Enhanced test mode with real diff and simulation support
- 📝 Updated `.env.example` configuration details

### Removed 🗑️

- 🗑️ Deleted `run_tests.sh` and `run_tests.py` scripts

### Fixed 🐛

- 🐛 Improve git staged files detection and staging
- 🔧 Remove colon from commit prompts
- 📝 Enhance token parsing and validation in configuration
- 🛡️ Improve error handling in configuration and core modules

### Security 🔒

- 📦 Enhanced version bumping and release processes in CI/CD workflows
- 🔐 Added GitHub release workflow with version management

## [0.3.1] - 2025-03-27

### Added 🌟

- 🌟 Enhanced project description retrieval feature to improve context for commit messages
- 📝 Added option for generating one-liner commit messages
- ✅ Added Codecov test results upload to CI workflow
- 📝 Created `conftest.py` to improve test configuration and module importing

### Changed 🔧

- 🔧 Updated CI workflow to use Python 3.13
- 🛠️ Switched from `bumpversion` to `bump-my-version` for version management
- 📊 Updated coverage configuration and test reporting
- 💡 Enhanced `send_to_llm()` function with optional one-liner commit message generation
- 📉 Reduced default max output tokens from 8192 to 512
- 🔍 Updated multi-provider examples with latest model names

### Removed 🗑️

- 🗑️ Deleted `run_tests.sh` and `run_tests.py` scripts

### Fixed 🐛

- 🐛 Improve git staged files detection and staging
- 🔧 Remove colon from commit prompts
- 📝 Enhance token parsing and validation in configuration
- 🛡️ Improve error handling in configuration and core modules
