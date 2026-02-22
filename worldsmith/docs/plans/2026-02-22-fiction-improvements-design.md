# Fiction Integration Improvements

**Date:** 2026-02-22

## Summary

Follow-up improvements to the fiction merge (2026-02-20). Expands the cliche detection hook with conservative new patterns, connects the prose-craft skill to the pattern audit system, bumps the version, and adds a help command for workflow discovery.

## Changes

### 1. Expand cliche hook with conservative patterns

Add two new categories to `hooks/scripts/check-fiction-cliches.sh`:

**Redundant adverbs** (verb already implies the adverb):
- "whispered quietly", "shouted loudly", "sprinted quickly", "crept slowly", "muttered softly", "screamed loudly", "tiptoed quietly", "rushed hurriedly"

Message: "adverb duplicates the verb — cut the adverb or choose a more precise verb"

**Fancy dialogue tags** (use "said" instead):
- "exclaimed", "opined", "mused", "interjected", "proclaimed", "declared", "retorted", "quipped", "remarked"

Message: "use 'said' or a physical beat instead"

These are high-confidence patterns with minimal false positive risk. They align with rules already documented in the prose-craft skill (redundant adverbs section and dialogue tags section).

### 2. Add pattern audit reference to prose-craft skill

Add a "Manuscript-Wide Audit" section to `skills/prose-craft/SKILL.md` before the "What This Skill Doesn't Cover" section. This connects the prose-craft skill to the existing `count_patterns.py` / `/worldsmith:check editorial` system, so users who trigger prose-craft during writing know the batch audit exists.

### 3. Version bump to 0.3.0

Bump `plugin.json` version from `0.2.0` to `0.3.0`. The fiction merge added a skill and hook (feature addition), and this follow-up expands the hook — collectively a minor version bump.

### 4. Update CLAUDE.md

Update the hook documentation in CLAUDE.md to reflect the expanded cliche detection categories.

### 5. Add `/worldsmith:help` command

Create `commands/help.md` — a quick-reference command that summarizes the three existing commands, two skills, typical workflows, and what the hooks do automatically. Helps users discover the plugin's capabilities without reading source files.

Typical workflows to document:
- **Starting a project**: `/worldsmith:init-world` to scaffold or adopt a doc ecosystem
- **Making changes**: `/worldsmith:change` for canonical edits, exploratory ideas, or promotions
- **Running diagnostics**: `/worldsmith:check [scope]` for consistency, editorial, xref, or status
- **Writing fiction**: prose-craft skill auto-triggers when writing/editing scenes
- **Automatic guards**: cliche detection fires on Write/Edit, propagation reminders fire on doc changes

## Design Decisions

- **Conservative hook expansion only**: Redundant adverbs and fancy dialogue tags are reliably grep-able with near-zero false positives. Filter words and weak verbs are left to the batch audit (`count_patterns.py`) because they're sometimes intentional.
- **Separate design doc**: This is a follow-up to the fiction merge, not a revision of it. Kept as a new doc rather than amending the original.
- **Skill references audit tool, not duplicates it**: The prose-craft skill points users to `/worldsmith:check editorial` rather than embedding pattern-counting logic.
