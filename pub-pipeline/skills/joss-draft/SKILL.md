---
name: joss-draft
description: "This skill should be used when the user asks to \"draft a JOSS paper\", \"write paper.md\", \"create JOSS paper\", \"write JOSS submission\", \"draft paper.md for JOSS\", \"convert paper to JOSS format\", or mentions writing a JOSS software paper. It discovers existing manuscripts and package content, then drafts a complete paper.md and paper.bib following JOSS format requirements."
---

# JOSS Paper Drafting

Analyze an R/Python package and draft a complete `paper.md` and `paper.bib` for JOSS submission. The paper follows current JOSS format requirements (2025+) with all required sections.

## Philosophy

Research packages exist in messy, real-world contexts — companion papers, existing LaTeX manuscripts, deep vignettes, `.papermill.md` state files, ecosystem documentation. Use your intelligence to discover and adapt what already exists rather than generating from scratch. Good prose the author has already written is almost always better than template-generated text.

The template structure below is guidance, not a straitjacket. Use it when starting from nothing; reshape existing content when you find it.

## Workflow

### 1. Discover Existing Content

Before generating anything, look for existing paper-like content that can inform or seed the JOSS paper. This is the most important step — skipping it means ignoring potentially excellent prose the author has already written.

**Search for existing manuscripts** (Glob/Read tools):
- `paper/` directory — LaTeX (.tex), Markdown (.md), Rmd (.Rmd) manuscripts
- `inst/paper/`, `manuscript/`, `doc/` — alternative locations
- `.papermill.md` — papermill state file with thesis, venue, outline, and strategic context
- `ECOSYSTEM.md`, `RESEARCH-NOTES.md` — ecosystem context and strategic notes

**Evaluate what you find:**
- Is there existing prose that describes the package well? Read it carefully.
- What is its quality? Could sections be adapted directly for JOSS?
- What is its scope? A 400-line software paper is mostly reusable; a 2000-line theory paper needs selective extraction.
- Does it have a bibliography? Import relevant entries rather than rebuilding from scratch.
- Does it reference companion papers or a broader research program? The JOSS paper should acknowledge this context.

**Key principle:** If the author has a LaTeX paper that already describes the package's purpose, design, and API — reshape it into JOSS format rather than starting from a blank template. Preserve the author's voice, terminology, and framing. Only add what's missing (e.g., State of the Field, AI Disclosure) and trim what's too long.

### 2. Analyze the Package

Thoroughly understand what the package does. Skip files you already read in Step 1.

**Read core files** (Read tool):
- `DESCRIPTION` / `pyproject.toml` — title, description, author info, dependencies
- `README.md` or `README.Rmd` — overview, examples, installation
- `CLAUDE.md` — architecture and design decisions (if present)
- `NEWS.md` / `CHANGELOG.md` — development history and features
- `CITATION.cff` or `inst/CITATION` — existing citation metadata

**Understand the API** (Glob/Grep/Read tools):
- List all exported functions from `NAMESPACE` (R) or public API (Python)
- Read key source files to understand architecture
- Identify the core abstraction (e.g., the main class/object)
- Note the design pattern (closure-returning, S3/S4/R6, functional, etc.)

**Check vignettes/tutorials** (Glob/Read tools):
- Read all vignettes or tutorial notebooks for use cases and examples
- Identify the strongest example for the paper

**Identify the research context**:
- What domain does this serve? (survival analysis, Bayesian stats, etc.)
- What problem does it solve that existing tools don't?
- Who is the target audience? (researchers, practitioners, students)
- Is this package part of a larger research program with companion papers?
- Check `related_work` in the user config for declared companion papers, preprints, and sibling packages. If a companion paper exists at a local path, read it for context.

### 3. Get Author Metadata

Gather author name, ORCID, affiliation, and email. Check these sources before prompting the user:
- `CITATION.cff` or `inst/CITATION`
- `DESCRIPTION` (R) or `pyproject.toml` (Python)
- `.papermill.md` frontmatter
- `.claude/pub-pipeline.local.md` (user config for this plugin)
- Existing manuscript frontmatter
- `deets` CLI (if available — a personal metadata store)

The information is usually already in the repo somewhere. Only ask the user for what you can't find.

### 4. Identify Competing Packages

Search for competing/related packages. Name specific packages and explain how this one differs:
- What does each competitor do?
- What gap does this package fill?
- Why build new rather than contribute to existing?

**How to find competitors** (WebSearch/Read/Grep tools):
- Search CRAN Task Views / PyPI classifiers relevant to the package's domain
- Read the package's dependency files for related packages
- Search the README and vignettes for mentions of other packages (Grep tool)
- Check the user config's `r.competitors` field for pre-identified competitors
- Search the web for "[domain] R/Python package" (WebSearch tool)

This is critical — JOSS reviewers specifically check the "State of the Field" section for this.

### 5. Draft paper.md

**If existing paper content was found in Step 1**, use it as the primary source:
- Read the existing manuscript carefully and reshape it into JOSS structure
- Preserve the author's voice, terminology, and framing
- Extract and condense prose that maps to JOSS sections
- Add any missing JOSS-required sections (State of the Field, AI Disclosure, Research Impact)
- Trim theoretical depth that belongs in vignettes or companion papers — but use judgment about what's worth keeping
- Import bibliography entries from any existing `.bib` files
- If the existing content is close to the right length and covers the right topics, the transformation may be mostly structural (LaTeX -> Markdown, add YAML frontmatter, reorganize sections)

**If no existing paper content exists**, draft from the package analysis in Steps 2-4.

Either way, populate the YAML frontmatter from the user config (`.claude/pub-pipeline.local.md`, if it exists). Use `r.domain` and `r.audience` to inform the Statement of Need. Use `r.competitors` to seed State of the Field. Use `ai_usage` fields for the AI Usage Disclosure section. Use `related_work` entries to identify companion papers (cite them), preprints (reference the DOI), and sibling packages (mention in State of the Field or Software Design).

The paper should follow this structure:

```markdown
---
title: 'packagename: Short description of what it does'
tags:
  - R
  - [domain tag 1]
  - [domain tag 2]
  - [method tag]
authors:
  - name: First M. Last
    orcid: 0000-0000-0000-0000
    affiliation: 1
affiliations:
  - name: Department, University
    index: 1
date: "DD Month YYYY"
bibliography: paper.bib
---

# Summary

[2-3 paragraphs: What the package does, at a high level, for a
non-specialist audience. Include the core abstraction and key
capabilities. Mention the language and any notable design choices.]

# Statement of Need

[1-2 paragraphs: What research problem this solves. Who needs it
and why. What is the gap in existing tools. Be specific about the
target audience — researchers in X, practitioners doing Y.]

# State of the Field

[1-2 paragraphs: Name specific competing packages. For each,
state what it does and what it lacks. Explain why building this
package was justified. Use citations for each package mentioned.]

# Software Design

[1-2 paragraphs: Key architectural decisions. The core abstraction
(e.g., closure-returning pattern, S3 class hierarchy). Trade-offs
made (e.g., flexibility vs performance, generality vs specificity).
Integration with other packages.]

# Research Impact Statement

[1 paragraph: Evidence of use. Published analyses, ongoing projects,
adoption by other packages. If the package is new, describe the
near-term credible impact based on the research community it serves.]

# AI Usage Disclosure

[1 paragraph: Transparent disclosure. If AI tools were used in
development, state which tools, where they were applied, and confirm
human oversight of all design decisions. If no AI was used, state
that explicitly.]

# Acknowledgements

[Funding sources, contributors, institutional support.]

# References
```

**Writing guidelines**:
- Target 750-1750 words (aim for ~1000)
- Write tight prose — every sentence earns its place
- No hyperbole or unjustified superlatives
- Use active voice where it improves clarity
- Match the author's existing voice from README/vignettes/existing paper
- Include 1-2 inline code examples if they clarify the design
- Use `[@key]` for parenthetical citations, `@key` for in-text

### 6. Draft paper.bib

Create `paper.bib` with BibTeX entries for:
- The R language itself (`@r_core`) or Python
- All packages named in State of the Field
- Key methodology references
- Any references from the package's existing `CITATION`, vignettes, or existing bibliography
- Companion papers in the research program (if applicable)

If an existing `.bib` file was found in Step 1, import relevant entries rather than rewriting them.

Use standard BibTeX format:
```bibtex
@Manual{r_core,
  title = {R: A Language and Environment for Statistical Computing},
  author = {{R Core Team}},
  organization = {R Foundation for Statistical Computing},
  address = {Vienna, Austria},
  year = {YYYY},  % use the current year
  url = {https://www.R-project.org/},
}

@Article{package_key,
  title = {Package Title},
  author = {Author Name},
  journal = {Journal Name},
  year = {2023},
  doi = {10.xxxx/xxxxx},
}
```

### 7. Validate the Draft

After writing, check:
- Word count is 750-1750
- All `@key` citations have matching BibTeX entries
- All required sections present (Summary, Statement of Need, State of the Field, Software Design, Research Impact, AI Disclosure)
- YAML frontmatter has all required fields
- Date format is correct (`%e %B %Y`)
- Referenced figure files exist (if any)

### 8. Place Files

Place `paper.md` and `paper.bib` at the package root or in a `paper/` subdirectory. If there's an existing `paper/` directory with other content (e.g., a LaTeX manuscript), place alongside it and note the relationship.

## Reference Files

For JOSS format specifications and exemplar papers, consult:
- **`${CLAUDE_PLUGIN_ROOT}/docs/joss-reference.md`** — Complete JOSS paper format spec, YAML fields, citation syntax, math/figure syntax
- **`${CLAUDE_PLUGIN_ROOT}/docs/joss-exemplars.md`** — Real JOSS R package papers with full content, structural analysis, patterns and anti-patterns

## Delegation

For substantial prose writing, consider delegating to the `academic-paper-writer` agent (if available) with format set to "Markdown (JOSS)". Provide the agent with the package analysis and any existing content from Steps 1-4 as context. Otherwise, draft inline.

For critical review of the draft, use the `academic-paper-reviewer` agent (if available) with JOSS format. Otherwise, self-review against the checklist in `joss-audit`.

## Important Notes

- The "State of the Field" section is where most JOSS reviews focus. Name specific packages.
- JOSS papers are short — resist the urge to write a full methods paper. Save that for JSS or a companion paper.
- Code examples in the paper should be minimal and illustrative, not comprehensive.
- ORCID is required for all authors. Help users register at https://orcid.org if needed.
- The paper must be stored in the same git repository as the software.
- If the package has companion theory papers at traditional venues, cite them and clarify the relationship (JOSS = software contribution, companion = theoretical contribution).
