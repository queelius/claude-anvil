# mf Command Reference

Complete reference for all mf commands and options.

> **Cross-repo note:** All paths below are relative to `~/github/repos/metafunctor` (the site root). When running from another directory, use `MF_SITE_ROOT=~/github/repos/metafunctor` or `cd` to the site root first.

## mf init

Initialize the `.mf/` directory structure.

```bash
mf init [OPTIONS]
```

**Options:**
- `-f, --force` - Overwrite existing .mf/ directory

## mf papers

Paper database and Hugo content management.

### mf papers process

Process a LaTeX file and add to database.

```bash
mf papers process PATH [OPTIONS]
```

**Arguments:**
- `PATH` - Path to LaTeX file

**Options:**
- `--slug TEXT` - Override auto-generated slug
- `-f, --force` - Reprocess even if unchanged

### mf papers list

List papers in the database.

```bash
mf papers list [OPTIONS]
```

**Options:**
- `-q, --query TEXT` - Search in title/abstract
- `-t, --tag TEXT` - Filter by tag (repeatable)
- `-c, --category TEXT` - Filter by category
- `--featured` - Show only featured papers
- `--json` - Output as JSON

### mf papers sync

Check for stale papers and regenerate.

```bash
mf papers sync [OPTIONS]
```

**Options:**
- `-y, --yes` - Auto-regenerate without prompts
- `--slug TEXT` - Sync specific paper only

### mf papers generate

Generate Hugo content pages from database.

```bash
mf papers generate [OPTIONS]
```

**Options:**
- `--slug TEXT` - Generate specific paper only
- `-f, --force` - Regenerate all, even if unchanged

### mf papers stats

Show database statistics.

```bash
mf papers stats
```

### mf papers fields

List all valid paper fields and their types.

```bash
mf papers fields
```

Shows field name, type (string, int, bool, string_list, dict), description, and constraints (choices, min/max values).

### mf papers set

Set a paper field value.

```bash
mf papers set SLUG FIELD VALUE [OPTIONS]
```

**Arguments:**
- `SLUG` - Paper slug
- `FIELD` - Field name (use dot notation for dict sub-keys)
- `VALUE` - New value (auto-coerced to field type)

**Options:**
- `--regenerate` - Regenerate Hugo content after change

**Examples:**
```bash
mf papers set my-paper stars 5
mf papers set my-paper status published
mf papers set my-paper tags "stats,ml"
mf papers set my-paper venue "NeurIPS 2024"
```

### mf papers unset

Remove a paper field override.

```bash
mf papers unset SLUG FIELD [OPTIONS]
```

**Arguments:**
- `SLUG` - Paper slug
- `FIELD` - Field name to remove

**Options:**
- `--regenerate` - Regenerate Hugo content after change

**Examples:**
```bash
mf papers unset my-paper stars
mf papers unset my-paper venue
```

### mf papers feature

Toggle a paper's featured status.

```bash
mf papers feature SLUG [OPTIONS]
```

**Arguments:**
- `SLUG` - Paper slug

**Options:**
- `--off` - Remove from featured (default: add to featured)
- `--regenerate` - Regenerate Hugo content after change

**Examples:**
```bash
mf papers feature my-paper
mf papers feature my-paper --off
```

### mf papers tag

Manage paper tags.

```bash
mf papers tag SLUG [OPTIONS]
```

**Arguments:**
- `SLUG` - Paper slug

**Options:**
- `--add TEXT` - Tag to add (repeatable)
- `--remove TEXT` - Tag to remove (repeatable)
- `--set TEXT` - Replace all tags (comma-separated)
- `--regenerate` - Regenerate Hugo content after change

**Examples:**
```bash
mf papers tag my-paper --add statistics --add ml
mf papers tag my-paper --remove old-tag
mf papers tag my-paper --set "statistics,ml,optimization"
```

## mf projects

GitHub project import and content generation.

### mf projects import

Import repositories from a GitHub user.

```bash
mf projects import --user USERNAME [OPTIONS]
```

**Options:**
- `--user TEXT` - GitHub username (required)
- `--exclude-forks` - Skip forked repos
- `--exclude-archived` - Skip archived repos
- `--min-stars N` - Minimum star count
- `--language TEXT` - Filter by language (repeatable)
- `-f, --force` - Overwrite existing entries

### mf projects refresh

Update project data from GitHub API.

```bash
mf projects refresh [OPTIONS]
```

**Options:**
- `--slug TEXT` - Refresh specific project only
- `--older-than N` - Only if not synced in N hours
- `-f, --force` - Force refresh all

### mf projects generate

Generate Hugo content pages.

```bash
mf projects generate [OPTIONS]
```

**Options:**
- `--slug TEXT` - Generate specific project only
- `--rich-only` - Only rich projects (branch bundles)

### mf projects list

List projects in the database.

```bash
mf projects list [OPTIONS]
```

**Options:**
- `-q, --query TEXT` - Search in name/description
- `--featured` - Show only featured
- `--hidden` - Show only hidden
- `--rich` - Show only rich projects
- `--json` - Output as JSON

### mf projects clean

Remove projects that no longer exist on GitHub.

```bash
mf projects clean --user USERNAME [OPTIONS]
```

**Options:**
- `--user TEXT` - GitHub username
- `-f, --force` - Skip confirmation

### mf projects rate-limit

Check GitHub API rate limit status.

```bash
mf projects rate-limit
```

### mf projects fields

List all valid project fields and their types.

```bash
mf projects fields
```

Shows field name, type, description, and constraints. Supports dot notation for dict sub-keys (e.g., `packages.pypi`, `external_docs.mkdocs`).

### mf projects set

Set a project field value.

```bash
mf projects set SLUG FIELD VALUE [OPTIONS]
```

**Arguments:**
- `SLUG` - Project slug
- `FIELD` - Field name (supports dot notation for dict fields)
- `VALUE` - New value (auto-coerced to field type)

**Options:**
- `--regenerate` - Regenerate Hugo content after change

**Examples:**
```bash
mf projects set my-project stars 5
mf projects set my-project category library
mf projects set my-project tags "python,stats"
mf projects set my-project packages.pypi my-package
```

### mf projects unset

Remove a project field override.

```bash
mf projects unset SLUG FIELD [OPTIONS]
```

**Arguments:**
- `SLUG` - Project slug
- `FIELD` - Field name to remove (supports dot notation)

**Options:**
- `--regenerate` - Regenerate Hugo content after change

**Examples:**
```bash
mf projects unset my-project stars
mf projects unset my-project packages.pypi
```

### mf projects feature

Toggle a project's featured status.

```bash
mf projects feature SLUG [OPTIONS]
```

**Arguments:**
- `SLUG` - Project slug

**Options:**
- `--off` - Remove from featured (default: add to featured)
- `--regenerate` - Regenerate Hugo content after change

**Examples:**
```bash
mf projects feature my-project
mf projects feature my-project --off
```

### mf projects hide

Toggle a project's hidden status.

```bash
mf projects hide SLUG [OPTIONS]
```

**Arguments:**
- `SLUG` - Project slug

**Options:**
- `--off` - Unhide the project (default: hide)
- `--regenerate` - Regenerate Hugo content after change

**Examples:**
```bash
mf projects hide my-project
mf projects hide my-project --off
```

### mf projects tag

Manage project tags.

```bash
mf projects tag SLUG [OPTIONS]
```

**Arguments:**
- `SLUG` - Project slug

**Options:**
- `--add TEXT` - Tag to add (repeatable)
- `--remove TEXT` - Tag to remove (repeatable)
- `--set TEXT` - Replace all tags (comma-separated)
- `--regenerate` - Regenerate Hugo content after change

**Examples:**
```bash
mf projects tag my-project --add python --add stats
mf projects tag my-project --remove old-tag
mf projects tag my-project --set "python,stats,ml"
```

## mf content

Content-to-project linking.

### mf content match-projects

Find content that should be linked to projects.

```bash
mf content match-projects [OPTIONS]
```

**Options:**
- `-t, --threshold FLOAT` - Confidence threshold (0.0-1.0)
- `--type TEXT` - Content types to scan (repeatable)
- `-y, --yes` - Auto-apply without confirmation
- `--project TEXT` - Match for specific project only

### mf content about

Find all content about a specific project.

```bash
mf content about PROJECT_SLUG
```

### mf content list-projects

List projects with their content counts.

```bash
mf content list-projects [OPTIONS]
```

**Options:**
- `--min-count N` - Minimum content count to show

## mf series

Series management and synchronization with external source repositories.

### mf series list

List all series in the database.

```bash
mf series list [OPTIONS]
```

**Options:**
- `-q, --query TEXT` - Search in title/description
- `-t, --tag TEXT` - Filter by tag (repeatable)
- `-s, --status TEXT` - Filter by status (active, completed, archived)
- `--featured` - Show only featured series
- `--json` - Output as JSON

### mf series show

Show details for a specific series.

```bash
mf series show SLUG
```

**Arguments:**
- `SLUG` - Series slug

### mf series sync

Sync posts from external source repository.

```bash
mf series sync [SLUG] [OPTIONS]
```

**Arguments:**
- `SLUG` - Series slug (optional if using --all)

**Options:**
- `--all` - Sync all series with source_dir configured
- `--push` - Push metafunctor -> source (default is pull)
- `--posts-only` - Skip landing page sync
- `--landing-only` - Skip posts sync
- `--delete` - Delete posts removed from source
- `--dry-run` - Preview changes without syncing
- `-v, --verbose` - Show all posts, not just changes

**Examples:**
```bash
mf series sync stepanov           # Pull from source
mf series sync stepanov --dry-run # Preview changes
mf series sync stepanov --push    # Push to source
mf series sync --all              # Sync all configured series
```

### mf series add

Add content to a series by updating frontmatter.

```bash
mf series add SERIES_SLUG CONTENT_PATH
```

**Arguments:**
- `SERIES_SLUG` - Series to add content to
- `CONTENT_PATH` - Path to markdown file or directory

**Examples:**
```bash
mf series add stepanov content/post/2024-01-01-my-post/index.md
mf series add stepanov content/post/2024-01-01-my-post/
```

### mf series remove

Remove content from a series by updating frontmatter.

```bash
mf series remove SERIES_SLUG CONTENT_PATH
```

**Arguments:**
- `SERIES_SLUG` - Series to remove content from
- `CONTENT_PATH` - Path to markdown file or directory

### mf series scan

Scan content for series usage and report statistics.

```bash
mf series scan [OPTIONS]
```

**Options:**
- `--include-orphans` - Show posts with series not in DB

### mf series stats

Show series database statistics.

```bash
mf series stats
```

### mf series fields

List all valid series fields and their types.

```bash
mf series fields
```

Shows field name, type, description, and constraints (e.g., status choices: active, completed, archived).

### mf series set

Set a series field value.

```bash
mf series set SLUG FIELD VALUE
```

**Arguments:**
- `SLUG` - Series slug
- `FIELD` - Field name (supports dot notation for dict fields)
- `VALUE` - New value (auto-coerced to field type)

**Examples:**
```bash
mf series set my-series status completed
mf series set my-series color "#ff6b6b"
mf series set my-series tags "math,computing"
```

### mf series unset

Remove a series field override.

```bash
mf series unset SLUG FIELD
```

**Arguments:**
- `SLUG` - Series slug
- `FIELD` - Field name to remove

**Examples:**
```bash
mf series unset my-series color
mf series unset my-series icon
```

### mf series feature

Toggle a series' featured status.

```bash
mf series feature SLUG [OPTIONS]
```

**Arguments:**
- `SLUG` - Series slug

**Options:**
- `--off` - Remove from featured (default: add to featured)

**Examples:**
```bash
mf series feature my-series
mf series feature my-series --off
```

### mf series tag

Manage series tags.

```bash
mf series tag SLUG [OPTIONS]
```

**Arguments:**
- `SLUG` - Series slug

**Options:**
- `--add TEXT` - Tag to add (repeatable)
- `--remove TEXT` - Tag to remove (repeatable)
- `--set TEXT` - Replace all tags (comma-separated)

**Examples:**
```bash
mf series tag my-series --add math --add computing
mf series tag my-series --remove old-tag
mf series tag my-series --set "math,computing,philosophy"
```

## mf posts

Blog post management — convenience layer over Hugo content files. No database; front matter is the source of truth.

### mf posts list

List blog posts with optional filters.

**Options:**
- `-q, --query TEXT` — Full-text search in title/body
- `-t, --tag TAG` — Filter by tag (repeatable)
- `-c, --category CAT` — Filter by category (repeatable)
- `--series SLUG` — Filter by series slug
- `--featured` — Only featured posts
- `--include-drafts` — Include draft posts
- `--since DATE` — Only posts since date (YYYY-MM-DD or 30d/4w/3m)
- `--json` — Output as JSON array

**Examples:**
```bash
mf posts list                           # All published posts
mf posts list --tag python --tag ml     # Posts tagged python OR ml
mf posts list --series stepanov         # Posts in stepanov series
mf posts list --featured --since 3m     # Featured posts from last 3 months
mf posts list --json                    # JSON for scripting
mf posts list -q "bloom filter"         # Full-text search
mf posts list --include-drafts          # Include drafts
```

### mf posts create

Scaffold a new blog post at `content/post/YYYY-MM-DD-slug/index.md`.

**Options:**
- `--title TEXT` — Post title (required)
- `--slug TEXT` — URL slug (auto-generated from title if omitted)
- `--date TEXT` — Post date YYYY-MM-DD (default: today)
- `-t, --tag TAG` — Tags (repeatable)
- `-c, --category CAT` — Categories (repeatable)
- `-s, --series SLUG` — Series membership (repeatable)
- `--description TEXT` — Card preview text
- `--featured` — Mark as featured

**Examples:**
```bash
mf posts create --title "My New Post"
mf posts create --title "Tagged" --tag python --tag ml --category AI
mf posts create --title "Series Post" --series stepanov
mf posts create --title "With Desc" --description "A short summary"
```

### mf posts set

Set a front matter field on a post. Values are auto-coerced.

```bash
mf posts set <slug> <field> <value>
```

**Examples:**
```bash
mf posts set 2024-01-15-my-post description "New description"
mf posts set my-post featured true
mf posts set my-post series_weight 5
```

### mf posts unset

Remove a front matter field from a post.

```bash
mf posts unset <slug> <field>
```

**Examples:**
```bash
mf posts unset my-post featured
mf posts unset my-post description
```

### mf posts tag

Manage tags on a post.

**Options:**
- `--add TAG` — Add tag (repeatable)
- `--remove TAG` — Remove tag (repeatable)
- `--set TAGS` — Replace all tags (comma-separated)

**Examples:**
```bash
mf posts tag my-post --add python --add ml
mf posts tag my-post --remove old-tag
mf posts tag my-post --set "python,ml,statistics"
```

### mf posts feature

Toggle featured status on a post.

**Options:**
- `--off` — Remove featured status

**Examples:**
```bash
mf posts feature my-post          # Mark as featured
mf posts feature my-post --off    # Remove featured
```

## mf taxonomy

Taxonomy analysis and normalization across all content.

### mf taxonomy audit

Find near-duplicate taxonomy terms (case mismatches, plural variants, etc.).

```bash
mf taxonomy audit [OPTIONS]
```

**Options:**
- `--json` - Output as JSON

**Examples:**
```bash
mf taxonomy audit                # Rich table of near-duplicates
mf taxonomy audit --json         # JSON array of issues
```

**Output fields (JSON):**
- `term_a`, `term_b` - The near-duplicate pair
- `type` - Duplicate type: `case_mismatch`, `plural_variant`, etc.
- `taxonomy` - `tags` or `categories`

### mf taxonomy orphans

Find tags and categories used by only one post (or fewer than a threshold).

```bash
mf taxonomy orphans [OPTIONS]
```

**Options:**
- `--min-count N` - Minimum usage count to be "healthy" (default: 2)
- `--json` - Output as JSON

**Examples:**
```bash
mf taxonomy orphans                # Tags/categories used only once
mf taxonomy orphans --min-count 3  # Used fewer than 3 times
mf taxonomy orphans --json         # JSON dict with tags/categories keys
```

**Output (JSON):**
```json
{
  "tags": ["rare-tag-1", "rare-tag-2"],
  "categories": ["rare-category"]
}
```

### mf taxonomy stats

Show taxonomy frequency distribution and co-occurrence data.

```bash
mf taxonomy stats [OPTIONS]
```

**Options:**
- `--limit N` - Limit top results shown (default: 50)
- `--json` - Output as JSON

**Examples:**
```bash
mf taxonomy stats                # Top 50 tags and categories
mf taxonomy stats --limit 10    # Top 10 only
mf taxonomy stats --json        # Full stats as JSON
```

**Output fields (JSON):**
- `tags` - Array of `{"tag": name, "count": N}` sorted by count descending
- `categories` - Array of `{"category": name, "count": N}` sorted by count descending
- `co_occurrences` - Dict of `"tag_a+tag_b": count` for frequently co-occurring tags
- `total_tags`, `total_categories`, `total_tag_usages`, `total_category_usages` - Aggregate totals

### mf taxonomy normalize

Rename a tag or category across all content files.

```bash
mf taxonomy normalize --from TEXT --to TEXT [OPTIONS]
```

**Options:**
- `--from TEXT` - Source term to rename (required)
- `--to TEXT` - Target term (required)
- `--dry-run` - Preview changes without modifying files
- `--yes` - Skip confirmation prompt

**Examples:**
```bash
mf taxonomy normalize --from "Python" --to "python" --dry-run   # Preview
mf taxonomy normalize --from "Python" --to "python" --yes       # Apply
mf taxonomy normalize --from "ML" --to "machine-learning"       # Interactive
```

## mf health

Content health checks for links, descriptions, images, drafts, and stale projects.

### mf health links

Find broken internal links in content.

```bash
mf health links [OPTIONS]
```

**Options:**
- `--json` - Output as JSON

**Examples:**
```bash
mf health links          # Rich table of broken links
mf health links --json   # JSON array
```

**Output fields (JSON):**
- `slug` - Content slug
- `title` - Content title
- `link` - The broken link
- `content_type` - Content type (post, papers, projects, etc.)

### mf health descriptions

Find posts missing the `description` field (used for social cards and search).

```bash
mf health descriptions [OPTIONS]
```

**Options:**
- `--json` - Output as JSON

**Examples:**
```bash
mf health descriptions          # Rich table
mf health descriptions --json   # JSON array
```

**Output fields (JSON):**
- `slug` - Post slug
- `title` - Post title
- `content_type` - Always "post"

### mf health images

Find posts missing the `featured_image` field.

```bash
mf health images [OPTIONS]
```

**Options:**
- `--json` - Output as JSON

**Examples:**
```bash
mf health images          # Rich table
mf health images --json   # JSON array
```

**Output fields (JSON):**
- `slug` - Post slug
- `title` - Post title
- `content_type` - Always "post"

### mf health drafts

List all drafts with age, sorted by oldest first.

```bash
mf health drafts [OPTIONS]
```

**Options:**
- `--json` - Output as JSON

**Examples:**
```bash
mf health drafts          # Rich table with age
mf health drafts --json   # JSON array
```

**Output fields (JSON):**
- `slug` - Content slug
- `title` - Content title
- `date` - Front matter date string
- `days_old` - Age in days
- `content_type` - Content type

### mf health stale

Find projects where the content description has diverged from the database description.

```bash
mf health stale [OPTIONS]
```

**Options:**
- `--json` - Output as JSON

**Examples:**
```bash
mf health stale          # Rich table with both descriptions
mf health stale --json   # JSON array
```

**Output fields (JSON):**
- `slug` - Project slug
- `title` - Project title
- `content_desc` - Description in the content file
- `db_desc` - Description in projects_db.json

## mf backup

Database backup management.

### mf backup list

List available backups.

```bash
mf backup list [OPTIONS]
```

**Options:**
- `-d, --db [paper_db|projects_db|all]` - Which database
- `-n, --limit N` - Max backups to show
- `--all` - Show all (no limit)

### mf backup status

Show backup health and statistics.

```bash
mf backup status
```

### mf backup rollback

Restore from a backup.

```bash
mf backup rollback DATABASE [OPTIONS]
```

**Arguments:**
- `DATABASE` - Which database (`paper_db` or `projects_db`)

**Options:**
- `-i, --index N` - Backup index (0=most recent, 1=second most recent, etc.)
- `-f, --force` - Skip confirmation

### mf backup clean

Remove old backups.

```bash
mf backup clean [OPTIONS]
```

**Options:**
- `--older-than N` - Remove backups older than N days
- `-f, --force` - Skip confirmation

## mf config

Configuration management.

### mf config show

Show current configuration.

```bash
mf config show [OPTIONS]
```

**Options:**
- `--all` - Show all settings including defaults

### mf config get

Get a specific configuration value.

```bash
mf config get KEY
```

### mf config set

Set a configuration value.

```bash
mf config set KEY VALUE
```

### mf config reset

Reset configuration to defaults.

```bash
mf config reset [KEY] [OPTIONS]
```

**Options:**
- `--all` - Reset all settings
- `-f, --force` - Skip confirmation

## mf claude

Claude Code skill management.

### mf claude install

Install the mf skill.

```bash
mf claude install [OPTIONS]
```

**Options:**
- `-f, --force` - Overwrite existing installation

### mf claude uninstall

Remove the mf skill.

```bash
mf claude uninstall [OPTIONS]
```

**Options:**
- `-f, --force` - Skip confirmation

### mf claude status

Check skill installation status.

```bash
mf claude status
```

## mf content audit

Audit linked_project references in content.

```bash
mf content audit [OPTIONS]
```

**Options:**
- `-t, --type TEXT` - Content types to audit (default: post, papers, writing)
- `--include-drafts` - Include draft content in audit
- `--fix` - Remove broken linked_project entries
- `-n, --dry-run` - Preview fixes without making changes
- `--json` - Output as JSON
- `-v, --verbose` - Show detailed information
- `--summary-only` - Only show statistics

**Extended Audit Options:**
- `--extended` - Run extended audit checks (required_fields, date_format, etc.)
- `--list-checks` - List available audit checks and exit
- `--check TEXT` - Comma-separated list of checks to run
- `--severity [error|warning|info]` - Minimum severity level to report

**Examples:**
```bash
mf content audit                    # Full audit
mf content audit --type post        # Only audit posts
mf content audit --fix --dry-run    # Preview fixes
mf content audit --fix              # Apply fixes
mf content audit --json             # Machine-readable output
mf content audit --summary-only     # Quick stats only
mf content audit --list-checks      # Show available checks
mf content audit --extended         # Run extended checks
mf content audit --check required_fields,stale_drafts
mf content audit --severity warning # Min severity level
```

## mf analytics

Content analytics and insights.

### mf analytics projects

Show projects ranked by linked content count.

```bash
mf analytics projects [OPTIONS]
```

**Options:**
- `--json` - Output as JSON
- `-n, --limit INTEGER` - Limit number of results
- `--include-hidden` - Include hidden projects
- `--include-drafts` - Include draft content

**Examples:**
```bash
mf analytics projects              # All projects ranked by content
mf analytics projects --limit 10   # Top 10 projects
mf analytics projects --json       # JSON output
```

### mf analytics gaps

Find projects without any linked content.

```bash
mf analytics gaps [OPTIONS]
```

**Options:**
- `--json` - Output as JSON
- `-n, --limit INTEGER` - Limit number of results
- `--with-mentions` - Show projects mentioned but not linked
- `--include-hidden` - Include hidden projects
- `--include-drafts` - Include draft content

**Examples:**
```bash
mf analytics gaps                  # Projects without content
mf analytics gaps --with-mentions  # Show where they're mentioned
mf analytics gaps --json           # JSON output
```

### mf analytics tags

Show tag usage distribution.

```bash
mf analytics tags [OPTIONS]
```

**Options:**
- `--json` - Output as JSON
- `-n, --limit INTEGER` - Limit number of results
- `--include-drafts` - Include draft content

**Examples:**
```bash
mf analytics tags              # Top 50 tags
mf analytics tags --limit 20   # Top 20 tags
mf analytics tags --json       # JSON output
```

### mf analytics timeline

Show content activity over time.

```bash
mf analytics timeline [OPTIONS]
```

**Options:**
- `--json` - Output as JSON
- `-m, --months INTEGER` - Number of months to show
- `--include-drafts` - Include draft content

**Examples:**
```bash
mf analytics timeline              # Last 12 months
mf analytics timeline --months 24  # Last 24 months
mf analytics timeline --json       # JSON output
```

### mf analytics suggestions

Suggest content that should be linked to projects.

```bash
mf analytics suggestions [OPTIONS]
```

**Options:**
- `--json` - Output as JSON
- `-n, --limit INTEGER` - Limit number of results
- `-t, --threshold FLOAT` - Minimum confidence threshold (0.0-1.0)
- `--include-drafts` - Include draft content

**Examples:**
```bash
mf analytics suggestions              # Suggestions above 50% confidence
mf analytics suggestions --threshold 0.7  # Higher confidence only
mf analytics suggestions --json       # JSON output
```

### mf analytics summary

Show full analytics overview.

```bash
mf analytics summary [OPTIONS]
```

**Options:**
- `--json` - Output as JSON
- `--include-drafts` - Include draft content

**Examples:**
```bash
mf analytics summary       # Full overview
mf analytics summary --json  # JSON output
```

## mf integrity

Database integrity checking and repair.

### mf integrity check

Run integrity checks on databases.

```bash
mf integrity check [OPTIONS]
```

**Options:**
- `--db TEXT` - Check specific database (paper_db, projects_db, projects_cache, series_db)
- `--json` - Output as JSON
- `-v, --verbose` - Show detailed information

**Examples:**
```bash
mf integrity check                 # Full check
mf integrity check --db paper_db   # Check specific database
mf integrity check --json          # JSON output
```

### mf integrity fix

Fix auto-fixable integrity issues.

Currently fixes:
- Stale cache entries (removes orphaned cache entries)
- Sync state orphans (clears sync state for non-existent posts)

```bash
mf integrity fix [OPTIONS]
```

**Options:**
- `--db TEXT` - Fix specific database only
- `-n, --dry-run` - Preview fixes without making changes
- `-y, --yes` - Apply fixes without confirmation
- `--json` - Output as JSON

**Examples:**
```bash
mf integrity fix --dry-run    # Preview fixes
mf integrity fix -y           # Apply fixes without confirmation
mf integrity fix --db projects_cache  # Fix specific database
```

### mf integrity orphans

Find orphaned entries across databases.

Shows entries that exist in databases but have no corresponding content files.

```bash
mf integrity orphans [OPTIONS]
```

**Options:**
- `--json` - Output as JSON
- `-v, --verbose` - Show detailed information

**Examples:**
```bash
mf integrity orphans           # Find orphans
mf integrity orphans --json    # JSON output
```
