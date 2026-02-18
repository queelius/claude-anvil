# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Claude Code plugin that wraps the `deets` CLI for personal metadata queries. The plugin exposes a single skill (`deets`) that teaches Claude how to use the `deets` command-line tool to look up identity, contact, academic, education, and cross-platform profile information.

## Structure

```
deets/
├── .claude-plugin/plugin.json   # Plugin manifest (name, version, author)
└── skills/deets/SKILL.md        # The skill: deets CLI usage patterns
```

No commands, agents, or hooks — just the skill. The skill triggers automatically when Claude needs personal metadata (author fields, git identity, ORCID, profile URLs, etc.).

## Key Design Decisions

- **No slash command**: The skill is designed for auto-detection via its description trigger phrases, not manual invocation. Other plugins (papermill, pub-pipeline) rely on this to populate author metadata without the user explicitly asking.
- **CLI dependency**: Requires `deets` to be installed on the host system. The skill documents the CLI interface but doesn't install or configure it.
- **Discovery-first**: The skill directs Claude to run `deets schema --format json` to discover available fields rather than hardcoding field names, so the plugin stays correct as the `deets` data store evolves.

## Editing Guidelines

- The skill's `description` frontmatter is critical — it controls when Claude auto-invokes this skill. Keep trigger phrases broad (identity, metadata, author, profile, ORCID, email, etc.).
- Preserve the output conventions section — other plugins depend on `deets get` returning bare pipe-friendly values.
- If adding a command wrapper, keep it minimal (one line delegating to the skill) per marketplace conventions.
