---
name: pypi-publish
description: "This skill should be used when the user asks to \"publish to PyPI\", \"upload to PyPI\", \"PyPI release\", \"publish my Python package\", \"package for PyPI\", \"submit to PyPI\", \"PyPI submission\", or mentions PyPI publishing. It guides the complete workflow: auditing package metadata, running tests, building distributions, testing on TestPyPI, and publishing to PyPI."
---

# PyPI Package Publication

Guide the complete workflow for publishing a Python package to the Python Package Index (PyPI). This skill audits package metadata, verifies tests pass, builds distributions, tests on TestPyPI, and handles the final publication.

## Workflow

### 1. Locate the Package

Identify the Python package to publish. Use Glob tool to search for:
- `pyproject.toml` (modern standard)
- `setup.py` (legacy)
- `setup.cfg` (legacy configuration)

If multiple build configuration files exist, prefer `pyproject.toml`. If no package configuration is found, ask the user which package to publish.

### 2. Load User Config

Read `.claude/pub-pipeline.local.md` if it exists (Read tool). Extract `python.pypi_username` from YAML frontmatter. If the file is missing, inform the user and offer to create one from the template at `${CLAUDE_PLUGIN_ROOT}/docs/user-config-template.md`.

### 3. Audit Package Metadata

Read the package configuration file(s) and verify all required metadata fields are present and properly formatted.

**Required fields** (Read tool):

| Field | Check |
|-------|-------|
| `name` | Present, follows PyPI naming rules (lowercase, hyphens/underscores only) |
| `version` | Present, follows PEP 440 (e.g., "1.0.0", "0.1.0a1") |
| `description` | Present, concise one-line summary |
| `readme` | Points to existing README file (README.md, README.rst) |
| `license` | Specified via SPDX identifier or license file |
| `authors` or `maintainers` | At least one with name and email |
| `urls` | Homepage, documentation, repository, bug tracker |
| `classifiers` | Development status, intended audience, license, Python versions |
| `python_requires` | Minimum Python version (e.g., ">=3.8") |

**Recommended fields**:
- `keywords` — searchability on PyPI
- `dependencies` — runtime requirements
- `optional-dependencies` — extras like `dev`, `test`, `docs`

### 4. Check README Renders Correctly

Verify the README file renders as valid Markdown or reStructuredText and will display correctly on PyPI.

**Build and validate** (Bash tool):
```bash
cd /path/to/package && python -m build && twine check dist/*
```

This creates source distribution and wheel, then validates that PyPI will accept the long description. Any rendering errors must be fixed before proceeding.

### 5. Verify Tests Exist and Pass

Confirm the package has a test suite and all tests pass.

**Run tests** (Bash tool):
```bash
cd /path/to/package && python -m pytest
```

If pytest is not the test runner, try:
```bash
cd /path/to/package && python -m unittest discover
```

If tests fail, stop and report the failures. Do not proceed with publishing.

### 6. Check Version Not Already Published

Verify the version number has been bumped and does not conflict with an existing PyPI release.

**Check PyPI** (Bash tool):
```bash
pip index versions package-name
```

If the current version already exists on PyPI, inform the user. PyPI does not allow re-uploading the same version number. The version must be incremented.

### 7. Build Distributions

Build source distribution (sdist) and wheel (bdist_wheel).

**Clean and build** (Bash tool):
```bash
cd /path/to/package && rm -rf dist/* && python -m build
```

Important: Always clean `dist/` before building to avoid uploading stale artifacts from previous builds.

Verify that `dist/` now contains:
- `package-name-X.Y.Z.tar.gz` (source distribution)
- `package_name-X.Y.Z-py3-none-any.whl` (wheel)

### 8. Test Upload to TestPyPI

Upload to TestPyPI (test.pypi.org) to verify the upload process and package metadata before publishing to production PyPI.

**Upload to TestPyPI** (Bash tool):
```bash
cd /path/to/package && twine upload --repository testpypi dist/*
```

User will be prompted for TestPyPI credentials:
- Username: `__token__`
- Password: TestPyPI API token (starts with `pypi-`)

If the user does not have a TestPyPI account or token, provide instructions:
1. Create account at https://test.pypi.org/account/register/
2. Generate API token at https://test.pypi.org/manage/account/token/
3. Store token in `~/.pypirc` or enter when prompted

### 9. Test Install from TestPyPI

Verify the package installs correctly from TestPyPI.

**Install from TestPyPI** (Bash tool):
```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ package-name
```

The `--extra-index-url` flag allows dependencies to be installed from production PyPI while the target package comes from TestPyPI.

**Verify installation**:
```bash
python -c "import package_name; print(package_name.__version__)"
```

If import fails or version is incorrect, investigate and fix before publishing to production PyPI.

### 10. Publish to PyPI

Upload to production PyPI.

**Final upload** (Bash tool):
```bash
cd /path/to/package && twine upload dist/*
```

User will be prompted for PyPI credentials:
- Username: `__token__`
- Password: PyPI API token (starts with `pypi-`)

If the user does not have a PyPI account or token, provide instructions:
1. Create account at https://pypi.org/account/register/
2. Generate API token at https://pypi.org/manage/account/token/
3. Scope the token to this specific project (recommended) or use account-wide token
4. Store token in `~/.pypirc` for future uploads

### 11. Post-Publication Tasks

After successful publication, verify the package is installable and complete post-release tasks.

**Verify installation** (Bash tool):
```bash
pip install package-name
python -c "import package_name; print(package_name.__version__)"
```

**Create GitHub release** (Bash tool):
```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
gh release create vX.Y.Z --title "vX.Y.Z" --notes "PyPI release: https://pypi.org/project/package-name/X.Y.Z/"
```

**Additional recommendations**:
- Update project documentation with installation instructions
- Announce release on relevant channels (blog, social media, mailing lists)
- Monitor PyPI project page for download statistics
- Set up GitHub Actions for automated publishing (see Trusted Publishers below)

### 12. Produce Audit Report

Format the pre-publication audit as a structured markdown report:

```markdown
# PyPI Audit Report: {package name} v{version}

## Summary
- **Status**: READY / NEEDS WORK / NOT READY
- **PyPI URL**: https://pypi.org/project/{package-name}/
- **TestPyPI**: Tested / Not tested
- **Checks**: X/Y passed

## Metadata Audit

### Required Fields
- [x] or [ ] name
- [x] or [ ] version
- [x] or [ ] description
- [x] or [ ] readme
- [x] or [ ] license
- [x] or [ ] authors/maintainers
- [x] or [ ] urls
- [x] or [ ] classifiers
- [x] or [ ] python_requires

### Recommended Fields
- [x] or [ ] keywords
- [x] or [ ] dependencies
- [x] or [ ] optional-dependencies

## Quality Checks
- [x] or [ ] README renders correctly (twine check)
- [x] or [ ] Tests exist and pass
- [x] or [ ] Version not yet on PyPI
- [x] or [ ] Build succeeds (sdist + wheel)

## Issues Found

### Critical (Must Fix Before Publishing)
1. [Issue description] — [how to fix]

### Warnings (Should Fix)
1. [Issue description] — [recommendation]

## Recommended Next Steps
1. [Ordered list of actions]
```

## Reference Files

For complete PyPI requirements, metadata specifications, and publishing best practices, consult:
- **`${CLAUDE_PLUGIN_ROOT}/docs/pypi-reference.md`** — Full PyPI metadata requirements, TestPyPI workflow, trusted publisher setup, and common rejection reasons

## Important Notes

- **Version immutability**: Once a version is published to PyPI, it cannot be deleted or re-uploaded. Increment the version for any changes. Use `X.Y.Z.postN` for post-release fixes or `X.Y.Z+1` for new features.

- **Clean dist/ before building**: Always `rm -rf dist/*` before running `python -m build`. Stale artifacts from previous builds can cause confusion or upload wrong files.

- **Authentication with `__token__`**: When prompted for username, always use `__token__` (literal string). The password is the API token. Never commit tokens to version control.

- **Trusted Publishers (GitHub Actions OIDC)**: For automated publishing from GitHub Actions, set up a Trusted Publisher at https://pypi.org/manage/account/publishing/. This eliminates the need for long-lived API tokens. The workflow uses OIDC authentication.

- **TestPyPI is not a staging environment**: TestPyPI is for testing the upload and installation process. It is not a full mirror of PyPI and may not have all dependencies. Always test with `--extra-index-url https://pypi.org/simple/` to allow dependencies from production PyPI.

- **Classifiers matter**: PyPI classifiers affect discoverability. Include classifiers for development status (Alpha/Beta/Stable), license, intended audience, and all supported Python versions (e.g., "Programming Language :: Python :: 3.8").

- **README is the PyPI homepage**: The README file becomes the project description page on PyPI. Ensure it includes installation instructions, quick start examples, and links to documentation.

- **Build tool requirements**: Ensure `build` and `twine` are installed before running this workflow:
  ```bash
  pip install build twine
  ```
