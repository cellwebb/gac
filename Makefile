.PHONY: setup install install-dev test lint format clean bump bump-patch bump-minor bump-major bump-alpha bump-beta bump-rc coverage

# Create virtual environment and install dependencies
setup:
	uv venv
	uv pip install -e ".[dev]"

# Install only runtime dependencies
install:
	uv pip install -e .

# Update dependencies
update:
	uv pip install -U -e ".[dev]"

# Install with development dependencies
install-dev:
	uv pip install -e ".[dev]"

test:
	uv run -- pytest

test-cov:
	uv run -- python -m pytest --cov=src --cov-report=term --cov-report=html

lint:
	uv run -- black --check src/ tests/
	uv run -- isort --check src/ tests/
	npx prettier --check "**/*.{md,yaml,yml,json}" --log-level silent
	npx markdownlint-cli2 --config .markdownlint-cli2.yaml "**/*.md"
	uv run -- flake8 --max-line-length=120 --ignore=E203,W503 src/ tests/

format:
	uv run -- black src/ tests/
	uv run -- isort src/ tests/
	npx prettier --write "**/*.{md,yaml,yml,json}" --log-level silent
	npx markdownlint-cli2 --fix --config .markdownlint-cli2.yaml "**/*.md"

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Version bumping
bump:
	@git diff --exit-code || (echo "Git working directory is not clean" && exit 1)
	@echo "Bumping $(VERSION) version..."
	@OLD_VERSION=$$(grep 'current_version' .bumpversion.toml | cut -d '"' -f2) && \
	bump-my-version bump $(VERSION) --no-commit --no-tag && \
	NEW_VERSION=$$(grep 'current_version' .bumpversion.toml | cut -d '"' -f2) && \
	echo "Version bumped from $$OLD_VERSION to $$NEW_VERSION" && \
	python scripts/prep_changelog_for_release.py CHANGELOG.md $$NEW_VERSION && \
	git add -A && \
	git commit -m "chore: bump version to $$NEW_VERSION" && \
	git tag -a "v$$NEW_VERSION" -m "Release version $$NEW_VERSION" && \
	echo "Created tag v$$NEW_VERSION" && \
	echo "To publish: git push && git push --tags"

bump-patch: VERSION=patch
bump-patch: bump

bump-minor: VERSION=minor
bump-minor: bump

bump-major: VERSION=major
bump-major: bump
