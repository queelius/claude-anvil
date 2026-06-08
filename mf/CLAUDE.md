# CLAUDE.md (mf plugin)

Editing guidance for the mf Claude Code plugin. Read before editing this plugin.

## What this is

mf drives the `mf` CLI (a separate package at github.com/queelius/mf) to manage
metafunctor.com Hugo content: papers, projects, posts, and series. The plugin
ships no code of its own; it is the judgment layer (intent to workflow), and the
CLI is the mechanics. The skill turns a natural-language request into the right
`mf` CLI invocations.

## Components

- **`skills/mf/SKILL.md`**: the site-architecture guide, `mf` CLI reference, and
  content workflows. This is the source of truth for CLI syntax and site
  conventions. Keep it factual; do not let it drift from the installed CLI.
- **`commands/mf.md`**: thin wrapper that triggers the `mf` skill. Keep it thin.
- **`skills/scribe/SKILL.md`** plus **`commands/scribe.md`**: latent-theme discovery
  across the corpus. `scribe` is its own skill (not part of the `mf` skill); the
  command is a thin wrapper. Keep workflow logic in the skill, not the command.
  (`scribe` may use crier's `crier_search` as an optional accelerator.)

## Boundary with the crier plugin

mf creates and updates content; the separate **crier** plugin distributes it.
The pipeline is mf to Hugo to crier. Never reimplement cross-posting here; point
at `/crier` instead. The `scribe` skill may use crier's `crier_search` MCP tool
as an optional accelerator, but it must keep its self-contained Glob fallback so
it works when crier is not installed. If you add a hard crier dependency
anywhere, declare it explicitly.

## Conventions to preserve when editing the skill

These live in `skills/mf/SKILL.md`; do not "fix" them without understanding why:

- Front matter uses `linked_project` (not `projects`) to avoid a Hugo URL
  collision.
- Front matter references slugs, not paths.
- Content lives under `content/post` (singular `post`).
- Rich projects use `_index.md`; simple ones use `index.md`.
- `mf generate` is read-only; `mf sync` mutates the database. Databases exist
  only for content whose ground truth lives elsewhere (projects, papers,
  series), not for posts/writing.
- Site-root resolution order: `MF_SITE_ROOT`, then walk up for a `.mf/`
  directory, then `~/.config/mf/config.yaml`. This is why the skill "works from
  any directory." The `~/github/...` paths shown in the skill are the author's
  own environment, not portable references.

## Version bumps

Keep `.claude-plugin/plugin.json` and the `mf` entry in the root
`.claude-plugin/marketplace.json` in sync (both currently 1.1.0). Never bump one
without the other.

## Validation

```bash
# Skill + command frontmatter
for f in skills/*/SKILL.md commands/*.md; do echo "=== $f ===" && head -5 "$f"; done
```
