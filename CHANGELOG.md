<!-- markdownlint-disable MD024 -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [TODO]

- A cleaner approach would be to reorganize the modules by extracting a core domain layer separate from utility
  functions, reducing cross-module dependencies.
- Enhance Test Coverage for Complex Functionality: The project needs more comprehensive tests for core features like
  error handling in generate_commit_message(), edge cases in error classification logic, and complete verification of
  the multi-level configuration system to ensure robustness in real-world scenarios.
- Key redaction: Add key redaction to sensitive data in logs and error messages.
- Large repo optimization: Optimize handling of large repositories with many files and directories.
- Error handling enhancement: Improve error messages and classification logic.
- Quick start guide: Add a quick start guide for new users.
- Document configuration precedence and best practices.
- Document real-world usage patterns and best practices.

## [Unreleased]

## [1.0.0] - 2025-04-13

### Added 🚀

- **Repository Context Enrichment**:
  - Added intelligent repository context extraction to improve AI commit messages
  - Implemented extraction of file purposes from docstrings
  - Added recent commit history for modified files
  - Included repository structure and branch information
  - Created example script in `examples/repo_context_example.py`
  - Added comprehensive unit tests for context extraction

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

- **Error Handling**:

  - Improved error handling in main workflow
  - Simplified error paths and recovery mechanisms
  - Enhanced error message display and logging

- **AI Model Integration**:

  - Added robust fallback mechanism for AI model generation
  - Implemented multi-model support with intelligent model selection
  - Improved token counting and diff preprocessing for AI prompts

- **Configuration**:
  - Updated default AI model to `groq:meta-llama/llama-4-scout-17b-16e-instruct`
  - Added backup model configuration
  - Loosened dependency version constraints

### Removed 🗑️

- Removed unnecessary type annotations and complex error handling patterns
- Simplified import statements and module interactions

### Fixed 🐛

- Corrected commit message cleaning logic
- Improved handling of code block markers in generated commit messages
- Enhanced diff preprocessing to handle large repositories

### CI/Build 🏗️

- Updated nightly workflow to run at 5am Los Angeles time
- Refined workflow triggers and conditions
- Updated Python version support to 3.13
- Improved release and tagging mechanisms

### Performance ⚡

- Optimized preprocessing logic for git diffs
- Enhanced token counting and model interaction efficiency

### Documentation 📝

- Added comprehensive docstrings to core modules
- Created repository context enrichment example script
- Updated project roadmap and todo items in changelog

### Security 🛡️

- Improved error handling to prevent potential code execution paths
- Enhanced input validation in preprocessing modules

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
