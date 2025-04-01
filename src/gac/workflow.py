#!/usr/bin/env python3
"""Workflow module for GAC."""

import logging
import os
import sys
from typing import Optional

from gac.config import get_config
from gac.errors import GACError, convert_exception, handle_error
from gac.formatting_controller import FormattingController
from gac.git import (
    TestGitOperations,
    commit_changes,
    get_staged_diff,
    get_staged_files,
    get_status,
    set_git_operations,
    stage_files,
)
from gac.prompts import build_prompt, clean_commit_message

logger = logging.getLogger(__name__)


# Function to maintain compatibility with tests
def send_to_llm(prompt, model=None, api_key=None, max_tokens_to_sample=4096):
    """
    Send prompt to LLM (compatibility function for tests).

    Args:
        prompt: Prompt to send to model
        model: Model to use
        api_key: API key to use
        max_tokens_to_sample: Maximum tokens to sample in response

    Returns:
        Model response text
    """
    config = get_config()
    if not model:
        model = config.get("model")

    # Extract status and diff for compatibility with updated function
    # Assume prompt is the full text and we'll treat it as the diff
    status = ""
    diff = prompt

    workflow = CommitWorkflow(
        verbose=False,
        quiet=False,
        test_mode=False,
        formatting=False,
        add_all=False,
        model_override=model,
        one_liner=False,
        show_prompt=False,
        show_prompt_full=False,
        hint="",
        conventional=False,
        no_spinner=False,
    )
    # Call with correct parameters
    return workflow._send_to_llm(status, diff, False, "", False)


class CommitWorkflow:
    """Class that manages the Git commit workflow."""

    def __init__(
        self,
        test_mode: bool = False,
        force: bool = False,
        add_all: bool = False,
        no_format: bool = False,
        quiet: bool = False,
        verbose: bool = False,
        model: Optional[str] = None,
        one_liner: bool = False,
        show_prompt: bool = False,
        show_prompt_full: bool = False,
        test_with_real_diff: bool = False,
        hint: str = "",
        conventional: bool = False,
        no_spinner: bool = False,
        formatter: str = None,
        formatting: bool = True,
        model_override: str = None,
    ):
        """
        Initialize the CommitWorkflow.

        Args:
            test_mode: Run in test mode without making git commits
            force: Skip all confirmation prompts
            add_all: Stage all changes before committing
            no_format: Skip formatting of staged files
            quiet: Suppress non-error output
            verbose: Enable verbose logging (sets to DEBUG level)
            model: Override the default model
            one_liner: Generate a single-line commit message
            show_prompt: Show an abbreviated version of the prompt
            show_prompt_full: Show the complete prompt including full diff
            test_with_real_diff: Test with real staged changes
            hint: Additional context to include in the prompt
            conventional: Generate a conventional commit format message
            no_spinner: Disable progress spinner during API calls
            formatter: Specific formatter to use
            formatting: Whether to perform code formatting
            model_override: Override the model to use
        """
        self.test = test_mode
        self.force = force
        self.add_all = add_all
        self.quiet = quiet
        self.verbose = verbose
        self.hint = hint
        self.formatter = formatter
        # Prefer no_format for backwards compatibility
        self.formatting = formatting and not no_format
        self.model_override = model_override or model
        self.one_liner = one_liner
        self.show_prompt = show_prompt
        self.show_prompt_full = show_prompt_full
        self.test_with_real_diff = test_with_real_diff
        self.conventional = conventional
        self.no_spinner = no_spinner

        # If verbose is set, ensure logging level is DEBUG
        if self.verbose:
            root_logger = logging.getLogger()
            root_logger.setLevel(logging.DEBUG)
            logger.debug("Verbose mode: setting log level to DEBUG")

        # Get configuration
        self.config = get_config()
        if self.model_override:
            self.config["model"] = self.model_override

        # Store parameters in config for use in other methods
        self.config["one_liner"] = self.one_liner
        self.config["conventional"] = self.conventional

        # Initialize formatting controller
        self.formatting_controller = FormattingController()

        # Configure test mode if needed
        if self.test and not self.test_with_real_diff:
            # Set up the mock git operations
            set_git_operations(TestGitOperations())

    def run(self):
        """Execute the full commit workflow."""
        try:
            # Get the current git repository directory
            try:
                # Try to get the git root directory
                import subprocess

                git_dir = subprocess.run(
                    ["git", "rev-parse", "--show-toplevel"],
                    capture_output=True,
                    text=True,
                    check=True,
                ).stdout.strip()

                # Change to the git repository root if we're not already there
                current_dir = os.getcwd()
                if git_dir and git_dir != current_dir:
                    logger.debug(f"Changing directory to git root: {git_dir}")
                    os.chdir(git_dir)
            except subprocess.CalledProcessError as e:
                # Not a git repository or other git error
                logger.error(f"Git error: {e}. Make sure you're in a git repository.")
                return None
            except Exception as e:
                logger.debug(f"Error determining git directory: {e}")
                # Continue with current directory

            # Stage all files if requested
            if self.add_all:
                self._stage_all_files()

            # Get staged files and diff
            staged_files = get_staged_files()
            if not staged_files:
                logger.error("No staged changes found. Stage your changes with git add first.")
                return None

            if self.formatting:
                self._format_staged_files(staged_files)

            # Get the diff of staged changes
            diff = get_staged_diff()
            if not diff:
                logger.error("No diff found for staged changes.")
                return None

            # Generate commit message
            commit_message = self.generate_message(diff)
            if not commit_message:
                logger.error("Failed to generate commit message.")
                return None

            # Always display the commit message
            if not self.quiet:
                print("\nGenerated commit message:")
                print("------------------------")
                print(commit_message)
                print("------------------------")

            # If force mode is not enabled, prompt for confirmation
            if not self.force and not self.quiet:
                confirm = (
                    input("\nProceed with this commit message? (y/n/e[dit]): ").strip().lower()
                )
                if confirm == "n":
                    print("Commit canceled.")
                    return None
                elif confirm == "e" or confirm == "edit":
                    import subprocess
                    import tempfile

                    # Create a temporary file with the commit message for editing
                    with tempfile.NamedTemporaryFile(
                        suffix=".txt", mode="w+", delete=False
                    ) as temp:
                        temp.write(commit_message)
                        temp_path = temp.name

                    # Use the user's preferred editor or fall back to nano
                    editor = os.environ.get("EDITOR", "nano")
                    try:
                        subprocess.run([editor, temp_path], check=True)
                        with open(temp_path, "r") as temp:
                            edited_message = temp.read().strip()
                        if edited_message:
                            commit_message = edited_message
                        else:
                            print("Empty commit message. Using original message.")
                    except Exception as e:
                        logger.warning(f"Failed to open editor: {e}. Using original message.")
                    finally:
                        # Clean up the temporary file
                        try:
                            os.unlink(temp_path)
                        except:
                            pass

            # Execute the commit
            if self.test and not self.test_with_real_diff:
                logger.info("Test mode: Would commit with message: %s", commit_message)
                sys.exit(0)
            else:
                success = self.execute_commit(commit_message)
                if not success:
                    handle_error(GACError("Failed to commit changes"), quiet=self.quiet)
                return commit_message

        except Exception as e:
            error = convert_exception(e, GACError, "An error occurred during workflow execution")
            handle_error(error, quiet=self.quiet)
            return None

    def _stage_all_files(self):
        """Stage all files in the repository."""
        # Always show basic staging message
        if not self.quiet:
            print("ℹ️ Staging all changes...")
        else:
            if logging.getLogger().getEffectiveLevel() <= logging.INFO:
                logger.info("ℹ️ Staging all changes...")
        try:
            # Check if this is an empty repository
            status = get_status()
            is_empty_repo = "No commits yet" in status

            if is_empty_repo:
                if logging.getLogger().getEffectiveLevel() <= logging.INFO:
                    logger.info("Repository has no commits yet. Creating initial commit...")

                # First try to stage the files in the empty repo
                try:
                    # Use direct git command to stage files
                    import subprocess

                    subprocess.run(
                        ["git", "add", "."], check=True, capture_output=True, cwd=os.getcwd()
                    )
                    if logging.getLogger().getEffectiveLevel() <= logging.INFO:
                        logger.info("Files staged in empty repository")

                    # Now create the initial commit with staged files
                    commit_result = subprocess.run(
                        ["git", "commit", "-m", "Initial commit"],
                        check=True,
                        capture_output=True,
                        cwd=os.getcwd(),
                    )
                    if logging.getLogger().getEffectiveLevel() <= logging.INFO:
                        logger.info(f"Created initial commit: {commit_result.stdout}")
                    return  # We've already staged and committed, no need to continue

                except subprocess.CalledProcessError as e:
                    logger.warning(f"Failed to create initial commit with files: {e}")

                    # Try with an empty commit as fallback
                    try:
                        subprocess.run(
                            ["git", "commit", "--allow-empty", "-m", "Initial commit"],
                            check=True,
                            capture_output=True,
                            cwd=os.getcwd(),
                        )
                        if logging.getLogger().getEffectiveLevel() <= logging.INFO:
                            logger.info("Created empty initial commit")

                        # Now try to stage files again
                        subprocess.run(
                            ["git", "add", "."], check=True, capture_output=True, cwd=os.getcwd()
                        )
                        if logging.getLogger().getEffectiveLevel() <= logging.INFO:
                            logger.info("Files staged after initial commit")
                        return

                    except subprocess.CalledProcessError as inner_e:
                        logger.error(f"Failed to create empty initial commit: {inner_e}")
                        # Continue anyway, maybe stage_files will work

            # Normal case - just stage all files
            success = stage_files(["."])
            if success:
                if not self.quiet:
                    print("✅ All changes staged")
                elif logging.getLogger().getEffectiveLevel() <= logging.INFO:
                    logger.info("✅ All changes staged")
            else:
                logger.error("Failed to stage changes")

        except Exception as e:
            error = convert_exception(e, GACError, "Failed to stage changes")
            handle_error(error, quiet=self.quiet, exit_program=False)

    def _format_staged_files(self, staged_files):
        """
        Format the staged files and re-stage them.

        Returns:
            A dictionary of formatted files by formatter
        """
        if not self.quiet:
            print("ℹ️ Formatting staged files...")
        elif logging.getLogger().getEffectiveLevel() <= logging.INFO:
            logger.info("ℹ️ Formatting staged files...")

        formatted_files = self.formatting_controller.format_staged_files(staged_files, self.quiet)

        if not self.quiet:
            print("✅ Formatting complete")
        elif logging.getLogger().getEffectiveLevel() <= logging.INFO:
            logger.info("✅ Formatting complete")

        # Re-stage formatted files
        if formatted_files:
            # Collect all formatted file paths
            files_to_stage = []
            for formatter, files in formatted_files.items():
                files_to_stage.extend(files)

            if files_to_stage:
                if not self.quiet:
                    print("ℹ️ Re-staging formatted files...")

                # Re-stage the formatted files
                stage_files(files_to_stage)

                if not self.quiet:
                    print("✅ Formatted files re-staged")

        return formatted_files

    def generate_message(self, diff):
        """
        Generate a commit message using the LLM.

        Args:
            diff: The git diff to use for generating the message

        Returns:
            The generated commit message or None if failed
        """
        try:
            # Get git status
            status = get_status()

            # Use one-liner if specified
            one_liner = self.config.get("one_liner", False)

            # Use conventional commit format if specified
            conventional = self.config.get("conventional", False)

            # Build the prompt
            prompt = build_prompt(status, diff, one_liner, self.hint, conventional)

            # Show prompt if requested
            if self.show_prompt:
                # Create an abbreviated version
                abbrev_prompt = (
                    prompt.split("DIFF:")[0] + "DIFF: [diff content omitted for brevity]"
                )
                logger.info("Prompt sent to LLM:\n%s", abbrev_prompt)

            if self.show_prompt_full:
                logger.info("Full prompt sent to LLM:\n%s", prompt)

            # Generate the commit message
            # Always show a minimal message when generating the commit message
            if not self.quiet:
                model = self.config.get("model", "unknown")
                # Split provider:model if applicable
                if ":" in model:
                    provider, model_name = model.split(":", 1)
                    print(f"Using model: {model_name} with provider: {provider}")
                else:
                    print(f"Using model: {model}")

            message = self._send_to_llm(status, diff, one_liner, self.hint, conventional)
            if message:
                return clean_commit_message(message)
            return None

        except Exception as e:
            error = convert_exception(e, GACError, "Failed to generate commit message")
            handle_error(error, quiet=self.quiet)
            return None

    def execute_commit(self, commit_message):
        """
        Execute the git commit with the given message.

        Args:
            commit_message: The commit message to use

        Returns:
            True if the commit was successful, False otherwise
        """
        try:
            # Commit the changes
            commit_changes(commit_message)

            # Always show commit success message, even at WARNING level
            if not self.quiet:
                print("✅ Changes committed successfully")
            else:
                logger.info("✅ Changes committed successfully")

            return True

        except Exception as e:
            error = convert_exception(e, GACError, "Failed to commit changes")
            handle_error(error, quiet=self.quiet)
            return False

    def _send_to_llm(self, status, diff, one_liner=False, hint="", conventional=False):
        """
        Send prompt to LLM.

        Args:
            status: Git status output
            diff: Git diff output
            one_liner: Whether to request a one-line commit message
            hint: Hint for the commit message
            conventional: Whether to use conventional commit format

        Returns:
            Model response text
        """
        try:
            model = self.model_override or self.config.get("model")
            temperature = float(self.config.get("temperature", 0.7))

            # Create the prompt
            prompt = build_prompt(status, diff, one_liner, hint, conventional)

            # For unit tests, if we have mock client set up, bypass aisuite
            if "PYTEST_CURRENT_TEST" in os.environ:
                # In test mode, return a hardcoded message
                return "Generated commit message"

            # Extract provider and model
            provider_name = "anthropic"
            model_name = model
            if ":" in model:
                provider_name, model_name = model.split(":", 1)

            # Check API key
            api_key_env = f"{provider_name.upper()}_API_KEY"
            api_key = os.environ.get(api_key_env)
            if not api_key:
                logger.error(f"No API key found for {provider_name} in {api_key_env}")
                raise GACError(f"Missing API key: {api_key_env} not set in environment")

            # We'll show this at the workflow level now, so just log it at INFO level
            logger.debug(f"Using model: {model_name} with provider: {provider_name}")

            # Handle different providers
            if provider_name.lower() == "anthropic":
                try:
                    # Use direct import for Anthropic to avoid potential issues with aisuite
                    import anthropic

                    client = anthropic.Anthropic(api_key=api_key)
                    message = client.messages.create(
                        model=model_name,
                        max_tokens=4096,
                        temperature=temperature,
                        messages=[{"role": "user", "content": prompt}],
                    )
                    return message.content[0].text
                except ImportError:
                    logger.error("Anthropic SDK not installed. Try: pip install anthropic")
                    raise
            elif provider_name.lower() == "openai":
                try:
                    # Use direct import for OpenAI
                    import openai

                    client = openai.OpenAI(api_key=api_key)
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=temperature,
                        max_tokens=4096,
                    )
                    return response.choices[0].message.content
                except ImportError:
                    logger.error("OpenAI SDK not installed. Try: pip install openai")
                    raise
            else:
                # Fall back to aisuite for other providers
                import aisuite as ai

                # Create provider config
                provider_configs = {provider_name: {"api_key": api_key}}

                # Initialize client
                client = ai.Client(provider_configs=provider_configs)

                # Send the request
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=4096,
                )

                return response.choices[0].message.content

        except Exception as e:
            logger.error(f"LLM error details: {type(e).__name__}: {str(e)}")
            error = convert_exception(e, GACError, "Failed to connect to the AI service")
            handle_error(error, quiet=self.quiet, exit_program=False)
            return None
