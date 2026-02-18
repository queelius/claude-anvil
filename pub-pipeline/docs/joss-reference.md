# JOSS Submission Reference

## Sources
- [JOSS Submission Guide](https://joss.readthedocs.io/en/latest/submitting.html)
- [JOSS Review Checklist](https://joss.readthedocs.io/en/latest/review_checklist.html)
- [JOSS Paper Format](https://joss.readthedocs.io/en/latest/paper.html)
- [JOSS Editorial Policies](https://joss.theoj.org/about#editorial_policies)

---

## Pre-Submission Requirements

### Software Must Have
- [ ] OSI-approved open source license (MIT, GPL, BSD, Apache, etc.)
- [ ] Publicly accessible repository (GitHub, GitLab, Bitbucket)
- [ ] Browsable source code without registration
- [ ] Readable issue tracker without registration
- [ ] Allows community issue creation
- [ ] Cloneable without registration
- [ ] Obvious research application (not purely pedagogical or trivial)
- [ ] Feature-complete, production-ready (not a prototype or work-in-progress)
- [ ] Comprehensive documentation (installation, usage, API reference)
- [ ] Automated testing with reasonable coverage
- [ ] Packaged per language community standards (CRAN for R, PyPI for Python, etc.)

### Development History
- [ ] Minimum 6 months of public development history
- [ ] Evidence of releases, public issues, and pull requests
- [ ] Contributions from individuals beyond original team (encouraged but not strictly required)
- [ ] Active maintenance (recent commits, responsive to issues)

### Author Requirements
- [ ] Submitting author is a major contributor to the software
- [ ] Active GitHub account for the submitting author
- [ ] All authors agree to participate in the review process
- [ ] All authors have ORCID identifiers

### Scope
- [ ] Software is within JOSS scope (research tools, not datasets, papers-about-papers, or thin wrappers)
- [ ] Not previously published in another journal (dual submission not allowed)
- [ ] Distinct from existing JOSS publications (not a minor variant of already-published software)

---

## Paper Format: `paper.md`

### Required YAML Frontmatter

```yaml
---
title: 'packagename: Short description of what it does'
tags:
  - R
  - relevant-tag-1
  - relevant-tag-2
authors:
  - name: First M. Last
    orcid: 0000-0000-0000-0000
    affiliation: 1
  - name: Second Author
    orcid: 0000-0000-0000-0000
    affiliation: "1, 2"
    corresponding: true
affiliations:
  - name: Department, University
    index: 1
    ror: 00000000  # optional Research Organization Registry ID
  - name: Other Institution
    index: 2
date: "16 February 2026"
bibliography: paper.bib
---
```

#### Frontmatter Field Details
- [ ] **title**: Include package name followed by colon and description. Use single quotes around the entire title
- [ ] **tags**: 3-5 relevant tags; include the programming language
- [ ] **authors**: Every author must have `name`, `orcid`, and `affiliation`. Use `corresponding: true` for the corresponding author
- [ ] **orcid**: Full 16-digit ORCID for every author (no exceptions). Register at https://orcid.org if needed
- [ ] **affiliations**: Use `index` numbers referenced by author entries. Include `ror` (Research Organization Registry ID) when available
- [ ] **date**: Submission date in "DD Month YYYY" format
- [ ] **bibliography**: Points to `paper.bib` (BibTeX file in the same directory)

### Required Sections

1. **Summary** — High-level functionality for a non-specialist audience. 2-4 sentences.
2. **Statement of Need** — Research problem, target audience, why existing tools are insufficient.
3. **State of the Field** — Name competing packages explicitly and explain how this software differs. Vague claims without citations are flagged by reviewers.
4. **Software Design** — Architecture, design decisions, and trade-offs (required since 2024).
5. **Research Impact Statement** — Citations to published work using the software, or concrete anticipated impact for new software.
6. **AI Usage Disclosure** — Required even if AI was not used (state "No AI tools were used").
7. **Acknowledgements** — Financial support, computing resources, non-author contributors.
8. **References** — Auto-generated from `paper.bib`.

### Word Count
- Target: 750-1750 words (excluding references and frontmatter)
- Papers under 750 words may be asked to expand
- Papers significantly over 1750 words will be asked to shorten
- The word limit enforces focus; detailed documentation belongs in the software's own docs, not the paper

### Citation Syntax
- Parenthetical: `[@key]` renders as "(Author Year)"
- In-text: `@key` renders as "Author (Year)"
- Multiple: `[@key1; @key2]` renders as "(Author1 Year1; Author2 Year2)"
- With page: `[@key, p. 42]` renders as "(Author Year, p. 42)"
- BibTeX entries in `paper.bib` — use full venue names (not abbreviations)

### Math Support
- Inline: `$x$` or `$\sin \frac{\pi}{2}$`
- Display: `$$...$$` on a separate line
- Labels: `\label{eq:name}` inside equation environment
- References: `\ref{eq:name}` or `\autoref{eq:name}`
- LaTeX math packages available: amsmath, amssymb

### Figures
- Syntax: `![Caption text](path/to/image.png)`
- Must be captioned and placed alone in a paragraph (blank lines above and below)
- Optional sizing: `{height="9pt"}` or `{width="100%"}`
- Supported formats: PNG, JPEG, PDF, SVG
- Place figure files in the same directory as `paper.md` or a subdirectory
- Reference in text with `\autoref{fig:label}` (if using LaTeX figure environment)

---

## Reviewer Checklist

### General Checks
- [ ] Source code is at the stated repository URL
- [ ] An OSI-approved `LICENSE` file is present in the repository root
- [ ] Submitting author has made major contributions to the software
- [ ] Author list is appropriate and complete (no missing contributors, no gift authorship)
- [ ] Software demonstrates clear research impact or scholarly significance

### Development History and Open-Source Practice
- [ ] Evidence of sustained development over months/years (not a single bulk commit)
- [ ] At least six months of public history with releases, issues, and pull requests
- [ ] Multiple developer commits; evidence of community feedback or engagement
- [ ] Follows open-source standards: license, documentation, tests, releases, contribution pathways
- [ ] Version control used effectively (meaningful commit messages, branches for features)

### Functionality
- [ ] Installation proceeds as documented (tested by reviewer)
- [ ] Core functional claims confirmed (reviewer runs examples)
- [ ] Performance claims verified with evidence (benchmarks, comparisons) or marked N/A
- [ ] Software handles edge cases gracefully (meaningful error messages, not silent failures)

### Documentation
- [ ] Clear problem definition and target audience stated
- [ ] Installation instructions with all dependencies listed
- [ ] Real-world usage examples (not just toy examples)
- [ ] Core functionality documented (API reference for all public functions/methods)
- [ ] Automated test suite with instructions for running tests
- [ ] Contribution guidelines (`CONTRIBUTING.md` or equivalent)
- [ ] Issue reporting and support guidelines
- [ ] Code of conduct (recommended)

### Paper Quality
- [ ] **Summary** is clear and accessible to non-specialists
- [ ] **Statement of Need** clearly states the problem and target audience
- [ ] **State of the Field** names and compares to existing packages (not vague)
- [ ] **Software Design** explains architecture and trade-offs
- [ ] **Research Impact Statement** provides evidence of impact or concrete anticipated use
- [ ] **AI Usage Disclosure** is present and transparent
- [ ] Writing quality is high: no structural or language issues
- [ ] References are complete, properly formatted, and use full venue names
- [ ] Word count is within 750-1750 range

---

## AI Usage Policy

### Required Disclosure Must Include
- Specific tools and models used (with versions, e.g., "ChatGPT-4, GitHub Copilot")
- Where AI was applied (code generation, paper drafting, documentation, test writing)
- Nature and scope of assistance (e.g., "used for initial boilerplate" vs. "generated core algorithm")
- Confirmation that humans reviewed, validated, and made all core design decisions

### Restrictions
- AI cannot be used in author-editor or author-reviewer conversations (except for translation assistance)
- All evaluative decisions must remain human-made
- Non-disclosure can lead to desk rejection, mandatory revisions, or withdrawal of accepted papers

### Best Practice
- Disclose proactively, even for minor AI use
- Frame disclosure positively ("We used X to improve Y, and validated by Z")
- Include the disclosure section in the paper even if no AI was used

---

## Submission Process

### Step-by-Step

1. **Pre-submission inquiry** (optional but recommended): Open an issue at https://github.com/openjournals/joss-reviews/issues to check scope. An editor responds within a few days.

2. **Prepare repository**: Ensure all reviewer checklist items pass. The repository is the primary artifact under review.

3. **Write `paper.md` and `paper.bib`**: Place in the repository root or a `paper/` subdirectory.

4. **Submit** at https://joss.theoj.org/papers/new with the repository URL and branch containing `paper.md`.

5. **Pre-review issue created**: A bot creates a GitHub issue in `openjournals/joss-reviews`. Managing editor checks scope and assigns a handling editor.

6. **Editor assigns reviewers**: 2+ reviewers assigned (typically within 1-2 weeks).

7. **Review period**: Reviewers work through the checklist in the GitHub issue, checking boxes and leaving comments. Target: 2 weeks for initial review, 4-8 weeks total.

8. **Author responds**: Address each checklist item, comment in the review issue confirming what was fixed.

9. **Reviewers confirm**: Once all checklist items satisfied, reviewers recommend acceptance.

10. **Acceptance and archival**: Create tagged release, deposit with Zenodo/figshare for archive DOI, update review issue. JOSS assigns paper DOI via CrossRef.

**No submission or publication fees.** JOSS is a free, open-access journal.

### Timeline Expectations
- Pre-review to reviewer assignment: 1-2 weeks
- Initial reviewer comments: 2-4 weeks after assignment
- Author revisions: varies (1-4 weeks typical)
- Total from submission to acceptance: 4-12 weeks (median ~6 weeks)
- Post-acceptance to DOI: 1-2 days

---

## Common Issues in Review

### Paper Content
1. **Weak "State of the Field"**: The most common criticism. Name 3-5 competing packages and explain the gap your software fills. Vague claims without citations are insufficient
2. **Paper too long**: Over 1750 words means content belongs in software docs, not the paper. Move API descriptions and methodology derivations to vignettes
3. **Paper too short**: Under 750 words usually means Statement of Need or State of the Field is underdeveloped
4. **Missing Research Impact Statement**: Provide concrete citations or describe specific ongoing research projects
5. **Incomplete AI Usage Disclosure**: Disclose even minor AI use. Omission is treated more seriously than the use itself

### Repository and Software
6. **No automated test suite**: JOSS requires automated tests (testthat for R, pytest for Python). Manual testing instructions alone are insufficient
7. **Missing `CONTRIBUTING.md`**: Reviewers check for contribution guidelines
8. **No clear installation instructions**: Must be documented and testable by reviewers
9. **Missing ORCID for authors**: Every author must have an ORCID (hard requirement)

### Process Issues
10. **Slow author response**: Respond within a few days, even if just to acknowledge and provide a timeline
11. **Not engaging with feedback**: Comment on each checklist item with what was fixed and where
12. **Submitting before software is ready**: JOSS reviews the software, not just the paper. Wait until production-ready

---

## Post-Acceptance

1. **Create tagged software release**: Tag the exact version that was reviewed (e.g., `v1.0.0`)
2. **Deposit with Zenodo or figshare**: Archive the repository to get a DOI for the software itself (separate from the paper DOI)
3. **Update review issue**: Provide the version number and archive DOI to the editor
4. **JOSS assigns paper DOI**: Metadata deposited with CrossRef; paper appears on https://joss.theoj.org
5. **Update software documentation**: Add the JOSS DOI badge to `README.md` and include the citation in documentation
6. **Add citation file**: Create or update `CITATION.cff` or `inst/CITATION` (for R) with the JOSS paper reference

---

## Quick Reference: Repository Checklist

| Item | Where |
|------|-------|
| Open source license | `LICENSE` in repo root |
| Installation docs | `README.md` or docs site |
| Usage examples | `README.md`, vignettes, or docs |
| API documentation | Function docs, pkgdown site, or equivalent |
| Automated tests | `tests/` directory with test framework |
| Contribution guidelines | `CONTRIBUTING.md` |
| Issue tracker | GitHub Issues (public, writable) |
| JOSS paper | `paper.md` + `paper.bib` in repo root or `paper/` |
| ORCID for all authors | YAML frontmatter in `paper.md` |
| AI usage disclosure | Section in `paper.md` |

---

**Last Updated**: 2026-02-16
