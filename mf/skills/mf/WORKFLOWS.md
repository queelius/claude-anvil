# mf Workflows

Step-by-step guides for common tasks.

> **Cross-repo note:** With global config set up (`~/.config/mf/config.yaml`), all commands work from any directory. Otherwise, use `MF_SITE_ROOT=~/github/repos/metafunctor` or `cd` to the site root.

## Post Workflows

### Creating a New Post

```bash
# 1. Scaffold the post (works from any directory with global config)
mf posts create --title "My New Post" --tag python --category Programming

# 2. Edit the content
# (open content/post/YYYY-MM-DD-my-new-post/index.md in your editor)

# 3. Remove draft flag when ready
mf posts set YYYY-MM-DD-my-new-post draft false

# 4. Deploy
make deploy

# 5. Cross-post (see /crier skill)
crier publish content/post/YYYY-MM-DD-my-new-post/index.md
```

### Finding and Filtering Posts

```bash
# Recent posts
mf posts list --since 30d

# Posts in a series
mf posts list --series stepanov

# Featured posts
mf posts list --featured

# Search by keyword
mf posts list -q "bloom filter"

# Multiple filters
mf posts list --tag python --since 3m

# JSON output for scripting
mf posts list --json
```

### Managing Post Metadata

```bash
# Set description for social cards
mf posts set my-post description "A short summary"

# Add tags
mf posts tag my-post --add python --add algorithms

# Replace all tags
mf posts tag my-post --set "python,ml,statistics"

# Feature a post
mf posts feature my-post

# Unfeature
mf posts feature my-post --off

# Remove a field entirely
mf posts unset my-post description
```

## Paper Workflows

### Adding a New Paper

When you have a new LaTeX paper to add:

```bash
# 1. Process the LaTeX source
mf papers process ~/latex/my-paper/main.tex

# 2. Verify it was added
mf papers list -q "my paper"

# 3. Generate Hugo page
mf papers generate --slug my-paper

# 4. Preview the site
make serve
```

### Updating an Existing Paper

When the LaTeX source has changed:

```bash
# Check if paper is stale
mf papers sync

# Or force regenerate
mf papers process ~/latex/my-paper/main.tex --force
mf papers generate --slug my-paper
```

### Bulk Paper Sync

Check and update all papers:

```bash
# Preview what would change
mf --dry-run papers sync

# Apply changes
mf papers sync --yes
```

## Project Workflows

### Initial Project Import

Import all your GitHub repositories:

```bash
# Check rate limit first
mf projects rate-limit

# Import (exclude forks, require at least 1 star)
mf projects import --user queelius --exclude-forks --min-stars 1

# Generate Hugo pages
mf projects generate
```

### Regular Project Sync

Keep project pages updated:

```bash
# Refresh only stale projects (not synced in 24 hours)
mf projects refresh --older-than 24

# Regenerate pages
mf projects generate
```

### Adding a Rich Project

Create a project with subsections (docs, tutorials, examples):

```bash
# 1. Edit projects_db.json to mark as rich
# Add: "rich_project": true, "content_sections": ["docs", "tutorials"]

# 2. Generate the bundle structure
mf projects generate --slug my-project

# 3. Edit the generated pages
# - content/projects/my-project/_index.md (main)
# - content/projects/my-project/docs/_index.md
# - content/projects/my-project/tutorials/_index.md
```

### Featuring Projects

Update which projects are featured:

```bash
# List current featured
mf projects list --featured

# Feature a project (updates projects_db.json and optionally regenerates)
mf projects feature my-project --regenerate

# Unfeature a project
mf projects feature my-project --off --regenerate
```

## Content Linking Workflows

### Auto-Link Content to Projects

Find posts that mention projects and link them:

```bash
# Preview matches
mf content match-projects --threshold 0.6

# Auto-apply high-confidence matches
mf content match-projects --threshold 0.8 --yes

# Or match for a specific project
mf content match-projects --project ctk
```

### Find Content About a Project

See what's already linked:

```bash
mf content about likelihood.model
```

### Manual Content Linking

Edit post front matter directly:

```yaml
# In content/post/2024-01-my-post/index.md
---
title: "My Post"
linked_project:
  - "likelihood.model"
  - "algebraic.mle"
---
```

**Important:** Use `linked_project` (not `projects`) and use slugs (not paths).

## Series Workflows

### Syncing a Series from External Repo

Sync posts from an external series repository (like the stepanov series):

```bash
# Preview changes first
mf series sync stepanov --dry-run

# Pull posts from source
mf series sync stepanov

# Or sync all series with source_dir configured
mf series sync --all
```

### Pushing Changes to Source Repo

If you've edited posts in metafunctor and want to push back:

```bash
# Preview what would be pushed
mf series sync stepanov --push --dry-run

# Push changes to source repo
mf series sync stepanov --push
```

### Adding Posts to a Series

Add existing posts to a series:

```bash
# Add a post to the stepanov series
mf series add stepanov content/post/2024-01-01-my-post/

# Or specify the index.md directly
mf series add stepanov content/post/2024-01-01-my-post/index.md
```

### Removing Posts from a Series

```bash
mf series remove stepanov content/post/2024-01-01-my-post/
```

### Checking Series Health

```bash
# Show all series and their post counts
mf series list

# Show details for a specific series
mf series show stepanov

# Scan for orphaned series references
mf series scan
```

### Adding Associations to a Series

Edit `series_db.json` to add associations to papers, media, and external links:

```json
{
  "stepanov": {
    "title": "Stepanov: Generic Programming in C++",
    "associations": {
      "papers": ["stepanov-whitepaper"],
      "media": ["stepanov-lectures-a9"],
      "links": [
        {"name": "Alex Stepanov's Site", "url": "http://stepanovpapers.com/"}
      ]
    }
  }
}
```

## Field Operations Workflows

All three domains (papers, projects, series) share a consistent set of field commands
built on the same core infrastructure (`core/field_ops.py`).

### Discovering Available Fields

Each domain has its own schema. Use `fields` to see what's available:

```bash
mf papers fields       # Paper fields (title, stars, status, venue, tags, ...)
mf projects fields     # Project fields (category, stars, featured, hide, packages.pypi, ...)
mf series fields       # Series fields (status, featured, color, icon, tags, ...)
```

### Setting and Removing Fields

```bash
# Set a field value (auto-coerced to correct type)
mf papers set my-paper stars 5
mf projects set my-project category library
mf series set my-series status completed

# Use dot notation for nested dict fields (projects only)
mf projects set my-project packages.pypi my-package
mf projects set my-project external_docs.mkdocs "https://..."

# Remove a field override
mf papers unset my-paper venue
mf projects unset my-project stars
mf series unset my-series color
```

### Featuring and Hiding

```bash
# Feature content across all domains
mf papers feature my-paper
mf projects feature my-project
mf series feature my-series

# Unfeature
mf papers feature my-paper --off
mf projects feature my-project --off
mf series feature my-series --off

# Hide projects from listings (projects-only)
mf projects hide my-project
mf projects hide my-project --off
```

### Managing Tags

```bash
# Add tags (repeatable)
mf papers tag my-paper --add statistics --add ml
mf projects tag my-project --add python --add stats
mf series tag my-series --add math --add computing

# Remove tags
mf papers tag my-paper --remove old-tag

# Replace all tags
mf projects tag my-project --set "python,stats,ml"
```

### Regenerating After Changes

Papers and projects support `--regenerate` to update Hugo content after a field change:

```bash
# Set and regenerate in one step
mf papers set my-paper stars 5 --regenerate
mf projects feature my-project --regenerate

# Or regenerate separately
mf papers set my-paper stars 5
mf papers generate --slug my-paper
```

Series do not have `--regenerate` since series content is managed via `sync` or manual editing.

### Typical Field Operations Pattern

```bash
# 1. Check available fields
mf projects fields

# 2. Set the value
mf projects set my-project category library

# 3. Optionally regenerate Hugo content
mf projects generate --slug my-project

# 4. Preview the site
make serve
```

## Taxonomy Hygiene Workflow

### Auditing Taxonomy Health

Find and fix inconsistent tags and categories:

```bash
# 1. Check for near-duplicates (case mismatches, plurals)
mf taxonomy audit

# 2. Review the results — common issues:
#    - "Python" vs "python" (case mismatch)
#    - "algorithm" vs "algorithms" (plural variant)

# 3. Preview a normalization
mf taxonomy normalize --from "Python" --to "python" --dry-run

# 4. Apply the fix
mf taxonomy normalize --from "Python" --to "python" --yes

# 5. Verify the fix
mf taxonomy audit
```

### Finding Orphan Tags

Clean up rarely-used tags:

```bash
# 1. Find tags used only once
mf taxonomy orphans

# 2. Or with a higher threshold
mf taxonomy orphans --min-count 3

# 3. Decide for each orphan:
#    - Normalize to an existing tag (mf taxonomy normalize)
#    - Keep it (if intentionally unique)
#    - Remove it (edit the front matter directly)

# 4. Check tag frequency distribution
mf taxonomy stats --limit 20
```

### Full Taxonomy Cleanup

Complete taxonomy hygiene pass:

```bash
# 1. Get the full picture
mf taxonomy stats
mf taxonomy audit
mf taxonomy orphans

# 2. Normalize duplicates (repeat for each pair)
mf taxonomy normalize --from "Source" --to "target" --dry-run
mf taxonomy normalize --from "Source" --to "target" --yes

# 3. Rebuild and verify
hugo --gc --minify
make serve    # Spot-check /tags/ and /categories/ pages
```

## Content Health Workflow

### Running All Health Checks

Comprehensive content health audit:

```bash
# 1. Check for broken internal links
mf health links

# 2. Find posts missing descriptions (important for SEO/social cards)
mf health descriptions

# 3. Find posts missing featured images
mf health images

# 4. List stale drafts
mf health drafts

# 5. Check project description sync
mf health stale
```

### Fixing Broken Links

When `mf health links` reports issues:

```bash
# 1. Get the list in JSON for scripting
mf health links --json

# 2. For each broken link, determine the fix:
#    - Typo in path: edit the markdown
#    - Content was moved: update the path
#    - Content was deleted: remove the link
#    - External link marked as internal: add https://

# 3. Verify fixes
mf health links
```

### Fixing Missing Descriptions

Posts without descriptions don't render well in social cards or search results:

```bash
# 1. Find posts missing descriptions
mf health descriptions

# 2. Fix each one
mf posts set <slug> description "A concise summary of the post"

# 3. Verify
mf health descriptions
```

### Pre-Deploy Health Check

Run before every deployment:

```bash
# Quick health check
mf health links && mf health descriptions && mf taxonomy audit

# Full validation
hugo --gc --minify
mf integrity check
mf health links
mf health descriptions
mf taxonomy audit

# Deploy
make deploy
```

## Backup Workflows

### Check Backup Health

```bash
mf backup status
```

### Restore from Backup

If something goes wrong:

```bash
# List recent backups
mf backup list --db paper_db

# Preview restore (dry run)
mf --dry-run backup rollback paper_db

# Restore most recent backup
mf backup rollback paper_db

# Or restore specific backup
mf backup rollback paper_db -i 2  # Third most recent
```

### Clean Old Backups

```bash
# Preview cleanup
mf backup clean --older-than 30 --dry-run

# Apply cleanup
mf backup clean --older-than 30
```

## Content Analytics Workflow

### Understanding Content-Project Relationships

Get a full picture of your site's content coverage:

```bash
# 1. Start with a full overview
mf analytics summary

# 2. Find projects that need more content
mf analytics gaps

# 3. See which projects have the most coverage
mf analytics projects --limit 10
```

### Finding Linking Opportunities

Discover content that should be linked to projects:

```bash
# 1. Get suggestions for content-project links
mf analytics suggestions

# 2. Filter to high-confidence matches only
mf analytics suggestions --threshold 0.7

# 3. Apply suggestions using match-projects
mf content match-projects --threshold 0.7

# 4. Or apply automatically
mf content match-projects --threshold 0.8 --yes
```

### Content Velocity Analysis

Track content creation over time:

```bash
# View last 12 months of activity
mf analytics timeline

# Extended view
mf analytics timeline --months 24

# Check tag distribution
mf analytics tags --limit 20
```

## Database Maintenance Workflow

### Regular Health Checks

Run these periodically to maintain database health:

```bash
# 1. Check all databases for issues
mf integrity check

# 2. View detailed information
mf integrity check --verbose

# 3. Check specific database
mf integrity check --db projects_cache
```

### Fixing Integrity Issues

When issues are found:

```bash
# 1. Preview what would be fixed
mf integrity fix --dry-run

# 2. Review the proposed changes

# 3. Apply fixes
mf integrity fix -y

# 4. Verify fixes applied
mf integrity check
```

### Finding Orphaned Entries

Entries in databases that lack corresponding content files:

```bash
# 1. Find all orphaned entries
mf integrity orphans

# 2. Review and decide:
#    - Delete orphaned database entries
#    - Regenerate missing content files

# 3. For papers, regenerate content:
mf papers generate --slug orphaned-paper

# 4. For projects, regenerate:
mf projects generate --slug orphaned-project
```

## Content Quality Audit Workflow

### Running Extended Audits

Use pluggable checks for content quality:

```bash
# 1. See available checks
mf content audit --list-checks

# 2. Run all extended checks
mf content audit --extended

# 3. Focus on specific checks
mf content audit --check required_fields,date_format

# 4. Filter by severity
mf content audit --severity error
```

### Fixing Audit Issues

When the audit finds problems:

```bash
# 1. Run audit with verbose output
mf content audit --extended --verbose

# 2. For linked_project issues, preview fixes
mf content audit --fix --dry-run

# 3. Apply fixes
mf content audit --fix

# 4. Re-run to verify
mf content audit --extended
```

### Targeted Content Type Audits

Audit specific content types:

```bash
# Audit only posts
mf content audit --type post --extended

# Audit papers
mf content audit --type papers --extended

# Include drafts in audit
mf content audit --include-drafts --extended
```

## Initialization Workflow

### Setting Up mf in a New Project

```bash
# Initialize .mf/ directory
mf init

# Import projects from GitHub
mf projects import --user queelius

# Generate content
mf projects generate

# Install Claude skill (optional)
mf claude install
```

### Checking Project Status

```bash
# Verify .mf/ exists and paths are correct
mf config show --all

# Check databases
mf papers stats
mf projects list --json | head

# Check backups
mf backup status
```
