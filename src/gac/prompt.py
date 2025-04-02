"""Prompt creation for GAC."""

import logging
import os
import re
from pathlib import Path

from gac.errors import ConfigError

logger = logging.getLogger(__name__)

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
</git-diff>"""


def find_template_file():
    """Find a prompt template file in standard locations."""
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


def load_prompt_template(template_path=None):
    """Load the prompt template from a file or use the default embedded template."""
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

    logger.debug("Using embedded default template")
    return DEFAULT_TEMPLATE


def build_prompt(status, diff, one_liner=False, hint="", template_path=None):
    """Build a prompt using a template file with XML-style tags."""
    template = load_prompt_template(template_path)

    template = template.replace("<status></status>", status)
    template = template.replace("<diff></diff>", diff)
    template = template.replace("<hint></hint>", hint)

    if one_liner:
        template = re.sub(r"<multi_line>.*?</multi_line>", "", template, flags=re.DOTALL)
        template = re.sub(r"<one_liner>(.*?)</one_liner>", r"\1", template, flags=re.DOTALL)
    else:
        template = re.sub(r"<one_liner>.*?</one_liner>", "", template, flags=re.DOTALL)
        template = re.sub(r"<multi_line>(.*?)</multi_line>", r"\1", template, flags=re.DOTALL)

    if not hint:
        template = re.sub(r"<hint_section>.*?</hint_section>", "", template, flags=re.DOTALL)
    else:
        template = re.sub(r"<hint_section>(.*?)</hint_section>", r"\1", template, flags=re.DOTALL)

    template = re.sub(r"<[^>]*>", "", template)
    template = re.sub(r"\n{3,}", "\n\n", template)

    return template.strip()


def clean_commit_message(message: str) -> str:
    """Clean up a commit message generated by an AI model."""
    message = message.strip()

    if message.startswith("```"):
        message = message[3:].lstrip()

    if message.endswith("```"):
        message = message[:-3].rstrip()

    if message.startswith("```") and "\n" in message:
        parts = message.split("\n", 1)
        if len(parts) > 1:
            message = parts[1].lstrip()

    for tag in ["<git-status>", "</git-status>", "<git-diff>", "</git-diff>"]:
        message = message.replace(tag, "")

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
    """Create an abbreviated version of the prompt by limiting the diff lines."""
    lines = prompt.split("\n")
    result = []

    in_diff_section = False
    diff_line_count = 0
    diff_lines_included = 0

    for line in lines:
        if "<git-diff>" in line:
            in_diff_section = True
            result.append(line)
        elif "</git-diff>" in line:
            in_diff_section = False
            if diff_line_count > max_diff_lines:
                result.append(
                    f"... [{diff_line_count - diff_lines_included} more lines truncated] ..."
                )
            result.append(line)
        elif in_diff_section:
            diff_line_count += 1
            if diff_line_count <= max_diff_lines:
                result.append(line)
                diff_lines_included += 1
        else:
            result.append(line)

    return "\n".join(result)
