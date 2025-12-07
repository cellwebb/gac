"""Tests for the always include scope feature (issue #37)."""

from unittest.mock import patch

import pytest

from gac.config import load_config


class TestAlwaysIncludeScopeConfig:
    """Test the always_include_scope configuration option."""

    def test_default_always_include_scope_false(self, monkeypatch):
        """Test that always_include_scope defaults to False."""
        monkeypatch.setenv("GAC_ALWAYS_INCLUDE_SCOPE", "")
        monkeypatch.delenv("GAC_ALWAYS_INCLUDE_SCOPE", raising=False)

        config = load_config()
        assert config["always_include_scope"] is False

    @pytest.mark.parametrize(
        "env_value,expected",
        [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("1", True),
            ("yes", True),
            ("YES", True),
            ("on", True),
            ("ON", True),
            ("false", False),
            ("False", False),
            ("FALSE", False),
            ("0", False),
            ("no", False),
            ("NO", False),
            ("off", False),
            ("OFF", False),
            ("anything_else", False),
            ("", False),
        ],
    )
    def test_always_include_scope_env_values(self, monkeypatch, env_value, expected):
        """Test various environment variable values for always_include_scope."""
        monkeypatch.setenv("GAC_ALWAYS_INCLUDE_SCOPE", env_value)

        config = load_config()
        assert config["always_include_scope"] is expected


class TestAlwaysIncludeScopeCLI:
    """Test the CLI behavior with always_include_scope setting."""

    @patch("gac.cli.main")
    def test_cli_applies_always_include_scope_when_enabled(self, mock_main, monkeypatch):
        """Test that CLI applies scope inference when always_include_scope is enabled and no --scope flag is used."""
        from click.testing import CliRunner

        from gac.cli import cli

        # Mock the config to return always_include_scope=True
        mock_config = {
            "log_level": "ERROR",
            "model": "test:model",
            "always_include_scope": True,
            "no_verify_ssl": False,
            "verbose": False,
            "skip_secret_scan": False,
            "hook_timeout": 120,
        }
        monkeypatch.setattr("gac.cli.config", mock_config)
        monkeypatch.setattr("gac.config.load_config", lambda: mock_config)

        runner = CliRunner()
        runner.invoke(cli, [])

        # Check that main was called with infer_scope=True (which triggers inference)
        mock_main.assert_called_once()
        call_kwargs = mock_main.call_args[1]
        assert call_kwargs["infer_scope"] is True

    @patch("gac.cli.main")
    def test_cli_uses_scope_flag_when_provided(self, mock_main, monkeypatch):
        """Test that --scope flag triggers scope inference when provided."""
        from click.testing import CliRunner

        from gac.cli import cli

        # Mock the config to return always_include_scope=True
        mock_config = {
            "log_level": "ERROR",
            "model": "test:model",
            "always_include_scope": True,
            "no_verify_ssl": False,
            "verbose": False,
            "skip_secret_scan": False,
            "hook_timeout": 120,
        }
        monkeypatch.setattr("gac.cli.config", mock_config)
        monkeypatch.setattr("gac.config.load_config", lambda: mock_config)

        runner = CliRunner()
        runner.invoke(cli, ["--scope"])

        # Check that main was called with infer_scope=True (which triggers inference)
        mock_main.assert_called_once()
        call_kwargs = mock_main.call_args[1]
        assert call_kwargs["infer_scope"] is True

    @patch("gac.cli.main")
    def test_cli_does_not_apply_scope_when_disabled(self, mock_main, monkeypatch):
        """Test that CLI does not apply scope when always_include_scope is disabled."""
        from click.testing import CliRunner

        from gac.cli import cli

        # Mock the config to return always_include_scope=False
        mock_config = {
            "log_level": "ERROR",
            "model": "test:model",
            "always_include_scope": False,
            "no_verify_ssl": False,
            "verbose": False,
            "skip_secret_scan": False,
            "hook_timeout": 120,
        }
        monkeypatch.setattr("gac.cli.config", mock_config)
        monkeypatch.setattr("gac.config.load_config", lambda: mock_config)

        runner = CliRunner()
        runner.invoke(cli, [])

        # Check that main was called with infer_scope=False (no scope)
        mock_main.assert_called_once()
        call_kwargs = mock_main.call_args[1]
        assert call_kwargs["infer_scope"] is False
