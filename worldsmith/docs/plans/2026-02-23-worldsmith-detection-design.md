# Tighten Worldsmith Detection to `.worldsmith/`

**Date:** 2026-02-23

## Summary

Replace the keyword heuristic in project detection with a single unambiguous check: does `.worldsmith/` exist? This directory is created by `/worldsmith:init-world` and is the only way to activate worldsmith hooks. No fallback, no migration, no keyword scanning.

## Motivation

The current detection script (`detect-worldsmith-project.sh`) uses keyword heuristics — it greps CLAUDE.md for terms like "worldbuilding", "propagation", "canonical hierarchy". This is fragile: any project mentioning those words triggers all worldsmith hooks (cliche detection, propagation reminders, completion checks). Explicit opt-in via a marker directory is safer and leaves room for future project-level config.

## Changes

### 1. Simplify `detect-worldsmith-project.sh`

Replace the docs/lore directory scanning and CLAUDE.md keyword grep with:

```bash
if [ -d "$PROJECT_DIR/.worldsmith" ]; then
  IS_WORLDSMITH=1
fi
```

Keep the context output section (docs inventory, manuscript listing, related projects) — it still runs after the gate passes, providing useful session-start information.

### 2. Update `commands/init-world.md`

All three modes (scaffold, adopt, verify) create `.worldsmith/` as part of their workflow:
- **Scaffold mode**: `mkdir -p .worldsmith` during initial setup
- **Adopt mode**: `mkdir -p .worldsmith` when setting up the project
- **Verify mode**: check for `.worldsmith/`, create if missing (with user confirmation)

### 3. Update `commands/help.md`

Note that `/worldsmith:init-world` is required to activate hooks and worldsmith detection.

### 4. Update `CLAUDE.md`

Document `.worldsmith/` as the required project marker. Update the detection script description.

## Design Decisions

- **No fallback heuristic**: Projects must explicitly opt in. No keyword scanning, no migration code. Existing projects run `/worldsmith:init-world` once to create `.worldsmith/`.
- **No migration**: Temporary migration code adds complexity that never gets removed. A one-time `init-world` run is simpler.
- **Directory, not file**: `.worldsmith/` already exists as a concept (patterns.md override). A directory is extensible — future config, state, or local hooks can live here.
- **Detection script keeps context output**: The docs inventory, manuscript listing, and related project checks are useful session-start context. They just run after the `.worldsmith/` gate instead of after the keyword gate.
