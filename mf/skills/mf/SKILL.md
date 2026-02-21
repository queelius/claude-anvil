---
name: mf
description: Use mf (metafunctor) to manage papers, projects, series, and content for the metafunctor.com Hugo site. Also covers site architecture, taxonomies, front matter conventions. For cross-posting, use the crier plugin. Invoke from ANY repo — mf works globally.
argument-hint: "[intent — e.g. 'new post about X', 'sync papers', 'health check']"
---

# mf — Metafunctor Site Management

A CLI toolkit + site architecture guide for metafunctor.com. Works from any directory.

**Division of labor:**
- **mf** does mechanics: database CRUD, Hugo content generation, metadata operations
- **Claude** does judgment: choosing commands, interpreting intent, sequencing workflows, writing content

**Install location:** `~/github/repos/mf` (editable install: `pip install -e ".[dev]"`)
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

**Papers:** `stars` (1-5), `pdf_file` (filename in `static/latex/`), `html_path`, `authors`, `abstract`
**Projects:** `featured`, `project: { status, type, year_started }`, `tech: { languages, topics }`, `sources: { github }`, `packages: { pypi, crates }`
**Series membership (in posts):** `series: ["slug"]`, `series_weight: N`

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

### Content Source Model

| Content | Ground Truth | mf Role | Has Database? |
|---------|-------------|---------|---------------|
| Projects | GitHub repos | DB + overrides + generate | Yes (projects_db.json) |
| Papers | LaTeX sources | DB + sync + generate | Yes (paper_db.json) |
| Series | mf series_db | DB + sync + landing pages | Yes (series_db.json) |
| Posts | The .md file | `mf posts` (list, create, set, tag, feature) | No |
| Writing | The .md file | None | No |
| Medical | The .md file | None | No |

**Key principle:** Databases exist only for content whose ground truth lives elsewhere.

## Intent Mapping

When users describe what they want, map to the right mf workflow:

| User says... | Workflow |
|-------------|----------|
| "new paper", "add a paper" | Paper workflow (below) |
| "new project", "add repo" | Project workflow (below) |
| "new post", "write about X" | Post workflow (below) |
| "health check", "audit site" | Health pass (below) |
| "deploy", "push to prod" | Pre-deploy (below) |
| "feature X", "star this paper" | `mf {type} feature <slug>` |
| "tag X with Y" | `mf {type} tag <slug> --add Y` |
| "sync papers/projects" | `mf papers sync` / `mf projects sync` |
| "cross-post", "share on socials" | Use `/crier` skill instead |
| "what content do I have" | `mf analytics summary` |
| "find broken links" | `mf health links` |
| "clean up tags" | `mf taxonomy audit` then `mf taxonomy normalize` |

### New Paper
1. `mf papers process path/to/paper.tex`
2. `mf papers set <slug> stars 5` (and any other metadata)
3. `mf papers generate --slug <slug>`
4. `mf pubs generate` (updates publications if peer-reviewed)
5. `make deploy`
6. Cross-post: use `/crier`

### New Project
1. Add to `.mf/projects_db.json` (or `mf projects import`)
2. `mf projects sync`
3. `hugo --gc --minify` (verify)
4. `make deploy`

### New Post
1. `mf posts create --title "Title" --tag x --category Y`
2. Edit `content/post/YYYY-MM-DD-slug/index.md` — write content
3. `mf posts set <slug> draft false` (when ready)
4. `make deploy`
5. Cross-post: use `/crier`

### Health Pass
1. `mf health links` — broken internal links
2. `mf health descriptions` — missing descriptions
3. `mf health images` — missing featured images
4. `mf health stale` — content diverged from DB
5. `mf integrity check` — database consistency
6. `mf content audit --extended` — pluggable content checks
7. `mf taxonomy audit` — near-duplicate terms

### Pre-Deploy
1. `mf integrity check` — database ok?
2. `hugo --gc --minify` — Hugo build errors?
3. `mf health links` — no broken links?
4. `make deploy` — build to docs/
5. `make push` — push to GitHub Pages

## Decision Guidance

### Command Group Cheat Sheet

| Group | Key verbs | Notes |
|-------|-----------|-------|
| `papers` | process, sync, generate, set, feature, tag | LaTeX → DB → Hugo |
| `projects` | import, sync, generate, refresh, set, feature, hide, bundle | GitHub → DB → Hugo |
| `series` | create, sync, add, set, feature, tag, delete | DB → landing pages |
| `packages` | sync, generate, set, feature, tag | PyPI/CRAN → DB → Hugo |
| `posts` | create, list, set, unset, tag, feature | Direct front matter edits (no DB) |
| `pubs` | generate, list | Subset of papers (peer-reviewed) |
| `content` | match-projects, about, list-projects, audit | Cross-content linking |
| `taxonomy` | audit, orphans, stats, normalize | Tag/category hygiene |
| `health` | links, descriptions, images, drafts, stale | Content quality checks |
| `analytics` | summary, gaps, tags, timeline, suggestions | Content insights |
| `integrity` | check, fix, orphans | Database consistency |
| `backup` | list, restore | Backup management |
| `config` | show | Configuration display |

### Generate vs Sync

- **generate** = rebuild Hugo pages from database (safe, idempotent)
- **sync** = pull from external sources into database, then generate (may change DB)
- When in doubt, `generate` first — it's read-only on the database

### Ordering Rules

- Always `sync` before `generate` if you want fresh data
- Always `generate` (or `sync`) before `make deploy`
- Run `mf pubs generate` after any paper change (publications derive from papers)

### Tips

- Most `set` commands accept `--regenerate` to auto-rebuild Hugo pages after the edit
- Use `mf --help` and `mf <group> --help` at runtime for exact flags
- All commands accept `--dry-run` for preview
- `--json` output available on most `list` and health commands

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
```

## mf-to-Crier Pipeline

Content flows: **mf (create/update) → Hugo (render) → crier (distribute)**

After creating or updating content with mf, suggest cross-posting:
```bash
# 1. Create/update content
mf papers generate --slug new-paper

# 2. Build site
make deploy

# 3. Cross-post (see /crier skill for full workflow)
crier audit content/papers/new-paper/index.md
crier publish content/papers/new-paper/index.md --to devto
```

For short-form platforms (Bluesky, Mastodon), Claude writes the rewrite and passes it via `--rewrite`. See the `/crier` skill for detailed guidance.

## Gotchas

- `docs/` is committed to git (GitHub Pages). Don't gitignore it.
- Rich projects use `_index.md` (branch bundle) vs regular use `index.md`.
- `linked_project` taxonomy, NOT `projects` — URL collision with content section.
- Series landing pages: external source takes priority over local `_index.md`.
- PyPI names sometimes differ from repo names (e.g., `soprano` → `soprano-tts`).
- R-universe URLs: `queelius.r-universe.dev/PACKAGE` (author subdomain, not package).
- Posts use `content/post` (singular), not `content/posts`.
