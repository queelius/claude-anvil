---
name: mf
description: Use mf (metafunctor) to manage papers, projects, series, and content for the metafunctor.com Hugo site. Also covers site architecture, taxonomies, front matter conventions, and the mf-to-crier publishing pipeline. Invoke from ANY repo — mf works globally.
---

# mf — Metafunctor Site Management

A CLI toolkit + site architecture guide for metafunctor.com. Works from any directory.

**Site root:** `~/github/repos/metafunctor`
**Site URL:** `https://metafunctor.com` (also `https://queelius.github.io/metafunctor`)
**Engine:** Hugo with Ananke theme
**Deployment:** `docs/` committed to master, served by GitHub Pages

## Site Architecture

### Content Sections

| Directory | Type | Notes |
|-----------|------|-------|
| `content/post/` | Blog posts | Date-prefixed dirs: `2024-01-slug/index.md` |
| `content/papers/` | Research papers | Generated from paper_db via `mf papers generate` |
| `content/publications/` | Peer-reviewed subset | Generated from paper_db via `mf pubs generate` |
| `content/projects/` | Software projects | Generated from projects_db via `mf projects generate` |
| `content/series/` | Multi-part series | Landing pages with `_index.md` |
| `content/writing/` | Fiction/creative | `writing_type: "novel"`, `"essay"`, `"short-story"` |
| `content/medical/` | Medical records | Custom sidebar layout, Chart.js for labs |
| `content/research/` | Research overviews | |
| `content/probsets/` | Problem sets | Organized by course |
| `content/media/` | Book/resource reviews | |

**Content type separation is strict:** fiction goes in `/writing`, not `/papers`.

### Taxonomies

| Taxonomy | URL | Purpose |
|----------|-----|---------|
| `tags` | `/tags/` | Technical keywords (kebab-case) |
| `categories` | `/categories/` | Broad content categories |
| `genres` | `/genres/` | Document types (paper, novel, etc.) |
| `series` | `/series/` | Multi-part content grouping |
| `linked_project` | `/linked-projects/` | Links content to projects |

**Critical:** Use `linked_project` (NOT `projects`) — URL must not conflict with `content/projects/`.
Use slugs, not paths:
```yaml
# Correct
linked_project: ["likelihood.model"]
# Wrong — causes Hugo panic
linked_project: ["/projects/likelihood.model/"]
```

### Front Matter Patterns

**Posts:**
```yaml
title: "Post Title"
date: 2026-02-13
description: "Card preview text"
categories: ["Computer Science"]
tags: ["algorithms", "data-structures"]
series: ["series-slug"]
series_weight: 5
featured: true
toc: true
```

**Papers:**
```yaml
title: "Paper Title"
stars: 5                  # Featured rating (1-5)
pdf_file: "paper.pdf"    # In static/latex/paper-name/
html_path: "/latex/paper-name/index.html"
authors: ["Author Name"]
abstract: "..."
```

**Projects:**
```yaml
title: "Project Name"
featured: true
project: { status: "active", type: "library", year_started: 2024 }
tech: { languages: ["Python"], topics: ["ml"] }
sources: { github: "https://..." }
packages: { pypi: "name", crates: "name" }
```

**Series membership (in posts):**
```yaml
series: ["minds-and-machines"]
series_weight: 5
```

### Bundle Types

- **Leaf bundle** (`index.md`): Most content. Self-contained page.
- **Branch bundle** (`_index.md`): Rich projects, series landing pages. Can have child pages.

Rich projects use `_index.md`. Regular projects use `index.md`.

### Build & Deploy

```bash
make serve          # Dev server with drafts (localhost:1313)
make build          # Build to public/ (testing)
make deploy         # Build to docs/ for production
make push           # Build + git push to GitHub Pages
```

`relativeURLs=true` — one build works on both domains.

## Content Source Model

| Content | Ground Truth | mf Role | Has Database? |
|---------|-------------|---------|---------------|
| Projects | GitHub repos | DB + overrides + generate | Yes (projects_db.json) |
| Papers | LaTeX sources | DB + sync + generate | Yes (paper_db.json) |
| Series | mf series_db | DB + sync + landing pages | Yes (series_db.json) |
| Posts | The .md file | `mf posts` (list, create, set, tag, feature) | No |
| Writing | The .md file | None | No |
| Medical | The .md file | None | No |

**Key principle:** Databases exist only for content whose ground truth lives elsewhere.

## mf CLI Reference

### Setup
```bash
cd ~/github/repos/metafunctor/scripts/mf && pip install -e .
```

### Papers
```bash
mf papers list                         # List all papers
mf papers generate                     # Regenerate content/papers/ from paper_db
mf papers generate --slug X            # Single paper
mf papers sync                         # Sync LaTeX sources to paper_db
mf papers set <slug> <field> <value>   # Set field (--regenerate)
mf papers feature <slug>               # Toggle featured (--off, --regenerate)
mf papers tag <slug> --add <tag>       # Manage tags (--add/--remove/--set)
mf papers fields                       # List valid fields
```

### Projects
```bash
mf projects list                       # List all projects
mf projects generate                   # Regenerate from projects_db + GitHub cache
mf projects sync                       # Full sync: clean, import, refresh, generate
mf projects refresh --slug X           # Refresh single project from GitHub
mf projects set <slug> <field> <val>   # Set field (--regenerate)
mf projects feature <slug>             # Toggle featured (--off, --regenerate)
mf projects hide <slug>                # Toggle hidden (--off, --regenerate)
mf projects tag <slug> --add <tag>     # Manage tags
mf projects bundle <slug>              # Generate rich project (docs/tutorials/examples)
mf projects fields                     # List valid fields
```

### Series
```bash
mf series list                         # List all series
mf series show <slug>                  # Show series details
mf series show <slug> --landing        # Display landing page content
mf series add <slug> <path>            # Add post to series
mf series sync <slug>                  # Sync with external source repo
mf series create <slug> --title "..."  # Create new series
mf series delete <slug>                # Remove from DB only
mf series delete <slug> --purge        # Remove DB + content + strip refs
mf series set <slug> <field> <value>   # Set field
mf series feature <slug>               # Toggle featured
mf series tag <slug> --add <tag>       # Manage tags
```

### Posts
```bash
mf posts list                          # List all posts
mf posts list --tag X --series Y       # Filter by tag/series
mf posts list --since 30d --featured   # Recent featured posts
mf posts list --json                   # JSON output for scripting
mf posts create --title "..." [opts]   # Scaffold new post
mf posts set <slug> <field> <value>    # Edit front matter in-place
mf posts unset <slug> <field>          # Remove front matter field
mf posts tag <slug> --add <tag>        # Manage tags (--add/--remove/--set)
mf posts feature <slug>               # Toggle featured (--off)
```

Hugo is the source of truth for posts — no database. `mf posts` provides convenience over front matter.

### Taxonomy
```bash
mf taxonomy audit                      # Find near-duplicate tags/categories
mf taxonomy audit --json               # JSON output
mf taxonomy orphans                    # Tags/categories used only once
mf taxonomy orphans --min-count N      # Custom threshold
mf taxonomy orphans --json             # JSON output
mf taxonomy stats                      # Tag/category frequency and co-occurrence
mf taxonomy stats --limit N            # Limit top results
mf taxonomy stats --json               # JSON output
mf taxonomy normalize --from X --to Y  # Rename a tag/category across all content
mf taxonomy normalize --dry-run        # Preview changes
```

### Health
```bash
mf health links                        # Find broken internal links
mf health links --json                 # JSON output
mf health descriptions                 # Posts missing description field
mf health descriptions --json          # JSON output
mf health images                       # Posts missing featured_image
mf health images --json                # JSON output
mf health drafts                       # List all drafts with age
mf health drafts --json                # JSON output
mf health stale                        # Projects where description diverged from DB
mf health stale --json                 # JSON output
```

### Publications
```bash
mf pubs generate                       # Regenerate content/publications/
mf pubs list                           # List publications
```

### Content Linking
```bash
mf content match-projects              # Auto-link content to projects
mf content about <project-slug>        # Find all content about a project
mf content list-projects               # Projects with content counts
mf content audit                       # Run content checks
mf content audit --extended            # Pluggable audit checks
```

### Analytics
```bash
mf analytics summary                   # Full content overview
mf analytics gaps                      # Projects without linked content
mf analytics tags                      # Tag usage distribution
mf analytics timeline                  # Content activity over time
mf analytics suggestions               # Cross-reference recommendations
```

### Infrastructure
```bash
mf backup list                         # List backups
mf backup restore <file>               # Restore from backup
mf config show                         # Show configuration
mf integrity check                     # Validate database consistency
mf integrity fix --dry-run             # Preview auto-fixes
mf integrity orphans                   # Find orphaned entries
```

## Cross-Repo Usage

The mf CLI resolves the site root in this order:
1. `MF_SITE_ROOT` environment variable (highest priority)
2. Walk up from cwd looking for `.mf/` directory
3. Global config at `~/.config/mf/config.yaml`

```bash
# One-time setup (from any directory):
mkdir -p ~/.config/mf
echo "site_root: ~/github/repos/metafunctor" > ~/.config/mf/config.yaml

# Now all commands work from any directory:
cd ~/github/repos/likelihood.model
mf posts create --title "New release"     # Creates in metafunctor/content/post/
mf posts list --tag python                # Lists metafunctor posts
mf about                                  # Auto-detect current repo

# Or use env var for one-off overrides:
MF_SITE_ROOT=~/other-site mf papers list
```

## mf to Crier Pipeline

Content flows: **mf (create/update) -> Hugo (render) -> crier (distribute)**

After creating or updating content with mf, suggest cross-posting:

```bash
# 1. Create/update content
mf papers generate --slug new-paper
# or: manually write a new post

# 2. Build site
make deploy

# 3. Cross-post (see /crier skill for full workflow)
crier audit content/papers/new-paper/index.md
crier publish content/papers/new-paper/index.md --to devto
```

For short-form platforms (Bluesky, Mastodon), Claude writes the rewrite and passes it via `--rewrite`. See the `/crier` skill for detailed guidance.

## Common Workflows

### Add a new paper
1. Process LaTeX: `mf papers process path/to/paper.tex`
2. Set metadata: `mf papers set slug stars 5`
3. Generate content: `mf papers generate --slug slug`
4. Update publications: `mf pubs generate`
5. Deploy: `make deploy`
6. Cross-post: use `/crier`

### Add a new project
1. Add entry to `.mf/projects_db.json` (or use `mf projects import`)
2. Sync: `mf projects sync`
3. Verify: `hugo --gc --minify`
4. Deploy: `make deploy`

### Create a blog post
1. `hugo new post/YYYY-MM-DD-slug/index.md` (from site root)
2. Edit front matter: add tags, categories, series, description
3. Write content
4. Deploy: `make deploy`
5. Cross-post: use `/crier`

### Feature/unfeature content
```bash
mf papers feature <slug>           # Toggle paper featured
mf projects feature <slug>        # Toggle project featured
mf series feature <slug>          # Toggle series featured
```

### Validate after changes
```bash
hugo --gc --minify                 # Catches front matter errors
mf integrity check                # Database consistency
mf content audit --extended       # Content quality checks
mf health links                   # Broken internal links
mf taxonomy audit                 # Near-duplicate taxonomy terms
```

## Gotchas

- `docs/` is committed to git (GitHub Pages). Don't gitignore it.
- Rich projects use `_index.md` (branch bundle) vs regular use `index.md`.
- `linked_project` taxonomy, NOT `projects` — URL collision with content section.
- Series landing pages: external source takes priority over local `_index.md`.
- PyPI names sometimes differ from repo names (e.g., `soprano` -> `soprano-tts`).
- R-universe URLs: `queelius.r-universe.dev/PACKAGE` (author subdomain, not package).

## Additional Resources

- For complete command reference, see [COMMANDS.md](COMMANDS.md)
- For step-by-step workflows, see [WORKFLOWS.md](WORKFLOWS.md)
