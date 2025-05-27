import pytest
from click.testing import CliRunner

from gac.cli import cli


class TestMainCommand:
    @pytest.fixture
    def mock_init(self, monkeypatch):
        # Patch the init command's callback directly in its source module
        def dummy_init(*args, **kwargs):
            pass

        monkeypatch.setattr("gac.init_cli.init.callback", dummy_init)
        yield

    def test_init_success(self, monkeypatch, mock_init):
        """Test 'gac init' runs without error when all dependencies succeed."""
        runner = CliRunner()
        # The init command's callback is already mocked by mock_init.
        # No need to mock load_config or run_git_command for gac.init_cli here.
        monkeypatch.setattr("rich.console.Console.print", lambda self, *a, **kw: None)
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

    def test_init_not_in_git_repo(self, monkeypatch, mock_init):
        """Test 'gac init' runs (it doesn't check for git repo status itself)."""
        runner = CliRunner()
        # The init command's callback is already mocked by mock_init.
        # No need to mock load_config or run_git_command for gac.init_cli here.
        monkeypatch.setattr("rich.console.Console.print", lambda self, *a, **kw: None)
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

    def test_main_command(self, monkeypatch):
        """Test main command runs without error when its core logic is mocked."""
        runner = CliRunner()
        # Patch gac.config.load_config to ensure that gac.cli.cli's setup phase
        # (which uses gac.cli.config) doesn't fail, and to provide a dummy model.
        monkeypatch.setattr("gac.config.load_config", lambda: {"log_level": "ERROR", "model": "dummy:model"})
        # Patch the main function in 'gac.cli' module, as this is what Click calls.
        monkeypatch.setattr("gac.cli.main", lambda **kwargs: None)
        monkeypatch.setattr("rich.console.Console.print", lambda self, *a, **kw: None)
        result = runner.invoke(cli, [])
        assert result.exit_code == 0
        # Output is empty because gac.cli.main and rich.console.Console.print are mocked.
