import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from gac.config_cli import config


def test_config_cli_show_set_get_unset(monkeypatch):
    runner = CliRunner()
    # Use a temp file for $HOME/.gac.env
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("HOME", tmpdir)

        fake_path = Path(tmpdir) / ".gac.env"
        with patch("gac.config_cli.GAC_ENV_PATH", fake_path):
            # Test 'set'
            result = runner.invoke(config, ["set", "TEST_VAR", "test_value"])
            assert result.exit_code == 0
            assert "Set TEST_VAR" in result.output
            # Test 'get'
            result = runner.invoke(config, ["get", "TEST_VAR"])
            assert result.exit_code == 0
            assert "test_value" in result.output
            # Test 'show'
            result = runner.invoke(config, ["show"])
            assert result.exit_code == 0
            assert "TEST_VAR=test_value" in result.output
            # Test 'unset'
            result = runner.invoke(config, ["unset", "TEST_VAR"])
            assert result.exit_code == 0
            assert "Unset TEST_VAR" in result.output
            # Should not find TEST_VAR now
            os.environ.pop("TEST_VAR", None)
            result = runner.invoke(config, ["get", "TEST_VAR"])
            assert result.exit_code == 0
            assert "not set" in result.output


def test_config_show_no_file():
    """Test show command when .gac.env doesn't exist."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"
        with patch("gac.config_cli.GAC_ENV_PATH", fake_path):
            result = runner.invoke(config, ["show"])
            assert result.exit_code == 0
            assert "No $HOME/.gac.env found" in result.output


def test_config_show_project_level(monkeypatch):
    """Test show command when only project .gac.env exists."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        project_env = project_dir / ".gac.env"
        project_env.write_text("GAC_MODEL=project-model\n", encoding="utf-8")

        fake_user_env = tmp_path / "home" / ".gac.env"
        fake_user_env.parent.mkdir(parents=True, exist_ok=True)

        with patch("gac.config_cli.GAC_ENV_PATH", fake_user_env):
            monkeypatch.chdir(project_dir)
            result = runner.invoke(config, ["show"])

        assert result.exit_code == 0
        assert "No $HOME/.gac.env found." in result.output
        assert "Project config (./.gac.env):" in result.output
        assert "GAC_MODEL=project-model" in result.output


def test_config_show_includes_override_note(monkeypatch):
    """Test show command lists both user and project config with override note."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        project_env = project_dir / ".gac.env"
        project_env.write_text("GAC_MODEL=project-model\n", encoding="utf-8")

        user_env = tmp_path / "home" / ".gac.env"
        user_env.parent.mkdir(parents=True, exist_ok=True)
        user_env.write_text("GAC_MODEL=home-model\n", encoding="utf-8")

        with patch("gac.config_cli.GAC_ENV_PATH", user_env):
            monkeypatch.chdir(project_dir)
            result = runner.invoke(config, ["show"])

        assert result.exit_code == 0
        assert f"User config ({user_env}):" in result.output
        assert "GAC_MODEL=home-model" in result.output
        assert "Project config (./.gac.env):" in result.output
        assert "GAC_MODEL=project-model" in result.output
        assert "overrides $HOME/.gac.env" in result.output


def test_config_unset_no_file():
    """Test unset command when .gac.env doesn't exist."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"
        with patch("gac.config_cli.GAC_ENV_PATH", fake_path):
            result = runner.invoke(config, ["unset", "NONEXISTENT_KEY"])
            assert result.exit_code == 0
            assert "No $HOME/.gac.env found" in result.output


def test_config_get_missing_key(monkeypatch):
    """Test get command for a key that doesn't exist in .gac.env."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("HOME", tmpdir)
        # Create empty .gac.env
        result = runner.invoke(config, ["set", "EXISTING_KEY", "value"])
        assert result.exit_code == 0
        # Try to get a non-existent key
        os.environ.pop("MISSING_KEY", None)
        result = runner.invoke(config, ["get", "MISSING_KEY"])
        assert result.exit_code == 0
        assert "not set" in result.output
