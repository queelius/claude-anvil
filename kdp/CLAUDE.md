# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Claude Code **plugin** (not a software project) that automates Amazon KDP (Kindle Direct Publishing) workflows for book authors — manuscript auditing, listing craft, and the full publishing pipeline. It handles technical books (LaTeX, math-heavy), fiction, and general nonfiction.

There is no build system, no test suite, no compiled code. The entire plugin is Markdown files with YAML frontmatter. "Development" means editing skills, commands, and reference docs.

## Architecture

### Plugin Structure

```
.claude-plugin/plugin.json    # Plugin manifest (name, version, metadata)
skills/                       # 3 skill files — the core logic
commands/                     # 3 slash commands — thin wrappers that trigger skills
docs/                         # Reference docs and config template
```

### Skill → Command Mapping

Each skill has a corresponding slash command. Commands are minimal — just frontmatter with `description:` and a one-line instruction that triggers the skill. The mapping:

| Command file | Skill directory | Purpose |
|---|---|---|
| `commands/kdp-audit.md` | `skills/kdp-audit/` | Audit manuscript against KDP requirements |
| `commands/kdp-listing.md` | `skills/kdp-listing/` | Craft Amazon listing: blurb, keywords, categories, bio |
| `commands/kdp-publish.md` | `skills/kdp-publish/` | Full KDP publishing workflow |

### User Config

All skills read `.claude/kdp.local.md` (in the user's target project, not this repo). The template is at `docs/user-config-template.md`. YAML frontmatter holds structured fields (`author`, `kdp`); the markdown body holds free-form notes.

Every skill includes a "Load user config" step early in its workflow. If the config file is missing, the skill offers to create one from the template using `${CLAUDE_PLUGIN_ROOT}/docs/user-config-template.md`.

### Reference Docs

Skills reference detailed requirements docs via `${CLAUDE_PLUGIN_ROOT}/docs/`:
- `kdp-reference.md` — KDP formatting, pricing, submission guide
- `kdp-exemplars.md` — Fiction blurb examples, keyword strategies, category tactics

## Conventions

### Skill File Structure

All skills (`skills/*/SKILL.md`) share:
1. **YAML frontmatter**: `name` and `description` (description lists trigger phrases for auto-detection)
2. **Numbered workflow steps** with tool annotations in parentheses: `(Read tool)`, `(Bash tool)`, `(Glob/Grep tools)`
3. **"Reference Files" section** pointing to `${CLAUDE_PLUGIN_ROOT}/docs/`

The audit skill (`kdp-audit`) additionally includes:
4. **Gap report template** using the Critical (Must Fix) / Warnings (Should Fix) / Passed structure
5. **"Offer to Fix" section** listing automatable remediation
6. **"Important Notes" section** with key gotchas

### Command File Structure

Commands (`commands/*.md`) are 3-5 lines:
```markdown
---
description: "One-line for slash-command help"
---
Brief instruction triggering the corresponding skill.
```

### Audit Report Pattern

The `kdp-audit` skill produces a structured gap report:
```
# KDP Audit Report: {book title}
## Summary (Status, Manuscript type, Format, Target)
## Critical Gaps (Must Fix)
## Warnings (Should Fix)
## Interior Formatting
## Cover Specifications
## Metadata
## Recommended Next Steps
```

### `${CLAUDE_PLUGIN_ROOT}` References

Skills reference docs via `${CLAUDE_PLUGIN_ROOT}/docs/filename.md`. This variable resolves to the plugin's installation directory at runtime. When adding new references, verify the target file exists in `docs/`.

## Validation

After making changes, verify:
```bash
# All skill frontmatter has name and description
for f in skills/*/SKILL.md; do echo "=== $f ===" && head -5 "$f" && echo; done

# All command frontmatter has description
for f in commands/*.md; do echo "=== $f ===" && head -5 "$f" && echo; done

# All ${CLAUDE_PLUGIN_ROOT} references point to existing files
grep -roh '\${CLAUDE_PLUGIN_ROOT}/[^`"]*' skills/ | sort -u
```
