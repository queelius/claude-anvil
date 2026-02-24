---
name: joss-audit
description: "This skill should be used when the user asks to \"audit for JOSS\", \"check JOSS readiness\", \"JOSS reviewer checklist\", \"prepare for JOSS submission\", \"is my package JOSS ready\", \"JOSS requirements\", or mentions JOSS submission compliance. It evaluates an R package and its paper.md against the complete JOSS reviewer checklist, producing a structured gap report."
---

# JOSS Submission Audit

Evaluate an R package against the complete JOSS reviewer checklist and produce a structured gap report. This covers software quality, documentation, development history, and paper.md format compliance.

## Workflow

### 1. Locate the Package and Paper

Identify the R package root (look for `DESCRIPTION`). Then search for `paper.md` — check root, `paper/`, `joss/`, and `inst/paper/`. If no `paper.md` exists, note this as a critical gap.

### 1b. Load User Config

Read `.claude/pub-pipeline.local.md` if it exists (Read tool). Extract author metadata (ORCID, affiliation) and package context from YAML frontmatter. If the file is missing, inform the user and offer to create one from the template at `${CLAUDE_PLUGIN_ROOT}/docs/user-config-template.md`.

### 2. Check Software Requirements

**License** (Read tool):
- Verify a plain-text `LICENSE` or `LICENSE.md` file exists
- Confirm it's an OSI-approved license (MIT, GPL-2, GPL-3, Apache-2.0, BSD, etc.)

**Repository quality** (Bash tool):
```bash
# Development history: 6+ months of commits
git log --oneline --since="6 months ago" | wc -l

# Multiple contributors
git shortlog -sn --all | head -10

# Issues/PRs activity
gh issue list --state all --limit 5
gh pr list --state all --limit 5

# Tags/releases
git tag -l | tail -5
```

**Documentation** (Glob/Read tools):
- `README.md` exists with installation instructions
- Usage examples present (in README, vignettes, or both)
- API documentation exists (`man/` directory with `.Rd` files)
- Contributing guidelines (`CONTRIBUTING.md` or in README)
- Issue reporting instructions

**Testing** (Bash/Glob tools):
- Test directory exists (`tests/testthat/` or `tests/`)
- Tests actually run: `Rscript -e 'devtools::test()'`
- Coverage check: `Rscript -e 'covr::package_coverage()'`

**Installation** (Bash tool):
- Verify package installs cleanly: `Rscript -e 'devtools::install()'`

### 3. Check Paper Format

If `paper.md` exists, validate against JOSS format requirements.

**YAML frontmatter** (Read tool — check first 50 lines):

| Field | Required | Check |
|-------|----------|-------|
| `title` | Yes | Present, descriptive, includes package name |
| `tags` | Yes | Array of relevant keywords, includes "R" |
| `authors` | Yes | Each has `name`, `orcid`, `affiliation` |
| `affiliations` | Yes | Each has `index` and `name` |
| `date` | Yes | Format: `%e %B %Y` (e.g., "9 October 2024") |
| `bibliography` | Yes | Points to existing `.bib` file |

**Required sections** (Grep tool):
- `# Summary` — high-level for non-specialists
- `# Statement of Need` or `# Statement of need` — research purpose, target audience
- `# State of the Field` or `# State of the field` — comparison to existing packages
- `# Software Design` or `# Software design` — architecture, trade-offs
- `# Research Impact` or similar — evidence of impact
- `# AI Usage Disclosure` or similar — generative AI transparency
- `# References`

**Bibliography** (Read/Grep tools):
- `paper.bib` exists at expected path
- All `@citation_key` references in paper.md have matching BibTeX entries
- No orphaned BibTeX entries (optional, informational)

**Citation cross-reference** (Bash tool):
```bash
# Extract citation keys from paper.md and cross-reference against paper.bib
grep -oP '@[\w]+' paper.md | sort -u > /tmp/paper_keys.txt
grep -oP '^\s*@\w+\{(\w+)' paper.bib | grep -oP '\w+$' | sort -u > /tmp/bib_keys.txt
comm -23 /tmp/paper_keys.txt /tmp/bib_keys.txt
```
All citation keys in paper.md must have matching BibTeX entries. Report any missing.

**Word count** (Bash tool):
```bash
# Count words between end of YAML frontmatter and References section
awk '/^---$/{n++; next} n>=2 && !/^# References/{print}' paper.md | wc -w
```
Target: 750-1750 words.

**Figures and math**:
- Figures are captioned and referenced image files exist
- Math uses `$...$` (inline) and `$$...$$` (display) syntax

### 4. Check AI Disclosure

If the package or paper used generative AI tools, verify the disclosure includes:
- Specific tools/models used (with versions)
- Where AI was applied (code, paper, documentation)
- Nature and scope of assistance
- Confirmation that humans reviewed and made core design decisions

### 5. Produce Gap Report

Format the report following this structure:

```markdown
# JOSS Audit Report: {package name}

## Summary
- **Status**: READY / NEEDS WORK / NOT READY
- **Paper exists**: Yes/No
- **Reviewer checklist**: X/Y items pass

## Critical Gaps (Blockers)
1. [Missing item] — [what to do]

## Warnings
1. [Issue] — [recommendation]

## Reviewer Checklist Results

### General Checks
- [ ] or [x] Source code at repository URL
- [ ] or [x] OSI-approved LICENSE file
- [ ] or [x] Submitting author is major contributor
- [ ] or [x] Demonstrates research impact

### Development History
- [ ] or [x] 6+ months public development
- [ ] or [x] Multiple contributors
- [ ] or [x] Issues/PRs activity
- [ ] or [x] Tagged releases

### Functionality
- [ ] or [x] Installation works as documented
- [ ] or [x] Functional claims confirmed

### Documentation
- [ ] or [x] Statement of need in README or paper
- [ ] or [x] Installation instructions
- [ ] or [x] Usage examples
- [ ] or [x] API documentation
- [ ] or [x] Automated tests
- [ ] or [x] Contribution guidelines

### Paper Quality
- [ ] or [x] Summary section
- [ ] or [x] Statement of Need
- [ ] or [x] State of the Field
- [ ] or [x] Software Design
- [ ] or [x] Research Impact Statement
- [ ] or [x] AI Usage Disclosure
- [ ] or [x] References complete
- [ ] or [x] Word count 750-1750

## Recommended Next Steps
1. [Ordered actions]
```

### 6. Offer to Fix

After presenting the report, offer to address gaps:
- Create `paper.md` and `paper.bib` via the `pub-pipeline:joss-writer` agent (or `/joss-draft` skill)
- Add `CONTRIBUTING.md`
- Add `CODE_OF_CONDUCT.md`
- Add missing ORCID fields
- Fix YAML frontmatter formatting
- Create AI usage disclosure section

For a deeper multi-agent audit, launch the `pub-pipeline:joss-reviewer` agent which spawns `software-auditor`, `community-auditor`, and `field-scout` specialists in parallel.

## Reference Files

For the complete JOSS requirements and reviewer checklist, consult:
- **`${CLAUDE_PLUGIN_ROOT}/docs/joss-reference.md`** — Full JOSS submission requirements, reviewer checklist, paper format spec, and post-acceptance workflow
- **`${CLAUDE_PLUGIN_ROOT}/docs/joss-exemplars.md`** — Real JOSS R package paper examples with structural analysis and patterns

## Important Notes

- JOSS has no submission or publication fees.
- JOSS does not outright reject — they request revisions. But scope mismatches can lead to desk rejection.
- The 6-month development history requirement is checked by reviewers examining git history.
- "State of the Field" must name specific competing packages and explain why building a new package was justified over contributing to existing ones.
- Post-acceptance requires: tagged release, Zenodo/figshare deposit, archive DOI.
