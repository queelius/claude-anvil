# CLAUDE.md — Papermill Plugin

## What This Is

Papermill is a Claude Code plugin for academic research paper lifecycle management. It provides skills (interactive prompt guides) and agents (autonomous subprocesses) that cover the full pipeline from idea to submission.

## Plugin Structure

```
papermill/
├── .claude-plugin/plugin.json    # Plugin manifest
├── commands/                     # Slash commands (thin wrappers triggering skills)
│   ├── init.md
│   ├── status.md
│   ├── thesis.md
│   ├── prior-art.md
│   ├── outline.md
│   ├── experiment.md
│   ├── simulation.md
│   ├── proof.md
│   ├── review.md
│   ├── venue.md
│   └── polish.md
├── skills/                       # Interactive skills (the core logic)
│   ├── init/SKILL.md             # Initialize paper project
│   ├── status/SKILL.md           # Paper state dashboard
│   ├── thesis/SKILL.md           # Extract/refine central claim
│   ├── prior-art/SKILL.md        # Literature survey
│   ├── outline/SKILL.md          # Paper structure
│   ├── review/SKILL.md           # Editorial review
│   ├── venue/SKILL.md            # Publication venue matching
│   ├── experiment/SKILL.md       # Experiment design
│   ├── simulation/SKILL.md       # Monte Carlo methodology
│   ├── proof/SKILL.md            # Proof development
│   └── polish/SKILL.md           # Submission preparation
├── agents/                       # Autonomous agents
│   ├── surveyor.md               # Literature survey agent
│   └── reviewer.md               # Editorial review agent
└── CLAUDE.md                     # This file
```

## File Formats

**Commands** (`commands/<name>.md`): YAML frontmatter with `description`, followed by a one-line instruction triggering the corresponding skill. Invoked as `/papermill:<name>`.

**Skills** (`skills/<name>/SKILL.md`): YAML frontmatter with `name` and `description` (third-person with trigger phrases), followed by markdown body with imperative-form instructions and tool annotations.

**Agents** (`agents/<name>.md`): YAML frontmatter with `name`, `description` (with `<example>` blocks), `tools`, `model`, and `color`, followed by a system prompt for the autonomous agent.

## State File

Skills read and write a `.papermill.md` file in each paper repo. This file has YAML frontmatter (structured project state) and a markdown body (free-form session notes). It persists across Claude Code sessions.

## Editing Guidelines

- Skills should be self-contained — each skill works independently
- Skills should read `.papermill.md` for context but work gracefully if it doesn't exist
- Agents should produce structured output that the calling skill can integrate
- Keep prompts focused: one skill = one activity
