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

Generate or verify cover files for the book. See `${CLAUDE_PLUGIN_ROOT}/docs/kdp-reference.md` for full cover requirements (dimensions, DPI, spine width calculation, bleed).

**Fallback note**: This phase uses the `kdp-cover` MCP server for AI cover generation. If the MCP tools are not available (Node.js not installed, `OPENAI_API_KEY` not set, or the server is not configured), fall back to manual cover preparation: verify existing cover dimensions with `identify` or `file` (Bash tool), direct the user to the KDP Cover Calculator at https://kdp.amazon.com/en_US/cover-calculator, and recommend hiring a designer or using KDP Cover Creator if no cover exists.

1. **Check for existing cover** (Read tool, Glob tool): Look for an existing cover path in `kdp.cover.front` from the config. If not set, glob for `cover*`, `front-cover*`, and `*-cover.*` files in the project. If a cover file exists, show it to the user (Read tool on the image file) and ask whether to use it or generate a new one.

2. **Gather art direction**: If no cover exists (or user wants a new one), ask the user for art direction preferences: visual style, mood, color palette, imagery. If the user has no strong preference, suggest a direction based on the genre from `kdp.genre` and the book title. Check `kdp.cover.art_direction` in the config for any previously saved preferences.

3. **Inform about cost**: Tell the user that each cover generation costs approximately $0.04-$0.08 via OpenAI image generation. Multiple iterations are normal (2-4 attempts to get a cover the user likes).

4. **Generate front cover** (kdp_generate_cover MCP tool): Call `kdp_generate_cover` with:
   - `title`: from the book title
   - `subtitle`: if applicable
   - `author_name`: from `kdp.pen_name` or `author.name`
   - `genre`: from `kdp.genre`
   - `art_direction`: from the user's preferences or suggested direction
   - `width`: 1600 (default)
   - `height`: 2560 (default)

5. **Show the cover** (Read tool): Read the generated image file to display it inline. Ask the user to verify:
   - Is the title text spelled correctly?
   - Does the overall look match the genre and tone?
   - Are the colors and composition appealing?

6. **Iterate if needed**: If the user wants changes ("try a different style", "make it darker", "more minimalist"), adjust the `art_direction` and call `kdp_generate_cover` again. Repeat steps 5-6 until the user approves.

7. **Save approved cover** (Edit tool): Save the approved front cover file path to `.claude/kdp.local.md` under `kdp.cover.front`. Also save the art direction used under `kdp.cover.art_direction` for future reference.

8. **Full-wrap cover for paperback** (if `kdp.target` is "paperback" or "both"):

   a. **Calculate dimensions** (kdp_cover_specs MCP tool): Call `kdp_cover_specs` with `page_count` (from manuscript), `trim_size` (from `kdp.trim_size`), and `paper_type` (from `kdp.paper_type`). Display the spine width, total dimensions, and zone layout to the user.

   b. **Generate full wrap** (kdp_generate_full_wrap MCP tool): Call `kdp_generate_full_wrap` with:
      - `front_cover_path`: the approved front cover
      - `title` and `author_name`: for spine text
      - `blurb`: from `kdp.blurb` (for back cover text)
      - `page_count`, `trim_size`, `paper_type`: from config
      - `isbn`: if the user has one
      - `back_color`: from `kdp.cover.color_scheme`, or let the tool auto-extract from the front cover

   c. **Show the full-wrap preview** (Read tool): Read the preview PNG file to display the complete wraparound cover. Ask the user to verify spine text, back cover blurb readability, and overall composition.

   d. **Save full-wrap path** (Edit tool): Save the full-wrap PDF path to `.claude/kdp.local.md` under `kdp.cover.full_wrap`.

### Phase 7: KDP Dashboard Submission

Automate the KDP dashboard submission using browser automation. This phase reads listing artifacts from the config (populated by `/kdp-listing` in Phase 3) and fills in the dashboard forms.

**KDP Account Setup** (first-time publishers only): Complete account setup at https://kdp.amazon.com (tax interview, bank details, email verification). See `${CLAUDE_PLUGIN_ROOT}/docs/kdp-reference.md` for the account setup walkthrough.

**Pre-submission check** (Read tool): Re-read `.claude/kdp.local.md` and verify all required fields are populated: `kdp.blurb`, `kdp.keywords` (7 entries), `kdp.categories`, `kdp.cover.front`, and `kdp.manuscript.path`. If any are missing, stop and direct the user to the appropriate earlier phase.

**Dashboard automation**:

1. **Open KDP** (Playwright MCP: browser_navigate): Navigate to `https://kdp.amazon.com`.

2. **Check login state** (Playwright MCP: browser_snapshot): Take a snapshot of the page. If the user is not logged in, tell them to log in using the browser window that opened. Wait for the dashboard to become visible (Playwright MCP: browser_wait_for).

3. **Navigate to the correct page** (Playwright MCP: browser_snapshot, browser_click):
   - For a new title: find and click the "Create" button or equivalent, then select the format (Kindle eBook or Paperback). If publishing both, start with eBook.
   - For an update to an existing title: if `kdp.asin` or `kdp.asin_paperback` is set in the config, navigate to that title's detail page. Otherwise, search the bookshelf by title name and select it.

4. **Fill Book Details** (Playwright MCP: browser_snapshot, browser_fill_form, browser_click): On each form page, take a snapshot first to understand the current layout, then fill fields adaptively:
   - Language: select the appropriate language
   - Title, subtitle: from the book metadata
   - Series name and volume number: from `kdp.series` if set
   - Author/pen name: from `kdp.pen_name` or `author.name`
   - Contributors: add any co-authors, editors, illustrators
   - Description: paste `kdp.blurb` from config
   - Publishing rights: select "I own the copyright" (confirm with user if uncertain)
   - Keywords: fill the 7 keyword slots from `kdp.keywords`
   - Categories: select the BISAC categories from `kdp.categories`
   - Age/grade range: skip for adult books, fill for children's/YA

5. **Upload manuscript** (Playwright MCP: browser_snapshot, browser_file_upload): Upload the manuscript file from `kdp.manuscript.path`. Take a snapshot to locate the upload control, then use file upload. Wait for the upload and conversion to complete (this may take 30 seconds to 5 minutes).

6. **Upload cover** (Playwright MCP: browser_snapshot, browser_file_upload): Upload the cover file:
   - eBook: front cover image from `kdp.cover.front`
   - Paperback: full-wrap PDF from `kdp.cover.full_wrap`, or front cover if no full-wrap exists

7. **Navigate to preview/review** (Playwright MCP: browser_snapshot, browser_click): Find and click the button to proceed to the preview or review page. Take a snapshot to confirm the page loaded.

8. **Stop and hand off to user**: Tell the user: "Everything is filled in. Review the details in the browser and click publish when you are ready." Do NOT click the publish button. The user must make this final decision.

9. **Capture ASIN after publish** (Playwright MCP: browser_snapshot): After the user confirms they have published, take a snapshot of the bookshelf page to look for the newly assigned ASIN. If the ASIN is not yet visible (KDP review takes 24-72 hours), note this and tell the user to run `/kdp-publish` again later to capture it.

10. **Save ASIN** (Edit tool): If an ASIN was captured, save it to `.claude/kdp.local.md` under `kdp.asin` (for eBook) or `kdp.asin_paperback` (for paperback).

**Multi-format coordination** (if publishing both eBook and paperback):
- Create the eBook first, then add paperback as a linked format (shared product page, reviews, "Look Inside")
- Metadata must match exactly across formats; cover files differ (front-only for eBook, full wrap for paperback)
- After the eBook is submitted, repeat steps 3-10 for the paperback format

**Important**: These instructions describe goals, not exact selectors. The KDP dashboard layout may change. Use browser_snapshot to read each page and determine the correct elements to interact with. Adapt to whatever layout is present.

### Phase 8: Pricing

Semi-automated pricing setup. Present options conversationally, then fill the pricing form via browser automation.

1. **Present pricing options** (Read tool): Load genre-specific price recommendations from `${CLAUDE_PLUGIN_ROOT}/docs/kdp-reference.md`. Present the user with a conversational summary:

   - **Royalty tier choice** (eBook only):
     - 70% royalty: price must be $2.99-$9.99, delivery cost deducted (~$0.10-$0.30 based on file size). Best for most books.
     - 35% royalty: any price $0.99+, no delivery cost. Use for short works, loss leaders, or prices outside the 70% range.

   - **KDP Select enrollment**:
     - Exclusive to Amazon for 90 days (auto-renews). Cannot sell eBook on other platforms during enrollment.
     - Benefits: Kindle Unlimited page reads, Kindle Countdown Deals, Free Book Promotions.
     - Trade-off: no wide distribution (Apple Books, Kobo, Barnes & Noble). Good for debut authors building readership on Amazon. Not ideal if the author has existing sales channels elsewhere.

   - **Suggested price**: Based on genre from `kdp.genre`, manuscript type, and the pricing tables in the reference doc, suggest a specific price point. For paperback, note that the price must cover printing costs plus Amazon's share.

   - **Territories**: recommend "Worldwide rights" if the author holds global rights, or ask about specific country restrictions.

2. **Confirm with user**: Ask the user to decide on: price, royalty tier (eBook), KDP Select enrollment (yes/no), and territories. Wait for confirmation before proceeding.

3. **Fill pricing form** (Playwright MCP: browser_snapshot, browser_fill_form, browser_click): Once the user has decided:
   - Take a snapshot to understand the pricing page layout
   - Select the royalty tier (eBook)
   - Enter the price in the appropriate currency fields
   - Select or deselect KDP Select enrollment
   - Set territory rights
   - For paperback: enter the list price (verify it meets the minimum shown on the page)

4. **Verify pricing summary** (Playwright MCP: browser_snapshot): Take a snapshot of the pricing summary. Show the user the estimated royalty per sale and confirm everything looks correct before proceeding to Phase 9.

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
