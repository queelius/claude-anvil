# Papermill

A [Claude Code](https://claude.ai/code) plugin for academic research paper lifecycle management.

Papermill provides interactive skills and autonomous agents that cover the full pipeline from idea to submission: thesis refinement, literature surveys, experiment design, editorial review, and venue matching.

## Installation

```bash
claude plugins add ~/github/papermill
```

Or from any directory containing the plugin:

```bash
claude plugins add .
```

## Commands

Invoke commands with `/papermill:<name>` in Claude Code. Each command triggers its corresponding skill.

| Skill | Description |
|-------|-------------|
| **init** | Initialize a paper repo -- discovers structure, sets up `.papermill.md` state file |
| **status** | Dashboard showing current stage, thesis, experiments, reviews, and next steps |
| **thesis** | Extract or refine the central claim and novelty (Socratic dialogue or draft extraction) |
| **prior-art** | Interactive literature survey with keyword generation, screening, classification, and gap analysis |
| **outline** | Design paper structure with section purposes, key content, and narrative arc |
| **experiment** | Design experiments with hypotheses, variables, methodology, and success criteria |
| **simulation** | Monte Carlo simulation design for validating theoretical results |
| **proof** | Mathematical proof development, verification, and presentation |
| **review** | Structured editorial review checking argument, correctness, writing, and venue fit |
| **venue** | Identify and evaluate publication venues with ranked recommendations |
| **polish** | Pre-submission checklist: formatting, citations, figures, metadata, build verification |

## Agents

Agents run autonomously and produce structured output files.

| Agent | Description |
|-------|-------------|
| **surveyor** | Deep autonomous literature search with citation network exploration |
| **reviewer** | Thorough autonomous editorial review of a paper draft |

## State File

Papermill uses a `.papermill.md` file in each paper repository to persist state across sessions. This file has YAML frontmatter (structured metadata) and a markdown body (session notes).

The state file is created by `/papermill:init` and updated by other skills as you work.

## Workflow

A typical workflow:

1. **`/papermill:init`** -- Set up the state file in your paper repo
2. **`/papermill:thesis`** -- Crystallize your central claim
3. **`/papermill:prior-art`** -- Survey the literature, identify gaps
4. **`/papermill:outline`** -- Design the paper structure
5. Write the paper (papermill helps, but the writing is yours)
6. **`/papermill:experiment`** / **`/papermill:simulation`** -- Design computational work
7. **`/papermill:proof`** -- Develop and verify proofs
8. **`/papermill:review`** -- Get editorial feedback
9. **`/papermill:venue`** -- Choose where to submit
10. **`/papermill:polish`** -- Final pre-submission check

Skills can be used in any order and revisited as needed. Use `/papermill:status` at any time for orientation.

## License

MIT
