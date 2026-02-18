---
name: pub-pipeline
description: "This skill should be used when the user asks to \"publish my package\", \"publication pipeline\", \"get this published\", \"how do I publish this\", or mentions publication without specifying an ecosystem. It detects the project type (R package, Python package, or book manuscript) and routes to the appropriate ecosystem-specific publication skill."
---

# Publication Pipeline Router

Detect the current project type and route to the appropriate publication workflow.

## Detection Logic

Check the current working directory for project type indicators:

| Check | Project Type | Route To |
|-------|-------------|----------|
| `DESCRIPTION` file with `Package:` field | R package | `/r-publish` (the `r-pub-pipeline` skill) |
| `pyproject.toml` or `setup.py` or `setup.cfg` | Python package | `/pypi-publish` (the `pypi-publish` skill) |
| `.docx`, `.epub`, `.tex` manuscript files | Book manuscript | `/kdp-publish` (the `kdp-publish` skill) |
| `.tex` + `.pdf` without `DESCRIPTION` or `pyproject.toml` | Academic paper | `/osf-preprint` (the `osf-preprint` skill) |
| Multiple types detected | Ambiguous | Ask the user which workflow to run |
| None detected | Unknown | Ask the user what they want to publish |

## Workflow

### Step 1: Detect project type (Glob tool)

Search the current directory for:
- `DESCRIPTION` (R package indicator — verify it contains a `Package:` field)
- `pyproject.toml`, `setup.py`, `setup.cfg` (Python package indicators)
- `*.tex`, `*.docx`, `*.epub`, `manuscript/` directory (book indicators)
- `.tex` + `.pdf` files without R package or Python package indicators (academic paper candidate)

### Step 2: Load user config (Read tool)

Read `.claude/pub-pipeline.local.md` if it exists. If missing, inform the user and offer to create one from the template at `${CLAUDE_PLUGIN_ROOT}/docs/user-config-template.md`.

### Step 3: Route

Based on detection, invoke the appropriate ecosystem skill. If the project type is ambiguous (e.g., both `DESCRIPTION` and `pyproject.toml` exist), present options to the user and ask which publication workflow to run.

## Supported Ecosystems

| Ecosystem | Skills | Commands |
|-----------|--------|----------|
| **R packages** | `cran-audit`, `joss-audit`, `joss-draft`, `r-pub-pipeline` | `/cran-audit`, `/joss-audit`, `/joss-draft`, `/r-publish` |
| **Python packages** | `pypi-publish` | `/pypi-publish` |
| **Books (Amazon KDP)** | `kdp-audit`, `kdp-listing`, `kdp-publish` | `/kdp-audit`, `/kdp-listing`, `/kdp-publish` |
| **Academic preprints** | `osf-preprint` | `/osf-preprint` |

## Reference Files

- **`${CLAUDE_PLUGIN_ROOT}/docs/user-config-template.md`** — Shared user config template
