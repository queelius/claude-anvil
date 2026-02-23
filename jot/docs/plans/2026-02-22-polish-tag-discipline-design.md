# Design: jot Plugin Polish + Tag Discipline

**Date**: 2026-02-22
**Status**: Approved

## Goals

1. Fix known issues in the existing jot plugin (repo URL, missing CLAUDE.md)
2. Tighten tag discipline in the `/jot` command's NL router so entries are always project-tagged
3. Verify end-to-end: SessionStart hook, `/jot` dashboard, `/jot triage`, auto-tagging

## Changes

### 1. `plugin.json` — Fix repo URL

Change `repository` from `https://github.com/queelius/claude-anvil` to `https://github.com/queelius/jot`.

### 2. `CLAUDE.md` — Add per-plugin editing guidance

Create `jot/CLAUDE.md` following monorepo conventions. Document:
- The plugin depends on `jot` CLI being installed
- Skill is a CLI reference (keep in sync with jot CLI changes)
- Commands are the intelligence layer (routing, triage logic)
- Hook script requires `jq` on PATH
- Tag discipline is enforced in the `/jot` command, not via hooks

### 3. `commands/jot.md` — Tighten tag discipline

Current behavior: "automatically include the current project as a tag if project context is available."

New behavior:
- **Always run project detection** before routing any `jot add` command
- **Always append detected tag** to `--tags` unless user explicitly provided tags that include it
- **If no project tag detected**, ask user what tag to use before running `jot add`
- This makes untagged entries the exception, not the default

### 4. End-to-end verification

After changes:
1. Install plugin: ensure SessionStart hook fires
2. Test `/jot` in a project with matching tags
3. Test `/jot add a task` auto-tagging
4. Test `/jot triage`

## Files

| File | Action |
|------|--------|
| `jot/.claude-plugin/plugin.json` | Edit: fix repo URL |
| `jot/CLAUDE.md` | Create |
| `jot/commands/jot.md` | Edit: tighten tag discipline |
| `jot/README.md` | Review, minor fixes if needed |
