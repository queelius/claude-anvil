---
description: Quick reference for bookwright commands, agents, and skills
allowed-tools: Read
argument-hint: ""
---

# /bookwright:help

Print a quick reference.

## Commands

- `/bookwright:init [name]`: scaffold a fresh book project.
- `/bookwright:design [master | partN]`: write a design spec via Socratic dialogue.
- `/bookwright:plan <chapter>`: write a per-chapter implementation plan from the spec.
- `/bookwright:draft <chapter | section>`: launch the writer orchestrator.
- `/bookwright:notebook <chapter>`: draft and execute the paired notebook.
- `/bookwright:check [scope]`: mechanical diagnostics (build, labels, page audit, threads, hooks).
- `/bookwright:review [scope]`: heavy multi-agent editorial review.
- `/bookwright:revise [report]`: apply a review report's findings (fix-then-verify).
- `/bookwright:iterate [scope]`: review-fix-review loop until convergence.
- `/bookwright:integrate [scope]`: per-Part or full-book integration check plus written record.
- `/bookwright:help`: this reference.

## Agents (v0.2)

Orchestrators: `writer`, `reviewer`, `rewriter`, `iterator`. Drafting specialists: `section-writer`, `notebook-author`, `source-reformulator`. Review specialists: `spec-auditor`, `quality-auditor`, `math-auditor`, `cross-ref-auditor`.

## Skills (auto-triggered)

- `bookwright:textbook-methodology`: prose-drafting tasks.
- `bookwright:cross-reference-discipline`: cross-referenced sections.
- `bookwright:notebook-paired-with-prose`: notebook tasks.

## Hooks

- Soul-voice (banned-phrase enforcement): provided by the `soul` plugin.
- LaTeX-macro-leak: provided by bookwright itself.

## Typical workflow

1. `/bookwright:init mybook` then `cd mybook`.
2. `/bookwright:design master`, then `/bookwright:design part1`, etc.
3. For each chapter: `/bookwright:plan chN`, then `/bookwright:draft chN`.
4. Chapter polish: `/bookwright:review chN` then `/bookwright:revise`, or just `/bookwright:iterate chN`.
5. Per-Part close: `/bookwright:integrate part1`.
6. Full-book close: `/bookwright:integrate book`.
