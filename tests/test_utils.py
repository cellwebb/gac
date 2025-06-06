"""Tests for gac.utils module."""

import subprocess
from unittest import mock

import pytest

from gac.errors import GacError
from gac.utils import print_message, run_subprocess, setup_logging


def test_setup_logging_all_branches(monkeypatch):
    # Test string log_level, quiet, force, suppress_noisy
    setup_logging("DEBUG", quiet=False, force=True, suppress_noisy=True)
    setup_logging("INFO", quiet=True)  # Should set log_level to ERROR
    setup_logging(10, quiet=False)  # int log level


def test_print_message_all_levels():
    # Just ensure no exceptions for various levels
    for level in ["info", "success", "warning", "error", "header", "notification"]:
        print_message("test", level=level)


def test_run_subprocess_success(monkeypatch):
    class Result:
        def __init__(self):
            self.returncode = 0
            self.stdout = "output\n"
            self.stderr = ""

    monkeypatch.setattr("subprocess.run", lambda *a, **kw: Result())
    assert run_subprocess(["echo", "hi"]) == "output"


def test_run_subprocess_nonzero(monkeypatch):
    class Result:
        def __init__(self):
            self.returncode = 1
            self.stdout = "fail\n"
            self.stderr = "bad"

    monkeypatch.setattr("subprocess.run", lambda *a, **kw: Result())
    import subprocess as sp

    import pytest

    with pytest.raises(sp.CalledProcessError):
        run_subprocess(["fail"], check=True, raise_on_error=True)
    # Should not raise if raise_on_error is False
    assert run_subprocess(["fail"], check=True, raise_on_error=False) == ""


def test_run_subprocess_timeout(monkeypatch):
    import subprocess as sp

    # Mock subprocess.run to simulate a timeout
    with mock.patch("subprocess.run", side_effect=sp.TimeoutExpired(cmd="timeout", timeout=0.1)):
        with pytest.raises(GacError):
            run_subprocess(["timeout"])  # Should raise GacError


def test_run_subprocess_calledprocesserror(monkeypatch):
    import subprocess as sp

    def raise_cpe(*a, **kw):
        raise sp.CalledProcessError(1, ["fail"], "", "fail")

    monkeypatch.setattr("subprocess.run", raise_cpe)
    import pytest

    with pytest.raises(sp.CalledProcessError):
        run_subprocess(["fail"], raise_on_error=True)
    # Should not raise if raise_on_error is False
    assert run_subprocess(["fail"], raise_on_error=False) == ""


def test_run_subprocess_exception(monkeypatch):
    def raise_exc(*a, **kw):
        raise Exception("fail")

    monkeypatch.setattr("subprocess.run", raise_exc)
    # Should not raise if raise_on_error is False
    assert run_subprocess(["fail"], raise_on_error=False) == ""
    # Should raise if raise_on_error is True
    import pytest

    with pytest.raises(subprocess.CalledProcessError):
        run_subprocess(["fail"], raise_on_error=True)
