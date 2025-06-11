# flake8: noqa: E501
"""Prompt creation for gac.

This module handles the creation of prompts for AI models, including template loading,
formatting, and integration with diff preprocessing.
"""

import logging
import os
import re
from typing import Optional

logger = logging.getLogger(__name__)

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

<conventions_no_scope>
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

Select ONE prefix that best matches the primary purpose of the changes.
If multiple prefixes apply, choose the one that represents the most significant change.
If you cannot confidently determine a type, use 'chore'.

Do NOT include a scope in your commit prefix.
</conventions_no_scope>

<conventions_scope_provided>
You MUST write a conventional commit message with EXACTLY ONE type and the REQUIRED scope '{scope}'.

FORMAT: type({scope}): description

Select ONE type from this list that best matches the primary purpose of the changes:
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

Select ONE type from this list that best matches the primary purpose of the changes:
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

You MUST infer an appropriate scope from the changes. A good scope is concise (usually one word) and indicates the component or area that was changed.
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

<readme_summary>
<summary></summary>
</readme_summary>

<git_status>
<status></status>
</git_status>

<git_diff_stat>
<diff_stat></diff_stat>
</git_diff_stat>

<git_diff>
<diff></diff>
</git_diff>

<instructions>
IMMEDIATELY AFTER ANALYZING THE CHANGES, RESPOND WITH ONLY THE COMMIT MESSAGE.
DO NOT include any preamble, reasoning, explanations or anything other than the commit message itself.
DO NOT use markdown formatting, headers, or code blocks.
The entire response will be passed directly to 'git commit -m'.
</instructions>"""


def build_prompt(
    status: str,
    processed_diff: str,
    diff_stat: str = "",
    one_liner: bool = False,
    hint: str = "",
    scope: Optional[str] = None,
    repo_path: Optional[str] = None,
) -> str:
    """Build a prompt for the AI model from git and repo information.

    Args:
        status: Git status output
        processed_diff: Git diff output, already preprocessed
        diff_stat: Git diff stat output showing file changes summary
        one_liner: Whether to request a one-line commit message
        hint: Optional hint to guide the AI
        scope: None = no scope, "infer" = infer scope, any other string = use as scope
        repo_path: Optional path to repository root for README detection
    """
    template = load_prompt_template()

    try:
        logger.debug(f"Processing scope parameter: {scope}")
        if scope is None:
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
            logger.debug(f"Using inferred-scope conventions (scope={scope})")
            template = re.sub(
                r"<conventions_scope_provided>.*?</conventions_scope_provided>\n", "", template, flags=re.DOTALL
            )
            template = re.sub(r"<conventions_no_scope>.*?</conventions_no_scope>\n", "", template, flags=re.DOTALL)
            template = template.replace("<conventions_scope_inferred>", "<conventions>")
            template = template.replace("</conventions_scope_inferred>", "</conventions>")
        else:
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

    readme_summary = ""
    if repo_path:
        readme_files = [
            "README.md",
            "README.rst",
            "README.txt",
            "README",
            "readme.md",
            "readme.rst",
            "readme.txt",
            "readme",
        ]
        for readme_name in readme_files:
            readme_path = os.path.join(repo_path, readme_name)
            if os.path.exists(readme_path):
                readme_summary = summarize_readme_with_nlp(readme_path)
                break

    if readme_summary:
        template = template.replace("<summary></summary>", readme_summary)
        logger.debug(f"Added README summary ({len(readme_summary)} characters)")
    else:
        template = re.sub(r"<readme_summary>.*?</readme_summary>\n?", "", template, flags=re.DOTALL)
        logger.debug("No README summary available - section removed")

    if hint:
        template = template.replace("<hint_text></hint_text>", hint)
        logger.debug(f"Added hint ({len(hint)} characters)")
    else:
        template = re.sub(r"<hint>.*?</hint>", "", template, flags=re.DOTALL)
        logger.debug("No hint provided")

    if one_liner:
        template = re.sub(r"<multi_line>.*?</multi_line>", "", template, flags=re.DOTALL)
    else:
        template = re.sub(r"<one_liner>.*?</one_liner>", "", template, flags=re.DOTALL)

    template = re.sub(r"\n(?:[ \t]*\n){2,}", "\n\n", template)
    template = template.replace("<diff></diff>", processed_diff)

    return template.strip()


def clean_commit_message(message: str) -> str:
    """Clean up AI-generated commit message for git usage.

    Removes preambles, code blocks, XML tags, and ensures proper
    conventional commit format. Fixes double prefix issues.
    """
    message = message.strip()

    message = re.sub(r"```[\w]*\n|```", "", message)
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
            message = message.split(indicator, 1)[1].strip()
            break

    lines = message.split("\n")
    for i, line in enumerate(lines):
        if any(
            line.strip().startswith(prefix)
            for prefix in ["feat:", "fix:", "docs:", "style:", "refactor:", "perf:", "test:", "build:", "ci:", "chore:"]
        ):
            message = "\n".join(lines[i:])
            break

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

    double_prefix_pattern = re.compile(
        r"^(" + r"|\s*".join(conventional_prefixes) + r"):\s*(" + r"|\s*".join(conventional_prefixes) + r")\(([^)]+)\):"
    )
    match = double_prefix_pattern.match(message)

    if match:
        second_type = match.group(2)
        scope = match.group(3)
        description = message[match.end() :].strip()
        message = f"{second_type}({scope}): {description}"

    if not any(
        message.strip().startswith(prefix + ":") or message.strip().startswith(prefix + "(")
        for prefix in conventional_prefixes
    ):
        message = f"chore: {message.strip()}"

    message = re.sub(r"\n(?:[ \t]*\n){2,}", "\n\n", message).strip()

    return message


def load_prompt_template() -> str:
    """Load the prompt template."""
    logger.debug("Using default template")
    return DEFAULT_TEMPLATE


def summarize_readme_with_nlp(readme_path: str) -> str:
    """Summarize README using NLP extractive summarization.

    Uses sumy library with LSA algorithm to extract 3 key sentences.
    Returns empty string if file not found or on error.
    """
    try:
        from sumy.nlp.stemmers import Stemmer
        from sumy.nlp.tokenizers import Tokenizer
        from sumy.parsers.plaintext import PlaintextParser
        from sumy.summarizers.lsa import LsaSummarizer
        from sumy.utils import get_stop_words

        if not os.path.exists(readme_path):
            logger.debug(f"README file not found at {readme_path}")
            return ""

        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        if not content.strip():
            logger.debug("README file is empty")
            return ""

        parser = PlaintextParser.from_string(content, Tokenizer("english"))
        stemmer = Stemmer("english")
        summarizer = LsaSummarizer(stemmer)
        summarizer.stop_words = get_stop_words("english")

        sentences = summarizer(parser.document, 3)
        summary_text = " ".join(str(sentence) for sentence in sentences)

        logger.debug(f"Generated README summary ({len(summary_text)} chars)")
        return summary_text.strip()

    except ImportError:
        logger.warning("sumy library not available - install with: pip install sumy")
        return ""
    except Exception as e:
        logger.warning(f"Error summarizing README: {e}")
        return ""
