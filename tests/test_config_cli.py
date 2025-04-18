import os
import tempfile

from click.testing import CliRunner

from gac.config_cli import config


def test_config_cli_show_set_get_unset(monkeypatch):
    runner = CliRunner()
    # Use a temp file for $HOME/.gac.env
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("HOME", tmpdir)
        # Test 'set'
        result = runner.invoke(config, ["set", "TEST_KEY", "test_value"])
        assert result.exit_code == 0
        assert "Set TEST_KEY" in result.output
        # Test 'get'
        result = runner.invoke(config, ["get", "TEST_KEY"])
        assert result.exit_code == 0
        assert "test_value" in result.output
        # Test 'show'
        result = runner.invoke(config, ["show"])
        assert result.exit_code == 0
        assert "TEST_KEY='test_value'" in result.output
        # Test 'unset'
        result = runner.invoke(config, ["unset", "TEST_KEY"])
        assert result.exit_code == 0
        assert "Unset TEST_KEY" in result.output
        # Should not find TEST_KEY now
        os.environ.pop("TEST_KEY", None)
        result = runner.invoke(config, ["get", "TEST_KEY"])
        assert result.exit_code == 0
        assert "not set" in result.output
