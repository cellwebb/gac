from unittest.mock import patch

from click.testing import CliRunner

from gac import cli


def test_cli_main_invocation(monkeypatch):
    runner = CliRunner()
    with patch("gac.cli.main") as main_fn, patch("gac.cli.setup_logging") as setup_logging:
        result = runner.invoke(
            cli.cli, ["-a", "-nf", "-o", "-p", "-s", "-q", "-y", "-h", "hint", "-m", "foo:bar", "--dry-run", "-v"]
        )
        assert result.exit_code == 0
        setup_logging.assert_called()
        main_fn.assert_called_once()
        kwargs = main_fn.call_args.kwargs
        assert kwargs["stage_all"] is True
        assert kwargs["should_format_files"] is False
        assert kwargs["model"] == "foo:bar"
        assert kwargs["hint"] == "hint"
        assert kwargs["one_liner"] is True
        assert kwargs["show_prompt"] is True
        assert kwargs["require_confirmation"] is False
        assert kwargs["push"] is True
        assert kwargs["quiet"] is True
        assert kwargs["dry_run"] is True


def test_cli_error_handling(monkeypatch):
    runner = CliRunner()
    with patch("gac.cli.main", side_effect=Exception("fail")), patch("gac.cli.handle_error") as handle_error:
        result = runner.invoke(cli.cli, ["--dry-run"])
        assert result.exit_code == 0
        handle_error.assert_called()
