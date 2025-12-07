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


def test_config_show_project_level_file():
    """Test show command with project-level .gac.env (lines 28-30, 36->35, 38)."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"
        project_path = Path(tmpdir) / ".gac.env"  # project-level in same dir for test

        # Create project-level config
        project_path.write_text("PROJECT_VAR=value\nSECRET_KEY=secret123\n")

        with patch("gac.config_cli.GAC_ENV_PATH", fake_path):  # user config doesn't exist
            with patch("gac.config_cli.Path.cwd", return_value=Path(tmpdir)):
                result = runner.invoke(config, ["show"])
                assert result.exit_code == 0
                assert "Project config (./.gac.env):" in result.output
                assert "PROJECT_VAR=value" in result.output
                assert "SECRET_KEY=***hidden***" in result.output
                assert "Note: Project-level .gac.env overrides" in result.output


def test_config_get_missing_var():
    """Test get command when variable doesn't exist (lines 51->50)."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"
        fake_path.touch()  # Create empty file

        with patch("gac.config_cli.GAC_ENV_PATH", fake_path):
            # Test get missing variable
            result = runner.invoke(config, ["get", "MISSING_VAR"])
            assert result.exit_code == 0
            assert "MISSING_VAR not set" in result.output


def test_config_show_both_user_and_project_exist_with_sensitivity():
    """Test show command with both user and project configs, covering sensitivity filtering (lines 28-30)."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        user_path = Path(tmpdir) / ".gac.user.env"
        project_path = Path(tmpdir) / "project.env"  # Use different name to avoid conflicts

        # Create user config with sensitive data
        user_path.write_text("USER=value\nAPI_KEY=secret123\nTOKEN=abc123\n")
        # Create project config with some data
        project_path.write_text("PROJECT=test\nPASSWORD=hidden\n")

        with patch("gac.config_cli.GAC_ENV_PATH", user_path):
            # Mock project_env_path to point to our separate file
            with patch("gac.config_cli.Path") as mock_path:
                mock_path.side_effect = lambda arg: project_path if str(arg) == ".gac.env" else user_path
                with patch("gac.config_cli.Path.cwd", return_value=Path(tmpdir)):
                    result = runner.invoke(config, ["show"])
                    assert result.exit_code == 0
                    assert "User config" in result.output
                    assert "Project config" in result.output
                    # Just check that the output contains sensitivity filtering
                    assert "***hidden***" in result.output


def test_config_unset_no_file():
    """Test unset command when .gac.env doesn't exist (lines 90-91)."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"
        # Don't create the file

        with patch("gac.config_cli.GAC_ENV_PATH", fake_path):
            result = runner.invoke(config, ["unset", "TEST_VAR"])
            assert result.exit_code == 0
            assert "No $HOME/.gac.env found." in result.output


def test_config_show_no_configs_exist():
    """Test show command when neither user nor project config exists (lines 28-30)."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_user_path = Path(tmpdir) / ".gac.env"

        # Change to the temp directory so project .gac.env is also in tmpdir and doesn't exist
        with runner.isolated_filesystem(temp_dir=tmpdir):
            with patch("gac.config_cli.GAC_ENV_PATH", fake_user_path):
                result = runner.invoke(config, ["show"])
                assert result.exit_code == 0
                assert "No $HOME/.gac.env found" in result.output
                assert "No project-level .gac.env found" in result.output


def test_config_show_with_none_values():
    """Test show command when config contains None values (lines 36->35, 51->50)."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_user_path = Path(tmpdir) / ".gac.env"
        fake_project_path = Path(tmpdir) / ".gac.env"

        # Create user config with a None-value-like entry (empty value)
        fake_user_path.write_text("VALID_KEY=valid_value\nNULL_KEY=\nEMPTY_KEY=\n")

        # Create project config with empty values
        fake_project_path.write_text("PROJECT_VALID=project_value\nPROJECT_NULL=\n")

        with runner.isolated_filesystem(temp_dir=tmpdir):
            with patch("gac.config_cli.GAC_ENV_PATH", fake_user_path):
                result = runner.invoke(config, ["show"])
                assert result.exit_code == 0
                # Both files should be processed, empty values should be handled gracefully
                assert "valid_value" in result.output or "project_value" in result.output
