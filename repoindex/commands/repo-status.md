---
name: repo-status
description: Quick overview of the collection, or a detailed single-repo view if a name is given.
argument-hint: "[repo-name]"
allowed-tools:
  - mcp__repoindex__get_manifest
  - mcp__repoindex__run_sql
---

# /repo-status

Quick, read-only status view. Two modes depending on whether a repo name is passed.

## Mode 1: No argument (collection overview)

1. Call `mcp__repoindex__get_manifest()`.
2. Format the response concisely, not as raw JSON. Include:
   - Total repos, total events, last refresh timestamp.
   - Language breakdown (top 5 by repo count).
   - Publication registries represented (if included in manifest).
   - Any staleness warning (if the last refresh was over 7 days ago, flag it and suggest `repoindex refresh`).
3. Keep the output under 15 lines. This is a glanceable dashboard.

## Mode 2: With a repo name argument

The argument is a repo name (possibly a fragment). Resolve it with fuzzy matching.

### Step 1: Resolve the name

```sql
SELECT id, name, path, language, description, is_clean, ahead, behind
FROM repos
WHERE name = ? OR name LIKE ?
ORDER BY CASE WHEN name = ? THEN 0 ELSE 1 END, name
LIMIT 5
```

If multiple matches, show the list and ask which one.

If zero matches, try a broader fuzzy search:

```sql
SELECT name, path FROM repos
WHERE name LIKE '%NAME%'
ORDER BY name
LIMIT 10
```

### Step 2: Detail view

Once a single repo is identified, run these three queries in parallel:

```sql
-- Main row
SELECT name, path, language, description, is_clean, ahead, behind,
       has_readme, has_license, has_ci, has_citation, has_codemeta,
       github_stars, github_forks, github_topics, github_description,
       github_is_archived
FROM repos WHERE id = ?
```

```sql
-- Recent events (last 30 days, max 15 rows)
SELECT type, timestamp, ref, message
FROM events
WHERE repo_id = ? AND timestamp > datetime('now', '-30 days')
ORDER BY timestamp DESC
LIMIT 15
```

```sql
-- Publications
SELECT registry, package_name, current_version, published, downloads_30d, doi
FROM publications WHERE repo_id = ?
```

### Step 3: Render

Show a compact repo card:

```
repo-name  (language, github stars, path)
description line if present

Git: clean / dirty, N ahead, M behind
Quality: readme ok, license ok, ci missing, citation missing
Publications: pypi 0.15.0 published, 3421 downloads 30d

Recent activity (last 30 days):
  git_tag    2d ago   v0.16.0
  commit     3d ago   feat: ...
  ...

Flags: archived, fork, private (only if any are true)
```

Omit empty sections. No need to repeat zero counts.

## When to use

- `/repo-status` alone: morning glance at the collection.
- `/repo-status name`: quick lookup of a single repo.
- Contrast with the `repo-doctor` agent: this command is a read-only detail view, not a triage. For a prioritized action list across the whole collection, use `repo-doctor`.
