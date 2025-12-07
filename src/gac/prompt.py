# flake8: noqa: E501
"""Prompt creation for gac.

This module handles the creation of prompts for AI models, including template loading,
formatting, and integration with diff preprocessing.
"""

import logging
import re
from functools import lru_cache
from importlib.resources import files

logger = logging.getLogger(__name__)


# ============================================================================
# Template Loading from Package Resources
# ============================================================================


@lru_cache(maxsize=1)
def _load_default_system_template() -> str:
    """Load the default system prompt template from package resources."""
    return files("gac.templates").joinpath("system_prompt.txt").read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def _load_default_user_template() -> str:
    """Load the default user prompt template from package resources."""
    return files("gac.templates").joinpath("user_prompt.txt").read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def _load_question_generation_template() -> str:
    """Load the question generation template from package resources."""
    return files("gac.templates").joinpath("question_generation.txt").read_text(encoding="utf-8")


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

    logger.debug("Using default system template from package resources")
    return _load_default_system_template()


def load_user_template() -> str:
    """Load the user prompt template (contains git data sections and instructions).

    Returns:
        User template content as string
    """
    logger.debug("Using default user template from package resources")
    return _load_default_user_template()


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


def build_question_generation_prompt(
    status: str,
    processed_diff: str,
    diff_stat: str = "",
    hint: str = "",
) -> tuple[str, str]:
    """Build system and user prompts for question generation about staged changes.

    Args:
        status: Git status output
        processed_diff: Git diff output, already preprocessed and ready to use
        diff_stat: Git diff stat output showing file changes summary
        hint: Optional hint to guide the question generation

    Returns:
        Tuple of (system_prompt, user_prompt) ready to be sent to an AI model
    """
    system_prompt = _load_question_generation_template()

    # Build user prompt with git context
    user_prompt = f"""<git_diff>
{processed_diff}
</git_diff>

<git_diff_stat>
{diff_stat}
</git_diff_stat>

<git_status>
{status}
</git_status>"""

    if hint:
        user_prompt = f"""<hint>
Additional context provided by the user: {hint}
</hint>

{user_prompt}"""

    # Add instruction to ask questions in the appropriate language if specified
    user_prompt += """

<format_instructions>
Analyze the changes above and determine the appropriate number of questions based on the change complexity. Generate 1-5 focused questions that clarify the intent, motivation, and impact of these changes. For very small changes, ask only 1-2 essential questions. Respond with ONLY a numbered list of questions as specified in the system prompt.
</format_instructions>"""

    return system_prompt.strip(), user_prompt.strip()
