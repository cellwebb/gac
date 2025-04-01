#!/usr/bin/env python3
"""Command-line interface for GAC."""

import logging
import os
import sys
from typing import Optional

import click

from gac.workflow import CommitWorkflow

logger = logging.getLogger(__name__)


@click.command()
@click.option("--test", "-t", is_flag=True, help="Run in test mode without making git commits")
@click.option("--force", "-f", is_flag=True, help="Skip all confirmation prompts")
@click.option("--add-all", "-a", is_flag=True, help="Stage all changes before committing")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-error output")
@click.option("--DEBUG", "log_level_debug", is_flag=True, help="Set log level to DEBUG")
@click.option("--INFO", "log_level_info", is_flag=True, help="Set log level to INFO")
@click.option("--WARNING", "log_level_warning", is_flag=True, help="Set log level to WARNING")
@click.option("--ERROR", "log_level_error", is_flag=True, help="Set log level to ERROR")
@click.option("--no-format", is_flag=True, help="Skip formatting of staged files")
@click.option(
    "--model",
    "-m",
    help="Override the default model (format: 'provider:model_name', e.g. 'ollama:llama3.2')",
)
@click.option("--one-liner", "-o", is_flag=True, help="Generate a single-line commit message")
@click.option(
    "--show-prompt",
    "-s",
    is_flag=True,
    help="Show an abbreviated version of the prompt sent to the LLM",
)
@click.option(
    "--show-prompt-full",
    is_flag=True,
    help="Show the complete prompt sent to the LLM, including full diff",
)
@click.option("--test-with-diff", is_flag=True, help="Test with real staged changes (if any)")
@click.option("--hint", "-h", default="", help="Additional context to include in the prompt")
@click.option(
    "--conventional",
    "-c",
    is_flag=True,
    help="Generate a conventional commit format message",
)
@click.option(
    "--no-spinner",
    is_flag=True,
    help="Disable progress spinner during API calls",
)
@click.option(
    "--local-models",
    is_flag=True,
    help="List available local Ollama models and exit",
)
@click.option(
    "--config-wizard",
    is_flag=True,
    help="Run the interactive configuration wizard",
)
def cli(
    test: bool,
    force: bool,
    add_all: bool,
    quiet: bool,
    log_level_debug: bool,
    log_level_info: bool,
    log_level_warning: bool,
    log_level_error: bool,
    no_format: bool,
    model: Optional[str],
    one_liner: bool,
    show_prompt: bool,
    show_prompt_full: bool,
    test_with_diff: bool,
    hint: str,
    conventional: bool,
    no_spinner: bool,
    local_models: bool,
    config_wizard: bool,
) -> None:
    """Git Auto Commit CLI."""
    # Configuration wizard takes precedence
    if config_wizard:
        from gac.config import run_config_wizard

        config = run_config_wizard()
        if config:
            # Save configuration to environment variables
            os.environ["GAC_MODEL"] = config["model"]
            os.environ["GAC_USE_FORMATTING"] = str(config["use_formatting"]).lower()
            print("Configuration saved successfully!")
        return

    # List local Ollama models and exit
    if local_models:
        list_local_models()
        return

    try:
        # Determine log level from flags
        log_level = logging.INFO  # Default
        verbose = False  # For backward compatibility

        if log_level_debug:
            log_level = logging.DEBUG
            verbose = True  # Map to verbose for backward compatibility
        elif log_level_info:
            log_level = logging.INFO
        elif log_level_warning:
            log_level = logging.WARNING
        elif log_level_error:
            log_level = logging.ERROR

        # Check for environment variable override
        log_level_env = os.environ.get("GAC_LOG_LEVEL")
        if log_level_env:
            log_level_env = log_level_env.upper()
            if log_level_env == "DEBUG":
                log_level = logging.DEBUG
                verbose = True
            elif log_level_env == "INFO":
                log_level = logging.INFO
            elif log_level_env == "WARNING":
                log_level = logging.WARNING
            elif log_level_env == "ERROR":
                log_level = logging.ERROR

        if quiet:
            # Suppress logging for non-error messages
            logging.getLogger().setLevel(logging.ERROR)
        else:
            # Set the determined log level
            logging.getLogger().setLevel(log_level)

        # Configure logging format based on level
        if log_level == logging.DEBUG:
            logging.basicConfig(
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                force=True,
            )
        else:
            logging.basicConfig(
                format="%(levelname)s: %(message)s",
                force=True,
            )

        # Create workflow instance and run it
        workflow = CommitWorkflow(
            test_mode=test,
            force=force,
            add_all=add_all,
            no_format=no_format,
            quiet=quiet,
            verbose=verbose,
            model=model,
            one_liner=one_liner,
            show_prompt=show_prompt,
            show_prompt_full=show_prompt_full,
            test_with_real_diff=test_with_diff,
            hint=hint,
            conventional=conventional,
            no_spinner=no_spinner,
        )
        workflow.run()
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


def list_local_models() -> None:
    """List available local Ollama models."""
    from gac.ai_utils import is_ollama_available
    from gac.utils import print_error, print_info, print_success

    print_info("Checking for local Ollama models...")

    if not is_ollama_available():
        print_error(
            "Ollama is not available. Install from https://ollama.com and make sure it's running."
        )
        print_info("After installing, run 'ollama pull llama3.2' to download a model.")
        return

    try:
        import ollama

        models = ollama.list().get("models", [])

        if not models:
            print_info("No Ollama models found. Run 'ollama pull llama3.2' to download a model.")
            return

        print_success(f"Found {len(models)} Ollama models:")
        for model in models:
            name = model.get("name", "unknown")
            size = model.get("size", 0) // (1024 * 1024)  # Convert to MB
            print_info(f"  - {name} ({size} MB)")

        print_info("\nUse with: gac --model ollama:MODEL_NAME")
    except Exception as e:
        print_error(f"Error listing Ollama models: {e}")
        print_info("Make sure Ollama is installed and running.")


if __name__ == "__main__":
    cli()
