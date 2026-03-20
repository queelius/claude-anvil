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
- The agent uses `model: opus` for maximum context window (1M tokens).
