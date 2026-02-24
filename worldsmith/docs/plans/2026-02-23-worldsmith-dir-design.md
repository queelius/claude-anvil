# `.worldsmith/` as Canonical Detection Signal

**Date:** 2026-02-23

## Summary

Replace the heuristic project detection (grep CLAUDE.md for keywords + check for docs/ directory) with an explicit `.worldsmith/` directory marker. Created by `/worldsmith:init-world`, checked by all hooks. Simplifies detection from 99 lines of heuristic bash to a single directory check.

## Changes

### 1. Simplify detection script

Replace `hooks/scripts/detect-worldsmith-project.sh` heuristic logic with a `[ -d .worldsmith ]` gate. Keep the useful inventory output (doc listing, manuscript count, related projects) — only the gate changes.

### 2. Create `.worldsmith/` in init-world

All three modes of `/worldsmith:init-world` create `.worldsmith/` as a first step:
- **Scaffold mode**: `mkdir -p .worldsmith` before creating `docs/`
- **Adopt mode**: `mkdir -p .worldsmith` during setup
- **Verify mode**: if `.worldsmith/` doesn't exist, create it and report

### 3. `.worldsmith/` contents

The directory serves as:
1. **Detection marker** (existence = worldsmith project)
2. **Override location** for `patterns.md` (already supported by `count_patterns.py`)

No config file for now (YAGNI). Future overrides (cliche exclusions, project metadata) can go here when needed.

### 4. Update docs

- `commands/help.md` — mention `.worldsmith/` marks a project
- `CLAUDE.md` — document `.worldsmith/` as detection signal
- `skills/worldsmith-methodology/references/doc-structure-guide.md` — add `.worldsmith/` to project structure

## Files Changed

| File | Change |
|------|--------|
| `hooks/scripts/detect-worldsmith-project.sh` | Replace heuristic with `[ -d .worldsmith ]` gate, keep inventory output |
| `commands/init-world.md` | Add `.worldsmith/` creation in all three modes |
| `commands/help.md` | Mention `.worldsmith/` as project marker |
| `CLAUDE.md` | Document `.worldsmith/` as detection signal |
| `skills/worldsmith-methodology/references/doc-structure-guide.md` | Add `.worldsmith/` to project structure |

## What Doesn't Change

- All other hooks (`propagation-reminder.sh`, `check-fiction-cliches.sh`, `completion-check.sh`) — gate on `WORLDSMITH_PROJECT` env var, unchanged
- `count_patterns.py` — already checks `.worldsmith/patterns.md`
- `hooks/hooks.json` — no changes
- Agent definitions — no changes

## Design Decisions

- **Hard cutover, no fallback**: Detection requires `.worldsmith/`. Existing projects run `/worldsmith:init-world` once. Simple, no dual-path code.
- **Marker + overrides, not marker-only**: The directory is the detection signal AND the home for project-level overrides (patterns.md today, potentially more later).
- **No config file yet**: YAGNI. The directory itself is sufficient as a marker. Config can be added when there's a concrete need.
- **Keep inventory output**: The detection script's useful context (doc listing, manuscript count, related projects) stays. Only the gate mechanism changes.
