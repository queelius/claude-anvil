---
name: vista
description: This skill should be used when the user asks about research directions, open problems, future work, or follow-up research from the academic literature. Trigger phrases include "open problems in X", "what's next for Y", "future work for paper Z", "research directions on T", "salient follow-up research", "what should I work on next in", "find me follow-up research unrelated to my prior work", "broad survey of W", "neglected directions in V". Routes the request to the right Vista MCP tool, reads back the structured paper sections, and synthesizes research directions in the conversation.
version: 0.1.0
---

# Vista

Vista surfaces *salient research directions* by reading the **Future Work**,
**Limitations**, **Discussion**, and **Conclusion** sections of highly-cited
papers. The MCP server does the mechanical work (OpenAlex search, PDF fetch,
section extraction, caching). This skill tells you when to call which MCP tool
and how to synthesize the structured payload it returns.

## Core principle

The MCP tools are **mechanical**. They return raw section text plus metadata.
You (Claude in this conversation) read the sections and produce the synthesis:
ranking, pattern detection, novelty assessment, cross-paper themes. Do not
expect the MCP to "give you the answer"; it gives you the inputs.

## When to invoke which tool

Read the user's question carefully and route:

| User intent | Tool | Notes |
|-------------|------|-------|
| "Open problems / future work / research directions in **a topic**" | `topic_followups(topic, max_papers=8, year_min=2020, min_citations=30)` | Most common. Recent, highly-cited, arXiv-available. |
| "What does paper / arXiv:1234.5678 / DOI X say about future work?" | `paper_followups(identifier)` | Single-paper deep-dive. Identifier can be DOI, arXiv id, OpenAlex id, or title. |
| "Older / classical / under-explored / neglected directions in X" | `find_seminal(topic, year_max=2019, min_citations=1000)` | Legacy track. The "papers everyone cites but nobody followed up on." |
| "Broad / cross-field / serendipitous search; find directions outside my prior work" | `broad_followups(query, fields=None, max_papers=12)` | Exploratory; looser thresholds; spans fields. |
| "Search the local catalog of distilled directions" | `search_directions(query, ...)` | Use after a build run. Searches what the user has already mined. |
| "List interesting / open / started directions" | `list_directions(...)` | Curation/review. |
| "Mark this direction as interesting" | `mark_direction(direction_id, status, notes)` | User curation. |
| "Save these directions for paper X" | `submit_directions(paper_id, directions)` | After you've synthesized directions, persist them so future runs can search them. |
| "What papers / directions / fields are in the store?" | `status()` or `run_sql(...)` | Inspection. |

If unsure: prefer `topic_followups` for topic questions and `paper_followups`
for paper questions. If the user wants breadth or surprise, use
`broad_followups`. If the request mentions classical, neglected, or
"never-followed-up", use `find_seminal`.

## Synthesis pattern after a tool call

Each on-demand tool returns:

```jsonc
{
  "topic": "diffusion models",
  "params": { ... },
  "papers": [
    {
      "paper_id": "Wxxxxxxx",
      "title": "...",
      "authors": [...],
      "year": 2023,
      "venue": "...",
      "cited_by_count": 1234,
      "doi": "...", "arxiv_id": "...", "arxiv_url": "...", "doi_url": "...",
      "abstract": "...",
      "sections": [
        {"type": "future_work", "heading": "Future Work", "content": "...", "char_count": ...},
        {"type": "limitations", "heading": "Limitations",  "content": "...", "char_count": ...},
        {"type": "discussion",  "heading": "Discussion",   "content": "...", "char_count": ...},
        {"type": "conclusion",  "heading": "Conclusion",   "content": "...", "char_count": ...}
      ]
    },
    ...
  ],
  "paper_count": 8
}
```

For each paper:

1. Read the `future_work` section if present, else `limitations`, else
   `discussion`/`conclusion` (the latter often contain future-work prose
   without a separate heading).
2. Pull out **concrete, actionable** directions. Reject vague aspirations
   ("more experiments", "scale up").
3. For each, capture: a one-sentence direction, a one-line rationale grounded
   in the section text, a short verbatim quote (substring of the section), and
   tags (`["topic-keyword", "method-keyword"]`).
4. Estimate `feasibility` and `novelty` (low/medium/high) based on the paper's
   stated limits.

Then synthesize across papers:

- **Consensus directions**: themes that appear across ≥2 papers.
- **Frontier directions**: novel, mentioned by one paper, well-supported.
- **Conspicuous absences**: areas the user might expect to be flagged but
  aren't (use sparingly; it's interpretive).
- **Contradictions**: papers disagreeing on what to do next.

Present the synthesis with explicit citations to paper title and year, and
include the arXiv or DOI URL so the user can drill in.

If the user wants the synthesized directions persisted, call
`submit_directions(paper_id, directions)` per paper. Otherwise leave the
catalog alone, since the conversation answer is enough.

## Defaults to nudge

- For ML/AI topics, `topic_followups` defaults are usually fine.
- For statistics, drop `min_citations` to ~20 and set `require_arxiv=False`
  (many top stats papers are not on arXiv).
- For ransomware / security, set `require_arxiv=False` and lean on
  `min_citations=15`. USENIX/NDSS papers are often OA but not arXiv.

## Output style

Default to a concise structured response: synthesis first, then a "directions
table" with paper, year, citation count, direction one-liner, and a link.
Offer to drill into any direction. Do not paste raw section text back at the
user unless they ask for it.

## Bulk / pipeline workflows

If the user asks to **build a corpus** rather than ask an in-conversation
question (e.g., "set up a recurring sweep across all four fields"), use the
bulk tools (`discover`, `extract_pending`, `render_markdown`) or hand them
back to the CLI: `vista pipeline --fields ml,ai,stats,ransomware --per-field 25`.

## Additional resources

- `references/tool-routing.md`: extended decision examples for picking the
  right MCP tool from ambiguous user phrasings.
- `references/output-shape.md`: full JSON schema for each tool's response.
