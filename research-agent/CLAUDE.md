# CLAUDE.md: Research Agent Plugin

## What This Is

An autonomous research agent plugin for Claude Code. Given a goal and an optional eval script, the agent runs an unbounded reasoning loop: decomposing, hypothesizing, attempting (proofs, code, simulations, counterexample search), evaluating, and reflecting. It works directly in the target project directory, creating a `.research/` directory for its artifacts.

## Plugin Structure

```
research-agent/
  .claude-plugin/plugin.json   # Plugin manifest
  skills/research/SKILL.md     # Launch skill: parse goal + eval, spawn agent
  commands/research.md          # Thin /research slash command
  agents/researcher.md          # Monolithic autonomous research agent
  CLAUDE.md                     # This file
```

## How It Works

1. User invokes `/research` with a goal (and optionally an eval script path)
2. The command delegates to the skill
3. The skill parses the goal and eval path, then launches the researcher agent
4. The agent creates `.research/` in the target project, then runs autonomously

## Editing Guidelines

- The agent prompt (`agents/researcher.md`) contains the full research methodology. It is intentionally large. Keep sections well-organized with clear headers.
- The skill (`skills/research/SKILL.md`) is thin. Its only job is to parse user intent and launch the agent. Do not put research methodology here.
- The command (`commands/research.md`) is a one-liner. Keep it that way.
- The agent uses `model: opus`, which resolves to the latest Opus (currently 4.7 with the 1M context window when the harness enables it). Long research runs still need file-system persistence (`log.md`, `state.md`, `attempts/`) because individual cycles may compress earlier history; the disk is always the source of truth.

## Capabilities

The researcher has three categories of tools:

1. **File and shell**: `Bash`, `BashOutput`, `KillShell`, `Read`, `Write`, `Edit`, `Glob`, `Grep`. The Bash + BashOutput + KillShell combination lets the researcher launch long-running experiments with `run_in_background: true`, monitor accumulated output, and terminate runs that have stalled.
2. **Research**: `WebSearch`, `WebFetch` for prior-art lookups, paper retrieval, and reference verification.
3. **Delegation**: `Task` for spawning sub-agents that pursue parallel approaches (different proof strategies, different parameter regimes, different literature angles). Sub-agent results return as structured summaries that the researcher integrates into `log.md`.

When extending the agent, prefer giving it more capability in these existing categories over adding new ones. Adding more tool categories without a clear use case dilutes the prompt.
