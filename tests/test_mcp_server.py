"""Tests for gac.mcp.server tool functions (gac_status and gac_commit)."""

from unittest.mock import MagicMock, patch

from gac.git import GitCommandResult
from gac.grouped_commit_workflow import WorkflowResult
from gac.mcp.models import (
    CommitInfo,
    CommitRequest,
    CommitResult,
    DiffStats,
    StatusRequest,
    StatusResult,
)
from gac.mcp.server import gac_commit, gac_status
from gac.mcp.server_utils import CommitListResult, FileStatus


class TestGacStatus:
    @patch("gac.mcp.server._check_git_repo", return_value=(False, "fatal: not a git repo"))
    def test_not_in_git_repo(self, mock_check):
        result = gac_status(StatusRequest())
        assert isinstance(result, StatusResult)
        assert result.is_repo is False
        assert result.error is not None
        assert "not a git repo" in result.error.lower()
        assert result.branch == ""

    @patch("gac.mcp.server._get_recent_commits")
    @patch("gac.mcp.server._get_diff_stats")
    @patch("gac.mcp.server._truncate_diff")
    @patch("gac.git.run_git_command")
    @patch("gac.mcp.server._get_file_status")
    @patch("gac.git.get_current_branch", return_value="main")
    @patch("gac.mcp.server._check_git_repo", return_value=(True, ""))
    def test_happy_path(
        self,
        mock_check,
        mock_branch,
        mock_file_status,
        mock_git_cmd,
        mock_truncate,
        mock_stats,
        mock_commits,
    ):
        mock_file_status.return_value = FileStatus(
            staged=["src/a.py"],
            unstaged=["src/b.py"],
            untracked=["new.py"],
            conflicts=[],
        )
        mock_git_cmd.return_value = GitCommandResult.ok("+added\n-removed")
        mock_truncate.return_value = ("+added\n-removed", False)
        mock_stats.return_value = DiffStats(files_changed=1, insertions=1, deletions=1, file_stats=[])
        mock_commits.return_value = CommitListResult(
            commits=[CommitInfo(hash="abc1234", message="feat: init", author="Alice", date="1 hour ago")]
        )

        result = gac_status(StatusRequest(include_diff=True, include_stats=True, include_history=3))

        assert result.is_repo is True
        assert result.branch == "main"
        assert result.staged_files == ["src/a.py"]
        assert result.unstaged_files == ["src/b.py"]
        assert result.untracked_files == ["new.py"]
        assert result.diff == "+added\n-removed"
        assert result.diff_stats is not None
        assert result.recent_commits is not None
        assert result.error is None
        assert result.is_clean is False

    @patch("gac.mcp.server._truncate_diff", return_value=("line1\nline2\nline3", True))
    @patch("gac.git.run_git_command", return_value=GitCommandResult.ok("line1\nline2\nline3\nline4\nline5"))
    @patch(
        "gac.mcp.server._get_file_status",
        return_value=FileStatus(staged=["a.py"], unstaged=[], untracked=[], conflicts=[]),
    )
    @patch("gac.git.get_current_branch", return_value="dev")
    @patch("gac.mcp.server._check_git_repo", return_value=(True, ""))
    def test_diff_truncation(self, mock_check, mock_branch, mock_file_status, mock_git_cmd, mock_truncate):
        result = gac_status(StatusRequest(include_diff=True, max_diff_lines=3))

        assert result.diff_truncated is True
        assert "truncated" in result.summary.lower()

    @patch("gac.mcp.server._check_git_repo", return_value=(True, ""))
    def test_exception_handling(self, mock_check):
        with patch("gac.git.get_current_branch", side_effect=RuntimeError("branch error")):
            result = gac_status(StatusRequest())

        assert result.is_repo is True
        assert result.error is not None
        assert "branch error" in result.error

    @patch("gac.mcp.server._get_recent_commits")
    @patch(
        "gac.mcp.server._get_file_status",
        return_value=FileStatus(staged=["a.py"], unstaged=[], untracked=[], conflicts=[]),
    )
    @patch("gac.git.get_current_branch", return_value="main")
    @patch("gac.mcp.server._check_git_repo", return_value=(True, ""))
    def test_history_error_surfaces_in_status_error(self, mock_check, mock_branch, mock_file_status, mock_commits):
        """When _get_recent_commits fails, the error should appear in StatusResult.error."""
        mock_commits.return_value = CommitListResult(commits=[], error="git log failed: not a repo")

        result = gac_status(StatusRequest(include_history=5))

        assert result.recent_commits == []
        assert result.error is not None
        assert "git log failed" in result.error

    @patch("gac.mcp.server._get_recent_commits")
    @patch(
        "gac.mcp.server._get_file_status",
        return_value=FileStatus(staged=["a.py"], unstaged=[], untracked=[], conflicts=[], error="file status degraded"),
    )
    @patch("gac.git.get_current_branch", return_value="main")
    @patch("gac.mcp.server._check_git_repo", return_value=(True, ""))
    def test_both_errors_combined_in_status(self, mock_check, mock_branch, mock_file_status, mock_commits):
        """When both file status and history fail, both errors appear in StatusResult.error."""
        mock_commits.return_value = CommitListResult(commits=[], error="git log failed")

        result = gac_status(StatusRequest(include_history=5))

        assert result.error is not None
        assert "file status degraded" in result.error
        assert "git log failed" in result.error

    @patch("gac.git.run_git_command")
    @patch(
        "gac.mcp.server._get_file_status",
        return_value=FileStatus(staged=["a.py"], unstaged=[], untracked=[], conflicts=[]),
    )
    @patch("gac.git.get_current_branch", return_value="main")
    @patch("gac.mcp.server._check_git_repo", return_value=(True, ""))
    def test_staged_only_diff(self, mock_check, mock_branch, mock_file_status, mock_git_cmd):
        mock_git_cmd.return_value = GitCommandResult.ok("+staged change")
        result = gac_status(StatusRequest(include_diff=True, staged_only=True, include_stats=False))

        mock_git_cmd.assert_called_with(["diff", "--cached"])
        assert result.diff == "+staged change"

    @patch("gac.git.run_git_command")
    @patch(
        "gac.mcp.server._get_file_status",
        return_value=FileStatus(staged=["a.py"], unstaged=[], untracked=[], conflicts=[]),
    )
    @patch("gac.git.get_current_branch", return_value="main")
    @patch("gac.mcp.server._check_git_repo", return_value=(True, ""))
    def test_diff_head_when_not_staged_only(self, mock_check, mock_branch, mock_file_status, mock_git_cmd):
        mock_git_cmd.return_value = GitCommandResult.ok("+change")
        gac_status(StatusRequest(include_diff=True, staged_only=False, include_stats=False))

        mock_git_cmd.assert_called_with(["diff", "HEAD"])

    @patch(
        "gac.mcp.server._get_file_status",
        return_value=FileStatus(staged=[], unstaged=[], untracked=["extra.py"], conflicts=[]),
    )
    @patch("gac.git.get_current_branch", return_value="main")
    @patch("gac.mcp.server._check_git_repo", return_value=(True, ""))
    def test_include_untracked_false(self, mock_check, mock_branch, mock_file_status):
        result = gac_status(StatusRequest(include_untracked=False))

        assert result.untracked_files == []
        assert result.is_clean is True

    @patch(
        "gac.mcp.server._get_file_status",
        return_value=FileStatus(staged=[], unstaged=[], untracked=[], conflicts=[]),
    )
    @patch("gac.git.get_current_branch", return_value="main")
    @patch("gac.mcp.server._check_git_repo", return_value=(True, ""))
    def test_clean_repo(self, mock_check, mock_branch, mock_file_status):
        result = gac_status(StatusRequest())

        assert result.is_clean is True
        assert result.diff is None
        assert result.recent_commits is None

    @patch(
        "gac.mcp.server._get_file_status",
        return_value=FileStatus(staged=["a.py"], unstaged=[], untracked=[], conflicts=[]),
    )
    @patch("gac.git.get_current_branch", return_value="main")
    @patch("gac.mcp.server._check_git_repo", return_value=(True, ""))
    def test_no_diff_no_stats_no_history(self, mock_check, mock_branch, mock_file_status):
        result = gac_status(StatusRequest(include_diff=False, include_stats=False, include_history=0))

        assert result.diff is None
        assert result.diff_stats is None
        assert result.recent_commits is None


# =============================================================================
# gac_commit tool
# =============================================================================


def _make_git_state(has_secrets: bool = False) -> MagicMock:
    gs = MagicMock()
    gs.has_secrets = has_secrets
    return gs


def _make_prompt_bundle(system: str = "sys", user: str = "usr") -> MagicMock:
    bundle = MagicMock()
    bundle.system_prompt = system
    bundle.user_prompt = user
    return bundle


def _make_grouped_result(commits: list[dict[str, object]] | None = None) -> WorkflowResult:
    gr = MagicMock()
    gr.commits = commits or [
        {"message": "feat(auth): add login", "files": ["src/auth.py"]},
        {"message": "fix(api): handle timeout", "files": ["src/api.py"]},
    ]
    return WorkflowResult(success=True, result=gr)


class TestGacCommit:
    @patch("gac.mcp.server._check_git_repo", return_value=(False, "fatal: not a git repo"))
    def test_not_in_git_repo(self, mock_check):
        result = gac_commit(CommitRequest())
        assert isinstance(result, CommitResult)
        assert result.success is False
        assert "not a git repo" in result.error.lower()

    @patch("gac.git.get_staged_files", return_value=["a.py"])
    @patch("gac.git.run_git_command")
    @patch("gac.config.load_config", return_value={})
    @patch("gac.mcp.server._check_git_repo", return_value=(True, ""))
    def test_no_model_configured(self, mock_check, mock_config, mock_git, mock_staged):
        result = gac_commit(CommitRequest())
        assert result.success is False
        assert "no model" in result.error.lower()

    @patch("gac.git.get_staged_files", return_value=[])
    @patch("gac.git.run_git_command")
    @patch("gac.config.load_config", return_value={"model": "openai:gpt-4"})
    @patch("gac.mcp.server._check_git_repo", return_value=(True, ""))
    def test_no_staged_changes(self, mock_check, mock_config, mock_git, mock_staged):
        result = gac_commit(CommitRequest())
        assert result.success is False
        assert "no staged" in result.error.lower()

    @patch("gac.git_state_validator.GitStateValidator")
    @patch("gac.git.get_staged_files", return_value=["a.py"])
    @patch("gac.git.run_git_command")
    @patch("gac.config.load_config", return_value={"model": "openai:gpt-4"})
    @patch("gac.mcp.server._check_git_repo", return_value=(True, ""))
    def test_failed_git_state(self, mock_check, mock_config, mock_git, mock_staged, mock_validator_cls):
        mock_validator_cls.return_value.get_git_state.return_value = None
        result = gac_commit(CommitRequest())
        assert result.success is False
        assert "failed to get git state" in result.error.lower()
        assert result.files_changed == ["a.py"]

    @patch("gac.postprocess.clean_commit_message", return_value="feat: add feature")
    @patch("gac.ai.generate_commit_message", return_value=("feat: add feature", 10, 5, 500, 0))
    @patch("gac.prompt_builder.PromptBuilder")
    @patch("gac.git_state_validator.GitStateValidator")
    @patch("gac.git.get_staged_files", return_value=["src/app.py"])
    @patch("gac.git.run_git_command")
    @patch("gac.config.load_config", return_value={"model": "openai:gpt-4"})
    @patch("gac.mcp.server._check_git_repo", return_value=(True, ""))
    def test_single_dry_run(
        self, mock_check, mock_config, mock_git, mock_staged, mock_validator_cls, mock_pb_cls, mock_gen, mock_clean
    ):
        mock_validator_cls.return_value.get_git_state.return_value = _make_git_state()
        mock_pb_cls.return_value.build_prompts.return_value = _make_prompt_bundle()

        result = gac_commit(CommitRequest(dry_run=True))

        assert result.success is True
        assert result.commit_message == "feat: add feature"
        assert result.commit_hash is None
        assert any("dry_run" in w for w in result.warnings)

    @patch("gac.postprocess.clean_commit_message", return_value="fix: patch bug")
    @patch("gac.ai.generate_commit_message", return_value=("fix: patch bug", 10, 5, 500, 0))
    @patch("gac.prompt_builder.PromptBuilder")
    @patch("gac.git_state_validator.GitStateValidator")
    @patch("gac.git.get_staged_files", return_value=["src/app.py"])
    @patch("gac.git.run_git_command")
    @patch("gac.config.load_config", return_value={"model": "openai:gpt-4"})
    @patch("gac.mcp.server._check_git_repo", return_value=(True, ""))
    def test_single_message_only(
        self, mock_check, mock_config, mock_git, mock_staged, mock_validator_cls, mock_pb_cls, mock_gen, mock_clean
    ):
        mock_validator_cls.return_value.get_git_state.return_value = _make_git_state()
        mock_pb_cls.return_value.build_prompts.return_value = _make_prompt_bundle()

        result = gac_commit(CommitRequest(message_only=True))

        assert result.success is True
        assert result.commit_message == "fix: patch bug"
        assert result.commit_hash is None
        assert any("message_only" in w for w in result.warnings)

    @patch("gac.mcp.server._stderr_console_redirect")
    @patch("gac.commit_executor.CommitExecutor")
    @patch("gac.postprocess.clean_commit_message", return_value="feat: add login")
    @patch("gac.ai.generate_commit_message", return_value=("feat: add login", 10, 5, 500, 0))
    @patch("gac.prompt_builder.PromptBuilder")
    @patch("gac.git_state_validator.GitStateValidator")
    @patch("gac.git.get_staged_files", return_value=["src/auth.py"])
    @patch("gac.git.run_git_command")
    @patch("gac.config.load_config", return_value={"model": "openai:gpt-4"})
    @patch("gac.mcp.server._check_git_repo", return_value=(True, ""))
    def test_single_commit_execute(
        self,
        mock_check,
        mock_config,
        mock_git,
        mock_staged,
        mock_validator_cls,
        mock_pb_cls,
        mock_gen,
        mock_clean,
        mock_executor_cls,
        mock_redirect,
    ):
        mock_validator_cls.return_value.get_git_state.return_value = _make_git_state()
        mock_pb_cls.return_value.build_prompts.return_value = _make_prompt_bundle()
        mock_git.return_value = GitCommandResult.ok("abc1234fullhash")
        mock_redirect.return_value.__enter__ = MagicMock(return_value=None)
        mock_redirect.return_value.__exit__ = MagicMock(return_value=False)

        result = gac_commit(CommitRequest())

        assert result.success is True
        assert result.commit_message == "feat: add login"
        assert result.commit_hash == "abc1234"
        mock_executor_cls.return_value.create_commit.assert_called_once_with("feat: add login")

    @patch("gac.mcp.server._stderr_console_redirect")
    @patch("gac.commit_executor.CommitExecutor")
    @patch("gac.postprocess.clean_commit_message", return_value="feat: add push")
    @patch("gac.ai.generate_commit_message", return_value=("feat: add push", 10, 5, 500, 0))
    @patch("gac.prompt_builder.PromptBuilder")
    @patch("gac.git_state_validator.GitStateValidator")
    @patch("gac.git.get_staged_files", return_value=["src/push.py"])
    @patch("gac.git.run_git_command")
    @patch("gac.config.load_config", return_value={"model": "openai:gpt-4"})
    @patch("gac.mcp.server._check_git_repo", return_value=(True, ""))
    def test_single_commit_with_push(
        self,
        mock_check,
        mock_config,
        mock_git,
        mock_staged,
        mock_validator_cls,
        mock_pb_cls,
        mock_gen,
        mock_clean,
        mock_executor_cls,
        mock_redirect,
    ):
        mock_validator_cls.return_value.get_git_state.return_value = _make_git_state()
        mock_pb_cls.return_value.build_prompts.return_value = _make_prompt_bundle()
        mock_git.return_value = GitCommandResult.ok("def5678fullhash")
        mock_redirect.return_value.__enter__ = MagicMock(return_value=None)
        mock_redirect.return_value.__exit__ = MagicMock(return_value=False)

        result = gac_commit(CommitRequest(push=True))

        assert result.success is True
        mock_executor_cls.return_value.push_to_remote.assert_called_once()

    @patch("gac.postprocess.clean_commit_message", return_value="")
    @patch("gac.ai.generate_commit_message", return_value=("", 0, 0, 0, 0))
    @patch("gac.prompt_builder.PromptBuilder")
    @patch("gac.git_state_validator.GitStateValidator")
    @patch("gac.git.get_staged_files", return_value=["a.py"])
    @patch("gac.git.run_git_command")
    @patch("gac.config.load_config", return_value={"model": "openai:gpt-4"})
    @patch("gac.mcp.server._check_git_repo", return_value=(True, ""))
    def test_single_empty_commit_message(
        self, mock_check, mock_config, mock_git, mock_staged, mock_validator_cls, mock_pb_cls, mock_gen, mock_clean
    ):
        mock_validator_cls.return_value.get_git_state.return_value = _make_git_state()
        mock_pb_cls.return_value.build_prompts.return_value = _make_prompt_bundle()

        result = gac_commit(CommitRequest())

        assert result.success is False
        assert "failed to generate" in result.error.lower()

    @patch("gac.grouped_commit_workflow.GroupedCommitWorkflow")
    @patch("gac.prompt_builder.PromptBuilder")
    @patch("gac.git_state_validator.GitStateValidator")
    @patch("gac.git.get_staged_files", return_value=["src/a.py", "src/b.py"])
    @patch("gac.git.run_git_command")
    @patch("gac.config.load_config", return_value={"model": "openai:gpt-4"})
    @patch("gac.mcp.server._check_git_repo", return_value=(True, ""))
    def test_grouped_dry_run(
        self, mock_check, mock_config, mock_git, mock_staged, mock_validator_cls, mock_pb_cls, mock_workflow_cls
    ):
        mock_validator_cls.return_value.get_git_state.return_value = _make_git_state()
        mock_pb_cls.return_value.build_prompts.return_value = _make_prompt_bundle()
        mock_workflow_cls.return_value.generate_grouped_commits_with_retry.return_value = _make_grouped_result()

        result = gac_commit(CommitRequest(group=True, dry_run=True))

        assert result.success is True
        assert result.grouped_commits is not None
        assert len(result.grouped_commits) == 2
        assert result.grouped_commits[0].scope == "auth"
        assert result.grouped_commits[0].suggested_message == "feat(auth): add login"
        assert any("dry_run" in w for w in result.warnings)

    @patch("gac.grouped_commit_workflow.GroupedCommitWorkflow")
    @patch("gac.prompt_builder.PromptBuilder")
    @patch("gac.git_state_validator.GitStateValidator")
    @patch("gac.git.get_staged_files", return_value=["src/a.py", "src/b.py"])
    @patch("gac.git.run_git_command")
    @patch("gac.config.load_config", return_value={"model": "openai:gpt-4"})
    @patch("gac.mcp.server._check_git_repo", return_value=(True, ""))
    def test_grouped_message_only(
        self, mock_check, mock_config, mock_git, mock_staged, mock_validator_cls, mock_pb_cls, mock_workflow_cls
    ):
        mock_validator_cls.return_value.get_git_state.return_value = _make_git_state()
        mock_pb_cls.return_value.build_prompts.return_value = _make_prompt_bundle()
        mock_workflow_cls.return_value.generate_grouped_commits_with_retry.return_value = _make_grouped_result()

        result = gac_commit(CommitRequest(group=True, message_only=True))

        assert result.success is True
        assert result.grouped_commits is not None
        assert any("message_only" in w for w in result.warnings)

    @patch("gac.mcp.server._stderr_console_redirect")
    @patch("gac.grouped_commit_workflow.GroupedCommitWorkflow")
    @patch("gac.prompt_builder.PromptBuilder")
    @patch("gac.git_state_validator.GitStateValidator")
    @patch("gac.git.get_staged_files", return_value=["src/a.py", "src/b.py"])
    @patch("gac.git.run_git_command")
    @patch("gac.config.load_config", return_value={"model": "openai:gpt-4"})
    @patch("gac.mcp.server._check_git_repo", return_value=(True, ""))
    def test_grouped_commit_execute(
        self,
        mock_check,
        mock_config,
        mock_git,
        mock_staged,
        mock_validator_cls,
        mock_pb_cls,
        mock_workflow_cls,
        mock_redirect,
    ):
        mock_validator_cls.return_value.get_git_state.return_value = _make_git_state()
        mock_pb_cls.return_value.build_prompts.return_value = _make_prompt_bundle()
        grouped_result = _make_grouped_result()
        mock_workflow_cls.return_value.generate_grouped_commits_with_retry.return_value = grouped_result
        mock_workflow_cls.return_value.execute_grouped_commits.return_value = 0
        mock_redirect.return_value.__enter__ = MagicMock(return_value=None)
        mock_redirect.return_value.__exit__ = MagicMock(return_value=False)

        result = gac_commit(CommitRequest(group=True))

        assert result.success is True
        assert result.grouped_commits is not None
        assert len(result.grouped_commits) == 2
        mock_workflow_cls.return_value.execute_grouped_commits.assert_called_once()

    @patch("gac.grouped_commit_workflow.GroupedCommitWorkflow")
    @patch("gac.prompt_builder.PromptBuilder")
    @patch("gac.git_state_validator.GitStateValidator")
    @patch("gac.git.get_staged_files", return_value=["src/a.py"])
    @patch("gac.git.run_git_command")
    @patch("gac.config.load_config", return_value={"model": "openai:gpt-4"})
    @patch("gac.mcp.server._check_git_repo", return_value=(True, ""))
    def test_grouped_generation_failure_returns_workflow_result(
        self, mock_check, mock_config, mock_git, mock_staged, mock_validator_cls, mock_pb_cls, mock_workflow_cls
    ):
        mock_validator_cls.return_value.get_git_state.return_value = _make_git_state()
        mock_pb_cls.return_value.build_prompts.return_value = _make_prompt_bundle()
        mock_workflow_cls.return_value.generate_grouped_commits_with_retry.return_value = WorkflowResult(
            success=False, exit_code=1
        )

        result = gac_commit(CommitRequest(group=True))

        assert result.success is False
        assert "failed to generate grouped" in result.error.lower()

    @patch("gac.mcp.server._stderr_console_redirect")
    @patch("gac.grouped_commit_workflow.GroupedCommitWorkflow")
    @patch("gac.prompt_builder.PromptBuilder")
    @patch("gac.git_state_validator.GitStateValidator")
    @patch("gac.git.get_staged_files", return_value=["src/a.py", "src/b.py"])
    @patch("gac.git.run_git_command")
    @patch("gac.config.load_config", return_value={"model": "openai:gpt-4"})
    @patch("gac.mcp.server._check_git_repo", return_value=(True, ""))
    def test_grouped_execution_failure(
        self,
        mock_check,
        mock_config,
        mock_git,
        mock_staged,
        mock_validator_cls,
        mock_pb_cls,
        mock_workflow_cls,
        mock_redirect,
    ):
        mock_validator_cls.return_value.get_git_state.return_value = _make_git_state()
        mock_pb_cls.return_value.build_prompts.return_value = _make_prompt_bundle()
        grouped_result = _make_grouped_result()
        mock_workflow_cls.return_value.generate_grouped_commits_with_retry.return_value = grouped_result
        mock_workflow_cls.return_value.execute_grouped_commits.return_value = 1
        mock_redirect.return_value.__enter__ = MagicMock(return_value=None)
        mock_redirect.return_value.__exit__ = MagicMock(return_value=False)

        result = gac_commit(CommitRequest(group=True))

        assert result.success is False
        assert "failed" in result.error.lower()
        assert result.grouped_commits is not None

    @patch("gac.mcp.server._check_git_repo", return_value=(True, ""))
    def test_exception_handling(self, mock_check):
        with patch("gac.config.load_config", side_effect=RuntimeError("config explosion")):
            result = gac_commit(CommitRequest())

        assert result.success is False
        assert "config explosion" in result.error

    @patch("gac.postprocess.clean_commit_message", return_value="feat: secret stuff")
    @patch("gac.ai.generate_commit_message", return_value=("feat: secret stuff", 10, 5, 500, 0))
    @patch("gac.prompt_builder.PromptBuilder")
    @patch("gac.git_state_validator.GitStateValidator")
    @patch("gac.git.get_staged_files", return_value=["src/app.py"])
    @patch("gac.git.run_git_command")
    @patch("gac.config.load_config", return_value={"model": "openai:gpt-4"})
    @patch("gac.mcp.server._check_git_repo", return_value=(True, ""))
    def test_secret_detection_warning(
        self, mock_check, mock_config, mock_git, mock_staged, mock_validator_cls, mock_pb_cls, mock_gen, mock_clean
    ):
        mock_validator_cls.return_value.get_git_state.return_value = _make_git_state(has_secrets=True)
        mock_pb_cls.return_value.build_prompts.return_value = _make_prompt_bundle()

        result = gac_commit(CommitRequest(dry_run=True))

        assert result.success is True
        assert any("secrets" in w.lower() for w in result.warnings)

    @patch("gac.git.get_staged_files", return_value=["a.py"])
    @patch("gac.git.run_git_command")
    @patch("gac.config.load_config", return_value={"model": "openai:gpt-4"})
    @patch("gac.mcp.server._check_git_repo", return_value=(True, ""))
    def test_stage_all_calls_git_add(self, mock_check, mock_config, mock_git, mock_staged):
        mock_git.side_effect = [None, RuntimeError("abort after staging")]
        with patch("gac.git_state_validator.GitStateValidator") as mock_v:
            mock_v.return_value.get_git_state.return_value = None
            gac_commit(CommitRequest(stage_all=True))

        mock_git.assert_any_call(["add", "--all"])

    @patch("gac.postprocess.clean_commit_message", return_value="feat: with model override")
    @patch("gac.ai.generate_commit_message", return_value=("feat: with model override", 10, 5, 500, 0))
    @patch("gac.prompt_builder.PromptBuilder")
    @patch("gac.git_state_validator.GitStateValidator")
    @patch("gac.git.get_staged_files", return_value=["a.py"])
    @patch("gac.git.run_git_command")
    @patch("gac.config.load_config", return_value={})
    @patch("gac.mcp.server._check_git_repo", return_value=(True, ""))
    def test_model_override_from_request(
        self, mock_check, mock_config, mock_git, mock_staged, mock_validator_cls, mock_pb_cls, mock_gen, mock_clean
    ):
        mock_validator_cls.return_value.get_git_state.return_value = _make_git_state()
        mock_pb_cls.return_value.build_prompts.return_value = _make_prompt_bundle()

        result = gac_commit(CommitRequest(model="anthropic:claude-3", dry_run=True))

        assert result.success is True
        mock_gen.assert_called_once()
        assert mock_gen.call_args.kwargs["model"] == "anthropic:claude-3"
