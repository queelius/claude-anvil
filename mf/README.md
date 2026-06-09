# mf — Claude Code Plugin

Metafunctor site management for Claude Code. Manage papers, projects, series,
and content for metafunctor.com — a Hugo site with blog architecture, content
workflows, and cross-posting via crier.

**Requires**: [mf](https://github.com/queelius/mf) CLI installed (`pip install -e ".[dev]"`).

## Components

| Type | Name | Purpose |
|------|------|---------|
| Skill | `mf` | Site architecture guide, mf CLI reference, content workflows |
| Skill | `scribe` | Discover latent themes across the corpus (a proposal, not a draft) |
| Command | `/mf` | Site management (new posts, sync papers, health checks) |
| Command | `/scribe` | Trigger the scribe theme-discovery skill |

Cross-posting lives in the separate **crier** plugin (`/crier`), not here: mf
creates and updates content, crier distributes it. The `scribe` skill can use
crier's `crier_search` tool as an optional accelerator but falls back to a
self-contained Glob path when crier is not installed.

## Install

```bash
# From the marketplace
/plugin install mf@queelius
```

## Workflows

- **Content creation**: Draft posts, sync academic papers into blog format, manage series
- **Site health**: Taxonomy audits, broken link checks, metadata validation
- **Cross-posting hand-off**: After content changes, route distribution to the crier plugin (`/crier`); mf itself never cross-posts

The mf skill works from any directory — it resolves the site root automatically.

## License

MIT
