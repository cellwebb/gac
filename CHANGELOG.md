# Changelog

## [3.10.17] - 2025-12-09

### Improvements

- Enhanced browser launch testing for better reliability

### Bug Fixes

- Fixed test coverage for browser launch failure handling

## [3.10.16] - 2025-12-09

### Improvements

- Improved test reliability for OAuth and configuration commands

### Bug Fixes

- Fixed mock target for print statements in Qwen OAuth tests

## [3.10.15] - 2025-12-09

### Improvements

- Updated Mistral model identifier for better compatibility

## [3.10.14] - 2025-12-08

### Improvements

- Enhanced test coverage across all components for better reliability
- Improved OAuth token isolation during testing to protect your credentials
- Better secret detection and validation during commit process

### Bug Fixes

- Fixed test interference with real authentication tokens
- Resolved issues with quiet mode behavior in validation tests

## [3.10.13] - 2025-12-07

### Improvements

- Better URL handling for Anthropic-compatible AI providers
- More comprehensive test coverage for better reliability
- Improved error handling and authentication flows
- Enhanced configuration management and validation
- Faster test execution with optimized mocking

## [3.10.12] - 2025-12-06

### Improvements

- Better reliability when working with grouped commits
- More comprehensive testing for interactive and grouped commit workflows
- Enhanced error handling with better debugging information

## [3.10.11] - 2025-12-06

### Improvements

- More reliable dry-run functionality with better testing coverage
- Enhanced question parsing in interactive mode for better accuracy
- Comprehensive test coverage improvements for commit execution

### Bug Fixes

- Fixed edge cases in parsing numbered list responses from AI

## [3.10.10] - 2025-12-06

### Improvements

- Better error handling and cleanup when commits fail
- Cleaner internal code structure for improved reliability
- More consistent parameter handling throughout the app

### Bug Fixes

- Fixed staging area restoration issues during failed commits
- Fixed interrupted commits leaving staging area in inconsistent state

## [3.10.9] - 2025-12-06

### Improvements

- Cleaner commit messages by removing AI reasoning blocks
- Better organization of internal code structure
- More maintainable template system for generating prompts

## [3.10.8] - 2025-12-06

### Improvements

- Better error handling when git hooks fail
- More reliable app exit behavior throughout the interface

## [3.10.7] - 2025-12-06

### Improvements

- Better internal code organization for improved reliability
- More accurate test execution with improved git command mocking
- Simplified workflow system with cleaner function signatures

### Bug Fixes

- Fixed test issues that could cause unexpected git operations

## [3.10.6] - 2025-12-06

### Improvements

- Better organization of internal code structure for improved maintainability
- More reliable OAuth authentication with unified retry handling
- Enhanced model string parsing with better error handling
- Simplified release process for smoother updates

### Bug Fixes

- Fixed test compatibility issues with updated prompt templates
- Improved error messages when model configuration is invalid

## [3.10.4] - 2025-12-06

### Improvements

- Enhanced test reliability to prevent failures in automated testing

## [3.10.3] - 2025-12-06

### Improvements

- Enhanced code quality with strict type checking and error handling
- Cleaned up unused code throughout the application for better performance

## [3.10.2] - 2025-12-06

### Improvements

- Better confirmation flow for commit messages with improved display options
- Reorganized documentation for easier provider implementation
- Enhanced testing coverage for commit workflow scenarios

## [3.10.1] - 2025-12-06

### Improvements

- Better organization with cleaner internal code structure
- More reliable git operations and commit handling
- Enhanced interactive mode with improved question flow
- Better error handling and validation throughout the app
- More comprehensive secret detection for security
- Improved provider URL handling for better consistency
- Enhanced testing coverage for more reliable operation

## [3.10.0] - 2025-12-05

### Improvements

- Better protection of your sensitive information in error messages
- Cleaner and more reliable AI provider system
- More consistent error handling across all AI providers
- Simplified internal code structure for better reliability

### Bug Fixes

- Fixed error handling in retry logic for more reliable AI responses
- Removed duplicate error handling that could cause inconsistent messages

## [3.9.3] - 2025-12-05

### Improvements

- Better error handling with specific exception types instead of generic errors
- Enhanced configuration system with improved type checking
- Cleaner code structure with more reliable error messages

## [3.9.2] - 2025-12-05

### Improvements

- Better error handling and validation for model format inputs
- Improved test reliability with consistent variable naming
- Enhanced error classification documentation and type safety

## [3.9.1] - 2025-12-05

### Improvements

- Sensitive information like API keys and tokens are now hidden when displaying configuration settings

### Bug Fixes

- Fixed configuration display to properly parse environment files and handle key-value pairs correctly

## [3.9.0] - 2025-12-05

### Improvements

- Improved performance with lazy initialization for AI providers
- Better authentication with OAuth token integration for Claude Code and Qwen
- Enhanced provider architecture for better maintainability
- Improved test coverage and reliability across all providers
- Better URL handling for custom Anthropic endpoints

### Bug Fixes

- Fixed connection error handling for LM Studio
- Fixed SSL verification for Qwen API calls
- Fixed authentication failures from expired OAuth tokens
- Fixed crashes when configuration values are missing

## [3.8.2] - 2025-12-04

### Improvements

- Added SSL verification for Qwen API calls to ensure secure connections
- Updated to version 3.8.2 with latest improvements

## [3.8.1] - 2025-12-04

### Improvements

- Better error messages when settings are invalid
- More reliable SSL certificate handling for all AI providers
- Enhanced configuration validation with clearer error messages

### Bug Fixes

- Fixed crashes when configuration values are missing
- Resolved issues with assert statements not working in optimized Python

## [3.8.0] - 2025-12-04

### What's New

- New --no-verify-ssl flag for corporate proxy environments

### Improvements

- Better SSL certificate handling for all AI providers
- Updated documentation with clearer command usage examples
- Improved code organization with consistent import paths

### Bug Fixes

- Fixed authentication issues with expired OAuth tokens

## [3.7.1] - 2025-12-04

### Improvements

- Qwen OAuth tokens now refresh automatically to prevent authentication failures
- Better authentication management with automatic retry when tokens expire
- Clear user feedback during Qwen re-authentication process

### Bug Fixes

- Fixed authentication failures from expired Qwen tokens

## [3.7.0] - 2025-12-04

### What's New

- Generate commit messages using Qwen.ai with OAuth authentication

### Improvements

- Claude Code tokens now refresh automatically to prevent authentication failures
- Better authentication management with login/logout/status commands for OAuth providers
- Enhanced token storage system for improved security and reliability

### Bug Fixes

- Fixed authentication failures from expired Claude Code tokens
- Improved Qwen API URL construction from OAuth tokens

## [3.6.4] - 2025-12-02

### Improvements

- Cleaner commit messages by removing extra whitespace

## [3.6.3] - 2025-12-01

### Improvements

- Enhanced test coverage for utility functions, provider configurations, and error handling scenarios
- Improved reliability of initialization workflows with better input validation and configuration management
- Cleaned up test modules for more consistent and maintainable test structure

## [3.6.2] - 2025-12-01

### Improvements

- Use arrow keys to navigate when answering interactive questions

## [3.6.1] - 2025-11-30

### Improvements

- Interactive mode now asks fewer questions for small changes and more questions for complex changes
- Better question scaling based on file count and line modifications for improved user experience

## [3.6.0] - 2025-11-30

### What's New

- Interactive mode with context-aware questions for more accurate commit messages
- Use --interactive/-i flag to provide additional context through Q&A

### Improvements

- clearer token warning messages about thresholds instead of limits
- Updated German and French documentation with proper AI terminology
- Enhanced documentation with interactive mode guides in 15 languages
- Simplified dependencies by removing unused halo package
- Better UI consistency with Rich status instead of Halo spinners

## [3.5.0] - 2025-11-29

### What's New

- New 'model' command to quickly update AI provider settings without changing other preferences
- Better documentation with provider lists formatted for easier reading in 15+ languages

### Improvements

- Simplified initialization workflow for cleaner setup experience
- Enhanced model configuration with support for 26+ AI providers including OpenAI, Anthropic, Azure, and custom endpoints
- Better test coverage and reliability for CLI commands and provider integrations

### Bug Fixes

- Fixed test isolation issues to prevent cross-test contamination
- Corrected model name references in provider tests for better accuracy

## [3.4.3] - 2025-11-29

### Improvements

- Fixed Kimi Coding provider key format for consistent configuration

### Bug Fixes

- Fixed provider key transformation in CLI initialization

## [3.4.2] - 2025-11-29

### Improvements

- Updated OpenAI default model to gpt-5-mini
- Updated Azure OpenAI default model to gpt-5-mini

## [3.4.1] - 2025-11-29

### Improvements

- Better error handling for Azure OpenAI provider with more comprehensive test coverage

### Bug Fixes

- Fixed version number update for 3.4.1 release

## [3.4.0] - 2025-11-29

### What's New

- Generate commit messages using Azure OpenAI provider
- Generate commit messages using Kimi Coding provider
- Generate commit messages using Moonshot AI provider

### Improvements

- Simplified provider setup with cleaner API key handling
- Updated documentation to include new providers and clearer setup instructions
- Streamlined provider registration process for better consistency

## [3.3.0] - 2025-11-15

### What's New

- Generate commit messages without committing using --message-only flag for script integration

### Improvements

- Better handling of file renames in grouped commits to preserve file history
- Comprehensive documentation in 16 languages for new --message-only functionality and script integration examples

## [3.2.0] - 2025-11-13

### What's New

- Generate commit messages using Replicate AI provider

### Improvements

- Updated OpenAI default model to gpt-5-mini
- Enhanced documentation with Replicate provider information across all languages

## [3.1.0] - 2025-11-12

### Improvements

- Better reliability with improved AI provider management
- Enhanced system architecture for easier maintenance

## [3.0.0] - 2025-11-10

### What's New

- Add support for project-level configuration files
- View both user-level and project-level settings with config show command

### Improvements

- Simplified configuration loading to only use .gac.env files
- Clear separation and labeling for different configuration sources

## [2.7.5] - 2025-11-08

### Improvements

- Better right-to-left language support with warning system
- Improved provider name handling for MiniMax.io and Synthetic.new models
- Enhanced reliability of interactive prompts and cancellations

## [2.7.4] - 2025-11-08

### Improvements

- Added Thai language support to documentation
- Improved provider name formatting to match official URLs
- Enhanced documentation formatting for supported providers list

## [2.7.3] - 2025-11-06

### Improvements

- Stay completely offline with new GAC_NO_TIKTOKEN setting
- Better documentation formatting for provider lists in all languages

## [2.7.2] - 2025-11-06

### Improvements

- Better token counting for local AI providers
- More reliable processing when network issues occur
- Enhanced error handling for unknown AI models

### Bug Fixes

- Fixed crashes when counting tokens for certain local providers

## [2.7.1] - 2025-11-06

### Improvements

- Use arrow keys and shortcuts in interactive prompts for easier navigation
- Improved Claude Code troubleshooting guide with clearer steps for expired tokens

## [2.7.0] - 2025-11-06

### What's New

- New dedicated 'gac auth' command for Claude Code OAuth authentication

### Improvements

- Simplified Claude Code re-authentication workflow
- Updated authentication instructions across all language documentation

## [2.6.1] - 2025-11-05

### What's New

- Claude Code automatically refreshes expired tokens

### Improvements

- Better documentation with simplified installation instructions
- More reliable Claude Code authentication with comprehensive test coverage

### Bug Fixes

- Fixed authentication flow issues with proper error handling

## [2.6.0] - 2025-11-05

### What's New

- Use Claude Code AI provider with secure OAuth authentication
- Comprehensive multilingual documentation for Claude Code setup

### Improvements

- Enhanced documentation with Claude Code cross-references across all languages
- Comprehensive OAuth test coverage for reliable authentication

## [2.5.2] - 2025-11-04

### What's New

- Added Norwegian, Swedish, Italian, and Vietnamese language support with complete documentation

### Improvements

- Configure timeout for git hooks with new --hook-timeout option
- Added localized screenshots for better user experience in new languages
- Improved test coverage with 791 new tests for CLI and language features

### Bug Fixes

- Fixed duplicate markdownlint directives in documentation files
- Fixed crash when hook timeout configuration was not set

## [2.5.1] - 2025-11-04

### Bug Fixes

- Fixed crash when hook timeout configuration was not set
- Hook timeout now properly defaults to 120 seconds when not specified

## [2.5.0] - 2025-11-04

### What's New

- Configure timeout for pre-commit and lefthook hooks with --hook-timeout option or GAC_HOOK_TIMEOUT environment variable

### Improvements

- Fixed broken image paths in multilingual documentation
- Updated release process documentation with clearer make commands
- Reorganized documentation structure for better internationalization

### Bug Fixes

- Corrected path references in Chinese documentation
- Fixed formatting placeholders in release documentation

## [2.4.1] - 2025-11-03

### Improvements

- Better type safety for error handling
- Improved internal code reliability

## [2.4.0] - 2025-11-03

### What's New

- Generate commit messages in your preferred language with new multilingual support
- New 'model' command to quickly update AI provider settings without changing other preferences

### Improvements

- Better compatibility with international systems using different character encodings
- Right-to-left language support with helpful warnings and confirmation preferences
- Expanded documentation with translations in German, Korean, Dutch, Spanish, Portuguese, and Hindi
- Better organized project structure with all examples moved to dedicated directory
- Simplified version management process for cleaner updates

### Bug Fixes

- Fixed crashes when working with non-English character sets on some systems
- Resolved language navigation issues by fixing broken documentation links
- Fixed filtering of empty configuration values during initialization
- Improved keyboard navigation in language selection menus

## [2.3.0] - 2025-11-03

### What's New

- Group your changes into multiple commits with the --group flag

### Improvements

- Better handling of large changes with increased token limits from 1024 to 4096
- Show file lists for each commit when using grouped commits
- Dynamic token scaling based on file count (2x-5x) for grouped commits
- Enhanced initialization with options to preserve existing API keys and language settings

### Bug Fixes

- Fixed staged changes preservation in grouped commit workflow
- Fixed English language selection to properly save configuration
- Improved security token detection for better pattern matching
- Fixed model identifier validation with clear error messages for 'provider:model' format

## [2.2.0] - 2025-11-02

### What's New

- Edit commit messages directly with new 'e' command
- Interactive terminal editor with vi/emacs key bindings

### Improvements

- Better cursor positioning and editor controls for editing
- Increased token limits to handle larger code changes
- Cleaner commit message editing with simplified interface

## [2.1.0] - 2025-10-31

### What's New

- Generate commit messages using Mistral AI provider
- New 'lang' command as a shortcut for setting commit message language

### Improvements

- Updated Cerebras AI model to zai-glm-4.6 for better performance
- Enhanced getting started guide with clearer installation instructions and screenshots
- More reliable testing with comprehensive edge case coverage
- Better language management with centralized language list

## [2.0.0] - 2025-10-30

### Improvements

- Easier feedback system for commit messages - just type your thoughts directly
- Clearer prompts when reviewing and confirming commit messages
- More flexible commit message formatting without character limits
- Better documentation reflects the simplified feedback workflow

## [1.15.0] - 2025-10-30

### What's New

- Generate commit messages in 25+ languages using language codes or full names
- Choose to translate conventional commit prefixes or keep them in English

### Improvements

- New language command for interactive language selection
- Flexible language configuration with environment variables and CLI flags

## [1.14.0] - 2025-10-29

### What's New

- Create custom system prompts to personalize how commit messages are generated

### Improvements

- Cleaner output formatting for better readability
- Better organization of prompt templates with separate system and user components

## [1.13.1] - 2025-10-28

### Improvements

- Cleaner commit messages by removing AI reasoning blocks
- Fixed grammar in provider list documentation

## [1.13.0] - 2025-10-28

### What's New

- Connect to custom Anthropic-compatible and OpenAI-compatible endpoints for more AI provider options

### Improvements

- Updated documentation screenshot to dark mode for better visibility and faster loading

## [1.12.1] - 2025-10-28

### Improvements

- Enhanced Gemini AI provider with better system instruction handling and improved response parsing

### Bug Fixes

- Fixed Gemini API errors by using the correct system instruction format
- Fixed empty text handling in Gemini responses

## [1.12.0] - 2025-10-27

### What's New

- Generate commit messages using DeepSeek AI provider

### Improvements

- Updated to version 1.12.0 with latest improvements

## [1.11.1] - 2025-10-27

### Improvements

- Generate commit messages using Together AI provider
- Standardized MiniMax branding throughout the application

## [1.11.0] - 2025-10-27

### What's New

- Generate commit messages using Minimax AI provider

### Improvements

- Enhanced documentation with comprehensive guide for adding new AI providers

## [1.10.3] - 2025-10-27

### What's New

- Generate commit messages using Together AI provider

### Improvements

- Improved project description to better highlight benefits
- Enhanced command descriptions and examples for clearer usage

## [1.10.2] - 2025-10-25

### Improvements

- Enhanced testing reliability for AI providers with better edge case handling

## [1.10.1] - 2025-10-25

### Improvements

- Faster git hook execution with new system
- Updated documentation for development setup

## [1.10.0] - 2025-10-24

### What's New

- Generate commit messages using Fireworks AI provider

### Improvements

- Better conversation context for AI-generated commit messages
- Enhanced README with visual emoji icons and streamlined installation
- More reliable AI provider handling with comprehensive edge case testing

## [1.9.5] - 2025-10-23

### Improvements

- Better documentation with clearer instructions and visual improvements
- More accurate token usage tracking when regenerating commit messages
- Cleaned up unused dependencies for faster installation
- Updated terminology throughout app for better clarity

## [1.9.4] - 2025-10-23

### Improvements

- Increased token limit for AI models that need extra reasoning space
- Better compatibility with advanced AI models that require more processing tokens

## [1.9.3] - 2025-10-23

### Improvements

- Added type checking for better code quality and reliability
- Updated OpenAI test model to gpt-5-nano for current compatibility
- Enhanced Synthetic provider with comprehensive test coverage
- Improved CI pipeline with better dependency management

## [1.9.2] - 2025-10-23

### Improvements

- Fixed provider name display from 'Chutes.ai' to 'Chutes'

### Bug Fixes

- Fixed API key handling for LM Studio provider
- Fixed provider key normalization to work consistently across all providers

## [1.9.1] - 2025-10-23

### Improvements

- Fixed LM Studio provider name for correct recognition
- Added Chutes.ai provider to supported AI options
- Updated documentation to include verbose flag for detailed commit messages

## [1.9.0] - 2025-10-23

### What's New

- Generate detailed commit messages with structured sections using verbose mode
- Set verbose mode preference through environment variable for persistent use

### Improvements

- Better commit message organization with sections for motivation and architecture
- More flexible configuration options for verbose output preferences

## [1.8.0] - 2025-10-23

### What's New

- Generate commit messages using Chutes.ai provider

### Improvements

- Updated Anthropic model to claude-haiku-4-5 for better compatibility

### Bug Fixes

- Fixed LM Studio provider name in provider list

## [1.7.0] - 2025-10-23

### What's New

- Support for Lefthook hooks alongside pre-commit

### Improvements

- Better compatibility with Python 3.14
- Updated development setup with unified formatting tools
- Enhanced documentation for contributors

### Bug Fixes

- Fixed Synthetic provider model name handling

## [1.6.0] - 2025-10-22

### What's New

- Generate commit messages using Synthetic AI provider

### Improvements

- Added support for Python 3.14
- Better error handling when AI services are busy or unavailable
- More precise error messages for authentication and timeout issues

## [1.5.2] - 2025-10-10

### What's New

- Add StreamLake AI provider for commit message generation

### Improvements

- Better error message when GAC isn't initialized
- Enhanced Ollama and LM Studio setup with API key support
- Cleaned up and improved developer documentation

### Bug Fixes

- Fixed configuration initialization guidance for new users

## [1.5.1] - 2025-10-10

### Improvements

- Updated Gemini AI provider with improved API compatibility
- Enhanced error handling and response validation for Gemini
- Better error messages for easier debugging

## [1.5.0] - 2025-10-10

### What's New

- Generate commit messages using Google's Gemini AI
- Use LM Studio as an AI provider for local processing

### Improvements

- Simplified Gemini setup with automatic configuration
- Enhanced error handling for all AI providers
- Added API key support for Ollama provider

### Bug Fixes

- Fixed empty response handling across all AI providers

## [1.4.2] - 2025-10-09

### Improvements

- Simplified commit message scope handling for more reliable generation
- Updated documentation to include Ollama AI provider
- Corrected version information for v1.4.1 release

## [1.4.1] - 2025-10-04

### Improvements

- Updated Z.AI provider support with streamlined configuration
- Cleaner changelog documentation for version 1.4.0 release

## [1.4.0] - 2025-10-04

### Improvements

- New Z.AI Coding provider option for commit message generation
- Simplified Z.AI provider configuration with shared API implementation
- Better support for Z.AI coding API without environment variables

## [1.3.1] - 2025-10-03

### Improvements

- Added support for Z.AI provider for commit message generation
- Updated changelog with comprehensive release history

## [1.3.0] - 2025-10-03

### What's New

- AI-powered secret detection scans your code before committing
- New Z.AI coding API endpoint support for better code generation

### Improvements

- Better secret detection with fewer false positives
- Enhanced error handling for rate limits and service issues
- Improved warning messages and user choices
- Better display formatting throughout the app

### Bug Fixes

- Fixed OpenAI token limit handling for large code changes
- Fixed crash issues when testing with outdated models

## [1.2.6] - 2025-10-01

### Improvements

- Better organized test suite for improved reliability
- Enhanced test coverage with more comprehensive testing
- Updated to version 1.2.6 with latest improvements

## [1.2.5] - 2025-10-01

### What's New

- New Z.AI provider option for generating commit messages

### Improvements

- Updated list of supported AI providers in documentation

## [1.2.4] - 2025-09-29

### What's New

- Enhanced testing for all AI providers to ensure more reliable commit message generation

### Improvements

- Better testing coverage for AI provider integrations
- Updated development documentation with clearer testing guidelines

## [1.2.3] - 2025-09-28

### Improvements

- Updated to version 1.2.3 with latest improvements and fixes

### Bug Fixes

- Fixed OpenAI token limit handling to prevent errors when processing large changes

## [1.2.2] - 2025-09-28

### Improvements

- Simplified OpenRouter AI provider configuration by removing optional site settings
- Updated documentation to reflect cleaner configuration options

## [1.2.1] - 2025-09-28

### Improvements

- More reliable AI message generation with better error handling
- Improved token counting accuracy for all AI providers
- Better error messages when AI operations fail
- Enhanced logging for easier troubleshooting

## [1.2.0] - 2025-09-28

### Improvements

- More reliable AI connections with better retry handling
- Cleaner and more consistent AI provider responses

## [1.1.0] - 2025-09-27

### What's New

- Added OpenRouter provider support for commit message generation

### Improvements

- Better organization with modular AI provider implementations
- More accurate token counting for Anthropic AI models
- Enhanced error handling with standardized error type classification

## [1.0.1] - 2025-09-26

### Improvements

- More accurate token counting for Anthropic AI models
- Better reliability when counting tokens with fallback estimation

## [1.0.0] - 2025-09-26

### Improvements

- More reliable AI connections with direct API calls
- Better error handling and retry logic for all AI providers
- Enhanced test coverage for AI provider interactions

## [0.19.1] - 2025-09-22

### Improvements

- Upgraded AI providers and core components for better performance and reliability
- Enhanced data validation and CLI formatting with updated dependencies

## [0.19.0] - 2025-09-21

### Improvements

- Simplified scope flag to now automatically infer scope from your changes
- Updated build system with modern tools for better consistency
- Improved documentation to reflect new automatic scope behavior

## [0.18.1] - 2025-09-21

### Improvements

- Streamlined development tools with unified formatting system
- Added advanced usage screenshot to documentation
- Better code quality checks with modern linting tools

## [0.18.0] - 2025-09-15

### Improvements

- More accurate token counting for Anthropic AI models
- Updated to version 0.18.0 with latest improvements and fixes

## [0.17.7] - 2025-09-15

### Improvements

- More accurate token counting for Anthropic AI models

## [0.17.6] - 2025-09-15

### Improvements

- More accurate token counting for Anthropic AI models

## [0.17.5] - 2025-09-14

### Improvements

- More accurate commit message generation with improved AI prompt structure
- Better testing across multiple Python versions for improved reliability
- Modernized build system with safer version management

## [0.17.4] - 2025-09-14

### Improvements

- Better organization for AI prompts with separate system and user components
- Improved CI testing with separate lint and test jobs
- More reliable version management with modern configuration format
- Enhanced version bump safety with better error checking

## [0.17.3] - 2025-09-14

### Improvements

- Better control over releases with tag-based publishing system
- Enhanced version management and release workflow

### Bug Fixes

- Fixed push failure reporting when using -p flag
- Improved error messages when git operations fail

## [0.17.0] - 2025-09-14

### What's New

- New setting to automatically include scope in commit messages
- Provide feedback when regenerating commit messages with 'r \<feedback\>'

### Improvements

- Better documentation for interactive reroll feature
- More reliable version bump detection during releases

## [0.16.3] - 2025-09-14

### What's New

- Better commit message generation with improved focus and scope guidance

### Improvements

- Enhanced test coverage for git operations and file staging
- Improved subprocess error handling and logging reliability

### Bug Fixes

- Fixed documentation commit type detection to prioritize code changes
- Better error messages when pre-commit hooks fail
- Resolved issues with project configuration file loading

## [0.16.2] - 2025-09-14

### Improvements

- Better version management to prevent conflicts during updates
- More reliable release process with automatic version syncing

## [0.16.1] - 2025-09-14

### Improvements

- Updated to version 0.16.1 with latest improvements and fixes

## [0.16.0] - 2025-09-14

### What's New

- Added support for Cerebras AI provider with qwen-3-coder-480b model
- New project-specific configuration using .gac.env files

### Improvements

- Better configuration loading order: user settings, then project settings, then environment variables
- Updated Groq default model to llama-4-maverick-17b-128e-instruct
- Simplified token counting for Anthropic models for better performance

### Bug Fixes

- Fixed error message display when AI operations fail
- Fixed issue where project configuration files weren't being loaded correctly

## [0.15.4] - 2025-09-14

### What's New

- Try gac without installing using uvx for quick testing

### Improvements

- Simplified installation with direct pipx command
- Better README organization with clearer installation instructions
- Updated project badges for improved visual presentation

### Bug Fixes

- Fixed build configuration to include all source files in the package

## [0.15.1] - 2025-09-14

### Improvements

- Updated to version 0.15.1 with latest improvements and fixes

## [0.15.0] - 2025-09-14

### What's New

- Automated releases to PyPI when pushing to main branch

### Improvements

- Better and faster code quality checks with modern tools
- More reliable version management for cleaner releases
- Simplified repository structure with cleaner URLs
- Improved test coverage and faster test execution
- Better file staging logic for more reliable commits

### Bug Fixes

- Fixed CI failures during package publishing
- Resolved version number issues that PyPI rejected
- Fixed test mocks after code cleanup

## [0.14.7] - 2025-06-07

### Improvements

- Commit messages now include a summary of file changes for better context
- Simplified and improved the way commit messages are generated
- Updated documentation to better describe current features and removed outdated information

## [0.14.6] - 2025-06-06

### What's New

- Automatic pre-commit hook checks before committing changes

### Improvements

- Better error messages when pre-commit hooks fail
- Enhanced test coverage and reliability

### Bug Fixes

- Graceful handling when pre-commit is not installed

## [0.14.5] - 2025-06-06

### Improvements

- Better handling of empty lines in prompts
- Added --no-verify flag documentation to usage guide

## [0.14.4] - 2025-06-02

### What's New

- Add pre-commit hook to check if your branch is behind the remote
- Skip pre-commit hooks with new --no-verify flag

### Improvements

- Updated documentation for better clarity and consistency
- Removed unused code to simplify the application

## [0.14.3] - 2025-05-30

### What's New

- You can now regenerate commit messages by typing 'r' or 'reroll' when asked to confirm
- See token usage estimates for AI-generated commit messages
- Warning when your changes are too large for AI processing

### Improvements

- Better commit message generation with more varied AI responses
- Improved token usage tracking and display
- Increased limit for processing larger code changes
- Enhanced documentation with clearer setup and usage instructions

## [0.14.2] - 2025-05-30

### What's New

- See estimated token usage for AI-generated commit messages
- Warning when your changes are too large for AI processing

### Improvements

- Increased limit for processing larger code changes
- Cleaner code comments for better maintenance

## [0.14.1] - 2025-05-27

### Improvements

- Cleaner documentation structure by removing redundant files
- Better commit message formatting with improved processing
- More efficient prompt generation with streamlined context
- Updated documentation with clearer installation and usage instructions

## [0.14.0] - 2025-05-27

### Improvements

- Simplified by removing code formatting, backup model, and preview features
- Removed Mistral AI provider and added OpenRouter support
- Cleaned up project structure and removed unnecessary dependencies

### Bug Fixes

- Fixed inconsistent naming by changing GAC to gac throughout the app

## [0.13.1] - 2025-05-26

### Improvements

- Binary files, lockfiles, and minified files now show helpful summaries instead of being hidden
- Added Contributor License Agreement for better project collaboration

## [0.13.0] - 2025-05-25

### What's New

- New diff command to view staged and unstaged changes
- Add --scope flag to better organize your commit messages

### Improvements

- Better organized command line options for easier use
- More informative documentation with updated examples and guides

## [0.12.0] - 2025-05-07

### What's New

- Preview your commit messages before committing with the new preview command

### Improvements

- Better organized documentation in a dedicated docs directory
- Updated installation instructions for easier setup

### Bug Fixes

- Fixed documentation links to point to correct locations
- Improved error handling for preview functionality

## [0.11.0] - 2025-04-18

### What's New

- New interactive setup command to guide you through initial configuration

### Improvements

- Simplified project by removing unused version management tool
- Enhanced documentation with clearer setup and troubleshooting guides

## [0.10.0] - 2025-04-18

### What's New

- New config commands for managing settings
- Dedicated configuration management system

### Improvements

- Better organization with unified command structure
- Enhanced configuration with user-level settings support

## [0.9.3] - 2025-04-17

### Improvements

- Faster and cleaner system checks with improved workflow
- Updated project roadmap for better visibility into future plans

## [0.9.2] - 2025-04-17

### What's New

- Better support for Windows users

### Improvements

- Improved documentation with clearer setup instructions
- Enhanced error handling and logging
- Better version display when checking updates

## [0.9.1] - 2025-04-17

### Improvements

- Improved code organization for better maintainability

## [0.9.0] - 2025-04-17

### Improvements

- Enhanced configuration management with environment file support
- Better logging options with quiet mode and customizable levels
- Improved documentation with clearer setup instructions and examples

## [0.8.0] - 2025-04-14

### Improvements

- Better code organization and cleaner internal structure
- Improved documentation with comprehensive guides and troubleshooting
- More informative feedback during dry runs and push operations

### Bug Fixes

- Fixed issue with worker count calculation for better performance
- Clearer success messages when pushing changes

## [0.7.5] - 2025-04-14

### What's New

- See your commit message in a cleaner, more readable format before confirming

### Improvements

- Dry run mode now shows more details about what will be committed
- Better handling when no files have changes staged or ready to commit

### Bug Fixes

- Fixed crashes when trying to commit without any file changes

## [0.7.4] - 2025-04-13

### Improvements

- More accurate code coverage tracking
- Faster testing with parallel execution
- Simplified version management process

## [0.7.3] - 2025-04-13

### Improvements

- Better error messages with more helpful context
- Consistent logging throughout the app for clearer output
- Simplified version management behind the scenes

## [0.7.2] - 2025-04-13

### Improvements

- Better verification to ensure all changes are committed properly
- Cleaner and more reliable error handling throughout the app
- Simplified template handling for generating commit messages
- More robust configuration loading with better defaults
- Improved handling of AI-generated commit messages

### Bug Fixes

- Fixed issue with incomplete commits when files remained staged
- Removed redundant configuration files to prevent confusion

## [0.7.1] - 2025-04-07

### Improvements

- Better configuration management with cleaner settings and improved error handling
- Enhanced documentation with updated installation guide and clearer setup instructions
- Improved code quality with better test coverage and simplified test structure

### Bug Fixes

- Fixed crashes when checking git repositories
- Removed references to non-existent config wizard to prevent errors

## [0.7.0] - 2025-04-06

### What's New

- Add support for Ollama AI provider
- New environment file configuration with multiple location support

### Improvements

- Better error handling throughout the application
- Simplified AI model configuration with manual input
- Enhanced configuration wizard with save location options
- Improved remote push validation and status reporting
- Cleaner code structure with consolidated AI functionality

### Bug Fixes

- Fixed staging issues during dry run mode
- Resolved crashes when checking git repositories
- Fixed false positives in remote push status

## [0.6.1] - 2025-04-04

### What's New

- Check the current version with --version flag
- Persistent configuration saved to home directory
- Optional --format flag for explicit file formatting

### Improvements

- Better diff truncation that preserves important context
- Simplified command line options with clearer naming
- Enhanced configuration wizard with environment file support
- Improved performance with optimized token counting
- Cleaner output formatting and message display

### Bug Fixes

- Fixed config wizard error when saving settings
- Resolved test failures with missing API keys
- Fixed CLI flag conflicts between format options

## [0.5.0] - 2025-04-01

### Improvements

- Simplified command structure with unified interface
- Better visual feedback with improved spinner and message formatting
- More reliable file staging and commit handling
- Cleaner error messages and logging output

### Bug Fixes

- Fixed missing dependency that prevented installation
- Resolved issues with prompt template loading
- Fixed crashes when working with empty repositories

## [0.4.3] - 2025-03-30

### What's New

- Code formatting now supports JavaScript, TypeScript, Markdown, HTML, CSS, JSON, YAML, Rust, and Go files

### Improvements

- Better simulation and test mode with clear ALL-CAPS labeling
- Improved file detection and formatting system for all supported file types

## [0.4.2] - 2025-03-30

### What's New

- Added support for different AI model token counting methods

### Improvements

- Better handling of large files when processing changes
- More accurate token counting for different AI models
- Enhanced error handling and validation for settings
- Improved subprocess reliability for git operations

### Bug Fixes

- Fixed issues with token limit validation
- Resolved git stash pop errors
- Fixed formatting logic to handle files correctly

## [0.4.1] - 2025-03-29

### Improvements

- Updated release process for more reliable updates

## [0.4.0] - 2025-03-29

### What's New

- Add extra context like JIRA ticket numbers to commit messages
- Better test mode with real file changes and simulation options

### Improvements

- Better detection of staged files including deleted and renamed
- Cleaner error messages when settings are invalid
- Improved code formatting process
- More reliable git operations

### Bug Fixes

- Fixed token limit validation error handling
- Removed extra colons from commit prompts
- Fixed staging issues with certain file types

## [0.3.0] - 2025-03-26

### What's New

- Control logging with quiet and verbose options
- Override AI model settings for single commands
- Added safety checks before releasing new versions

### Improvements

- Updated minimum Python version to 3.10 for better performance
- Simplified model configuration to use single setting
- Better code quality and test coverage tracking

### Bug Fixes

- Fixed model configuration handling when provider is specified
- Improved reliability of git operations

## [0.2.0] - 2025-03-25

### What's New

- Support for multiple AI providers including OpenAI, Groq, Mistral, AWS, Azure and Google

### Improvements

- Added automatic testing and code quality checks
- Better file handling after code formatting
- More flexible configuration options

### Bug Fixes

- Fixed issue with re-staging files after Python formatting
- Corrected output formatting alignment

## [0.1.0a1] - 2024-12-12

### Improvements

- Simplified command output with clearer logging
- Better reliability when running git operations
- Streamlined internal code for cleaner performance

### Bug Fixes

- Fixed issues with command return values

## [0.1.0] - 2025-03-24

### Improvements

- Better control over logging with new verbose and quiet options
- Improved error messages when operations fail
- Cleaner and more readable output formatting
