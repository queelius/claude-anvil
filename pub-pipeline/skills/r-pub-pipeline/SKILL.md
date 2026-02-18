---
name: r-pub-pipeline
description: "This skill should be used when the user asks to \"publish my R package\", \"R publication pipeline\", \"get this R package published\", \"CRAN and JOSS pipeline\", \"publish to CRAN and JOSS\", or mentions an end-to-end R package publication workflow. It orchestrates the full CRAN → JOSS → (optionally JSS) publication pipeline for R packages, coordinating audits, paper drafting, and review cycles."
---

# R Package Publication Pipeline

Orchestrate the full publication pipeline for R packages: CRAN submission → JOSS paper → optionally JSS methods paper. This skill coordinates the other skills (`/cran-audit`, `/joss-audit`, `/joss-draft`) into a coherent workflow.

## Strategy

The recommended publication order for R packages:

1. **CRAN** — Distribution, discoverability, installation via `install.packages()`
2. **JOSS** — Quick DOI, peer-reviewed citation, Crossref/Google Scholar indexing
3. **JSS** (optional) — High-prestige methods paper, Web of Science indexed (IF ~5)

Each stage builds on the previous. CRAN gives the package legitimacy. JOSS gives it a citable DOI. JSS gives the methodology academic weight.

## Workflow

### Phase 1: Assess Current State

Start by understanding where the package stands:

**Load user config** (Read tool): Read `.claude/pub-pipeline.local.md` if it exists. Extract author metadata, `r.domain`, `r.audience`, `r.competitors`, and publication `targets` from the YAML frontmatter.

```
1. Read DESCRIPTION for package metadata (Read tool)
2. Check git log for development history (Bash tool)
3. Look for existing paper.md, CITATION.cff (Glob tool)
4. Check if already on CRAN — search https://cran.r-project.org/package={name} (WebFetch tool)
5. Check if already on JOSS — search joss.theoj.org (WebSearch tool)
```

Classify the package into one of:

| State | Next Step |
|-------|-----------|
| Not on CRAN, no paper.md | Start with CRAN audit |
| On CRAN, no paper.md | Start with JOSS audit |
| On CRAN, has paper.md | Review paper, prepare JOSS submission |
| On CRAN, published in JOSS | Consider JSS (if substantive methodology) |

**Note**: If the package is bioinformatics-focused (genomics, proteomics, etc.), consider Bioconductor instead of CRAN. Bioconductor has its own submission process and is the standard distribution channel for bioinformatics R packages.

Present the assessment to the user and confirm the plan before proceeding.

### Phase 2: CRAN Readiness

Invoke `/cran-audit` (the `cran-audit` skill) to evaluate CRAN readiness.

If the package is not CRAN-ready:
1. Present the gap report
2. Offer to fix automatable issues
3. Guide manual fixes
4. Re-audit after fixes
5. Walk through submission workflow when ready

If the package is already on CRAN, skip to Phase 3.

**Key CRAN submission steps** (when ready):
1. `usethis::use_version("minor")` — bump version
2. `devtools::check(args = "--as-cran")` — final check
3. Test on other platforms:
   - `devtools::check_win_devel()` — Windows (win-builder)
   - `rhub::check_for_cran()` — Multiple platforms via R-hub
4. `devtools::submit_cran()` — submit
5. Confirm via email link
6. After acceptance: `usethis::use_github_release()`, then `usethis::use_dev_version()`

**If CRAN rejects the submission**:
1. Read the reviewer's email carefully — they identify specific issues
2. Fix all identified issues (do not partially fix)
3. Re-run `devtools::check(args = "--as-cran")` to verify
4. Resubmit via `devtools::submit_cran()` — CRAN allows resubmission
5. In `cran-comments.md`, note what was fixed since the previous submission
6. Do not resubmit more than once per week unless requested by CRAN

### Phase 3: JOSS Readiness

Invoke `/joss-audit` (the `joss-audit` skill) to evaluate JOSS readiness.

Key prerequisites that are often missing:
- **Development history**: Need 6+ months of public git history
- **Contributing guidelines**: `CONTRIBUTING.md` or section in README
- **paper.md**: The JOSS paper itself

If `paper.md` doesn't exist, proceed to Phase 4.

### Phase 4: Draft JOSS Paper

Invoke `/joss-draft` (the `joss-draft` skill) to draft `paper.md` and `paper.bib`.

After drafting:
1. Present the draft to the user for review
2. Iterate on feedback
3. Optionally use the `academic-paper-reviewer` agent for critical review
4. Commit the paper to the repository

### Phase 5: JOSS Submission

Walk the user through JOSS submission:

1. **Pre-submission checklist**:
   - Package on CRAN (or at minimum, installable from GitHub)
   - `paper.md` and `paper.bib` committed to repository
   - All JOSS reviewer checklist items pass (`/joss-audit`)
   - ORCID for all authors

2. **Submit**:
   - Go to https://joss.theoj.org/papers/new
   - Fill in repository URL and other fields
   - Wait for pre-review issue

3. **During review** (2-6 weeks):
   - Respond to reviewer feedback promptly (target 2 weeks)
   - Make requested changes to code and paper
   - Re-run `/joss-audit` after changes

4. **Post-acceptance**:
   - Create tagged release (e.g., `v1.0.0`)
   - Deposit on Zenodo:
     1. Go to https://zenodo.org and log in with GitHub
     2. Enable the Zenodo-GitHub integration for this repository (Settings → GitHub)
     3. Create a GitHub release (this triggers automatic Zenodo archiving)
     4. Copy the Zenodo DOI from the automatically created deposit
   - Update review issue with version number and Zenodo DOI
   - JOSS assigns paper DOI via Crossref

### Phase 6: JSS Consideration (Optional)

Evaluate whether a JSS (Journal of Statistical Software) paper is warranted:

**JSS is appropriate when**:
- The package implements novel statistical methodology
- There's substantive mathematical content to present (proofs, derivations)
- The paper would be 20-50 pages of methods + software description
- The target audience is academic statisticians

**JSS is NOT appropriate when**:
- The package is primarily a software tool (JOSS covers this)
- The mathematics is textbook material
- The paper would essentially repeat the JOSS paper at greater length

If JSS is appropriate, note that:
- JSS uses `rticles::jss_article` RMarkdown format
- JSS papers are 20-50 pages and include mathematical exposition
- JSS is indexed in Web of Science (Impact Factor ~5)
- Review takes 6-18 months
- The `academic-paper-writer` agent can help draft in RMarkdown format

## Decision Helpers

### Is My Package Publishable?

| Criterion | Minimum for CRAN | Minimum for JOSS |
|-----------|-----------------|-----------------|
| License | OSI-approved | OSI-approved |
| Tests | Pass R CMD check | Automated test suite |
| Docs | Man pages for exports | README + examples + API docs |
| History | Any | 6+ months public |
| Users | Not required | Evidence of use encouraged |
| Paper | Not required | 750-1750 word paper.md |

### Timeline Expectations

| Stage | Duration |
|-------|----------|
| CRAN prep + audit | 1-3 days |
| CRAN review | 1-7 days (usually 1-2) |
| JOSS prep + paper | 1-2 days |
| JOSS review | 2-8 weeks |
| JSS prep + paper | 2-4 weeks |
| JSS review | 6-18 months |

## Reference Files

- **`${CLAUDE_PLUGIN_ROOT}/docs/cran-reference.md`** — CRAN Repository Policy, submission workflow, common rejections
- **`${CLAUDE_PLUGIN_ROOT}/docs/joss-reference.md`** — JOSS requirements, reviewer checklist, paper format
- **`${CLAUDE_PLUGIN_ROOT}/docs/joss-exemplars.md`** — Real JOSS R package papers with analysis

## Important Notes

- Never submit to JOSS before the package is installable (ideally on CRAN).
- CRAN and JOSS are complementary: CRAN for distribution, JOSS for citation.
- Each publication stage builds credibility for the next.
- The user controls the pace — present options, don't push.
