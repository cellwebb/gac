"""Integration tests verifying record_tokens is invoked from each workflow path.

These tests cover the wiring between the AI generation step and the stats
module. They mock external dependencies (git, AI, hooks) but assert that
`record_tokens` is actually called with the expected (prompt, completion, model)
values from:
    - gac.main (single commit flow)
    - gac.grouped_commit_workflow (grouped commits flow)
    - gac.mcp.server (MCP gac_commit tool)
"""

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from gac.cli import cli
from gac.mcp.models import CommitRequest, CommitResult
from gac.mcp.server import gac_commit


@pytest.fixture
def runner():
    """CLI runner."""
    return CliRunner()


@pytest.fixture
def base_cli_mocks(monkeypatch):
    """Mock the CLI dependencies needed to drive a single-commit workflow.

    Records all calls to record_tokens / record_gac on the returned dict so
    tests can assert wiring.
    """
    calls: dict[str, list] = {"record_tokens": [], "record_gac": [], "record_commit": []}

    mocked_config = {
        "model": "anthropic:test-model",
        "temperature": 0.7,
        "max_output_tokens": 150,
        "max_retries": 2,
        "log_level": "ERROR",
        "warning_limit_tokens": 10000,
        "no_verify_ssl": False,
        "always_include_scope": False,
        "verbose": False,
        "use_50_72_rule": False,
        "signoff": False,
        "skip_secret_scan": False,
        "hook_timeout": 120,
    }
    monkeypatch.setattr("gac.config.load_config", lambda: mocked_config)

    def mock_run_git_command(args, **kwargs):
        if args == ["rev-parse", "--show-toplevel"]:
            return "/mock/repo/path"
        if args == ["status"]:
            return "On branch main"
        if args == ["diff", "--staged"]:
            return "diff --git a/file.py b/file.py\n+New line"
        if len(args) >= 3 and args[0] == "commit" and args[1] == "-m":
            return "mock commit"
        return "mock git output"

    monkeypatch.setattr("gac.git.run_git_command", mock_run_git_command)

    monkeypatch.setattr("gac.git.get_staged_files", lambda existing_only=False: ["file.py"])

    monkeypatch.setattr("gac.main.clean_commit_message", lambda msg, **kwargs: msg)
    monkeypatch.setattr("click.confirm", lambda *args, **kwargs: True)
    monkeypatch.setattr("click.prompt", lambda *args, **kwargs: "y")
    monkeypatch.setattr("gac.main.run_pre_commit_hooks", lambda: True)

    # Spy on the stats functions instead of replacing with no-ops
    monkeypatch.setattr(
        "gac.main.record_commit",
        lambda *a, **kw: calls["record_commit"].append((a, kw)),
    )
    monkeypatch.setattr(
        "gac.main.record_gac",
        lambda *a, **kw: calls["record_gac"].append((a, kw)),
    )
    monkeypatch.setattr(
        "gac.main.record_tokens",
        lambda *a, **kw: calls["record_tokens"].append((a, kw)),
    )

    monkeypatch.setattr("gac.main.generate_commit_message", lambda *a, **kw: ("feat: add new thing", 10, 5, 500, 0))

    def mock_count_tokens(content, model):
        return 250 if isinstance(content, list) else 12

    monkeypatch.setattr("gac.main.count_tokens", mock_count_tokens)
    monkeypatch.setattr("gac.ai_utils.count_tokens", mock_count_tokens)

    return calls


class TestMainWorkflowRecordsTokens:
    """Verify gac.main._execute_single_commit_workflow calls record_tokens."""

    def test_single_commit_records_tokens_with_model(self, runner, base_cli_mocks):
        result = runner.invoke(cli, ["--yes", "--no-verify"])

        assert result.exit_code == 0, result.output

        # Tokens were recorded exactly once for the single AI call.
        assert len(base_cli_mocks["record_tokens"]) == 1
        args, kwargs = base_cli_mocks["record_tokens"][0]
        # Signature: record_tokens(prompt_tokens, completion_tokens, model=...)
        assert args[0] == 10  # prompt (from provider)
        assert args[1] == 5  # completion (from provider)
        assert kwargs.get("model") == "anthropic:test-model"

        # record_gac was passed the model too
        assert len(base_cli_mocks["record_gac"]) == 1
        _, gac_kwargs = base_cli_mocks["record_gac"][0]
        assert gac_kwargs.get("model") == "anthropic:test-model"

    def test_single_commit_records_tokens_even_for_message_only(self, runner, base_cli_mocks):
        """--message-only short-circuits before commit but tokens were still spent."""
        result = runner.invoke(cli, ["--message-only", "--no-verify"])

        assert result.exit_code == 0, result.output
        assert len(base_cli_mocks["record_tokens"]) == 1
        # No commit was made - record_commit / record_gac should NOT have run.
        assert len(base_cli_mocks["record_commit"]) == 0
        assert len(base_cli_mocks["record_gac"]) == 0

    def test_single_commit_records_tokens_per_regenerate(self, runner, base_cli_mocks, monkeypatch):
        """A regenerate triggers another AI call; tokens must be recorded again."""
        # Sequence: first prompt -> reroll, second prompt -> accept.
        responses = iter(["r", "y"])
        monkeypatch.setattr("click.prompt", lambda *args, **kwargs: next(responses))

        result = runner.invoke(cli, ["--no-verify"])

        assert result.exit_code == 0, result.output
        assert len(base_cli_mocks["record_tokens"]) == 2


class TestGroupedWorkflowRecordsTokens:
    """Verify the grouped commits workflow calls record_tokens."""

    def test_generate_grouped_commits_records_tokens(self, monkeypatch):
        """generate_grouped_commits_with_retry records tokens once per AI call."""
        calls: list = []

        monkeypatch.setattr(
            "gac.grouped_commit_workflow.record_tokens",
            lambda *a, **kw: calls.append((a, kw)),
        )

        # Stub out the AI call to return a valid grouped JSON response.
        valid_response = (
            '{"commits": [{"files": ["a.py"], "message": "feat: a"}, {"files": ["b.py"], "message": "fix: b"}]}'
        )
        monkeypatch.setattr(
            "gac.grouped_commit_workflow.generate_grouped_commits",
            lambda **kwargs: (valid_response, 500, 80, 500, 0),
        )

        # count_tokens: 500 for the conversation list, 80 for the response string.
        def mock_count_tokens(content, model):
            return 500 if isinstance(content, list) else 80

        monkeypatch.setattr("gac.grouped_commit_workflow.count_tokens", mock_count_tokens)

        # Bypass the token-warning prompt.
        monkeypatch.setattr("gac.grouped_commit_workflow.check_token_warning", lambda *a, **kw: True)

        from gac.grouped_commit_workflow import GroupedCommitWorkflow

        workflow = GroupedCommitWorkflow({"warning_limit_tokens": 10000})

        result = workflow.generate_grouped_commits_with_retry(
            model="openai:gpt-test",
            conversation_messages=[
                {"role": "system", "content": "sys"},
                {"role": "user", "content": "usr"},
            ],
            temperature=0.5,
            max_output_tokens=100,
            max_retries=2,
            quiet=True,
            staged_files_set={"a.py", "b.py"},
            require_confirmation=False,
        )

        # Generation succeeded
        assert not isinstance(result, int)

        # Tokens were recorded with prompt=500, completion=80, model=openai:gpt-test
        assert len(calls) == 1
        args, kwargs = calls[0]
        assert args[0] == 500
        assert args[1] == 80
        assert kwargs.get("model") == "openai:gpt-test"

    def test_execute_grouped_commits_passes_model_to_record_gac(self, monkeypatch):
        """execute_grouped_commits should forward model= to record_gac on success."""
        gac_calls: list = []
        monkeypatch.setattr(
            "gac.grouped_commit_workflow.record_gac",
            lambda *a, **kw: gac_calls.append((a, kw)),
        )
        monkeypatch.setattr(
            "gac.grouped_commit_workflow.record_commit",
            lambda *a, **kw: None,
        )

        # Stub git commands - all interactions return bland values.
        monkeypatch.setattr("gac.grouped_commit_workflow.run_git_command", lambda *a, **kw: "")
        monkeypatch.setattr(
            "gac.grouped_commit_workflow.get_staged_files",
            lambda existing_only=False: ["a.py", "b.py"],
        )
        monkeypatch.setattr(
            "gac.grouped_commit_workflow.detect_rename_mappings",
            lambda diff: {},
        )
        monkeypatch.setattr(
            "gac.grouped_commit_workflow.execute_commit",
            lambda *a, **kw: None,
        )
        monkeypatch.setattr(
            "gac.grouped_commit_workflow.clean_commit_message",
            lambda msg, **kwargs: msg,
        )

        from gac.grouped_commit_workflow import GroupedCommitResult, GroupedCommitWorkflow

        workflow = GroupedCommitWorkflow({"warning_limit_tokens": 10000})
        result = GroupedCommitResult(
            commits=[
                {"files": ["a.py"], "message": "feat: a"},
                {"files": ["b.py"], "message": "fix: b"},
            ],
            raw_response="{}",
        )

        exit_code = workflow.execute_grouped_commits(
            result=result,
            dry_run=False,
            push=False,
            no_verify=True,
            hook_timeout=120,
            model="anthropic:claude-haiku-4-5",
        )

        assert exit_code == 0
        assert len(gac_calls) == 1
        _, kwargs = gac_calls[0]
        assert kwargs.get("model") == "anthropic:claude-haiku-4-5"


class TestMcpServerRecordsTokens:
    """Verify gac.mcp.server.gac_commit calls record_tokens for the AI call."""

    @patch("gac.postprocess.clean_commit_message", return_value="feat: x")
    @patch("gac.ai.generate_commit_message", return_value=("feat: x", 10, 5, 500, 0))
    @patch("gac.prompt_builder.PromptBuilder")
    @patch("gac.git_state_validator.GitStateValidator")
    @patch("gac.git.get_staged_files", return_value=["a.py"])
    @patch("gac.git.run_git_command")
    @patch("gac.config.load_config", return_value={"model": "openai:gpt-test"})
    @patch("gac.mcp.server._check_git_repo", return_value=(True, ""))
    def test_mcp_dry_run_records_tokens(
        self,
        mock_check,
        mock_config,
        mock_git,
        mock_staged,
        mock_validator_cls,
        mock_pb_cls,
        mock_gen,
        mock_clean,
        monkeypatch,
    ):
        """Even in dry_run mode the AI was called, so tokens must be recorded."""
        gs = MagicMock()
        gs.has_secrets = False
        mock_validator_cls.return_value.get_git_state.return_value = gs

        bundle = MagicMock()
        bundle.system_prompt = "sys"
        bundle.user_prompt = "usr"
        mock_pb_cls.return_value.build_prompts.return_value = bundle

        # count_tokens called from the MCP path returns predictable values.
        def mock_count_tokens(content, model):
            return 333 if isinstance(content, list) else 44

        monkeypatch.setattr("gac.ai_utils.count_tokens", mock_count_tokens)

        captured: list = []
        monkeypatch.setattr("gac.stats.record_tokens", lambda *a, **kw: captured.append((a, kw)))

        result = gac_commit(CommitRequest(dry_run=True))
        assert isinstance(result, CommitResult)
        assert result.success is True

        assert len(captured) == 1
        args, kwargs = captured[0]
        assert args[0] == 10
        assert args[1] == 5
        assert kwargs.get("model") == "openai:gpt-test"
