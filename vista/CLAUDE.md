# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

Vista is a **dual-mode application** packaged as one Python project:

1. A **standalone CLI** (`vista`) that builds a bulk catalog of research
   directions by mining the Future Work / Limitations / Discussion / Conclusion
   sections of highly-cited papers from OpenAlex.
2. A **Claude Code plugin / MCP server** (`vista-mcp`) that exposes the same
   pipeline as on-demand tools so the in-conversation Claude can fetch raw
   section text and synthesize directions inline.

Both modes share one SQLite store, one `vista` package, and one config. They
diverge only at the entry points (`vista.cli:app` vs `vista.mcp_server:main`).

The plugin manifest (`.claude-plugin/plugin.json`) and MCP registration
(`.mcp.json`) ship in the repo. `.mcp.json` resolves `${CLAUDE_PLUGIN_ROOT}` to
this directory at runtime so `uv run --project ... vista-mcp` finds the package.

## Common commands

```bash
# Install (editable, with the API extra for the unattended analyzer path)
uv venv && uv pip install -e '.[api]'

# Run the test suite (pytest is NOT a declared dep; use --with)
uv run --with pytest python -m pytest tests/ -q

# Run a single test file or test
uv run --with pytest python -m pytest tests/test_extract.py -q
uv run --with pytest python -m pytest tests/test_extract.py::test_dedup_keeps_longer

# CLI: end-to-end build of the catalog (idempotent; resumes per-stage)
vista pipeline --fields ml,ai,stats,ransomware --per-field 25
vista pipeline --skip-analyze    # discover/fetch/extract/render only (no API key needed)
vista status                      # counts table by field/track

# CLI: individual stages (each is idempotent and only touches unfinished work)
vista discover --fields ml --per-field 10
vista fetch --max-papers 5
vista extract
vista analyze --premium           # uses PREMIUM_MODEL (claude-fable-5)
vista render
vista seed-bib path/to/refs.bib --field stats

# Run the MCP server manually (for debugging; normally invoked by Claude Code)
uv run vista-mcp                  # speaks stdio, JSON-RPC

# Browse the store with Datasette (optional [viz] extra)
uv pip install -e '.[viz]'
uv run --with datasette datasette data/papers.db
```

`ANTHROPIC_API_KEY` is **only** required for `vista analyze` and `vista pipeline`
without `--skip-analyze`. The MCP path never calls the Anthropic SDK; the
in-conversation Claude does the synthesis.

## Architecture

### The synthesis split (load-bearing design choice)

The MCP server in `vista/mcp_server.py` is **mechanical**: it returns raw
section text + metadata as JSON. It does no LLM calls. Synthesis (ranking,
direction extraction, novelty assessment) happens in whatever Claude is on the
other end of the MCP connection.

There is exactly one place that does call the Anthropic SDK:
`vista/pipeline/analyze.py`. That path is opt-in via the `[api]` extra and is
designed for unattended (cron, CI) runs of `vista analyze`. The `anthropic`
import is lazy inside `_client()` so the package works without it.

When adding new MCP tools, **do not add LLM calls to them**. If you need
synthesis, return the raw inputs and let the conversation synthesize. The skill
in `skills/vista/SKILL.md` explains the synthesis pattern callers use.

### Pipeline (discover → fetch → extract → analyze → render)

Each stage is **idempotent and resumable**; the SQLite schema encodes
"unfinished" via the absence of rows in the next table. `Store.papers()` takes
flags `needs_pdf`, `needs_extraction`, `needs_analysis` that translate into
WHERE clauses joining against `sections` and `directions`.

One wrinkle worth knowing before you "fix" it: a paper whose PDF yields no
matching sections would, under the pure "absence of rows" rule, be re-extracted
on every run. To prevent that, `run_extract` (and the live `fetch_and_extract`)
write a placeholder `sections` row with empty content and `method="regex-empty"`
when nothing matches. So `needs_extraction` means *no sections row at all*, not
*an empty one*. Re-running deliberately skips papers already known to yield
nothing.

| Stage | Module | Inputs | Outputs |
|-------|--------|--------|---------|
| discover | `vista/pipeline/discover.py` + `vista/sources/openalex.py` | `FIELDS` config, citation thresholds | `papers` rows |
| fetch | `vista/pipeline/fetch.py` | papers with `oa_url` / `pdf_url` / `arxiv_id` | PDFs in `data/pdfs/`, `papers.pdf_path` set |
| extract | `vista/pipeline/extract.py` | PDFs | `sections` rows (regex-matched headings) |
| analyze | `vista/pipeline/analyze.py` | sections + abstract | `directions` rows |
| render | `vista/render/markdown.py` | full store | `out/index.md` + per-paper / per-tag markdown |

The `vista/core.py` module wraps fetch + extract for the live MCP path so
on-demand tool calls cache into the same store.

### Storage

Single SQLite file. Schema in `vista/storage/schema.sql`. Four tables (`papers`,
`sections`, `directions`, `runs`) plus the `v_directions_full` view that pre-joins
directions to their parent paper for browsing. Foreign keys + WAL mode are on.

`Store.upsert_paper`, `Store.upsert_sections`, `Store.replace_directions` are
the idempotent write paths used by every pipeline stage; all are safe to
re-run. `upsert_paper` and `upsert_sections` use `ON CONFLICT ... DO UPDATE` on
their natural keys (`papers.id` and `(paper_id, section_type)`).
`replace_directions` instead deletes a paper's existing directions and
re-inserts, because `directions.id` is autoincrement with no natural key to
conflict on.

### Where data lives

By default, **outside the repo**. `vista/config.py` uses
`platformdirs.user_data_dir("vista", appauthor="queelius")` so the catalog
survives plugin updates and is shared between the CLI and MCP server. Override
with environment variables for project-local storage (useful when working from
a checkout):

```bash
export VISTA_DATA_DIR=$PWD/data
export VISTA_OUT_DIR=$PWD/out
```

### MCP tool surface (three groups)

`vista/mcp_server.py` registers 15 tools via `FastMCP`. They split into:

- **On-demand research** (`topic_followups`, `paper_followups`, `find_seminal`,
  `broad_followups`): live OpenAlex → cache → fetch → extract → return JSON.
  These accept `field="ad-hoc"` and a `track` like `topic` / `paper` / `legacy`
  / `broad` so the catalog tracks ad-hoc lookups separately from bulk runs.
- **Stored corpus** (`search_directions`, `list_directions`, `get_paper`,
  `submit_directions`, `mark_direction`): query and curate already-built data.
- **Pipeline + escape hatch** (`discover`, `extract_pending`, `render_markdown`,
  `status`, `run_sql`, `get_schema`): bulk operations and read-only SQL.
  `run_sql` blocks DDL/DML via `_FORBIDDEN_SQL` regex and auto-appends LIMIT.

All tools return JSON-stringified payloads (not Python objects); FastMCP
serializes them as MCP responses.

### Field configuration (where to add new domains)

`vista/config.py:FIELDS` is the single source of truth for what gets crawled.
Each entry declares:

- `concept_ids`: OpenAlex concept IDs (filter on `concepts.id`).
- `venue_ids` *(optional)*: canonical OpenAlex source IDs to filter primary
  location.
- `fulltext_filter`: one of `arxiv-required` (require arXiv mirror, best for
  ML/AI), `venue-only` (canonical venues, accept paywalls), or `any` (no
  filter). This is the principled solution to OpenAlex's flaky `is_oa` flag for
  NeurIPS/ICML/ICLR.
- `keywords` *(optional)*: keyword filter for "any"-strategy fields.
- `min_citations_recent` / `min_citations_legacy`: per-track thresholds.

Add a new field by appending to this dict; no code changes elsewhere are
needed. The CLI's `_build_config` and the discovery filter builder both read
this dict.

### Tracks

A `track` column on `papers` distinguishes how a paper got into the store:

- `recent`: post-2020, top-cited per field. Bulk run default.
- `legacy`: pre-2020, very-highly-cited (the "neglected futures" candidates).
- `seed`: ingested from `.bib` via `vista seed-bib`.
- `topic` / `paper` / `broad`: populated by the matching MCP on-demand tools.

When adding new MCP tools that fetch papers, give them their own track string
so the catalog stays auditable.

### Section extraction

`vista/pipeline/extract.py:SECTION_PATTERNS` is a dict of compiled regexes for
the four section types. Text comes from PyMuPDF first (it is column-aware and
keeps `5 Conclusion` on its own line in two-column conference papers), falling
back to `pdftotext -layout` (poppler) only if PyMuPDF is unavailable; the
heading regex depends on that one-heading-per-line layout. Headings are matched
on their own line (`^...$`) with optional leading numbering: decimal
(`6.`, `6.1`) or roman (`VI.`). There is no `Chapter N` form. The walker
captures lines until: (a) a tracked heading reappears, (b) `REFS_HEADING`
matches (references / acknowledgments / appendix), (c) `GENERIC_HEADING`
matches a likely-other heading, (d) three consecutive blank lines after at
least 5 captured lines, or (e) the `MAX_SECTION_LINES` (200) safety cap is hit.

If a paper uses creative headings ("Outlook", "Where We Go From Here", etc.)
that aren't captured, **add the variant to `SECTION_PATTERNS`** rather than
post-processing. The dedup keeps the longest match per section type, so
multiple matches per paper (e.g., chapter conclusions) are handled.

### Models

`DEFAULT_MODEL = claude-sonnet-4-6`, `PREMIUM_MODEL = claude-fable-5`. The
default model is overridable via `FOLLOWUPS_MODEL` env var. These only matter
for the Anthropic-SDK analyzer path; the MCP path is model-agnostic.

## Tests

Tests in `tests/` cover the regex-driven section extractor and the LLM JSON
output parser. They're standalone (no API key, no network, no DB) and run in
under a second. They are **the right place to add coverage** for new heading
patterns or new analyzer-output edge cases.

`pytest` is intentionally not in `dependencies` or any extra. Run via
`uv run --with pytest ...` or install it ad-hoc into the venv.

## Plugin layout (for plugin work)

```
.claude-plugin/plugin.json     plugin manifest (name, author, etc.)
.mcp.json                      MCP server registration; uses ${CLAUDE_PLUGIN_ROOT}
skills/vista/SKILL.md          when-to-call-which-tool routing for the conversation
skills/vista/references/       extended routing examples + JSON schemas
agents/research-synthesizer.md subagent for bulk landscape reports
agents/cross-referencer.md     subagent for intersecting literature with user's prior work
```

The skill is the conversation-side rulebook for the MCP. When MCP tool
contracts change (params, return shape), update both `mcp_server.py` and
`skills/vista/SKILL.md` plus `references/output-shape.md` to keep the routing
guidance honest.

## Conventions specific to this repo

- **Logging**: CLI uses `RichHandler` for colored output; MCP logs to stderr
  only (stdout is the JSON-RPC transport). Don't `print()` from MCP code.
- **OpenAlex IDs**: stripped of the `https://openalex.org/` prefix at parse
  time (`OpenAlexWork.from_api`). The `id` column is the bare `Wxxxxxxx` form.
- **Author identity**: package author and `mailto` default is
  `lex@metafunctor.com` (used as the OpenAlex polite-pool contact).
- **Read-only SQL**: any new MCP tool that takes a SQL string must reuse the
  `_FORBIDDEN_SQL` regex pattern from `mcp_server.py` rather than writing its
  own filter.
