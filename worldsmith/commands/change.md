---
description: Apply a change to the worldbuilding project — edits, new ideas, or promotions
allowed-tools: Read, Write, Edit, Grep, Glob, AskUserQuestion
argument-hint: [description of change or idea]
---

# /worldsmith:change

Apply a change to the worldbuilding project. Determine the appropriate mode from the user's request and the project context. This is not a rigid step-by-step script -- understand the rules, then reason about the specific change.

## Setup

Read the project's CLAUDE.md first. Parse the document roles table to know which files serve which roles. Understand the canonical hierarchy and any project-specific rules.

## Mode Determination

Determine the mode from the user's request:

- **Canonical change** -- The user is fixing, revising, or updating established facts. Correcting a date, updating a character arc after writing a chapter, revising a system rule, reconciling a contradiction.
- **Exploratory idea** -- The user is developing something new that isn't established yet. Drafting mythology, sketching a future plot thread, experimenting with a system extension, noting an idea for later.
- **Promotion** -- The user wants to make an exploratory idea canonical. Moving provisional content to established status.

If the mode is unclear from `$ARGUMENTS`, ask.

## Canonical Change

1. Identify the canonical source for the fact being changed. Use the canonical hierarchy: canonical tables > timeline authority > system specs > character entries > outline > manuscript.
2. Update the authoritative source doc first.
3. Think about what else is affected. Consult the project's CLAUDE.md for the doc structure and propagation notes. Consider: does this change affect character ages, event references, system plausibility, scene logistics, cross-references, or thematic commitments?
4. Update affected docs. Update manuscript passages where the old fact appears.
5. If project-level facts changed (world structure, canonical tables, character conventions, anti-cliche rules, series relationships), update CLAUDE.md.

## Exploratory Idea

1. Identify which doc role the idea belongs to (lore, systems, characters, backlog, themes).
2. Write to the appropriate doc's exploratory or provisional section. If no such section exists, create one clearly labeled.
3. Mark the content as provisional with a date: `[PROVISIONAL — YYYY-MM-DD]`.
4. Note any conflicts with existing canonical facts. Do not resolve them yet -- just flag them.
5. Do NOT update the manuscript based on exploratory content.
6. Do NOT propagate to other canonical sections.

## Promotion

1. Find the exploratory content to be promoted.
2. Check for conflicts with canonical facts. If conflicts exist, resolve them -- this may require the user's input.
3. Move the content from the exploratory section to the canonical section. Remove the provisional marker.
4. Treat it as a canonical change from this point: reconcile affected docs and manuscript.

## Rules

- Bidirectional updates between docs and manuscript are OK. A scene may introduce a detail that flows back to docs, or a doc revision may require manuscript changes.
- CLAUDE.md is a living document. Update it when project-level facts change.
- For series projects, if a shared world fact changes, note which related projects may need checking. Do not modify other projects' files without explicit direction.
- After completing, summarize what changed and what the user might want to verify. List the files modified and any downstream effects that were not addressed.
- Consult `${CLAUDE_PLUGIN_ROOT}/skills/worldsmith-methodology/references/propagation-awareness.md` for guidance on how changes ripple through interconnected docs.
