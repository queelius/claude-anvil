---
description: Launch multi-agent editorial review (consistency, craft, voice, structure auditors in parallel)
allowed-tools: Read, Write, Glob, Grep, Bash, Task
argument-hint: "[work-name] [scope: full manuscript, or specific chapters e.g. 'chapters 3-5']"
---

# /worldsmith:review

Launch the **reviewer** orchestrator agent for a deep, multi-agent editorial review.

This spawns 4 specialist auditors in parallel (consistency, craft, voice, structure), cross-verifies critical findings, and produces a unified report to `.worldsmith/reviews/YYYY-MM-DD/`.

Pass `$ARGUMENTS` as the review scope. If no scope is specified, review the full manuscript.

This is the thorough review. For a lighter single-pass diagnostic, use `/worldsmith:check`.

## Multi-Work Awareness

If `.worldsmith/project.yaml` exists, this project contains multiple works sharing canonical lore.

**Work selection from `$ARGUMENTS`:**
- If a recognized work name appears in the arguments, scope the review to that work's manuscript directory.
- If no work name is specified and multiple works exist, review the **primary work** (first in `project.yaml`) and note this in the report preamble.
- Arguments can combine work name and scope: `/worldsmith:review Hemorrhagic` or `/worldsmith:review "The Policy" chapters 3-5`.

**Scoping rules:**
- Manuscript files come from the selected work's `manuscript` directory only.
- Canonical docs (lore) are always shared — all works reference the same lore directory.
- Review reports go to `.worldsmith/reviews/YYYY-MM-DD/<work-name>/` for multi-work projects.
- For single-work projects (no project.yaml), behavior is unchanged.

Pass the resolved work name and manuscript path to the reviewer agent in the launch prompt.
