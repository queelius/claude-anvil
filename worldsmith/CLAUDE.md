# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Worldsmith is a Claude Code **plugin** for documentation-first fiction worldbuilding (the "Silmarillion approach"). There is no build system, test suite, or compiled code. The entire codebase is Markdown files with YAML frontmatter, bash scripts, and JSON hooks. "Development" means editing skills, commands, agents, hooks, and scripts.

## Plugin Structure

```
.claude-plugin/plugin.json                       # Manifest (name, version, description)
skills/worldsmith-methodology/SKILL.md            # Editorial methodology skill
skills/worldsmith-methodology/references/          # Deep reference docs (propagation, doc structure)
skills/prose-craft/SKILL.md                      # Prose craft rules (show-don't-tell, dialogue, scene structure)
commands/{init-world,change,check,review,help}.md  # 5 slash commands
agents/reviewer.md                                # Review orchestrator (spawns specialist auditors)
agents/writer.md                                  # Writer orchestrator (spawns specialist writers)
agents/rewriter.md                                # Rewriter orchestrator (fix-then-verify loop)
agents/{consistency,craft,voice,structure}-auditor.md  # 4 review specialists (read-only)
agents/{lore-writer,scene-writer,character-developer}.md  # 3 writing specialists
hooks/hooks.json                                  # SessionStart + PostToolUse + Stop hooks
hooks/scripts/detect-worldsmith-project.sh        # Project detection (checks for .worldsmith/ directory)
hooks/scripts/propagation-reminder.sh            # PostToolUse propagation reminders
hooks/scripts/check-fiction-cliches.sh           # Cliche detection (stock reactions, dead metaphors, emotional labeling, redundant adverbs, fancy dialogue tags)
hooks/scripts/completion-check.sh                # Stop hook: propagation verification
scripts/count_patterns.py                         # Prose pattern counting (reads patterns.md)
scripts/patterns.md                               # Default pattern definitions (overridable per project)
```

## File Format Conventions

### Commands (`commands/*.md`)
YAML frontmatter with `description`, `allowed-tools`, and optional `argument-hint`. Body contains instructions FOR Claude describing rules and awareness, not rigid scripts. Commands reference `$ARGUMENTS` for user input and `${CLAUDE_PLUGIN_ROOT}` for sibling files.

### Skills (`skills/*/SKILL.md`)
Two skills, independently triggered:
- **worldsmith-methodology** — Editorial methodology: canonical hierarchy, propagation, doc roles, dual workflow. Triggers on doc ecosystem and worldbuilding keywords.
- **prose-craft** — Sentence-level prose craft: show-don't-tell, dialogue mechanics, scene structure, AI-fiction failure modes. Triggers on fiction writing and editing keywords.

YAML frontmatter with `name`, `description` (trigger phrases for auto-detection), and `version`. Body is lean methodology with references to detailed docs via `${CLAUDE_PLUGIN_ROOT}`. When adding references, verify the target file exists.

### Agents (`agents/*.md`)
Three orchestrators and seven specialists. YAML frontmatter with `name`, `description` (with `<example>` blocks), `tools` (list), `model: opus`, and `color`.

**Orchestrators** (spawn specialists via Task tool):
- **reviewer** — Multi-agent editorial review. Reads project context, launches 4 auditors in parallel, cross-verifies critical findings, synthesizes unified report to `.worldsmith/reviews/`.
- **writer** — Multi-agent content generation. Plans assignments, launches specialists, integrates output, handles doc propagation.
- **rewriter** — Multi-agent revision. Reads review findings, dispatches writer specialists to fix, then reviewer specialists to verify. Fix-then-verify feedback loop.

**Review specialists** (read-only, launched by reviewer):
- **consistency-auditor** — Timeline, facts, character state, spatial contradictions
- **craft-auditor** — Prose quality, cliche detection, scene mechanics (has Bash for `count_patterns.py`)
- **voice-auditor** — Character voice consistency, dialogue distinctiveness, POV
- **structure-auditor** — Pacing, tension, scene turns, thematic coherence, arc trajectory

**Writing specialists** (launched by writer):
- **lore-writer** — History, mythology, cultures, systems with consequence chains
- **scene-writer** — Prose scenes with craft discipline (read-only, produces draft in output)
- **character-developer** — Voice patterns, arc development, relationship mapping

### Hooks (`hooks/hooks.json`)
Three event types:
- **SessionStart** (command): Runs `detect-worldsmith-project.sh` — checks for `.worldsmith/` directory, sets `WORLDSMITH_PROJECT` env var, outputs doc inventory
- **PostToolUse** (command, matcher: `Write|Edit`): Two hooks — propagation reminders for doc/manuscript edits, and cliche detection for stock body reactions, dead metaphors, emotional labeling, redundant adverbs, and fancy dialogue tags in fiction files (.tex, .md, .mdx, .txt)
- **Stop** (prompt): Completion verification before session exit

### Scripts
- `scripts/count_patterns.py` — Python, reads pattern definitions from `scripts/patterns.md`. Projects can override by placing `patterns.md` in `.worldsmith/` at project root.
- `scripts/patterns.md` — Default pattern list (crutch words, filter words, weak verbs, dialogue tags). Plain markdown, self-documenting, editable by Claude or by hand.
- `hooks/scripts/detect-worldsmith-project.sh` — Bash, runs on SessionStart.

## Core Concepts

**Role-based doc ecosystem.** The plugin thinks in document roles (timeline authority, lore, systems, characters, style conventions, outline, editorial backlog, themes/anti-cliche, exploratory ideas) — not hardcoded filenames. Each target project's CLAUDE.md maps roles to its own file structure.

**Canonical hierarchy** (when sources disagree): canonical tables > timeline authority > system specs > character entries > outline > manuscript.

**Dual workflow:**
- **Canonical changes**: docs first, then manuscript, then propagation check
- **Exploratory ideas**: provisional sections only, no manuscript changes until promoted

**Propagation awareness.** Every change has a blast radius. Claude traces changes through the doc graph using awareness (not rigid matrices). Details in `references/propagation-awareness.md`.

**Series awareness.** Projects can reference related projects (prequels, sequels, shared-world companions) in their CLAUDE.md. Shared world facts propagate across projects; project-local facts don't.

## Validation

```bash
# Skill frontmatter has name and description
for f in skills/*/SKILL.md; do echo "=== $f ===" && head -5 "$f" && echo; done

# Command frontmatter has description and allowed-tools
for f in commands/*.md; do echo "=== $f ===" && head -5 "$f" && echo; done

# Agent frontmatter has name, description, tools, model
for f in agents/*.md; do echo "=== $f ===" && head -10 "$f" && echo; done

# ${CLAUDE_PLUGIN_ROOT} references point to existing files
grep -roh '\${CLAUDE_PLUGIN_ROOT}/[^`"]*' skills/ commands/ | sort -u | while read ref; do
  resolved="${ref/\$\{CLAUDE_PLUGIN_ROOT\}/\.}"
  [ -f "$resolved" ] || echo "BROKEN: $ref"
done

# Hook scripts are executable
ls -la hooks/scripts/*.sh
```

## Editing Guidelines

- Commands provide rules and awareness, not rigid step-by-step scripts — Claude Code is the intelligence layer
- Skills are lean (~2000 words max) with detailed content in `references/`
- Review specialists are strictly read-only — only Read/Grep/Glob tools (craft-auditor also gets Bash)
- Orchestrators coordinate specialists via Task tool — don't add Task to specialist tool lists
- Hook prompts are carefully worded to avoid false positives on non-worldbuilding edits
- When editing propagation-related content, check both `references/propagation-awareness.md` and `hooks/hooks.json`
