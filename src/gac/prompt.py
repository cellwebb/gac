# flake8: noqa: E501
"""Prompt creation for gac.

This module handles the creation of prompts for AI models, including template loading,
formatting, and integration with diff preprocessing.
"""

import logging
import re

from gac.constants import CommitMessageConstants

logger = logging.getLogger(__name__)


# ============================================================================
# Prompt Templates
# ============================================================================

DEFAULT_SYSTEM_TEMPLATE = """<role>
You are an expert git commit message generator. Your task is to analyze code changes and create a concise, meaningful git commit message. You will receive git status and diff information. Your entire response will be used directly as a git commit message.
</role>

<focus>
Your commit message must reflect the core purpose and impact of these changes.
Prioritize the primary intent over implementation details.
Consider what future developers need to understand about this change.
Identify if this introduces new capabilities, fixes problems, or improves existing code.
</focus>

<mixed_changes>
When changes span multiple areas:
- Choose the commit type based on the PRIMARY purpose, not the largest file count
- Feature additions with supporting tests/docs should use 'feat'
- Bug fixes with added tests should use 'fix'
- Refactoring that improves multiple components should use 'refactor'
- Documentation updates are 'docs' only when that's the sole purpose
</mixed_changes>

<format>
  <one_liner>
  Create a single-line commit message.
  Your message should be clear, concise, and descriptive of the core change.
  Use present tense ("Add feature" not "Added feature").
  </one_liner><multi_line>
  Create a commit message with:
  - First line: A concise summary that could stand alone
  - Blank line after the summary
  - Detailed body with multiple bullet points explaining the key changes
  - Focus on WHY changes were made, not just WHAT was changed
  - Order points from most important to least important
  </multi_line><verbose>
  IMPORTANT: You MUST create a MULTI-PARAGRAPH commit message with detailed sections.
  DO NOT create a single-line commit message.

  Your commit message MUST follow this structure:

  Line 1: A concise summary (that could stand alone) with conventional commit prefix
  Line 2: BLANK LINE (required)
  Lines 3+: Detailed multi-paragraph body with the following sections:

  ## Motivation
  Explain why this commit exists in 2-3 sentences. What problem does it solve? What need does it address?

  ## Architecture / Approach
  Describe how it was implemented in 2-4 sentences. Include key design decisions and any rejected alternatives.
  Reference specific modules, functions, or classes when relevant.

  ## Affected Components
  List the main modules, subsystems, or directories impacted by this change.

  OPTIONAL sections (include only if relevant):

  ## Performance / Security Impact
  Describe any performance improvements, trade-offs, or security considerations.
  Include concrete data such as benchmark results if available.

  ## Compatibility / Testing
  Mention any compatibility considerations, known limitations, testing performed, or next steps for validation.

  REQUIREMENTS:
  - Your response MUST be at least 10 lines long with multiple paragraphs
  - Use active voice and present tense ("Implements", "Adds", "Refactors")
  - Provide concrete, specific information rather than vague descriptions
  - Keep the tone professional and technical
  - Focus on intent and reasoning, not just code changes
  - Use markdown headers (##) for section organization
  </verbose>
</format>

<conventions_no_scope>
You MUST start your commit message with the most appropriate conventional commit prefix.

IMPORTANT: Check file types FIRST when determining the commit type:
- If changes are ONLY to documentation files (*.md, *.rst, *.txt in docs/, README*, CHANGELOG*, etc.), ALWAYS use 'docs:'
- Use 'docs:' ONLY when ALL changes are documentation files - INCLUDING README updates, regardless of how significant the changes are
- If changes include both documentation and code, use the prefix for the code changes, unless it is a documentation-only change

Commit type prefixes:
- feat: A new feature or functionality addition
- fix: A bug fix or error correction
- docs: Documentation changes only (INCLUDING README updates, regardless of how significant)
- style: Changes to code style/formatting without logic changes
- refactor: Code restructuring without behavior changes
- perf: Performance improvements
- test: Adding/modifying tests
- build: Changes to build system/dependencies
- ci: Changes to CI configuration
- chore: Miscellaneous changes not affecting src/test files

Select ONE prefix that best matches the primary purpose of the changes.
If multiple prefixes apply, choose the one that represents the most significant change.
If you cannot confidently determine a type, use 'chore'.

Do NOT include a scope in your commit prefix.
</conventions_no_scope>

<conventions_with_scope>
You MUST write a conventional commit message with EXACTLY ONE type and an inferred scope.

FORMAT: type(scope): description

IMPORTANT: Check file types FIRST when determining the commit type:
- If changes are ONLY to documentation files (*.md, *.rst, *.txt in docs/, README*, CHANGELOG*, etc.), ALWAYS use 'docs'
- If changes include both documentation and code, use the prefix for the code changes, unless it is a documentation-only change

Select ONE type from this list that best matches the primary purpose of the changes:
- feat: A new feature or functionality addition
- fix: A bug fix or error correction
- docs: Documentation changes only (INCLUDING README and CHANGELOG updates, regardless of how significant)
- style: Changes to code style/formatting without logic changes
- refactor: Code restructuring without behavior changes
- perf: Performance improvements
- test: Adding/modifying tests
- build: Changes to build system/dependencies
- ci: Changes to CI configuration
- chore: Miscellaneous changes not affecting src/test files

You MUST infer an appropriate scope from the changes. A good scope is concise (usually one word) and indicates the component or area that was changed.

<scope_rules>
For scope inference, select the most specific component affected:
- Use module/component names from the codebase (auth, api, cli, core)
- Use functional areas for cross-cutting changes (config, build, test)
- Keep scopes consistent with existing commit history when possible
- Prefer established patterns over creating new scope names
- Use singular form (auth, not auths; test, not tests)
</scope_rules>

Examples of good scopes: api, auth, ui, core, docs, build, prompt, config

CORRECT EXAMPLES (these formats are correct):
✅ feat(auth): add login functionality
✅ fix(api): resolve null response issue
✅ refactor(core): improve data processing
✅ docs(readme): update installation instructions

INCORRECT EXAMPLES (these formats are wrong and must NOT be used):
❌ chore: feat(component): description
❌ fix: refactor(component): description
❌ feat: feat(component): description
❌ chore: chore(component): description

You MUST NOT prefix the type(scope) with another type. Use EXACTLY ONE type, which MUST include the scope in parentheses.
</conventions_with_scope>

<examples_no_scope>
Good commit messages (no scope):
[OK] feat: add OAuth2 integration with Google and GitHub
[OK] fix: resolve race condition in user session management
[OK] docs: add troubleshooting section for common installation issues
[OK] refactor: extract validation logic into reusable utilities
[OK] test: add comprehensive unit tests for token validation
[OK] build: upgrade to latest security patches

Bad commit messages:
[ERROR] fix stuff
[ERROR] update code
[ERROR] feat(auth): add login (scope included when not requested)
[ERROR] WIP: still working on this
[ERROR] Fixed bug
[ERROR] Changes
</examples_no_scope>

<examples_verbose_no_scope>
Example of a good VERBOSE commit message (without scope):

feat: add verbose mode for detailed commit message generation

## Motivation
Users need the ability to generate comprehensive commit messages that follow best practices for code review and documentation. The existing one-liner and multi-line modes don't provide sufficient structure for complex changes that require detailed explanations of motivation, architecture decisions, and impact.

## Architecture / Approach
Adds a new --verbose/-v flag to the CLI that modifies the prompt generation in build_prompt(). When enabled, the prompt instructs the AI to generate commit messages with structured sections including Motivation, Architecture/Approach, Affected Components, and optional Performance/Testing sections. The implementation uses the existing format selection logic with verbose taking priority over one_liner and multi_line modes.

## Affected Components
- src/gac/cli.py: Added --verbose flag and parameter passing
- src/gac/main.py: Extended main() to accept and pass verbose parameter
- src/gac/prompt.py: Added <verbose> template section with detailed instructions
- tests/test_prompt.py: Added test coverage for verbose mode

## Compatibility / Testing
Added new test test_build_prompt_verbose_mode to verify the verbose template generation. All existing tests pass. The verbose mode is opt-in via the -v flag, maintaining backward compatibility.
</examples_verbose_no_scope>

<examples_verbose_with_scope>
Example of a good VERBOSE commit message (with scope):

feat(cli): add verbose mode for detailed commit message generation

## Motivation
Users need the ability to generate comprehensive commit messages that follow best practices for code review and documentation. The existing one-liner and multi-line modes don't provide sufficient structure for complex changes that require detailed explanations of motivation, architecture decisions, and impact.

## Architecture / Approach
Adds a new --verbose/-v flag to the CLI that modifies the prompt generation in build_prompt(). When enabled, the prompt instructs the AI to generate commit messages with structured sections including Motivation, Architecture/Approach, Affected Components, and optional Performance/Testing sections. The implementation uses the existing format selection logic with verbose taking priority over one_liner and multi_line modes.

## Affected Components
- src/gac/cli.py: Added --verbose flag and parameter passing
- src/gac/main.py: Extended main() to accept and pass verbose parameter
- src/gac/prompt.py: Added <verbose> template section with detailed instructions
- tests/test_prompt.py: Added test coverage for verbose mode

## Compatibility / Testing
Added new test test_build_prompt_verbose_mode to verify the verbose template generation. All existing tests pass. The verbose mode is opt-in via the -v flag, maintaining backward compatibility.
</examples_verbose_with_scope>

<examples_with_scope>
Good commit message top lines (with scope):
[OK] feat(auth): add OAuth2 integration with Google and GitHub
[OK] fix(api): resolve race condition in user session management
[OK] docs(readme): add troubleshooting section for common installation issues
[OK] refactor(core): extract validation logic into reusable utilities
[OK] test(auth): add comprehensive unit tests for token validation
[OK] build(deps): upgrade to latest security patches

Bad commit messages:
[ERROR] fix stuff
[ERROR] update code
[ERROR] feat: fix(auth): add login (double prefix)
[ERROR] WIP: still working on this
[ERROR] Fixed bug
[ERROR] Changes
</examples_with_scope>"""

DEFAULT_USER_TEMPLATE = """<hint>
Additional context provided by the user: <hint_text></hint_text>
</hint>

<git_diff>
<diff></diff>
</git_diff>

<git_diff_stat>
<diff_stat></diff_stat>
</git_diff_stat>

<git_status>
<status></status>
</git_status>

<language_instructions>
IMPORTANT: You MUST write the entire commit message in <language_name></language_name>.
All text in the commit message, including the summary line and body, must be in <language_name></language_name>.
<prefix_instruction></prefix_instruction>
</language_instructions>

<format_instructions>
IMMEDIATELY AFTER ANALYZING THE CHANGES, RESPOND WITH ONLY THE COMMIT MESSAGE.
DO NOT include any preamble, reasoning, explanations or anything other than the commit message itself.
DO NOT use markdown formatting, headers, or code blocks.
The entire response will be passed directly to 'git commit -m'.
</format_instructions>"""


# ============================================================================
# Template Loading
# ============================================================================


def load_system_template(custom_path: str | None = None) -> str:
    """Load the system prompt template.

    Args:
        custom_path: Optional path to a custom system template file

    Returns:
        System template content as string
    """
    if custom_path:
        return load_custom_system_template(custom_path)

    logger.debug("Using default system template")
    return DEFAULT_SYSTEM_TEMPLATE


def load_user_template() -> str:
    """Load the user prompt template (contains git data sections and instructions).

    Returns:
        User template content as string
    """
    logger.debug("Using default user template")
    return DEFAULT_USER_TEMPLATE


def load_custom_system_template(path: str) -> str:
    """Load a custom system template from a file.

    Args:
        path: Path to the custom system template file

    Returns:
        Custom system template content

    Raises:
        FileNotFoundError: If the template file doesn't exist
        IOError: If there's an error reading the file
    """
    try:
        with open(path, encoding="utf-8") as f:
            content = f.read()
            logger.info(f"Loaded custom system template from {path}")
            return content
    except FileNotFoundError:
        logger.error(f"Custom system template not found: {path}")
        raise
    except OSError as e:
        logger.error(f"Error reading custom system template from {path}: {e}")
        raise


# ============================================================================
# Template Processing Helpers
# ============================================================================


def _remove_template_section(template: str, section_name: str) -> str:
    """Remove a tagged section from the template.

    Args:
        template: The template string
        section_name: Name of the section to remove (without < > brackets)

    Returns:
        Template with the section removed
    """
    pattern = f"<{section_name}>.*?</{section_name}>\\n?"
    return re.sub(pattern, "", template, flags=re.DOTALL)


def _select_conventions_section(template: str, infer_scope: bool) -> str:
    """Select and normalize the appropriate conventions section.

    Args:
        template: The template string
        infer_scope: Whether to infer scope for commits

    Returns:
        Template with the appropriate conventions section selected
    """
    try:
        logger.debug(f"Processing infer_scope parameter: {infer_scope}")
        if infer_scope:
            logger.debug("Using inferred-scope conventions")
            template = _remove_template_section(template, "conventions_no_scope")
            template = template.replace("<conventions_with_scope>", "<conventions>")
            template = template.replace("</conventions_with_scope>", "</conventions>")
        else:
            logger.debug("Using no-scope conventions")
            template = _remove_template_section(template, "conventions_with_scope")
            template = template.replace("<conventions_no_scope>", "<conventions>")
            template = template.replace("</conventions_no_scope>", "</conventions>")
    except Exception as e:
        logger.error(f"Error processing scope parameter: {e}")
        template = _remove_template_section(template, "conventions_with_scope")
        template = template.replace("<conventions_no_scope>", "<conventions>")
        template = template.replace("</conventions_no_scope>", "</conventions>")
    return template


def _select_format_section(template: str, verbose: bool, one_liner: bool) -> str:
    """Select the appropriate format section based on verbosity and one-liner settings.

    Priority: verbose > one_liner > multi_line

    Args:
        template: The template string
        verbose: Whether to use verbose format
        one_liner: Whether to use one-liner format

    Returns:
        Template with the appropriate format section selected
    """
    if verbose:
        template = _remove_template_section(template, "one_liner")
        template = _remove_template_section(template, "multi_line")
    elif one_liner:
        template = _remove_template_section(template, "multi_line")
        template = _remove_template_section(template, "verbose")
    else:
        template = _remove_template_section(template, "one_liner")
        template = _remove_template_section(template, "verbose")
    return template


def _select_examples_section(template: str, verbose: bool, infer_scope: bool) -> str:
    """Select the appropriate examples section based on verbosity and scope settings.

    Args:
        template: The template string
        verbose: Whether verbose mode is enabled
        infer_scope: Whether scope inference is enabled

    Returns:
        Template with the appropriate examples section selected
    """
    if verbose and infer_scope:
        template = _remove_template_section(template, "examples_no_scope")
        template = _remove_template_section(template, "examples_with_scope")
        template = _remove_template_section(template, "examples_verbose_no_scope")
        template = template.replace("<examples_verbose_with_scope>", "<examples>")
        template = template.replace("</examples_verbose_with_scope>", "</examples>")
    elif verbose:
        template = _remove_template_section(template, "examples_no_scope")
        template = _remove_template_section(template, "examples_with_scope")
        template = _remove_template_section(template, "examples_verbose_with_scope")
        template = template.replace("<examples_verbose_no_scope>", "<examples>")
        template = template.replace("</examples_verbose_no_scope>", "</examples>")
    elif infer_scope:
        template = _remove_template_section(template, "examples_no_scope")
        template = _remove_template_section(template, "examples_verbose_no_scope")
        template = _remove_template_section(template, "examples_verbose_with_scope")
        template = template.replace("<examples_with_scope>", "<examples>")
        template = template.replace("</examples_with_scope>", "</examples>")
    else:
        template = _remove_template_section(template, "examples_with_scope")
        template = _remove_template_section(template, "examples_verbose_no_scope")
        template = _remove_template_section(template, "examples_verbose_with_scope")
        template = template.replace("<examples_no_scope>", "<examples>")
        template = template.replace("</examples_no_scope>", "</examples>")
    return template


# ============================================================================
# Prompt Building
# ============================================================================


def build_prompt(
    status: str,
    processed_diff: str,
    diff_stat: str = "",
    one_liner: bool = False,
    infer_scope: bool = False,
    hint: str = "",
    verbose: bool = False,
    system_template_path: str | None = None,
    language: str | None = None,
    translate_prefixes: bool = False,
) -> tuple[str, str]:
    """Build system and user prompts for the AI model using the provided templates and git information.

    Args:
        status: Git status output
        processed_diff: Git diff output, already preprocessed and ready to use
        diff_stat: Git diff stat output showing file changes summary
        one_liner: Whether to request a one-line commit message
        infer_scope: Whether to infer scope for the commit message
        hint: Optional hint to guide the AI
        verbose: Whether to generate detailed commit messages with motivation, architecture, and impact sections
        system_template_path: Optional path to custom system template
        language: Optional language for commit messages (e.g., "Spanish", "French", "Japanese")
        translate_prefixes: Whether to translate conventional commit prefixes (default: False keeps them in English)

    Returns:
        Tuple of (system_prompt, user_prompt) ready to be sent to an AI model
    """
    system_template = load_system_template(system_template_path)
    user_template = load_user_template()

    system_template = _select_conventions_section(system_template, infer_scope)
    system_template = _select_format_section(system_template, verbose, one_liner)
    system_template = _select_examples_section(system_template, verbose, infer_scope)
    system_template = re.sub(r"\n(?:[ \t]*\n){2,}", "\n\n", system_template)

    user_template = user_template.replace("<status></status>", status)
    user_template = user_template.replace("<diff_stat></diff_stat>", diff_stat)
    user_template = user_template.replace("<diff></diff>", processed_diff)

    if hint:
        user_template = user_template.replace("<hint_text></hint_text>", hint)
        logger.debug(f"Added hint ({len(hint)} characters)")
    else:
        user_template = _remove_template_section(user_template, "hint")
        logger.debug("No hint provided")

    if language:
        user_template = user_template.replace("<language_name></language_name>", language)

        # Set prefix instruction based on translate_prefixes setting
        if translate_prefixes:
            prefix_instruction = f"""CRITICAL: You MUST translate the conventional commit prefix into {language}.
DO NOT use English prefixes like 'feat:', 'fix:', 'docs:', etc.
Instead, translate them into {language} equivalents.
Examples:
- 'feat:' → translate to {language} word for 'feature' or 'add'
- 'fix:' → translate to {language} word for 'fix' or 'correct'
- 'docs:' → translate to {language} word for 'documentation'
The ENTIRE commit message, including the prefix, must be in {language}."""
            logger.debug(f"Set commit message language to: {language} (with prefix translation)")
        else:
            prefix_instruction = (
                "The conventional commit prefix (feat:, fix:, etc.) should remain in English, but everything after the prefix must be in "
                + language
                + "."
            )
            logger.debug(f"Set commit message language to: {language} (English prefixes)")

        user_template = user_template.replace("<prefix_instruction></prefix_instruction>", prefix_instruction)
    else:
        user_template = _remove_template_section(user_template, "language_instructions")
        logger.debug("Using default language (English)")

    user_template = re.sub(r"\n(?:[ \t]*\n){2,}", "\n\n", user_template)

    return system_template.strip(), user_template.strip()


def build_group_prompt(
    status: str,
    processed_diff: str,
    diff_stat: str,
    one_liner: bool,
    hint: str,
    infer_scope: bool,
    verbose: bool,
    system_template_path: str | None,
    language: str | None,
    translate_prefixes: bool,
) -> tuple[str, str]:
    """Build prompt for grouped commit generation (JSON output with multiple commits)."""
    system_prompt, user_prompt = build_prompt(
        status=status,
        processed_diff=processed_diff,
        diff_stat=diff_stat,
        one_liner=one_liner,
        hint=hint,
        infer_scope=infer_scope,
        verbose=verbose,
        system_template_path=system_template_path,
        language=language,
        translate_prefixes=translate_prefixes,
    )

    user_prompt = _remove_template_section(user_prompt, "format_instructions")

    grouping_instructions = """
<format_instructions>
Your task is to split the changed files into separate, logical commits. Think of this like sorting files into different folders where each file belongs in exactly one folder.

CRITICAL REQUIREMENT - Every File Used Exactly Once:
You must assign EVERY file from the diff to exactly ONE commit.
- NO file should be left out
- NO file should appear in multiple commits
- EVERY file must be used once and ONLY once

Think of it like dealing cards: Once you've dealt a card to a player, that card cannot be dealt to another player.

HOW TO SPLIT THE FILES:
1. Review all changed files in the diff
2. Group files by logical relationship (e.g., related features, bug fixes, documentation)
3. Assign each file to exactly one commit based on what makes the most sense
4. If a file could fit in multiple commits, pick the best fit and move on - do NOT duplicate it
5. Continue until every single file has been assigned to a commit

ORDERING:
Order the commits in a logical sequence considering dependencies, natural progression, and overall workflow.

YOUR RESPONSE FORMAT:
Respond with valid JSON following this structure:
```json
{
  "commits": [
    {
      "files": ["src/auth/login.ts", "src/auth/logout.ts"],
      "message": "<commit_message_conforming_to_prescribed_structure_and_format>"
    },
    {
      "files": ["src/db/schema.sql", "src/db/migrations/001.sql"],
      "message": "<commit_message_conforming_to_prescribed_structure_and_format>"
    },
    {
      "files": ["tests/auth.test.ts", "tests/db.test.ts", "README.md"],
      "message": "<commit_message_conforming_to_prescribed_structure_and_format>"
    }
  ]
}
```

☝️ Notice how EVERY file path in the example above appears exactly ONCE across all commits. "src/auth/login.ts" appears once. "tests/auth.test.ts" appears once. No file is repeated.

VALIDATION CHECKLIST - Before responding, verify:
□ Total files across all commits = Total files in the diff
□ Each file appears in exactly 1 commit (no duplicates, no omissions)
□ Every commit has at least one file
□ If you list all files from all commits and count them, you get the same count as unique files in the diff
</format_instructions>
"""

    user_prompt = user_prompt + grouping_instructions

    return system_prompt, user_prompt


# ============================================================================
# Message Cleaning Helpers
# ============================================================================


def _remove_think_tags(message: str) -> str:
    """Remove AI reasoning <think> tags and their content from the message.

    Args:
        message: The message to clean

    Returns:
        Message with <think> tags removed
    """
    while re.search(r"<think>(?:(?!</think>)[^\n])*\n.*?</think>", message, flags=re.DOTALL | re.IGNORECASE):
        message = re.sub(
            r"<think>(?:(?!</think>)[^\n])*\n.*?</think>\s*", "", message, flags=re.DOTALL | re.IGNORECASE, count=1
        )

    message = re.sub(r"\n\n+\s*<think>.*?</think>\s*", "", message, flags=re.DOTALL | re.IGNORECASE)
    message = re.sub(r"<think>.*?</think>\s*\n\n+", "", message, flags=re.DOTALL | re.IGNORECASE)

    message = re.sub(r"<think>\s*\n.*$", "", message, flags=re.DOTALL | re.IGNORECASE)

    conventional_prefixes_pattern = r"(" + "|".join(CommitMessageConstants.CONVENTIONAL_PREFIXES) + r")[\(:)]"
    if re.search(r"^.*?</think>", message, flags=re.DOTALL | re.IGNORECASE):
        prefix_match = re.search(conventional_prefixes_pattern, message, flags=re.IGNORECASE)
        think_match = re.search(r"</think>", message, flags=re.IGNORECASE)

        if not prefix_match or (think_match and think_match.start() < prefix_match.start()):
            message = re.sub(r"^.*?</think>\s*", "", message, flags=re.DOTALL | re.IGNORECASE)

    message = re.sub(r"</think>\s*$", "", message, flags=re.IGNORECASE)

    return message


def _remove_code_blocks(message: str) -> str:
    """Remove markdown code blocks from the message.

    Args:
        message: The message to clean

    Returns:
        Message with code blocks removed
    """
    return re.sub(r"```[\w]*\n|```", "", message)


def _extract_commit_from_reasoning(message: str) -> str:
    """Extract the actual commit message from reasoning/preamble text.

    Args:
        message: The message potentially containing reasoning

    Returns:
        Extracted commit message
    """
    for indicator in CommitMessageConstants.COMMIT_INDICATORS:
        if indicator.lower() in message.lower():
            message = message.split(indicator, 1)[1].strip()
            break

    lines = message.split("\n")
    for i, line in enumerate(lines):
        if any(line.strip().startswith(f"{prefix}:") for prefix in CommitMessageConstants.CONVENTIONAL_PREFIXES):
            message = "\n".join(lines[i:])
            break

    return message


def _remove_xml_tags(message: str) -> str:
    """Remove XML tags that might have leaked into the message.

    Args:
        message: The message to clean

    Returns:
        Message with XML tags removed
    """
    for tag in CommitMessageConstants.XML_TAGS_TO_REMOVE:
        message = message.replace(tag, "")
    return message


def _fix_double_prefix(message: str) -> str:
    """Fix double type prefix issues like 'chore: feat(scope):' to 'feat(scope):'.

    Args:
        message: The message to fix

    Returns:
        Message with double prefix corrected
    """
    double_prefix_pattern = re.compile(
        r"^("
        + r"|\s*".join(CommitMessageConstants.CONVENTIONAL_PREFIXES)
        + r"):\s*("
        + r"|\s*".join(CommitMessageConstants.CONVENTIONAL_PREFIXES)
        + r")\(([^)]+)\):"
    )
    match = double_prefix_pattern.match(message)

    if match:
        second_type = match.group(2)
        scope = match.group(3)
        description = message[match.end() :].strip()
        message = f"{second_type}({scope}): {description}"

    return message


def _ensure_conventional_prefix(message: str) -> str:
    """Ensure the message starts with a conventional commit prefix.

    Args:
        message: The message to check

    Returns:
        Message with conventional prefix ensured
    """
    if not any(
        message.strip().startswith(prefix + ":") or message.strip().startswith(prefix + "(")
        for prefix in CommitMessageConstants.CONVENTIONAL_PREFIXES
    ):
        message = f"chore: {message.strip()}"
    return message


def _normalize_whitespace(message: str) -> str:
    """Normalize whitespace, ensuring no more than one blank line between paragraphs.

    Args:
        message: The message to normalize

    Returns:
        Message with normalized whitespace
    """
    return re.sub(r"\n(?:[ \t]*\n){2,}", "\n\n", message).strip()


# ============================================================================
# Message Cleaning
# ============================================================================


def clean_commit_message(message: str) -> str:
    """Clean up a commit message generated by an AI model.

    This function:
    1. Removes any preamble or reasoning text
    2. Removes code block markers and formatting
    3. Removes XML tags that might have leaked into the response
    4. Fixes double type prefix issues (e.g., "chore: feat(scope):")
    5. Normalizes whitespace

    Args:
        message: Raw commit message from AI

    Returns:
        Cleaned commit message ready for use
    """
    message = message.strip()
    message = _remove_think_tags(message)
    message = _remove_code_blocks(message)
    message = _extract_commit_from_reasoning(message)
    message = _remove_xml_tags(message)
    message = _fix_double_prefix(message)
    message = _normalize_whitespace(message)
    return message
