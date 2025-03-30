"""Code formatting utilities for various file types.

This module provides functions to format files using various formatters:
- Python: black and isort
- JavaScript/TypeScript: prettier
- Markdown/HTML/CSS/JSON/YAML: prettier
- Rust: rustfmt
- Go: gofmt

It includes functions to format individual files or all staged files of supported types.
"""

import logging
from typing import List, Tuple

from gac.git import get_staged_files, stage_files
from gac.utils import run_subprocess

logger = logging.getLogger(__name__)


def run_black(python_files: List[str] = None) -> bool:
    """
    Run black code formatter on the specified Python files or all staged Python files.

    Args:
        python_files: List of Python files to format. If None, all staged Python files will be used.

    Returns:
        True if files were formatted, False otherwise
    """
    if python_files is None:
        logger.debug("Identifying Python files for formatting with black...")
        python_files = get_staged_files(file_type=".py", existing_only=True)

    if not python_files:
        logger.info("No existing Python files to format with black.")
        return False

    try:
        run_subprocess(["black"] + python_files)
        logger.info(f"Black formatted {len(python_files)} files.")
        return True
    except Exception as e:
        logger.error(f"Error running black: {e}")
        return False


def run_isort(python_files: List[str] = None) -> bool:
    """
    Run isort import sorter on the specified Python files or all staged Python files.

    Args:
        python_files: List of Python files to format. If None, all staged Python files will be used.

    Returns:
        True if files were formatted, False otherwise
    """
    if python_files is None:
        logger.debug("Identifying Python files for import sorting with isort...")
        python_files = get_staged_files(file_type=".py", existing_only=True)

    if not python_files:
        logger.info("No existing Python files to sort imports with isort.")
        return False

    try:
        run_subprocess(["isort"] + python_files)
        logger.info(f"Isort sorted imports in {len(python_files)} files.")
        return True
    except Exception as e:
        logger.error(f"Error running isort: {e}")
        return False


def run_prettier(file_patterns: List[str] = None, files: List[str] = None) -> bool:
    """
    Run prettier formatter on the specified files or all staged files matching the patterns.

    Args:
        file_patterns: List of file extensions/patterns to match (e.g., [".js", ".ts"]).
                      If None, common prettier patterns are used.
        files: List of specific files to format.
               If None, all staged files matching patterns will be used.

    Returns:
        True if files were formatted, False otherwise
    """
    if file_patterns is None:
        # Default patterns that prettier can handle
        file_patterns = [
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".md",
            ".html",
            ".css",
            ".json",
            ".yaml",
            ".yml",
        ]

    if files is None:
        logger.debug(f"Identifying files for formatting with prettier: {file_patterns}...")
        files = []
        for pattern in file_patterns:
            files.extend(get_staged_files(file_type=pattern, existing_only=True))

    if not files:
        logger.info("No existing files to format with prettier.")
        return False

    try:
        run_subprocess(["prettier", "--write"] + files)
        logger.info(f"Prettier formatted {len(files)} files.")
        return True
    except Exception as e:
        logger.error(f"Error running prettier: {e}")
        return False


def run_rustfmt(rust_files: List[str] = None) -> bool:
    """
    Run rustfmt on the specified Rust files or all staged Rust files.

    Args:
        rust_files: List of Rust files to format. If None, all staged Rust files will be used.

    Returns:
        True if files were formatted, False otherwise
    """
    if rust_files is None:
        logger.debug("Identifying Rust files for formatting with rustfmt...")
        rust_files = get_staged_files(file_type=".rs", existing_only=True)

    if not rust_files:
        logger.info("No existing Rust files to format with rustfmt.")
        return False

    try:
        run_subprocess(["rustfmt"] + rust_files)
        logger.info(f"Rustfmt formatted {len(rust_files)} files.")
        return True
    except Exception as e:
        logger.error(f"Error running rustfmt: {e}")
        return False


def run_gofmt(go_files: List[str] = None) -> bool:
    """
    Run gofmt on the specified Go files or all staged Go files.

    Args:
        go_files: List of Go files to format. If None, all staged Go files will be used.

    Returns:
        True if files were formatted, False otherwise
    """
    if go_files is None:
        logger.debug("Identifying Go files for formatting with gofmt...")
        go_files = get_staged_files(file_type=".go", existing_only=True)

    if not go_files:
        logger.info("No existing Go files to format with gofmt.")
        return False

    try:
        # gofmt -w writes changes to the file
        run_subprocess(["gofmt", "-w"] + go_files)
        logger.info(f"Gofmt formatted {len(go_files)} files.")
        return True
    except Exception as e:
        logger.error(f"Error running gofmt: {e}")
        return False


def format_staged_files(stage_after_format: bool = True) -> Tuple[bool, List[str]]:
    """
    Format all staged files using appropriate formatters.

    This function detects file types and runs the appropriate formatters on them,
    and optionally re-stages the formatted files.

    Args:
        stage_after_format: Whether to re-stage the formatted files.

    Returns:
        Tuple containing:
        - True if any files were formatted, False otherwise
        - List of formatted file extensions
    """
    logger.debug("Running code formatters on staged files...")

    # Get all staged files first to avoid multiple git calls
    all_staged_files = get_staged_files(existing_only=True)
    if not all_staged_files:
        logger.info("No existing files to format.")
        return False, []

    # Track formatted file types
    formatted_exts = []

    # Categorize files by extension
    python_files = []
    js_ts_files = []
    md_html_css_json_yaml_files = []
    rust_files = []
    go_files = []

    js_ts_extensions = [".js", ".jsx", ".ts", ".tsx"]
    md_html_css_json_yaml_extensions = [".md", ".html", ".css", ".json", ".yaml", ".yml"]

    for file in all_staged_files:
        ext = "." + file.split(".")[-1].lower() if "." in file else ""
        if ext == ".py":
            python_files.append(file)
        elif ext in js_ts_extensions:
            js_ts_files.append(file)
        elif ext in md_html_css_json_yaml_extensions:
            md_html_css_json_yaml_files.append(file)
        elif ext == ".rs":
            rust_files.append(file)
        elif ext == ".go":
            go_files.append(file)

    # Run formatters only if files exist
    any_formatted = False

    if python_files:
        black_result = run_black(python_files)
        isort_result = run_isort(python_files)
        if black_result or isort_result:
            any_formatted = True
            formatted_exts.append(".py")
            logger.info(f"Formatted {len(python_files)} Python files")

    if js_ts_files:
        if run_prettier(files=js_ts_files):
            any_formatted = True
            for ext in js_ts_extensions:
                if any(f.endswith(ext) for f in js_ts_files):
                    formatted_exts.append(ext)
            logger.info(f"Formatted {len(js_ts_files)} JavaScript/TypeScript files")

    if md_html_css_json_yaml_files:
        if run_prettier(files=md_html_css_json_yaml_files):
            any_formatted = True
            for ext in md_html_css_json_yaml_extensions:
                if any(f.endswith(ext) for f in md_html_css_json_yaml_files):
                    formatted_exts.append(ext)
            logger.info(
                f"Formatted {len(md_html_css_json_yaml_files)} Markdown/HTML/CSS/JSON/YAML files"
            )

    if rust_files:
        if run_rustfmt(rust_files):
            any_formatted = True
            formatted_exts.append(".rs")
            logger.info(f"Formatted {len(rust_files)} Rust files")

    if go_files:
        if run_gofmt(go_files):
            any_formatted = True
            formatted_exts.append(".go")
            logger.info(f"Formatted {len(go_files)} Go files")

    # Re-stage files if required
    if stage_after_format and any_formatted:
        logger.debug("Re-staging formatted files after formatting...")
        # Directly use the files we already know were formatted
        formatted_files = []
        formatted_files.extend(python_files if ".py" in formatted_exts else [])
        formatted_files.extend(
            js_ts_files if any(ext in formatted_exts for ext in js_ts_extensions) else []
        )
        formatted_files.extend(
            md_html_css_json_yaml_files
            if any(ext in formatted_exts for ext in md_html_css_json_yaml_extensions)
            else []
        )
        formatted_files.extend(rust_files if ".rs" in formatted_exts else [])
        formatted_files.extend(go_files if ".go" in formatted_exts else [])

        if formatted_files:
            stage_files(formatted_files)
            logger.info(f"Re-staged {len(formatted_files)} files after formatting.")

    return any_formatted, formatted_exts
