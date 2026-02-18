# PyPI Publication Reference

## Sources
- [PyPI Official Documentation](https://pypi.org/help/)
- [Python Packaging User Guide](https://packaging.python.org/)
- [PyPI Publishing Tutorial](https://packaging.python.org/tutorials/packaging-projects/)
- [Trusted Publisher Guide](https://docs.pypi.org/trusted-publishers/)
- [PEP 621 - Project Metadata](https://peps.python.org/pep-0621/)

---

## Pre-Publication Checklist

### Package Structure
- [ ] `pyproject.toml` with all required metadata
- [ ] `README.md` or `README.rst` present
- [ ] `LICENSE` file with OSI-approved license
- [ ] Source code in standard package layout (`src/` or flat)
- [ ] Version follows semantic versioning (major.minor.patch)
- [ ] Package name available on PyPI (check conflicts)
- [ ] No restricted/offensive package names

### Metadata Requirements
- [ ] `name` in lowercase with hyphens (not underscores)
- [ ] `version` string valid per PEP 440
- [ ] `description` is single-line summary
- [ ] `readme` field points to README file
- [ ] `requires-python` specifies minimum Python version
- [ ] `license` with SPDX identifier or license file
- [ ] `authors` with name and email
- [ ] `classifiers` include Development Status, Intended Audience, License, Python versions
- [ ] `urls` include Homepage, Documentation, Repository, Bug Tracker

### Code Quality
- [ ] Works on target Python versions
- [ ] Cross-platform compatible (Windows, macOS, Linux)
- [ ] No hardcoded paths or platform-specific code
- [ ] Dependencies pinned sensibly (not too strict)
- [ ] Optional dependencies in `[project.optional-dependencies]`
- [ ] Entry points defined if package provides CLI tools

### Documentation
- [ ] README with installation, quickstart, and examples
- [ ] Docstrings for public API
- [ ] CHANGELOG.md or NEWS.md documenting versions
- [ ] Links to external documentation (if applicable)
- [ ] Code examples tested and working

### Testing
- [ ] Automated tests present
- [ ] Tests run on supported Python versions
- [ ] CI/CD configured (GitHub Actions recommended)
- [ ] Test coverage tracked
- [ ] No tests requiring network access (or properly skipped)

### Build Artifacts
- [ ] Source distribution (sdist) builds cleanly
- [ ] Wheel builds if applicable (platform-specific or pure-Python)
- [ ] Build backend configured (`setuptools`, `hatchling`, `flit`, etc.)
- [ ] No unnecessary files in distribution (`check-manifest` passed)

## Required pyproject.toml

### Complete Example

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "example-package"
version = "0.1.0"
description = "A short description of your package"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "you@example.com"}
]
maintainers = [
    {name = "Maintainer Name", email = "maintainer@example.com"}
]
keywords = ["example", "tutorial", "packaging"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Operating System :: OS Independent",
    "Topic :: Software Development :: Libraries :: Python Modules",
]
dependencies = [
    "requests>=2.28.0",
    "click>=8.0.0",
]

[project.optional-dependencies]
dev = ["pytest>=7.0", "black", "mypy", "ruff"]
docs = ["sphinx>=5.0", "sphinx-rtd-theme"]

[project.urls]
Homepage = "https://github.com/username/example-package"
Documentation = "https://example-package.readthedocs.io"
Repository = "https://github.com/username/example-package.git"
"Bug Tracker" = "https://github.com/username/example-package/issues"
Changelog = "https://github.com/username/example-package/blob/main/CHANGELOG.md"

[project.scripts]
example-cli = "example_package.cli:main"

[tool.setuptools]
packages = ["example_package"]

[tool.setuptools.package-data]
example_package = ["py.typed", "data/*.json"]
```

### Alternative Build Backends

**Hatchling:**
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**Flit:**
```toml
[build-system]
requires = ["flit_core>=3.2"]
build-backend = "flit_core.buildapi"
```

**Poetry:**
```toml
[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
```

## Common Trove Classifiers

### Development Status
- `Development Status :: 3 - Alpha`
- `Development Status :: 4 - Beta`
- `Development Status :: 5 - Production/Stable`
- `Development Status :: 6 - Mature`
- `Development Status :: 7 - Inactive`

### Intended Audience
- `Intended Audience :: Developers`
- `Intended Audience :: Science/Research`
- `Intended Audience :: Education`
- `Intended Audience :: End Users/Desktop`
- `Intended Audience :: System Administrators`

### License (must match actual license)
- `License :: OSI Approved :: MIT License`
- `License :: OSI Approved :: Apache Software License`
- `License :: OSI Approved :: BSD License`
- `License :: OSI Approved :: GNU General Public License v3 (GPLv3)`
- `License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)`

### Programming Language
- `Programming Language :: Python :: 3`
- `Programming Language :: Python :: 3.8`
- `Programming Language :: Python :: 3.9`
- `Programming Language :: Python :: 3.10`
- `Programming Language :: Python :: 3.11`
- `Programming Language :: Python :: 3.12`
- `Programming Language :: Python :: 3 :: Only`

### Topic
- `Topic :: Software Development :: Libraries :: Python Modules`
- `Topic :: Scientific/Engineering`
- `Topic :: System :: Monitoring`
- `Topic :: Utilities`

Full list: https://pypi.org/classifiers/

## TestPyPI vs PyPI Workflow

### 1. Test on TestPyPI First (Recommended)

TestPyPI is a separate instance for testing package uploads.

```bash
# Install build tools
python -m pip install --upgrade build twine

# Build distributions
python -m build

# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
python -m pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    your-package-name
```

**Important TestPyPI notes:**
- TestPyPI databases are separate (need separate account)
- Package names reserved on TestPyPI don't reserve on PyPI
- TestPyPI may be wiped periodically
- Dependencies must come from real PyPI (use `--extra-index-url`)

### 2. Upload to Production PyPI

```bash
# Upload to PyPI (production)
python -m twine upload dist/*

# Or specify repository explicitly
python -m twine upload --repository pypi dist/*
```

### 3. Configure ~/.pypirc (Optional)

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmc...

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgENdGVzdC5weXBpLm9yZw...
```

**Security note:** Use trusted publishers or API tokens, not passwords.

## Trusted Publisher Setup (GitHub Actions OIDC)

**This is the modern, recommended approach.** No API tokens needed.

### Benefits
- No long-lived secrets to manage
- Automatic token rotation
- Tied to specific repository and workflow
- More secure than API tokens

### Setup Steps

1. **On PyPI:**
   - Go to your project settings
   - Navigate to "Publishing" section
   - Click "Add a new publisher"
   - Fill in:
     - PyPI Project Name: `your-package-name`
     - Owner: `your-github-username` or org
     - Repository name: `your-repo-name`
     - Workflow name: `publish.yml` (or your workflow file name)
     - Environment name: `release` (optional but recommended)

2. **GitHub Actions Workflow:**

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

permissions:
  contents: read

jobs:
  pypi-publish:
    name: Upload release to PyPI
    runs-on: ubuntu-latest
    environment:
      name: release
      url: https://pypi.org/p/your-package-name
    permissions:
      id-token: write  # REQUIRED for trusted publishing
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.x'

      - name: Build package
        run: |
          python -m pip install --upgrade build
          python -m build

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          # No password or token needed!
          # OIDC authentication happens automatically
```

3. **Create GitHub Release to Trigger:**

```bash
git tag v0.1.0
git push origin v0.1.0
# Then create release on GitHub UI or use gh CLI:
gh release create v0.1.0 --title "v0.1.0" --notes "Release notes"
```

### Environment Protection Rules (Recommended)

In GitHub repository settings → Environments → release:
- [ ] Required reviewers (prevents accidental releases)
- [ ] Wait timer (optional cooldown period)
- [ ] Deployment branches (limit to `main` or release branches)

## Token Authentication (Legacy Method)

Still common for local uploads or non-GitHub CI.

### 1. Generate API Token on PyPI

- Go to Account Settings → API tokens
- Click "Add API token"
- Set scope (entire account or specific project)
- Token name: descriptive (e.g., "GitHub Actions for mypackage")
- Copy token (starts with `pypi-`)

### 2. Use Token with Twine

**Environment variable (recommended):**
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-AgEIcHlwaS5vcmc...
python -m twine upload dist/*
```

**Command line:**
```bash
python -m twine upload -u __token__ -p pypi-AgEIcHlwaS5vcmc... dist/*
```

**In ~/.pypirc:**
```ini
[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmc...
```

### GitHub Secrets Setup

For GitHub Actions without trusted publishers:
- Settings → Secrets → Actions → New repository secret
- Name: `PYPI_API_TOKEN`
- Value: `pypi-AgEI...` (the token)

```yaml
- name: Publish to PyPI
  env:
    TWINE_USERNAME: __token__
    TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
  run: |
    python -m twine upload dist/*
```

## Common Issues

### 1. Version Already Exists
**Error:** `File already exists.`

**Cause:** PyPI doesn't allow re-uploading the same version.

**Fix:**
- Bump version in `pyproject.toml`
- Delete local `dist/` folder
- Rebuild: `python -m build`
- Upload new version

**Prevention:** Use `--skip-existing` flag (but fix version properly)

### 2. README Rendering Failures
**Error:** `The description failed to render in the default format of reStructuredText.`

**Cause:** Invalid RST syntax or wrong content-type.

**Fix for Markdown:**
```toml
[project]
readme = "README.md"  # Not readme = {file = "README.md", content-type = "text/markdown"}
```

Modern `pyproject.toml` auto-detects Markdown from `.md` extension.

**Fix for RST:**
- Validate RST: `python -m readme_renderer README.rst`
- Install: `pip install readme-renderer[rst]`

### 3. Missing Metadata
**Error:** `Missing required field: [field_name]`

**Required fields:**
- `name`
- `version`

**Common missing fields:**
- `description` (short summary)
- `authors` or `maintainers`

**Fix:** Add all required fields to `[project]` section.

### 4. Package Name Conflicts
**Error:** `The name 'package-name' conflicts with an existing project.`

**Causes:**
- Name already taken (case-insensitive)
- Name too similar to existing package
- Reserved name (e.g., `pip`, `setuptools`)

**Fix:**
- Choose different name
- Add prefix/suffix (e.g., `yourname-package`, `package-utils`)
- Check availability: https://pypi.org/project/package-name/

### 5. sdist vs Wheel Gotchas

**Source Distribution (sdist):**
- `.tar.gz` file
- Contains raw source code
- Requires build tools on user's machine
- Always upload sdist

**Wheel:**
- `.whl` file
- Pre-built distribution
- Faster installation
- Platform-specific or pure-Python

**Common issues:**
- Missing files in sdist: Add to `MANIFEST.in` or use `check-manifest`
- Wheel includes too much: Configure `tool.setuptools` exclusions
- Platform-specific wheel on wrong platform: Build with `cibuildwheel`

**Fix:**
```bash
# Check what's in distributions
tar -tzf dist/package-0.1.0.tar.gz
unzip -l dist/package-0.1.0-py3-none-any.whl

# Validate before upload
python -m twine check dist/*
```

### 6. Build Backend Issues
**Error:** `Unable to find build backend`

**Fix:** Ensure `[build-system]` is complete:
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"
```

### 7. Import Name vs Package Name
**Issue:** Package installed as `my-package` but imports as `my_package`

**Explanation:** PyPI uses hyphens; Python imports use underscores.

**Convention:**
- PyPI name: `my-awesome-package` (hyphens)
- Import name: `my_awesome_package` (underscores)
- Directory: `src/my_awesome_package/` or `my_awesome_package/`

## Post-Publish Checklist

### Immediate
- [ ] Verify package appears on PyPI: `https://pypi.org/project/your-package/`
- [ ] Test installation: `pip install your-package`
- [ ] Check README renders correctly on PyPI page
- [ ] Verify all links work (documentation, repository, bug tracker)
- [ ] Create Git tag matching version: `git tag v0.1.0 && git push origin v0.1.0`

### Documentation
- [ ] Update README with installation command
- [ ] Add PyPI badge to README: `[![PyPI](https://img.shields.io/pypi/v/package.svg)](https://pypi.org/project/package/)`
- [ ] Update documentation site (ReadTheDocs, etc.)
- [ ] Announce release (Twitter, Mastodon, mailing lists, etc.)

### Repository
- [ ] Create GitHub/GitLab release matching tag
- [ ] Update CHANGELOG.md
- [ ] Bump to next dev version (e.g., `0.1.1.dev0`) to prevent confusion
- [ ] Close milestone for this release (if using)
- [ ] Thank contributors

### Monitoring
- [ ] Watch PyPI email for potential issues
- [ ] Monitor GitHub issues for installation problems
- [ ] Check download stats: `https://pypistats.org/packages/your-package`
- [ ] Set up security alerts (GitHub Dependabot, PyUp, etc.)

### Optional but Recommended
- [ ] Submit to conda-forge (if scientific package)
- [ ] Add to awesome-lists or topic collections
- [ ] Write blog post or tutorial
- [ ] Submit to Python Weekly, PyCoder's Weekly, etc.
