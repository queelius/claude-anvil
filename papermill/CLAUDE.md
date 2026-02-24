# CLAUDE.md — Papermill Plugin

## What This Is

Papermill is a Claude Code plugin for academic research paper lifecycle management. It provides skills (interactive prompt guides) and agents (autonomous subprocesses) that cover the full pipeline from idea to submission — including two multi-agent systems: one for writing and one for reviewing.

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
│   ├── draft.md                  # Multi-agent paper drafting
│   ├── experiment.md
│   ├── simulation.md
│   ├── proof.md
│   ├── review.md                 # Multi-agent editorial review
│   ├── venue.md
│   └── polish.md
├── skills/                       # Interactive skills (the core logic)
│   ├── init/SKILL.md             # Initialize paper project
│   ├── status/SKILL.md           # Paper state dashboard
│   ├── thesis/SKILL.md           # Extract/refine central claim
│   ├── prior-art/SKILL.md        # Literature survey
│   ├── outline/SKILL.md          # Paper structure
│   ├── draft/SKILL.md            # Multi-agent paper drafting
│   ├── review/SKILL.md           # Multi-agent editorial review
│   ├── venue/SKILL.md            # Publication venue matching
│   ├── experiment/SKILL.md       # Experiment design
│   ├── simulation/SKILL.md       # Monte Carlo methodology
│   ├── proof/SKILL.md            # Proof development
│   └── polish/SKILL.md           # Submission preparation
├── agents/                       # Autonomous agents
│   ├── writer.md                 # Multi-agent writing orchestrator (lead author)
│   ├── literature-writer.md      # Related work & background specialist
│   ├── formal-writer.md          # Mathematical content specialist
│   ├── method-writer.md          # Methodology & algorithms specialist
│   ├── results-writer.md         # Results & discussion specialist
│   ├── reviewer.md               # Multi-agent review orchestrator (area chair)
│   ├── surveyor.md               # Literature survey agent
│   ├── literature-scout-broad.md # Broad field survey (shared by writer & reviewer)
│   ├── literature-scout-targeted.md # Direct comparison finder (shared by writer & reviewer)
│   ├── logic-checker.md          # Proof and argument verification
│   ├── novelty-assessor.md       # Contribution evaluation against literature
│   ├── methodology-auditor.md    # Experimental design and statistical rigor
│   ├── prose-auditor.md          # Writing quality and narrative structure
│   ├── citation-verifier.md      # Reference accuracy and completeness
│   └── format-validator.md       # Build verification and venue compliance (shared)
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
- `drafts/YYYY-MM-DD/` — multi-agent draft output (section drafts + writing plan + literature context)

Legacy: older projects may have a `.papermill.md` file in the project root. The init skill auto-migrates this to `.papermill/state.md`.

## Multi-Agent Writing System

The draft skill (`/papermill:draft`) launches a multi-agent writing system orchestrated by the `writer` agent (lead author). The workflow:

1. **Comprehension** — orchestrator reads state, outline, thesis, existing content
2. **Writing plan** — orchestrator maps outline sections to specialist writers
3. **Literature grounding** — 2 scouts (broad + targeted) run in parallel (reused from review system)
4. **Section drafting** — 4 specialist writers run in parallel, each assigned specific sections
5. **Integration** — orchestrator merges sections, unifies notation, writes transitions
6. **Bookend sections** — orchestrator writes abstract, introduction, conclusion (require full draft)
7. **Verification** — format-validator checks compilation (reused from review system)
8. **Output** — manuscript + section drafts written to project and `.papermill/drafts/`

### Section Writer Specialists

| Agent | Content Type | Assigned Sections |
|-------|-------------|-------------------|
| `literature-writer` | Narrative synthesis of prior work | Related Work, Background, State of the Art |
| `formal-writer` | Mathematical rigor | Preliminaries, Theory, Proofs, Formal Analysis |
| `method-writer` | Technical procedure | Method, Algorithm Design, Experimental Setup |
| `results-writer` | Evidence interpretation | Results, Analysis, Discussion, Evaluation |

### XML Input Protocol for Writers

All section writers receive input via XML tags:
- `<assignment>` — section title, purpose, key content, estimated length
- `<outline>` — full paper outline
- `<thesis>` — central claim and novelty
- `<literature_context>` — merged scout findings
- `<existing_content>` — existing manuscript content
- `<prior_sections>` — preceding sections for flow
- `<format>` — target format and conventions
- `<venue>` — target venue and requirements

### Shared Agents

The writing and review systems share these agents:
- `literature-scout-broad` — field survey for literature grounding
- `literature-scout-targeted` — direct comparison finding
- `format-validator` — build verification and venue compliance

## Multi-Agent Review System

The review skill (`/papermill:review`) launches a multi-agent review orchestrated by the `reviewer` agent (area chair). The workflow:

1. **Comprehension** — orchestrator reads paper and state
2. **Literature grounding** — 2 scouts (broad + targeted) run in parallel
3. **Specialist review** — 6 reviewers run in parallel, each receiving literature context
4. **Cross-verification** — critical/low-confidence findings get second opinions
5. **Synthesis** — deduplicate, resolve conflicts, calibrate severity, check for blind spots
6. **Report** — unified report + individual specialist reports written to `.papermill/reviews/`

## Typical Workflow

```
/papermill:init          → Set up the project
/papermill:thesis        → Crystallize the central claim
/papermill:prior-art     → Survey the literature
/papermill:outline       → Design paper structure
/papermill:draft         → Multi-agent paper drafting ← NEW
/papermill:review        → Multi-agent editorial review
/papermill:proof         → Verify mathematical content
/papermill:experiment    → Design experiments
/papermill:simulation    → Design Monte Carlo studies
/papermill:venue         → Find publication venues
/papermill:polish        → Pre-submission preparation
/papermill:status        → Project dashboard
```

## Editing Guidelines

- Skills should be self-contained — each skill works independently
- Skills should read `.papermill/state.md` for context but work gracefully if it doesn't exist
- Agents should produce structured output that the calling skill can integrate
- Keep prompts focused: one skill = one activity
- Review agents receive input via XML tags (`<paper>`, `<literature_context>`, `<state>`) in the Task prompt
- Writing agents receive input via XML tags (`<assignment>`, `<outline>`, `<thesis>`, `<literature_context>`, `<existing_content>`, `<prior_sections>`, `<format>`, `<venue>`) in the Task prompt
