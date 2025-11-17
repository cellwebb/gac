#!/usr/bin/env python3
"""MCP (Model Context Protocol) server for gac - Git Auto Commit.

This module exposes gac's functionality as an MCP server, allowing AI coding agents
to generate commit messages, stage files, commit changes, and push to remotes.
"""

import json
import logging
import sys
from typing import Any

from mcp.server.fastmcp import FastMCP

from gac.ai import generate_commit_message as ai_generate_commit_message
from gac.config import load_config
from gac.errors import AIError, GitError
from gac.git import (
    get_current_branch,
    get_diff,
    get_repo_root,
    get_staged_files,
    get_staged_status,
    push_changes,
    run_git_command,
)
from gac.preprocess import preprocess_diff
from gac.prompt import build_prompt, clean_commit_message
from gac.security import scan_staged_diff

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("gac")

# Load configuration
config = load_config()


@mcp.tool()
def generate_commit_message(
    hint: str = "",
    one_liner: bool = False,
    verbose: bool = False,
    model: str | None = None,
    language: str | None = None,
    infer_scope: bool = False,
) -> dict[str, Any]:
    """Generate a commit message for the currently staged changes.

    Args:
        hint: Optional hint or context to guide the commit message generation
        one_liner: If True, generate a one-line commit message
        verbose: If True, generate a detailed multi-paragraph commit message
        model: Model to use in format 'provider:model' (e.g. 'anthropic:claude-haiku-4-5')
        language: Language for the commit message (e.g. 'en', 'es', 'fr')
        infer_scope: If True, automatically infer conventional commit scope

    Returns:
        Dictionary containing:
        - success: Whether message generation succeeded
        - message: The generated commit message (if successful)
        - error: Error message (if failed)
        - staged_files: List of staged files
        - model_used: The model that was used
    """
    try:
        # Check if in git repository
        try:
            repo_root = get_repo_root()
            logger.info(f"Working in repository: {repo_root}")
        except GitError as e:
            return {"success": False, "error": str(e)}

        # Get staged files
        staged_files = get_staged_files(existing_only=False)
        if not staged_files:
            return {
                "success": False,
                "error": "No staged changes found. Stage your changes with git add first.",
                "staged_files": [],
            }

        # Use configured model if not specified
        if model is None:
            model_from_config = config.get("model")
            if model_from_config is None:
                return {
                    "success": False,
                    "error": "No model configured. Run 'gac init' or provide a model parameter.",
                }
            model = str(model_from_config)

        # Get configuration values
        temperature = float(config.get("temperature", 0.3))
        max_output_tokens = int(config.get("max_output_tokens", 200))
        max_retries = int(config.get("max_retries", 3))

        # Get git status and diff
        status = get_staged_status()
        diff = run_git_command(["diff", "--staged"])

        # Preprocess diff
        processed_diff = preprocess_diff(diff, model)

        # Build prompt
        system_prompt, user_prompt = build_prompt(
            diff=processed_diff,
            status=status,
            hint=hint,
            one_liner=one_liner,
            verbose=verbose,
            language=language,
            infer_scope=infer_scope,
        )

        # Generate commit message
        logger.info(f"Generating commit message with {model}")
        raw_message = ai_generate_commit_message(
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            max_tokens=max_output_tokens,
            max_retries=max_retries,
            quiet=False,
        )

        # Clean the message
        commit_message = clean_commit_message(raw_message)

        return {
            "success": True,
            "message": commit_message,
            "staged_files": staged_files,
            "model_used": model,
        }

    except Exception as e:
        logger.error(f"Error generating commit message: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


@mcp.tool()
def stage_files(file_paths: list[str]) -> dict[str, Any]:
    """Stage specific files for commit.

    Args:
        file_paths: List of file paths to stage (relative to repository root)

    Returns:
        Dictionary containing:
        - success: Whether staging succeeded
        - staged_files: List of files that were staged
        - error: Error message (if failed)
    """
    try:
        # Check if in git repository
        try:
            get_repo_root()
        except GitError as e:
            return {"success": False, "error": str(e)}

        if not file_paths:
            return {"success": False, "error": "No file paths provided"}

        # Stage each file
        for file_path in file_paths:
            run_git_command(["add", file_path])

        # Get the updated list of staged files
        staged_files = get_staged_files(existing_only=False)

        return {
            "success": True,
            "staged_files": staged_files,
            "message": f"Staged {len(file_paths)} file(s)",
        }

    except Exception as e:
        logger.error(f"Error staging files: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


@mcp.tool()
def stage_all_changes() -> dict[str, Any]:
    """Stage all changes in the repository (equivalent to 'git add --all').

    Returns:
        Dictionary containing:
        - success: Whether staging succeeded
        - staged_files: List of all staged files
        - error: Error message (if failed)
    """
    try:
        # Check if in git repository
        try:
            get_repo_root()
        except GitError as e:
            return {"success": False, "error": str(e)}

        # Stage all changes
        run_git_command(["add", "--all"])

        # Get the updated list of staged files
        staged_files = get_staged_files(existing_only=False)

        return {
            "success": True,
            "staged_files": staged_files,
            "message": f"Staged all changes ({len(staged_files)} file(s))",
        }

    except Exception as e:
        logger.error(f"Error staging all changes: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


@mcp.tool()
def unstage_files(file_paths: list[str]) -> dict[str, Any]:
    """Unstage specific files (equivalent to 'git reset HEAD <file>').

    Args:
        file_paths: List of file paths to unstage (relative to repository root)

    Returns:
        Dictionary containing:
        - success: Whether unstaging succeeded
        - staged_files: List of remaining staged files
        - error: Error message (if failed)
    """
    try:
        # Check if in git repository
        try:
            get_repo_root()
        except GitError as e:
            return {"success": False, "error": str(e)}

        if not file_paths:
            return {"success": False, "error": "No file paths provided"}

        # Unstage each file
        for file_path in file_paths:
            run_git_command(["reset", "HEAD", file_path])

        # Get the updated list of staged files
        staged_files = get_staged_files(existing_only=False)

        return {
            "success": True,
            "staged_files": staged_files,
            "message": f"Unstaged {len(file_paths)} file(s)",
        }

    except Exception as e:
        logger.error(f"Error unstaging files: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


@mcp.tool()
def commit_changes(message: str, no_verify: bool = False) -> dict[str, Any]:
    """Commit staged changes with the provided message.

    Args:
        message: The commit message to use
        no_verify: If True, skip pre-commit and commit-msg hooks

    Returns:
        Dictionary containing:
        - success: Whether commit succeeded
        - commit_hash: The hash of the created commit
        - error: Error message (if failed)
    """
    try:
        # Check if in git repository
        try:
            get_repo_root()
        except GitError as e:
            return {"success": False, "error": str(e)}

        # Check for staged files
        staged_files = get_staged_files(existing_only=False)
        if not staged_files:
            return {
                "success": False,
                "error": "No staged changes to commit",
            }

        if not message or not message.strip():
            return {"success": False, "error": "Commit message cannot be empty"}

        # Build git commit command
        commit_args = ["commit", "-m", message]
        if no_verify:
            commit_args.append("--no-verify")

        # Execute commit
        run_git_command(commit_args)

        # Get the commit hash
        commit_hash = run_git_command(["rev-parse", "HEAD"]).strip()

        return {
            "success": True,
            "commit_hash": commit_hash,
            "message": "Changes committed successfully",
        }

    except Exception as e:
        logger.error(f"Error committing changes: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


@mcp.tool()
def push_to_remote() -> dict[str, Any]:
    """Push commits to the remote repository.

    Returns:
        Dictionary containing:
        - success: Whether push succeeded
        - branch: The current branch that was pushed
        - error: Error message (if failed)
    """
    try:
        # Check if in git repository
        try:
            get_repo_root()
        except GitError as e:
            return {"success": False, "error": str(e)}

        # Get current branch
        try:
            branch = get_current_branch()
        except GitError as e:
            return {"success": False, "error": f"Could not determine current branch: {e}"}

        # Push changes
        success = push_changes()

        if success:
            return {
                "success": True,
                "branch": branch,
                "message": f"Successfully pushed to remote branch '{branch}'",
            }
        else:
            return {
                "success": False,
                "error": "Push failed. Check that you have remote configured and push permissions.",
            }

    except Exception as e:
        logger.error(f"Error pushing to remote: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


@mcp.tool()
def get_git_status() -> dict[str, Any]:
    """Get the status of staged and unstaged files.

    Returns:
        Dictionary containing:
        - success: Whether status retrieval succeeded
        - staged_status: Formatted status of staged files
        - staged_files: List of staged files
        - branch: Current branch name
        - error: Error message (if failed)
    """
    try:
        # Check if in git repository
        try:
            repo_root = get_repo_root()
        except GitError as e:
            return {"success": False, "error": str(e)}

        # Get staged files and status
        staged_files = get_staged_files(existing_only=False)
        staged_status = get_staged_status()

        # Get current branch
        try:
            branch = get_current_branch()
        except GitError:
            branch = "unknown"

        return {
            "success": True,
            "staged_status": staged_status,
            "staged_files": staged_files,
            "branch": branch,
            "repo_root": repo_root,
        }

    except Exception as e:
        logger.error(f"Error getting git status: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


@mcp.tool()
def get_staged_diff_content(color: bool = False) -> dict[str, Any]:
    """Get the diff of staged changes.

    Args:
        color: If True, include ANSI color codes in the diff output

    Returns:
        Dictionary containing:
        - success: Whether diff retrieval succeeded
        - diff: The diff content
        - staged_files: List of staged files
        - error: Error message (if failed)
    """
    try:
        # Check if in git repository
        try:
            get_repo_root()
        except GitError as e:
            return {"success": False, "error": str(e)}

        # Get staged files
        staged_files = get_staged_files(existing_only=False)
        if not staged_files:
            return {
                "success": True,
                "diff": "",
                "staged_files": [],
                "message": "No staged changes",
            }

        # Get diff
        diff = get_diff(staged=True, color=color)

        return {
            "success": True,
            "diff": diff,
            "staged_files": staged_files,
        }

    except Exception as e:
        logger.error(f"Error getting staged diff: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


@mcp.tool()
def scan_staged_for_secrets() -> dict[str, Any]:
    """Scan staged changes for potential secrets (API keys, passwords, etc.).

    Returns:
        Dictionary containing:
        - success: Whether scan completed
        - secrets_found: Whether any secrets were detected
        - secrets: List of detected secrets with details
        - error: Error message (if failed)
    """
    try:
        # Check if in git repository
        try:
            get_repo_root()
        except GitError as e:
            return {"success": False, "error": str(e)}

        # Get staged files
        staged_files = get_staged_files(existing_only=False)
        if not staged_files:
            return {
                "success": True,
                "secrets_found": False,
                "secrets": [],
                "message": "No staged changes to scan",
            }

        # Get diff and scan for secrets
        diff = run_git_command(["diff", "--staged"])
        secrets = scan_staged_diff(diff)

        # Format secrets for output
        formatted_secrets = []
        for secret in secrets:
            formatted_secrets.append(
                {
                    "type": secret.secret_type,
                    "file": secret.file_path,
                    "line": secret.line_number,
                    "matched_text": secret.matched_text,
                }
            )

        return {
            "success": True,
            "secrets_found": len(secrets) > 0,
            "secrets": formatted_secrets,
            "message": f"Scan complete. Found {len(secrets)} potential secret(s).",
        }

    except Exception as e:
        logger.error(f"Error scanning for secrets: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


@mcp.tool()
def generate_and_commit(
    hint: str = "",
    one_liner: bool = False,
    verbose: bool = False,
    model: str | None = None,
    language: str | None = None,
    infer_scope: bool = False,
    no_verify: bool = False,
    auto_push: bool = False,
) -> dict[str, Any]:
    """Generate a commit message and commit changes in one step.

    This is a convenience tool that combines generate_commit_message and commit_changes.

    Args:
        hint: Optional hint or context to guide the commit message generation
        one_liner: If True, generate a one-line commit message
        verbose: If True, generate a detailed multi-paragraph commit message
        model: Model to use in format 'provider:model' (e.g. 'anthropic:claude-haiku-4-5')
        language: Language for the commit message (e.g. 'en', 'es', 'fr')
        infer_scope: If True, automatically infer conventional commit scope
        no_verify: If True, skip pre-commit and commit-msg hooks
        auto_push: If True, automatically push after committing

    Returns:
        Dictionary containing:
        - success: Whether the operation succeeded
        - message: The generated commit message
        - commit_hash: The hash of the created commit
        - pushed: Whether changes were pushed (if auto_push=True)
        - error: Error message (if failed)
    """
    try:
        # First generate the commit message
        gen_result = generate_commit_message(
            hint=hint,
            one_liner=one_liner,
            verbose=verbose,
            model=model,
            language=language,
            infer_scope=infer_scope,
        )

        if not gen_result.get("success"):
            return gen_result

        commit_msg = gen_result.get("message")
        if not commit_msg:
            return {"success": False, "error": "Failed to generate commit message"}

        # Commit with the generated message
        commit_result = commit_changes(message=commit_msg, no_verify=no_verify)

        if not commit_result.get("success"):
            return commit_result

        result = {
            "success": True,
            "message": commit_msg,
            "commit_hash": commit_result.get("commit_hash"),
            "model_used": gen_result.get("model_used"),
        }

        # Push if requested
        if auto_push:
            push_result = push_to_remote()
            result["pushed"] = push_result.get("success", False)
            if push_result.get("success"):
                result["branch"] = push_result.get("branch")
            else:
                result["push_error"] = push_result.get("error")

        return result

    except Exception as e:
        logger.error(f"Error in generate_and_commit: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


# Resources for inspecting git state
@mcp.resource("git://status")
def git_status_resource() -> str:
    """Get the current git status as a resource."""
    result = get_git_status()
    if result.get("success"):
        return json.dumps(result, indent=2)
    else:
        return json.dumps({"error": result.get("error")})


@mcp.resource("git://diff/staged")
def git_diff_staged_resource() -> str:
    """Get the staged diff as a resource."""
    result = get_staged_diff_content(color=False)
    if result.get("success"):
        return result.get("diff", "")
    else:
        return json.dumps({"error": result.get("error")})


@mcp.resource("git://branch")
def git_branch_resource() -> str:
    """Get the current branch name as a resource."""
    try:
        branch = get_current_branch()
        return branch
    except GitError as e:
        return json.dumps({"error": str(e)})


def main():
    """Run the MCP server."""
    try:
        # Run the server via stdio
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
