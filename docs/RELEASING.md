# Release Process for GAC

This document outlines the process for releasing new versions of GAC to PyPI using automated GitHub Actions.

## Overview

GAC uses an automated release process. When you push a version tag to GitHub, a GitHub Actions workflow automatically builds and publishes the package to PyPI. **No manual uploading is required.**

## Prerequisites

1. **Repository Access**: You need push access to the main repository
2. **GitHub Actions**: The repository must have `PYPI_API_TOKEN` configured in secrets (already set up)
3. **Local Tools**:

   ```bash
   uv pip install -e ".[dev]"  # includes make for version management
   ```

## Release Checklist

### 1. Pre-release Checks

- [ ] All tests passing: `make test`
- [ ] Code formatted: `make format`
- [ ] Linting passes: `make lint`
- [ ] No uncommitted changes: `git status`
- [ ] On `main` branch: `git checkout main`
- [ ] Pull latest changes: `git pull origin main`

### 2. Version Bump

Update version in `src/gac/__version__.py`:

```python
__version__ = "2.3.0"  # new version
```

#### Option 1: Manual

Edit the file directly following [Semantic Versioning](https://semver.org/):

- **Patch** (1.6.X): Bug fixes, small improvements
- **Minor** (1.X.0): New features, backwards-compatible changes (e.g., adding a new provider)
- **Major** (X.0.0): Breaking changes

#### Option 2: Using make bump-level

```bash
# For bug fixes:
make bump-patch

# For new features:
make bump-minor

# For breaking changes:
make bump-major
```

### 3. Update Changelog

Update `CHANGELOG.md` with:

- Version number and date
- New features
- Bug fixes
- Breaking changes (if any)
- Contributors

**Example:**

```markdown
## [2.3.0] - 2024-01-15

### Added

- New Z.AI provider support
- Interactive language selection with `gac language`

### Fixed

- Secret scanner false positives for example files

### Changed

- Improved error messages for missing API keys
```

### 4. Commit Version Changes

```bash
# Commit the version bump and changelog
git add src/gac/__version__.py CHANGELOG.md
git commit -m "chore(version): bump from 2.2.0 to 2.3.0"
git push origin main
```

### 5. Create and Push Release Tag

**This step triggers the automated release!**

```bash
# Create the version tag
git tag v2.3.0  # Use your actual version (must match __version__.py)

# Push the tag to GitHub
git push origin v2.3.0
```

**What happens next:**

1. GitHub Actions workflow (`.github/workflows/publish.yml`) is triggered
2. Workflow verifies the tag version matches `src/gac/__version__.py`
3. Package is automatically built using `uv build`
4. Package is automatically published to PyPI using `twine`
5. You'll receive a notification if it fails

Monitor the [Actions tab](https://github.com/cellwebb/gac/actions) to track the release progress.

### 6. Post-release Verification

1. **Check GitHub Actions**:

   - Go to [Actions tab](https://github.com/cellwebb/gac/actions)
   - Verify the "Publish to PyPI" workflow succeeded
   - Check for any errors in the logs

2. **Verify on PyPI**:

   - Check [PyPI project page](https://pypi.org/project/gac/)
   - Ensure the new version is listed
   - Verify package description and metadata look correct

3. **Test Installation**:

   ```bash
   # Install the new version
   uv tool install --reinstall gac

   # Verify version
   gac --version  # Should show the new version
   ```

4. **Create GitHub Release** (optional but recommended):

   - Go to [Releases](https://github.com/cellwebb/gac/releases)
   - Click "Draft a new release"
   - Select your tag
   - Copy changelog entries into the release notes
   - Publish the release

## Automated Workflow Details

### How It Works

The workflow in `.github/workflows/publish.yml`:

1. **Triggers** on tags matching `v[0-9]+.[0-9]+.[0-9]+` (e.g., `v2.3.0`)
2. **Extracts** version from the tag name
3. **Verifies** tag version matches `src/gac/__version__.py`
4. **Builds** the package using `uv build`
5. **Publishes** to PyPI using `twine` with the `PYPI_API_TOKEN` secret

### Benefits

- ✅ No manual uploading required
- ✅ Consistent build environment
- ✅ Automatic version verification
- ✅ Clear audit trail in GitHub Actions logs
- ✅ Can't accidentally publish wrong version
- ✅ Can merge multiple PRs before releasing

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 2.3.0)
- **MAJOR**: Breaking changes (rare)
- **MINOR**: New features, backwards compatible (most releases)
- **PATCH**: Bug fixes, small improvements

**Examples:**

- Adding a new provider: MINOR bump (2.3.0 → 2.4.0)
- Fixing a bug: PATCH bump (2.3.0 → 2.3.1)
- Changing CLI flags: MAJOR bump (2.3.0 → 3.0.0)

## Troubleshooting

### GitHub Actions workflow failed

**Check the logs:**

1. Go to [Actions tab](https://github.com/cellwebb/gac/actions)
2. Click on the failed workflow run
3. Check which step failed

**Common issues:**

- **Version mismatch**: Tag version doesn't match `src/gac/__version__.py`
  - Fix: Delete the tag, update version, create tag again
- **Build failure**: Package build errors
  - Fix: Test build locally with `uv build`, fix errors, push changes
- **PyPI upload failure**: Authentication or duplicate version
  - Fix: Check PyPI token is valid in repository secrets

### Delete a tag (if needed)

If you pushed the wrong tag:

```bash
# Delete local tag
git tag -d v2.3.0

# Delete remote tag
git push --delete origin v2.3.0
```

Then fix the issue and create a new tag.

### Version already exists on PyPI

PyPI doesn't allow re-uploading the same version. If you need to fix a bad release:

1. **Yank the release** on PyPI (prevents new installs)
2. Fix the issue in your code
3. Bump to a new patch version (e.g., 2.3.0 → 2.3.1)
4. Release the new version

**Never reuse a version number that's been published to PyPI.**

### Testing before release

To test the package build without publishing:

```bash
# Clean old builds
rm -rf dist/ build/ *.egg-info

# Build the package
uv build

# Check the distribution
uvx twine check dist/*

# Test installation locally
uv pip install dist/*.whl
```

## Emergency Procedures

### Yanking a Bad Release

If a critical bug is discovered after release:

1. **Yank on PyPI**:

   - Go to [PyPI project page](https://pypi.org/project/gac/)
   - Select the version
   - Click "Options" → "Yank release"
   - Add reason (e.g., "Critical bug in secret scanner")

2. **Release a fix**:
   - Fix the bug
   - Bump to new patch version
   - Follow normal release process

Yanking doesn't delete the release but prevents new installations while allowing existing users to continue.

### Reverting a Release

You **cannot** delete or replace a version on PyPI. Options:

1. **Yank** the bad version (recommended)
2. **Release a fix** as a new patch version
3. **Communicate** the issue to users via GitHub Issues/Discussions

## Security Notes

- ✅ `PYPI_API_TOKEN` is stored in GitHub repository secrets
- ✅ Only maintainers with push access can trigger releases
- ✅ All releases are logged in GitHub Actions
- ✅ Never commit tokens to git
- ✅ Rotate tokens periodically

## Quick Reference

```bash
# Complete release process (assuming version already bumped)
git checkout main
git pull origin main
git tag v2.3.0
git push origin v2.3.0

# Monitor release
open https://github.com/cellwebb/gac/actions

# Verify after release
uv tool install --reinstall gac
gac --version
```

## Need Help?

- Check [GitHub Actions logs](https://github.com/cellwebb/gac/actions)
- Review [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
- Open an issue if you encounter problems
