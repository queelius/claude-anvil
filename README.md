# vista

Surface salient research directions by reading the **Future Work**,
**Limitations**, **Discussion**, and **Conclusion** sections of highly-cited
papers. Live OpenAlex search, PDF section extraction, structured catalog.

Vista is a Claude Code plugin **and** a standalone Python CLI. The plugin
exposes the work as MCP tools so the in-conversation Claude can fetch raw
section text on demand and synthesize directions inline. The CLI does bulk
catalog builds.

## Two ways to use it

### As a Claude Code plugin (in-conversation lookups)

In any conversation:

> "What are the open problems in diffusion models?"
> "Summarize the future work in arXiv:2005.14165."
> "Find me follow-up research outside reliability/survival analysis."

The `vista` skill routes these to MCP tools (`topic_followups`,
`paper_followups`, `find_seminal`, `broad_followups`). The MCP server
returns structured JSON. Claude reads the section text and synthesizes
in the response.

### As a standalone CLI (bulk catalog builds)

```bash
vista pipeline --fields ml,ai,stats,ransomware --per-field 25
```

Discovers papers, fetches PDFs, extracts sections, distills directions, and
renders a browseable markdown catalog plus a queryable SQLite database.

## Install

```bash
cd ~/github/beta/vista
uv venv
uv pip install -e .
python -m pytest tests/ -q
```

For the headless batch path (cron, CI), install the optional `api` extra and
set `ANTHROPIC_API_KEY`:

```bash
uv pip install -e '.[api]'
export ANTHROPIC_API_KEY=sk-ant-...
```

In-conversation use through the plugin does **not** need an API key. Claude
in the conversation does the synthesis.

## Wire up the plugin

### Project-scoped (recommended for testing)

Add a `.mcp.json` at the project root where you want vista available:

```json
{
  "mcpServers": {
    "vista": {
      "command": "uv",
      "args": ["run", "--project", "/home/spinoza/github/beta/vista", "vista-mcp"]
    }
  }
}
```

### As a full plugin

The plugin manifest lives at `.claude-plugin/plugin.json` and the MCP config
at `.mcp.json` (both shipped in this repo). To install as a plugin, point
your Claude Code plugin loader at this directory, or symlink it under
`~/.claude/plugins/vista/`. The `${CLAUDE_PLUGIN_ROOT}` variable in
`.mcp.json` resolves to the plugin's path at runtime.

After wiring, verify in Claude Code: the `vista` skill should appear, and
`mcp__vista__*` tools should be callable.

## MCP tool surface

### On-demand research (live OpenAlex)

| Tool | Purpose |
|------|---------|
| `topic_followups(topic, max_papers, year_min, min_citations)` | Top-cited recent papers on a topic, with their FW/Lim/Disc/Conc sections. |
| `paper_followups(identifier)` | Single paper by DOI / arXiv id / OpenAlex id / title. |
| `find_seminal(topic, year_max, min_citations)` | Older highly-cited papers; the "neglected futures" angle. |
| `broad_followups(query, fields)` | Cross-field exploratory; for serendipity outside your prior work. |

All four cache results to the local SQLite store (`data/papers.db`) and
return structured JSON: paper metadata, abstract, raw section text per type.

### Stored corpus

| Tool | Purpose |
|------|---------|
| `search_directions(query, ...)` | Keyword + filter search over distilled directions. |
| `list_directions(field, track, status, limit)` | Paginated catalog listing. |
| `get_paper(paper_id)` | Full paper record with sections and any directions. |
| `submit_directions(paper_id, directions[])` | Persist synthesized directions for a paper. |
| `mark_direction(direction_id, status, notes)` | Curation: open / interesting / started / abandoned. |

### Pipeline

| Tool | Purpose |
|------|---------|
| `discover(fields, track, per_field)` | Bulk OpenAlex query. |
| `extract_pending()` | Fetch + extract any papers not yet processed. |
| `render_markdown()` | Regenerate `out/index.md` plus per-paper files. |
| `status()` | Counts dashboard. |

### SQL escape hatch

| Tool | Purpose |
|------|---------|
| `run_sql(query)` | Read-only SQL against the local store. DDL/DML blocked. |
| `get_schema()` | Schema and view definitions. |

## CLI commands

```
vista discover     OpenAlex query, store paper metadata
vista fetch        download arXiv / OA PDFs
vista extract      PyMuPDF text + heading regex for the four section types
vista analyze      Anthropic-API distillation (optional, needs API key)
vista render       browseable markdown index plus per-paper files
vista seed-bib     ingest .bib entries, resolve via OpenAlex
vista status       counts by field/track
vista pipeline     run all stages end-to-end
```

The pipeline stages are idempotent. Re-running picks up where the previous
run left off, only touching papers that have not yet been processed at each
stage.

## Tracks

- `recent`: post-2020, top-cited per field. Bulk of a normal run.
- `legacy`: pre-2020, very-highly-cited. Older directions where the field may
  not have followed up. Use the `find_seminal` MCP tool for the on-demand
  version.
- `seed`: papers ingested from the user's `.bib` files via `seed-bib`.
- `topic` / `paper` / `broad`: ad-hoc tracks populated by the on-demand MCP
  tools.

## Fields

Configured in `vista/config.py`. Each field has OpenAlex concept IDs, optional
canonical venue source IDs, a `fulltext_filter` strategy
(`arxiv-required` / `venue-only` / `any`), and per-track citation thresholds.
Pre-configured: `ml`, `ai`, `stats`, `ransomware`.

## Mining the catalog

```sql
-- High-feasibility recent directions
SELECT direction, paper_title, year, cited_by_count
FROM v_directions_full
WHERE feasibility = 'high' AND track = 'recent'
ORDER BY cited_by_count DESC LIMIT 30;

-- Directions grouped by tag
SELECT json_each.value AS tag, COUNT(*) AS n
FROM directions, json_each(directions.field_tags_json)
GROUP BY tag ORDER BY n DESC;

-- Mark interesting directions
UPDATE directions
SET user_status = 'interesting',
    user_notes = 'Maps to my masked-causes work'
WHERE id = 42;
```

Browse with Datasette:

```bash
uv run --with datasette datasette data/papers.db
```

## Output layout

```
out/
├── index.md                       master index, grouped by field
├── by-tag.md                      directions grouped by LLM-assigned tag
├── queries.md                     example SQL for mining the store
└── papers/
    └── <field>--<slug>--<id>.md   one file per paper
data/
├── papers.db                      SQLite store
├── pdfs/                          cached PDFs
└── text/                          cached plain-text extracts
```

Per-paper markdown files have YAML frontmatter compatible with Hugo, so the
output drops into a static site if needed later.

## Plugin layout

```
.claude-plugin/plugin.json     manifest
.mcp.json                      MCP server registration
skills/vista/
├── SKILL.md                   trigger phrases, routing rules, synthesis pattern
└── references/
    ├── tool-routing.md        worked examples for picking the right tool
    └── output-shape.md        full JSON schemas for tool responses
agents/
├── research-synthesizer.md    bulk landscape report from many papers
└── cross-referencer.md        intersect literature with user's prior work
vista/                         Python package (CLI + pipeline + MCP server)
```

## Known limitations

- **Future work inside conclusions.** Some papers do not have a separate
  Future Work heading; the future work prose sits at the tail of Conclusion.
  The regex extractor captures the Conclusion section in that case, and the
  MCP returns it. Synthesis pulls directions out of conclusion text fine.
- **OpenAlex venue coverage is sparse for NeurIPS, ICML, and ICLR.** OpenAlex
  does not index every NeurIPS paper as type `article` with `is_oa=true`. The
  `arxiv-required` filter strategy works around this for ML and AI by
  requiring an arXiv mirror.
- **Stats and ransomware coverage is uneven.** Many top stats papers are
  paywalled with no arXiv version; many security papers live in fragmented
  yearly proceedings. Expect a higher skip rate at fetch time.
- **Heading regex is conservative.** Some papers use creative headings
  ("Outlook", "Where We Go From Here") that the regex misses. Add patterns
  to `vista/pipeline/extract.py` as needed.
