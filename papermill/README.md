# Papermill

A [Claude Code](https://claude.ai/code) plugin for academic research paper lifecycle management.

Papermill provides interactive skills and autonomous agents that cover the full pipeline from idea to submission: thesis refinement, literature surveys, multi-agent drafting, experiment design, multi-agent editorial review, and venue matching.

## Installation

```bash
/plugin marketplace add queelius/claude-anvil
/plugin install papermill@queelius
```

## Commands

Invoke commands with `/papermill:<name>` in Claude Code. Each command triggers its corresponding skill.

| Skill | Description |
|-------|-------------|
| **init** | Initialize a paper repo -- discovers structure, sets up `.papermill/state.md` state file |
| **status** | Dashboard showing current stage, thesis, experiments, reviews, and next steps |
| **thesis** | Extract or refine the central claim and novelty (Socratic dialogue or draft extraction) |
| **prior-art** | Interactive literature survey with keyword generation, screening, classification, and gap analysis |
| **outline** | Design paper structure with section purposes, key content, and narrative arc |
| **draft** | Multi-agent paper drafting with specialist writers for literature, math, methodology, and results |
| **experiment** | Design experiments with hypotheses, variables, methodology, and success criteria |
| **simulation** | Monte Carlo simulation design for validating theoretical results |
| **proof** | Mathematical proof development, verification, and presentation |
| **review** | Multi-agent editorial review with 8 specialists covering logic, novelty, methodology, prose, citations, and formatting |
| **revise** | Apply review findings via the reviser orchestrator: fix-then-verify per finding, revision report paired with the review |
| **venue** | Identify and evaluate publication venues with ranked recommendations |
| **polish** | Pre-submission checklist: formatting, citations, figures, metadata, build verification |

## Agents

Agents run autonomously and produce structured output files. The plugin has two multi-agent systems — one for **writing** and one for **reviewing** — that share literature scouts and the format validator.

### Writing System

| Agent | Model | Description |
|-------|-------|-------------|
| **writer** | fable | Multi-agent writing orchestrator (lead author) — plans paper, spawns writers, integrates draft |
| **literature-writer** | fable | Related work and background sections — narrative synthesis of prior work |
| **formal-writer** | fable | Mathematical content — definitions, theorems, proofs, derivations |
| **method-writer** | fable | Methodology and algorithms — experimental design, pseudocode, reproducibility |
| **results-writer** | fable | Results, analysis, and discussion — evidence interpretation and implications |

### Review System

| Agent | Model | Description |
|-------|-------|-------------|
| **reviewer** | fable | Multi-agent review orchestrator (area chair) — spawns specialists and synthesizes unified report |
| **reviser** | fable | Multi-agent revision orchestrator: routes findings to section writers, verifies fixes with the owning specialist |
| **logic-checker** | fable | Proof correctness, logical chain integrity, assumption sufficiency |
| **novelty-assessor** | fable | Contribution evaluation against literature context |
| **methodology-auditor** | fable | Experimental design, statistical rigor, reproducibility |
| **prose-auditor** | fable | Writing quality, narrative arc, notation consistency |
| **citation-verifier** | sonnet | Reference accuracy, missing citations, bibliography integrity |

### Shared Agents

| Agent | Model | Description |
|-------|-------|-------------|
| **literature-scout-broad** | fable | Broad field survey — competing approaches, benchmarks, state of the art |
| **literature-scout-targeted** | fable | Direct comparison finder — same problem, same techniques, overlapping claims |
| **format-validator** | sonnet | Build verification, label resolution, venue formatting compliance |
| **surveyor** | sonnet | Deep autonomous literature search with citation network exploration |

## State File

Papermill uses a `.papermill/` directory in each paper repository to persist state and output:

```
.papermill/
├── state.md                      # Project state (YAML frontmatter + session notes)
├── drafts/
│   └── YYYY-MM-DD/
│       ├── writing-plan.md       # Section assignment table
│       ├── literature-writer.md  # Individual specialist drafts
│       ├── formal-writer.md
│       ├── method-writer.md
│       ├── results-writer.md
│       └── literature-context.md # Merged literature scout output
└── reviews/
    └── YYYY-MM-DD/
        ├── review.md             # Unified review report
        ├── logic-checker.md      # Individual specialist reports
        ├── novelty-assessor.md
        ├── methodology-auditor.md
        ├── prose-auditor.md
        ├── citation-verifier.md
        ├── format-validator.md
        └── literature-context.md # Merged literature scout output
```

The state file is created by `/papermill:init` and updated by other skills as you work. Legacy `.papermill.md` files are auto-migrated by init.

## Workflow

A typical workflow:

1. **`/papermill:init`** -- Set up the state file in your paper repo
2. **`/papermill:thesis`** -- Crystallize your central claim
3. **`/papermill:prior-art`** -- Survey the literature, identify gaps
4. **`/papermill:outline`** -- Design the paper structure
5. **`/papermill:draft`** -- Multi-agent paper drafting
6. **`/papermill:experiment`** / **`/papermill:simulation`** -- Design computational work
7. **`/papermill:proof`** -- Develop and verify proofs
8. **`/papermill:review`** -- Get multi-agent editorial feedback
9. **`/papermill:venue`** -- Choose where to submit
10. **`/papermill:polish`** -- Final pre-submission check

Skills can be used in any order and revisited as needed. Use `/papermill:status` at any time for orientation.

## License

MIT
