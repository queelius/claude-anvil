# Tool output shapes

Full JSON shape for each Vista MCP tool's response.

## On-demand tools

`topic_followups`, `paper_followups`, `find_seminal`, `broad_followups`
all return the same paper shape:

```jsonc
{
  "topic" | "query" | "identifier": "...",        // input echoed back
  "params": { /* parameters used, useful for tuning */ },
  "papers": [ /* see Paper below */ ],
  "paper_count": 8
}
```

`paper_followups` returns just the single Paper (no wrapper).

### Paper

```jsonc
{
  "paper_id": "W2907492528",                 // OpenAlex ID
  "title": "...",
  "authors": ["A. Author", "B. Coauthor"],   // truncated to 8
  "year": 2020,
  "venue": "Conference / journal name",
  "cited_by_count": 8883,
  "doi": "10.xxxx/yyyy",
  "arxiv_id": "1901.00596",
  "arxiv_url": "https://arxiv.org/abs/1901.00596",
  "doi_url": "https://doi.org/10.xxxx/yyyy",
  "abstract": "...",
  "field": "ad-hoc",                         // or ml | ai | stats | ransomware
  "track": "topic",                          // or recent | legacy | seed | broad | paper
  "sections": [
    {
      "type": "future_work",                 // future_work | limitations | discussion | conclusion
      "heading": "Future Directions",        // the actual heading we matched
      "content": "...",                      // raw section text
      "char_count": 1914
    }
  ],
  "note": "pdf_unavailable"                  // optional; present when fetch failed
}
```

If a paper has no sections (PDF unavailable, extraction failed), the
`sections` array is empty and `note` may be set. Skip those papers in your
synthesis or flag them to the user.

## Catalog tools

`search_directions`, `list_directions`:

```jsonc
{
  "query": "...",                            // omitted in list_directions
  "count": 25,
  "results": [
    {
      "id": 42,                              // direction id (use with mark_direction)
      "direction": "...",
      "rationale": "...",
      "feasibility": "medium",
      "novelty": "high",
      "field_tags_json": "[\"gnn\",\"theory\"]",
      "user_status": "open",
      "paper_id": "Wxxx",
      "title": "...",
      "year": 2020,
      "venue": "...",
      "cited_by_count": 1234,
      "field": "ml",
      "track": "recent"
    }
  ]
}
```

`get_paper`: same as Paper above, plus `directions: [...]` (rows from the
directions table).

## Curation tools

`submit_directions`:

```jsonc
{ "paper_id": "Wxxx", "stored": 5 }
// or { "paper_id": "...", "error": "paper not in store" }
```

`mark_direction`:

```jsonc
{ "direction_id": 42, "status": "interesting", "notes": "..." }
```

## Pipeline tools

`discover`:

```jsonc
{ "counts": { "ml/recent": 25, "ai/recent": 20, ... } }
```

`extract_pending`:

```jsonc
{
  "fetch":   { "attempted": 30, "ok": 27, "failed": 3 },
  "extract": { "attempted": 27, "with_sections": 25, "no_sections": 2 }
}
```

`render_markdown`:

```jsonc
{ "render": { "papers": 75 } }
```

`status`:

```jsonc
{
  "totals": { "papers": 75, "directions": 432 },
  "by_field_track": [
    { "field": "ml", "track": "recent", "papers": 25, "with_pdf": 25,
      "with_sections": 24, "with_directions": 24 }
  ]
}
```

## SQL tools

`run_sql`:

```jsonc
{ "row_count": 12, "rows": [ { /* per-column key-value */ } ] }
// or { "error": "syntax error..." }
```

DDL/DML are rejected with `{"error": "only read-only queries allowed"}`.

`get_schema`:

```jsonc
{ "schema": "CREATE TABLE papers (...) ..." }
```
