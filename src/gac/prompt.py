"""Module for prompt-related functionality for GAC.

This module handles building and cleaning prompts for AI providers.
"""


def build_prompt(
    status: str, diff: str, one_liner: bool = False, hint: str = "", conventional: bool = True
) -> str:
    """
    Build a prompt for the LLM to generate a commit message.

    Args:
        status: Output of git status
        diff: Output of git diff --staged
        one_liner: If True, request a single-line commit message
        hint: Optional context to include in the prompt (like "JIRA-123")
        conventional: If True, enforce conventional commit format

    Returns:
        The formatted prompt string
    """
    template = (
        "Write a concise and meaningful git commit message based on the staged "
        "changes shown below.\n"
        "{format_section}\n"
        "{conventional_section}\n"
        "{hint_section}\n"
        "\n"
        "Do not include any explanation or preamble like 'Here's a commit message', etc.\n"
        "Just output the commit message directly.\n"
        "\n"
        "Git status:\n"
        "<git-status>\n"
        "{status}\n"
        "</git-status>\n"
        "\n"
        "Changes to be committed:\n"
        "<git-diff>\n"
        "{diff}\n"
        "</git-diff>"
    )

    if one_liner:
        format_section = (
            "Format it as a single line (50-72 characters if possible). "
            "If applicable, still use conventional commit prefixes like feat/fix/docs/etc., "
            "but keep everything to a single line with no bullet points."
        )
    else:
        format_section = (
            "Format it with a concise summary line (50-72 characters) followed by a "
            "more detailed explanation with multiple bullet points highlighting the "
            "specific changes made. Order the bullet points from most important to least important."
        )

    conventional_section = (
        (
            "IMPORTANT: EVERY commit message MUST start with a conventional commit prefix. "
            "This is a HARD REQUIREMENT. Choose from:"
            "\n- feat: A new feature"
            "\n- fix: A bug fix"
            "\n- docs: Documentation changes"
            "\n- style: Changes that don't affect code meaning (formatting, whitespace)"
            "\n- refactor: Code changes that neither fix a bug nor add a feature"
            "\n- perf: Performance improvements"
            "\n- test: Adding or correcting tests"
            "\n- build: Changes to build system or dependencies"
            "\n- ci: Changes to CI configuration"
            "\n- chore: Other changes that don't modify src or test files"
            "\n\nYOU MUST choose the most appropriate type based on the changes. "
            "If you CANNOT determine a type, use 'chore'. "
            "THE PREFIX IS MANDATORY - NO EXCEPTIONS."
        )
        if conventional
        else ""
    )

    hint_section = f"Please consider this context from the user: {hint}" if hint else ""

    return template.format(
        format_section=format_section,
        conventional_section=conventional_section,
        hint_section=hint_section,
        status=status,
        diff=diff,
    )


def clean_commit_message(message: str) -> str:
    """
    Clean the commit message to ensure it doesn't contain triple backticks or XML tags.

    Args:
        message: The commit message to clean

    Returns:
        The cleaned commit message
    """
    message = message.strip()

    # Remove leading and trailing backticks
    if message.startswith("```"):
        message = message[3:].lstrip()

    if message.endswith("```"):
        message = message[:-3].rstrip()

    # Handle markdown-style language specification like ```python
    if message.startswith("```") and "\n" in message:
        message = message.split("\n", 1)[1].lstrip()

    # Remove any XML tags that might have been included
    for tag in ["<git-status>", "</git-status>", "<git-diff>", "</git-diff>"]:
        message = message.replace(tag, "")

    # Add conventional commit prefix if not present (for backward compatibility with tests)
    if not any(
        message.startswith(prefix)
        for prefix in [
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
    ):
        message = f"chore: {message}"

    return message


def create_abbreviated_prompt(prompt: str, max_diff_lines: int = 50) -> str:
    """
    Create an abbreviated version of the prompt by limiting the diff lines.

    Args:
        prompt: The original full prompt
        max_diff_lines: Maximum number of diff lines to include

    Returns:
        Abbreviated prompt with a note about hidden lines
    """
    # Locate the diff section using the tags
    diff_start_tag = "<git-diff>"
    diff_end_tag = "</git-diff>"

    # If tags aren't found, return original prompt
    if diff_start_tag not in prompt or diff_end_tag not in prompt:
        return prompt

    # Split the prompt into parts
    before_diff, rest = prompt.split(diff_start_tag, 1)
    diff_content, after_diff = rest.split(diff_end_tag, 1)

    # Split diff into lines and check if it's already small enough
    diff_lines = diff_content.split("\n")
    if len(diff_lines) <= max_diff_lines:
        return prompt

    # Take half of the lines from the beginning and half from the end
    half = max_diff_lines // 2
    first_half = diff_lines[:half]
    second_half = diff_lines[-half:]

    # Create the message about hidden lines
    hidden_count = len(diff_lines) - max_diff_lines
    hidden_msg = f"\n\n... {hidden_count} lines hidden ...\n\nUse --show-prompt-full to see the complete prompt.\n\n"

    # Create the abbreviated diff and reconstruct the prompt
    abbreviated_diff = "\n".join(first_half) + hidden_msg + "\n".join(second_half)
    return before_diff + diff_start_tag + abbreviated_diff + diff_end_tag + after_diff
