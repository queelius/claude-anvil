---
description: Write a per-chapter implementation plan from the relevant design spec
allowed-tools: Read, Write, Glob, Grep, AskUserQuestion
argument-hint: "<chapter-name-or-number>"
---

# /bookwright:plan

Produce a per-chapter implementation plan from the relevant design spec. The plan is the basis for `/bookwright:draft`.

## What it produces

A plan markdown file at `docs/superpowers/plans/YYYY-MM-DD-<chapter-name>.md` with:

- Goal, architecture summary, tech stack, scope, base SHA.
- Source-material list (which papers/sections to reformulate).
- Lessons inherited from prior plans (page-budget discipline, banned-phrase reminders, cross-ref discipline).
- File structure: which chapter and section subfiles get created.
- Cross-reference map: which labels this chapter defines and which it references.
- Per-task list (typically 8-10 tasks: scaffold + per-section + bib notes + exercises + notebook + integration).
- Each task with content checklist, page-budget target, header-comment-block requirement, commit message.

## Steps

1. Read the master spec and the relevant per-Part spec.
2. Read the chapter's stub file in `book/chapters/` if it exists.
3. Walk the per-section spec items from the per-Part spec; turn each into a Task with its content checklist.
4. Add scaffold Task 1, bib-notes Task N-1, exercises Task N, and (if applicable) notebook Task N+1.
5. Save the plan to the plans directory.
6. Report it back; suggest next step: `/bookwright:draft <chapter>` to execute the plan.
