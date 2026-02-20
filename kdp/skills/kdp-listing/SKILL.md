---
name: kdp-listing
description: "This skill should be used when the user asks to \"craft Amazon listing\", \"write book blurb\", \"KDP blurb\", \"book description\", \"Amazon keywords\", \"book categories\", \"KDP listing\", \"improve my blurb\", \"help with book marketing metadata\", or mentions creating or refining the marketing copy for a book on Amazon KDP. It generates blurb, keywords, categories, and author bio — the four artifacts that determine discoverability and conversion on Amazon."
---

# KDP Listing Craft

Generate the four marketing artifacts for an Amazon KDP listing: blurb (book description), keywords, BISAC categories, and author bio. This skill gathers just enough context about the book to write effective marketing copy, then saves all artifacts to the user's project config.

## Workflow

### 1. Load User Config

Read `.claude/pub-pipeline.local.md` if it exists (Read tool). Extract the `kdp` section and `author` metadata from YAML frontmatter. Key fields to look for:

- `kdp.blurb` — existing blurb draft (if any)
- `kdp.keywords` — existing keyword list
- `kdp.categories` — existing BISAC categories
- `kdp.author_bio` — existing bio
- `kdp.pen_name` — pen name (if different from `author.name`)
- `kdp.series` — series name and volume number
- `kdp.genre` — declared genre
- `author.name` — author's real name
- `author.bio` — general bio text

If the config file is missing, offer to create one from the template at `${CLAUDE_PLUGIN_ROOT}/docs/user-config-template.md`.

### 2. Analyze the Manuscript

Gather enough context to write marketing copy. This skill does not read or analyze the full manuscript — it collects what it needs to sell the book.

**Scan for existing context docs** (Glob tool):
Search for files that summarize the book's content and intent:
- `outline*`, `synopsis*`, `summary*`, `pitch*`
- `worldbuild*`, `blurb*`, `logline*`
- `README*`, `CONCEPT*`, `PREMISE*`

**Read found docs** (Read tool):
Read any matching files. These often contain the clearest distillation of what the book is about — more useful for marketing copy than the manuscript itself.

**Read the opening** (Read tool):
Find and read the first chapter or opening section to understand tone, voice, and genre register. Look for the first chapter file, or the first 100 lines of the main manuscript file. The opening establishes the voice that the blurb should echo.

**Ask the user to fill gaps**:
After reading available context, ask for anything still missing:
- Describe the book in 2-3 sentences (the "elevator pitch")
- Name the core conflict or central question
- Identify 2-3 comparable titles ("readers who liked X will like this")
- Describe the target reader (who picks this book up and why)

### 3. Draft Blurb

The blurb is the single most important marketing asset. It appears on the Amazon product page and its first two sentences appear in search results.

**Check existing blurb**: If `kdp.blurb` is non-empty in the config, present it and ask: refine the existing blurb, or start fresh?

**Consult exemplars** (Read tool):
Reference the exemplar blurb patterns for genre-appropriate structures, anti-patterns, and annotated examples.

**Structure by book type**:

*Fiction*: Hook sentence (concrete, visual, specific) -> escalation of conflict -> stakes (both personal and external) -> NO spoilers past the first act -> comp-title call to action.

*Nonfiction*: Problem the reader faces -> promise of what the book delivers -> author's authority to deliver it -> what the reader will gain or be able to do.

*Technical*: What the book covers and why it matters -> who it is for (specific audience) -> what makes it different from other books on the topic.

**Generate 2-3 variants** for the user to pick from or combine. Each variant should take a different angle on the hook or emphasize different stakes.

**Apply HTML formatting** for Amazon display:
- `<b>` for emphasis on hook lines or key phrases
- `<i>` for comp-title CTAs and book titles
- `<br>` for paragraph breaks (Amazon strips standard line breaks)

**Validate**:
- Under 4000 characters (Amazon's hard limit)
- Hook lands in the first 2 sentences (these are what Amazon shows in search results and category browse pages — everything after is behind the "Read more" fold)
- No spoilers beyond the first act or first 20% of the book
- No superlative claims ("the best," "an unforgettable," "a masterpiece")
- No external links or contact information

**Iterate** with the user until they are satisfied with the blurb. Offer specific revisions: tighten the hook, raise the stakes, adjust tone, add or remove comp titles.

### 4. Keywords (7 Slots)

Each keyword slot can hold a phrase up to 50 characters. Keywords supplement the title, subtitle, and categories — they help readers find the book through Amazon search but do not appear on the listing page.

**Consult exemplars** (Read tool):
Consult the exemplars reference doc for effective keyword patterns and TOS boundaries.

**Generate keyword candidates** using these strategies:
- Genre + subgenre phrases (e.g., "dark fantasy sword and sorcery")
- Thematic phrases readers search for (e.g., "reluctant hero quest")
- Setting and tone markers (e.g., "small town mystery")
- Comp-adjacent phrasing without naming authors (e.g., "books like grimdark fantasy")

**Rules**:
- Do NOT repeat words already in the title or subtitle (they are indexed automatically)
- Do NOT use competitor author names or book titles (TOS violation)
- Do NOT use subjective claims ("best," "award-winning")
- Do NOT use temporary claims ("new release 2026")
- Each keyword should pass the test: would a reader searching this phrase be happy to find this book?

**Present recommendations** with reasoning for each keyword. Explain what search behavior each phrase targets. Let the user adjust, swap, or reorder.

### 5. BISAC Categories (Up to 3)

Amazon uses BISAC (Book Industry Standards and Advisory Committee) codes for browse classification. Select 2 categories at setup (3 for print books). After publication, request up to 10 total via KDP support.

**Consult exemplars** (Read tool):
Consult the exemplars reference doc for example BISAC paths and the niche-vs-broad trade-off.

**Recommend specific subcategories** over broad top-level categories. Choosing "Fiction > Fantasy > Epic" places the book in three browse paths (Epic, Fantasy, Fiction), while choosing just "Fiction > Fantasy" gives only two.

**Explain the niche-vs-broad trade-off**: Narrow categories have fewer competitors but also fewer browsers. The goal is to rank in a category where the book can reach the top 20, which earns visibility on the category page.

**Present 2-3 primary recommendations** plus 2-3 post-publish expansion candidates. For each, explain why the book fits and what the competitive landscape looks like.

### 6. Author Bio

The author bio appears on the Amazon product page and the Author Central page. Maximum 2000 characters.

**Pull existing data**: Use `author.name` (or `kdp.pen_name` if set) and `author.bio` from the config as a starting point.

**Consult exemplars** (Read tool):
Consult the exemplars reference doc for genre conventions and annotated bio examples.

**Adapt for genre context**:
- *Genre fiction* (fantasy, thriller, sci-fi, romance): Third person. Lead with genre credentials and personality. Light tone is welcome.
- *Literary fiction*: Third person or first person. Lead with publications, awards, residencies. More restrained tone.
- *Technical/nonfiction*: Third person. Lead with professional credentials and expertise relevant to the book's topic.

**Draft the bio** following these principles:
- Lead with what makes the author credible for this specific book
- Include geographic grounding (readers like knowing where authors live)
- If previous publications exist, name them; if not, don't apologize for it
- One personal detail humanizes; three personal details pad
- Keep under 2000 characters

### 7. Series Metadata (If Applicable)

**Check config**: Look for `kdp.series` in the user config.

**If not set**, ask whether the book is part of a series. If yes, capture:
- Series name
- Volume number (e.g., "Book 1")
- Whether earlier volumes are already published

**If part of a series**, note that all books in the series should share at least one BISAC category to keep them grouped in browse results and strengthen the series page.

### 8. Save Artifacts

Write all outputs back to `.claude/pub-pipeline.local.md` under the `kdp` section (Edit tool). Fields to populate:

```yaml
kdp:
  blurb: |
    [full blurb with HTML formatting]
  keywords:
    - "keyword phrase 1"
    - "keyword phrase 2"
    - "keyword phrase 3"
    - "keyword phrase 4"
    - "keyword phrase 5"
    - "keyword phrase 6"
    - "keyword phrase 7"
  categories:
    - "Fiction > Fantasy > Epic"
    - "Fiction > Fantasy > Action & Adventure"
  author_bio: |
    [author bio text]
  series:
    name: "Series Name"
    volume: 1
```

Confirm the save with the user. Summarize what was written and where.

## Reference Files

For KDP listing best practices, exemplar blurbs, and metadata requirements, consult:
- **`${CLAUDE_PLUGIN_ROOT}/docs/kdp-exemplars.md`** — Blurb examples by genre, keyword strategies, category selection tactics, author bio conventions, and anti-patterns
- **`${CLAUDE_PLUGIN_ROOT}/docs/kdp-reference.md`** — Full KDP metadata requirements, content guidelines, pricing, and submission workflow

## Important Notes

- The blurb's first 2 sentences appear in Amazon search results and category pages. The hook MUST land in the opening — everything after is behind the "Read more" fold.
- Keywords supplement title, subtitle, and categories. Do not duplicate words already indexed elsewhere — that wastes a keyword slot.
- This skill crafts the listing, not the book. It reads enough manuscript context to market effectively, not to edit or critique.
- Run this skill before `/kdp-publish` — the publish workflow reads these artifacts from the config and checks for completeness.
- All artifacts are saved to `.claude/pub-pipeline.local.md` in the user's project, not to the plugin repo.
