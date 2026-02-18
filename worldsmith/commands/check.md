---
description: Run diagnostics — consistency, editorial, cross-references, or project status
allowed-tools: Read, Grep, Glob, Bash(python3:*), AskUserQuestion
argument-hint: [scope: all|consistency|editorial|xref|status]
---

# /worldsmith:check

Run read-only diagnostics on the worldbuilding project. Do NOT modify any files. Report findings and let the user decide what to act on.

## Setup

Read the project's CLAUDE.md. Parse the document roles table, canonical hierarchy, and any project-specific rules. This is the foundation for every diagnostic mode.

## Mode Selection

Determine the mode from `$ARGUMENTS`. Default to **all** if no scope is specified.

- `consistency` -- Contradictions between docs and manuscript
- `editorial` -- Prose patterns and style analysis
- `xref` -- Cross-reference health
- `status` -- Project health overview
- `all` -- Run all modes, unified report

## Consistency Diagnostics

Check for contradictions between docs and between docs and manuscript. Use the canonical hierarchy to determine which source is correct when conflicts are found.

**Timeline** -- Dates, ages, event sequences, duration claims. Compare the timeline authority against manuscript references, character doc age entries, lore event descriptions, and outline entries. Flag mismatches with specific locations in both the canonical source and the conflicting reference.

**Facts** -- Canonical table values, system rules, geographic facts. Compare authoritative docs against manuscript statements. Search manuscript for references to established facts and verify accuracy.

**Characters** -- Knowledge states (does a character know something they shouldn't yet?), emotional states (does the arc trajectory make sense given prior scenes?), capabilities (does a character do something their docs say they can't?), relationships (are bidirectional entries consistent?).

**Spatial** -- Locations, distances, travel times, architectural details. Compare systems/mechanics geographic facts against manuscript descriptions. Check travel time plausibility against established distances and terrain.

## Editorial Diagnostics

Analyze prose patterns and style adherence. Use `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/count_patterns.py` for mechanical pattern counting. The script reads patterns from `${CLAUDE_PLUGIN_ROOT}/scripts/patterns.md` (defaults) but will use `.worldsmith/patterns.md` in the project root if it exists (project-specific overrides). Layer analytical judgment on top of the counts.

**Prose patterns** -- Identify accumulating crutch words, filter word density, weak verb constructions, and adverb-heavy dialogue tags. Distinguish between occasional use (acceptable) and pattern accumulation (problematic).

**Pacing** -- Scene balance across chapters, info dump detection, draggy sections, rushed transitions. Check whether chapters earn their length relative to their narrative content.

**Style drift** -- Compare manuscript prose against the style conventions doc. Check POV consistency, tense conventions, prose principles adherence, intentional repetitions (are deliberate patterns being maintained?), anti-cliche rule violations.

**Thematic drift** -- Compare manuscript content against the themes/anti-cliche doc. Are thematic commitments being honored? Are anti-cliche rules being violated? Are philosophical positions being maintained or contradicted?

**Character voice** -- Compare character dialogue and internal monologue against character doc voice patterns. Are speech tics consistent? Do characters sound distinct from each other? Does voice evolve along the documented trajectory?

## Cross-Reference Diagnostics

Examine cross-reference health, primarily in the outline/diagnostic hub.

- Verify that outline cross-references point to real entries in other docs.
- Find stale references (outline points to a doc entry that has been modified or removed).
- Find missing references (doc entries that should be referenced in the outline but aren't).
- Check bidirectional links (if the outline references a character doc entry, does the character doc reference back to that scene?).
- Identify orphaned doc entries (content in docs that is never referenced by the outline or manuscript).

## Status Diagnostics

Project health overview. A high-level picture of the project's state.

**Doc inventory** -- For each expected role: does the file exist? What's its size? When was it last modified? Does it have exploratory sections? How complete does it appear?

**CLAUDE.md completeness** -- Does it have all expected sections (project overview, document roles table, consistency rules, world structure, character conventions, series references, propagation notes)? Is the document roles table accurate (do referenced files exist)?

**Manuscript stats** -- How many chapters/files? Total word count. Last modified dates. Which chapters appear most recently worked on?

**Feedback history** -- Does a feedback doc exist? Date range of entries. Unresolved items count.

**Maturity assessment** -- Based on the inventory: is the project in early development (sparse docs, small manuscript), active drafting (growing docs and manuscript), revision (feedback entries, docs being refined), or polishing (docs stable, manuscript receiving minor edits)?

**Recommended next steps** -- Based on gaps found: missing docs that would benefit the project, incomplete sections, stale CLAUDE.md entries, unresolved feedback items.

## Report Format

Group findings by severity:

- **HIGH** -- Contradictions, broken references, factual errors that would confuse readers or break plot logic.
- **MEDIUM** -- Style drift, stale cross-references, missing doc sections, pattern accumulation that isn't yet severe.
- **LOW** -- Minor inconsistencies, optional improvements, nice-to-have additions.

For each finding:
- **Location**: File and line/section where the issue appears.
- **Issue**: What is wrong.
- **Canonical source**: Which document is authoritative on this point.
- **Recommendation**: How to fix it.

When running **all** modes, produce a unified report with a summary section at the top listing counts by severity and category.

## Series Awareness

If the project's CLAUDE.md lists related projects, and those projects are accessible, check cross-project consistency for shared world facts: timeline events that span projects, geographic constants, system rules, cultural constants. Report cross-project inconsistencies in their own section.
