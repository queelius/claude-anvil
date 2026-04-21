---
name: research
description: >-
  Launch an autonomous research agent that iterates toward a goal through
  proofs, code, simulations, tests, and counterexample search.
  Fire-and-forget mode: the agent runs autonomously and writes all results
  to .research/ in the target project.
---

# Autonomous Research Agent

Launch an autonomous research agent that iterates toward a goal through proofs, code, simulations, tests, and counterexample search.

## Step 1: Parse the Goal

Read the user's message to extract:

1. **Goal** (required): The natural-language research objective. This is the main content of the user's message.
2. **Eval script** (optional): A path to an executable script. Look for phrases like "eval script at", "use ... as eval", or a path ending in `.sh`, `.py`, or similar.

If the goal is unclear, ask the user to clarify before proceeding. If no eval script is mentioned, the agent will self-evaluate.

## Step 2: Verify Eval Script (if provided)

If an eval script path was given, verify it exists (Read tool). If it does not exist, tell the user and ask whether to proceed with self-evaluation instead.

## Step 3: Launch the Agent

Spawn the researcher agent (Agent tool) with this prompt structure:

    <goal>
    {the user's research goal, verbatim}
    </goal>

    <eval>
    {path to eval script, or "none - use self-evaluation"}
    </eval>

    <working_directory>
    {current working directory}
    </working_directory>

    Begin your research. Create .research/ and start the DECOMPOSE phase.

The agent runs autonomously from here. Inform the user:

> Research agent launched. It will work autonomously in this directory, writing progress to `.research/log.md`. When it finishes, the synthesis will be at `.research/synthesis.md`.
