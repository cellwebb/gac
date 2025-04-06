"""
Pytest configuration file with coverage setup to avoid the module-not-measured warning.
"""

import os
import sys
from unittest.mock import patch

import pytest

# Add the src directory to the path to ensure proper importing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))


# Disable coverage warnings about modules already imported
def pytest_configure(config):
    import warnings

    from coverage.exceptions import CoverageWarning

    warnings.filterwarnings("ignore", category=CoverageWarning, message="Module .* was previously imported")


@pytest.fixture
def mock_run_subprocess():
    """Mock for gac.git.run_subprocess."""
    with patch("gac.git.run_subprocess") as mock:
        yield mock


@pytest.fixture
def mock_get_staged_files():
    """Mock for gac.git.get_staged_files."""
    with patch("gac.git.get_staged_files") as mock:
        mock.return_value = ["file1.py", "file2.txt"]
        yield mock


@pytest.fixture
def mock_get_config():
    """Mock for gac.config.get_config."""
    with patch("gac.config.get_config") as mock:
        mock.return_value = {
            "model": "anthropic:claude-3-haiku",
            "use_formatting": True,
            "warning_limit_tokens": 1000,
        }
        yield mock


@pytest.fixture
def mock_commit_changes():
    """Mock for gac.git.commit_changes."""
    with patch("gac.git.commit_changes") as mock:
        yield mock


@pytest.fixture
def mock_prompt():
    """Mock for click.prompt."""
    with patch("click.prompt") as mock:
        mock.return_value = "y"
        yield mock


@pytest.fixture
def mock_print():
    """Mock for builtins.print."""
    with patch("builtins.print") as mock:
        yield mock


@pytest.fixture
def mock_logging():
    """Mock for gac.git.logging."""
    with patch("gac.git.logging") as mock:
        mock.ERROR = 40  # Standard logging.ERROR value
        mock.DEBUG = 10  # Standard logging.DEBUG value
        yield mock


@pytest.fixture
def mock_count_tokens():
    """Mock for gac.ai.count_tokens."""
    with patch("gac.ai.count_tokens") as mock:
        mock.return_value = 100
        yield mock


@pytest.fixture
def mock_build_prompt():
    """Mock for gac.prompt.build_prompt."""
    with patch("gac.prompt.build_prompt") as mock:
        mock.return_value = "Test prompt"
        yield mock


@pytest.fixture
def mock_stage_files():
    """Mock for gac.git.stage_files."""
    with patch("gac.git.stage_files") as mock:
        yield mock


@pytest.fixture
def mock_chat():
    """Mock for gac.ai.chat."""
    with patch("gac.ai.chat") as mock:
        mock.return_value = "Generated commit message"
        yield mock


@pytest.fixture
def mock_os_environ():
    """Mock for os.environ."""
    with patch.dict("os.environ", {}, clear=True) as mock_env:
        yield mock_env


@pytest.fixture
def base_mocks(
    mock_print,
    mock_prompt,
    mock_run_subprocess,
    mock_commit_changes,
    mock_count_tokens,
    mock_get_staged_files,
    mock_get_config,
    mock_stage_files,
):
    """Fixture that provides all the common mocks for main() function tests."""
    return {
        "print": mock_print,
        "prompt": mock_prompt,
        "run_subprocess": mock_run_subprocess,
        "commit_changes": mock_commit_changes,
        "count_tokens": mock_count_tokens,
        "get_staged_files": mock_get_staged_files,
        "get_config": mock_get_config,
        "stage_files": mock_stage_files,
    }
