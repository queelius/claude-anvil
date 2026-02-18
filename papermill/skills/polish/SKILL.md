---
name: polish
description: >-
  This skill should be used when the user asks to "polish my paper for
  submission", "pre-flight check", "is my paper ready to submit",
  "final check before submission", "prepare for submission", or needs
  final preparation before submitting a paper. Performs a systematic
  pre-flight check covering formatting, citations, figures, metadata,
  and build verification. Produces a checklist report with suggested
  fixes.
---

# Submission Polish

Perform a final quality check on a research paper before submission. This is the last line of defense -- catch everything that would annoy a reviewer or cause a desk rejection.

## Step 1: Read Context

Read `.papermill.md` (Read tool) for:
- **Venue**: Target venue and its requirements.
- **Format**: Paper format (latex, markdown, rmarkdown).
- **Review history**: Outstanding issues from previous reviews.

If `.papermill.md` does not exist, the pre-flight check can still run — infer the format from the manuscript files and ask the user for the target venue. The checklist works regardless. Suggest running `/papermill:init` to capture venue and format persistently.

Read the complete manuscript (Read tool).

## Step 2: Pre-Flight Checklist

Work through each category systematically. Report issues as they are found.

### Formatting
- [ ] Paper compiles without errors
- [ ] No LaTeX warnings (especially undefined references, missing citations)
- [ ] Page count within venue limits
- [ ] Correct venue template/style file used
- [ ] Margins, font size, and spacing match requirements
- [ ] Line numbers included if required by venue
- [ ] Anonymous submission if required (no author names in text or metadata)

### Abstract
- [ ] Word count within venue limits (typically 150-300 words)
- [ ] Self-contained (no citations, no undefined terms)
- [ ] States the problem, approach, main result, and significance
- [ ] Matches the paper's actual content

### Citations and References
- [ ] All citations resolve (no "?" in the PDF)
- [ ] Bibliography is complete (no missing fields)
- [ ] Citation style matches venue requirements
- [ ] All references are cited in the text (no orphan bib entries that should be removed)
- [ ] All cited works are in the bibliography
- [ ] Self-citations are reasonable in number

### Figures and Tables
- [ ] All figures are referenced in the text
- [ ] Figure captions are self-contained (reader should understand without reading the text)
- [ ] Resolution is sufficient for print (300+ DPI for raster images)
- [ ] Color is used accessibly (works in grayscale, colorblind-safe)
- [ ] Tables have clear headers and units

### Mathematical Content
- [ ] All symbols are defined before use
- [ ] Notation is consistent throughout
- [ ] Equation numbering is correct and referenced
- [ ] Theorem/definition/proof environments are properly labeled
- [ ] No orphan proofs (every proof has a parent theorem/proposition)

### Writing Quality
- [ ] No first-person narrative inconsistencies ("I" vs "we")
- [ ] Consistent tense usage
- [ ] No obvious typos or grammatical errors
- [ ] Acronyms defined on first use
- [ ] No overly long paragraphs (break up walls of text)

### Metadata
- [ ] Author names and affiliations are correct
- [ ] ORCID identifiers included if venue supports them
- [ ] Keywords/subject classification provided
- [ ] Acknowledgments section present (funding, help, etc.)
- [ ] Data availability statement if required
- [ ] Code availability statement if applicable

### Supplementary Material
- [ ] Appendices are referenced from the main text
- [ ] Supplementary files are in the required format
- [ ] Appendix content is not essential to understanding the main paper

## Step 3: Build Verification

Run a clean build appropriate to the paper format (Bash tool). Use the manuscript path discovered in Step 1 (from `.papermill.md` or by scanning for `.tex`/`.md`/`.Rmd` files with Glob tool). Examples:

**LaTeX papers:**
```bash
latexmk -pdf <path-to-main.tex>
```

**Markdown papers:**
```bash
pandoc <path-to-paper.md> -o paper.pdf
```

**R Markdown papers:**
```bash
Rscript -e "rmarkdown::render('<path-to-paper.Rmd>')"
```

Report:
- Number of pages
- Number of warnings (LaTeX warnings, pandoc warnings, R warnings)
- Number of undefined references
- Number of overfull/underfull hbox warnings (LaTeX; prioritize overfull)

## Step 4: Present Results

Present the checklist results:

> **Pre-Flight Report**
>
> **Status**: [Ready / Issues found]
>
> **Passing**: N/M checks passed
> **Issues**:
> 1. [issue + suggested fix]
> 2. [issue + suggested fix]
> ...

## Step 5: Fix Issues

Offer to fix issues directly:

- Formatting fixes: Apply them.
- Content fixes: Suggest specific changes and ask for approval.
- Style fixes: Propose rewording.

## Step 6: Update State File

After all issues are resolved:

- Set `stage` to `submission` in `.papermill.md` (Edit tool).
- Append a timestamped note: "Pre-flight check passed. Ready for submission to [venue]."

## Step 7: Suggest Next Steps

> Paper is polished and ready. Final steps:
>
> - **Submit**: Follow the venue's submission instructions.
> - **`/papermill:venue`**: If you haven't selected a venue yet, do so now.
> - **Archive**: Consider creating a git tag marking the submitted version.
