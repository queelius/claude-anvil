# CLAUDE.md: Research Agent Plugin

## What This Is

An autonomous research agent plugin for Claude Code. Given a goal and an optional eval script, the agent runs an unbounded reasoning loop: decomposing, hypothesizing, attempting (proofs, code, simulations, counterexample search), evaluating, and reflecting. It works directly in the target project directory, creating a `.research/` directory for its artifacts.

## Plugin Structure

```
research-agent/
  .claude-plugin/plugin.json    # Plugin manifest
  skills/research/SKILL.md      # Launch skill: parse goal + eval, spawn agent
  skills/status/SKILL.md        # Read-only status of an in-flight run
  skills/resume/SKILL.md        # Continue an interrupted run
  skills/synthesize/SKILL.md    # Force the run to conclude with synthesis.md
  commands/research.md          # /research-agent:research (launch)
  commands/status.md            # /research-agent:status
  commands/resume.md            # /research-agent:resume
  commands/synthesize.md        # /research-agent:synthesize
  agents/researcher.md          # The autonomous research agent (mode-aware)
  CLAUDE.md                     # This file
```

## How It Works

The agent has three modes of operation, selected by the XML tags the
launching skill passes:

- **fresh**: `<goal>...</goal>` plus `<eval>...</eval>`. Used by `/research-agent:research`. Creates `.research/`, writes goal.md, optionally runs the eval baseline, then begins the DECOMPOSE phase.
- **resume**: `<mode>resume</mode>`. Used by `/research-agent:resume`. Reads state.md and log.md, reorients, then continues from the documented current focus.
- **synthesize**: `<mode>synthesize</mode>`. Used by `/research-agent:synthesize`. Reads state.md and log.md, finalizes statuses, writes synthesis.md, exits without starting new cycles.

The status skill is **not** an agent dispatch: it reads `.research/` files
directly and produces a structured summary. This is faster, cheaper, and
deterministic, and it never accidentally restarts the agent.

## Editing Guidelines

- The agent prompt (`agents/researcher.md`) contains the full research methodology and mode dispatch. It is intentionally large. Keep sections well-organized with clear headers.
- Each skill (`skills/<name>/SKILL.md`) is thin. The skill's job is to parse user intent and prepare the right XML tags for the agent (or, for status, read files directly). Do not put research methodology in skills.
- Commands are one-liners. Keep them that way.
- The agent uses `model: opus`, which resolves to the latest Opus (currently 4.7 with the 1M context window when the harness enables it). Long research runs still need file-system persistence (`log.md`, `state.md`, `attempts/`) because very long runs may compress earlier history; the disk is always the source of truth.

When adding a new mode (e.g., a "branch" mode that forks a research run from a checkpoint), edit four files in lockstep: a new skill, a new command, a new section in the agent's Initialization documenting the mode, and the mode list in this file.

## Capabilities

The researcher has three categories of tools:

1. **File and shell**: `Bash`, `BashOutput`, `KillShell`, `Read`, `Write`, `Edit`, `Glob`, `Grep`. The Bash + BashOutput + KillShell combination lets the researcher launch long-running experiments with `run_in_background: true`, monitor accumulated output, and terminate runs that have stalled.
2. **Research**: `WebSearch`, `WebFetch` for prior-art lookups, paper retrieval, and reference verification.
3. **Delegation**: `Task` for spawning sub-agents that pursue parallel approaches (different proof strategies, different parameter regimes, different literature angles). Sub-agent results return as structured summaries that the researcher integrates into `log.md`.

When extending the agent, prefer giving it more capability in these existing categories over adding new ones. Adding more tool categories without a clear use case dilutes the prompt.
