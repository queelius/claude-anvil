---
description: Launch the rewriter orchestrator to apply fixes from a review report
allowed-tools: Read, Glob, Grep, Bash, Task
argument-hint: "[work-name] [review-path | severity HIGH|MEDIUM|LOW | category consistency|craft|voice|structure]"
---

# /worldsmith:revise

Launch the **rewriter** orchestrator agent to apply fixes from a review report.

The rewriter reads the review findings, triages them (auto-fixable, needs judgment, deferred), then for each auto-fixable finding:

1. Dispatches the right writer specialist (`scene-writer`, `lore-writer`, or `character-developer`) to apply the fix
2. Dispatches the matching reviewer specialist (`consistency-auditor`, `craft-auditor`, `voice-auditor`, or `structure-auditor`) to verify the fix resolved the original finding without introducing new issues
3. Retries failed fixes up to twice, then flags for human review

The output is a revision report at the same path as the source review, with before/after for every fix and propagation notes for canonical doc updates.

## Locating the Review Report

If `$ARGUMENTS` contains an explicit path (e.g., `.worldsmith/reviews/2026-03-12/Hemorrhagic/review.md`), use it.

Otherwise locate the latest review report:
- Multi-work project: `.worldsmith/reviews/<latest-date>/<work-name>/review.md`
- Single-work project: `.worldsmith/reviews/<latest-date>/review.md`

Use Bash to find the latest date directory: `ls -t .worldsmith/reviews/ 2>/dev/null | head -1`.

If no review report exists, do NOT silently launch the rewriter. Tell the user: "No review report found in `.worldsmith/reviews/`. Run `/worldsmith:review` first to produce one." Then stop.

## Filters

`$ARGUMENTS` may contain a severity or category filter that scopes the rewriter to a subset of findings.

Severity filters: `HIGH`, `MEDIUM`, `LOW` (case-insensitive).
- `/worldsmith:revise HIGH` applies only HIGH-severity fixes
- `/worldsmith:revise Hemorrhagic HIGH` filters by both work and severity

Category filters: `consistency`, `craft`, `voice`, `structure`.
- `/worldsmith:revise consistency` applies only consistency-domain fixes
- Multiple filters may be combined: `/worldsmith:revise HIGH consistency`

Forward filter values to the rewriter in the launch prompt. The rewriter's Phase 2 (Triage) already groups findings by severity and domain.

## Multi-Work Awareness

If `.worldsmith/project.yaml` exists, this project contains multiple works sharing canonical lore.

**Work selection from `$ARGUMENTS`:**
- If a recognized work name appears in the arguments, scope to that work's review report (`.worldsmith/reviews/<date>/<work-name>/review.md`).
- If no work name is specified and multiple works exist, default to the **primary work** (first in `project.yaml`) and note this in the launch prompt.
- Arguments can combine work name with filters: `/worldsmith:revise Hemorrhagic HIGH consistency`.

**Scoping rules:**
- Manuscript edits target the selected work's `manuscript` directory only.
- Canonical doc updates (shared lore) are universe-wide and propagate to all works that reference the changed lore.
- The rewriter's Phase 5 (Integration + Propagation) handles cross-work propagation when shared lore changes.
- Revision report path mirrors the review report path (multi-work: `.worldsmith/reviews/<date>/<work-name>/revision.md`).

Pass the resolved work name, review report path, and any filters to the rewriter agent in the launch prompt.
