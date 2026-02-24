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
│   ├── review/SKILL.md           # Multi-agent editorial review
│   ├── venue/SKILL.md            # Publication venue matching
│   ├── experiment/SKILL.md       # Experiment design
│   ├── simulation/SKILL.md       # Monte Carlo methodology
│   ├── proof/SKILL.md            # Proof development
│   └── polish/SKILL.md           # Submission preparation
├── agents/                       # Autonomous agents
│   ├── reviewer.md               # Multi-agent review orchestrator (area chair)
│   ├── surveyor.md               # Literature survey agent
│   ├── literature-scout-broad.md # Broad field survey for review grounding
│   ├── literature-scout-targeted.md # Direct comparison finder for review
│   ├── logic-checker.md          # Proof and argument verification
│   ├── novelty-assessor.md       # Contribution evaluation against literature
│   ├── methodology-auditor.md    # Experimental design and statistical rigor
│   ├── prose-auditor.md          # Writing quality and narrative structure
│   ├── citation-verifier.md      # Reference accuracy and completeness
│   └── format-validator.md       # Build verification and venue compliance
└── CLAUDE.md                     # This file
```

## File Formats

**Commands** (`commands/<name>.md`): YAML frontmatter with `description`, followed by a one-line instruction triggering the corresponding skill. Invoked as `/papermill:<name>`.

**Skills** (`skills/<name>/SKILL.md`): YAML frontmatter with `name` and `description` (third-person with trigger phrases), followed by markdown body with imperative-form instructions and tool annotations.

**Agents** (`agents/<name>.md`): YAML frontmatter with `name`, `description` (with `<example>` blocks), `tools`, `model`, and `color`, followed by a system prompt for the autonomous agent.

## State File

Skills read and write a `.papermill/state.md` file in each paper repo. This file has YAML frontmatter (structured project state) and a markdown body (free-form session notes). It persists across Claude Code sessions.

The `.papermill/` directory also contains:
- `reviews/YYYY-MM-DD/` — multi-agent review output (unified report + individual specialist reports)

Legacy: older projects may have a `.papermill.md` file in the project root. The init skill auto-migrates this to `.papermill/state.md`.

## Multi-Agent Review System

The review skill (`/papermill:review`) launches a multi-agent review orchestrated by the `reviewer` agent (area chair). The workflow:

1. **Comprehension** — orchestrator reads paper and state
2. **Literature grounding** — 2 scouts (broad + targeted) run in parallel
3. **Specialist review** — 6 reviewers run in parallel, each receiving literature context
4. **Cross-verification** — critical/low-confidence findings get second opinions
5. **Synthesis** — deduplicate, resolve conflicts, calibrate severity, check for blind spots
6. **Report** — unified report + individual specialist reports written to `.papermill/reviews/`

## Editing Guidelines

- Skills should be self-contained — each skill works independently
- Skills should read `.papermill/state.md` for context but work gracefully if it doesn't exist
- Agents should produce structured output that the calling skill can integrate
- Keep prompts focused: one skill = one activity
- Review agents receive input via XML tags (`<paper>`, `<literature_context>`, `<state>`) in the Task prompt
