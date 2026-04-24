---
name: repo-audit
description: Read-only quality audit summary via `repoindex ops audit`. Shows critical and recommended gaps without fixing anything.
argument-hint: "[--language X | --tag T | --recent 7d | --category essentials | --severity critical]"
allowed-tools:
  - Bash
  - mcp__repoindex__run_sql
---

# /repo-audit

Run `repoindex ops audit` with the given filters and summarize the results. Read-only: this command surfaces gaps, it does not fix them.

## Arguments

Forward any arguments directly to the CLI. Common filters:

| Flag | Purpose |
|------|---------|
| `--language python` | Only Python repos |
| `--tag work/active` | Only repos with a matching tag |
| `--recent 7d` | Only repos with commits in the last 7 days |
| `--dirty` | Only repos with uncommitted changes |
| `--category essentials` | Scope to essentials, development, discoverability, or documentation |
| `--severity critical` | Show only critical issues |

## Workflow

### Step 1: Run the audit

Always pass `--json` so the output is parseable.

```bash
repoindex ops audit --json <forwarded args>
```

Each JSON line represents one repo with its score per category and a list of failed checks.

### Step 2: Aggregate

Walk the JSONL output and count:

- Total repos audited.
- Critical failures: sum of critical-severity failed checks, grouped by check name.
- Recommended failures: same, grouped by check name.
- Repos with zero issues (perfect score).
- Worst offenders: repos with the most critical failures.

### Step 3: Summarize

Produce a compact report:

```
Audit summary (N repos, filters: ...)

Critical gaps
  no_license            7 repos: foo, bar, baz, ...
  no_readme             3 repos: ...
Recommended gaps
  no_citation           12 repos: ...
  no_ci                 9 repos: ...

Perfect (no gaps):  4 repos
Worst offenders:
  repo-a   4 critical, 6 recommended
  repo-b   3 critical, 5 recommended
```

Cap each repo list to the first 5 names plus a count for the rest.

### Step 4: Offer follow-ups

End with suggestions, do not execute them automatically:

- To fix deterministic gaps across a subset: `repoindex ops generate <kind>` with a query filter.
- To drill into one repo: use the `repo-polish` agent.
- To re-run with tighter scope: `/repo-audit --severity critical --category essentials`.

## When to use

- Pre-release overview across a subset (for example `/repo-audit --language python`).
- Contrast with the `repo-polish` agent: this command is a collection-wide read-only summary. `repo-polish` is a full single-repo release preparation workflow that actually writes files.
- Contrast with the `repo-doctor` agent: `repo-doctor` covers dirty state, unpushed commits, staleness, and publication gaps. `/repo-audit` focuses specifically on the metadata completeness checks that `ops audit` encodes.
