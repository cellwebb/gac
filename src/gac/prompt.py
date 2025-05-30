# flake8: noqa: E501
"""Prompt creation for gac.

This module handles the creation of prompts for AI models, including template loading,
formatting, and integration with diff preprocessing.
"""

import logging
import re
from typing import Optional

from gac.constants import Utility
from gac.preprocess import preprocess_diff

logger = logging.getLogger(__name__)

# Default template to use when no template file is found
DEFAULT_TEMPLATE = """<role>
You are an expert git commit message generator. Your task is to analyze code changes and create a concise, meaningful git commit message. You will receive git status and diff information. Your entire response will be used directly as a git commit message.
</role>

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

<conventions>
You MUST start your commit message with the most appropriate conventional commit prefix:
- feat: A new feature or functionality addition
- fix: A bug fix or error correction
- docs: Documentation changes only
- style: Changes to code style/formatting without logic changes
- refactor: Code restructuring without behavior changes
- perf: Performance improvements
- test: Adding/modifying tests
- build: Changes to build system/dependencies
- ci: Changes to CI configuration
- chore: Miscellaneous changes not affecting src/test files

Select the prefix that best matches the primary purpose of the changes.
If multiple prefixes apply, choose the one that represents the most significant change.
If you cannot confidently determine a type, use 'chore'.
</conventions>

<scope_instructions>
When creating the commit message, include a scope in parentheses after the type and before the colon if it helps categorize the change.
Examples:
- feat(auth): add login functionality
- fix(api): handle null response
- docs: update README

Choose a short, lowercase scope that describes the area of the codebase being changed.
</scope_instructions>

<hint>
Additional context provided by the user: <hint_text></hint_text>
</hint>

<git_status>
<status></status>
</git_status>

<git_diff>
<diff></diff>
</git_diff>

<instructions>
IMMEDIATELY AFTER ANALYZING THE CHANGES, RESPOND WITH ONLY THE COMMIT MESSAGE.
DO NOT include any preamble, reasoning, explanations or anything other than the commit message itself.
DO NOT use markdown formatting, headers, or code blocks.
The entire response will be passed directly to 'git commit -m'.
</instructions>
"""


def load_prompt_template() -> str:
    """Load the prompt template from the embedded default template.

    Returns:
        Template content as string
    """
    logger.debug("Using default template")
    return DEFAULT_TEMPLATE


def build_prompt(
    status: str,
    diff: str,
    one_liner: bool = False,
    hint: str = "",
    model: str = "anthropic:claude-3-haiku-latest",
    template_path: Optional[str] = None,  # Kept for API compatibility but unused
    scope: Optional[str] = None,
) -> str:
    """Build a prompt for the AI model using the provided template and git information.

    Args:
        status: Git status output
        diff: Git diff output
        one_liner: Whether to request a one-line commit message
        hint: Optional hint to guide the AI
        model: Model identifier for token counting
        template_path: Unused parameter kept for API compatibility

    Returns:
        Formatted prompt string ready to be sent to an AI model
    """
    template = load_prompt_template()

    # Preprocess the diff with smart filtering and truncation
    logger.debug(f"Preprocessing diff ({len(diff)} characters)")
    processed_diff = preprocess_diff(diff, token_limit=Utility.DEFAULT_DIFF_TOKEN_LIMIT, model=model)
    logger.debug(f"Processed diff ({len(processed_diff)} characters)")

    # Handle scope instructions
    if scope is not None:  # User explicitly used --scope
        if scope:  # User provided a specific scope
            template = template.replace(
                "<scope_instructions>",
                f"The user specified the scope to be '{scope}'. "
                f"Please include this exact scope in parentheses after the type (e.g., 'fix({scope}): ...').",
            )
        else:  # User used --scope without a value
            template = template.replace(
                "<scope_instructions>",
                "The user requested to include a scope in the commit message. "
                "Please determine and include the most appropriate scope in parentheses after the type.",
            )
    else:
        # Remove scope instructions if --scope was not used
        template = re.sub(r"<scope_instructions>.*?</scope_instructions>\n", "", template, flags=re.DOTALL)

    template = template.replace("<status></status>", status)
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

    # Clean up extra whitespace
    template = re.sub(r"\n{3,}", "\n\n", template)

    return template.strip()


def clean_commit_message(message: str) -> str:
    """Clean up a commit message generated by an AI model.

    This function:
    1. Removes any preamble or reasoning text
    2. Removes code block markers and formatting
    3. Removes XML tags that might have leaked into the response
    4. Ensures the message starts with a conventional commit prefix

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

    # Ensure message starts with a conventional commit prefix
    conventional_prefixes = [
        "feat:",
        "fix:",
        "docs:",
        "style:",
        "refactor:",
        "perf:",
        "test:",
        "build:",
        "ci:",
        "chore:",
    ]

    # If the message doesn't start with a conventional prefix, add one
    if not any(message.strip().startswith(prefix) for prefix in conventional_prefixes):
        message = f"chore: {message.strip()}"

    # Final cleanup: trim extra whitespace and ensure no more than one blank line
    message = re.sub(r"\n{3,}", "\n\n", message).strip()

    return message
