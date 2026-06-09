---
description: Per-Part or full-book integration check with a written integration-pass record
allowed-tools: Read, Write, Bash, Glob, Grep, Task
argument-hint: "[part | book] [name]"
---

# /bookwright:integrate

Run the integration check that mirrors the Bernoulli textbook's Plan 4/8/13/15/18 Task 10 pattern.

## What it does

1. Run `/bookwright:check book` (or the appropriate scope) and capture results.
2. Verify the cross-reference map by dispatching `bookwright:cross-ref-auditor` (Task tool): chapter labels defined exactly once, expected forward refs match the baseline, no unexpected unresolved refs. The auditor also generates the cross-reference map table for the record.
3. Compute per-Part page totals against spec targets.
4. Run a running-thread inventory across the chapters in scope.
5. Run the soul-voice and macro-leak audits.
6. Write an integration-pass record to `docs/superpowers/plans/YYYY-MM-DD-<scope>-integration-pass.md` with:
   - Date, plan reference, HEAD SHA at integration time.
   - Verification results table.
   - Known deferred items (documented forward refs that resolve in later work).
   - Open follow-ups for the polish plan.
7. Commit the record.

## When to run it

- After completing the last chapter of a Part.
- After completing the full book draft (full-book scope).
- Before publishing to verify the deferred-items list is empty or appropriately documented.
