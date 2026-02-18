# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Claude Code **plugin marketplace** (`queelius`). Contains multiple plugins distributed as a single git repo. No build system, test suite, or compiled code — the codebase is Markdown files with YAML frontmatter.

**Install**: `/plugin marketplace add queelius/claude-code-marketplace`
**Install a plugin**: `/plugin install repoindex@queelius`

| Plugin | Purpose | Version |
|--------|---------|---------|
| **papermill** | Academic paper lifecycle: thesis, lit survey, experiment, review, venue, submission | 0.1.0 |
| **worldsmith** | Documentation-first fiction worldbuilding (the "Silmarillion approach") | 0.1.0 |
| **pub-pipeline** | Publication workflows: R/CRAN/JOSS, Python/PyPI, books/KDP | 0.2.0 |
| **mf** | Metafunctor site management: blog architecture, content workflows, crier | 1.0.0 |
| **repoindex** | Collection-aware repository intelligence — query, analyze, maintain git repos | 0.10.0 |

## Plugin Anatomy

Each plugin directory follows Claude Code plugin conventions:

```
<plugin>/
├── .claude-plugin/plugin.json   # Manifest: name, version, description, author
├── skills/<name>/SKILL.md       # Interactive skills (the core logic)
├── commands/<name>.md            # Slash commands (thin wrappers triggering skills)
├── agents/<name>.md              # Autonomous subagents with system prompts
└── CLAUDE.md                     # Per-plugin editing guidance (optional)
```

Additionally: worldsmith has `hooks/`, `scripts/`, and `templates/`; pub-pipeline has `docs/` (reference material and design plans).

## File Format Conventions

### Skills (`skills/<name>/SKILL.md`)
YAML frontmatter with `name` and `description` (description contains trigger phrases for auto-detection). Body is numbered workflow steps with tool annotations in parentheses: `(Read tool)`, `(Bash tool)`, `(Glob/Grep tools)`.

### Commands (`commands/<name>.md`)
Minimal (3-5 lines). YAML frontmatter with `description`. Body is a one-line instruction that triggers the corresponding skill. Worldsmith commands also use `allowed-tools` and `argument-hint` frontmatter fields.

### Agents (`agents/<name>.md`)
YAML frontmatter with `name`, `description` (with `<example>` blocks showing trigger patterns), `tools` (list of allowed tools), `model`, and `color`. Body is the agent's system prompt.

### Hooks (`hooks/hooks.json` — worldsmith only)
JSON with `PostToolUse` and `Stop` event handlers. Prompt-based hooks that remind about cross-reference propagation when worldbuilding docs are edited.

## Cross-Plugin Patterns

**State files**: Both papermill (`.papermill.md`) and pub-pipeline (`.claude/pub-pipeline.local.md`) use per-project state files with YAML frontmatter + markdown body. These live in the *target* project, not in the plugin repo.

**`${CLAUDE_PLUGIN_ROOT}` references**: Skills reference sibling files via this variable (resolves to plugin installation directory at runtime). When adding references, verify the target file exists.

**Router pattern**: pub-pipeline has a top-level router skill (`skills/pub-pipeline/SKILL.md`) that detects project type by indicator files and delegates to ecosystem-specific skills. The router has no command — it triggers via natural language.

**Audit report pattern** (pub-pipeline): Audit skills produce structured gap reports with Critical (Must Fix) / Warnings (Should Fix) / Passed sections.

**Propagation discipline** (worldsmith): Every doc change must trace through a six-document graph (outline, lore, characters, worldbuilding, style-guide, future-ideas). Canonical docs are always updated before manuscript text.

## Validation

After editing any plugin, verify from that plugin's directory:

```bash
# Skill frontmatter has name and description
for f in skills/*/SKILL.md; do echo "=== $f ===" && head -5 "$f" && echo; done

# Command frontmatter has description
for f in commands/*.md; do echo "=== $f ===" && head -5 "$f" && echo; done

# Agent frontmatter has name, description, tools, model
for f in agents/*.md; do echo "=== $f ===" && head -10 "$f" && echo; done

# Validate marketplace JSON
claude plugin validate .
```

## Editing Guidelines

- Each plugin has its own CLAUDE.md with plugin-specific conventions — read it before editing that plugin
- Skills should be self-contained and work independently
- Commands are thin wrappers — keep logic in skills, not commands
- When editing a skill's workflow steps, preserve the numbered-step structure and tool annotations
- Agents need well-defined tool lists — only grant tools the agent actually needs
- This is a monorepo — all plugins share one git history
