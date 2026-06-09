---
name: synthesize
description: >-
  Force a research-agent run to conclude. Launches the researcher in
  synthesis mode: it reads state.md and log.md, writes
  .research/synthesis.md with outcome, key findings, failed approaches,
  open questions, and recommendations, then exits. Use when current
  results are good enough or the agent is stalling.
---

# Synthesize Research

Force the researcher to write its final synthesis and conclude, even if
it would otherwise continue exploring. If the user names a branch, add
`<branch>name</branch>` to the launch prompt to conclude only that branch
(output: `.research/branches/<name>/synthesis.md`). A main-line synthesis
automatically compares all branches.

## When to use

- Current results are good enough; lock them in
- The agent is stalling (eval flat/declining for several cycles)
- A deadline forces a conclusion regardless of completeness
- The user wants a checkpoint before pivoting to a related research line

## Step 1: Verify .research/ exists

Use the Read tool on `.research/state.md`. If the file does not exist, tell the user there is no research to synthesize and suggest `/research-agent:research` to start one.

## Step 2: Check whether already synthesized

Use the Glob tool for `.research/synthesis.md`. If it already exists, ask the user whether they want to overwrite (re-synthesize, which makes sense after `/research-agent:resume` reopened the concluded run on explicit confirmation) or stop.

## Step 3: Launch the researcher with synthesis framing

Spawn the researcher agent (Agent tool, subagent_type `research-agent:researcher`) with this prompt:

    <mode>synthesize</mode>

    <working_directory>
    {absolute path to current working directory}
    </working_directory>

    Synthesize your research and conclude. Do NOT run new attempts. Do
    NOT start new cycles. The user has decided to lock in current
    results.

    Step 1: Read .research/state.md and .research/log.md in full to
    recall every sub-problem, hypothesis, and attempt.

    Step 2: Update .research/state.md with final statuses. Mark every
    sub-problem as one of: resolved, abandoned, or unresolved. Mark
    every hypothesis as one of: confirmed, refuted, inconclusive.

    Step 3: Write .research/synthesis.md per the Termination Protocol
    in your system prompt. Required sections: Goal, Outcome (one
    paragraph), Key Findings, Failed Approaches, Open Questions,
    Recommendations.

    Step 4: Append a final entry to .research/log.md noting the forced
    conclusion and pointing at synthesis.md.

    Be honest in the synthesis. If the goal was not achieved, say so
    plainly. If results are partial, describe their scope precisely.
    The synthesis is the single document a future reader will rely on.

## Step 4: Inform the user

After launching, tell the user:

> Researcher synthesizing. It will read state.md and log.md, finalize statuses, and write .research/synthesis.md. This usually completes in one cycle (no new attempts).
