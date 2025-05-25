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
    logger.debug("Extracting repository context from diff")
    if not diff:
        logger.debug("No diff provided, returning empty context")
        return ""

    logger.debug("Diff content starts with: %s", diff[:200] if len(diff) > 200 else diff)

    # Log the full diff for debugging purposes
    logger.debug("Full diff content (first 1000 chars): %s", diff[:1000])

    # Extract affected file paths
    file_paths = re.findall(r"diff --git a/(.*) b/", diff)
    if not file_paths:
        logger.debug("No file paths found in diff, returning empty context")
        return ""

    logger.debug(f"Found {len(file_paths)} files in diff: {file_paths}")

    # Log the first few file paths for verification
    for i, path in enumerate(file_paths[:5], 1):
        logger.debug(f"File {i}/{len(file_paths)}: {path}")
        logger.debug(f"File exists: {os.path.exists(path)}")
        logger.debug(f"Is file: {os.path.isfile(path) if os.path.exists(path) else 'N/A'}")
        logger.debug(f"File extension: {os.path.splitext(path)[1] if os.path.exists(path) else 'N/A'}")

    context_sections = []

    # 1. Extract file purpose from docstrings
    file_purposes = []
    logger.debug("Extracting file purposes from docstrings")
    logger.debug(f"Files to process: {file_paths[:5]}")

    for i, path in enumerate(file_paths[:5], 1):  # Limit to 5 files to avoid token bloat
        logger.debug(f"Processing file {i}/{min(5, len(file_paths))}: {path}")
        if path.endswith(".py"):
            try:
                logger.debug(f"Getting content for file: {path}")
                # Get the file content from HEAD - don't raise if command fails
                file_content = run_git_command(["show", f"HEAD:{path}"], silent=True, raise_on_error=False)
                logger.debug(f"Got {len(file_content or '')} bytes for {path}")

                if file_content:
                    logger.debug(f"Looking for docstring in {path}")
                    # Extract module docstring
                    docstring_match = re.search(r'"""(.*?)"""', file_content, re.DOTALL)
                    if docstring_match:
                        docstring = docstring_match.group(1).strip()
                        logger.debug(f"Found docstring in {path}: {docstring[:100]}...")
                        # Get first non-empty line as summary
                        summary = next((line for line in docstring.split("\n") if line.strip()), "")
                        if summary:
                            file_purposes.append(f"• {path}: {summary}")
                            logger.debug(f"Added purpose for {path}")
                        else:
                            logger.debug(f"No summary found in docstring for {path}")
                    else:
                        logger.debug(f"No docstring found in {path}")
                else:
                    logger.debug(f"No content found for file: {path}")
            except Exception as e:
                logger.debug(f"Error extracting docstring from {path}", exc_info=True)

    if file_purposes:
        context_sections.append("File purposes:\n" + "\n".join(file_purposes))

    # 2. Add recent related commits
    logger.debug("Fetching recent related commits")
    try:
        # Get recent commits for the modified files
        recent_commits = run_git_command(
            ["log", "--pretty=format:%h %s", "-n", "3", "--", *file_paths[:5]], silent=True
        )
        if recent_commits:
            commit_lines = recent_commits.split("\n")[:3]  # Limit to 3 commits
            logger.debug(f"Found {len(commit_lines)} recent commits")
            context_sections.append("Recent related commits:\n" + "\n".join([f"• {c}" for c in commit_lines]))
        else:
            logger.debug("No recent commits found for modified files")
    except Exception as e:
        logger.debug(f"Error getting recent commits: {e}", exc_info=True)

    # 3. Add repository structure information
    logger.debug("Fetching repository structure information")
    try:
        # Get the repo name
        logger.debug("Getting remote URL")
        remote_url = run_git_command(["config", "--get", "remote.origin.url"], silent=True)
        if remote_url:
            logger.debug(f"Found remote URL: {remote_url}")
            # Extract repo name from URL
            repo_name = re.search(r"/([^/]+?)(\.git)?$", remote_url)
            if repo_name:
                repo_name = repo_name.group(1)
                logger.debug(f"Extracted repo name: {repo_name}")
                context_sections.append(f"Repository: {repo_name}")
        else:
            logger.debug("No remote URL found")

        # Get the branch name
        logger.debug("Getting current branch name")
        branch = run_git_command(["rev-parse", "--abbrev-ref", "HEAD"], silent=True)
        if branch:
            logger.debug(f"On branch: {branch}")
            context_sections.append(f"Branch: {branch}")
        else:
            logger.debug("Could not determine current branch")
    except Exception as e:
        logger.debug(f"Error getting repository info: {e}", exc_info=True)

    # 4. Get directory structure for context
    logger.debug("Analyzing directory structure")
    if file_paths:
        # Determine common parent directory
        parent_dirs = [os.path.dirname(p) for p in file_paths]
        logger.debug(f"Parent directories: {parent_dirs}")

        if parent_dirs and any(parent_dirs):
            common_dir = os.path.commonpath(parent_dirs) if len(parent_dirs) > 1 else parent_dirs[0]
            logger.debug(f"Common directory: {common_dir}")

            if common_dir:
                try:
                    logger.debug(f"Getting directory listing for: {common_dir}")
                    dir_content = run_git_command(["ls-tree", "--name-only", "HEAD", common_dir], silent=True)
                    if dir_content:
                        dir_files = [f for f in dir_content.split("\n") if f][:5]  # Limit to 5 entries
                        logger.debug(f"Found {len(dir_files)} files in directory")
                        context_sections.append(
                            f"Directory context ({common_dir}):\n" + "\n".join([f"• {f}" for f in dir_files])
                        )
                    else:
                        logger.debug(f"No files found in directory: {common_dir}")
                except Exception as e:
                    logger.debug(f"Error getting directory context: {e}", exc_info=True)
        else:
            logger.debug("No valid parent directories found in file paths")

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

    # Extract and add repository context
    repo_context = extract_repository_context(diff)
    logger.debug(f"Extracted repository context: {repo_context}")
    if repo_context.strip():
        # Replace the entire repository_context section with the context
        template = re.sub(
            r"<repository_context>.*?</repository_context>",
            f"<repository_context>\n{repo_context}\n</repository_context>",
            template,
            flags=re.DOTALL,
        )
        logger.debug(f"Added repository context ({len(repo_context)} characters)")
    else:
        # Remove the repository_context section if no context was found
        template = re.sub(r"<repository_context>.*?</repository_context>\n*", "", template, flags=re.DOTALL)
        logger.debug("No repository context could be extracted")

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
    message = re.sub(r"\n{3,}", "\n\n", message)

    # Ensure we don't have any trailing/leading whitespace
    return message.strip()
