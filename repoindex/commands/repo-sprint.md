---
name: repo-sprint
description: Assemble context for a focused work session (dirty repos, unpushed commits, recent activity, release candidates).
allowed-tools:
  - mcp__repoindex__get_manifest
  - mcp__repoindex__run_sql
---

# /repo-sprint

"What's open right now?" Pulls together the signals that matter at the start of a coding day so you can pick the next thing to work on.

## Workflow

Run the following queries in parallel and synthesize. Use `mcp__repoindex__run_sql` for each.

### 1. Dirty working trees

```sql
SELECT name, path, language FROM repos
WHERE is_clean = 0
ORDER BY name
```

### 2. Unpushed commits

```sql
SELECT name, ahead, path FROM repos
WHERE ahead > 0
ORDER BY ahead DESC
```

### 3. Recent commit activity (last 3 days)

```sql
SELECT r.name, r.language, COUNT(*) AS commits, MAX(e.timestamp) AS last
FROM events e JOIN repos r ON e.repo_id = r.id
WHERE e.type = 'commit' AND e.timestamp > datetime('now', '-3 days')
GROUP BY r.id
ORDER BY last DESC
LIMIT 15
```

### 4. Release candidates

Repos that detected a registry package and have commits since the last release tag. Heuristic:

```sql
WITH last_tag AS (
  SELECT repo_id, MAX(timestamp) AS tagged FROM events
  WHERE type = 'git_tag'
  GROUP BY repo_id
),
recent_commits AS (
  SELECT repo_id, COUNT(*) AS n, MAX(timestamp) AS last_commit
  FROM events
  WHERE type = 'commit' AND timestamp > datetime('now', '-30 days')
  GROUP BY repo_id
)
SELECT r.name, p.registry, p.current_version,
       rc.n AS commits_30d, lt.tagged AS last_release
FROM repos r
JOIN publications p ON p.repo_id = r.id AND p.published = 1
JOIN recent_commits rc ON rc.repo_id = r.id
LEFT JOIN last_tag lt ON lt.repo_id = r.id
WHERE (lt.tagged IS NULL OR rc.last_commit > lt.tagged)
ORDER BY rc.n DESC
LIMIT 10
```

### 5. Recently active repos with open quality gaps

```sql
WITH recent AS (
  SELECT DISTINCT repo_id FROM events
  WHERE type = 'commit' AND timestamp > datetime('now', '-14 days')
)
SELECT r.name, r.language,
       (CASE WHEN r.has_license = 0 THEN 1 ELSE 0 END) +
       (CASE WHEN r.has_readme  = 0 THEN 1 ELSE 0 END) +
       (CASE WHEN r.has_ci      = 0 THEN 1 ELSE 0 END) AS gaps
FROM repos r
JOIN recent rc ON rc.repo_id = r.id
WHERE COALESCE(r.github_is_archived, 0) = 0
  AND (r.has_license = 0 OR r.has_readme = 0 OR r.has_ci = 0)
ORDER BY gaps DESC
LIMIT 10
```

## Output

Produce a "sprint kickoff" summary, grouped by urgency:

```
Open work

Uncommitted    N repos
  repo-a, repo-b, ...

Unpushed       M repos, K commits total
  repo-c  12 commits ahead
  repo-d   3 commits ahead

Active this week
  repo-e  (python)   14 commits, last 2h ago
  repo-f  (rust)      6 commits, last 1d ago

Release candidates (commits since last tag)
  repo-e  pypi 0.15.0, 14 commits in the last 30 days
  ...

Active repos with open gaps
  repo-g   missing license, missing ci
```

Then ask: "Which of these do you want to focus on first?"

## Notes

- Do not run any write operations. This command is purely context assembly.
- If all sections are empty, say so and note that the collection looks quiet.
- Section contents may overlap across sections (for example, a dirty repo with unpushed commits). That is fine; the overlap tells you which repo is the clear priority.

## When to use

- Start of the day, before diving into code.
- When returning to the collection after time away.
- Contrast with `/repo-status`: sprint synthesizes across repos, status shows one repo.
