---
description: Autonomous review-fix-review loop until convergence or iteration cap
allowed-tools: Read, Glob, Grep, Task
argument-hint: "[work-name] [--max-iterations N] [--threshold high|medium|zero] [--pause-on high|all|none]"
---

# /worldsmith:iterate

Launch the **iterator** orchestrator agent to drive a manuscript toward clean autonomously.

The iterator composes `/worldsmith:review` and `/worldsmith:revise` in a loop:

1. Run the reviewer (4 specialists in parallel)
2. Count findings; check convergence
3. If not converged, run the rewriter in iterate-mode (best-guess on routine creative calls, defer high-stake judgments)
4. Repeat until convergence, regression-plateau, or iteration cap
5. At the end, batch all deferred high-stake judgments into one `AskUserQuestion` checkpoint
6. Run one final revision pass with the user's answers
7. Write a summary report

The author resumes control only at the end-of-loop checkpoint, not per-finding. Use this for finishing-pass work on manuscripts that already have a complete draft.

## Defaults

| Flag | Default | Meaning |
|------|---------|---------|
| `--max-iterations N` | 8 | Hard cap on rounds |
| `--threshold high\|medium\|zero` | `high` | Stop when no findings remain at this severity or worse |
| `--pause-on high\|all\|none` | `high` | Which judgments to defer to the end-of-loop checkpoint |

Default behavior is aggressive: iterate until zero HIGH findings remain (up to 8 rounds), best-guess routine creative judgments, only pause for plot/character/world-stakes decisions.

## Cost Warning

A full iterate run with defaults costs roughly 80-150 specialist agent invocations and several million tokens. This is the most expensive single command in the worldsmith plugin. Use it for finishing passes on real drafts, not every-edit cleanup.

The summary report includes a best-effort cost estimate so future runs can be calibrated.

## Stopping early

The iterator stops earlier than the cap when:

- **Converged**: no findings at the configured threshold remain
- **Plateau**: a round produces zero new fixes and zero new deferred judgments (no further progress possible)

Both are reported in the final summary with the reason.

## Output

All session artifacts live under `.worldsmith/iterate/<timestamp>/<work>/`:

- `state.md`: run configuration and per-round log
- `summary.md`: final user-facing summary with cost estimate
- `round-NNN/review.md` + `round-NNN/revision.md`: per-round artifacts
- `final-revision/revision.md`: post-checkpoint revision (if user answered any deferred judgments)
- `unresolved.md`: any judgments dropped from the checkpoint (only if more than 16 deferred)

The default `.worldsmith/reviews/` directory is untouched. Direct `/worldsmith:review` invocations still write there as before.

## Multi-Work Awareness

If `.worldsmith/project.yaml` exists, this project contains multiple works sharing canonical lore.

**Work selection from `$ARGUMENTS`:**
- If a recognized work name appears in the arguments, scope iteration to that work.
- If no work name is specified and multiple works exist, default to the **primary work** (first in `project.yaml`) and note this in the launch prompt.
- Arguments can combine work name and flags: `/worldsmith:iterate Hemorrhagic --max-iterations 12 --pause-on all`.

**Scoping rules:**
- Manuscript edits target the selected work's `manuscript` directory only.
- Canonical doc updates (shared lore) propagate across works via the rewriter's Phase 5.
- Session artifacts go under the work's subdirectory in `.worldsmith/iterate/<timestamp>/<work>/`.

Pass the resolved work name and all flags to the iterator agent in the launch prompt.

## When NOT to use iterate

- **Active drafting.** Iterate is for finishing passes on existing drafts. Use `/worldsmith:draft` to add new content.
- **Single bug fix.** If you know exactly what to change, edit directly or use `/worldsmith:change`.
- **Per-finding interactivity.** If you want to make creative decisions on every judgment, use `/worldsmith:revise` instead. Iterate is for autonomous runs that surface only the highest-stakes calls.
