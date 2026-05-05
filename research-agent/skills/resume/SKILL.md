---
name: resume
description: >-
  Resume an interrupted research-agent run. Re-launches the researcher
  with instructions to read .research/state.md and log.md, reorient, and
  continue from the documented current focus. Use after a context
  compression, session restart, or explicit pause.
---

# Resume Research

Continue a paused or interrupted research-agent run.

## Step 1: Verify .research/ exists

Use the Read tool on `.research/state.md`. If the file does not exist, tell the user there is no research to resume here and suggest `/research-agent:research` to start fresh.

## Step 2: Quick state preview

Use Read tool to load `.research/state.md` and the last 5 entries from `.research/log.md`. Show the user a one-paragraph preview of what the researcher will pick up:

> Resuming research on "{goal}". Current focus: {from state.md}. Last cycle was {N} on {date}: {modality} -> {result}. Outstanding sub-problems: {count open}. Untested hypotheses: {count untested}.

## Step 3: Launch the researcher with resume framing

Spawn the researcher agent (Agent tool, subagent_type `research-agent:researcher`) with this prompt:

    <mode>resume</mode>

    <working_directory>
    {absolute path to current working directory}
    </working_directory>

    Resume your research from disk. Do NOT recreate .research/ or
    overwrite goal.md.

    Step 1: Read .research/state.md in full to reload current beliefs,
    sub-problem statuses, hypothesis statuses, and current focus.

    Step 2: Read the last 15 entries of .research/log.md to recall recent
    activity, including any failed attempts and pivots.

    Step 3: Continue your research loop from the documented "Current
    focus" in state.md. Run cycles as normal: DECOMPOSE if needed,
    HYPOTHESIZE, ATTEMPT, EVALUATE, REFLECT. Append to log.md after
    every cycle.

    If state.md indicates the goal has been concluded (synthesis.md
    exists), do NOT run new cycles; tell the orchestrator the research
    is already complete and point at synthesis.md.

## Step 4: Inform the user

After launching, tell the user:

> Researcher resumed. It has reloaded state from .research/state.md and is continuing from the current focus. Use `/research-agent:status` to check progress, or `/research-agent:synthesize` to force conclusion.
