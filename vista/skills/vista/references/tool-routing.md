# Tool routing reference

Worked examples for picking the right Vista MCP tool from a user's phrasing.

## "Open problems in X" → topic_followups

User: "What are the open problems in diffusion models?"

```
topic_followups(topic="diffusion models", max_papers=8)
```

The phrase "open problems" reliably maps to topic_followups. Use the same
tool for "future work in", "research directions on", "what's next for",
"what's hot in" if the user specifies a topic.

## "What does paper X say about future work" → paper_followups

User: "What's the future work in the Attention Is All You Need paper?"

The paper is identifiable by title.

```
paper_followups(identifier="Attention Is All You Need")
```

User: "Read me arxiv:2005.14165 and tell me what's next"

```
paper_followups(identifier="2005.14165")
```

User: "DOI 10.1038/s41586-021-03819-2, open problems?"

```
paper_followups(identifier="10.1038/s41586-021-03819-2")
```

## "Older / neglected / classical" → find_seminal

User: "What older highly-cited papers in stats had future work that nobody
followed up on?"

```
find_seminal(topic=None, year_max=2015, year_min=2000, min_citations=500, max_papers=10)
```

Note: `topic=None` returns the top-cited legacy papers across the full
literature within the year window. Pass a topic if the user wants to scope.

## "Cross-field / outside my prior work / serendipitous" → broad_followups

User: "Find me research unrelated to my prior work that has interesting
follow-ups."

The user explicitly asks for *unrelated*. We don't know what their prior
work is from this skill alone, but we can return a wide cross-field sample.

```
broad_followups(query="open problems", max_papers=15, year_min=2022)
```

If the user names target fields:

User: "Anything interesting that bridges ML and statistics?"

```
broad_followups(query="ML statistics intersection", fields=["ml", "stats"])
```

## "Catalog already on disk" → search_directions / list_directions

User: "Show me the high-feasibility directions I've already extracted."

```
list_directions(field=None, user_status="open", limit=50)
# then filter / sort in conversation by feasibility
```

User: "Search my catalog for 'masked likelihood'."

```
search_directions(query="masked likelihood", limit=20)
```

## Ambiguous phrasing: disambiguate

User: "Future work."

Too vague. Ask: "Future work on what topic, or for which paper?" Don't guess
between `topic_followups` and `paper_followups` without a topic or
identifier.

User: "What should I work on?"

Ask: "Across the literature broadly, or scoped to a topic / your existing
catalog?" Then route to `broad_followups`, `topic_followups`, or
`list_directions` accordingly.

## Stats-specific defaults

For stats topics, drop the citation threshold and don't require arXiv:

```
topic_followups(
  topic="masked likelihood",
  min_citations=15,
  require_arxiv=False,
)
```

Some stats papers will fail to fetch (paywalled, no OA). The tool will skip
them gracefully; `paper_count` reflects what actually came back.
