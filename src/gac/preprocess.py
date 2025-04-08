#!/usr/bin/env python3
"""Preprocessing utilities for git diffs."""

import logging
import re

logger = logging.getLogger(__name__)

BINARY_FILE_PATTERNS = [r"Binary files .* differ", r"GIT binary patch"]

MINIFIED_FILE_EXTENSIONS = [
    ".min.js",
    ".min.css",
    ".bundle.js",
    ".bundle.css",
    ".compressed.js",
    ".compressed.css",
    ".opt.js",
    ".opt.css",
]

BUILD_DIRECTORIES = [
    "/dist/",
    "/build/",
    "/vendor/",
    "/node_modules/",
    "/assets/vendor/",
    "/public/build/",
    "/static/dist/",
]


def preprocess_diff(diff: str) -> str:
    """Preprocess a git diff to make it more suitable for AI analysis."""
    filtered_diff = filter_binary_and_minified(diff)

    # TODO: Add more preprocessing steps as needed
    # - Truncate very large diffs
    # - Summarize large file changes
    # - Focus on important structural changes

    return filtered_diff


def is_minified_content(content: str) -> bool:
    """Check if a file's content appears to be minified based on heuristics."""
    if not content:
        return False

    lines = content.split("\n")
    if not lines:
        return False

    # If file has few lines but is large, it's likely minified
    if len(lines) < 10 and len(content) > 1000:
        return True

    # Check for very long lines (typical in minified files)
    long_lines_count = sum(1 for line in lines if len(line) > 500)

    # If more than 20% of lines are very long, consider it minified
    if long_lines_count > 0 and (long_lines_count / len(lines)) > 0.2:
        return True

    return False


def filter_binary_and_minified(diff: str) -> str:
    """Filter out binary and minified files from a git diff."""
    if not diff:
        return diff

    # Split the diff into file sections
    # Git diff format starts each file with "diff --git"
    file_sections = re.split(r"(diff --git )", diff)

    # Recombine the split sections with their headers
    if file_sections[0] == "":
        file_sections.pop(0)

    sections = []
    i = 0
    while i < len(file_sections):
        if file_sections[i] == "diff --git " and i + 1 < len(file_sections):
            sections.append(file_sections[i] + file_sections[i + 1])
            i += 2
        else:
            sections.append(file_sections[i])
            i += 1

    # Filter out binary files
    filtered_sections = []
    for section in sections:
        # Skip binary files
        if any(re.search(pattern, section) for pattern in BINARY_FILE_PATTERNS):
            file_match = re.search(r"diff --git a/(.*) b/", section)
            if file_match:
                filename = file_match.group(1)
                logger.info(f"Filtered out binary file: {filename}")
            continue

        # Check for minified file extensions
        file_match = re.search(r"diff --git a/(.*) b/", section)
        if file_match:
            filename = file_match.group(1)

            # Skip files with minified extensions
            if any(filename.endswith(ext) for ext in MINIFIED_FILE_EXTENSIONS):
                logger.info(f"Filtered out minified file by extension: {filename}")
                continue

            # Skip files in build directories
            if any(directory in filename for directory in BUILD_DIRECTORIES):
                logger.info(f"Filtered out file in build directory: {filename}")
                continue

            # Check file content for minification
            # We'll look for the content in the diff itself, though this is imperfect
            # because we're only seeing the changes, not the whole file.
            if is_minified_content(section):
                logger.info(f"Filtered out likely minified file by content: {filename}")
                continue

        filtered_sections.append(section)

    return "".join(filtered_sections)
