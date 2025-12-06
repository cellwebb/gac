.PHONY: setup install install-dev dev test test-integration test-all test-cov type-check lint format clean bump bump-patch bump-minor bump-major coverage

PRETTIER ?= npx prettier@3.1.0

# Create virtual environment and install dependencies
setup:
	uv venv
	uv pip install -e ".[dev]"

# Install only runtime dependencies
install:
	uv venv
	uv pip install -e .

# Update dependencies
update:
	uv pip install -U -e ".[dev]"

# Set up development environment
dev:
	@echo "Installing development dependencies..."
	uv venv
	uv pip install -e ".[dev]"
	@echo "Setting up Lefthook git hooks..."
	@if command -v lefthook >/dev/null 2>&1; then \
		lefthook install; \
		lefthook run pre-commit --all || true; \
	else \
		echo "⚠️  Lefthook not found. Install it with 'brew install lefthook' or see docs/CONTRIBUTING.md."; \
	fi
	@echo "✅ Development environment ready!"

test:
	uv run -- pytest

test-integration:
	uv run -- pytest -m integration -v

test-all:
	uv run -- pytest -m ""

test-cov:
	uv run -- python -m pytest --cov=src --cov-report=term --cov-report=html

type-check:
	uv run -- mypy src/gac

lint:
	uv run -- ruff check src/ tests/
	uv run -- ruff format --check src/ tests/
	$(PRETTIER) --check "**/*.{md,yaml,yml,json}"
	npx markdownlint-cli2 --config .markdownlint-cli2.yaml "**/*.md"

format:
	uv run -- ruff check --fix src/ tests/
	uv run -- ruff format src/ tests/
	$(PRETTIER) --write "**/*.{md,yaml,yml,json}"
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
	@# Check for uncommitted changes before starting
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "Error: Git working directory is not clean"; \
		echo "Please commit or stash your changes first"; \
		git status --short; \
		exit 1; \
	fi
	@echo "Bumping $(VERSION) version..."
	@RESULT=$$(BUMP_KIND=$(VERSION) python -c "import os, re; from pathlib import Path; version_file = Path('src/gac/__version__.py'); content = version_file.read_text(encoding='utf-8'); match = re.search(r'__version__ = \"([^\"]+)\"', content); old_version = match.group(1); parts = old_version.split('.'); major, minor, patch = map(int, parts); kind = os.environ['BUMP_KIND']; new_version = f'{major}.{minor}.{patch + 1}' if kind == 'patch' else f'{major}.{minor + 1}.0' if kind == 'minor' else f'{major + 1}.0.0'; version_file.write_text(content.replace(f'__version__ = \"{old_version}\"', f'__version__ = \"{new_version}\"', 1), encoding='utf-8'); print(old_version, new_version)") && \
	OLD_VERSION=$$(echo "$$RESULT" | awk '{print $$1}') && \
	NEW_VERSION=$$(echo "$$RESULT" | awk '{print $$2}') && \
	echo "Version bumped from $$OLD_VERSION to $$NEW_VERSION" && \
	uvx kittylog release $$NEW_VERSION --audience users && \
	git add -A && \
	git commit -m "chore(version): bump version from $$OLD_VERSION to $$NEW_VERSION" && \
	git tag -a "v$$NEW_VERSION" -m "Release version $$NEW_VERSION" && \
	echo "✅ Created tag v$$NEW_VERSION" && \
	echo "📦 To publish: git push && git push --tags"

bump-patch: VERSION=patch
bump-patch: bump

bump-minor: VERSION=minor
bump-minor: bump

bump-major: VERSION=major
bump-major: bump
