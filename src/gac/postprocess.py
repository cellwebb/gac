"""Post-processing for AI-generated commit messages.

This module handles cleaning and normalization of commit messages generated
by AI models, removing artifacts like think tags, code blocks, and XML tags.
"""

import re

from gac.constants import CommitMessageConstants

# Pattern matching think content tags.
# Used by extract_think_tag_text() for token estimation.
# _remove_think_tags() uses its own inline patterns because its removal
# logic is more complex (handles unclosed tags, partial tags at start/end, etc.).
_THINK_TAG_RE = re.compile(r"<(think|thinking)>(.*?)</\1>", re.DOTALL | re.IGNORECASE)


def extract_think_tag_text(content: str) -> str:
    """Extract the text content from all <think> and <thinking> tags.

    Some models (e.g. DeepSeek-R1, Qwen-QWQ) embed their reasoning inside
    ``<think>`` tags within the main response content rather than reporting
    it via separate API thinking blocks.  This function extracts that text
    so it can be used for reasoning token estimation before the tags are
    stripped during post-processing.

    Args:
        content: The raw response content that may contain ``<think>`` or ``<thinking>`` tags.

    Returns:
        The concatenated text from all ``<think>`` blocks, or an empty string
        if none are found.
    """
    matches = [m.group(2) for m in _THINK_TAG_RE.finditer(content)]
    return "\n".join(matches) if matches else ""


def _remove_think_tags(message: str) -> str:
    """Remove AI reasoning tags and their content from the message.

    Handles both <think>...</think> and <thinking>...</thinking> variants.

    Args:
        message: The message to clean

    Returns:
        Message with reasoning tags removed
    """
    # Tag alternation pattern for both think and thinking variants
    _tag = r"(?:think|thinking)"

    message = re.sub(
        rf"<{_tag}>(?:(?!</{_tag}>)[^\n])*\n.*?</{_tag}>\s*",
        "",
        message,
        flags=re.DOTALL | re.IGNORECASE,
    )

    message = re.sub(
        rf"\n\n+\s*<{_tag}>.*?</{_tag}>\s*",
        "",
        message,
        flags=re.DOTALL | re.IGNORECASE,
    )
    message = re.sub(
        rf"<{_tag}>.*?</{_tag}>\s*\n\n+",
        "",
        message,
        flags=re.DOTALL | re.IGNORECASE,
    )

    message = re.sub(
        rf"<{_tag}>\s*\n.*$",
        "",
        message,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # Multi-line tag block preceded by a single newline
    # (e.g., after removing a prior block above).
    # The \n inside the tag content ensures we only match actual reasoning
    # blocks, not inline mentions of the tag names in commit text.
    message = re.sub(
        rf"\n\s*<{_tag}>[^<]*\n.*?</{_tag}>\s*",
        "\n",
        message,
        flags=re.DOTALL | re.IGNORECASE,
    )
    # Multi-line tag block followed by a single newline
    message = re.sub(
        rf"<{_tag}>[^<]*\n.*?</{_tag}>\s*\n",
        "",
        message,
        flags=re.DOTALL | re.IGNORECASE,
    )
    # Standalone multi-line tag block at start of message (after prior subs)
    message = re.sub(
        rf"^\s*<{_tag}>[^<]*\n.*?</{_tag}>\s*",
        "",
        message,
        flags=re.DOTALL | re.IGNORECASE,
    )

    conventional_prefixes_pattern = r"(" + "|".join(CommitMessageConstants.CONVENTIONAL_PREFIXES) + r")[\(:)]"
    if re.search(rf"^.*?</{_tag}>", message, flags=re.DOTALL | re.IGNORECASE):
        prefix_match = re.search(conventional_prefixes_pattern, message, flags=re.IGNORECASE)
        think_match = re.search(rf"</{_tag}>", message, flags=re.IGNORECASE)

        if not prefix_match or (think_match and think_match.start() < prefix_match.start()):
            message = re.sub(
                rf"^.*?</{_tag}>\s*",
                "",
                message,
                flags=re.DOTALL | re.IGNORECASE,
            )

    message = re.sub(rf"</{_tag}>\s*$", "", message, flags=re.IGNORECASE)

    return message


def _remove_code_blocks(message: str) -> str:
    """Remove markdown code blocks from the message.

    Args:
        message: The message to clean

    Returns:
        Message with code blocks removed
    """
    return re.sub(r"```[\w]*\n|```", "", message)


def _extract_commit_from_reasoning(message: str) -> str:
    """Extract the actual commit message from reasoning/preamble text.

    Args:
        message: The message potentially containing reasoning

    Returns:
        Extracted commit message
    """
    for indicator in CommitMessageConstants.COMMIT_INDICATORS:
        if indicator.lower() in message.lower():
            message = message.split(indicator, 1)[1].strip()
            break

    lines = message.split("\n")
    for i, line in enumerate(lines):
        if any(line.strip().startswith(f"{prefix}:") for prefix in CommitMessageConstants.CONVENTIONAL_PREFIXES):
            message = "\n".join(lines[i:])
            break

    return message


def _remove_xml_tags(message: str) -> str:
    """Remove XML tags that might have leaked into the message.

    Args:
        message: The message to clean

    Returns:
        Message with XML tags removed
    """
    for tag in CommitMessageConstants.XML_TAGS_TO_REMOVE:
        message = message.replace(tag, "")
    return message


def _fix_double_prefix(message: str) -> str:
    """Fix double type prefix issues like 'chore: feat(scope):' to 'feat(scope):'.

    Args:
        message: The message to fix

    Returns:
        Message with double prefix corrected
    """
    double_prefix_pattern = re.compile(
        r"^("
        + r"|\s*".join(CommitMessageConstants.CONVENTIONAL_PREFIXES)
        + r"):\s*("
        + r"|\s*".join(CommitMessageConstants.CONVENTIONAL_PREFIXES)
        + r")\(([^)]+)\):"
    )
    match = double_prefix_pattern.match(message)

    if match:
        second_type = match.group(2)
        scope = match.group(3)
        description = message[match.end() :].strip()
        message = f"{second_type}({scope}): {description}"

    return message


def _normalize_whitespace(message: str) -> str:
    """Normalize whitespace, ensuring no more than one blank line between paragraphs.

    Args:
        message: The message to normalize

    Returns:
        Message with normalized whitespace
    """
    return re.sub(r"\n(?:[ \t]*\n){2,}", "\n\n", message).strip()


def _truncate_at_word_boundary(text: str, max_len: int, suffix: str = "...") -> str:
    """Truncate text at a word boundary, not mid-word.

    Args:
        text: The text to truncate
        max_len: Maximum length including suffix
        suffix: The suffix to add when truncating (default: "...")

    Returns:
        Truncated text with suffix if needed
    """
    if len(text) <= max_len:
        return text

    # Account for suffix length
    available = max_len - len(suffix)
    if available < 1:
        return text[:max_len]

    # Find the last space before the cutoff
    truncated = text[:available]
    last_space = truncated.rfind(" ")

    # Only break at word boundary if it gives us a reasonable chunk
    # (at least 50% of available space, otherwise hard truncate)
    if last_space > available * 0.5:
        return text[:last_space] + suffix
    else:
        return truncated + suffix


def enforce_fifty_seventy_two(message: str) -> str:
    """Enforce the 50/72 rule on a commit message.

    The 50/72 rule states:
    - First line (subject): max 50 characters
    - Line 2: blank
    - Body lines: max 72 characters per line

    This function wraps long lines and ensures the format is correct.

    Args:
        message: The commit message to process

    Returns:
        Commit message with 50/72 rule enforced
    """
    lines = message.split("\n")
    if not lines:
        return message

    # Handle subject line (first line) - truncate to 50 chars at word boundary
    subject = lines[0]
    if len(subject) > 50:
        # Check for conventional commit prefix: type(scope): description
        prefix_match = re.match(r"^([\w]+(?:\([^)]+\))?: )(.+)$", subject)
        if prefix_match:
            prefix = prefix_match.group(1)
            description = prefix_match.group(2)
            available = 50 - len(prefix)
            if available > 10:  # Only truncate if we have reasonable space
                subject = prefix + _truncate_at_word_boundary(description, available)
            else:
                # Prefix is too long, truncate whole thing
                subject = _truncate_at_word_boundary(subject, 50)
        else:
            # No prefix, truncate at word boundary
            subject = _truncate_at_word_boundary(subject, 50)
    lines[0] = subject

    # Ensure blank line after subject
    if len(lines) > 1 and lines[1].strip():
        lines.insert(1, "")

    # Wrap body lines to 72 characters
    wrapped_lines = [lines[0], ""] if len(lines) > 1 else [lines[0]]

    for line in lines[2:]:
        if len(line) <= 72:
            wrapped_lines.append(line)
        else:
            # Wrap this line to 72 chars
            # Try to break at word boundaries
            words = line.split(" ")
            current_line = ""
            for word in words:
                if len(current_line) + len(word) + 1 <= 72:
                    current_line = f"{current_line} {word}".strip() if current_line else word
                else:
                    if current_line:
                        wrapped_lines.append(current_line)
                    current_line = word
            if current_line:
                wrapped_lines.append(current_line)

    return "\n".join(wrapped_lines)


def clean_commit_message(message: str, fifty_seventy_two: bool = False) -> str:
    """Clean up a commit message generated by an AI model.

    This function:
    1. Removes any preamble or reasoning text
    2. Removes code block markers and formatting
    3. Removes XML tags that might have leaked into the response
    4. Fixes double type prefix issues (e.g., "chore: feat(scope):")
    5. Normalizes whitespace
    6. Enforces 50/72 rule if requested

    Args:
        message: Raw commit message from AI
        fifty_seventy_two: Whether to enforce the 50/72 rule

    Returns:
        Cleaned commit message ready for use
    """
    message = message.strip()
    message = _remove_think_tags(message)
    message = _remove_code_blocks(message)
    message = _extract_commit_from_reasoning(message)
    message = _remove_xml_tags(message)
    message = _fix_double_prefix(message)
    message = _normalize_whitespace(message)

    if fifty_seventy_two:
        message = enforce_fifty_seventy_two(message)

    return message
