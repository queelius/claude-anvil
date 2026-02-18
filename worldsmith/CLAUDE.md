# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Worldsmith is a Claude Code **plugin** for documentation-first fiction worldbuilding (the "Silmarillion approach"). There is no build system, test suite, or compiled code. The entire codebase is Markdown files with YAML frontmatter, bash scripts, JSON hooks, and starter templates. "Development" means editing skills, commands, agents, hooks, scripts, and templates.

## Plugin Structure

```
.claude-plugin/plugin.json   # Manifest (name, version, description, author)
skills/<name>/SKILL.md        # Interactive skills (core logic + trigger phrases)
skills/<name>/references/     # Deep reference docs loaded by skills
commands/<name>.md            # Slash commands (workflow entry points)
agents/<name>.md              # Autonomous subagents with system prompts
hooks/hooks.json              # Prompt-based PostToolUse and Stop hooks
scripts/*.sh                  # Bash utilities (doc detection, propagation, pattern counting)
templates/*.template          # Starter templates for /worldsmith:init-world scaffolding
```

## File Format Conventions

### Commands (`commands/*.md`)
YAML frontmatter with `description`, `allowed-tools` (comma-separated tool names), and optional `argument-hint`. Body contains the full workflow with numbered steps. Commands reference `$ARGUMENTS` for user input.

### Skills (`skills/*/SKILL.md`)
YAML frontmatter with `name`, `description` (contains trigger phrases for auto-detection), and `version`. Body uses numbered workflow steps with tool annotations in parentheses: `(Read tool)`, `(Bash tool)`, `(Glob/Grep tools)`. Skills reference sibling files via `${CLAUDE_PLUGIN_ROOT}` — when adding references, verify the target file exists.

### Agents (`agents/*.md`)
YAML frontmatter with `name`, `description` (with `<example>` blocks showing trigger patterns), `tools` (list), `model: inherit`, and `color`. Body is the agent's system prompt. **Two of three agents are READ-ONLY** (continuity-checker, editor) — they only have Read/Grep/Glob tools to prevent accidental file corruption.

### Hooks (`hooks/hooks.json`)
Prompt-based hooks (not code-based). Two event types:
- **PostToolUse** (matcher: `Write|Edit`): Reminds about cross-reference propagation when docs/manuscript are edited
- **Stop** (matcher: `*`): Blocks session exit if propagation appears incomplete

### Templates (`templates/*.template`)
Use `{{PLACEHOLDER}}` syntax (e.g. `{{PROJECT_NAME}}`, `{{GENRE}}`, `{{FORMAT}}`). Placeholders are filled by the `/worldsmith:init-world` command during project scaffolding.

### Scripts (`scripts/*.sh`)
All use `set -euo pipefail`. Accept positional arguments with `${1:?Usage: ...}` pattern.

## Core Concept: The Doc Ecosystem

The plugin's entire methodology revolves around six tightly coupled documents that form a target project's editorial system:

```
                    outline.md
                   (diagnostic hub)
                   /    |    \
          lore.md   characters.md   worldbuilding.md
              \         |         /
                style-guide.md
                        |
                  future-ideas.md
```

**Canonical hierarchy** (when sources disagree): CANONICAL tables > Timeline > Character entries > Outline > Manuscript.

**Dual workflow** is a first-class concept:
- **Canonical** (`/fix`): docs first → manuscript → outline → verify propagation
- **Exploratory** (`/explore`): write to provisional sections only, no manuscript changes until `/promote`

Every command, agent, skill, and hook enforces or supports this ecosystem. When editing plugin components, preserve this discipline.

## Propagation Rules

The propagation matrix is central to the plugin. It's encoded in:
- `skills/doc-ecosystem/references/propagation-rules.md` (detailed rules)
- `templates/CLAUDE.md.template` (cross-reference table for target projects)
- `scripts/check-propagation.sh` (automated checking)
- `hooks/hooks.json` (runtime reminders)

If you change the propagation rules in one place, update all four.

## Validation

```bash
# Skill frontmatter has name and description
for f in skills/*/SKILL.md; do echo "=== $f ===" && head -5 "$f" && echo; done

# Command frontmatter has description and allowed-tools
for f in commands/*.md; do echo "=== $f ===" && head -5 "$f" && echo; done

# Agent frontmatter has name, description, tools, model
for f in agents/*.md; do echo "=== $f ===" && head -10 "$f" && echo; done

# ${CLAUDE_PLUGIN_ROOT} references point to existing files
grep -roh '\${CLAUDE_PLUGIN_ROOT}/[^`"]*' skills/ | sort -u | while read ref; do
  resolved="${ref/\$\{CLAUDE_PLUGIN_ROOT\}/\.}"
  [ -f "$resolved" ] || echo "BROKEN: $ref"
done

# Scripts are executable
ls -la scripts/*.sh
```

## Editing Guidelines

- Commands are workflow entry points — they contain the full step-by-step process, not just a trigger for a skill
- Skills provide methodology and reference material loaded on-demand via trigger phrases
- Keep READ-ONLY agents (continuity-checker, editor) restricted to Read/Grep/Glob tools only
- When editing propagation-related content, check all four locations where rules are encoded
- Templates use `{{PLACEHOLDER}}` — don't accidentally introduce literal values
- The hook prompts are carefully worded to avoid false positives on non-worldbuilding edits
