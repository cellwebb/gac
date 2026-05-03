"""Simple targeted tests to improve grouped_commit_workflow.py coverage.

Focuses on high-impact missing areas with minimal mocking.
"""

from unittest import mock

from gac.config import GACConfig
from gac.errors import GitError
from gac.git import GitCommandResult
from gac.grouped_commit_workflow import GroupedCommitResult, GroupedCommitWorkflow, WorkflowResult
from gac.workflow_context import GenerationConfig, WorkflowContext, WorkflowFlags, WorkflowState


def _build_ctx(
    show_prompt: bool = False,
    interactive: bool = False,
    require_confirmation: bool = False,
    quiet: bool = False,
) -> WorkflowContext:
    """Build a WorkflowContext for testing execute_workflow."""
    mock_git_state = mock.Mock()
    mock_prompts = mock.Mock()
    mock_prompts.system_prompt = "System prompt" if show_prompt else "System"
    mock_prompts.user_prompt = "User prompt" if show_prompt else "User"
    mock_commit_executor = mock.Mock()
    mock_interactive_mode = mock.Mock()

    return WorkflowContext(
        config=GenerationConfig(
            model="openai:gpt-4",
            temperature=0.7,
            max_output_tokens=1000,
            max_retries=3,
        ),
        flags=WorkflowFlags(
            require_confirmation=require_confirmation,
            quiet=quiet,
            no_verify=False,
            dry_run=False,
            message_only=False,
            push=False,
            show_prompt=show_prompt,
            interactive=interactive,
            hook_timeout=120,
            fifty_seventy_two=False,
            signoff=False,
        ),
        state=WorkflowState(
            prompts=mock_prompts,
            git_state=mock_git_state,
            hint="some hint" if interactive else "",
            commit_executor=mock_commit_executor,
            interactive_mode=mock_interactive_mode,
        ),
    )


def test_push_failure_returns_false():
    """Test push_changes returning False triggers restore."""
    config = GACConfig({"warning_limit_tokens": 4096})
    workflow = GroupedCommitWorkflow(config)

    result = GroupedCommitResult(
        commits=[{"files": ["file1.py"], "message": "Test commit"}],
        raw_response="test response",
    )

    with mock.patch("gac.grouped_commit_executor.get_staged_files", return_value=["file1.py"]):
        with mock.patch("gac.grouped_commit_executor.run_git_command", return_value=GitCommandResult.ok("diff data")):
            with mock.patch("gac.grouped_commit_executor.detect_rename_mappings", return_value={}):
                with mock.patch("gac.grouped_commit_executor.execute_commit"):
                    with mock.patch("gac.git.push_changes", return_value=False):
                        with mock.patch("gac.grouped_commit_executor.restore_staging") as mock_restore:
                            with mock.patch("gac.grouped_commit_executor.console.print"):
                                exit_code = workflow.execute_grouped_commits(
                                    result=result,
                                    dry_run=False,
                                    push=True,
                                    no_verify=False,
                                    hook_timeout=120,
                                )

    assert exit_code == 1
    mock_restore.assert_called_once()


def test_push_git_error_triggers_restore():
    """Test GitError during push triggers restore."""
    config = GACConfig({"warning_limit_tokens": 4096})
    workflow = GroupedCommitWorkflow(config)

    result = GroupedCommitResult(
        commits=[{"files": ["file1.py"], "message": "Test commit"}],
        raw_response="test response",
    )

    with mock.patch("gac.grouped_commit_executor.get_staged_files", return_value=["file1.py"]):
        with mock.patch("gac.grouped_commit_executor.run_git_command", return_value=GitCommandResult.ok("diff data")):
            with mock.patch("gac.grouped_commit_executor.detect_rename_mappings", return_value={}):
                with mock.patch("gac.grouped_commit_executor.execute_commit"):
                    with mock.patch("gac.git.push_changes", side_effect=GitError("push failed")):
                        with mock.patch("gac.grouped_commit_executor.restore_staging") as mock_restore:
                            with mock.patch("gac.grouped_commit_executor.console.print"):
                                exit_code = workflow.execute_grouped_commits(
                                    result=result,
                                    dry_run=False,
                                    push=True,
                                    no_verify=False,
                                    hook_timeout=120,
                                )

    assert exit_code == 1
    mock_restore.assert_called_once()


def test_push_os_error_triggers_restore():
    """Test OSError during push triggers restore."""
    config = GACConfig({"warning_limit_tokens": 4096})
    workflow = GroupedCommitWorkflow(config)

    result = GroupedCommitResult(
        commits=[{"files": ["file1.py"], "message": "Test commit"}],
        raw_response="test response",
    )

    with mock.patch("gac.grouped_commit_executor.get_staged_files", return_value=["file1.py"]):
        with mock.patch("gac.grouped_commit_executor.run_git_command", return_value=GitCommandResult.ok("diff data")):
            with mock.patch("gac.grouped_commit_executor.detect_rename_mappings", return_value={}):
                with mock.patch("gac.grouped_commit_executor.execute_commit"):
                    with mock.patch("gac.git.push_changes", side_effect=OSError("os error")):
                        with mock.patch("gac.grouped_commit_executor.restore_staging") as mock_restore:
                            with mock.patch("gac.grouped_commit_executor.console.print"):
                                exit_code = workflow.execute_grouped_commits(
                                    result=result,
                                    dry_run=False,
                                    push=True,
                                    no_verify=False,
                                    hook_timeout=120,
                                )

    assert exit_code == 1
    mock_restore.assert_called_once()


def test_push_success():
    """Test successful push after commits."""
    config = GACConfig({"warning_limit_tokens": 4096})
    workflow = GroupedCommitWorkflow(config)

    result = GroupedCommitResult(
        commits=[{"files": ["file1.py"], "message": "Test commit"}],
        raw_response="test response",
    )

    with mock.patch("gac.grouped_commit_executor.get_staged_files", return_value=["file1.py"]):
        with mock.patch("gac.grouped_commit_executor.run_git_command", return_value=GitCommandResult.ok("diff data")):
            with mock.patch("gac.grouped_commit_executor.detect_rename_mappings", return_value={}):
                with mock.patch("gac.grouped_commit_executor.execute_commit"):
                    with mock.patch("gac.git.push_changes", return_value=True):
                        with mock.patch("gac.grouped_commit_executor.console.print"):
                            exit_code = workflow.execute_grouped_commits(
                                result=result,
                                dry_run=False,
                                push=True,
                                no_verify=False,
                                hook_timeout=120,
                            )

    assert exit_code == 0


def test_execute_workflow_show_prompt():
    """Test that show_prompt displays the prompt panel."""
    config = GACConfig({"warning_limit_tokens": 4096})
    workflow = GroupedCommitWorkflow(config)
    ctx = _build_ctx(show_prompt=True)

    with mock.patch("gac.grouped_commit_executor.get_staged_files", return_value=["file1.py"]):
        with mock.patch("gac.grouped_commit_executor.console.print") as mock_print:
            with mock.patch.object(
                workflow,
                "generate_grouped_commits_with_retry",
                return_value=WorkflowResult(success=True, exit_code=0),
            ):
                exit_code = workflow.execute_workflow(ctx, config)

    assert exit_code == 0
    assert mock_print.call_count >= 1
    first_call_arg = mock_print.call_args_list[0][0][0]
    from rich.panel import Panel

    assert isinstance(first_call_arg, Panel)
    assert first_call_arg.title == "Prompt for LLM"


def test_execute_workflow_interactive_mode():
    """Test that interactive mode invokes InteractiveMode."""
    config = GACConfig({"warning_limit_tokens": 4096})
    workflow = GroupedCommitWorkflow(config)
    ctx = _build_ctx(interactive=True)

    with mock.patch("gac.grouped_commit_executor.get_staged_files", return_value=["file1.py"]):
        with mock.patch("gac.grouped_commit_executor.console.print"):
            with mock.patch.object(
                workflow,
                "generate_grouped_commits_with_retry",
                return_value=WorkflowResult(success=True, exit_code=0),
            ):
                exit_code = workflow.execute_workflow(ctx, config)

    assert exit_code == 0
    ctx.state.interactive_mode.handle_interactive_flow.assert_called_once()


def test_execute_workflow_accept_decision():
    """Test execute_workflow when user accepts commits."""
    config = GACConfig({"warning_limit_tokens": 4096})
    workflow = GroupedCommitWorkflow(config)
    ctx = _build_ctx(require_confirmation=True)

    grouped_result = GroupedCommitResult(
        commits=[{"files": ["file1.py"], "message": "Test"}],
        raw_response="test",
    )

    with mock.patch("gac.grouped_commit_executor.get_staged_files", return_value=["file1.py"]):
        with mock.patch("gac.grouped_commit_executor.console.print"):
            with mock.patch("gac.grouped_commit_workflow.count_tokens", return_value=100):
                with mock.patch.object(
                    workflow,
                    "generate_grouped_commits_with_retry",
                    return_value=WorkflowResult(success=True, result=grouped_result),
                ):
                    with mock.patch.object(workflow, "display_grouped_commits"):
                        with mock.patch.object(workflow, "handle_grouped_commit_confirmation", return_value="accept"):
                            with mock.patch.object(workflow, "execute_grouped_commits", return_value=0) as mock_exec:
                                exit_code = workflow.execute_workflow(ctx, config)

    assert exit_code == 0
    mock_exec.assert_called_once()


def test_execute_workflow_reject_decision():
    """Test execute_workflow when user rejects commits."""
    config = GACConfig({"warning_limit_tokens": 4096})
    workflow = GroupedCommitWorkflow(config)
    ctx = _build_ctx(require_confirmation=True)

    grouped_result = GroupedCommitResult(
        commits=[{"files": ["file1.py"], "message": "Test"}],
        raw_response="test",
    )

    with mock.patch("gac.grouped_commit_executor.get_staged_files", return_value=["file1.py"]):
        with mock.patch("gac.grouped_commit_executor.console.print"):
            with mock.patch("gac.grouped_commit_workflow.count_tokens", return_value=100):
                with mock.patch.object(
                    workflow,
                    "generate_grouped_commits_with_retry",
                    return_value=WorkflowResult(success=True, result=grouped_result),
                ):
                    with mock.patch.object(workflow, "display_grouped_commits"):
                        with mock.patch.object(workflow, "handle_grouped_commit_confirmation", return_value="reject"):
                            exit_code = workflow.execute_workflow(ctx, config)

    assert exit_code == 0


def test_execute_workflow_regenerate_then_accept():
    """Test execute_workflow regenerate loop then accept."""
    config = GACConfig({"warning_limit_tokens": 4096})
    workflow = GroupedCommitWorkflow(config)
    ctx = _build_ctx(require_confirmation=True)

    grouped_result = GroupedCommitResult(
        commits=[{"files": ["file1.py"], "message": "Test"}],
        raw_response="test",
    )

    call_count = 0

    def mock_confirmation(result, conversation_messages):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return "regenerate"
        return "accept"

    with mock.patch("gac.grouped_commit_executor.get_staged_files", return_value=["file1.py"]):
        with mock.patch("gac.grouped_commit_executor.console.print"):
            with mock.patch("gac.grouped_commit_workflow.count_tokens", return_value=100):
                with mock.patch.object(
                    workflow,
                    "generate_grouped_commits_with_retry",
                    return_value=WorkflowResult(success=True, result=grouped_result),
                ):
                    with mock.patch.object(workflow, "display_grouped_commits"):
                        with mock.patch.object(
                            workflow, "handle_grouped_commit_confirmation", side_effect=mock_confirmation
                        ):
                            with mock.patch.object(workflow, "execute_grouped_commits", return_value=0):
                                exit_code = workflow.execute_workflow(ctx, config)

    assert exit_code == 0
    assert call_count == 2


def test_execute_workflow_no_confirmation():
    """Test execute_workflow with require_confirmation=False executes directly."""
    config = GACConfig({"warning_limit_tokens": 4096})
    workflow = GroupedCommitWorkflow(config)
    ctx = _build_ctx(require_confirmation=False)

    grouped_result = GroupedCommitResult(
        commits=[{"files": ["file1.py"], "message": "Test"}],
        raw_response="test",
    )

    with mock.patch("gac.grouped_commit_executor.get_staged_files", return_value=["file1.py"]):
        with mock.patch("gac.grouped_commit_executor.console.print"):
            with mock.patch("gac.grouped_commit_workflow.count_tokens", return_value=100):
                with mock.patch.object(
                    workflow,
                    "generate_grouped_commits_with_retry",
                    return_value=WorkflowResult(success=True, result=grouped_result),
                ):
                    with mock.patch.object(workflow, "display_grouped_commits"):
                        with mock.patch.object(workflow, "execute_grouped_commits", return_value=0) as mock_exec:
                            exit_code = workflow.execute_workflow(ctx, config)

    assert exit_code == 0
    mock_exec.assert_called_once()
