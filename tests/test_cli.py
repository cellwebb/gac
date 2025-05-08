import pytest
from click.testing import CliRunner

from gac.cli import cli


@pytest.fixture
def mock_preview(monkeypatch):
    # Patch the preview command to a dummy function
    import gac.preview_cli

    def dummy_preview(*args, **kwargs):
        pass

    monkeypatch.setattr(gac.preview_cli, "preview", dummy_preview)
    yield


def test_preview_success(monkeypatch):
    """Test 'gac preview' runs without error when all dependencies succeed."""
    runner = CliRunner()
    # Patch dependencies in preview_cli
    monkeypatch.setattr(
        "gac.preview_cli.load_config",
        lambda: {
            "model": "test:model",
            "backup_model": "test:backup",
            "temperature": 0.1,
            "max_output_tokens": 100,
            "max_retries": 1,
        },
    )
    monkeypatch.setattr(
        "gac.preview_cli.run_git_command", lambda args: "ok" if "status" in args or "diff" in args else "/repo"
    )
    monkeypatch.setattr("gac.preview_cli.build_prompt", lambda **kwargs: "prompt")
    monkeypatch.setattr("gac.preview_cli.generate_with_fallback", lambda **kwargs: "commit message")
    monkeypatch.setattr("gac.preview_cli.clean_commit_message", lambda msg: msg)
    # Patch Console.print to avoid actual output
    monkeypatch.setattr("rich.console.Console.print", lambda self, *a, **kw: None)
    result = runner.invoke(cli, ["preview", "HEAD"])
    assert result.exit_code == 0
    assert "Preview commit message" in result.output or result.output == ""


def test_preview_not_in_git_repo(monkeypatch):
    """Test 'gac preview' fails with proper error if not in a git repo."""
    runner = CliRunner()
    monkeypatch.setattr(
        "gac.preview_cli.load_config",
        lambda: {
            "model": "test:model",
            "backup_model": "test:backup",
            "temperature": 0.1,
            "max_output_tokens": 100,
            "max_retries": 1,
        },
    )

    def fail_git_command(args):
        if args[0] == "rev-parse":
            raise Exception("fail")
        return "ok"

    monkeypatch.setattr("gac.preview_cli.run_git_command", fail_git_command)
    monkeypatch.setattr("gac.preview_cli.build_prompt", lambda **kwargs: "prompt")
    monkeypatch.setattr("gac.preview_cli.generate_with_fallback", lambda **kwargs: "commit message")
    monkeypatch.setattr("gac.preview_cli.clean_commit_message", lambda msg: msg)
    monkeypatch.setattr("rich.console.Console.print", lambda self, *a, **kw: None)
    result = runner.invoke(cli, ["preview", "HEAD"])
    assert result.exit_code != 0
    assert "Not in a git repository" in result.output
