# pub-pipeline Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Evolve r-pub-pipeline into a unified pub-pipeline plugin covering R (CRAN/JOSS/JSS), Python (PyPI), and books (Amazon KDP), with shared user config, slash commands, and improved skills.

**Architecture:** A single Claude Code plugin with skills organized by ecosystem. A top-level router skill detects project type and delegates to ecosystem-specific skills. Shared user config (`.claude/pub-pipeline.local.md`) provides author metadata across all workflows.

**Tech Stack:** Claude Code plugin system (skills, commands, plugin.json), Markdown with YAML frontmatter.

---

## Phase 1: Foundation (rename, config, commands infrastructure)

### Task 1: Rename plugin and update plugin.json

**Files:**
- Modify: `.claude-plugin/plugin.json`

**Step 1: Update plugin.json**

Replace the contents of `.claude-plugin/plugin.json` with:

```json
{
  "name": "pub-pipeline",
  "version": "0.2.0",
  "description": "Unified publication pipeline: R packages (CRAN/JOSS/JSS), Python packages (PyPI), and books (Amazon KDP)",
  "author": {
    "name": "Alexander Towell",
    "email": "lex@metafunctor.com",
    "url": "https://github.com/queelius"
  },
  "repository": "https://github.com/queelius/pub-pipeline",
  "license": "MIT",
  "keywords": ["R", "CRAN", "JOSS", "PyPI", "KDP", "publication", "academic", "audit"]
}
```

**Step 2: Commit**

```bash
git add .claude-plugin/plugin.json
git commit -m "rename plugin to pub-pipeline, bump to v0.2.0"
```

---

### Task 2: Create shared user config template

**Files:**
- Create: `docs/user-config-template.md`

**Step 1: Write the template file**

Create `docs/user-config-template.md` with the full config template from the design doc. Include:
- `author` block (name, orcid, email, affiliation)
- `coauthors` list
- `r` block (domain, audience, competitors)
- `python` block (pypi_username)
- `kdp` block (pen_name, publisher, categories)
- `ai_usage` block (used, tools, scope, human_oversight)
- `funding` field
- Markdown body section for free-form notes
- Comments explaining each field

**Step 2: Commit**

```bash
git add docs/user-config-template.md
git commit -m "add shared user config template for all publication ecosystems"
```

---

### Task 3: Create commands directory with all 7 command files

**Files:**
- Create: `commands/cran-audit.md`
- Create: `commands/joss-audit.md`
- Create: `commands/joss-draft.md`
- Create: `commands/r-publish.md`
- Create: `commands/pypi-publish.md`
- Create: `commands/kdp-audit.md`
- Create: `commands/kdp-publish.md`

**Step 1: Create all command files**

Each command file follows this pattern:

```markdown
---
description: "One-line description"
---
Brief instruction triggering the corresponding skill.
```

Specific content for each:

**commands/cran-audit.md:**
```markdown
---
description: "Audit an R package against CRAN Repository Policy"
---
Run the cran-audit skill: audit the current R package against CRAN Repository Policy and produce a structured gap report with actionable fixes.
```

**commands/joss-audit.md:**
```markdown
---
description: "Evaluate an R package against the JOSS reviewer checklist"
---
Run the joss-audit skill: evaluate the current R package and its paper.md against the complete JOSS reviewer checklist and produce a structured gap report.
```

**commands/joss-draft.md:**
```markdown
---
description: "Draft a JOSS paper (paper.md and paper.bib)"
---
Run the joss-draft skill: analyze the current R package and draft a complete paper.md and paper.bib for JOSS submission.
```

**commands/r-publish.md:**
```markdown
---
description: "Orchestrate the full R package publication pipeline"
---
Run the r-pub-pipeline skill: orchestrate the full publication pipeline for this R package through CRAN, JOSS, and optionally JSS.
```

**commands/pypi-publish.md:**
```markdown
---
description: "Publish a Python package to PyPI"
---
Run the pypi-publish skill: audit, build, test, and publish the current Python package to PyPI.
```

**commands/kdp-audit.md:**
```markdown
---
description: "Audit a manuscript for Amazon KDP readiness"
---
Run the kdp-audit skill: audit the current manuscript against Amazon KDP formatting and metadata requirements, producing a structured gap report.
```

**commands/kdp-publish.md:**
```markdown
---
description: "Guide the Amazon KDP book publishing workflow"
---
Run the kdp-publish skill: walk through the complete Amazon KDP publishing workflow from manuscript preparation through publication.
```

**Step 2: Commit**

```bash
git add commands/
git commit -m "add slash commands for all 7 skills"
```

---

### Task 4: Rename pub-pipeline skill → r-pub-pipeline and create new router

**Files:**
- Move: `skills/pub-pipeline/SKILL.md` → `skills/r-pub-pipeline/SKILL.md`
- Create: `skills/pub-pipeline/SKILL.md` (new router)

**Step 1: Move the existing pub-pipeline skill**

```bash
mkdir -p skills/r-pub-pipeline
mv skills/pub-pipeline/SKILL.md skills/r-pub-pipeline/SKILL.md
```

**Step 2: Update the moved skill's frontmatter**

In `skills/r-pub-pipeline/SKILL.md`, change the frontmatter:

Old:
```yaml
name: pub-pipeline
description: "This skill should be used when the user asks to \"publish my R package\"..."
```

New:
```yaml
name: r-pub-pipeline
description: "This skill should be used when the user asks to \"publish my R package\", \"R publication pipeline\", \"get this R package published\", \"CRAN and JOSS pipeline\", \"publish to CRAN and JOSS\", or mentions an end-to-end R package publication workflow. It orchestrates the full CRAN → JOSS → (optionally JSS) publication pipeline for R packages, coordinating audits, paper drafting, and review cycles."
```

Also update the heading from `# R Package Publication Pipeline` to include an explicit note that this is the R-specific orchestrator.

**Step 3: Create the new top-level router skill**

Create `skills/pub-pipeline/SKILL.md`:

```markdown
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
| `DESCRIPTION` file exists (with `Package:` field) | R package | `/r-publish` (the `r-pub-pipeline` skill) |
| `pyproject.toml` or `setup.py` or `setup.cfg` exists | Python package | `/pypi-publish` (the `pypi-publish` skill) |
| `.docx`, `.epub`, `.tex` manuscript files exist | Book manuscript | `/kdp-publish` (the `kdp-publish` skill) |
| Multiple types detected | Ambiguous | Ask the user which workflow to run |
| None detected | Unknown | Ask the user what they want to publish |

## Workflow

### Step 1: Detect project type (Glob tool)

Search the current directory for:
- `DESCRIPTION` (R package indicator)
- `pyproject.toml`, `setup.py`, `setup.cfg` (Python package indicators)
- `*.tex`, `*.docx`, `*.epub`, `manuscript/` directory (book indicators)

### Step 2: Load user config (Read tool)

Read `.claude/pub-pipeline.local.md` if it exists. If missing, inform the user and offer to create one from `${CLAUDE_PLUGIN_ROOT}/docs/user-config-template.md`.

### Step 3: Route

Based on detection, invoke the appropriate skill. If ambiguous, present options to the user.

## Supported Ecosystems

| Ecosystem | Skills | Commands |
|-----------|--------|----------|
| **R packages** | `cran-audit`, `joss-audit`, `joss-draft`, `r-pub-pipeline` | `/cran-audit`, `/joss-audit`, `/joss-draft`, `/r-publish` |
| **Python packages** | `pypi-publish` | `/pypi-publish` |
| **Books (Amazon KDP)** | `kdp-audit`, `kdp-publish` | `/kdp-audit`, `/kdp-publish` |
```

**Step 4: Commit**

```bash
git add skills/r-pub-pipeline/ skills/pub-pipeline/
git commit -m "rename R orchestrator to r-pub-pipeline, add top-level router"
```

---

## Phase 2: Improve existing R skills

### Task 5: Improve cran-audit skill

**Files:**
- Modify: `skills/cran-audit/SKILL.md`

**Step 1: Apply all improvements**

Make these changes to `skills/cran-audit/SKILL.md`:

1. **Add user config step** after "### 1. Locate the Package":

   Add a new step "### 1b. Load User Config" that reads `.claude/pub-pipeline.local.md` for author metadata and package context. Reference the template at `${CLAUDE_PLUGIN_ROOT}/docs/user-config-template.md` if missing.

2. **Add to Code Quality checks** (Step 2):
   - Add: `Search for options() or par() calls that don't restore via on.exit() or withr`
   - Add: `Run urlchecker::url_check() to verify all URLs are valid and HTTPS`

3. **Add to evaluation table** (Step 3):
   - Add row: `| **Examples** | \dontrun{} only for truly non-runnable code; prefer \donttest{} for slow examples |`
   - Add row: `| **Side effects** | options()/par() restored via on.exit() or withr; no persistent state changes |`

4. **Remove domain-specific note** (Important Notes section):
   Delete: `- NaN warnings during optimization are common and usually acceptable — the concern is errors, not warnings from numerical exploration.`

5. **Add to "Offer to Fix" section**:
   - Add: `- Replace \dontrun{} with \donttest{} where appropriate`

**Step 2: Commit**

```bash
git add skills/cran-audit/SKILL.md
git commit -m "improve cran-audit: add config, URL checks, dontrun/donttest, side effects"
```

---

### Task 6: Improve joss-audit skill

**Files:**
- Modify: `skills/joss-audit/SKILL.md`

**Step 1: Apply all improvements**

1. **Add user config step** after "### 1. Locate the Package and Paper":

   Add "### 1b. Load User Config" step (same pattern as cran-audit).

2. **Soften requirement labels** (Step 3, lines 72-74):

   Change all instances of `(NEW 2025 requirement)` to `(recently added requirement — verify against current JOSS guidelines)`.

3. **Add citation cross-reference command** after the word count command in Step 3:

   ```markdown
   **Citation cross-reference** (Grep/Bash tools):
   ```bash
   # Extract all citation keys from paper.md
   grep -oP '@\w+' paper.md | sort -u > /tmp/paper_keys.txt
   # Extract all BibTeX entry keys from paper.bib
   grep -oP '^\s*@\w+\{(\w+)' paper.bib | grep -oP '\w+$' | sort -u > /tmp/bib_keys.txt
   # Find keys in paper.md not in paper.bib
   comm -23 /tmp/paper_keys.txt /tmp/bib_keys.txt
   ```
   All citation keys in paper.md must have matching BibTeX entries. Report any missing.
   ```

4. **Improve word count command robustness**:

   Replace the existing sed command with:
   ```bash
   # Count words between end of YAML frontmatter and References section
   awk '/^---$/{n++; next} n>=2 && !/^# References/{print}' paper.md | wc -w
   ```

**Step 2: Commit**

```bash
git add skills/joss-audit/SKILL.md
git commit -m "improve joss-audit: add config, soften requirement labels, citation cross-ref"
```

---

### Task 7: Improve joss-draft skill

**Files:**
- Modify: `skills/joss-draft/SKILL.md`

**Step 1: Apply all improvements**

1. **Replace Step 2 (Get Author Metadata)** entirely:

   Old: The `deets` CLI section.
   New:
   ```markdown
   ### 2. Get Author Metadata

   **Load user config** (Read tool):
   Read `.claude/pub-pipeline.local.md` if it exists. Extract author and coauthor fields from the YAML frontmatter.

   If the config file is missing or incomplete, ask the user for:
   - Full name, ORCID, affiliation, email for each author
   - Any additional co-authors

   If the user has the `deets` CLI installed, it can also be used as a fallback:
   ```bash
   deets get identity.name
   deets get academic.orcid
   ```
   ```

2. **Add tool guidance to Step 3** (Identify Competing Packages):

   After "Why build new rather than contribute to existing?", add:
   ```markdown
   **How to find competitors** (WebSearch/Read/Bash tools):
   - Search CRAN Task Views relevant to the package's domain (WebSearch tool)
   - Read the package's `DESCRIPTION` file for packages listed in Imports/Suggests
   - Search the package's README and vignettes for mentions of other packages (Grep tool)
   - Check the user config's `r.competitors` field for pre-identified competitors
   - Search the web for "[domain] R package" (WebSearch tool)
   ```

3. **Fix hardcoded year** in BibTeX template (line 155):

   Change `year = {2024},` to `year = {YYYY},  % use the current year`

4. **Add user config reference** to Step 4 (Draft paper.md):

   Before the template, add: "Populate the YAML frontmatter from the user config (author, coauthors, affiliations). Use the `r.domain` and `r.audience` fields to inform the Statement of Need. Use `r.competitors` to seed the State of the Field section. Use `ai_usage` fields for the AI Usage Disclosure section."

**Step 2: Commit**

```bash
git add skills/joss-draft/SKILL.md
git commit -m "improve joss-draft: replace deets with config, add tool guidance, fix year"
```

---

### Task 8: Improve r-pub-pipeline skill (formerly pub-pipeline)

**Files:**
- Modify: `skills/r-pub-pipeline/SKILL.md`

**Step 1: Apply all improvements**

1. **Add user config step** to Phase 1 (Assess Current State):

   Add as the first step: "Read `.claude/pub-pipeline.local.md` for author metadata and publication targets."

2. **Add tool annotations** to Phase 1 assessment steps (lines 27-31):

   ```markdown
   1. Read DESCRIPTION for package metadata (Read tool)
   2. Check git log for development history (Bash tool)
   3. Look for existing paper.md, CITATION.cff (Glob tool)
   4. Check if already on CRAN — search https://cran.r-project.org/package={name} (WebFetch tool)
   5. Check if already on JOSS — search joss.theoj.org (WebSearch tool)
   ```

3. **Add Bioconductor note** to Phase 1, after the classification table:

   ```markdown
   **Note**: If the package is bioinformatics-focused (genomics, proteomics, etc.), consider Bioconductor instead of CRAN. Bioconductor has its own submission process and is the standard distribution channel for bioinformatics R packages.
   ```

4. **Fix tagged release** in Phase 5 (line 108):

   Change `v1.0.0-joss` to `v1.0.0`.

5. **Expand Zenodo workflow** in Phase 5 (line 109):

   Replace the terse Zenodo line with:
   ```markdown
   - Deposit on Zenodo:
     1. Go to https://zenodo.org and log in with GitHub
     2. Enable the Zenodo-GitHub integration for this repository (Settings → GitHub)
     3. Create a GitHub release (this triggers automatic Zenodo archiving)
     4. Copy the Zenodo DOI from the automatically created deposit
   ```

6. **Add CRAN rejection handling** to Phase 2, after the submission steps:

   ```markdown
   **If CRAN rejects the submission**:
   1. Read the reviewer's email carefully — they identify specific issues
   2. Fix all identified issues (do not partially fix)
   3. Re-run `devtools::check(args = "--as-cran")` to verify
   4. Resubmit via `devtools::submit_cran()` — CRAN allows resubmission
   5. In `cran-comments.md`, note what was fixed since the previous submission
   6. Do not resubmit more than once per week unless requested by CRAN
   ```

7. **Update win-builder reference** in Phase 2 (line 62):

   Change `devtools::check_win_devel()` to:
   ```markdown
   3. Test on other platforms:
      - `devtools::check_win_devel()` — Windows (win-builder)
      - `rhub::check_for_cran()` — Multiple platforms via R-hub
   ```

**Step 2: Commit**

```bash
git add skills/r-pub-pipeline/SKILL.md
git commit -m "improve r-pub-pipeline: config, Bioconductor, Zenodo, rejection handling"
```

---

### Task 9: Generalize joss-exemplars.md

**Files:**
- Modify: `docs/joss-exemplars.md`

**Step 1: Remove dfr.dist-specific content**

1. **Summary table** (line 5): Rename "Score/Hess" column to "Notes"

2. **Summary table entries** (lines 7-8): Remove "closest to dfr.dist" and "hazard-based like dfr.dist". Replace with neutral notes:
   - univariateML: "concise, under current minimum"
   - survPen: "good domain-first structure"

3. **univariateML section** (line 21): Change "Closest to dfr.dist — MLE for univariate distributions" to "MLE for univariate distributions, R package, statistical focus"

4. **survPen section** (line 64): Change "same domain as dfr.dist" to "survival analysis domain, penalized splines"

5. **BayesMFSurv section** (line 113): Change "closest to dfr.dist's domain of masked causes" to "Bayesian survival models, misclassified failure events"

6. **Delete the entire "For dfr.dist Specifically" section** (lines 167-183)

7. **Generalize the tags section** (lines 157-165): Change the heading from implicit dfr.dist context to "Tags Commonly Used for R Statistics Packages" (already the heading, but remove the dfr.dist-specific example below it)

**Step 2: Commit**

```bash
git add docs/joss-exemplars.md
git commit -m "generalize joss-exemplars: remove dfr.dist-specific content"
```

---

## Phase 3: New skills and reference docs

### Task 10: Create pypi-publish skill

**Files:**
- Create: `skills/pypi-publish/SKILL.md`

**Step 1: Write the skill file**

Create `skills/pypi-publish/SKILL.md` with:

- **Frontmatter**: name `pypi-publish`, description covering triggers like "publish to PyPI", "upload to PyPI", "PyPI release", "publish my Python package"
- **Workflow**:
  1. Locate package (pyproject.toml / setup.py / setup.cfg)
  2. Load user config (`.claude/pub-pipeline.local.md` — `python.pypi_username` field)
  3. Audit metadata: check name, version, description, license, author/email, project URLs, classifiers, python_requires, readme
  4. Check README renders: `python -m build && twine check dist/*`
  5. Check tests exist and pass: `pytest` or `python -m pytest`
  6. Check version: verify not already published on PyPI (`pip index versions package-name`)
  7. Build: `python -m build`
  8. Test on TestPyPI: `twine upload --repository testpypi dist/*`
  9. Test install from TestPyPI: `pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ package-name`
  10. Publish: `twine upload dist/*`
  11. Post-publish: verify `pip install package-name`, create GitHub release, tag
- **Reference**: `${CLAUDE_PLUGIN_ROOT}/docs/pypi-reference.md`
- **Important notes**: trusted publishers (GitHub Actions OIDC), `__token__` auth, version immutability

**Step 2: Commit**

```bash
git add skills/pypi-publish/
git commit -m "add pypi-publish skill"
```

---

### Task 11: Create pypi-reference.md

**Files:**
- Create: `docs/pypi-reference.md`

**Step 1: Write the reference doc**

Create `docs/pypi-reference.md` covering:

- Required pyproject.toml fields (with example)
- Trove classifiers reference (most common ones)
- TestPyPI vs PyPI workflow
- Trusted publisher setup (GitHub Actions OIDC — the modern way)
- Token authentication (`__token__` + API token)
- Common issues (version already exists, README rendering, missing metadata)
- Post-publish checklist

Keep it concise — PyPI is simpler than CRAN/JOSS. Target ~200-300 lines.

**Step 2: Commit**

```bash
git add docs/pypi-reference.md
git commit -m "add PyPI reference doc"
```

---

### Task 12: Create kdp-audit skill

**Files:**
- Create: `skills/kdp-audit/SKILL.md`

**Step 1: Write the skill file**

Create `skills/kdp-audit/SKILL.md` with:

- **Frontmatter**: name `kdp-audit`, description covering triggers like "KDP audit", "check manuscript formatting", "is my book ready for KDP", "Amazon publishing requirements", "Kindle formatting check"
- **Workflow**:
  1. Detect manuscript type (Glob tool): `.tex`, `.docx`, `.epub`, `.md`, or KPF
  2. Load user config (Read tool): `.claude/pub-pipeline.local.md` — `kdp` section
  3. Check interior formatting:
     - Trim size (standard: 6x9 for non-fiction, 5.5x8.5 for fiction)
     - Margins (minimum 0.375" inside, varies by page count for spine)
     - Font (embedded, readable at all sizes)
     - Page numbers, headers/footers
     - Table of contents (required for non-fiction)
  4. Check cover specs:
     - Kindle eBook: 2560x1600px (1.6:1 ratio), RGB, JPEG/TIFF
     - Paperback: 300 DPI, includes spine (width depends on page count)
     - Check if cover file exists and meets specs (Read tool for image)
  5. Check metadata readiness:
     - Title, subtitle
     - Description/blurb (up to 4000 chars)
     - Up to 3 BISAC categories
     - Up to 7 keywords
     - Author bio
  6. Technical books only:
     - LaTeX compilation check (Bash tool): `pdflatex` or `xelatex`
     - Math rendering quality
     - Code listings formatting (monospace, syntax highlighting)
     - Index presence, bibliography
  7. Fiction only:
     - Chapter structure (front matter, chapters, back matter)
     - Scene break formatting consistency
     - Dialog formatting
  8. Produce gap report (same pattern as CRAN/JOSS audits):
     ```markdown
     # KDP Audit Report: {title}
     ## Summary
     - **Status**: READY / NEEDS WORK / NOT READY
     - **Format**: [Kindle eBook / Paperback / Both]
     ## Critical (Must Fix)
     ## Warnings (Should Fix)
     ## Passed
     ## Recommended Next Steps
     ```
- **Reference**: `${CLAUDE_PLUGIN_ROOT}/docs/kdp-reference.md`

**Step 2: Commit**

```bash
git add skills/kdp-audit/
git commit -m "add kdp-audit skill"
```

---

### Task 13: Create kdp-publish skill

**Files:**
- Create: `skills/kdp-publish/SKILL.md`

**Step 1: Write the skill file**

Create `skills/kdp-publish/SKILL.md` with:

- **Frontmatter**: name `kdp-publish`, description covering triggers like "publish on KDP", "Amazon book publishing", "Kindle Direct Publishing", "publish my book", "self-publish"
- **Workflow**:
  1. Load user config: author name, pen name (if different), publisher name
  2. Assess current state:
     - Manuscript format and readiness (recommend running `/kdp-audit` first)
     - Cover status (exists? meets specs?)
     - ISBN status (have one? using free ASIN?)
  3. Manuscript preparation:
     - Format conversion if needed (LaTeX→PDF, Markdown→EPUB/DOCX)
     - Final proofread checklist
  4. Cover preparation:
     - Verify dimensions and DPI
     - Spine width calculation: `spine_width_inches = page_count * 0.002252` (white paper) or `* 0.002347` (cream paper)
     - Guide to KDP Cover Calculator tool
  5. KDP account setup:
     - Guide to https://kdp.amazon.com
     - Tax interview (if not done)
     - Bank account for royalties
  6. Book creation walkthrough:
     - Language, title, subtitle, series, edition
     - Author/contributors
     - Description (HTML formatting allowed)
     - Publishing rights
     - Keywords and categories
  7. Pricing strategy:
     - eBook: $2.99-$9.99 for 70% royalty, or 35% at any price
     - KDP Select: Kindle Unlimited enrollment, 90-day exclusivity
     - Paperback: set list price, Amazon calculates royalty
     - Print cost estimation
  8. Upload and preview:
     - Upload manuscript and cover
     - Use KDP Previewer to check formatting
     - Review on multiple device types
  9. Publish:
     - Final review of all details
     - Submit (72-hour review typical, up to 7 days)
  10. Post-publish:
      - Verify listing on Amazon
      - Update Author Central page
      - Link to Goodreads
      - Set up A+ Content (if eligible)
      - Plan launch strategy
- **Reference**: `${CLAUDE_PLUGIN_ROOT}/docs/kdp-reference.md`
- **Important notes**: KDP is free, royalties paid monthly, print-on-demand means no inventory

**Step 2: Commit**

```bash
git add skills/kdp-publish/
git commit -m "add kdp-publish skill"
```

---

### Task 14: Create kdp-reference.md

**Files:**
- Create: `docs/kdp-reference.md`

**Step 1: Write the reference doc**

Create `docs/kdp-reference.md` covering:

- **Manuscript formatting**:
  - Supported file formats (DOCX, EPUB, KPF, PDF for print)
  - Trim sizes (with standard recommendations)
  - Margins (with page-count-dependent minimums)
  - Font requirements
  - Interior elements (TOC, headers, page numbers)
- **Cover requirements**:
  - eBook: 2560x1600px minimum, 1.6:1 ratio, RGB JPEG/TIFF
  - Paperback: 300 DPI, spine width formula, bleed area
  - Cover Calculator tool reference
- **Metadata**:
  - BISAC category codes (top-level list with examples)
  - Keyword strategy (7 keywords, search optimization)
  - Description formatting (HTML tags allowed)
- **Pricing and royalties**:
  - eBook royalty tiers (35% and 70%)
  - 70% eligibility requirements ($2.99-$9.99, various territory rules)
  - KDP Select (Kindle Unlimited) trade-offs
  - Print pricing (cost calculator reference)
- **Common rejection reasons**:
  - Content guidelines violations
  - Cover quality issues
  - Metadata mismatches
  - Public domain content rules
- **ISBN guidance**:
  - Free ASIN (Amazon-assigned) vs purchased ISBN
  - When to buy an ISBN (if distributing beyond Amazon)
  - Bowker vs national ISBN agencies

Target ~300-400 lines.

**Step 2: Commit**

```bash
git add docs/kdp-reference.md
git commit -m "add KDP reference doc"
```

---

## Phase 4: Final touches

### Task 15: Update README.md

**Files:**
- Modify: `README.md`

**Step 1: Rewrite README for unified plugin**

Update to reflect:
- New name: pub-pipeline
- All 3 ecosystems (R, Python, KDP)
- Full skill and command table
- Updated installation instructions
- Updated prerequisites (R tools, Python build/twine, no `deets` dependency)
- Config system explanation (point to `docs/user-config-template.md`)

**Step 2: Commit**

```bash
git add README.md
git commit -m "update README for unified pub-pipeline plugin"
```

---

### Task 16: Validate plugin structure

**Step 1: Verify all files exist**

Run:
```bash
# Check all expected files exist
ls -la .claude-plugin/plugin.json
ls -la skills/pub-pipeline/SKILL.md
ls -la skills/cran-audit/SKILL.md
ls -la skills/joss-audit/SKILL.md
ls -la skills/joss-draft/SKILL.md
ls -la skills/r-pub-pipeline/SKILL.md
ls -la skills/pypi-publish/SKILL.md
ls -la skills/kdp-audit/SKILL.md
ls -la skills/kdp-publish/SKILL.md
ls -la commands/cran-audit.md
ls -la commands/joss-audit.md
ls -la commands/joss-draft.md
ls -la commands/r-publish.md
ls -la commands/pypi-publish.md
ls -la commands/kdp-audit.md
ls -la commands/kdp-publish.md
ls -la docs/user-config-template.md
ls -la docs/cran-reference.md
ls -la docs/joss-reference.md
ls -la docs/joss-exemplars.md
ls -la docs/pypi-reference.md
ls -la docs/kdp-reference.md
```

**Step 2: Verify all skill frontmatter has name and description**

```bash
for f in skills/*/SKILL.md; do
  echo "=== $f ==="
  head -5 "$f"
  echo
done
```

**Step 3: Verify all command frontmatter has description**

```bash
for f in commands/*.md; do
  echo "=== $f ==="
  head -5 "$f"
  echo
done
```

**Step 4: Verify no dfr.dist references remain**

```bash
grep -ri "dfr.dist" skills/ docs/ || echo "CLEAN: no dfr.dist references"
```

**Step 5: Verify no deets references in skills** (except as optional fallback in joss-draft)

```bash
grep -ri "deets" skills/ | grep -v "fallback\|optional"
```

**Step 6: Verify all ${CLAUDE_PLUGIN_ROOT} references point to existing files**

```bash
grep -roh '\${CLAUDE_PLUGIN_ROOT}/[^`"]*' skills/ | sort -u
# Then manually verify each path exists under the repo root
```

**Step 7: Final commit if any fixes needed**

---

## Task Dependency Summary

```
Task 1 (rename plugin.json) ─────────┐
Task 2 (user config template) ───────┤
Task 3 (commands) ───────────────────┤──→ All foundation done
Task 4 (rename + router skill) ──────┘
                                      │
Task 5 (cran-audit) ─────────────────┤
Task 6 (joss-audit) ─────────────────┤
Task 7 (joss-draft) ─────────────────┤──→ All R skills improved
Task 8 (r-pub-pipeline) ─────────────┤
Task 9 (generalize exemplars) ───────┘
                                      │
Task 10 (pypi-publish skill) ────────┤
Task 11 (pypi-reference.md) ─────────┤
Task 12 (kdp-audit skill) ───────────┤──→ All new content done
Task 13 (kdp-publish skill) ─────────┤
Task 14 (kdp-reference.md) ──────────┘
                                      │
Task 15 (README) ────────────────────┤──→ Final touches
Task 16 (validation) ────────────────┘
```

**Parallelization**: Within each phase, all tasks are independent and can be run in parallel. Phases must be sequential (Phase 2 depends on Phase 1's rename, etc.).
