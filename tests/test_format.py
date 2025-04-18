"""Tests for gac.format module."""

from unittest.mock import patch

import pytest

from gac.format import (
    check_formatter_available,
    format_code,
    format_files,
    main,
    run_formatter,
    validate_format,
)


@patch("gac.format.subprocess.run")
def test_run_formatter_success(mock_subprocess_run):
    """Test run_formatter returns True when formatting succeeds."""
    # Setup mock to simulate successful command execution
    mock_subprocess_run.return_value.returncode = 0

    # Test formatting files
    result = run_formatter(["black"], ["file1.py", "file2.py"], "black")

    # Verify the behavior: function returns True on success
    assert result is True


@patch("gac.format.subprocess.run")
def test_run_formatter_failure(mock_subprocess_run):
    """Test run_formatter returns False when formatting fails."""
    # Setup mock to simulate command failure
    mock_subprocess_run.return_value.returncode = 1
    mock_subprocess_run.return_value.stderr = "Error message"

    # Test formatting files
    result = run_formatter(["black"], ["file1.py", "file2.py"], "black")

    # Verify the behavior: function returns False on failure
    assert result is False


@patch("gac.format.subprocess.run")
def test_run_formatter_exception(mock_subprocess_run):
    """Test run_formatter handles exceptions gracefully."""
    # Setup mock to simulate exception during command execution
    mock_subprocess_run.side_effect = Exception("Command failed")

    # Test formatting files
    result = run_formatter(["black"], ["file1.py", "file2.py"], "black")

    # Verify the behavior: function returns False on exception
    assert result is False


@pytest.mark.parametrize(
    "input_code,expected",
    [
        ("print('hello')", 'print("hello")\n'),
        ("x=1", "x = 1\n"),
    ],
)
def test_format_code_valid(input_code, expected):
    assert format_code(input_code) == expected


def test_validate_format_invalid_code():
    with pytest.raises(ValueError):
        validate_format("x =")


@patch("gac.format.subprocess.run")
def test_check_formatter_available_success(mock_subprocess_run):
    mock_subprocess_run.return_value.returncode = 0
    formatter = {"command": ["black"], "name": "black"}
    assert check_formatter_available(formatter)


@patch("gac.format.subprocess.run")
def test_check_formatter_available_failure(mock_subprocess_run):
    mock_subprocess_run.return_value.returncode = 1
    formatter = {"command": ["black"], "name": "black"}
    assert not check_formatter_available(formatter)


@patch("gac.format.subprocess.run")
def test_check_formatter_available_exception(mock_subprocess_run):
    mock_subprocess_run.side_effect = Exception("fail")
    formatter = {"command": ["black"], "name": "black"}
    assert not check_formatter_available(formatter)


@patch("gac.format.os.path.exists", return_value=True)
@patch("gac.format.check_formatter_available", return_value=True)
@patch("gac.format.run_formatter", return_value=True)
def test_format_files_success(mock_run, mock_check, mock_exists, tmp_path):
    file1 = tmp_path / "f.py"
    file1.write_text("x=1")
    files = [str(file1)]
    formatted = format_files(files)
    assert str(file1) in formatted


@patch("gac.format.os.path.exists", return_value=False)
def test_format_files_missing_file(mock_exists):
    files = ["notfound.py"]
    assert format_files(files) == []


@patch("gac.format.os.path.exists", return_value=True)
@patch("gac.format.check_formatter_available", return_value=True)
@patch("gac.format.run_formatter", return_value=True)
def test_format_files_dry_run(mock_run, mock_check, mock_exists, tmp_path):
    file1 = tmp_path / "f.py"
    file1.write_text("x=1")
    files = [str(file1)]
    formatted = format_files(files, dry_run=True)
    assert str(file1) in formatted


@patch("gac.format.os.path.exists", return_value=True)
@patch("gac.format.check_formatter_available", return_value=False)
def test_format_files_no_formatter(mock_check, mock_exists, tmp_path):
    file1 = tmp_path / "f.py"
    file1.write_text("x=1")
    files = [str(file1)]
    assert format_files(files) == []


@patch("gac.format.logger")
def test_main_no_args(mock_logger, monkeypatch):
    monkeypatch.setattr("sys.argv", ["prog"])
    with pytest.raises(SystemExit):
        main()
    assert mock_logger.error.called


@patch("gac.format.logger")
@patch("gac.format.format_files", return_value=["a.py"])
def test_main_with_args(mock_format_files, mock_logger, monkeypatch):
    monkeypatch.setattr("sys.argv", ["prog", "a.py"])
    main()
    assert mock_logger.info.called
