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

### Added

- TROUBLESHOOTING.md with comprehensive guide for resolving common installation and configuration issues

### Changed

- Improved push change handling with enhanced logging and user feedback
- Updated installation documentation for clearer configuration instructions
- Refined linting commands to use check mode for black, isort, and prettier
- Updated VSCode settings to exclude more files from file explorer

### Documentation

- Enhanced dry run logging for push changes
- Improved installation and configuration guide clarity
- Updated project documentation with more precise instructions

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
  - Python 3.13 support
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
