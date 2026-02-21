---
name: kdp-publish
description: "This skill should be used when the user asks to \"publish on KDP\", \"publish my book\", \"Amazon book publishing\", \"Kindle Direct Publishing\", \"self-publish\", \"publish on Amazon\", \"KDP workflow\", \"submit to Amazon KDP\", \"publish to Kindle\", or mentions Amazon/KDP book publishing. It guides the complete workflow for publishing a book through Amazon KDP, handling both technical books and fiction/nonfiction."
---

# KDP Book Publishing Workflow

Orchestrate the full workflow for publishing a book through Amazon KDP (Kindle Direct Publishing): audit the manuscript, craft the listing, prepare files, and submit. This skill coordinates `/kdp-audit` and `/kdp-listing` into a phased pipeline, then walks through the mechanical submission steps on the KDP dashboard.

## Strategy

The recommended publication sequence:

1. **Audit** -- Verify the manuscript meets KDP formatting and content requirements
2. **Listing** -- Craft blurb, keywords, categories, and author bio (the marketing artifacts that determine discoverability)
3. **Prepare** -- Convert manuscript to final format, verify cover specs
4. **Submit** -- Walk through the KDP dashboard, upload files, set pricing, publish

Each phase gates the next. Do not submit a manuscript that fails audit. Do not fill in listing fields without the artifacts from `/kdp-listing`. Present the phase map, confirm the plan, and proceed one phase at a time.

## Workflow

### Phase 1: Assess Current State

Determine where the book stands in the pipeline to skip completed phases.

**Load user config** (Read tool): Read `.claude/kdp.local.md` if it exists. Extract the `kdp` section and `author` metadata from YAML frontmatter. If the file is missing, offer to create one from the template at `${CLAUDE_PLUGIN_ROOT}/docs/user-config-template.md`.

**Detect manuscript files** (Glob tool): Search for manuscript files in the project:
- `.tex` files (LaTeX -- technical books)
- `.docx` files (Word -- fiction/nonfiction)
- `.epub` files (eBook source)
- `.md` files (Markdown manuscripts)
- `.pdf` files (final output)
- `.kpf` files (Kindle Create project)

Classify the manuscript type: Technical (LaTeX, math, code), Fiction (chapters, dialog), or General nonfiction.

**Check what already exists** (Glob/Read tools):
- Cover files? (`cover*.jpg`, `cover*.pdf`, `paperback-cover.*`, `full-cover.*`)
- Audit already done? (Look for recent audit report in conversation history or notes)
- Listing artifacts in config? (`kdp.blurb`, `kdp.keywords`, `kdp.categories` populated?)
- Manuscript in final format? (compiled PDF, validated EPUB)

**Present status table** to the user summarizing findings.

**Decision matrix** -- determine where to enter the pipeline:

| State | Next Phase |
|-------|------------|
| No manuscript found | Cannot proceed -- ask user for manuscript location |
| Manuscript exists, no audit done | Phase 2: Audit |
| Audit passed, no listing artifacts in config | Phase 3: Listing |
| Listing artifacts ready, manuscript not in final format | Phase 5: Manuscript Preparation |
| Everything ready, not yet submitted | Phase 6: Cover Preparation or Phase 7: Submit |
| Published, not verified | Phase 10: Post-Publish |

Present the recommended plan and confirm with the user before proceeding.

### Phase 2: Audit

Run `/kdp-audit` to evaluate the manuscript against KDP requirements.

The audit checks interior formatting, cover specs, metadata completeness, and genre-specific requirements. It produces a structured gap report with Critical / Warnings / Passed sections.

If critical gaps are found:
1. Present the gap report to the user
2. Offer to fix automatable issues (margins, missing front matter, scene break markers)
3. Guide manual fixes (cover creation, content revisions)
4. Re-audit after fixes

**Gate**: The manuscript must pass audit (no critical gaps) before proceeding to Phase 3. Warnings are acceptable but should be noted for later attention.

### Phase 3: Craft Listing

Run `/kdp-listing` to generate the four marketing artifacts:
- Blurb (book description, max 4000 characters with HTML formatting)
- Keywords (7 keyword phrases for Amazon search)
- BISAC categories (2-3 browse categories)
- Author bio (for the product page and Author Central)

The listing skill reads manuscript context, generates drafts, iterates with the user, and saves all artifacts to `.claude/kdp.local.md`.

**Gate**: All four artifacts must be saved to the config before proceeding. Phase 7 reads them during dashboard submission.

### Phase 4: Pre-Order Setup (Optional)

Ask the user whether they want to set up a pre-order before the book is finalized.

**When pre-orders make sense**: Fiction launches where Day 1 ranking matters (pre-orders count toward release-day sales rank), books with an existing audience, or series releases.

**Pre-order mechanics**:
- Available up to 90 days before publication date
- Upload a placeholder or final manuscript; set publication date and price
- Final manuscript must be uploaded at least 72 hours before publication date
- Missing the 72-hour deadline may result in KDP blocking pre-order privileges for one year

**How to set up**: Create the title on KDP dashboard (see Phase 7), choose "Make this book available for pre-order," set the release date, upload manuscript, and complete pricing (Phase 8).

If not using pre-orders, skip to Phase 5.

### Phase 5: Manuscript Preparation

Ensure the manuscript is in final publishable form.

**Format conversion** (Bash tool):
- *LaTeX to PDF*: Run `pdflatex` (multiple passes for cross-references; add `bibtex` pass if bibliography exists). Verify fonts embedded, margins correct, page numbers start after front matter.
- *Markdown to EPUB*: Use `pandoc manuscript.md -o manuscript.epub --toc`. Validate with `epubcheck` if available.
- *DOCX to PDF*: Use `libreoffice --headless --convert-to pdf` or Word's built-in PDF export with fonts embedded.

**Final proofread checklist**:
- [ ] Front matter complete (title page, copyright, dedication, TOC)
- [ ] Chapter headings consistent in style
- [ ] Page numbers start after front matter
- [ ] All images/figures embedded and captioned
- [ ] Bibliography/references formatted correctly (if applicable)
- [ ] Back matter complete (acknowledgments, About the Author)
- [ ] No orphan blank pages

### Phase 6: Cover Preparation

Verify cover files meet KDP specifications. See `${CLAUDE_PLUGIN_ROOT}/docs/kdp-reference.md` for full cover requirements (dimensions, DPI, spine width calculation, bleed).

**Quick checks**:
- eBook cover: minimum 2560x1600 pixels, 1.6:1 aspect ratio, JPEG or TIFF, under 50MB
- Paperback cover: 300 DPI minimum, full wraparound PDF with bleed (0.125" each side)

**Verify dimensions** (Bash tool): Use `identify -format "%wx%h" cover.jpg` (ImageMagick) or `file cover.jpg` to check actual dimensions.

Direct the user to the **KDP Cover Calculator**: https://kdp.amazon.com/en_US/cover-calculator

If cover files do not exist, pause and recommend hiring a designer or using KDP Cover Creator.

### Phase 7: KDP Dashboard Submission

Walk the user through the KDP dashboard "Create a New Title" process. This phase reads listing artifacts from the config (populated by `/kdp-listing` in Phase 3).

**KDP Account Setup** (first-time publishers only): Complete account setup at https://kdp.amazon.com — tax interview, bank details, email verification. See `${CLAUDE_PLUGIN_ROOT}/docs/kdp-reference.md` for the account setup walkthrough.

**Book Details** (step through dashboard fields):

1. **Language and Title**: Select language. Enter title (max 200 chars), subtitle (optional), series name and number (if applicable), edition number (if revised edition).

2. **Author and Contributors**: Use `kdp.pen_name` from config (or `author.name` if no pen name). Add co-authors, editors, illustrators, translators as contributors.

3. **Description**: Paste the blurb from `kdp.blurb` in the config. Verify HTML formatting renders correctly in the preview. If `kdp.blurb` is empty, stop and run `/kdp-listing` first.

4. **Publishing Rights**: Ask the user:
   - "I own the copyright" (original works)
   - "This is a public domain work" (classics, expired copyright)
   - Rights holder confirmation (licensed content)

5. **Keywords**: Enter the 7 keywords from `kdp.keywords` in the config. If empty, stop and run `/kdp-listing` first.

6. **Categories**: Select the BISAC categories from `kdp.categories` in the config. If empty, stop and run `/kdp-listing` first.

7. **Age and Grade Range**: Required for children's books. Optional for YA (select 12-18). Skip for adult books.

8. **Upload Manuscript**: eBook accepts EPUB, DOCX, or PDF. Paperback accepts PDF only (PDF/X-1a:2001 recommended). Wait for conversion (30 seconds to 5 minutes).

9. **Upload Cover**: eBook: single front cover image (JPEG/TIFF). Paperback: full wraparound cover PDF or use KDP Cover Creator.

10. **KDP Previewer**: Review the book in Kindle, tablet, and phone views. Check for text overflow, broken images, TOC links, page breaks, extra blank pages, and font substitution.

**Multi-format coordination** (if publishing both eBook and paperback):
- Create the eBook first, then add paperback as a linked format (shared product page, reviews, "Look Inside")
- Metadata must match exactly across formats; cover files differ (front-only for eBook, full wrap for paperback)

### Phase 8: Pricing

Interactive decisions made during the workflow, not pre-populated from config.

**eBook royalty tiers**:
- **70% royalty**: Price must be $2.99-$9.99. Delivery cost deducted (~$0.10-$0.30 per download based on file size). Best for most books.
- **35% royalty**: Any price $0.99+. No delivery cost. Use for short works, loss leaders, or prices outside the $2.99-$9.99 range.

**KDP Select enrollment**:
- Exclusive to Amazon for 90 days (auto-renews). Cannot sell eBook on other platforms during enrollment.
- Benefits: Kindle Unlimited (readers borrow, author earns per page read), Kindle Countdown Deals, Free Book Promotions.
- Trade-off: No wide distribution (Apple Books, Kobo, Barnes & Noble). Good for debut authors building readership on Amazon. Not ideal with existing sales channels elsewhere.

**Genre-aware price recommendations**: See `${CLAUDE_PLUGIN_ROOT}/docs/kdp-reference.md` for genre-specific price ranges, paperback printing cost calculations, and royalty examples.

**Territories**: Choose "Worldwide rights" if the author holds global rights, or select specific countries.

### Phase 9: Publish

**Final review checklist**:
- [ ] All metadata correct (title, author, description, keywords, categories)
- [ ] Pricing set for all territories
- [ ] Preview reviewed and approved
- [ ] ISBN decision made (KDP-assigned or a provided ISBN)

**Submit for review**:
- Click "Publish Kindle eBook" or "Approve Proof" (paperback)
- Review timeline: 24-72 hours for eBooks, up to 5 business days for paperbacks
- Email notification when the book goes live

**For paperback**: Strongly recommend ordering a proof copy before approving ($5-$10 including shipping). Check print quality, margins, spine alignment, and color accuracy. Proofs can be ordered without publishing.

### Phase 10: Post-Publish

After KDP approves the book:

1. **Verify listing**: Search Amazon for the book by title or ASIN/ISBN. Check "Look Inside" preview, category placement, keyword discoverability, and "Buy" button.
2. **Author Central setup**: Claim the author page at https://authorcentral.amazon.com, add photo and bio from config.
3. **Goodreads linking** (optional): Claim the book, connect author profile.
4. **A+ Content** (if eligible): Add rich media to the product page.
5. **Launch promotions** (KDP Select only): Kindle Countdown Deals, Free Book Promotions.
6. **Ongoing monitoring**: Check KDP sales dashboard for sales, royalties, page reads, and rankings.

See `${CLAUDE_PLUGIN_ROOT}/docs/kdp-reference.md` for detailed post-publication steps including Author Central, A+ Content, and launch promotion strategies.

## Reference Files

For complete KDP requirements, formatting guidelines, and exemplar listings:
- **`${CLAUDE_PLUGIN_ROOT}/docs/kdp-reference.md`** -- Full KDP formatting requirements, cover templates, metadata guidelines, submission checklist, and pricing calculator reference
- **`${CLAUDE_PLUGIN_ROOT}/docs/kdp-exemplars.md`** -- Blurb examples by genre, keyword strategies, category selection tactics, author bio conventions
- **`${CLAUDE_PLUGIN_ROOT}/docs/user-config-template.md`** -- Template for `.claude/kdp.local.md` user config file

## Important Notes

- Run `/kdp-audit` or `/kdp-listing` independently for a specific step without the full pipeline.
- KDP Select is a 90-day exclusive commitment -- the eBook cannot be sold on other platforms during enrollment.
- KDP is free to use. Amazon takes a percentage via the royalty split (30% or 65% depending on tier).
- Royalties are paid monthly, ~60 days after month-end. Minimum threshold: $100 (direct deposit).
- Paperbacks are print-on-demand. No inventory, no upfront printing costs.
- ISBN is not required. KDP provides a free ASIN for eBooks and a free ISBN for paperbacks. A custom ISBN is useful for distribution beyond Amazon.
- Manuscript updates post-publication take 24-72 hours to propagate.
