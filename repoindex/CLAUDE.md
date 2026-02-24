# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Claude Code plugin that wraps the [repoindex](https://github.com/queelius/repoindex) CLI — a local git catalog indexing ~170 repos with metadata from GitHub, PyPI, CRAN, and Zenodo. The plugin translates natural language and slash commands into `repoindex` CLI invocations. There is no build system, test suite, or compiled code — the codebase is Markdown files with YAML frontmatter.

**Prerequisite**: `repoindex` CLI must be installed (`pip install repoindex`) and database populated (`repoindex refresh --github`).

## Architecture

The plugin has three tiers that interact with the same CLI:

1. **Skills** (reference docs loaded into context) — `repoindex` (CLI reference with query flags, SQL data model, common queries) and `repo-polish` (audit-driven release preparation workflow with deterministic CLI fixes + AI-assisted prose).

2. **Commands** (thin slash-command wrappers) — `/repo-status` runs three CLI commands and formats a dashboard; `/repo-query` translates natural language to `repoindex query` or `repoindex sql` commands.

3. **Agent** — `repo-explorer` is an autonomous Sonnet-class subagent for multi-query collection analysis (cross-referencing tables, generating reports, finding patterns across repos).

The key design principle: **delegate deterministic work to the CLI** (citation generation, license files, GitHub topic sync), **use AI judgment only for prose** (README writing, description copywriting, topic suggestions).

## Editing Conventions

- Skills use YAML frontmatter with `name` and `description` (description contains trigger phrases for auto-detection)
- Commands use YAML frontmatter with `description`, `argument-hint`, and `allowed-tools`
- The agent frontmatter needs `name`, `description` (with `<example>` blocks), `tools`, `model`, and `color`
- The `repoindex` skill is the canonical CLI reference — when the CLI adds new flags or tables, update this skill
- The `repo-polish` skill's workflow steps must preserve the `--dry-run` first / show user / execute pattern
- Commit messages use conventional prefixes scoped to plugin: `feat(repoindex):`, `fix(repoindex):`, `docs(repoindex):`

## SQL Data Model (for reference when editing skills)

Four tables in `~/.repoindex/repoindex.db`:
- **repos**: core identity (`name`, `path`), git status (`is_clean`, `ahead`, `behind`), metadata (`language`, `description`), GitHub stats (`github_stars`, `github_topics`)
- **publications**: registry packages (`pypi`/`cran`/`zenodo`/`npm`), `published` flag (0=detected, 1=confirmed), download counts
- **events**: git activity (`commit`/`git_tag`/`branch`/`merge`) with timestamps
- **tags**: user/implicit/github classification tags

All joins go through `repo_id` foreign key.
