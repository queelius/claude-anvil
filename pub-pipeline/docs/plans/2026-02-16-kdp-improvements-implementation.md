# KDP Publishing Improvements — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Bring KDP skills to architectural parity with R ecosystem — new listing craft skill, improved audit, refactored publish as orchestrator, exemplars reference doc.

**Architecture:** Three skills (kdp-listing new, kdp-audit improved, kdp-publish refactored as orchestrator) plus kdp-exemplars.md reference doc. No compiled code — all Markdown with YAML frontmatter. Skills reference `${CLAUDE_PLUGIN_ROOT}/docs/` for grounded knowledge.

**Tech Stack:** Markdown, YAML frontmatter, Claude Code plugin conventions.

**Design doc:** `docs/plans/2026-02-16-kdp-improvements-design.md`

---

### Task 1: Create `docs/kdp-exemplars.md`

This is a dependency for `kdp-listing` — the craft skill references these exemplars for genre-aware blurb templates.

**Files:**
- Create: `docs/kdp-exemplars.md`

**Step 1: Write the exemplars doc**

Model after `docs/joss-exemplars.md` structure. Content sections:

1. **Summary table** of exemplar blurbs (genre, word count, structure, what works)
2. **Fiction blurb exemplars** (3-4 genres: fantasy, thriller, literary, sci-fi) — each with full blurb text, structural annotation (hook/escalation/stakes/CTA identified), and analysis of why it works
3. **Blurb anti-patterns** — common mistakes: spoilers in blurb, passive voice, burying the hook, too much backstory, no stakes, generic adjectives
4. **Keyword strategies by genre** — concrete examples for fiction genres, TOS boundaries (no competitor names, no misleading terms, no title-word repetition)
5. **Category selection examples** — showing niche-vs-broad trade-off with ranking implications, example BISAC paths for common fiction genres
6. **Author bio examples** — fiction author bio patterns (credentials vs. personality, third vs. first person)

The blurbs should be original (not copied from real Amazon listings) but representative of strong patterns in each genre. Annotate each with inline comments identifying structural elements.

**Step 2: Validate references**

Run:
```bash
# Verify file exists and has content
wc -l docs/kdp-exemplars.md

# Verify no accidental package-specific content from other ecosystems
grep -ri "CRAN\|JOSS\|PyPI\|dfr.dist" docs/kdp-exemplars.md || echo "CLEAN"
```

**Step 3: Commit**

```bash
git add docs/kdp-exemplars.md
git commit -m "Add KDP exemplars: blurb examples, keyword strategies, category tactics"
```

---

### Task 2: Create `skills/kdp-listing/SKILL.md`

The new craft skill — generates Amazon listing artifacts (blurb, keywords, categories, author bio).

**Files:**
- Create: `skills/kdp-listing/SKILL.md`

**Step 1: Write the skill file**

YAML frontmatter must have `name: kdp-listing` and a `description` with trigger phrases. Follow the pattern from existing skills (e.g., `skills/joss-draft/SKILL.md`).

Workflow steps (numbered, with tool annotations):

1. **Load user config** (Read tool) — read `.claude/pub-pipeline.local.md`, extract `kdp` section. If missing, offer to create from `${CLAUDE_PLUGIN_ROOT}/docs/user-config-template.md`.

2. **Analyze the manuscript** — layered context gathering:
   - Scan for outline, synopsis, worldbuilding, summary, or pitch docs (Glob tool: `outline*`, `synopsis*`, `summary*`, `pitch*`, `worldbuild*`, `*.outline.*`)
   - Read any found docs (Read tool)
   - Read chapter 1 / opening section for tone and voice (Read tool)
   - Ask user to fill gaps: describe the book, themes, core conflict, comparable titles, target reader

3. **Draft blurb** — the #1 marketing asset:
   - Check if existing blurb in config (`kdp.blurb`). If yes, offer: refine existing or start fresh.
   - Consult `${CLAUDE_PLUGIN_ROOT}/docs/kdp-exemplars.md` for genre-appropriate patterns
   - Fiction structure: hook sentence → escalation of conflict → stakes → NO spoilers
   - Generate 2-3 variants for user to pick/edit
   - Apply HTML formatting for Amazon (`<b>`, `<i>`, `<br>`)
   - Validate: under 4000 chars, hook in first 2 sentences (these show in search results)
   - Iterate with user until satisfied

4. **Keywords** (7 slots):
   - Genre + subgenre phrases (e.g., "dark fantasy sword and sorcery")
   - Thematic phrases readers search for (e.g., "reluctant hero quest")
   - Do NOT repeat words already in title/subtitle
   - Do NOT use competitor author/book names (TOS violation)
   - Do NOT use subjective claims ("best", "top rated")
   - Present recommendations with reasoning, let user adjust

5. **BISAC categories** (up to 3):
   - Recommend specific subcategories over broad top-level (e.g., "Fiction > Fantasy > Epic" not just "Fiction > Fantasy")
   - Explain niche-vs-broad trade-off: niche = easier to rank, broad = more competition but more traffic
   - Note: 2 categories at setup, can request up to 10 total post-publish via KDP support

6. **Author bio**:
   - Pull from `author.name`, `author.bio` in config
   - Adapt for genre context (fiction bios differ from academic bios)
   - Suggest third-person vs. first-person based on genre convention
   - Keep under 2000 chars

7. **Series metadata** (if applicable):
   - Check `kdp.series` in config
   - If not set, ask if this is part of a series
   - Series name, volume number

8. **Save artifacts** (Edit tool):
   - Write all outputs back to `.claude/pub-pipeline.local.md` under the `kdp` section
   - Fields: `blurb`, `keywords`, `categories`, `author_bio`, `series`
   - Confirm save with user

**Reference Files section:**
```
- **`${CLAUDE_PLUGIN_ROOT}/docs/kdp-exemplars.md`** — Genre-specific blurb examples, keyword strategies, category tactics, anti-patterns
- **`${CLAUDE_PLUGIN_ROOT}/docs/kdp-reference.md`** — Full KDP metadata requirements, content guidelines
```

**Step 2: Validate skill frontmatter**

Run:
```bash
head -5 skills/kdp-listing/SKILL.md
```

Verify: `name: kdp-listing` and `description:` with trigger phrases present.

**Step 3: Validate references**

Run:
```bash
grep -oh '\${CLAUDE_PLUGIN_ROOT}/[^`"]*' skills/kdp-listing/SKILL.md | sort -u
```

Verify each referenced file exists in `docs/`.

**Step 4: Commit**

```bash
git add skills/kdp-listing/SKILL.md
git commit -m "Add kdp-listing skill: craft blurb, keywords, categories, author bio"
```

---

### Task 3: Create `commands/kdp-listing.md`

Thin command wrapper for the new skill.

**Files:**
- Create: `commands/kdp-listing.md`

**Step 1: Write the command file**

```markdown
---
description: "Craft Amazon KDP listing: blurb, keywords, categories, author bio"
---
Run the kdp-listing skill: analyze the manuscript and craft all Amazon listing artifacts (blurb, keywords, categories, author bio).
```

**Step 2: Validate command frontmatter**

Run:
```bash
head -5 commands/kdp-listing.md
```

Verify: `description:` field present.

**Step 3: Commit**

```bash
git add commands/kdp-listing.md
git commit -m "Add /kdp-listing command"
```

---

### Task 4: Improve `skills/kdp-audit/SKILL.md`

Add fiction-specific checks, EPUB validation, cover dimension checking, Kindle-specific issues.

**Files:**
- Modify: `skills/kdp-audit/SKILL.md`

**Step 1: Read current file**

Read the full file to understand current structure before editing.

**Step 2: Enhance fiction checks (section 6)**

Current fiction section (lines ~155-173) checks chapter structure, scene breaks, dialog. Improve with:

- **Front matter order check**: title page → copyright page → dedication (optional) → epigraph (optional) → TOC. Flag if out of order or missing critical elements.
- **Back matter order check**: acknowledgments → about the author → also by this author → preview of next book (optional). Flag if "About the Author" is missing entirely.
- **Scene break validation**: check for consistent markers (all `* * *` or all `---` etc.), flag mixed styles or bare blank lines used as scene breaks
- **Widow/orphan note**: remind that these need manual checking in PDF/EPUB preview

**Step 3: Add EPUB validation (new section after section 5)**

Add a new section "5b. eBook Validation" covering:
- If `epubcheck` is available (Bash tool: `which epubcheck`), run it on any `.epub` file
- Common EPUB issues to flag: broken NCX/nav, missing cover image in OPF manifest, invalid HTML entities, CSS that won't render on Kindle
- If EPUB doesn't exist but `.md` or `.docx` does, recommend conversion via Pandoc before audit

**Step 4: Enhance cover checking (section 3)**

Current cover check looks for file patterns. Add:
- Use `identify` (ImageMagick) or `file` command (Bash tool) to check actual pixel dimensions, not just file existence
- Validate aspect ratio (1.6:1 for eBook cover)
- Check file size < 50MB
- For paperback: calculate expected cover dimensions from page count and trim size, compare to actual

**Step 5: Add Kindle-specific checks (new section or extend section 2)**

Add checks for:
- Footnotes → should be endnotes for eBooks (footnotes break on Kindle)
- Tables wider than viewport (Kindle screens are narrow — tables > 3 columns are problematic)
- Complex CSS (Kindle ignores most CSS; flag if `.css` files have advanced layout rules)
- Image dimensions (flag images > 5MB individually, or > 127KB for inline images on older Kindles)

**Step 6: Validate**

Run:
```bash
head -5 skills/kdp-audit/SKILL.md
grep -oh '\${CLAUDE_PLUGIN_ROOT}/[^`"]*' skills/kdp-audit/SKILL.md | sort -u
```

**Step 7: Commit**

```bash
git add skills/kdp-audit/SKILL.md
git commit -m "Improve kdp-audit: fiction checks, EPUB validation, cover dimensions, Kindle issues"
```

---

### Task 5: Refactor `skills/kdp-publish/SKILL.md`

Transform from monolithic 10-step into orchestrator that delegates to audit + listing.

**Files:**
- Modify: `skills/kdp-publish/SKILL.md`

**Step 1: Read current file**

Read the full file.

**Step 2: Restructure into phased orchestrator**

Rewrite the workflow to:

1. **Load user config** (Read tool) — same as current step 1
2. **Assess current state** — detect manuscript files, classify type, check what already exists (cover? audit report? listing artifacts in config?)
   - Present status table to user
   - Decision matrix:
     | State | Next Phase |
     |-------|-----------|
     | No manuscript found | Cannot proceed — ask user |
     | Manuscript exists, no audit done | Phase: Audit |
     | Audit passed, no listing artifacts | Phase: Listing |
     | Listing ready, not submitted | Phase: Submission |
     | Published, not verified | Phase: Post-Publish |
3. **Phase: Audit** — recommend/delegate to `/kdp-audit`. Gate: must pass before proceeding. Offer fix cycle + re-audit.
4. **Phase: Listing** — recommend/delegate to `/kdp-listing`. Gate: blurb, keywords, categories must be saved to config.
5. **Phase: Pre-order setup** (optional) — new section:
   - Ask user if they want to set up pre-order (up to 90 days before launch)
   - Guide: upload placeholder or final manuscript, set publication date, set price
   - Pre-orders count toward Day 1 ranking
   - Can update manuscript up to 72 hours before publication date
6. **Phase: Manuscript preparation** — keep from current step 3 (format conversion: LaTeX→PDF, MD→EPUB, DOCX→PDF via Pandoc/LibreOffice; final proofread checklist)
7. **Phase: Cover preparation** — keep from current step 4 (verify specs, spine width calc, cover calculator link)
8. **Phase: KDP dashboard submission** — keep from current steps 6-8, but now reads listing artifacts from config instead of generating them inline:
   - Title, subtitle, series from config
   - Author/contributors from config
   - Description/blurb from `kdp.blurb` in config
   - Keywords from `kdp.keywords` in config
   - Categories from `kdp.categories` in config
   - Publishing rights (interactive)
   - Upload manuscript + cover
   - Preview (KDP Previewer)
9. **Phase: Pricing** — keep from current step 7, but make decisions interactive:
   - eBook vs paperback vs both (from `kdp.target` in config)
   - KDP Select enrollment decision (interactive, with trade-off explanation)
   - Royalty tier selection (interactive)
   - Price setting (interactive, genre-aware recommendations)
10. **Phase: Publish** — keep from current step 9 (submit, proof copy recommendation)
11. **Phase: Post-publish** — keep from current step 10 (verify listing, Author Central, Goodreads, A+ Content)
    - Add multi-format coordination: when both eBook and paperback published, guide linking on same product page, consistent metadata

**Step 3: Remove content that moved to kdp-listing**

Remove: blurb writing guidance (current step 6 "Step 3: Description"), keyword strategy (current step 6 "Step 5: Keywords and Categories"), detailed category selection guidance. These are now in `kdp-listing`. The publish skill reads the artifacts.

**Step 4: Update Reference Files section**

Add reference to `kdp-exemplars.md`.

**Step 5: Validate**

Run:
```bash
head -5 skills/kdp-publish/SKILL.md
grep -oh '\${CLAUDE_PLUGIN_ROOT}/[^`"]*' skills/kdp-publish/SKILL.md | sort -u
```

**Step 6: Commit**

```bash
git add skills/kdp-publish/SKILL.md
git commit -m "Refactor kdp-publish as orchestrator: delegates to audit + listing, adds pre-orders"
```

---

### Task 6: Expand user config template

Add KDP-relevant fields to the config template.

**Files:**
- Modify: `docs/user-config-template.md`

**Step 1: Read current file**

Read the full file.

**Step 2: Expand the KDP section**

Replace current `kdp:` block (lines 32-35) with:

```yaml
kdp:
  pen_name: null                       # if different from author.name
  publisher: null                      # imprint name, if any
  genre: ""                            # e.g., "epic fantasy", "thriller", "literary fiction"
  series:
    name: null                         # series name, if part of a series
    volume: null                       # volume/book number
  trim_size: "5.5x8.5"                # fiction default; "6x9" for nonfiction
  paper_type: "cream"                  # "cream" for fiction, "white" for technical/nonfiction
  target: "both"                       # "ebook", "paperback", or "both"
  categories: []                       # BISAC codes (populated by /kdp-listing)
  keywords: []                         # up to 7 phrases (populated by /kdp-listing)
  blurb: ""                            # Amazon description (populated by /kdp-listing)
  author_bio: ""                       # genre-appropriate bio (populated by /kdp-listing)
```

**Step 3: Validate**

Verify YAML is valid (no tab characters, consistent indentation):
```bash
head -50 docs/user-config-template.md
```

**Step 4: Commit**

```bash
git add docs/user-config-template.md
git commit -m "Expand KDP user config: genre, series, trim size, listing artifact fields"
```

---

### Task 7: Update router and CLAUDE.md

Update the router skill's ecosystem table and CLAUDE.md's skill→command mapping.

**Files:**
- Modify: `skills/pub-pipeline/SKILL.md` (line 45)
- Modify: `CLAUDE.md` (lines 20, 41-42)
- Modify: `.claude-plugin/plugin.json` (version bump)

**Step 1: Update router skill**

In `skills/pub-pipeline/SKILL.md`, update the "Supported Ecosystems" table (line 45) to include `kdp-listing`:

Change:
```
| **Books (Amazon KDP)** | `kdp-audit`, `kdp-publish` | `/kdp-audit`, `/kdp-publish` |
```
To:
```
| **Books (Amazon KDP)** | `kdp-audit`, `kdp-listing`, `kdp-publish` | `/kdp-audit`, `/kdp-listing`, `/kdp-publish` |
```

**Step 2: Update CLAUDE.md**

In `CLAUDE.md`:
- Update plugin structure comment (line 20): `skills/` count from "8 skill files" to "9 skill files", `commands/` count from "7 slash commands" to "8 slash commands"
- Add row to skill→command mapping table (after line 42):
  ```
  | `commands/kdp-listing.md` | `skills/kdp-listing/` | KDP |
  ```

**Step 3: Bump plugin version**

In `.claude-plugin/plugin.json`, bump version from `"0.2.0"` to `"0.3.0"` (new skill = minor version bump).

**Step 4: Validate everything**

Run the full validation suite from the CLAUDE.md:
```bash
# All skill frontmatter has name and description
for f in skills/*/SKILL.md; do echo "=== $f ===" && head -5 "$f" && echo; done

# All command frontmatter has description
for f in commands/*.md; do echo "=== $f ===" && head -5 "$f" && echo; done

# All ${CLAUDE_PLUGIN_ROOT} references point to existing files
grep -roh '\${CLAUDE_PLUGIN_ROOT}/[^`"]*' skills/ | sort -u

# No stale package-specific content in exemplars
grep -ri "dfr.dist" skills/ docs/ || echo "CLEAN"
```

**Step 5: Commit**

```bash
git add skills/pub-pipeline/SKILL.md CLAUDE.md .claude-plugin/plugin.json
git commit -m "Update router, CLAUDE.md, and bump version to 0.3.0 for kdp-listing"
```

---

### Task 8: Final validation and summary commit

**Step 1: Run full validation**

```bash
# Count files
echo "Skills:" && ls skills/*/SKILL.md | wc -l
echo "Commands:" && ls commands/*.md | wc -l
echo "Docs:" && ls docs/*.md | wc -l

# Verify all CLAUDE_PLUGIN_ROOT references resolve
for ref in $(grep -roh '\${CLAUDE_PLUGIN_ROOT}/[^`"]*' skills/ | sort -u); do
  path="${ref/\$\{CLAUDE_PLUGIN_ROOT\}/\.}"
  if [ -f "$path" ]; then
    echo "OK: $ref"
  else
    echo "MISSING: $ref -> $path"
  fi
done
```

**Step 2: Verify git log**

```bash
git log --oneline -10
```

Verify all 7 commits from Tasks 1-7 are present.

**Step 3: Review diff from main**

```bash
git diff main --stat
```

Verify: new files created, existing files modified, no unexpected changes.
