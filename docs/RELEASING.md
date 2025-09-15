# Release Process for GAC

This document outlines the process for releasing new versions of GAC to PyPI.

## Prerequisites

1. **PyPI Account**: Create accounts at:

   - [PyPI](https://pypi.org/account/register/)
   - [TestPyPI](https://test.pypi.org/account/register/) (for testing)

2. **API Tokens**: Generate tokens with "Entire account" scope:

   - [PyPI token](https://pypi.org/manage/account/token/)
   - [TestPyPI token](https://test.pypi.org/manage/account/token/)

3. **Configure ~/.pypirc**:

   ```ini
   [testpypi]
   repository = https://test.pypi.org/legacy/
   username = __token__
   password = pypi-AgEIcH...  # your TestPyPI token

   [pypi]
   repository = https://upload.pypi.org/legacy/
   username = __token__
   password = pypi-AgEIcH...  # your PyPI token
   ```

4. **Install Release Tools**:

   ```bash
   uv pip install -e ".[dev]"  # includes build and twine
   ```

## Release Checklist

### 1. Pre-release Checks

- [ ] All tests passing: `pytest`
- [ ] Code formatted: `make format`
- [ ] No uncommitted changes: `git status`
- [ ] On correct branch (usually `main`)
- [ ] Pull latest changes: `git pull`

### 2. Version Bump

**IMPORTANT**: Version must be bumped in the PR for CI to publish!

Update version in `src/gac/__version__.py`:

```python
__version__ = "0.15.0"  # new version
```

Or use `bump-my-version` tool:

```bash
# For bug fixes:
bump-my-version bump patch

# For new features:
bump-my-version bump minor

# For breaking changes:
bump-my-version bump major
```

Version numbering follows semantic versioning:

- MAJOR.MINOR.PATCH (e.g., 1.2.3)
- MAJOR: Breaking changes
- MINOR: New features, backwards compatible
- PATCH: Bug fixes

### 3. Update Changelog

Update `CHANGELOG.md` with:

- Version number and date
- New features
- Bug fixes
- Breaking changes
- Contributors

### 4. Build Distributions

```bash
# Clean old builds
rm -rf dist/ build/ *.egg-info

# Build wheel and source distribution
python -m build

# Verify distributions
twine check dist/*
```

### 5. Test on TestPyPI

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation (in a clean environment)
pip install --index-url https://test.pypi.org/simple/ --no-deps gac

# Verify it works
gac --version
```

### 6. Release to PyPI

```bash
# Upload to real PyPI
twine upload dist/*
```

### 7. Post-release

1. **Verify the release on PyPI**:

   - Check [PyPI project page](https://pypi.org/project/gac/)
   - Ensure the new version is listed

2. **Optional: Create Git tag** (for reference):

   ```bash
   git tag -a v0.15.0 -m "Release version 0.15.0"
   git push origin v0.15.0
   ```

   Note: Tags are optional since CI publishes based on version changes, not tags.

3. **Verify Installation**:

   ```bash
   pipx install --force gac
   gac --version
   ```

4. **Update Documentation**:
   - Update README if needed
   - Update installation instructions to reference PyPI

## Automated Releases (GitHub Actions)

The project includes `.github/workflows/publish.yml` for automated releases:

- Triggers automatically when code is pushed to `main` branch
- **Only publishes if the version in `src/gac/__version__.py` has been bumped**
- Requires `PYPI_API_TOKEN` secret in repository settings
- No manual tagging required

### How it works

1. Create a PR with your changes
2. **Bump the version** in `src/gac/__version__.py`
3. Update `CHANGELOG.md`
4. Merge the PR to main
5. CI automatically publishes to PyPI if version changed

If the version hasn't been bumped, the CI will skip publishing (preventing duplicate uploads).

## Troubleshooting

### 403 Forbidden Error

- Check token has "Entire account" scope
- Verify username is `__token__` (with double underscores)
- Ensure token starts with `pypi-`

### Package Name Conflict

- Check if name exists: `pip search <package-name>`
- Consider alternative names if taken

### Build Issues

- Ensure `build` is installed: `pip install build`
- Check `pyproject.toml` is valid
- Verify all required files are included

## Emergency Rollback

If a bad release is published:

1. **Yank the release** on PyPI (doesn't delete, but prevents new installs)
2. Fix the issue
3. Release a new patch version
4. Never reuse a version number that's been published

## Version Management Tools

For automated version bumping, consider:

- `bump-my-version` (already in dev dependencies)
- Manual updates to `src/gac/__version__.py`

## Security Notes

- Never commit tokens to git
- Use repository secrets for CI/CD
- Rotate tokens periodically
- Use 2FA on PyPI account
