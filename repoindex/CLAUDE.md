# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Claude Code plugin that provides MCP-driven agents for the [repoindex](https://github.com/queelius/repoindex) local git catalog. The plugin orchestrates multi-step workflows via three specialized agents; all metadata access goes through the repoindex MCP server.

**Prerequisite**: `repoindex` CLI installed (`pip install repoindex[mcp]`), database populated (`repoindex refresh --external`), and the repoindex MCP server configured in `~/.claude.json`.

## Architecture

The plugin is agent-first. Claude Code's built-in MCP support is the single interface for reading repoindex data; agents orchestrate multi-step workflows on top of those tools.

Three agents:

1. **`repo-doctor`** (sonnet): fixed triage workflow. "What needs attention across my repos?" Runs a health check across dirty repos, unpushed commits, quality gaps, stale repos, and publication gaps. Produces a prioritized action list.

2. **`repo-polish`** (opus): single-repo release preparation. Audits a repo, generates boilerplate via `repoindex ops generate`, writes prose (README, descriptions) with AI judgment, re-audits.

3. **`repo-explorer`** (sonnet): open-ended analysis. "Which of my Python repos are on PyPI?" Cross-references tables with custom SQL and narrative synthesis.

### Tool access

All three agents use the repoindex MCP tools:
- `get_manifest()`: database overview
- `get_schema(table?)`: SQL DDL introspection
- `run_sql(query)`: read-only SQL queries
- `tag(repo, action, tag)`: manage user-assigned tags
- `export(output_dir, query?)`: produce arkiv archives
- `refresh(sources?)`: trigger metadata refresh

`repo-polish` also uses Bash for `repoindex ops generate` commands (write operations that don't have MCP equivalents).

### Design principle

Delegate deterministic work to the CLI (`ops generate` for citation files, licenses, GitHub topic sync). Use AI judgment only for prose (README writing, description copywriting, topic suggestions).

## Editing Conventions

- Agent frontmatter needs `name`, `description` (with `<example>` blocks), `tools`, `model`, `color`
- The `description` field contains trigger phrases for auto-detection; be specific
- Tools are listed by name; MCP tools use the `mcp__repoindex__*` prefix
- Commit messages use conventional prefixes: `feat(repoindex):`, `fix(repoindex):`, `docs(repoindex):`

## SQL Data Model (for reference when editing agents)

Four tables in `~/.repoindex/index.db`:

- **repos**: core identity (`name`, `path`), git status (`is_clean`, `ahead`, `behind`), metadata (`language`, `description`, `keywords`), boolean flags (`has_readme`, `has_license`, `has_ci`, `has_citation`, `has_codemeta`, `has_funding`, `has_contributors`, `has_changelog`), GitHub stats (`github_stars`, `github_topics`, `github_is_archived`), Gitea stats (`gitea_stars`, `gitea_topics`)
- **publications**: registry packages (`pypi`/`cran`/`zenodo`/`npm`/`cargo`/`docker`/`rubygems`/`go`), `published` flag, `downloads_total`/`downloads_30d`, `doi`
- **events**: git activity (`commit`/`git_tag`/`branch`/`merge`) with timestamps
- **tags**: classification tags, auto-derived from metadata. Source attribution: `user`, `implicit`, `github`, `gitea`, `pyproject`, `pypi`, `cran`

All joins go through `repo_id` foreign key.

## Migration Note

Earlier versions of this plugin had CLI reference skills (`repoindex`, `repo-polish`), slash commands (`/repo-query`, `/repo-status`), and one agent. With the repoindex v0.15.0 MCP server providing full CLI parity, those skills and commands are obsolete:
- CLI reference: covered by MCP tool descriptions plus `get_schema()`
- `/repo-query`: covered by `run_sql` directly
- `/repo-status`: covered by `run_sql` or `repo-doctor` agent
- `repo-polish` skill: converted to an agent
