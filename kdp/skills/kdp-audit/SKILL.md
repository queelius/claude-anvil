---
name: kdp-audit
description: >-
  Audit a book manuscript against Amazon KDP requirements: interior
  formatting, cover specs, metadata, and genre-specific checks. Handles
  technical books (LaTeX, math), fiction, and nonfiction. Produces a
  structured gap report with Critical and Warnings sections plus
  automation suggestions.
---

# KDP Manuscript Audit

Audit a book manuscript against Amazon KDP (Kindle Direct Publishing) requirements and produce a structured gap report. This skill evaluates interior formatting, cover specs, metadata completeness, and genre-specific requirements (technical vs. fiction).

## Workflow

### 1. Detect Manuscript Type

Identify manuscript files and format. Look for these file types in the current directory or specified path:

**Primary manuscript formats** (Glob tool):
- `.tex` files (LaTeX manuscripts, common for technical books)
- `.docx` files (Microsoft Word, common for fiction/nonfiction)
- `.epub` files (eBook source)
- `.md` files (Markdown manuscripts)
- `.pdf` files (final output)
- `.kpf` files (Kindle Create project)

**Manuscript type classification**:
- **Technical**: LaTeX source, math equations, code listings, index/bibliography
- **Fiction**: Structured chapters, scene breaks, dialog formatting
- **General nonfiction**: Standard chapters, images, minimal equations

If no manuscript is found, ask the user which file to audit.

### 1b. Load User Config

Read `.claude/kdp.local.md` if it exists (Read tool). Extract the `kdp` configuration section and `author` metadata from YAML frontmatter. The config may include:

```yaml
kdp:
  trim_size: "6x9"
  paper_type: "white"
  binding: "paperback"
  genre: "technical"
  target_page_count: 300
author:
  name: "Author Name"
  bio: "Brief author bio"
```

If the file is missing, inform the user and offer to create one from the template at `${CLAUDE_PLUGIN_ROOT}/docs/user-config-template.md`.

### 2. Check Interior Formatting

Verify the manuscript meets KDP interior requirements. Full specs are in `${CLAUDE_PLUGIN_ROOT}/docs/kdp-reference.md` (Interior Formatting section); read it and check the manuscript against:

- **Trim size**: look for margin or geometry declarations (Grep tool); verify it matches a KDP-supported size (common for nonfiction 6x9, fiction 5.5x8.5 or 5x8, textbooks 7x10 or 8.5x11)
- **Margins**: inside margin grows with page count (formula `0.375" + page_count / 1000 * 0.125"`), outside at least 0.25", gutter at least 0.5" for 150+ pages
- **Fonts**: must be embedded; standard fonts preferred (Times New Roman, Garamond, Arial, Courier); minimum 7pt
- **Page numbers**: start after front matter, consistent placement
- **Table of Contents**: present and functional, hyperlinked in eBook, typically 2 to 3 levels deep

### 3. Check Cover Specifications

Verify covers meet KDP requirements. Full specs are in `${CLAUDE_PLUGIN_ROOT}/docs/kdp-reference.md` (Cover Requirements section).

**Find cover files** (Glob tool): `cover*.jpg`, `cover*.jpeg`, `cover*.tiff`, `ebook-cover.*` for eBook; `paperback-cover.pdf`, `full-cover.pdf`, `cover-print.*` for paperback.

**Verify dimensions** (Bash tool):
- If `identify` (ImageMagick) is available: `identify -format "%wx%h" cover.jpg`
- Otherwise: `file cover.jpg` often reports dimensions
- eBook cover: minimum 2560x1600 pixels, aspect ratio approximately 1.6:1, RGB, JPEG or TIFF, under 50MB
- Paperback cover PDF: minimum 300 DPI, spine width `page_count * 0.002252"` (white paper) or `0.0025"` (cream)

**Cover content requirements**: title readable at thumbnail size, author name present, high contrast, no prohibited content. Report actual vs. required dimensions. If cover files are absent, flag as a critical gap.

### 4. Check Metadata Readiness

Verify all required listing metadata exists in the manuscript or in `.claude/kdp.local.md`. Full field specs and constraints are in `${CLAUDE_PLUGIN_ROOT}/docs/kdp-reference.md` (Metadata section).

Grep manuscript front matter and the user config for:

- Title, subtitle (each up to 200 chars), series info
- Description or blurb (up to 4000 chars, HTML allowed)
- Up to 3 BISAC categories
- Up to 7 keywords
- Author bio (100 to 200 words recommended)
- Language, pricing, territories, DRM setting, ISBN decision

Flag missing fields so the user can provide them via the KDP dashboard.

### 5. Technical Books Only

If manuscript is technical (LaTeX, math-heavy, code listings):

**LaTeX compilation** (Bash tool):
```bash
cd /path/to/manuscript && pdflatex -interaction=nonstopmode manuscript.tex
```
Verify compilation succeeds with no critical errors.

**Math rendering**:
- Check for `\usepackage{amsmath}` or equivalent
- Verify math symbols render correctly (sample PDF pages)
- KDP supports PDF with embedded fonts; math must be rasterized

**Code listings**:
- Check for `listings` or `minted` package usage
- Verify syntax highlighting, line numbers, proper formatting
- Ensure code fits within margins (line wrapping or font scaling)

**Index and bibliography**:
- Verify `\printindex` and `\bibliography{}` commands present
- Check that index entries are defined (`\index{}`)
- Verify `.bib` file exists and is referenced
- Run `makeindex` and `bibtex` successfully

### 5b. eBook Validation

Check for eBook-specific issues that affect Kindle rendering and KDP acceptance.

**EPUB validation** (Glob tool, Bash tool):
- Check if `.epub` files exist in the project
- If `epubcheck` is available (`which epubcheck`), run it on the EPUB file and report results
- If `epubcheck` is not installed, note it as a recommendation and list common EPUB issues to manually check:
  - Broken NCX/nav table of contents
  - Missing cover image reference in OPF manifest
  - Invalid HTML entities in content
  - CSS that won't render on Kindle (floats, absolute positioning, complex grid/flexbox)
- If no EPUB exists but `.md` or `.docx` source files do, recommend conversion via Pandoc before audit:
  ```bash
  pandoc manuscript.md -o manuscript.epub --toc --metadata title="Book Title"
  ```
- Note: Kindle Direct Publishing accepts EPUB, DOCX, and PDF. EPUB gives the most control over eBook formatting.

### 5c. Kindle Format Checks

Check for issues that specifically break on Kindle devices:

**Footnotes** (Grep tool):
- Search for `\footnote` in LaTeX source, or footnote markers in DOCX/HTML
- Kindle handles footnotes poorly — recommend converting to endnotes for eBooks

**Wide tables** (Grep tool):
- Flag tables with more than 3 columns — Kindle screens are narrow and tables don't reflow well
- Recommend converting wide tables to lists or simplifying

**Complex CSS** (Grep tool):
- If CSS files exist, flag advanced layout rules: absolute positioning, floats, flexbox, grid, fixed widths in pixels
- Kindle's CSS support is limited — flag any rules that won't render correctly

**Large images** (Bash tool):
- Flag individual images over 5MB — they slow loading on Kindle
- Check with `ls -la` on image files or `identify` if ImageMagick is available

### 6. Fiction Only

If manuscript is fiction or narrative nonfiction:

**Chapter structure** (Grep tool):
- Body: Chapters with consistent heading styles
- Verify chapter numbering is sequential with no gaps
- Check for consistent chapter title formatting (all caps, title case, etc.)

**Front matter order validation** (Grep/Read tools):
- Expected order for fiction: title page -> copyright page -> dedication (optional) -> epigraph (optional) -> table of contents
- Flag if critical elements are missing (title page, copyright page)
- Flag if elements are out of standard order

**Back matter order validation** (Grep/Read tools):
- Expected order: acknowledgments (optional) -> about the author -> also by this author (optional) -> preview of next book (optional)
- Flag if "About the Author" section is missing entirely — this is expected by KDP and readers

**Scene breaks and formatting**:
- Scene breaks marked with `* * *` or similar (not just blank lines)
- Dialog formatting: Consistent use of em-dashes vs. quotation marks
- Paragraph indentation: First line indent (0.25-0.5") except after scene breaks
- No widows/orphans (single lines at top/bottom of page)

**Scene break consistency** (Grep tool):
- Check that scene breaks use a consistent marker throughout (all `* * *`, all `---`, all `###`, etc.)
- Flag if multiple different scene break styles are used in the same manuscript
- Flag if bare blank lines (no marker) are used as scene breaks — these can be lost in eBook conversion

**Special elements**:
- Epigraphs formatted consistently
- Letters, emails, or other narrative devices clearly distinguished
- No footnotes (not well-supported in eBooks; use endnotes or inline)

### 7. Produce Gap Report

Use the template at `${CLAUDE_PLUGIN_ROOT}/docs/audit-report-template.md` as the skeleton. Populate findings from the preceding steps. Omit sections that do not apply (for example, the Fiction checklist for a technical book).

### 8. Offer to Fix

After presenting the report, offer to fix issues that can be automated:
- Add missing front matter sections (copyright page, title page templates)
- Fix LaTeX margin settings via `geometry` package
- Generate BISAC category suggestions based on content
- Create author bio template
- Add missing TOC entries
- Fix scene break markers
- Generate spine width calculation for paperback cover

## Reference Files

For complete KDP requirements and the audit output structure:
- `${CLAUDE_PLUGIN_ROOT}/docs/kdp-reference.md` for KDP formatting, cover, metadata, and submission specifications
- `${CLAUDE_PLUGIN_ROOT}/docs/audit-report-template.md` for the gap report skeleton

## Important Notes

- **KDP review time**: 24-72 hours for eBooks, up to 5 business days for paperbacks
- **Content guidelines**: No prohibited content (explicit sexual content requires erotica category, hate speech prohibited, public domain verification required)
- **ISBN**: Optional for eBooks (Amazon provides ASIN). Free ISBN available for paperbacks, or a custom ISBN can be provided.
- **Royalty options**: 35% (no delivery cost) or 70% (delivery cost deducted, price restrictions apply)
- **KDP Print vs. IngramSpark**: KDP is Amazon-exclusive; consider IngramSpark for wider distribution
- **Preview before publishing**: Always download and review the digital previewer or order a proof copy
- **Updates**: Manuscripts can be updated post-publication, but updates take 24-72 hours to propagate
