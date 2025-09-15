# flake8: noqa: E501
"""Prompt creation for gac.

This module handles the creation of prompts for AI models, including template loading,
formatting, and integration with diff preprocessing.
"""

import logging
import re

logger = logging.getLogger(__name__)

# Default template to use when no template file is found
DEFAULT_TEMPLATE = """<role>
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
  Create a single-line commit message (50-72 characters if possible).
  Your message should be clear, concise, and descriptive of the core change.
  Use present tense ("Add feature" not "Added feature").
  </one_liner><multi_line>
  Create a commit message with:
  - First line: A concise summary (50-72 characters) that could stand alone
  - Blank line after the summary
  - Detailed body with multiple bullet points explaining the key changes
  - Focus on WHY changes were made, not just WHAT was changed
  - Order points from most important to least important
  </multi_line>
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

<conventions_scope_provided>
You MUST write a conventional commit message with EXACTLY ONE type and the REQUIRED scope '{scope}'.

FORMAT: type({scope}): description

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

CORRECT EXAMPLES (these formats are correct):
✅ feat({scope}): add new feature
✅ fix({scope}): resolve bug
✅ refactor({scope}): improve code structure
✅ chore({scope}): update dependencies

INCORRECT EXAMPLES (these formats are wrong and must NOT be used):
❌ chore: feat({scope}): description
❌ fix: refactor({scope}): description
❌ feat: feat({scope}): description
❌ chore: chore({scope}): description

You MUST NOT prefix the type({scope}) with another type. Use EXACTLY ONE type, which MUST include the scope in parentheses.
</conventions_scope_provided>

<conventions_scope_inferred>
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
</conventions_scope_inferred>

<hint>
Additional context provided by the user: <hint_text></hint_text>
</hint>

<git_status>
<status></status>
</git_status>

<git_diff_stat>
<diff_stat></diff_stat>
</git_diff_stat>

<git_diff>
<diff></diff>
</git_diff>



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

<examples_with_scope>
Good commit messages (with scope):
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
</examples_with_scope>

<instructions>
IMMEDIATELY AFTER ANALYZING THE CHANGES, RESPOND WITH ONLY THE COMMIT MESSAGE.
DO NOT include any preamble, reasoning, explanations or anything other than the commit message itself.
DO NOT use markdown formatting, headers, or code blocks.
The entire response will be passed directly to 'git commit -m'.
</instructions>"""


def load_prompt_template() -> str:
    """Load the prompt template from the embedded default template.

    Returns:
        Template content as string
    """
    logger.debug("Using default template")
    return DEFAULT_TEMPLATE


def build_prompt(
    status: str,
    processed_diff: str,
    diff_stat: str = "",
    one_liner: bool = False,
    hint: str = "",
    scope: str | None = None,
) -> tuple[str, str]:
    """Build system and user prompts for the AI model using the provided template and git information.

    Args:
        status: Git status output
        processed_diff: Git diff output, already preprocessed and ready to use
        diff_stat: Git diff stat output showing file changes summary
        one_liner: Whether to request a one-line commit message
        hint: Optional hint to guide the AI
        scope: Optional scope parameter. None = no scope, "infer" = infer scope, any other string = use as scope

    Returns:
        Tuple of (system_prompt, user_prompt) ready to be sent to an AI model
    """
    template = load_prompt_template()

    # Select the appropriate conventions section based on scope parameter
    try:
        logger.debug(f"Processing scope parameter: {scope}")
        if scope is None:
            # No scope - use the plain conventions section
            logger.debug("Using no-scope conventions")
            template = re.sub(
                r"<conventions_scope_provided>.*?</conventions_scope_provided>\n", "", template, flags=re.DOTALL
            )
            template = re.sub(
                r"<conventions_scope_inferred>.*?</conventions_scope_inferred>\n", "", template, flags=re.DOTALL
            )
            template = template.replace("<conventions_no_scope>", "<conventions>")
            template = template.replace("</conventions_no_scope>", "</conventions>")
        elif scope == "infer" or scope == "":
            # User wants to infer a scope from changes (either with "infer" or empty string)
            logger.debug(f"Using inferred-scope conventions (scope={scope})")
            template = re.sub(
                r"<conventions_scope_provided>.*?</conventions_scope_provided>\n", "", template, flags=re.DOTALL
            )
            template = re.sub(r"<conventions_no_scope>.*?</conventions_no_scope>\n", "", template, flags=re.DOTALL)
            template = template.replace("<conventions_scope_inferred>", "<conventions>")
            template = template.replace("</conventions_scope_inferred>", "</conventions>")
        else:
            # User provided a specific scope
            logger.debug(f"Using provided-scope conventions with scope '{scope}'")
            template = re.sub(
                r"<conventions_scope_inferred>.*?</conventions_scope_inferred>\n", "", template, flags=re.DOTALL
            )
            template = re.sub(r"<conventions_no_scope>.*?</conventions_no_scope>\n", "", template, flags=re.DOTALL)
            template = template.replace("<conventions_scope_provided>", "<conventions>")
            template = template.replace("</conventions_scope_provided>", "</conventions>")
            template = template.replace("{scope}", scope)
    except Exception as e:
        logger.error(f"Error processing scope parameter: {e}")
        # Fallback to no scope if there's an error
        template = re.sub(
            r"<conventions_scope_provided>.*?</conventions_scope_provided>\n", "", template, flags=re.DOTALL
        )
        template = re.sub(
            r"<conventions_scope_inferred>.*?</conventions_scope_inferred>\n", "", template, flags=re.DOTALL
        )
        template = template.replace("<conventions_no_scope>", "<conventions>")
        template = template.replace("</conventions_no_scope>", "</conventions>")

    template = template.replace("<status></status>", status)
    template = template.replace("<diff_stat></diff_stat>", diff_stat)
    template = template.replace("<diff></diff>", processed_diff)

    # Add hint if present
    if hint:
        template = template.replace("<hint_text></hint_text>", hint)
        logger.debug(f"Added hint ({len(hint)} characters)")
    else:
        template = re.sub(r"<hint>.*?</hint>", "", template, flags=re.DOTALL)
        logger.debug("No hint provided")

    # Process format options (one-liner vs multi-line)
    if one_liner:
        template = re.sub(r"<multi_line>.*?</multi_line>", "", template, flags=re.DOTALL)
    else:
        template = re.sub(r"<one_liner>.*?</one_liner>", "", template, flags=re.DOTALL)

    # Clean up examples sections based on scope settings
    if scope is None:
        # No scope - keep no_scope examples, remove scope examples
        template = re.sub(r"<examples_with_scope>.*?</examples_with_scope>\n?", "", template, flags=re.DOTALL)
        template = template.replace("<examples_no_scope>", "<examples>")
        template = template.replace("</examples_no_scope>", "</examples>")
    else:
        # With scope (either provided or inferred) - keep scope examples, remove no_scope examples
        template = re.sub(r"<examples_no_scope>.*?</examples_no_scope>\n?", "", template, flags=re.DOTALL)
        template = template.replace("<examples_with_scope>", "<examples>")
        template = template.replace("</examples_with_scope>", "</examples>")

    # Clean up extra whitespace, collapsing blank lines that may contain spaces
    template = re.sub(r"\n(?:[ \t]*\n){2,}", "\n\n", template)

    # Split the template into system and user prompts
    # System prompt contains all instructions, role, conventions, examples
    # User prompt contains the actual git data

    # Extract the git data sections for the user prompt
    user_sections = []

    # Extract git status
    status_match = re.search(r"<git_status>.*?</git_status>", template, re.DOTALL)
    if status_match:
        user_sections.append(status_match.group(0))
        # Remove from system prompt
        template = template.replace(status_match.group(0), "")

    # Extract git diff stat
    diff_stat_match = re.search(r"<git_diff_stat>.*?</git_diff_stat>", template, re.DOTALL)
    if diff_stat_match:
        user_sections.append(diff_stat_match.group(0))
        # Remove from system prompt
        template = template.replace(diff_stat_match.group(0), "")

    # Extract git diff
    diff_match = re.search(r"<git_diff>.*?</git_diff>", template, re.DOTALL)
    if diff_match:
        user_sections.append(diff_match.group(0))
        # Remove from system prompt
        template = template.replace(diff_match.group(0), "")

    # Extract hint if present
    hint_match = re.search(r"<hint>.*?</hint>", template, re.DOTALL)
    if hint_match and hint:  # Only include if hint was provided
        user_sections.append(hint_match.group(0))
        # Remove from system prompt
        template = template.replace(hint_match.group(0), "")

    # System prompt is everything else (role, conventions, examples, instructions)
    system_prompt = template.strip()
    system_prompt = re.sub(r"\n(?:[ \t]*\n){2,}", "\n\n", system_prompt)

    # User prompt is the git data sections
    user_prompt = "\n\n".join(user_sections).strip()

    return system_prompt, user_prompt


def clean_commit_message(message: str) -> str:
    """Clean up a commit message generated by an AI model.

    This function:
    1. Removes any preamble or reasoning text
    2. Removes code block markers and formatting
    3. Removes XML tags that might have leaked into the response
    4. Ensures the message starts with a conventional commit prefix
    5. Fixes double type prefix issues (e.g., "chore: feat(scope):")

    Args:
        message: Raw commit message from AI

    Returns:
        Cleaned commit message ready for use
    """
    message = message.strip()

    # Remove any markdown code blocks
    message = re.sub(r"```[\w]*\n|```", "", message)

    # Extract the actual commit message if it follows our reasoning pattern
    # Look for different indicators of where the actual commit message starts
    commit_indicators = [
        "# Your commit message:",
        "Your commit message:",
        "The commit message is:",
        "Here's the commit message:",
        "Commit message:",
        "Final commit message:",
        "# Commit Message",
    ]

    for indicator in commit_indicators:
        if indicator.lower() in message.lower():
            # Extract everything after the indicator
            message = message.split(indicator, 1)[1].strip()
            break

    # If message starts with any kind of explanation text, try to locate a conventional prefix
    lines = message.split("\n")
    for i, line in enumerate(lines):
        if any(
            line.strip().startswith(prefix)
            for prefix in ["feat:", "fix:", "docs:", "style:", "refactor:", "perf:", "test:", "build:", "ci:", "chore:"]
        ):
            message = "\n".join(lines[i:])
            break

    # Remove any XML tags that might have leaked into the response
    for tag in [
        "<git-status>",
        "</git-status>",
        "<git_status>",
        "</git_status>",
        "<git-diff>",
        "</git-diff>",
        "<git_diff>",
        "</git_diff>",
        "<repository_context>",
        "</repository_context>",
        "<instructions>",
        "</instructions>",
        "<format>",
        "</format>",
        "<conventions>",
        "</conventions>",
    ]:
        message = message.replace(tag, "")

    # Fix double type prefix issues (e.g., "chore: feat(scope):") to just "feat(scope):")
    conventional_prefixes = [
        "feat",
        "fix",
        "docs",
        "style",
        "refactor",
        "perf",
        "test",
        "build",
        "ci",
        "chore",
    ]

    # Look for double prefix pattern like "chore: feat(scope):" and fix it
    # This regex looks for a conventional prefix followed by another conventional prefix with a scope
    double_prefix_pattern = re.compile(
        r"^(" + r"|\s*".join(conventional_prefixes) + r"):\s*(" + r"|\s*".join(conventional_prefixes) + r")\(([^)]+)\):"
    )
    match = double_prefix_pattern.match(message)

    if match:
        # Extract the second type and scope, which is what we want to keep
        second_type = match.group(2)
        scope = match.group(3)
        description = message[match.end() :].strip()
        message = f"{second_type}({scope}): {description}"

    # Ensure message starts with a conventional commit prefix
    if not any(
        message.strip().startswith(prefix + ":") or message.strip().startswith(prefix + "(")
        for prefix in conventional_prefixes
    ):
        message = f"chore: {message.strip()}"

    # Final cleanup: trim extra whitespace and ensure no more than one blank line
    # Handle blank lines that may include spaces or tabs
    message = re.sub(r"\n(?:[ \t]*\n){2,}", "\n\n", message).strip()

    return message
