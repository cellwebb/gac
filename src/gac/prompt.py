"""Prompt creation for GAC.

This module handles the creation of prompts for AI models, including template loading,
formatting, and integration with diff preprocessing.
"""

import logging
import os
import re
from pathlib import Path
from typing import Optional

from gac.errors import ConfigError
from gac.git import run_git_command
from gac.preprocess import preprocess_diff

logger = logging.getLogger(__name__)

# Maximum number of tokens to allocate for the diff in the prompt
DEFAULT_DIFF_TOKEN_LIMIT = 6000

# Default template to use when the file is not found
DEFAULT_TEMPLATE = """Write a concise and meaningful git commit message based on the staged changes shown below.

<format_section>
  <one_liner>
  Format it as a single line (50-72 characters if possible). 
  If applicable, still use conventional commit prefixes like feat/fix/docs/etc., 
  but keep everything to a single line with no bullet points.
  </one_liner>
  
  <multi_line>
  Format it with a concise summary line (50-72 characters) followed by a 
  more detailed explanation with multiple bullet points highlighting the 
  specific changes made. Order the bullet points from most important to least important.
  </multi_line>
</format_section>

<conventional_section>
IMPORTANT: EVERY commit message MUST start with a conventional commit prefix. 
This is a HARD REQUIREMENT. Choose from:
- feat: A new feature
- fix: A bug fix
- docs: Documentation changes
- style: Changes that don't affect code meaning (formatting, whitespace)
- refactor: Code changes that neither fix a bug nor add a feature
- perf: Performance improvements
- test: Adding or correcting tests
- build: Changes to build system or dependencies
- ci: Changes to CI configuration
- chore: Other changes that don't modify src or test files

YOU MUST choose the most appropriate type based on the changes. 
If you CANNOT determine a type, use 'chore'. 
THE PREFIX IS MANDATORY - NO EXCEPTIONS.
</conventional_section>

<hint_section>
Please consider this context from the user: <hint></hint>
</hint_section>

Do not include any explanation or preamble like 'Here's a commit message', etc.
Just output the commit message directly.

Git status:
<git-status>
<status></status>
</git-status>

Changes to be committed:
<git-diff>
<diff></diff>
</git-diff>
"""


def get_default_template_path():
    """Returns the path to the default template file packaged with GAC.

    Returns:
        Path to the default template file
    """
    return Path(__file__).parent / "templates" / "default.prompt"


def load_prompt_template(template_path: Optional[str] = None) -> str:
    """Load the prompt template from a file or use the default embedded template.

    Args:
        template_path: Optional path to a template file (not used, kept for API compatibility)

    Returns:
        Template content as string
    """
    default_template_path = get_default_template_path()
    if default_template_path.exists():
        logger.debug(f"Loading default template from {default_template_path}")
        with open(default_template_path, "r") as f:
            return f.read()

    logger.debug("Default template file not found, using embedded template")
    return DEFAULT_TEMPLATE


def add_repository_context(diff: str) -> str:
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
                # Get the file content from HEAD
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
    template_path: Optional[str] = None,  # Kept for backwards compatibility but not used
    model: str = "anthropic:claude-3-haiku-latest",
) -> str:
    """Build a prompt for the AI model using the provided template and git information.

    Args:
        status: Git status output
        diff: Git diff output
        one_liner: Whether to request a one-line commit message
        hint: Optional hint to guide the AI
        template_path: Optional path to a custom template file
        model: Model identifier for token counting

    Returns:
        Formatted prompt string ready to be sent to an AI model
    """
    template = load_prompt_template(template_path)

    # Preprocess the diff with smart filtering and truncation
    logger.debug(f"Preprocessing diff ({len(diff)} characters)")
    processed_diff = preprocess_diff(diff, token_limit=DEFAULT_DIFF_TOKEN_LIMIT, model=model)
    logger.debug(f"Processed diff ({len(processed_diff)} characters)")

    # Generate repository context
    repo_context = add_repository_context(diff)
    logger.debug(f"Added repository context ({len(repo_context)} characters)")

    # Replace placeholders with actual content
    template = template.replace("<status></status>", status)

    # Add repository context before the diff if present
    if repo_context:
        processed_diff = f"{repo_context}\n\n{processed_diff}"

    template = template.replace("<diff></diff>", processed_diff)
    template = template.replace("<hint></hint>", hint)

    # Process format options (one-liner vs multi-line)
    if one_liner:
        template = re.sub(r"<multi_line>.*?</multi_line>", "", template, flags=re.DOTALL)
        template = re.sub(r"<one_liner>(.*?)</one_liner>", r"\1", template, flags=re.DOTALL)
    else:
        template = re.sub(r"<one_liner>.*?</one_liner>", "", template, flags=re.DOTALL)
        template = re.sub(r"<multi_line>(.*?)</multi_line>", r"\1", template, flags=re.DOTALL)

    # Process hint section
    if not hint:
        template = re.sub(r"<hint_section>.*?</hint_section>", "", template, flags=re.DOTALL)
    else:
        template = re.sub(r"<hint_section>(.*?)</hint_section>", r"\1", template, flags=re.DOTALL)

    # Process format section if present
    template = re.sub(r"<format_section>(.*?)</format_section>", r"\1", template, flags=re.DOTALL)

    # Remove git-status and git-diff tags
    template = re.sub(r"<git-status>(.*?)</git-status>", r"\1", template, flags=re.DOTALL)
    template = re.sub(r"<git-diff>(.*?)</git-diff>", r"\1", template, flags=re.DOTALL)

    # Remove any remaining XML tags and clean up whitespace
    template = re.sub(r"<[^>]*>", "", template)
    template = re.sub(r"\n{3,}", "\n\n", template)

    return template.strip()


def clean_commit_message(message: str) -> str:
    """Clean up a commit message generated by an AI model.

    This function:
    1. Removes code block markers (```backticks```)
    2. Removes XML tags that might have leaked into the response
    3. Ensures the message starts with a conventional commit prefix

    Args:
        message: Raw commit message from AI

    Returns:
        Cleaned commit message ready for use
    """
    message = message.strip()

    # Remove code block markers (backticks)
    if message.startswith("```"):
        # Check if the first line contains a language identifier (e.g., ```python)
        if "\n" in message:
            first_line_end = message.find("\n")
            first_line = message[:first_line_end]
            if first_line.count("```") == 1:
                message = message[first_line_end + 1 :]
        else:
            message = message[3:].lstrip()

    if message.endswith("```"):
        message = message[:-3].rstrip()

    # Handle cases where message still has backticks
    message = message.replace("```\n", "").replace("\n```", "")

    # Remove any XML tags that might have leaked into the response
    for tag in ["<git-status>", "</git-status>", "<git-diff>", "</git-diff>"]:
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
    if not any(message.startswith(prefix) for prefix in conventional_prefixes):
        message = f"chore: {message}"

    return message.strip()
