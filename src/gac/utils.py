"""Utility functions for gac."""

import locale
import logging
import subprocess
import sys
from typing import Any

from rich.console import Console
from rich.theme import Theme

from gac.constants import EnvDefaults, Logging
from gac.errors import GacError


def __getattr__(name: str) -> Any:
    """Lazy re-exports for backward compatibility."""
    if name in ("count_tokens", "extract_text_content"):
        from gac.ai_utils import count_tokens, extract_text_content

        return count_tokens if name == "count_tokens" else extract_text_content
    if name == "edit_commit_message_inplace":
        from gac.editor import edit_commit_message_inplace

        return edit_commit_message_inplace
    if name == "edit_commit_message_in_editor":
        from gac.editor import edit_commit_message_in_editor

        return edit_commit_message_in_editor
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def should_skip_ssl_verification() -> bool:
    """Return True when SSL certificate verification should be skipped.

    This is useful for corporate environments with proxy servers that
    intercept SSL traffic and cause certificate verification failures.

    Can be enabled via:
    - GAC_NO_VERIFY_SSL=true environment variable
    - --no-verify-ssl CLI flag (which sets the env var)

    Returns:
        True if SSL verification should be skipped, False otherwise.
    """
    from gac.config import _parse_bool_env

    return _parse_bool_env("GAC_NO_VERIFY_SSL", EnvDefaults.NO_VERIFY_SSL)


def get_ssl_verify() -> bool:
    """Get the SSL verification setting for httpx requests.

    Returns:
        True to verify SSL certificates (default), False to skip verification.
    """
    return not should_skip_ssl_verification()


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

    kwargs: dict[str, Any] = {"force": force} if force else {}

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


def get_safe_encodings() -> list[str]:
    """Get a list of safe encodings to try for subprocess calls, in order of preference.

    Returns:
        List of encoding strings to try, with UTF-8 first
    """
    encodings = ["utf-8"]

    # Add locale encoding as fallback
    locale_encoding = locale.getpreferredencoding(False)
    if locale_encoding and locale_encoding not in encodings:
        encodings.append(locale_encoding)

    # Windows-specific fallbacks
    if sys.platform == "win32":
        windows_encodings = ["cp65001", "cp936", "cp1252"]  # UTF-8, GBK, Windows-1252
        for enc in windows_encodings:
            if enc not in encodings:
                encodings.append(enc)

    # Final fallback to system default
    if "utf-8" not in encodings:
        encodings.append("utf-8")

    return encodings


def run_subprocess_with_encoding(
    command: list[str],
    encoding: str,
    silent: bool = False,
    timeout: int = 60,
    check: bool = True,
    strip_output: bool = True,
    raise_on_error: bool = True,
) -> str:
    """Run subprocess with a specific encoding, handling encoding errors gracefully.

    Args:
        command: List of command arguments
        encoding: Specific encoding to use
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
        logger.debug(f"Running command: {' '.join(command)} (encoding: {encoding})")

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
            encoding=encoding,
            errors="replace",  # Replace problematic characters instead of crashing
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
    except UnicodeError as e:
        # This should be rare with errors="replace", but handle it just in case
        if not silent:
            logger.debug(f"Encoding error with {encoding}: {e}")
        raise
    except Exception as e:
        if not silent:
            logger.debug(f"Command error: {e}")
        if raise_on_error:
            # Convert generic exceptions to CalledProcessError for consistency
            raise subprocess.CalledProcessError(1, command, "", str(e)) from e
        return ""


def run_subprocess(
    command: list[str],
    silent: bool = False,
    timeout: int = 60,
    check: bool = True,
    strip_output: bool = True,
    raise_on_error: bool = True,
) -> str:
    """Run a subprocess command safely and return the output, trying multiple encodings.

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

    Note:
        Tries multiple encodings in order: utf-8, locale encoding, platform-specific fallbacks
        This prevents UnicodeDecodeError on systems with non-UTF-8 locales (e.g., Chinese Windows)
    """
    encodings = get_safe_encodings()
    last_exception = None

    for encoding in encodings:
        try:
            return run_subprocess_with_encoding(
                command=command,
                encoding=encoding,
                silent=silent,
                timeout=timeout,
                check=check,
                strip_output=strip_output,
                raise_on_error=raise_on_error,
            )
        except UnicodeError as e:
            last_exception = e
            if not silent:
                logger.debug(f"Failed to decode with {encoding}: {e}")
            continue
        except (subprocess.CalledProcessError, GacError, subprocess.TimeoutExpired):
            # These are not encoding-related errors, so don't retry with other encodings
            raise

    # If we get here, all encodings failed with UnicodeError
    if not silent:
        logger.error(f"Failed to decode command output with any encoding: {encodings}")

    # Raise the last UnicodeError we encountered
    if last_exception:
        raise subprocess.CalledProcessError(1, command, "", f"Encoding error: {last_exception}") from last_exception
    else:
        raise subprocess.CalledProcessError(1, command, "", "All encoding attempts failed")
