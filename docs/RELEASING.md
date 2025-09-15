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

### 7. Create Release Tag

**This step triggers the automated PyPI release!**

```bash
# Create and push the version tag
git tag v0.15.0  # Use your actual version
git push origin v0.15.0

# GitHub Actions will now:
# 1. Build the package
# 2. Verify version matches tag
# 3. Upload to PyPI
```

Monitor the [Actions tab](https://github.com/cellwebb/gac/actions) to ensure successful publication.

### 8. Post-release

1. **Verify the release on PyPI**:

   - Check [PyPI project page](https://pypi.org/project/gac/)
   - Ensure the new version is listed

2. **Verify Installation**:

   ```bash
   pipx install --force gac
   gac --version
   ```

3. **Update Documentation**:
   - Update README if needed
   - Update installation instructions to reference PyPI

## Automated Releases (GitHub Actions)

The project includes `.github/workflows/publish.yml` for automated releases:

- Triggers when you push a version tag (e.g., `v0.17.3`)
- Verifies the tag version matches `src/gac/__version__.py`
- Automatically builds and publishes to PyPI
- Requires `PYPI_API_TOKEN` secret in repository settings

### How it works

1. Merge your PR(s) to main with version bumped in `src/gac/__version__.py`
2. When ready to release, create and push a tag:

   ```bash
   git checkout main
   git pull
   git tag v0.17.3  # Use your version number
   git push origin v0.17.3
   ```

3. GitHub Actions automatically publishes to PyPI
4. The workflow verifies the tag matches the code version

### Benefits

- Full control over when to release
- Can merge multiple PRs before releasing
- Tags provide clear release history
- Prevents accidental releases

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
