# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Claude Code **plugin marketplace** (`queelius`). All plugins are distributed as a single git repo. No build system, test suite, or compiled code — the codebase is Markdown files with YAML frontmatter.

**Install**: `/plugin marketplace add queelius/claude-anvil`
**Install a plugin**: `/plugin install repoindex@queelius`

| Plugin | Dir | Purpose | Version |
|--------|-----|---------|---------|
| **papermill** | `papermill/` | Academic paper lifecycle: thesis, lit survey, experiment, review, venue, submission | 0.6.0 |
| **worldsmith** | `worldsmith/` | Documentation-first fiction worldbuilding (the "Silmarillion approach") | 0.6.1 |
| **pub-pipeline** | `pub-pipeline/` | Publication workflows: R/CRAN/JOSS, Python/PyPI | 0.6.0 |
| **mf** | `mf/` | Metafunctor site management: blog architecture, content workflows, crier | 1.1.0 |
| **repoindex** | `repoindex/` | Collection-aware repository intelligence — query, analyze, maintain git repos | 0.12.0 |
| **alex-confidential** | `locksmith/` | Confidentiality toolkit — cryptoid, pagevault, gpg encryption | 0.2.0 |
| **kdp** | `kdp/` | Amazon KDP book publishing: manuscript audit, listing craft, submission workflow | 0.2.0 |
| **jot** | `jot/` | Journal-aware sessions — surfaces tasks, ideas, and plans from your jot journal | 0.3.0 |
| **crier** | `crier/` | Cross-post blog content to multiple platforms via the crier CLI | 1.1.0 |

## Plugin Anatomy

Each plugin directory follows Claude Code plugin conventions:

```
<plugin>/
├── .claude-plugin/plugin.json   # Manifest: name, version, description, author
├── skills/<name>/SKILL.md       # Interactive skills (the core logic)
├── commands/<name>.md            # Slash commands (thin wrappers or rich command docs)
├── agents/<name>.md              # Autonomous subagents with system prompts
└── CLAUDE.md                     # Per-plugin editing guidance (read before editing)
```

Not all plugins use every component. Minimal plugins like alex-confidential have only a skill. Larger plugins add extras: worldsmith has `hooks/`, `scripts/`; pub-pipeline has `docs/` (reference material and design plans).

## File Format Conventions

### Skills (`skills/<name>/SKILL.md`)
YAML frontmatter with `name` and `description` (description contains trigger phrases for auto-detection). Body style varies by plugin: pub-pipeline/papermill use numbered workflow steps with tool annotations `(Read tool)`; worldsmith uses lean methodology with `references/` subdirectories for detailed content.

### Commands (`commands/<name>.md`)
YAML frontmatter with `description`. Most are minimal (3-5 lines) with a one-line instruction triggering the corresponding skill. Worldsmith commands are richer — they include `allowed-tools`, `argument-hint`, and inline rules/awareness for Claude.

### Agents (`agents/<name>.md`)
YAML frontmatter with `name`, `description` (with `<example>` blocks showing trigger patterns), `tools` (list of allowed tools), `model`, and `color`. Body is the agent's system prompt.

### Hooks (`hooks/hooks.json`)
JSON with event handlers. Worldsmith uses three: `SessionStart` (command hook for ambient project detection), `PostToolUse` (prompt hook for propagation reminders on Write/Edit), `Stop` (prompt hook for completion verification).

## Cross-Plugin Patterns

**State files**: papermill (`.papermill.md`), pub-pipeline (`.claude/pub-pipeline.local.md`), and kdp (`.claude/kdp.local.md`) use per-project state files with YAML frontmatter + markdown body. These live in the *target* project, not in this repo.

**`${CLAUDE_PLUGIN_ROOT}` references**: Skills reference sibling files via this variable (resolves to plugin installation directory at runtime). When adding references, verify the target file exists.

**Router pattern**: pub-pipeline has a top-level router skill (`skills/pub-pipeline/SKILL.md`) that detects project type by indicator files (`DESCRIPTION` → R, `pyproject.toml` → Python, `.tex`+`.pdf` → academic paper) and delegates to the ecosystem-specific skill. The router has no command — it triggers via natural language.

**Author metadata via deets CLI**: Plugins needing author info (papermill, pub-pipeline) can fall back to the `deets` CLI tool (`deets show --format json`), configured globally. Per-project config files (e.g. `.claude/pub-pipeline.local.md`) are checked first.

**Audit report pattern** (pub-pipeline, kdp): Audit skills produce structured gap reports with Critical (Must Fix) / Warnings (Should Fix) / Passed sections.

**Propagation discipline** (worldsmith): Role-based document system — the plugin thinks in doc roles (timeline authority, lore, systems, characters, style conventions, outline, themes, editorial backlog), not hardcoded filenames. Each target project maps roles to its own file structure. Canonical docs are always updated before manuscript text.

## Validation

After editing any plugin, verify from that plugin's directory:

```bash
# Skill frontmatter has name and description
for f in skills/*/SKILL.md; do echo "=== $f ===" && head -5 "$f" && echo; done

# Command frontmatter has description
for f in commands/*.md; do echo "=== $f ===" && head -5 "$f" && echo; done

# Agent frontmatter has name, description, tools, model
for f in agents/*.md; do echo "=== $f ===" && head -10 "$f" && echo; done

# ${CLAUDE_PLUGIN_ROOT} references point to existing files
grep -roh '\${CLAUDE_PLUGIN_ROOT}/[^`"]*' skills/ commands/ | sort -u | while read ref; do
  resolved="${ref/\$\{CLAUDE_PLUGIN_ROOT\}/\.}"
  [ -f "$resolved" ] || echo "BROKEN: $ref"
done
```

## Version Bumps

Versions live in **two places** that must stay in sync:
1. `.claude-plugin/marketplace.json` — the marketplace catalog (drives update detection)
2. Each plugin's `.claude-plugin/plugin.json` — the plugin manifest

**Always update both.** If `marketplace.json` isn't bumped, Claude Code won't detect the update.

## Editing Guidelines

- Each plugin has its own CLAUDE.md with plugin-specific conventions — read it before editing that plugin
- Skills should be self-contained and work independently
- Commands are thin wrappers — keep logic in skills, not commands
- When editing a skill's workflow steps, preserve the existing structure and tool annotations
- Agents need well-defined tool lists — only grant tools the agent actually needs
- All plugins share one git history — use conventional commit prefixes scoped to plugin, e.g. `feat(pub-pipeline):`, `fix(worldsmith):`
