# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Claude Code **plugin** (not a software project) that automates publication workflows across four ecosystems:
- **R packages**: CRAN → JOSS → JSS pipeline
- **Python packages**: PyPI publishing
- **Books**: Amazon KDP (technical + fiction/nonfiction)
- **Academic preprints**: OSF / MetaArXiv

There is no build system, no test suite, no compiled code. The entire plugin is Markdown files with YAML frontmatter. "Development" means editing skills, commands, and reference docs.

## Architecture

### Plugin Structure

```
.claude-plugin/plugin.json    # Plugin manifest (name, version, metadata)
skills/                       # 10 skill files — the core logic
commands/                     # 9 slash commands — thin wrappers that trigger skills
docs/                         # Reference docs and config template
docs/plans/                   # Design and implementation plans (architectural decisions)
```

### Routing Pattern

The **pub-pipeline** skill (`skills/pub-pipeline/SKILL.md`) is a top-level router. It detects project type by looking for indicator files (`DESCRIPTION` → R, `pyproject.toml` → Python, `.tex`/`.docx` → book) and delegates to the ecosystem-specific skill. If ambiguous, it asks the user.

### Skill → Command Mapping

Each skill has a corresponding slash command. Commands are minimal — just frontmatter with `description:` and a one-line instruction that triggers the skill. The mapping:

| Command file | Skill directory | Ecosystem |
|---|---|---|
| `commands/cran-audit.md` | `skills/cran-audit/` | R |
| `commands/joss-audit.md` | `skills/joss-audit/` | R |
| `commands/joss-draft.md` | `skills/joss-draft/` | R |
| `commands/r-publish.md` | `skills/r-pub-pipeline/` | R |
| `commands/pypi-publish.md` | `skills/pypi-publish/` | Python |
| `commands/kdp-audit.md` | `skills/kdp-audit/` | KDP |
| `commands/kdp-listing.md` | `skills/kdp-listing/` | KDP |
| `commands/kdp-publish.md` | `skills/kdp-publish/` | KDP |
| `commands/osf-preprint.md` | `skills/osf-preprint/` | Academic preprints |

The router skill (`skills/pub-pipeline/`) has no command — it triggers via natural language ("publish my package").

### Shared User Config

All skills read `.claude/pub-pipeline.local.md` (in the user's target project, not this repo). The template is at `docs/user-config-template.md`. YAML frontmatter holds structured fields (`author`, `coauthors`, `r`, `python`, `kdp`, `ai_usage`, `funding`); the markdown body holds free-form notes.

Every skill includes a "Load user config" step early in its workflow. If the config file is missing, the skill offers to create one from the template using `${CLAUDE_PLUGIN_ROOT}/docs/user-config-template.md`.

### Reference Docs

Skills reference detailed policy/requirements docs via `${CLAUDE_PLUGIN_ROOT}/docs/`:
- `cran-reference.md` — CRAN Repository Policy, submission checklist
- `joss-reference.md` — JOSS reviewer checklist, paper format spec
- `joss-exemplars.md` — Real JOSS paper examples (generalized, not package-specific)
- `pypi-reference.md` — PyPI metadata requirements, trusted publishers
- `kdp-reference.md` — KDP formatting, pricing, submission guide
- `kdp-exemplars.md` — Fiction blurb examples, keyword strategies, category tactics
- `osf-reference.md` — OSF API v2 endpoints, authentication, preprint providers, and common errors

## Conventions

### Skill File Structure

All skills (`skills/*/SKILL.md`) share:
1. **YAML frontmatter**: `name` and `description` (description lists trigger phrases for auto-detection)
2. **Numbered workflow steps** with tool annotations in parentheses: `(Read tool)`, `(Bash tool)`, `(Glob/Grep tools)`
3. **"Reference Files" section** pointing to `${CLAUDE_PLUGIN_ROOT}/docs/`

Audit skills (cran-audit, joss-audit, kdp-audit) additionally include:
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

All audit skills (cran-audit, joss-audit, kdp-audit) produce structured gap reports. `pypi-publish` also includes an audit step (step 12) with a similar but distinct report structure. The standard audit report pattern:
```
# {Type} Audit Report: {name}
## Summary (Status, Score, Blockers)
## Critical (Must Fix)
## Warnings (Should Fix)
## Passed
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

# No stale package-specific content in exemplars
grep -ri "dfr.dist" skills/ docs/ || echo "CLEAN"
```
