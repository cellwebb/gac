# Git Auto Commit (gac) Project Roadmap

## Current Status

Git Auto Commit (gac) is a CLI tool that uses large language models to generate meaningful commit messages based on
staged changes. The codebase now fully supports Python 3.10+, macOS, Linux, and Windows. We have completed a major
architectural shift toward functional programming, emphasizing pure functions, immutability, and composability. The
codebase now follows a functional paradigm with improved type hints, better error handling, and a more streamlined
architecture. Test coverage is strong, and the codebase is simpler and easier to maintain.

## Next Updates and Historical Milestones

### Upcoming Updates

- [ ] Performance improvements for large repositories and diffs
- [ ] Smarter diff context visualization
- [ ] Additional configuration and prompt customization options
- [ ] Further simplification of configuration management
- [ ] Selective addition of new AI providers as they become available
- [ ] Ongoing improvements to error handling and reliability
- [ ] Additional test coverage for interactive CLI and config modules

### Historical Milestones & Completed Goals

- [x] Basic implementation with multiple LLM providers
- [x] Command-line interface with various options
- [x] Full functional programming refactor
- [x] Interactive setup (`gac init`) for configuration
- [x] Windows/macOS/Linux compatibility
- [x] Improved test coverage and error handling
- [x] Simplified configuration and logging
- [x] Functional Programming Transition
  - [x] Redesign core modules around pure functions with explicit dependencies
  - [x] Improve data flow with immutability principles
  - [x] Replace remaining class-based interfaces with function-based alternatives
  - [x] Remove all dual implementation patterns
  - [x] Create a consistent error handling approach based on functional patterns
- [x] Core Architecture Simplification
  - [x] Consolidate utility functions into domain-specific modules
  - [x] Remove redundant abstraction layers
  - [x] Reduce parameter counts in complex functions
  - [x] Create pipeline helpers for common workflows
  - [x] Replace environment variable configuration with pure configuration objects
  - [x] Develop a unified logging strategy compatible with functional paradigm
  - [x] Extract side effects to the edges of the application
  - [x] Implement more detailed function documentation
- [x] Performance and Reliability
  - [x] Optimize token usage for large diffs
  - [x] Implement smart truncation for git diffs
  - [x] Add token counting mechanism for different AI models
  - [x] Create more robust connection error handling
  - [x] Implement request retry mechanisms with backoff
  - [x] Add filesystem-based fallbacks for network failures
  - [x] Improve performance for large repositories
- [x] Usability and Customization
  - [x] Implement template-based prompt system
  - [x] Add support for user-configurable prompts
  - [x] Create better documentation for template customization
  - [x] Simplify configuration management
  - [x] Remove non-essential configuration wizard
- [x] User Experience
  - [x] Replace custom spinner with Halo for better progress indication
  - [x] Progressive loading of AI responses
  - [x] Implement better error recovery for failed API calls
  - [x] Add interactive `gac init` setup for configuration with provider/model/API key selection and backup model
        support
  - [x] Improved visualization of diff context
- [x] Platform & CI
  - [x] Implement and document full Windows compatibility
  - [x] Update release workflow with semantic versioning
  - [x] Migrate to markdownlint-cli2
  - [x] Add comprehensive test cases for constants and utilities
  - [x] Implement multi-level configuration loading
  - [x] Simplify main.py configuration handling

## Long-term Vision

Our vision remains:

1. **Core Functionality**: Generate excellent commit messages using AI with minimal complexity
2. **Functional Purity**: Maintain high functional purity for maintainability and reliability
3. **Developer Experience**: Provide a consistent and intuitive API for developers
4. **Performance**: Optimize for speed and efficiency in the commit workflow
5. **Extensibility**: Create a plugin architecture for extending functionality
6. **Customization**: Add support for user-defined prompt templates and configuration

## Explicitly Not Planned

We've decided against these items to maintain focus:

- ~~CLI subcommand structure (gac commit, gac config, etc.)~~
- ~~Command completion for shells~~
- ~~Web-based configuration interface~~
- ~~VS Code/IDE extensions~~
- ~~Multilingual commit messages~~
- ~~Complex class hierarchies and abstractions~~
- ~~Caching mechanisms of any kind~~

## Reconsidered Items

- **Adding new AI providers**: Will selectively add support for promising new models
- **Interactive mode**: Planning to add limited interactive refinement capability (now includes interactive config setup
  with `gac init`)
- **Request retry mechanisms**: Implemented to improve reliability
