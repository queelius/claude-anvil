# Papermill State File Schema

Canonical schema for `.papermill/state.md`, the per-paper state file that all papermill skills read and write. Use this as the single source of truth when initializing, refreshing, or validating state.

The state file has two parts:

1. **YAML frontmatter**: structured project state (below)
2. **Markdown body**: free-form session notes, including a `## Notes` section and optional `## Related Work and Software`

## Full Template

When creating a new state file, use this template and populate the placeholder values from the context gathered during init:

```markdown
---
title: "<title>"
stage: <stage>
format: <format>
authors:
  - name: "<name>"
    email: "<email>"
    orcid: "<orcid or empty string>"

thesis:
  claim: ""
  novelty: ""
  refined: null

prior_art:
  last_survey: null
  key_references: []
  gaps: ""

experiments: []

venue:
  target: null
  candidates: []

review_history: []

related_papers: []
---

## Notes

Initialized by papermill on <YYYY-MM-DD>.
```

If the user described related papers or software during init, also append a `## Related Work and Software` section to the body with a natural-language description.

## Field Constraints

- **`stage`** must be one of: `idea`, `thesis`, `literature`, `outlining`, `drafting`, `review`, `submission`
- **`format`** must be one of: `latex`, `markdown`, `rmarkdown`
- **`orcid`** should be the bare identifier (e.g., `0000-0002-1234-5678`), not a URL
- **`thesis.refined`** starts as `null` and is set to `true` by the thesis skill after Socratic refinement
- **`prior_art.last_survey`** is a date string (`YYYY-MM-DD`) or `null`
- Leave empty fields as empty strings `""`, not `null`, unless the schema specifies `null`

## List Field Structures

These fields start empty at init and are populated by their respective skills over the lifetime of the paper.

### `experiments[]`

Populated by the experiment and simulation skills.

```yaml
experiments:
  - name: "descriptive-name"
    type: "simulation | benchmark | case-study | ablation"
    hypothesis: "Expected outcome in one sentence"
    status: "planned | running | completed | failed"
    script: "path/to/script.R"
    last_run: null  # YYYY-MM-DD when last executed
```

### `review_history[]`

Populated by the review skill. One entry per review pass.

```yaml
review_history:
  - date: "YYYY-MM-DD"
    type: "self-review"
    findings_major: 0
    findings_minor: 0
    recommendation: "ready | minor-revision | major-revision | not-ready"
    notes: "Brief summary of key findings"
```

### `venue.candidates[]`

Populated by the venue skill.

```yaml
venue:
  candidates:
    - name: "Journal or Conference Name"
      fit: "high | good | moderate"
      deadline: "YYYY-MM-DD or rolling"
```

### `related_papers[]`

Populated by init (from user input) or refresh. Captures links to other projects in the user's research program.

```yaml
related_papers:
  - path: "~/github/path/to/related-project"
    rel: "extends | extended-by | implements | implemented-by | companion | series | merged-into | supersedes"
    label: "One-line description of the relationship"
```

**`rel` vocabulary**:

| Value | Meaning |
|---|---|
| `extends` / `extended-by` | Builds on or is built upon |
| `implements` / `implemented-by` | Theory paper ↔ software package |
| `companion` | Different angle on the same research |
| `series` | Part of a numbered series (e.g. Part II of...) |
| `merged-into` | Absorbed into another paper |
| `supersedes` | Replaces a previous version |

**`path`** should be absolute or `~/`-relative.

## Session Notes

The markdown body below the frontmatter is free-form. Conventions:

- **`## Notes`**: required section; init writes the first entry here ("Initialized by papermill on YYYY-MM-DD").
- **`## Related Work and Software`** (optional): captures the natural-language context the user provided about related projects, preserved verbatim for Claude to read in future sessions.
- **Timestamped entries**: skills (init refresh, review, etc.) may append dated bullets, e.g. `- 2026-04-21 (init refresh): Added missing thesis block.`

## Migration From Legacy `.papermill.md`

Earlier versions of papermill kept state in a top-level `.papermill.md` file. The init skill auto-migrates these to `.papermill/state.md`:

1. `mkdir -p .papermill/reviews` (create the new directory structure)
2. Read `.papermill.md`
3. Write the content unchanged to `.papermill/state.md`
4. Delete `.papermill.md`

No schema changes are needed; the file content is preserved as-is. Schema gaps are filled in the separate refresh pass.
