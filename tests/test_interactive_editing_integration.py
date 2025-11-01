"""Integration tests for in-place interactive editing functionality."""

import subprocess
from pathlib import Path
from unittest import mock

import pytest

from gac.main import main


@pytest.mark.integration
class TestInplaceEditingIntegration:
    """Integration tests for in-place editing within main workflow."""

    def test_main_workflow_with_edit_option(self, tmp_path):
        """Test that the 'e' option works within the main workflow."""
        repo_dir = tmp_path / "test_repo"
        repo_dir.mkdir()

        import os

        original_dir = os.getcwd()
        try:
            os.chdir(repo_dir)

            subprocess.run(["git", "init"], check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test User"], check=True, capture_output=True)

            test_file = Path("test.txt")
            test_file.write_text("Initial content\n")
            subprocess.run(["git", "add", "test.txt"], check=True, capture_output=True)

            call_count = {"count": 0}

            def mock_click_prompt(*args, **kwargs):
                call_count["count"] += 1
                if call_count["count"] == 1:
                    return "e"
                return "y"

            with (
                mock.patch("click.prompt", side_effect=mock_click_prompt),
                mock.patch("gac.main.generate_commit_message", return_value="test: initial commit message"),
                mock.patch("gac.utils.prompt", return_value="test: edited commit message"),
                mock.patch.dict("os.environ", {"GAC_MODEL": "anthropic:claude-haiku-4-5"}),
            ):
                try:
                    main(
                        model="anthropic:claude-haiku-4-5", require_confirmation=True, quiet=True, skip_secret_scan=True
                    )
                except SystemExit as e:
                    if e.code != 0:
                        raise

            result = subprocess.run(["git", "log", "-1", "--pretty=%B"], capture_output=True, text=True, check=True)
            commit_message = result.stdout.strip()
            assert commit_message == "test: edited commit message"
        finally:
            os.chdir(original_dir)

    def test_main_workflow_edit_then_regenerate(self, tmp_path):
        """Test edit followed by regeneration in the main workflow."""
        repo_dir = tmp_path / "test_repo"
        repo_dir.mkdir()

        import os

        original_dir = os.getcwd()
        try:
            os.chdir(repo_dir)

            subprocess.run(["git", "init"], check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test User"], check=True, capture_output=True)

            test_file = Path("test.txt")
            test_file.write_text("Content for regeneration test\n")
            subprocess.run(["git", "add", "test.txt"], check=True, capture_output=True)

            responses = iter(["e", "r", "y"])

            def mock_click_prompt(*args, **kwargs):
                return next(responses)

            generation_count = {"count": 0}

            def mock_generate(*args, **kwargs):
                generation_count["count"] += 1
                if generation_count["count"] == 1:
                    return "test: first message"
                return "test: regenerated message"

            with (
                mock.patch("click.prompt", side_effect=mock_click_prompt),
                mock.patch("gac.main.generate_commit_message", side_effect=mock_generate),
                mock.patch("gac.utils.prompt", return_value="test: edited but will regenerate"),
                mock.patch.dict("os.environ", {"GAC_MODEL": "anthropic:claude-haiku-4-5"}),
            ):
                try:
                    main(
                        model="anthropic:claude-haiku-4-5", require_confirmation=True, quiet=True, skip_secret_scan=True
                    )
                except SystemExit as e:
                    if e.code != 0:
                        raise

            result = subprocess.run(["git", "log", "-1", "--pretty=%B"], capture_output=True, text=True, check=True)
            commit_message = result.stdout.strip()
            assert commit_message == "test: regenerated message"
            assert generation_count["count"] == 2
        finally:
            os.chdir(original_dir)

    def test_main_workflow_edit_cancelled(self, tmp_path):
        """Test that cancelling edit preserves the original message."""
        repo_dir = tmp_path / "test_repo"
        repo_dir.mkdir()

        import os

        original_dir = os.getcwd()
        try:
            os.chdir(repo_dir)

            subprocess.run(["git", "init"], check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test User"], check=True, capture_output=True)

            test_file = Path("test.txt")
            test_file.write_text("Content\n")
            subprocess.run(["git", "add", "test.txt"], check=True, capture_output=True)

            responses = iter(["e", "y"])

            def mock_click_prompt(*args, **kwargs):
                return next(responses)

            with (
                mock.patch("click.prompt", side_effect=mock_click_prompt),
                mock.patch("gac.main.generate_commit_message", return_value="test: original message"),
                mock.patch("gac.utils.prompt", side_effect=KeyboardInterrupt()),
                mock.patch.dict("os.environ", {"GAC_MODEL": "anthropic:claude-haiku-4-5"}),
            ):
                try:
                    main(
                        model="anthropic:claude-haiku-4-5", require_confirmation=True, quiet=True, skip_secret_scan=True
                    )
                except SystemExit as e:
                    if e.code != 0:
                        raise

            result = subprocess.run(["git", "log", "-1", "--pretty=%B"], capture_output=True, text=True, check=True)
            commit_message = result.stdout.strip()
            assert commit_message == "test: original message"
        finally:
            os.chdir(original_dir)
