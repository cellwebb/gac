"""Utility functions for gac."""

import logging
import os
import subprocess
from typing import List, Union

from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme

from gac.errors import GACError


def setup_logging(log_level: Union[int, str] = logging.WARNING, quiet: bool = False, force: bool = False) -> None:
    """Configure logging for the application."""
    if isinstance(log_level, str):
        log_level = getattr(logging, log_level.upper(), logging.WARNING)

    log_level_env = os.environ.get("GAC_LOG_LEVEL")
    if log_level_env:
        log_level_env = log_level_env.upper()
        if log_level_env == "DEBUG":
            log_level = logging.DEBUG
        elif log_level_env == "INFO":
            log_level = logging.INFO
        elif log_level_env == "WARNING":
            log_level = logging.WARNING
        elif log_level_env == "ERROR":
            log_level = logging.ERROR

    if quiet:
        log_level = logging.ERROR

    kwargs = {"force": force} if force else {}

    if log_level == logging.DEBUG:
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            **kwargs,
        )
    else:
        logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s", **kwargs)

    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


theme = Theme(
    {
        "success": "green bold",
        "info": "blue",
        "warning": "yellow",
        "error": "red bold",
        "header": "magenta",
        "notification": "bright_cyan bold",
    }
)
console = Console(theme=theme)
logger = logging.getLogger(__name__)


def print_message(message: str, level: str = "info") -> None:
    """Print a styled message with the specified level."""
    console.print(message, style=level)


def print_header(message: str) -> None:
    """Print a header message with color."""
    console.print(Panel(message, style="header"))


def run_subprocess(
    command: List[str],
    silent: bool = False,
    timeout: int = 60,
    check: bool = True,
    strip_output: bool = True,
    raise_on_error: bool = True,
) -> str:
    """Run a subprocess command safely and return the output.

    Args:
        command: List of command arguments
        silent: If True, suppress debug logging
        timeout: Command timeout in seconds
        check: Whether to check return code (for compatibility)
        strip_output: Whether to strip whitespace from output
        raise_on_error: Whether to raise an exception on error

    Returns:
        Command output as string

    Raises:
        GACError: If the command times out
        subprocess.CalledProcessError: If the command fails and raise_on_error is True
    """
    if not silent:
        logger.debug(f"Running command: {' '.join(command)}")

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            timeout=timeout,
        )

        if result.returncode != 0 and (check or raise_on_error):
            if not silent:
                logger.debug(f"Command stderr: {result.stderr}")

            error = subprocess.CalledProcessError(result.returncode, command, result.stdout, result.stderr)
            raise error

        output = result.stdout
        if strip_output:
            output = output.strip()

        return output
    except subprocess.TimeoutExpired as e:
        logger.error(f"Command timed out after {timeout} seconds: {' '.join(command)}")
        raise GACError(f"Command timed out: {' '.join(command)}") from e
    except subprocess.CalledProcessError as e:
        if not silent:
            logger.error(f"Command failed: {e.stderr.strip() if hasattr(e, 'stderr') else str(e)}")
        if raise_on_error:
            raise
        return ""
    except Exception as e:
        if not silent:
            logger.debug(f"Command error: {e}")
        if raise_on_error:
            raise
        return ""


def is_ollama_available() -> bool:
    """Check if Ollama is available."""
    try:
        import ollama

        _ = ollama.list()
        return True
    except (ImportError, Exception) as e:
        logger.debug(f"Ollama is not available: {str(e)}")
        return False


def file_matches_pattern(file_path: str, pattern: str) -> bool:
    """Check if a file matches a pattern."""
    if pattern.endswith("/*"):
        dir_pattern = pattern[:-2]
        return file_path.startswith(dir_pattern)
    elif pattern.startswith("*"):
        return file_path.endswith(pattern[1:])
    else:
        return file_path == pattern
