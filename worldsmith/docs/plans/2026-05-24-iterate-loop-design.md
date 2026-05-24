# Autonomous Iterate Loop: /worldsmith:iterate

**Date**: 2026-05-24
**Status**: Design
**Scope**: New `iterator` orchestrator agent, new `/worldsmith:iterate` command, small extension to the rewriter agent

## Motivation

The reviewer (`/worldsmith:review`) diagnoses. The rewriter (`/worldsmith:revise`) fixes. To take a manuscript from "first draft" to "clean draft," a human currently runs them in alternation: review, look at the report, run revise, run review again, look at the new findings, run revise again, and so on. This works but is slow, manual, and easy to abandon halfway.

`/worldsmith:iterate` automates that loop. Hand it a manuscript and it runs review and revise back-to-back until findings drop below a threshold, a regression-plateau is detected, or an iteration cap is hit. The author resumes control at the end to resolve any high-stake judgment calls the loop deliberately deferred.

The composition is the key insight: this command does not introduce new editorial intelligence. It reuses the existing reviewer and rewriter agents unchanged in their internal logic; it only orchestrates them in a loop with convergence detection and a small extension for stake-classified judgments.

### What breaks today (without iterate)

1. **Multi-pass revision is manual.** The author types five commands and inspects three reports to make one revision pass productive. Most authors run /worldsmith:review once and stop.
2. **Regressions go uncaught.** If a fix introduces a new finding, the only way to catch it is another full /worldsmith:review. Authors rarely do this.
3. **Convergence is invisible.** Without iterate, there is no signal "this manuscript is now clean enough to ship." Authors guess.

### What already works (and is reused)

- The reviewer orchestrator: multi-agent parallel auditors, unified report.
- The rewriter orchestrator: fix-then-verify dispatch with retry logic.
- The triage in rewriter Phase 2: auto-fixable, needs-judgment, defer.
- Multi-work scoping via project.yaml env vars.
- Manuscript path conventions (now reliably enforced by the cliche hook).

## Design

### 1. Architecture

A new orchestrator agent `worldsmith:iterator` drives the loop. A new thin command `/worldsmith:iterate` launches it. The reviewer and rewriter are reused unchanged in their internal protocols (one optional rewriter extension noted below).

```
/worldsmith:iterate [args]
        |
        v
Task: worldsmith:iterator
        |
        for round in 1..max_iterations:
        |       |
        |       Task: worldsmith:reviewer  (writes round report)
        |       |
        |       (count findings; check convergence)
        |       |
        |       Task: worldsmith:rewriter  (iterate-mode: best-guess low/medium stake, defer high)
        |       |
        |       (read revision report; collect deferred-judgments)
        |
        AskUserQuestion (batch all deferred-judgments)
        |
        Task: worldsmith:rewriter  (final round with user answers as fix guidance)
        |
        Write summary at .worldsmith/iterate/<timestamp>/<work>/summary.md
        |
        Return to user
```

### 2. The iterator agent

New file: `agents/iterator.md`. System prompt structure mirrors reviewer.md and rewriter.md.

**Tools**: Read, Write, Glob, Grep, Bash, Task, AskUserQuestion.

**Workflow** (numbered phases, like the other orchestrators):

**Phase 1: Comprehension.** Read project CLAUDE.md, project.yaml if multi-work, current manuscript state. Resolve the target work. Parse args.

**Phase 2: Initialize state.** Create iterate session directory at `.worldsmith/iterate/YYYY-MM-DD-HHMMSS/<work>/`. Initialize `state.md` with config (max_iterations, threshold, pause-on, work scope) and empty round log.

**Phase 3: Iteration loop.** For round in 1..max_iterations:

1. Launch reviewer via Task. Instruct it to write its report to `<session-dir>/round-NNN/review.md` instead of the default `.worldsmith/reviews/` path. Pass work scope.
2. Read the round's review.md. Parse findings. Count by severity (HIGH / MEDIUM / LOW) and category (consistency / craft / voice / structure).
3. Check convergence: if HIGH count == 0 (default threshold), break with reason `converged`. If round == max_iterations, break with reason `cap`. (Plateau check happens after rewriter.)
4. Launch rewriter via Task. Pass iterate-mode flags in the prompt: `pause-on=<high|all|none>`, `output-dir=<session-dir>/round-NNN/`, `mode=iterate`. The rewriter writes revision.md to the round directory.
5. Read the round's revision.md. Parse outcomes: fixed_count, deferred_high_stake list (with location + original finding text + suggested options), retry-failures.
6. Append to deferred_judgments queue.
7. Plateau check: if fixed_count == 0 and deferred_high_stake count did not change (no new judgments added), break with reason `plateau` (the loop is no longer making progress).
8. Update `state.md` round log.

**Phase 4: Deferred-judgment checkpoint** (only if deferred_judgments is non-empty):

1. If deferred_judgments count > 12 (3 AskUserQuestion batches of 4), present a meta-question first: "12+ judgment findings deferred. How to proceed? Resolve all individually / Best-guess all / Stop here and I will resolve manually."
2. Otherwise (or after user picks "resolve individually"): batch deferred judgments into AskUserQuestion calls (max 4 questions per call, max 4 calls per session to keep checkpoint reasonable, anything beyond is dropped to a `unresolved.md` for manual handling).
3. Each judgment becomes one question with options derived from the rewriter's suggested directions.
4. Collect user answers.

**Phase 5: Final revision round** (only if there were user answers from Phase 4):

1. Launch rewriter once more via Task in `mode=final-revise` with the user answers passed as fix guidance per finding. Writes to `<session-dir>/final-revision/revision.md`.

**Phase 6: Summary.** Write `<session-dir>/summary.md`:

- Run config (max_iterations, threshold, pause-on, work)
- Per-round table: round, HIGH/MEDIUM/LOW counts, fixed_count, deferred_high_stake delta, regressions introduced
- Convergence outcome: `converged | cap | plateau | manual-stop`
- Deferred judgments resolved: count and brief list
- Unresolved findings (if any)
- Time elapsed (best-effort, from session dir timestamp to now)
- Token estimate (best-effort): `rounds * (reviewer_calls_per_round + rewriter_calls_per_round)`

Return a short string to the main session with summary stats and the path to summary.md.

### 3. Convergence criterion

**Default**: HIGH-severity findings count == 0. The loop stops as soon as no HIGH findings remain, even if MEDIUM and LOW persist.

**Rationale**: User asked for aggression, but stop-on-zero-total is impossible in practice (LOW findings are mostly stylistic suggestions, never fully zero). HIGH-only is the aggressive-but-achievable target.

**Configurable** via `--threshold`:
- `--threshold high` (default): stop when HIGH count == 0
- `--threshold medium`: stop when HIGH and MEDIUM both == 0 (more thorough, more iterations)
- `--threshold zero`: stop when total findings == 0 (will almost always hit the cap)

### 4. Iteration cap

**Default**: 8 rounds. **Configurable** via `--max-iterations N`.

**Rationale**: 8 rounds × roughly 5-15 minutes of subagent work per round = 45 minutes to 2 hours of autonomous run time. That is enough to make real progress; longer and the user probably wants to be in the loop themselves. Authors who want longer just override.

### 5. Plateau detection

After each rewriter round, compute fixed_count_this_round. If a round produces zero fixes (rewriter could not auto-fix anything new and added no new deferred-judgments), the loop has plateaued: subsequent rounds will not make progress. Break with reason `plateau`.

**Why**: Without this, the loop wastes the remaining iteration budget on rounds that produce identical findings.

**Edge**: a round that adds new deferred-judgments but auto-fixes zero is still progress (the judgments are queued for the user). Do not plateau on that case.

### 6. Stake-classified judgments (rewriter extension)

The rewriter's Phase 2 (Triage) currently outputs three buckets: auto-fixable, needs-judgment, defer. The needs-judgment bucket gains an optional metadata field:

```
stake: low | medium | high
```

**Stake heuristics** (documented in rewriter agent prompt):

- **low**: Cosmetic or stylistic. "This sentence could be tighter, here are two phrasings." Best-guess pick is safe.
- **medium**: Style or structure that affects a single passage. "The transition into this scene could go three ways." Best-guess pick is defensible with documented rationale.
- **high**: Plot, character, or world stakes. "Should this character betray the protagonist?" "Does this scene change the antagonist's motivation?" Best-guess is dangerous; must defer.

The rewriter, when invoked from `/worldsmith:revise` directly, populates the stake field but does nothing differently (its existing AskUserQuestion-per-judgment flow continues). The iterator uses the stake field to decide best-guess vs defer.

This keeps `/worldsmith:revise` unchanged in user-visible behavior. The stake field is new metadata that callers can opt-in to consume.

### 7. Iterate-mode rewriter behavior

When the iterator launches the rewriter, the launch prompt carries:

```xml
<mode>iterate</mode>
<pause-on>high</pause-on>
<output-dir>.worldsmith/iterate/<timestamp>/<work>/round-NNN/</output-dir>
<instructions>
You are running in iterate mode. Do NOT use AskUserQuestion.

For needs-judgment findings:
- If pause-on=high and stake is low or medium: best-guess fix with rationale in revision report
- If pause-on=high and stake is high: skip the fix, list in a "deferred-judgments" section of the revision report
- If pause-on=all: skip all judgment findings, defer to the deferred-judgments section
- If pause-on=none: best-guess everything regardless of stake

Defer findings (structural rework) are skipped as normal.

The revision report must include a machine-readable deferred-judgments section structured as:

```yaml
deferred-judgments:
  - finding-id: <unique>
    location: <file:line>
    severity: HIGH|MEDIUM|LOW
    stake: high
    original-finding: <text>
    suggested-options:
      - <option-1>
      - <option-2>
```

This is what the iterator reads at Phase 3 step 5 above.
</instructions>
```

### 8. The /worldsmith:iterate command

Thin wrapper, mirrors `/worldsmith:draft` and `/worldsmith:revise` in shape.

**Frontmatter**:

```yaml
---
description: Autonomous review-fix-review loop until convergence or iteration cap
allowed-tools: Read, Glob, Grep, Task
argument-hint: "[work-name] [--max-iterations N] [--threshold high|medium|zero] [--pause-on high|all|none]"
---
```

**Body**: brief description of the iterate loop, the launch via Task to the iterator agent, multi-work scoping section identical in shape to `/worldsmith:draft` and `/worldsmith:revise`. Forwards `$ARGUMENTS` (less the resolved work name) to the iterator.

### 9. Output paths

All iterate session artifacts live under `.worldsmith/iterate/YYYY-MM-DD-HHMMSS/<work>/`. The timestamp suffix allows multiple iterate runs per day without overwrite.

```
.worldsmith/iterate/2026-05-24-143015/the-policy/
  state.md                     # config + round log
  summary.md                   # final user-facing summary
  unresolved.md                # any judgments dropped from checkpoint
  round-001/
    review.md                  # reviewer output
    revision.md                # rewriter output with deferred-judgments section
  round-002/
    review.md
    revision.md
  ...
  final-revision/
    revision.md                # post-checkpoint rewriter output
```

The existing `.worldsmith/reviews/` directory is untouched by iterate. Direct `/worldsmith:review` invocations still write there as before.

### 10. Cost considerations

A single iterate run with default settings (8 rounds, 4 reviewer specialists in parallel per round + rewriter fix-and-verify dispatches per finding) costs roughly 80-150 specialist agent invocations and several million tokens. This is the biggest single-command cost in the worldsmith plugin.

**Mitigations**:
- Default cap of 8 rounds. Lower cap = lower cost.
- Plateau break: most runs converge in 3-5 rounds, not 8.
- The user receives the cost estimate in the summary report so future runs can calibrate.
- Optional flag `--dry-run` (deferred to v2 of iterate): runs the first round only, reports projected findings and estimated cost for full run, asks user to confirm. Not in scope for this design.

### 11. Configurable flags summary

| Flag | Default | Effect |
|------|---------|--------|
| `--max-iterations N` | 8 | Cap on iteration count |
| `--threshold high\|medium\|zero` | `high` | Convergence severity gate |
| `--pause-on high\|all\|none` | `high` | Which judgments to defer to end-of-loop checkpoint |

Flag parsing in `$ARGUMENTS` uses simple key=value or `--flag value` patterns. The iterator handles parsing in Phase 1 and validates.

### 12. Backward compatibility

- Reviewer agent: unchanged.
- Rewriter agent: gains an optional `stake` field on needs-judgment findings. Existing `/worldsmith:revise` flow is identical to today.
- /worldsmith:review and /worldsmith:revise commands: unchanged.
- Iterate is purely additive.

## Out of scope (deferred)

- **Resume from partial state.** Mid-loop interruption leaves a partial session dir. No `--resume` flag in v1. Future enhancement: read state.md and continue from last completed round.
- **Dry-run mode.** Run only round 1 to project cost. Future enhancement.
- **Per-category convergence.** Currently threshold is global (HIGH overall). Future: "stop when consistency HIGH == 0 even if craft HIGH remains."
- **Cross-work iterate.** Multi-work projects iterate one work at a time. No combined-universe iterate. Likely fine since manuscripts are work-scoped anyway.
- **Test harness for iterator.** The iterator's behavior is hard to test without running real reviewer/rewriter subagents (which would be flaky and slow). Defer to manual smoke test on a real manuscript.

## Versioning

New command, new agent, small additive change to rewriter: minor bump 0.10.0 -> 0.11.0.
