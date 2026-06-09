---
description: Apply fixes from a review report via the rewriter orchestrator (fix-then-verify)
allowed-tools: Read, Glob, Grep, Task
argument-hint: "[review-report-path] [--scope blocking|substantive|minor|all]"
---

# /bookwright:revise

Launch the `rewriter` orchestrator on a review report produced by `/bookwright:review`.

## Behavior

- With a path argument, use that report. Without one, use the newest `docs/superpowers/reviews/YYYY-MM-DD-*.md` that is not itself a `-revision` file; confirm the choice with the user before dispatching.
- Pass the severity scope through (`--scope`, default `all`).
- The rewriter fixes findings (drafting specialists for content, direct edits for mechanical items), verifies each fix with the auditor that found it, rebuilds the book, and writes `<report-basename>-revision.md` next to the source report.

## Distinction from /bookwright:draft and /bookwright:iterate

- `/bookwright:draft` drafts new sections from a chapter plan.
- `/bookwright:revise` is one fix pass over an existing review report.
- `/bookwright:iterate` loops review and revise until convergence.
