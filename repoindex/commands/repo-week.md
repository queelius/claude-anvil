---
name: repo-week
description: Weekly activity summary across the repo collection (commits, releases, top churn).
argument-hint: "[window, e.g. 7d or 30d, default 7d]"
allowed-tools:
  - mcp__repoindex__run_sql
  - mcp__repoindex__get_manifest
---

# /repo-week

Summarize recent activity across the repository collection. Default window is 7 days.

## Arguments

- No argument: use 7 days.
- One argument like `7d`, `14d`, `30d`, `90d`: parse the integer and use that many days.
- If the argument does not match `\d+d`, fall back to 7 days and note this at the top.

## Workflow

Call `mcp__repoindex__run_sql` with the queries below, substituting the chosen window into `datetime('now', '-N days')`.

### 1. Top repos by commit churn

```sql
SELECT r.name, r.language, COUNT(*) AS commits, MAX(e.timestamp) AS last
FROM events e JOIN repos r ON e.repo_id = r.id
WHERE e.type = 'commit' AND e.timestamp > datetime('now', '-7 days')
GROUP BY r.id
ORDER BY commits DESC
LIMIT 15
```

### 2. Releases (git tags) in the window

```sql
SELECT r.name, e.ref, e.timestamp, e.message
FROM events e JOIN repos r ON e.repo_id = r.id
WHERE e.type = 'git_tag' AND e.timestamp > datetime('now', '-7 days')
ORDER BY e.timestamp DESC
```

### 3. Overall totals

```sql
SELECT type, COUNT(*) AS n
FROM events
WHERE timestamp > datetime('now', '-7 days')
GROUP BY type
ORDER BY n DESC
```

### 4. Dormant repos that woke up

Repos with activity in the window but no prior activity in the 30 days before that:

```sql
WITH recent AS (
  SELECT DISTINCT repo_id FROM events
  WHERE type = 'commit' AND timestamp > datetime('now', '-7 days')
),
before AS (
  SELECT DISTINCT repo_id FROM events
  WHERE type = 'commit'
    AND timestamp BETWEEN datetime('now', '-37 days') AND datetime('now', '-7 days')
)
SELECT r.name, r.language FROM repos r
JOIN recent rc ON rc.repo_id = r.id
LEFT JOIN before b ON b.repo_id = r.id
WHERE b.repo_id IS NULL
ORDER BY r.name
```

## Output

Keep it scannable. Suggested layout:

```
Week in review (last N days)

Commits: X across Y repos
Releases: Z tags across W repos

Top churn
  repo-a   (python)    42 commits, last 2h ago
  repo-b   (rust)      18 commits, last 1d ago
  ...

Releases
  repo-a   v0.16.0     2 days ago
  ...

Woke up
  repo-c, repo-d

Quiet week across the rest.
```

Do not list every repo. Cap to top 10 by churn. If totals are zero, say so briefly.

## When to use

- Weekly review at the start of the work week.
- Monthly retrospective: pass `30d` as the argument.
- Contrast with `repo-doctor`, which is a health triage rather than an activity summary.
