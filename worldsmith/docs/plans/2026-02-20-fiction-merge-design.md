# Merge Fiction Plugin into Worldsmith

**Date:** 2026-02-20

## Summary

Absorb the standalone `fiction` plugin (`~/github/repos/fiction`) into worldsmith. The fiction plugin provides two components — a prose craft skill and a cliche detection hook — that complement worldsmith's editorial methodology without duplicating it.

## Changes

### 1. New skill: `skills/prose-craft/SKILL.md`

Copy `fiction/skills/fiction/SKILL.md` to `worldsmith/skills/prose-craft/SKILL.md`. Rename to `prose-craft` in YAML frontmatter. No content changes — the skill is self-contained and already references `soul` and per-project CLAUDE.md appropriately.

### 2. Cliche hook: `hooks/scripts/check-fiction-cliches.sh`

Move `fiction/hooks/check-fiction-cliches.sh` to `worldsmith/hooks/scripts/check-fiction-cliches.sh`. Add `WORLDSMITH_PROJECT` gate (same pattern as `propagation-reminder.sh`). Keep the `$CLAUDE_PLUGIN_ROOT` self-exemption. Add as a second PostToolUse hook on `Write|Edit` in `hooks/hooks.json`.

### 3. Manifest and docs updates

- Update `plugin.json` description to mention prose craft
- Update worldsmith `CLAUDE.md` to document the new skill and hook

### 4. Delete fiction repo

Remove `~/github/repos/fiction` after merge is verified.

## Design Decisions

- **Gated on `WORLDSMITH_PROJECT`**: Cliche hook only fires in worldsmith-detected projects, consistent with all other worldsmith hooks.
- **Separate skill, not folded in**: Prose craft is a distinct concern from editorial methodology. Two skills keep triggers and content independent.
- **No content changes to skill**: The fiction SKILL.md is well-written and complete as-is.
