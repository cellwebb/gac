"""Parse and validate grouped-commit JSON responses from the AI.

This module owns two concerns:

1. **Structural validation** – parsing raw AI output into a well-formed
   ``{"commits": [...]}`` dict with the required keys and types.
2. **File-coverage validation** – checking that the union of files across
   all commits exactly matches the set of staged files.

Both produce ``(is_valid, feedback, detail)`` tuples suitable for
feeding back into the retry loop.
"""

from __future__ import annotations

import json
import logging
from collections import Counter
from typing import Any

logger = logging.getLogger(__name__)


def parse_json_response(raw_response: str) -> dict[str, Any]:
    """Parse a raw AI response into a validated grouped-commits dict.

    Extracts the first ``{…}`` block from the response, parses it as
    JSON, and validates the required structure.

    Returns:
        Parsed dict with a ``"commits"`` key containing a non-empty list.

    Raises:
        ValueError: If the response is not valid JSON or is structurally
            invalid (missing keys, wrong types, empty lists/messages).
    """
    extract = raw_response
    first_brace = raw_response.find("{")
    last_brace = raw_response.rfind("}")
    if first_brace != -1 and last_brace != -1 and first_brace < last_brace:
        extract = raw_response[first_brace : last_brace + 1]

    try:
        parsed: dict[str, Any] = json.loads(extract)
    except json.JSONDecodeError as e:
        logger.debug(f"JSON parsing failed: {e}. Extract length: {len(extract)}, Response length: {len(raw_response)}")
        raise ValueError("Invalid JSON response") from e

    # Validate structure
    if "commits" not in parsed or not isinstance(parsed["commits"], list):
        raise ValueError("Response missing 'commits' array")
    if len(parsed["commits"]) == 0:
        raise ValueError("No commits in response")
    for idx, commit in enumerate(parsed["commits"]):
        if "files" not in commit or not isinstance(commit["files"], list):
            raise ValueError(f"Commit {idx + 1} missing 'files' array")
        if "message" not in commit or not isinstance(commit["message"], str):
            raise ValueError(f"Commit {idx + 1} missing 'message' string")
        if len(commit["files"]) == 0:
            raise ValueError(f"Commit {idx + 1} has empty files list")
        if not commit["message"].strip():
            raise ValueError(f"Commit {idx + 1} has empty message")

    return parsed


def validate_file_coverage(staged: set[str], grouped_result: Any) -> tuple[bool, str, str]:
    """Validate that grouped commits cover all staged files exactly.

    Args:
        staged: The set of file paths that are staged.
        grouped_result: Parsed JSON response with a ``"commits"`` key.

    Returns:
        A 3-tuple ``(is_valid, feedback, detail)``:

        - **is_valid** – ``True`` when every staged file appears exactly
          once across all commits, and no unexpected files appear.
        - **feedback** – Human-readable feedback string for the AI model
          (empty when valid).
        - **detail** – Short summary of problems (empty when valid).
    """
    if not isinstance(grouped_result, dict):
        return True, "", ""
    commits = grouped_result.get("commits", [])
    if not commits:  # pragma: no cover
        return True, "", ""

    for commit in commits:
        if not isinstance(commit, dict) or "files" not in commit:
            return True, "", ""  # Let structural validation handle it

    all_files: list[str] = []
    for commit in commits:
        files = commit.get("files", [])
        all_files.extend([str(p) for p in files])

    counts = Counter(all_files)
    union_set = set(all_files)

    duplicates = sorted(f for f, c in counts.items() if c > 1)
    missing = sorted(staged - union_set)
    unexpected = sorted(union_set - staged)

    if not duplicates and not missing and not unexpected:
        return True, "", ""

    problems: list[str] = []
    if missing:
        problems.append(f"Missing: {', '.join(missing)}")
    if unexpected:
        problems.append(f"Not staged: {', '.join(unexpected)}")
    if duplicates:
        problems.append(f"Duplicates: {', '.join(duplicates)}")

    feedback = f"{'; '.join(problems)}. Required files: {', '.join(sorted(staged))}. Respond with ONLY valid JSON."
    return False, feedback, "; ".join(problems)
