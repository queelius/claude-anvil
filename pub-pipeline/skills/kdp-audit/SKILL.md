---
name: kdp-audit
description: "This skill should be used when the user asks to \"KDP audit\", \"check manuscript formatting\", \"is my book ready for KDP\", \"Amazon publishing requirements\", \"Kindle formatting check\", \"manuscript readiness\", \"book formatting audit\", \"prepare for Amazon KDP\", or mentions KDP/Amazon publishing compliance. It audits a book manuscript against Amazon KDP (Kindle Direct Publishing) requirements for both eBook and paperback formats, handling technical books (LaTeX, math-heavy) and fiction/general nonfiction."
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

Read `.claude/pub-pipeline.local.md` if it exists (Read tool). Extract the `kdp` configuration section and `author` metadata from YAML frontmatter. The config may include:

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

**Trim size validation**:
- Common sizes for nonfiction: 6×9 inches
- Common sizes for fiction: 5.5×8.5 inches (also 5×8, 5.25×8)
- Common sizes for textbooks: 7×10, 7.5×9.25, 8×10, 8.25×11, 8.5×11 inches
- Verify manuscript trim size matches KDP supported sizes

**Margin requirements** (varies by page count):
- Inside margin formula: 0.375" + (page_count / 1000) * 0.125"
- Outside margin: 0.25" minimum
- Top/bottom margins: 0.25" minimum
- Gutter (spine side) must accommodate binding: 0.5"+ for 150+ pages
- Check if LaTeX geometry package or Word margins are set correctly

**Font requirements**:
- Fonts must be embedded (verify in PDF metadata)
- Standard fonts preferred: Times New Roman, Garamond, Arial, Courier
- Minimum 7pt font size (10-12pt body text recommended)
- Check LaTeX preamble or Word styles for font declarations

**Page numbers and headers/footers**:
- Page numbers should start after front matter (after TOC)
- Headers/footers optional but should be consistent
- Verify no page numbers on blank pages or chapter openers (style preference)

**Table of Contents** (Read/Grep tools):
- TOC must be present and functional (hyperlinked in eBook)
- Verify chapter titles match TOC entries
- Check depth (typically 2-3 levels)

### 3. Check Cover Specifications

**Kindle eBook cover** (file check via Glob tool):
- Minimum resolution: 2560×1600 pixels
- Aspect ratio: 1.6:1 (portrait)
- Color mode: RGB
- Format: JPEG or TIFF
- File size: <50MB
- Look for files matching: `cover*.jpg`, `cover*.jpeg`, `cover*.tiff`, `ebook-cover.*`

**Paperback cover** (if applicable):
- Resolution: 300 DPI minimum
- Color mode: CMYK for print, RGB for PDF preview
- Format: PDF preferred (flattened layers)
- Spine width calculation: page_count × 0.002252 inches (for white paper)
- Spine width calculation: page_count × 0.0025 inches (for cream paper)
- Full cover width: (trim_width × 2) + spine_width + 0.25" bleed
- Full cover height: trim_height + 0.25" bleed
- Look for files matching: `paperback-cover.pdf`, `full-cover.pdf`, `cover-print.*`

**Actual dimension verification** (Bash tool):
- If `identify` (ImageMagick) is available: `identify -format "%wx%h" cover.jpg`
- Otherwise fall back to `file cover.jpg` which often reports dimensions
- For eBook cover: verify dimensions are at least 2560x1600, verify aspect ratio is approximately 1.6:1
- For paperback cover PDF: verify resolution is at least 300 DPI
- Report actual vs required dimensions in the audit output

**Cover content requirements**:
- Title must be clearly readable at thumbnail size
- Author name present
- High contrast, professional design
- No prohibited content (pornographic, violent, misleading)

If cover files don't exist, note as a critical gap.

### 4. Check Metadata Readiness

**Required metadata**:
- **Title**: Descriptive, not misleading (max 200 chars)
- **Subtitle**: Optional but recommended (max 200 chars)
- **Series info**: Series name and number if applicable
- **Description/blurb**: Up to 4000 characters, HTML formatting allowed
- **Categories**: Up to 3 BISAC codes (Browse Subject Headings)
- **Keywords**: Up to 7 keywords/phrases for discoverability
- **Author bio**: Brief professional bio (100-200 words recommended)
- **Language**: Primary language of manuscript

**Pricing and rights**:
- ISBN: Optional (KDP provides free ASIN for eBooks, offers free ISBN for paperback)
- Publication date: Can be set to auto-publish or scheduled
- Territories: Where distribution rights are held
- DRM: Recommended to enable for eBooks

Grep for metadata in manuscript front matter or config. If missing, list what needs to be provided via KDP dashboard.

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

Format the report as:

```markdown
# KDP Audit Report: {book title}

## Summary
- **Status**: READY / NEEDS WORK / NOT READY
- **Manuscript type**: Technical / Fiction / Nonfiction
- **Format**: LaTeX / DOCX / EPUB / PDF
- **Target**: eBook only / Paperback only / Both

## Critical Gaps (Must Fix)
1. [Issue description] — [file:line] — [how to fix]

## Warnings (Should Fix)
1. [Issue description] — [recommendation]

## Interior Formatting
- [ ] or [x] Trim size: {size} (supported: yes/no)
- [ ] or [x] Margins: inside {calc}, outside {val}, top {val}, bottom {val}
- [ ] or [x] Fonts embedded and standard
- [ ] or [x] Page numbers start after front matter
- [ ] or [x] Table of Contents present and functional

## Cover Specifications
- [ ] or [x] eBook cover: {resolution}, {ratio}, {format}
- [ ] or [x] Paperback cover: {resolution}, spine width {calc}
- [ ] or [x] Cover dimensions verified: {actual} (required: {minimum})

## Metadata
- [ ] or [x] Title and subtitle
- [ ] or [x] Description/blurb (<4000 chars)
- [ ] or [x] Categories (up to 3 BISAC codes)
- [ ] or [x] Keywords (up to 7)
- [ ] or [x] Author bio present

## Technical Books Only
- [ ] or [x] LaTeX compiles successfully
- [ ] or [x] Math rendering correct
- [ ] or [x] Code listings formatted
- [ ] or [x] Index and bibliography present

## Fiction Only
- [ ] or [x] Front matter order: title -> copyright -> dedication -> TOC
- [ ] or [x] Back matter includes About the Author
- [ ] or [x] Scene breaks use consistent markers
- [ ] or [x] Scene breaks clearly marked
- [ ] or [x] Dialog formatting consistent
- [ ] or [x] Paragraph indentation correct

## eBook Validation
- [ ] or [x] EPUB validates (epubcheck)
- [ ] or [x] No Kindle-breaking issues (footnotes, wide tables, complex CSS)

## Recommended Next Steps
1. [Ordered list of actions to reach READY status]
```

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

For complete KDP requirements and submission workflow, consult:
- **`${CLAUDE_PLUGIN_ROOT}/docs/kdp-reference.md`** — Full KDP formatting requirements, cover templates, metadata guidelines, and submission checklist

## Important Notes

- **KDP review time**: 24-72 hours for eBooks, up to 5 business days for paperbacks
- **Content guidelines**: No prohibited content (explicit sexual content requires erotica category, hate speech prohibited, public domain verification required)
- **ISBN**: Optional for eBooks (Amazon provides ASIN). Free ISBN available for paperbacks, or a custom ISBN can be provided.
- **Royalty options**: 35% (no delivery cost) or 70% (delivery cost deducted, price restrictions apply)
- **KDP Print vs. IngramSpark**: KDP is Amazon-exclusive; consider IngramSpark for wider distribution
- **Preview before publishing**: Always download and review the digital previewer or order a proof copy
- **Updates**: Manuscripts can be updated post-publication, but updates take 24-72 hours to propagate
