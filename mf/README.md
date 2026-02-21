# mf — Claude Code Plugin

Metafunctor site management for Claude Code. Manage papers, projects, series,
and content for metafunctor.com — a Hugo site with blog architecture, content
workflows, and cross-posting via crier.

**Requires**: [mf](https://github.com/queelius/mf) CLI installed (`pip install -e ".[dev]"`).

## Components

| Type | Name | Purpose |
|------|------|---------|
| Skill | `mf` | Site architecture guide, mf CLI reference, content workflows |
| Skill | `crier` | Cross-posting workflow — audit, select, rewrite for social platforms |
| Command | `/mf` | Site management (new posts, sync papers, health checks) |
| Command | `/crier` | Cross-post blog content to dev.to, Hashnode, Bluesky, and more |

## Install

```bash
# From the marketplace
/plugin install mf@queelius
```

## Workflows

- **Content creation**: Draft posts, sync academic papers into blog format, manage series
- **Site health**: Taxonomy audits, broken link checks, metadata validation
- **Cross-posting**: Audit unpublished content, generate platform-specific rewrites, track what's been posted where

The mf skill works from any directory — it resolves the site root automatically.

## License

MIT
