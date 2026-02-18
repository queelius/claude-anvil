# KDP Publishing Improvements — Design Document

**Date**: 2026-02-16
**Status**: Approved
**Scope**: Bring KDP skills to architectural parity with the R ecosystem

## Problem

The KDP (Kindle Direct Publishing) skills are functional but structurally immature compared to the R ecosystem skills. The R side has a pipeline orchestrator (`r-pub-pipeline`), a craft skill that generates artifacts (`joss-draft`), and grounded exemplars (`joss-exemplars.md`). The KDP side has two disconnected skills (`kdp-audit` and `kdp-publish`) with no orchestration, no artifact-generating skill, and no exemplars.

The user is about to publish fiction through KDP and wants the skills ready before that session.

## Division of Labor

Pub-pipeline never touches manuscript content. It handles everything *around* the book: formatting validation, Amazon listing optimization, submission mechanics, and post-publish setup. Book writing is a separate workflow.

## Design

### Skill Changes (3 skills)

#### 1. `kdp-listing` (NEW)

Craft Amazon listing artifacts. This is the main value-add — the "easy wins" for discoverability and appeal.

**Workflow**:

1. **Load user config** — read `.claude/pub-pipeline.local.md` for existing KDP metadata
2. **Analyze the manuscript** — layered approach:
   - Scan for outline, synopsis, worldbuilding, or summary docs (Glob tool)
   - Read chapter 1 for tone/voice (Read tool)
   - Ask user to describe the book, themes, hooks, and comps to fill gaps
3. **Draft blurb** (the #1 marketing asset)
   - If existing blurb found in config → offer to refine it
   - If no blurb → generate fresh
   - Genre-aware structure from `kdp-exemplars.md`
   - Fiction pattern: hook sentence → escalation → stakes → NO spoilers
   - Present 2-3 variants for user to pick/edit
   - HTML formatting for Amazon (`<b>`, `<i>`, `<br>`)
   - Validate: under 4000 chars, strong opening hook
4. **Keywords** (7 slots)
   - Genre + subgenre phrases
   - Thematic phrases readers search for
   - Present recommendations with reasoning
   - Avoid TOS violations (no competitor names, no misleading terms)
5. **BISAC categories** (up to 3)
   - Recommend specific subcategories over broad ones
   - Explain competition/ranking trade-off (niche = easier to rank)
   - Note: can request additional categories post-publish via KDP support
6. **Author bio**
   - Pull from user config, adapt for genre context
   - Fiction bios differ from technical bios
7. **Series metadata** (if applicable)
   - Series name, volume number
8. **Save artifacts** — write all outputs to `.claude/pub-pipeline.local.md` under `kdp` section

**Command**: `commands/kdp-listing.md`

#### 2. `kdp-audit` (IMPROVED)

Existing skill with these additions:

- **Stronger fiction checks**:
  - Front matter order: title page → copyright → dedication → TOC
  - Back matter order: acknowledgments → about author → also-by → preview chapter
  - Scene break consistency (standardized markers, not just blank lines)
  - Dialog formatting consistency
- **EPUB validation**: integrate `epubcheck` when available, flag common EPUB issues (broken NCX, missing cover image ref)
- **Cover dimension checking**: use `identify` (ImageMagick) or `file` command to check actual pixel dimensions, not just file existence
- **Kindle-specific issues**: footnotes should be endnotes, tables wider than screen, complex CSS that breaks on Kindle

#### 3. `kdp-publish` (REFACTORED — becomes orchestrator)

Refactored from monolithic 10-step workflow to an orchestrating skill that delegates to audit and listing.

**New workflow**:

1. **Load user config**
2. **Assess current state** — detect manuscript, classify type, check what exists (cover, blurb, config)
3. **Phase: Audit** — delegate to `/kdp-audit`. Gate: must pass before proceeding. Offer fix cycle.
4. **Phase: Listing** — delegate to `/kdp-listing`. Gate: all listing artifacts must be saved.
5. **Phase: Pre-order setup** (optional path)
   - Guide pre-order setup on KDP (up to 90 days before launch)
   - Upload placeholder or final manuscript
   - Set pre-order price, publication date
   - Pre-orders all count toward Day 1 ranking
6. **Phase: Manuscript preparation** — format conversion (LaTeX→PDF, MD→EPUB, DOCX→PDF), final proofread checklist
7. **Phase: Cover preparation** — verify specs, spine width calculation, cover calculator link
8. **Phase: KDP dashboard submission** — step-by-step walkthrough (title, author, description from listing artifacts, rights, upload, preview)
9. **Phase: Pricing** — interactive prompts for royalty tier, KDP Select decision, pricing strategy by genre
10. **Phase: Publish** — submit for review, proof copy recommendation for paperback
11. **Phase: Post-publish** — verify listing, Author Central, Goodreads, A+ Content, launch promotions

**Removed from kdp-publish** (moved to kdp-listing): blurb writing guidance, keyword strategy, category selection

**Multi-format coordination**: when publishing both eBook and paperback, guide linking them on the same product page, consistent metadata, coordinated pricing.

### New Reference Doc: `docs/kdp-exemplars.md`

Structured like `joss-exemplars.md` but for Amazon listings:

- **Blurb examples by genre** (3-4 genres): full blurbs with structural annotation
  - Hook sentence identified
  - Escalation/stakes highlighted
  - What makes it work / what to avoid
- **Anti-patterns**: common blurb mistakes (spoilers, passive voice, too much backstory, no stakes, burying the hook)
- **Keyword strategies by genre**: concrete examples, TOS boundaries
- **Category selection examples**: showing niche-vs-broad trade-off with ranking implications

### User Config Expansion

Current:
```yaml
kdp:
  pen_name: null
  publisher: null
  categories: []
```

Expanded:
```yaml
kdp:
  pen_name: null
  publisher: null
  genre: ""                    # e.g., "epic fantasy", "thriller", "literary fiction"
  series:
    name: null
    volume: null
  trim_size: "5.5x8.5"        # fiction default
  paper_type: "cream"          # cream for fiction, white for technical
  target: "both"               # "ebook", "paperback", or "both"
  categories: []               # BISAC codes (populated by kdp-listing)
  keywords: []                 # up to 7 (populated by kdp-listing)
  blurb: ""                    # draft blurb (populated by kdp-listing)
  author_bio: ""               # genre-appropriate bio (populated by kdp-listing)
```

Publishing strategy decisions (ISBN, KDP Select, pricing tier) are NOT config — they are interactive prompts during the `kdp-publish` workflow.

### New Command

`commands/kdp-listing.md`:
```yaml
---
description: "Craft Amazon KDP listing: blurb, keywords, categories, author bio"
---
Run the kdp-listing skill: analyze the manuscript and craft all Amazon listing artifacts.
```

## Key Design Decisions

1. **No separate orchestrator skill** — `kdp-publish` delegates to `/kdp-audit` and `/kdp-listing` as sub-steps, avoiding an extra skill file
2. **Pre-order workflow included** — optional path in `kdp-publish`, important for fiction launch strategy
3. **Blurb is iterative** — `kdp-listing` detects existing blurb and offers to refine, or generates fresh
4. **Manuscript analysis is layered** — outline/synopsis docs → chapter 1 → ask user. Let Claude be smart about sourcing context.
5. **Config = identity + book metadata** — publishing strategy decisions are interactive workflow prompts
6. **Division of labor** — pub-pipeline handles everything around the book, never the book content itself
