#!/usr/bin/env python3
"""Prompt building logic for gac."""

from typing import NamedTuple

from rich.console import Console
from rich.panel import Panel

from gac.config import GACConfig
from gac.git_state_validator import GitState


class PromptBundle(NamedTuple):
    """Bundle of system and user prompts."""

    system_prompt: str
    user_prompt: str


class PromptBuilder:
    """Builds prompts for AI commit message generation."""

    def __init__(self, config: GACConfig):
        self.config = config

    def build_prompts(
        self,
        git_state: GitState,
        group: bool = False,
        one_liner: bool = False,
        hint: str = "",
        infer_scope: bool = False,
        verbose: bool = False,
        language: str | None = None,
    ) -> PromptBundle:
        """Build prompts from git state."""
        from gac.prompt import build_group_prompt, build_prompt

        # Get language and translate prefixes from config
        if language is None:
            language_value = self.config.get("language")
            language = language_value if isinstance(language_value, str) else None

        translate_prefixes_value = self.config.get("translate_prefixes")
        translate_prefixes: bool = (
            bool(translate_prefixes_value) if isinstance(translate_prefixes_value, bool) else False
        )

        # Get system template path from config
        system_template_path_value = self.config.get("system_prompt_path")
        system_template_path: str | None = (
            system_template_path_value if isinstance(system_template_path_value, str) else None
        )

        if group:
            system_prompt, user_prompt = build_group_prompt(
                status=git_state.status,
                processed_diff=git_state.processed_diff,
                diff_stat=git_state.diff_stat,
                one_liner=one_liner,
                hint=hint,
                infer_scope=infer_scope,
                verbose=verbose,
                system_template_path=system_template_path,
                language=language,
                translate_prefixes=translate_prefixes,
            )
        else:
            system_prompt, user_prompt = build_prompt(
                status=git_state.status,
                processed_diff=git_state.processed_diff,
                diff_stat=git_state.diff_stat,
                one_liner=one_liner,
                hint=hint,
                infer_scope=infer_scope,
                verbose=verbose,
                system_template_path=system_template_path,
                language=language,
                translate_prefixes=translate_prefixes,
            )

        return PromptBundle(system_prompt=system_prompt, user_prompt=user_prompt)

    def display_prompts(self, system_prompt: str, user_prompt: str) -> None:
        """Display prompts for debugging purposes."""
        console = Console()
        full_prompt = f"SYSTEM PROMPT:\n{system_prompt}\n\nUSER PROMPT:\n{user_prompt}"
        console.print(Panel(full_prompt, title="Prompt for LLM", border_style="bright_blue"))
