import logging
from logging import getLogger
from pathlib import Path
from typing import Optional

from gac.ai import AI
from gac.repo_context import RepoContext

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = getLogger(__name__)


def get_repo_context(repo_path: Path, ai: AI) -> Optional[RepoContext]:
    try:
        logger.info("Creating RepoContext instance...")
        context = RepoContext(repo_path, ai)
        logger.info("Successfully created RepoContext")
        return context
    except Exception as e:
        logger.error(f"Failed to create RepoContext: {e}")
        return None


def main():
    logger.info("Repository Context Enrichment Example")
    logger.info("=" * 40)
    logger.info("\n")

    ai = AI()

    repo_path = Path(__file__).parent.parent
    logger.info(f"Using repository path: {repo_path}")

    context = get_repo_context(repo_path, ai)
    if context is None:
        logger.error("Failed to get repository context")
        return

    logger.info("Getting repository context...")
    repo_context = context.get_repo_context()
    logger.info("Repository context retrieved successfully")

    logger.info("\nRepository Context:")
    logger.info("-" * 40)
    for key, value in repo_context.items():
        logger.info(f"{key}: {value}")

    logger.info("\nGetting file context...")
    file_path = Path(__file__)
    file_context = context.get_file_context(file_path)
    logger.info("File context retrieved successfully")

    logger.info("\nFile Context:")
    logger.info("-" * 40)
    for key, value in file_context.items():
        logger.info(f"{key}: {value}")


if __name__ == "__main__":
    main()
