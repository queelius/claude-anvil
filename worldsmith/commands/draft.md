---
description: Launch the writer orchestrator to draft scenes, chapters, lore, or character work
allowed-tools: Read, Glob, Grep, Task
argument-hint: "[work-name] [assignment, e.g. 'chapter 5', 'Greymoor battle scene', 'develop the Ashwalker culture']"
---

# /worldsmith:draft

Launch the **writer** orchestrator agent to produce new content for the project.

The writer plans the assignment, then dispatches specialist agents in parallel:

- `lore-writer` for history, mythology, cultures, systems
- `scene-writer` for prose scenes with craft discipline
- `character-developer` for voice patterns, arcs, relationships

It integrates their output, propagates new facts into the canonical doc ecosystem, and writes manuscript content to the appropriate directory.

For revising existing prose against a review report, use `/worldsmith:revise` instead. This command is for creating new content.

## Assignment

Pass `$ARGUMENTS` to the writer as the assignment. The writer classifies it (lore, scene, character, multi-specialist) during its Phase 2. The command does not pre-classify.

Examples of valid assignments:
- `chapter 5`
- `the opening scene where Maren confronts her mother`
- `Greymoor battle scene`
- `develop the Ashwalker culture`
- `flesh out Sera's backstory`

If `$ARGUMENTS` is empty or ambiguous, the writer will ask via `AskUserQuestion` rather than guess.

## Multi-Work Awareness

If `.worldsmith/project.yaml` exists, this project contains multiple works sharing canonical lore.

**Work selection from `$ARGUMENTS`:**
- If a recognized work name appears in the arguments, scope the draft to that work's manuscript directory.
- If no work name is specified and multiple works exist, default to the **primary work** (first in `project.yaml`) and note this in the launch prompt.
- Arguments can combine work name and assignment: `/worldsmith:draft Hemorrhagic the opening scene` or `/worldsmith:draft "The Policy" chapter 5`.

**Scoping rules:**
- Manuscript output goes to the selected work's `manuscript` directory.
- Canonical docs (shared lore) are always shared. Updates from the draft affect all works that reference the changed lore.
- Work-specific lore (per-work `lore:` directory in `project.yaml`, if present) is also available to the writer.
- For single-work projects (no `project.yaml`), the writer infers the manuscript directory from common conventions (`chapters/`, `manuscript/`, `scenes/`).

Pass the resolved work name, manuscript path, and assignment to the writer agent in the launch prompt.
