"""Code formatting module for GAC."""

import logging
import os
import subprocess
import sys
from typing import Dict, List

logger = logging.getLogger(__name__)


FORMATTERS = {
    "python": [
        {
            "name": "black",
            "command": ["black"],
            "extensions": [".py"],
        },
        {
            "name": "isort",
            "command": ["isort"],
            "extensions": [".py"],
        },
    ],
    "javascript": [
        {
            "name": "prettier",
            "command": ["prettier", "--write"],
            "extensions": [".js", ".jsx", ".ts", ".tsx", ".json", ".md", ".html", ".css"],
            "check_command": ["prettier", "--version"],
        },
    ],
    "rust": [
        {
            "name": "rustfmt",
            "command": ["rustfmt"],
            "extensions": [".rs"],
        },
    ],
    "go": [
        {
            "name": "gofmt",
            "command": ["gofmt", "-w"],
            "extensions": [".go"],
            "single_file": True,  # gofmt processes one file at a time
        },
    ],
}


def run_formatter(command: List[str], files: List[str], formatter_name: str) -> bool:
    """Run a formatter on the specified files.

    Args:
        command: Command to run the formatter
        files: List of file paths to format
        formatter_name: Name of the formatter

    Returns:
        bool: True if formatting was successful, False otherwise
    """
    if not files:
        return False

    try:
        logger.debug(f"Running {formatter_name} on {len(files)} files")

        # Some formatters like gofmt need to process files one at a time
        formatter_config = next((f for lang in FORMATTERS.values() for f in lang if f["name"] == formatter_name), None)
        if formatter_config and formatter_config.get("single_file", False):
            for file in files:
                result = subprocess.run(
                    command + [file],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode != 0:
                    logger.warning(f"{formatter_name} failed on {file}: {result.stderr.strip()}")
                    return False
            return True
        else:
            # Most formatters can handle multiple files at once
            result = subprocess.run(
                command + files,
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                logger.warning(f"{formatter_name} failed: {result.stderr.strip()}")
                return False
            return True
    except Exception as e:
        logger.error(f"Error running {formatter_name}: {e}")
        return False


def check_formatter_available(formatter_config: Dict) -> bool:
    """Check if a formatter is available on the system."""
    check_command = formatter_config.get("check_command", formatter_config["command"][:1] + ["--version"])

    try:
        result = subprocess.run(
            check_command,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0
    except Exception:
        return False


def format_files(files: List[str], dry_run: bool = False) -> List[str]:
    """Format the given files using available formatters.

    Detects appropriate formatters based on file extensions and runs them.

    Args:
        files: List of file paths to format
        dry_run: If True, returns what would be formatted without making changes

    Returns:
        List of successfully formatted file paths
    """
    if not files:
        return []

    files_to_format = []
    for file in files:
        if not os.path.exists(file):
            logger.warning(f"File {file} does not exist. Skipping.")
        else:
            files_to_format.append(file)

    grouped_by_ext = {}
    for file_path in files_to_format:
        _, ext = os.path.splitext(file_path)
        if ext not in grouped_by_ext:
            grouped_by_ext[ext] = []
        grouped_by_ext[ext].append(file_path)

    formatted_files = []
    for ext, ext_files in grouped_by_ext.items():
        for _, formatters in FORMATTERS.items():
            for formatter in formatters:
                if ext in formatter["extensions"]:
                    if check_formatter_available(formatter):
                        if dry_run:
                            for file in ext_files:
                                if file not in formatted_files:
                                    formatted_files.append(file)
                        else:
                            success = run_formatter(formatter["command"], ext_files, formatter["name"])
                            if success:
                                for file in ext_files:
                                    if file not in formatted_files:
                                        formatted_files.append(file)

    return formatted_files


def format_code(code: str) -> str:
    """Format code string using black."""
    result = subprocess.run(
        ["black", "-", "-q"],
        input=code.encode(),
        capture_output=True,
    )
    return result.stdout.decode()


def validate_format(code: str) -> None:
    """Validate code formatting using black."""
    result = subprocess.run(
        ["black", "-", "-q", "--check"],
        input=code.encode(),
        capture_output=True,
    )
    if result.returncode != 0:
        raise ValueError("Invalid formatting")


def main():
    """Main entry point for the formatter."""
    if len(sys.argv) < 2:
        logger.error("Usage: python -m gac.format file1 file2 ...")
        sys.exit(1)

    files = sys.argv[1:]
    result = format_files(files)

    if result:
        logger.info(f"Formatted {len(result)} files:")
        for file in result:
            logger.info(f"  - {file}")
    else:
        logger.info("No files were formatted.")


if __name__ == "__main__":
    main()
