"""Code formatting module for GAC."""

import logging
import os
import subprocess
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
    """Run a formatter on the specified files."""
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


def format_files(files) -> Dict[str, List[str]]:
    """Format the given files."""
    if not files:
        return {}

    # Convert files to dictionary format if it's a list
    files_dict = {}
    if isinstance(files, list):
        for file in files:
            files_dict[file] = "M"  # Assume modified
    else:
        files_dict = files  # Already a dictionary

    # Group files by extension for appropriate formatter selection
    grouped_by_ext = {}
    for file_path, status in files_dict.items():
        if status == "D":  # Skip deleted files
            continue

        # Get file extension
        _, ext = os.path.splitext(file_path)
        if ext not in grouped_by_ext:
            grouped_by_ext[ext] = []
        grouped_by_ext[ext].append(file_path)

    # Apply appropriate formatters based on file extensions
    formatted_files = {}

    for ext, ext_files in grouped_by_ext.items():
        # Find all formatters that handle this extension
        for lang, formatters in FORMATTERS.items():
            for formatter in formatters:
                if ext in formatter["extensions"]:
                    # Check if formatter is available
                    if check_formatter_available(formatter):
                        # Format the files
                        success = run_formatter(formatter["command"], ext_files, formatter["name"])
                        if success:
                            if formatter["name"] not in formatted_files:
                                formatted_files[formatter["name"]] = []
                            formatted_files[formatter["name"]].extend(ext_files)

    return formatted_files


if __name__ == "__main__":
    # Simple command-line interface for manual testing
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m gac.format file1 file2 ...")
        sys.exit(1)

    files_to_format = sys.argv[1:]
    result = format_files(files_to_format)

    if result:
        print(f"Formatted {sum(len(f) for f in result.values())} files:")
        for formatter, formatted in result.items():
            print(f"  - {formatter}: {formatted}")
    else:
        print("No files were formatted.")
