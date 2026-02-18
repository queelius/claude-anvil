# Design: pub-pipeline (unified publication plugin)

**Date**: 2026-02-15
**Status**: Approved
**Scope**: Rename r-pub-pipeline → pub-pipeline; improve existing R skills; add PyPI and KDP skills; add commands; add shared user config system

---

## Overview

Evolve the R-only `r-pub-pipeline` plugin into a unified `pub-pipeline` Claude Code plugin covering three publication ecosystems:

1. **R packages** — CRAN → JOSS → JSS (existing, improved)
2. **Python packages** — PyPI (new)
3. **Books** — Amazon KDP for both technical and fiction/nonfiction (new)

## Plugin Structure

```
pub-pipeline/
├── .claude-plugin/
│   └── plugin.json                   # Renamed, updated description
├── skills/
│   ├── pub-pipeline/SKILL.md         # Top-level router (detects project type)
│   │
│   ├── cran-audit/SKILL.md           # R: CRAN audit (improved)
│   ├── joss-audit/SKILL.md           # R: JOSS audit (improved)
│   ├── joss-draft/SKILL.md           # R: JOSS paper drafting (improved)
│   ├── r-pub-pipeline/SKILL.md       # R: CRAN→JOSS→JSS orchestrator (renamed from pub-pipeline)
│   │
│   ├── pypi-publish/SKILL.md         # Python: PyPI publishing
│   │
│   ├── kdp-audit/SKILL.md            # Amazon: KDP manuscript audit
│   └── kdp-publish/SKILL.md          # Amazon: KDP publishing workflow
│
├── commands/                          # Slash commands (1 per skill)
│   ├── cran-audit.md
│   ├── joss-audit.md
│   ├── joss-draft.md
│   ├── r-publish.md
│   ├── pypi-publish.md
│   ├── kdp-audit.md
│   └── kdp-publish.md
│
├── docs/
│   ├── user-config-template.md        # Shared config template
│   ├── cran-reference.md              # R: CRAN policy (improved)
│   ├── joss-reference.md              # R: JOSS requirements (improved)
│   ├── joss-exemplars.md              # R: JOSS paper examples (generalized)
│   ├── pypi-reference.md              # Python: PyPI requirements (new)
│   └── kdp-reference.md              # Amazon: KDP guide (new)
│
├── README.md                          # Updated for unified plugin
└── LICENSE
```

## Shared User Config System

### Location

`.claude/pub-pipeline.local.md` in each project where the plugin is used.

### Format

YAML frontmatter for structured fields, markdown body for free-form context.

### Template (shipped as `docs/user-config-template.md`)

```yaml
---
# pub-pipeline user configuration
# Copy to .claude/pub-pipeline.local.md in your project and fill in your details.

author:
  name: "First M. Last"
  orcid: "0000-0000-0000-0000"
  email: "you@example.com"
  affiliation: "Department, University"

coauthors: []

# Per-ecosystem config (fill in sections relevant to your project)
r:
  domain: ""
  audience: ""
  competitors: []

python:
  pypi_username: ""

kdp:
  pen_name: null
  publisher: null
  categories: []

ai_usage:
  used: false
  tools: []
  scope: ""
  human_oversight: ""

funding: null
---

## Additional Context

Free-form notes about the project for paper drafting or audits.
```

### Skill Integration

Every skill that needs user metadata includes a step:

> **Load user config**: Read `.claude/pub-pipeline.local.md` if it exists. Extract relevant fields from YAML frontmatter. If the file is missing, inform the user and offer to create one from the template at `${CLAUDE_PLUGIN_ROOT}/docs/user-config-template.md`.

This replaces all `deets` CLI references.

## Top-Level Router Skill (pub-pipeline)

The `pub-pipeline` skill detects project type and routes:

| Detection | Project Type | Routes To |
|-----------|-------------|-----------|
| `DESCRIPTION` file | R package | `r-pub-pipeline` |
| `pyproject.toml` or `setup.py` | Python package | `pypi-publish` |
| Manuscript files (`.docx`, `.epub`, LaTeX `\documentclass`) | Book | `kdp-publish` |
| Ambiguous | Unknown | Ask user |

## Existing R Skill Improvements

### All R skills

- Add "Load user config" step
- Remove all `deets` CLI references
- Remove `dfr.dist`-specific content from `joss-exemplars.md`
- Add tool annotations to steps that lack them

### cran-audit

- Remove NaN optimization note (domain-specific to numerical packages)
- Add `\dontrun{}` vs `\donttest{}` guidance
- Add `urlchecker::url_check()` step to data gathering
- Add `options()`/`par()` side-effect checking

### joss-audit

- Soften "NEW 2025 requirement" → "recently added requirement"
- Add concrete Grep command for citation key cross-referencing
- Improve word count command robustness

### joss-draft

- Replace `deets` section with user config lookup
- Add tool guidance for competing-package research (Step 3: suggest CRAN Task Views, web search)
- Fix hardcoded R Core Team BibTeX year → "use current year"
- Reorder: lead with user config, mention `deets` as optional fallback only

### pub-pipeline → r-pub-pipeline (renamed)

- Add Bioconductor consideration to Phase 1 assessment
- Fix `v1.0.0-joss` → `v1.0.0` (standard semver)
- Add CRAN rejection handling guidance to Phase 2
- Expand Zenodo workflow detail in Phase 5
- Add tool annotations to Phase 1 assessment steps
- Update `devtools::check_win_devel()` to mention R-hub as modern alternative

## New PyPI Skill: `pypi-publish`

Single skill covering the full PyPI publishing workflow.

### Workflow

1. **Detect package**: Find `pyproject.toml`, `setup.py`, or `setup.cfg`
2. **Audit metadata**: Check required fields (name, version, description, license, author, URLs, classifiers, python_requires)
3. **Check README**: Verify README renders correctly as PyPI description
4. **Check tests**: Verify test suite exists and passes
5. **Check version**: Verify version bump, no duplicate on PyPI
6. **Build**: `python -m build` (sdist + wheel)
7. **Test on TestPyPI**: `twine upload --repository testpypi dist/*`
8. **Test install**: `pip install --index-url https://test.pypi.org/simple/ package-name`
9. **Publish**: `twine upload dist/*`
10. **Post-publish**: Verify `pip install package-name` works, create GitHub release

### Reference doc: `docs/pypi-reference.md`

Brief document covering:
- Required pyproject.toml fields
- Classifiers reference
- TestPyPI vs PyPI workflow
- Common rejection reasons
- Trusted publisher setup (GitHub Actions OIDC)

## New KDP Skills

### `kdp-audit` — Manuscript audit

**Scope**: Both technical (LaTeX/math-heavy) and fiction/nonfiction manuscripts.

### Workflow

1. **Detect manuscript type**: LaTeX source? Word doc? Markdown? EPUB?
2. **Check format specs**:
   - Interior: Trim size, margins, fonts, page numbers
   - Cover: 2560x1600px (Kindle), 300 DPI (print), spine width calculation
   - File format: `.docx`, `.epub`, `.pdf`, or KPF
3. **Check metadata readiness**:
   - Title, subtitle, series info
   - Description/blurb (up to 4000 chars)
   - Categories (up to 3 BISAC codes)
   - Keywords (up to 7)
   - Author bio
4. **Technical books only**:
   - LaTeX compilation check
   - Math rendering verification
   - Code listing formatting
   - Index/bibliography presence
5. **Fiction only**:
   - Chapter structure (front matter, body, back matter)
   - Scene breaks, formatting consistency
6. **Produce gap report** (same pattern as CRAN/JOSS audits)

### `kdp-publish` — Publishing workflow

### Workflow

1. **Load user config**: Author name, pen name, publisher
2. **Manuscript preparation**: Format conversion if needed
3. **Cover preparation**: Verify or guide cover creation
4. **KDP account setup**: Guide to kdp.amazon.com
5. **Book creation**: Walk through KDP dashboard fields
6. **Metadata entry**: Title, description, categories, keywords
7. **Pricing strategy**:
   - KDP Select (Kindle Unlimited exclusivity, 70% royalty) vs wide distribution (35%)
   - Print pricing (cost calculator)
8. **Upload and preview**: Manuscript + cover upload, KDP previewer check
9. **Publish**: Submit for review (72-hour typical turnaround)
10. **Post-publish**: Verify listing, update author page, link to Goodreads

### Reference doc: `docs/kdp-reference.md`

Covering:
- KDP formatting requirements (Kindle + paperback)
- BISAC category codes
- Keyword strategy
- Pricing tiers and royalty rates
- Common rejection reasons
- ISBN guidance (free ASIN vs purchased ISBN)

## Commands

Each command is a minimal markdown file with frontmatter that invokes its corresponding skill:

```markdown
---
description: "Short description for slash-command help"
---
Brief instruction that triggers the skill.
```

7 commands total, one per skill (excluding the top-level `pub-pipeline` router which triggers via natural language).

## Out of Scope

- **mf-claude plugin**: Separate project, separate conversation
- **JSS paper drafting**: Mentioned in r-pub-pipeline but not a standalone skill (too niche, long-form academic writing delegated to academic-paper-writer agent)
- **Automated submission**: The plugin guides the user through submission; it does not submit on their behalf
