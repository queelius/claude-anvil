---
description: Launch the writer orchestrator for prose drafting (whole chapter or single section)
allowed-tools: Read, Glob, Grep, Task
argument-hint: "<chapter-name | section-path>"
---

# /bookwright:draft

Launch the `writer` orchestrator agent to draft prose. Argument can be a whole chapter (the writer iterates through its per-section tasks) or a single section path (one task end-to-end).

## What the writer does (briefly)

For each section task in the relevant plan:

1. Reads the plan's content checklist and content-source list.
2. Dispatches the appropriate drafting specialist:
   - `section-writer` for narrative prose.
   - `notebook-author` if the task includes a paired notebook.
   - `source-reformulator` if the task requires reformulating an external paper.
3. After the draft commits, dispatches `spec-auditor` and `quality-auditor` in parallel for review.
4. If either auditor surfaces substantive findings, re-dispatches section-writer with the finding as input and re-runs the relevant auditor to verify the fix.
5. Reports the task's commit SHAs and word counts back to the user.

## When to use what

- `/bookwright:draft chapter5` runs ALL section tasks of chapter 5 in sequence (scaffold first, then sections, then bib + exercises, then notebook).
- `/bookwright:draft ch05/bloom-from-scratch.tex` runs only that one section task.

For per-Part or full-book integration verification, use `/bookwright:integrate` instead. For editorial review of an existing chapter (no drafting), use `/bookwright:review`.
