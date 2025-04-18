# Git Auto Commit (gac) Project Roadmap

## Current Status

Git Auto Commit (gac) is a CLI tool that uses large language models to generate meaningful commit messages based on
staged changes. The codebase now fully supports Python 3.10+, macOS, Linux, and Windows (see
[WINDOWS_COMPATIBILITY_PLAN.md](WINDOWS_COMPATIBILITY_PLAN.md)). We have completed a major architectural shift toward
functional programming, emphasizing pure functions, immutability, and composability. The codebase now follows a
functional paradigm with improved type hints, better error handling, and a more streamlined architecture. We have
significantly improved test coverage, particularly for the main.py and ai.py modules. The codebase has been simplified
by removing deprecated functions and unnecessary parameters.

## Next Steps

### Short-term Goals

1. **Complete Functional Programming Transition** ✅

   - [x] Redesign core modules around pure functions with explicit dependencies
   - [x] Improve data flow with immutability principles
   - [x] Replace remaining class-based interfaces with function-based alternatives
   - [x] Remove all dual implementation patterns
   - [x] Create a consistent error handling approach based on functional patterns

2. **Simplify Core Architecture** ✅

   - [x] Consolidate utility functions into domain-specific modules
   - [x] Remove redundant abstraction layers
   - [x] Reduce parameter counts in complex functions
   - [x] Create pipeline helpers for common workflows
   - [x] Replace environment variable configuration with pure configuration objects
   - [x] Develop a unified logging strategy compatible with functional paradigm
   - [x] Extract side effects to the edges of the application
   - [x] Implement more detailed function documentation

3. **Performance and Reliability Improvements** 🔄

   - [x] Optimize token usage for large diffs
   - [x] Implement smart truncation for git diffs
   - [x] Add token counting mechanism for different AI models
   - [x] Create more robust connection error handling
   - [x] Implement request retry mechanisms with backoff
   - [x] Add filesystem-based fallbacks for network failures
   - [x] Improve performance for large repositories

4. **Usability and Customization** ✅

   - [x] Implement template-based prompt system
   - [x] Add support for user-configurable prompts
   - [x] Create better documentation for template customization
   - [x] Simplify configuration management
   - [x] Remove non-essential configuration wizard

5. **User Experience Improvements** 🔄

   - [x] Replace custom spinner with Halo for better progress indication
   - [x] Progressive loading of AI responses
   - [x] Implement better error recovery for failed API calls
   - [ ] Create better visualization of diff context

## Current Sprint Focus

- [x] **Configuration Simplification**: Remove complex configuration wizard
- [x] **Markdown Linting**: Migrate to markdownlint-cli2
- [x] **Test Coverage**: Add comprehensive test cases for constants and utilities
- [x] **Release Workflow**: Update semantic versioning approach
- [x] **Configuration Management**: Implement multi-level configuration loading
- [x] **Dependency Management**: Update Makefile and dependency handling
- [x] **Windows Support**: Implement and document full Windows compatibility

## Next Sprint

- [ ] **Advanced Configuration System** 🔧:

  - [ ] Design a robust, flexible configuration management system
    - Implement a clear hierarchy of configuration sources
    - Create a unified configuration loading mechanism
    - Support for multiple configuration file formats (env, toml, yaml)
  - [ ] Develop comprehensive configuration validation
    - Add schema validation for configuration files
    - Implement detailed error reporting for configuration issues
    - Create meaningful validation messages for users
  - [ ] Improve configuration discovery and loading
    - Clearly define and document configuration file precedence
    - Add logging for configuration file detection and loading
    - Support for environment-specific configurations
  - [ ] Create detailed documentation for configuration system
    - Document exact order of configuration file lookup
    - Provide clear examples of configuration file usage
    - Explain how to override configurations at different levels

- [ ] **Configuration Documentation**:

  - [ ] Create comprehensive documentation for configuration file precedence
    - Explicitly document the exact order GAC looks for configuration:
      1. Command-line arguments (highest priority)
      2. Project-level `.gac.env`
      3. User-level `~/.gac.env`
      4. Package-level `config.env`
      5. Default built-in values (lowest priority)
    - Provide clear examples of how configuration is resolved
    - Explain how to customize and override configurations
    - Add troubleshooting guide for configuration issues

- [ ] **Performance Optimization**:

  - [ ] Further optimize token usage for large repositories
  - [ ] Implement intelligent diff processing strategies
  - [ ] Add configurable token limit settings

- [ ] **Testing and Quality**:

  - [ ] Increase test coverage for configuration and AI modules
  - [ ] Add more comprehensive error handling tests
  - [ ] Implement property-based testing for core functions

- [ ] **Windows Compatibility**:

  - [ ] Ensure cross-platform path handling using `pathlib.Path`
  - [ ] Implement platform-specific shell command execution
  - [ ] Handle Windows-specific environment variables
  - [ ] Update documentation with Windows setup instructions
  - [ ] Add Windows job to CI/CD pipeline
  - [ ] Test and validate all functionality on Windows

## Long-term Vision

Our simplified vision remains:

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
- **Interactive mode**: Planning to add limited interactive refinement capability
- **Request retry mechanisms**: Implemented to improve reliability

## Completed Items

- [x] Basic implementation with multiple LLM providers
- [x] Command-line interface with various options
- [x] Optimized token usage for large diffs
- [x] Improved error handling with specific error types
- [x] Support for multiple configuration locations
- [x] Simplified configuration management
- [x] Removed non-essential configuration wizard
- [x] Updated release workflow with semantic versioning
- [x] Migrated to markdownlint-cli2
- [x] Added comprehensive test cases for constants and utilities
- [x] Implemented multi-level configuration loading
- [x] Simplified main.py configuration handling

## Token Optimization Strategy

### Current Implementation

Our token optimization strategy focuses on intelligent handling of large diffs and AI model interactions:

1. **Smart Truncation**

   - Dynamically truncate git diffs based on token limits
   - Preserve critical context while reducing overall token count
   - Implement model-specific tokenization strategies

2. **Intelligent Token Counting**

   - Use `tiktoken` for accurate token counting across different models
   - Support multiple encoding strategies (Claude, OpenAI, etc.)
   - Dynamically select appropriate tokenization method

3. **Diff Processing**
   - Prioritize meaningful changes over large, auto-generated files
   - Skip known large file patterns (lock files, build artifacts)
   - Implement token-aware diff selection

### Future Enhancements

- Develop additional configurable token limit settings
- Create more adaptive truncation algorithms
- Improve context preservation during diff reduction
- Add support for more AI model tokenization strategies

### Technical Challenges

- Maintaining semantic meaning while reducing token count
- Handling diverse file types and programming languages
- Balancing performance with comprehensive context

### Guiding Principles

- Minimize token usage without losing critical information
- Provide transparent, predictable truncation
- Support multiple AI providers with different tokenization methods
