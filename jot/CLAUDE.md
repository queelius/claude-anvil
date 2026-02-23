# CLAUDE.md — jot plugin

Editing guidance for the jot Claude Code plugin.

## Dependencies

The `jot` CLI must be installed and on PATH. Install via:
```bash
go install github.com/queelius/jot/cmd/jot@latest
```

The SessionStart hook script also requires `jq` on PATH. The `/jot triage` command optionally uses `gh` CLI for PR cross-referencing.

## Component Roles

- **Skill** (`skills/jot/SKILL.md`) — CLI reference. This is a factual description of jot's commands, flags, and data model. Keep it in sync with the jot CLI when commands or flags change. Do not add intelligence or workflow logic here.

- **Commands** (`commands/`) — Intelligence layer. `/jot` provides project-aware dashboards and natural language routing. `/jot triage` cross-references entries with git history. Workflow logic, tag discipline, and presentation decisions live here.

- **Agent** (`agents/journal-analyst.md`) — Autonomous analysis for multi-query tasks (patterns, reports, health checks). Uses `jot` CLI with `--json` for all data access.

- **Hook** (`hooks/`) — SessionStart auto-detection. The bash script fuzzy-matches the current directory name against jot tags and shows a compact summary. It must be fast (<15s timeout) and fail silently if jot/jq are unavailable.

## Conventions

- Tag discipline is enforced in the `/jot` command routing rules, not via PostToolUse hooks. The command auto-detects the project tag from cwd and includes it on all `jot add` operations.

- All programmatic access to jot uses `--json` output. Human-readable formatting is done by Claude, not by the CLI.

- The skill is the source of truth for CLI syntax. Commands and agents should not duplicate flag documentation — they reference the skill implicitly.

## Validation

```bash
# Skill frontmatter
head -5 skills/jot/SKILL.md

# Command frontmatter
for f in commands/*.md; do echo "=== $f ===" && head -5 "$f" && echo; done

# Agent frontmatter
head -10 agents/journal-analyst.md

# Hook script is executable and has shebang
head -1 hooks/scripts/detect-jot-context.sh
ls -la hooks/scripts/detect-jot-context.sh
```
