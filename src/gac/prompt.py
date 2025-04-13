"""Prompt creation for GAC.

This module handles the creation of prompts for AI models, including template loading,
formatting, and integration with diff preprocessing.
"""

import logging
import os
import re
from pathlib import Path
from typing import Optional

from gac.constants import DEFAULT_DIFF_TOKEN_LIMIT
from gac.errors import ConfigError
from gac.git import run_git_command
from gac.preprocess import preprocess_diff

logger = logging.getLogger(__name__)

DEFAULT_TEMPLATE = """Write a concise and meaningful git commit message based on the staged changes shown below.

<one_liner>
Format it as a single line.
</one_liner>

<multi_line>
Format it with a concise summary line followed by details using bullet points.
</multi_line>

<hint_section>
Please consider this context from the user: {hint}
</hint_section>

Git status:
{status}

Changes to be committed:
{diff}
"""


def find_template_file() -> Optional[str]:
    """Find a prompt template file in standard locations.

    Searches for template files in the following order:
    1. Environment variable GAC_TEMPLATE_PATH
    2. Current directory: ./prompt.template
    3. User config directory: ~/.config/gac/prompt.template
    4. Package directory: gac/templates/default.prompt
    5. Project directory: prompts/default.prompt

    Returns:
        Path to the template file or None if not found
    """
    env_path = os.environ.get("GAC_TEMPLATE_PATH")
    if env_path and os.path.exists(env_path):
        return env_path

    current_dir_path = Path("./prompt.template")
    if current_dir_path.exists():
        return str(current_dir_path)

    config_dir_path = Path.home() / ".config" / "gac" / "prompt.template"
    if config_dir_path.exists():
        return str(config_dir_path)

    package_template = Path(__file__).parent / "templates" / "default.prompt"
    if package_template.exists():
        return str(package_template)

    default_template = Path(__file__).parent.parent.parent / "prompts" / "default.prompt"
    if default_template.exists():
        return str(default_template)

    return None


def load_prompt_template(template_path: Optional[str] = None) -> str:
    """Load the prompt template from a file or use the default embedded template.

    Args:
        template_path: Optional path to a template file

    Returns:
        Template content as string

    Raises:
        ConfigError: If no template file is found
    """
    if template_path:
        if os.path.exists(template_path):
            logger.debug(f"Loading prompt template from {template_path}")
            with open(template_path, "r") as f:
                return f.read()
        else:
            raise ConfigError(f"Prompt template file not found at {template_path}")

    template_file = find_template_file()
    if template_file:
        logger.debug(f"Loading prompt template from {template_file}")
        with open(template_file, "r") as f:
            return f.read()

    logger.debug("No template file found, using default template")
    return DEFAULT_TEMPLATE


def add_repository_context(diff: str) -> str:
    """Extract and format repository context from the git diff.

    Args:
        diff: The git diff to analyze

    Returns:
        Formatted repository context as a string
    """
    if not diff:
        return ""

    file_paths = re.findall(r"diff --git a/(.*) b/", diff)
    if not file_paths:
        return ""

    context_sections = ["Repository Context:", "File purposes:"]

    # Get repository information
    try:
        repo_url = run_git_command(["config", "--get", "remote.origin.url"], silent=True)
        if repo_url:
            repo_name = re.search(r"[:/]([^/]+?)(?:\.git)?$", repo_url)
            if repo_name:
                context_sections.append(f"Repository: {repo_name.group(1)}")
    except Exception as e:
        logger.debug(f"Error getting repository information: {e}")

    # Get branch information
    try:

        branch = run_git_command(["rev-parse", "--abbrev-ref", "HEAD"], silent=True)
        if branch:
            context_sections.append(f"Branch: {branch}")
    except Exception as e:
        logger.debug(f"Error getting branch information: {e}")

    # Get directory context
    for path in file_paths:
        dir_name = os.path.dirname(path).split("/")[0]
        if dir_name:
            try:
                dir_content = run_git_command(["ls-tree", "--name-only", "HEAD", dir_name], silent=True)
                if dir_content:
                    context_sections.append(f"Directory context ({dir_name}):")
                    # Add directory contents as bullet points
                    for file in dir_content.strip().split("\n"):
                        context_sections.append(f"• {file}")
                    break
            except Exception as e:
                logger.debug(f"Error getting directory context: {e}")

    purposes = []
    for path in file_paths[:5]:
        if path.endswith(".py"):
            try:
                file_content = run_git_command(["show", f"HEAD:{path}"], silent=True)
                if file_content:
                    docstring_match = re.search(r'"""(.*?)"""', file_content, re.DOTALL)
                    if docstring_match:
                        docstring = docstring_match.group(1).strip()
                        if docstring:
                            purposes.append(f"• {path}: {docstring}")
            except Exception as e:
                logger.debug(f"Error extracting docstring from {path}: {e}")

    if purposes:
        context_sections.extend(purposes)

    if file_paths:
        try:
            # Get the commit history for the modified files
            history = run_git_command(["log", "--pretty=format:%h %s", "-n", "3", "--", *file_paths], silent=True)
            if history:
                # Format the history with bullet points
                formatted_history = "\n".join(f"• {line}" for line in history.split("\n") if line)
                context_sections.append(f"\nRecent related commits:\n{formatted_history}")
        except Exception as e:
            logger.debug(f"Error getting commit history: {e}")

    return "\n".join(context_sections)


def build_prompt(
    status: str,
    diff: str,
    one_liner: bool = False,
    hint: str = "",
    template_path: Optional[str] = None,
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

    logger.debug(f"Preprocessing diff ({len(diff)} characters)")
    processed_diff = preprocess_diff(diff, token_limit=DEFAULT_DIFF_TOKEN_LIMIT, model=model)
    logger.debug(f"Processed diff ({len(processed_diff)} characters)")

    # Add repository context if available
    repo_context = add_repository_context(diff)

    if repo_context:
        processed_diff = f"{repo_context}\n\n{processed_diff}"

    # Format the template with status and diff
    # Handle different tag formats for compatibility with tests
    if "<status></status>" in template:
        template = template.replace("<status></status>", status)
    else:
        template = template.replace("{status}", status)

    if "<diff></diff>" in template:
        template = template.replace("<diff></diff>", processed_diff)
    else:
        template = template.replace("{diff}", processed_diff)

    if "<hint></hint>" in template:
        template = template.replace("<hint></hint>", hint)
    else:
        template = template.replace("{hint}", hint)

    # Handle one-liner vs multi-line sections
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

    Args:
        message: Raw commit message from AI

    Returns:
        Cleaned commit message ready for use
    """
    message = message.strip()

    # Handle code blocks with language specifier
    if "```" in message:
        # Extract content from code blocks
        lines = message.split("\n")
        content_lines = []
        inside_block = False

        for line in lines:
            if line.startswith("```"):
                # Toggle inside_block state, but skip the marker line
                inside_block = not inside_block
                continue

            if inside_block:
                content_lines.append(line)

        if content_lines:
            message = "\n".join(content_lines).strip()

    # Remove XML tags
    xml_tags = ["<git-status>", "</git-status>", "<git-diff>", "</git-diff>"]
    for tag in xml_tags:
        message = message.replace(tag, "")

    # Define conventional commit prefixes
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
