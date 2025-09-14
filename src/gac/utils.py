"""Utility functions for gac."""

import logging
import subprocess

from rich.console import Console
from rich.theme import Theme

from gac.constants import Logging
from gac.errors import GacError


def setup_logging(
    log_level: int | str = Logging.DEFAULT_LEVEL,
    quiet: bool = False,
    force: bool = False,
    suppress_noisy: bool = False,
) -> None:
    """Configure logging for the application.

    Args:
        log_level: Log level to use (DEBUG, INFO, WARNING, ERROR)
        quiet: If True, suppress all output except errors
        force: If True, force reconfiguration of logging
        suppress_noisy: If True, suppress noisy third-party loggers
    """
    if isinstance(log_level, str):
        log_level = getattr(logging, log_level.upper(), logging.WARNING)

    if quiet:
        log_level = logging.ERROR

    kwargs = {"force": force} if force else {}

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        **kwargs,
    )

    if suppress_noisy:
        for noisy_logger in ["requests", "urllib3"]:
            logging.getLogger(noisy_logger).setLevel(logging.WARNING)

    logger.info(f"Logging initialized with level: {logging.getLevelName(log_level)}")


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


def run_subprocess(
    command: list[str],
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
        GacError: If the command times out
        subprocess.CalledProcessError: If the command fails and raise_on_error is True
    """
    if not silent:
        logger.debug(f"Running command: {' '.join(command)}")

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )

        should_raise = result.returncode != 0 and (check or raise_on_error)

        if should_raise:
            if not silent:
                logger.debug(f"Command stderr: {result.stderr}")
            raise subprocess.CalledProcessError(result.returncode, command, result.stdout, result.stderr)

        output = result.stdout
        if strip_output:
            output = output.strip()

        return output
    except subprocess.TimeoutExpired as e:
        logger.error(f"Command timed out after {timeout} seconds: {' '.join(command)}")
        raise GacError(f"Command timed out: {' '.join(command)}") from e
    except subprocess.CalledProcessError as e:
        if not silent:
            logger.error(f"Command failed: {e.stderr.strip() if e.stderr else str(e)}")
        if raise_on_error:
            raise
        return ""
    except Exception as e:
        if not silent:
            logger.debug(f"Command error: {e}")
        if raise_on_error:
            # Convert generic exceptions to CalledProcessError for consistency
            raise subprocess.CalledProcessError(1, command, "", str(e)) from e
        return ""
