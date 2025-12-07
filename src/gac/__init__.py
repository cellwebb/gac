"""Git Auto Commit (gac) - Generate commit messages using AI."""

from gac import init_cli
from gac.__version__ import __version__
from gac.ai import generate_commit_message
from gac.prompt import build_prompt

__all__ = [
    "__version__",
    "build_prompt",
    "generate_commit_message",
    "init_cli",
]
