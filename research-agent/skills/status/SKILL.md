---
name: status
description: >-
  Show the current state of an in-flight research-agent run from
  .research/state.md, log.md, and attempts/. Read-only summary of cycles,
  sub-problems, hypothesis statuses, eval trend, and current focus.
---

# Research Status

Show the current state of an in-flight research-agent run. Read-only:
this skill never modifies the .research/ directory or relaunches the
agent.

## Step 1: Locate .research/

Use the Glob tool to confirm `.research/` exists in the working directory.
If absent, tell the user there is no research run here and suggest
`/research-agent:research` to start one.

## Step 2: Read core state files

Read in order (Read tool), degrading gracefully on partial runs:

1. `.research/goal.md` for the original goal and eval script path (the only required file; if missing, treat the directory as not a research run)
2. `.research/state.md` if it exists; when missing, report "initialized, no cycles yet" and skip the sub-problem and hypothesis sections
3. `.research/log.md` if it exists, for the last 10 cycle entries (read the full file if it is short, otherwise tail with Bash: `tail -200 .research/log.md`); when missing, skip the recent-activity section
4. `.research/scores.jsonl` if it exists: one JSON object per eval run; this is the preferred source for the eval trend (fall back to parsing log.md when absent)

## Step 3: Inventory artifacts

Use Glob and Bash to count:

- `attempts/*/notes.md`: total attempts; list the most recent 3 with their
  slugs and one-line summaries
- `findings/*`: confirmed results promoted out of attempts/
- `synthesis.md`: present means the run has concluded (note this prominently)

## Step 4: Format the report

Output a structured summary:

```markdown
# Research Status: {one-line goal}

## Goal
{verbatim from goal.md, trimmed if very long}

## Run state
- Total cycles logged: N
- Last cycle: {timestamp} in {phase}
- Current focus: {from state.md}
- Concluded: yes (synthesis.md present) | no

## Sub-problems
| Status | Count |
|--------|-------|
| open | N |
| in-progress | N |
| resolved | N |
| abandoned | N |
| unresolved (terminal) | N |

Currently focused sub-problem: {description}

## Hypotheses
| Status | Count |
|--------|-------|
| untested | N |
| confirmed | N |
| refuted | N |
| inconclusive | N |

## Recent activity
- {date} Cycle N: {hypothesis snippet} via {modality} -> {pass/fail}
- ... (last 5 cycles)

## Eval trend
- Latest score: X (or "self-evaluation")
- Best score: Y
- Trend over last 5 cycles: improving | flat | declining

## Attempts inventory
- {N} attempts total
- {M} findings promoted
- Most recent attempts:
  - attempts/{NNN}-{slug}: {one-line note}
  - ...
```

## Step 5: Suggest next actions

End the report with a brief next-actions block based on the run state:

- If concluded (`synthesis.md` present): point the user to `.research/synthesis.md`
- If active and progressing: suggest `/research-agent:resume` to continue
- If stalled (3+ failed cycles in last 5, or flat/declining eval trend): suggest `/research-agent:synthesize` to lock in current results, or note that the researcher should pivot strategies on next resume
- If just started (under 3 cycles): note that it is too early to evaluate trend
