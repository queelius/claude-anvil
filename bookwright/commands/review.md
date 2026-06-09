---
description: Heavy multi-agent editorial review (4 specialist auditors in parallel)
allowed-tools: Read, Glob, Grep, Task
argument-hint: "[section | chapter | part | book] [name]"
---

# /bookwright:review

Launch the `reviewer` orchestrator. Dispatches all four review specialists in parallel: `spec-auditor`, `quality-auditor`, `math-auditor`, `cross-ref-auditor`. Synthesizes the findings into a unified report.

## Scope

- `section <path>`: one section. Single-pass review by all four auditors.
- `chapter <name>`: all sections of the named chapter.
- `part <name>`: all chapters of the named Part.
- `book`: everything (heavy; do not use casually).

## Output

A unified review report saved to `docs/superpowers/reviews/YYYY-MM-DD-<scope>.md`, with sections from each auditor: spec compliance, quality (cold-read), math correctness, cross-references. To apply fixes, run `/bookwright:draft` with the review report path as input (the writer orchestrator's fix mode). `/bookwright:integrate` is read-only verification, not a fix path.

## Distinction from /bookwright:check and /bookwright:integrate

- `/bookwright:check` is fast, mechanical, no judgment.
- `/bookwright:review` is heavy, editorial, full multi-agent dispatch.
- `/bookwright:integrate` is per-Part or full-book verification with a written integration-pass record.
