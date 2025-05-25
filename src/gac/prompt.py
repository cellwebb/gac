# flake8: noqa: E501
"""Prompt creation for GAC.

This module handles the creation of prompts for AI models, including template loading,
formatting, and integration with diff preprocessing.
"""

import logging
import os
import re
from typing import Optional

from gac.constants import Utility
from gac.git import run_git_command
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
  </one_liner>
  <multi_line>
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

If a scope is provided, include it in parentheses after the type and before the colon, like this:
- feat(scope): description
- fix(scope): description
- etc.

Select the prefix that best matches the primary purpose of the changes.
If multiple prefixes apply, choose the one that represents the most significant change.
If you cannot confidently determine a type, use 'chore'.
</conventions>

<hint>
Additional context provided by the user: <hint_text></hint_text>
</hint>

<git_status>
<status></status>
</git_status>

<repository_context>
</repository_context>

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


def extract_repository_context(diff: str) -> str:
    """Extract and format repository context from the git diff.

    This function enhances the prompt by providing valuable repository context information:
    1. File purposes extracted from docstrings
    2. Recent commit history for the modified files
    3. Project structure information

    Args:
        diff: The git diff to analyze

    Returns:
        Formatted repository context as a string
    """
    if not diff:
        return ""

    # Extract affected file paths
    file_paths = re.findall(r"diff --git a/(.*) b/", diff)
    if not file_paths:
        return ""

    context_sections = []

    # 1. Extract file purpose from docstrings
    file_purposes = []
    for path in file_paths[:5]:  # Limit to 5 files to avoid token bloat
        if path.endswith(".py"):
            try:
                # Get the file content from HEAD - don't raise if command fails
                file_content = run_git_command(["show", f"HEAD:{path}"], silent=True)
                if file_content:
                    # Extract file docstring (first triple-quoted string)
                    docstring_match = re.search(r'"""(.*?)"""', file_content, re.DOTALL)
                    if docstring_match:
                        # Extract the first line as a summary
                        docstring = docstring_match.group(1).strip()
                        first_line = docstring.split("\n")[0].strip()
                        if first_line:
                            file_purposes.append(f"• {path}: {first_line}")
            except Exception as e:
                logger.debug(f"Error extracting docstring from {path}: {e}")

    if file_purposes:
        context_sections.append("File purposes:\n" + "\n".join(file_purposes))

    # 2. Add recent related commits
    try:
        # Get recent commits for the modified files
        recent_commits = run_git_command(
            ["log", "--pretty=format:%h %s", "-n", "3", "--", *file_paths[:5]], silent=True
        )
        if recent_commits:
            commit_lines = recent_commits.split("\n")[:3]  # Limit to 3 commits
            context_sections.append("Recent related commits:\n" + "\n".join([f"• {c}" for c in commit_lines]))
    except Exception as e:
        logger.debug(f"Error getting recent commits: {e}")

    # 3. Add repository structure information
    try:
        # Get the repo name
        remote_url = run_git_command(["config", "--get", "remote.origin.url"], silent=True)
        if remote_url:
            # Extract repo name from URL
            repo_name = re.search(r"/([^/]+?)(\.git)?$", remote_url)
            if repo_name:
                context_sections.append(f"Repository: {repo_name.group(1)}")

        # Get the branch name
        branch = run_git_command(["rev-parse", "--abbrev-ref", "HEAD"], silent=True)
        if branch:
            context_sections.append(f"Branch: {branch}")
    except Exception as e:
        logger.debug(f"Error getting repository info: {e}")

    # 4. Get directory structure for context
    if len(file_paths) > 0:
        # Determine common parent directory
        parent_dirs = [os.path.dirname(p) for p in file_paths]
        if parent_dirs and any(parent_dirs):
            common_dir = os.path.commonpath(parent_dirs) if len(parent_dirs) > 1 else parent_dirs[0]
            if common_dir:
                try:
                    # List files in this directory to provide context
                    dir_content = run_git_command(["ls-tree", "--name-only", "HEAD", common_dir], silent=True)
                    if dir_content:
                        dir_files = dir_content.split("\n")[:5]  # Limit to 5 entries
                        context_sections.append(
                            f"Directory context ({common_dir}):\n" + "\n".join([f"• {f}" for f in dir_files])
                        )
                except Exception as e:
                    logger.debug(f"Error getting directory context: {e}")

    # Combine all sections with headers
    if context_sections:
        return "Repository Context:\n" + "\n\n".join(context_sections)

    return ""


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

    # Add scope to the conventions section if provided
    if scope:
        template = template.replace(
            "Select the prefix that best matches the primary purpose of the changes.",
            f"If a scope is provided, include it in parentheses after the type and before the colon, like this:\n- feat({scope}): description\n- fix({scope}): description\n- etc.\n\nSelect the prefix that best matches the primary purpose of the changes.",
        )

    template = template.replace("<status></status>", status)
    template = template.replace("<diff></diff>", processed_diff)

    # Add repository context if present
    repo_context = extract_repository_context(diff)
    if repo_context:
        template = template.replace(
            "<repository_context></repository_context>", f"<repository_context>\n{repo_context}\n</repository_context>"
        )
        logger.debug(f"Added repository context ({len(repo_context)} characters)")
    else:
        template = template.replace("<repository_context></repository_context>", "")
        logger.debug("No repository context could be extracted")

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
    message = re.sub(r"\n{3,}", "\n\n", message)

    # Ensure we don't have any trailing/leading whitespace
    return message.strip()
