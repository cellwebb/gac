"""Workflow context objects to reduce parameter explosion.

These dataclasses bundle related parameters that are passed through
the commit workflow, making function signatures cleaner and more maintainable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gac.commit_executor import CommitExecutor
    from gac.git_state_validator import GitState
    from gac.interactive_mode import InteractiveMode
    from gac.prompt_builder import PromptBundle


@dataclass(frozen=True)
class CLIOptions:
    """Options passed from CLI to main workflow.

    Bundles all command-line arguments to reduce parameter explosion in main().
    """

    # Git workflow options
    stage_all: bool = False
    push: bool = False
    no_verify: bool = False
    hook_timeout: int = 120

    # Workflow mode
    group: bool = False
    interactive: bool = False
    require_confirmation: bool = True
    dry_run: bool = False

    # AI/Model config
    model: str | None = None

    # Prompt/output format config
    hint: str = ""
    one_liner: bool = False
    infer_scope: bool = False
    verbose: bool = False
    language: str | None = None

    # Output config
    quiet: bool = False
    message_only: bool = False
    show_prompt: bool = False

    # Security
    skip_secret_scan: bool = False


@dataclass(frozen=True)
class GenerationConfig:
    """Configuration for AI message generation.

    These settings control how the AI model generates commit messages.
    """

    model: str
    temperature: float
    max_output_tokens: int
    max_retries: int


@dataclass(frozen=True)
class WorkflowFlags:
    """Boolean flags controlling workflow behavior.

    These flags determine how the commit workflow executes.
    """

    require_confirmation: bool
    quiet: bool
    no_verify: bool
    dry_run: bool
    message_only: bool
    push: bool
    show_prompt: bool
    interactive: bool
    hook_timeout: int = 120


@dataclass
class WorkflowState:
    """Runtime state for a commit workflow.

    Contains the prompts, git state, and executor instances needed
    to execute the workflow. This is mutable as conversation messages
    may be updated during interactive flows.
    """

    prompts: PromptBundle
    git_state: GitState
    hint: str
    commit_executor: CommitExecutor
    interactive_mode: InteractiveMode


@dataclass(frozen=True)
class WorkflowContext:
    """Complete context for executing a commit workflow.

    Bundles all configuration, flags, and state needed to execute
    a single or grouped commit workflow.
    """

    config: GenerationConfig
    flags: WorkflowFlags
    state: WorkflowState

    @property
    def model(self) -> str:
        return self.config.model

    @property
    def temperature(self) -> float:
        return self.config.temperature

    @property
    def max_output_tokens(self) -> int:
        return self.config.max_output_tokens

    @property
    def max_retries(self) -> int:
        return self.config.max_retries

    @property
    def quiet(self) -> bool:
        return self.flags.quiet

    @property
    def dry_run(self) -> bool:
        return self.flags.dry_run

    @property
    def message_only(self) -> bool:
        return self.flags.message_only

    @property
    def interactive(self) -> bool:
        return self.flags.interactive

    @property
    def system_prompt(self) -> str:
        return self.state.prompts.system_prompt

    @property
    def user_prompt(self) -> str:
        return self.state.prompts.user_prompt

    @property
    def hint(self) -> str:
        return self.state.hint

    @property
    def git_state(self) -> GitState:
        return self.state.git_state
