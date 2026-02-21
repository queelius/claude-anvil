---
name: jot
description: >-
  Use when the user needs to interact with their plaintext journal. Provides
  CLI reference for jot — a plaintext journal tool for capturing ideas, tasks,
  notes, plans, and logs. Trigger on: "jot add", "jot list", "jot search",
  "jot tags", "capture idea", "track task", "journal", "what are my tasks",
  "what am I working on", "project status", "search my notes", "open tasks",
  "stale entries", "add a note", "log this".
---

# jot CLI Reference

jot is a CLI-first plaintext journal tool designed for LLM orchestration. Entries are markdown files with YAML frontmatter stored at `entries/YYYY/MM/YYYYMMDD-slug.md`. All commands provide simple CRUD primitives with JSON output for machine consumption. Intelligence lives in the LLM layer; jot provides the data substrate.

## Journal Resolution

jot walks up from the current working directory looking for `.jot/` directories. If no local journal is found, it falls back to `~/.jot` (the global journal). Run `jot which` to display the active journal's name, path, and scope (local or global). Run `jot init` to create a new journal in the current directory.

## Data Model

Entry fields: `title` (string), `type` (idea/task/note/plan/log), `tags` (array of strings), `status` (open/in_progress/done/blocked/archived), `priority` (low/medium/high/critical), `due` (date string), `created` (timestamp), `modified` (timestamp). Task-specific fields: `blocked_by`, `depends_on`. Entries are stored as markdown files with YAML frontmatter. Slugs follow the format `YYYYMMDD-title-slug` (e.g., `20240102-api-redesign`).

## Output Formats

Default output is table format. Global flags control output: `--json` (JSONL, one JSON object per line), `--table` (columnar), `--markdown` or `--md` (markdown list). The `--fuzzy` global flag enables Levenshtein-based fuzzy matching for tags and search queries across all commands. Always prefer `--json` when parsing results programmatically.

## Commands

### Capture — Creating Entries

```bash
# Quick capture (one-liner, title = content)
jot add "Quick thought about API caching"
jot add "Fix login bug" --type=task --priority=high --tags=auth
jot add "Review PR" --type=task --due=3d --tags=work,urgent
jot add "Sprint retro notes" --type=log --status=open

# Editor-based capture (opens $EDITOR with template)
jot new
jot new --type=idea --tags=api,architecture
jot new --title="API Redesign Proposal" --priority=high --due=2024-03-01
```

The `add` command takes a single positional argument as content and title. Flags: `--type`/`-t`, `--tags`, `--priority`/`-p`, `--due`/`-d` (accepts YYYY-MM-DD, 3d, 1w, today, tomorrow), `--status`/`-s`. Tasks default to status `open` if no status is specified.

The `new` command opens the configured editor with a frontmatter template. Flags: `--title`, `--type`/`-t`, `--tags`, `--priority`/`-p`, `--due`/`-d`. The entry is discarded if the editor closes without changes or with empty content.

### View and Query

```bash
# List entries (newest first by default)
jot list                                    # All entries
jot list --type=task --status=open          # Open tasks
jot list --tags=api --since=7d             # Recent entries tagged 'api'
jot list --priority=high --sort=priority   # High priority, sorted
jot list --due=today                        # Due today
jot list --due=overdue                      # Overdue items
jot list --json --limit=10                 # Machine-readable, limited
jot list --verbose                          # Show status, priority, tags columns
jot list --search="GraphQL" --type=note    # Content search within list

# Search content (dedicated full-text search)
jot search "GraphQL implementation"
jot search "authentication" --type=task --context=3
jot search "api" --tags=backend --status=open --json
jot search "caching" --fuzzy               # Fuzzy matching

# Tags (enriched summaries: TAG, COUNT, TYPES, OPEN, DONE, LATEST)
jot tags                                    # All tags with counts and status breakdown
jot tags api                                # Entries tagged 'api' (delegates to list)
jot tags --fuzzy api                        # Fuzzy tag matching with summaries
jot tags --json                             # JSON output

# Show a single entry
jot show api-redesign                       # Partial slug match, rendered markdown
jot show api-redesign --json                # Full JSON output
jot show api-redesign --raw                 # Raw markdown (no terminal rendering)
jot show api-redesign --json --meta         # Include sidecar metadata
```

### List Filter Flags

All filter flags on the `list` command (alias: `ls`):

- `--type`/`-t` — Filter by type (idea/task/note/plan/log)
- `--status`/`-s` — Filter by status (open/in_progress/done/blocked/archived)
- `--tags` — Filter by tag (comma-separated)
- `--priority`/`-p` — Filter by priority (low/medium/high/critical)
- `--since` — Entries created since (7d, 2w, 2024-01-01)
- `--until` — Entries created until (date or YYYY-MM-DD)
- `--due`/`-d` — Filter by due date (today, week, overdue, or specific date)
- `--search`/`-q` — Content search within filtered results
- `--sort` — Sort field (created, modified, title, priority). Default: created descending
- `--limit`/`-n` — Limit number of results
- `--reverse`/`-r` — Reverse sort order (ascending)
- `--verbose`/`-v` — Show all columns (status, priority, due)

Filters are AND-combined. Default sort is by creation date, newest first.

### Search Flags

The `search` command takes a positional query argument and supports:

- `--type`/`-t` — Filter by type
- `--tags` — Filter by tag
- `--status`/`-s` — Filter by status
- `--priority`/`-p` — Filter by priority
- `--context`/`-C` — Lines of context around content matches (integer)

Search is case-insensitive and matches against titles and content. Results show the slug, title, and matching lines with highlights.

### Modify

```bash
# Change status
jot status api-redesign in_progress
jot status api-redesign done
jot status api-redesign blocked

# Edit in editor
jot edit api-redesign                       # Partial slug match, opens $EDITOR
```

The `status` command takes two positional arguments: slug and new status. Valid statuses: open, in_progress, done, blocked, archived. The `edit` command opens the entry file in the configured editor and updates the modified timestamp on save.

### Lifecycle

```bash
# Find stale entries (active but not recently modified)
jot stale                                   # Not modified in 90 days
jot stale --days 30 --type=idea            # Stale ideas, 30-day threshold
jot stale --tags=api --json                # Stale API entries, JSON output

# Bulk archive
jot archive --stale                         # Preview stale entries to archive
jot archive --stale --confirm              # Execute archive
jot archive --stale --days 30 --confirm    # Archive entries stale 30+ days
jot archive --older-than 6m               # Preview entries older than 6 months
jot archive --status done --confirm        # Archive all done entries
jot archive --stale --type=idea            # Only stale ideas

# Purge (permanently delete archived entries)
jot purge --all                             # Preview what would be purged
jot purge --all --force                    # Purge with interactive confirmation
jot purge --all --force --yes              # Purge without interactive prompt
jot purge --older-than 6m --force          # Purge old archived entries
jot purge --all --type=note --force        # Purge only archived notes

# Remove a single entry
jot rm api-redesign                         # Partial slug match, confirms
jot rm api-redesign --yes                  # Skip confirmation
```

The `stale` command finds active entries (not done/archived) that have not been modified within the threshold. Default threshold is 90 days. Sorted by modified date ascending (stalest first).

The `archive` command requires one mode flag: `--stale`, `--older-than`, or `--status`. It is dry-run by default and shows what would change. Use `--confirm` to execute. Narrowing flags `--type` and `--tags` combine with any mode.

The `purge` command requires one mode flag: `--all` or `--older-than`. It only targets entries with status "archived". Requires `--force` to execute, with interactive confirmation. Add `--yes`/`-y` to skip the interactive prompt. Narrowing flags `--type` and `--tags` are supported.

The `rm` command (aliases: `remove`, `delete`) permanently deletes a single entry, its sidecar metadata, and asset directory. Confirms by default; use `--yes`/`-y` to skip.

### Data — Import and Export

```bash
# Export
jot export > backup.json                    # JSON export (default)
jot export --markdown > backup.md          # Markdown export
jot export --type=task --status=open       # Filtered export

# Import
jot import backup.json                      # Import from export file
cat backup.json | jot import -             # Import from stdin
jot import backup.json --dry-run           # Preview without importing
jot import backup.json --skip-existing     # Skip duplicates
```

### Admin

```bash
# Journal info
jot which                                   # Show active journal (name, path, scope)
jot which --json                           # JSON output
jot init                                    # Initialize journal in current directory
jot init /path/to/project                  # Initialize in specific directory

# Configuration
jot config                                  # Show full config
jot config editor                          # Get a setting
jot config set editor "code -w"            # Set a setting
jot config set output.format json          # Set default output format

# Validation
jot lint                                    # Lint all entries
jot lint api-redesign                      # Lint specific entry
jot lint --json                            # JSON output
```

## Slug Resolution

Partial slug matching works on `show`, `status`, `edit`, `rm`, and `lint` commands. Provide any substring of the slug (e.g., `api-redesign` instead of `20240102-api-redesign`). If multiple entries match, the user is prompted to select one. A single match resolves silently.

## Workflow Patterns

**Project context check** — find everything related to a project:

```bash
jot tags --fuzzy <project-name> --json      # Discover project tags
jot list --tags=<tag> --status=open --json   # Open items for project
jot search "<project-name>" --json           # Content mentioning project
```

**Quick triage** — review what needs attention:

```bash
jot list --type=task --status=open --json    # All open tasks
jot list --due=overdue --json                # Overdue items
jot stale --days 30                          # Forgotten items
jot tags                                     # Tag overview with open/done counts
```

**Capture workflow** — add entries and tag them:

```bash
jot add "idea text" --type=idea --tags=project
jot add "task text" --type=task --tags=project --priority=high --due=1w
jot add "meeting notes" --type=log --tags=project,meetings
```

**End-of-sprint cleanup** — archive completed work:

```bash
jot archive --status done --confirm          # Archive done entries
jot archive --stale --days 60 --confirm     # Archive forgotten items
jot purge --older-than 6m --force --yes     # Clean up old archived entries
```

## Important Notes

- Always prefer `--json` output when parsing results programmatically.
- Tags are the primary project-scoping mechanism. Use tags to find and group project-related entries.
- The `tags` command provides enriched summaries showing TAG, COUNT, TYPES (with breakdown), OPEN, DONE, and LATEST modification date for each tag.
- The `--fuzzy` flag enables Levenshtein-based fuzzy matching for tags and search. Use it when the exact tag name or search term is uncertain.
- Due dates accept relative formats: `3d` (3 days), `1w` (1 week), `today`, `tomorrow`, and absolute dates as `YYYY-MM-DD`.
- Duration strings for `--since`, `--older-than`, etc. accept: `7d` (days), `2w` (weeks), `6m` (months), `1y` (years).
- The list command defaults to descending order (newest first). Use `--reverse` for ascending.
- The `archive` and `purge` commands are safe by default: archive is dry-run without `--confirm`, purge requires both `--force` and interactive confirmation (or `--yes`).
