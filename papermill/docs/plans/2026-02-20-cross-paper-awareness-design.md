# Cross-Paper Awareness for Papermill

**Date**: 2026-02-20
**Status**: Approved
**Scope**: Schema addition + skill updates to init, init/refresh, and status

## Problem

Papermill manages individual papers in isolation. In practice, papers exist in a research ecosystem — they extend each other, share a series, implement each other's theory in software, and should cross-cite. The user already captures these relationships in freeform prose (ASCII dependency trees, narrative descriptions, citation tables), but there is no structured representation that skills can read consistently.

## Design Decision

**Structured context** — add a `related_papers` YAML block to `.papermill.md` with typed links. Skills read it as context but do not enforce anything. Claude's natural reasoning does the heavy lifting. No active cross-checking, no bidirectional sync, no centralized registry.

## Schema

New top-level field in `.papermill.md` YAML frontmatter:

```yaml
related_papers:
  - path: ~/github/papers/masked-causes-in-series-systems
    rel: extends
    label: "Foundation paper — general masked-cause framework (C1-C2-C3)"
  - path: ~/github/rlang/maskedcauses
    rel: implemented-by
    label: "R package implementing the methods from this and the foundation paper"
  - path: ~/github/papers/expo-masked-fim
    rel: companion
    label: "Exponential special case; this paper generalizes to Weibull"
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `path` | string | yes | Path to the related project (absolute or `~/`-relative) |
| `rel` | enum | yes | Relationship type (see vocabulary below) |
| `label` | string | yes | One-line freeform description of the relationship |

### Relationship Vocabulary

| `rel` value | Meaning (from *this* paper's perspective) | Directional |
|-------------|------------------------------------------|-------------|
| `extends` | This paper extends/generalizes that work | Yes |
| `extended-by` | That paper extends this one | Yes |
| `implements` | This paper implements that work's theory | Yes |
| `implemented-by` | That repo implements this paper's methods | Yes |
| `companion` | Different angle on the same research | No |
| `series` | Part of a numbered series together | No |
| `merged-into` | This paper was absorbed into that one | Yes |
| `supersedes` | This paper replaces that one | Yes |

No `cites`/`should-cite` type — citation is implicit. Every `related_papers` entry implies "should cite." The prior-art and review skills can detect missing citations by comparing entries against the `.bib` file.

## Discovery

Two layers, both feeding into the explicit `related_papers` block:

| Layer | How | When |
|-------|-----|------|
| **Explicit** | User declares paths and relationships | Always, source of truth |
| **Repoindex** | Query for repos containing `.papermill.md` | Opt-in during init/refresh |

Discovery does not create a separate category — it suggests candidates that the user confirms, which are then added to `related_papers` like any manually-added entry.

### Repoindex Discovery Query

```bash
repoindex sql "SELECT name, path FROM repos WHERE path IN (SELECT repo_path FROM files WHERE name = '.papermill.md')"
```

If repoindex is not installed or the query fails, skip gracefully.

## Skill Changes

### init (Step 7 — schema)

Add `related_papers: []` to the `.papermill.md` template.

### init (Step 6 — related work question)

Expand the existing "Ask About Related Work and Software" step:

1. Run the existing question about related work (unchanged).
2. If the user describes relationships, structure them into `related_papers` entries in addition to the freeform notes. Ask the user to confirm the `rel` type for each.
3. If repoindex is available, query for other papermill-tracked repos. Present matches and ask: "I found N other papermill-tracked projects. Are any of these related to this paper?"
4. For each confirmed relationship, add a `related_papers` entry.

### init/refresh (Schema migration — Refresh Mode Step 1)

Add migration case:

```
Missing `related_papers` → add as `[]`
```

### init/refresh (Fill in missing context — Refresh Mode Step 3)

Add a new check:

- If `related_papers` is empty, run the repoindex discovery query (if available) and offer to populate relationships. Also re-run the Step 6 question about related work.
- If `related_papers` is non-empty, still offer repoindex discovery to catch new projects added since last refresh.

### status (Step 3 — dashboard)

Add a **Related Papers** section to the dashboard, between Venue and Recent Activity:

```
### Related Papers

| Project | Relationship | Description |
|---------|-------------|-------------|
| masked-causes-in-series-systems | extends | Foundation paper — general framework |
| maskedcauses | implemented-by | R package implementing the methods |

If `related_papers` is empty, show: "None linked. Run `/papermill:init` with refresh to discover related projects."
```

### Other skills (no changes)

These skills already read `.papermill.md` before operating. The `related_papers` block becomes part of their natural context:

- **thesis**: Reads related papers' theses for positioning context
- **prior-art**: Notices related papers when searching, checks for citation coverage
- **outline**: Considers how this paper fits into the broader series/ecosystem
- **review**: Flags missing citations for listed related papers
- **polish**: Checks code availability statements against `implemented-by` links

No explicit logic changes needed — Claude reasons about the structured data naturally.

## What This Does NOT Do (by design)

- No bidirectional sync (linking in A does not auto-update B)
- No enforcement or validation across repos
- No centralized registry or index of all papers
- No filesystem scanning beyond repoindex
- No active cross-checking logic in skills

These could be layered on later. The schema is forward-compatible.

## Migration Path

Existing `.papermill.md` files get the new field via the standard refresh flow:

```
/papermill:init → "Would you like to refresh?" → yes
→ "Added 1 missing field: related_papers"
→ "I found N other papermill-tracked projects via repoindex. Any related?"
→ user picks connections → done
```

Freeform relationship info in `## Related Work and Software` notes stays untouched. The structured block supplements it.
