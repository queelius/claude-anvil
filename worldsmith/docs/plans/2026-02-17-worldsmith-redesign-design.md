# Worldsmith Plugin Redesign

Date: 2026-02-17

## Problem

The current worldsmith plugin (v0.1.0, 43 files) over-engineers the editorial process. Skills are encyclopedias teaching Claude things it already knows. Commands prescribe rigid step-by-step scripts instead of giving Claude rules and letting it reason. The plugin hardcodes 6 specific filenames instead of working with any project structure. Features proven essential in real projects (feedback/, timeline authority, themes/anti-cliche, character voice patterns, series awareness) are missing.

## Philosophy

- **Awareness over formalism.** Make Claude aware of the doc structure and consistency discipline. Let it reason about consequences. Don't prescribe rigid propagation matrices or step-by-step workflows.
- **The CLAUDE.md is the real product.** It tells every future Claude session about the project's editorial system. Everything else is scaffolding.
- **Docs and manuscript should stay consistent.** Bidirectional updates are OK — it's a messy creative process. The discipline is noticing when things diverge and reconciling, not enforcing a strict ordering.
- **All docs are living documents, including CLAUDE.md.** As the world evolves through writing, the docs evolve with it. CLAUDE.md is the most frequently read doc — keep it current.
- **Projects vary.** No prescribed file structure. Work with whatever exists. Roles (timeline authority, character tracking, etc.) matter more than filenames.
- **Provide what Claude can't infer.** The project's doc structure, the consistency discipline, the canonical hierarchy, character documentation standards. Don't teach Claude mythology design or pacing analysis — it already knows.

## Design

### Plugin Structure

```
worldsmith/
├── .claude-plugin/plugin.json
├── skills/
│   └── worldsmith-methodology/
│       ├── SKILL.md                        # Core rules (~2000 words)
│       └── references/
│           ├── propagation-awareness.md    # How changes ripple, guidance not matrix
│           └── doc-structure-guide.md      # What good docs look like (for init-world)
├── commands/
│   ├── init-world.md                       # Scaffold or adopt a project
│   ├── change.md                           # Unified change workflow
│   └── check.md                            # Unified diagnostics
├── agents/
│   ├── lorekeeper.md                       # Creative worldbuilding (read-write)
│   └── critic.md                           # Consistency + editorial (read-only)
├── hooks/
│   ├── hooks.json                          # SessionStart + PostToolUse + Stop
│   └── scripts/
│       └── detect-worldsmith-project.sh    # Project detection for SessionStart
├── scripts/
│   └── count-patterns.sh                   # Prose pattern counting for audits
├── CLAUDE.md
├── README.md
└── LICENSE
```

13 core files (down from 43). No templates/ directory — init-world generates content dynamically.

### Skill: worldsmith-methodology

Single skill providing the core rules. Follows best practices: lean SKILL.md (~2000 words), imperative form, third-person description with trigger phrases, detailed content in references/.

**SKILL.md body sections:**

1. **Core Philosophy** (~200 words) — Docs are source of truth for the world. Manuscript and docs should stay consistent. Bidirectional updates are OK. When they conflict, docs are usually right but use judgment. All docs including CLAUDE.md are living documents.

2. **The Document Ecosystem** (~400 words) — Role-based, not filename-based. Roles: timeline authority, lore/history, systems/mechanics, character tracking, style conventions, outline/diagnostic hub, editorial backlog, themes/anti-cliche, feedback. Canonical hierarchy for conflict resolution: canonical tables > timeline authority > system specs > character entries > outline > manuscript. Which roles typically have exploratory sections.

3. **Dual Workflow** (~200 words) — Canonical changes (to established facts) vs. exploratory ideas (not yet established). Canonical: update the source doc, then reconcile other docs and manuscript. Exploratory: write to exploratory sections, mark as provisional, don't update manuscript until promoted. But this isn't rigid — Claude determines the mode from context.

4. **Propagation Awareness** (~150 words) — When something changes, think about what else might be affected. Consult the project's CLAUDE.md for the doc structure. Points to references/propagation-awareness.md for guidance.

5. **Character Documentation Standards** (~200 words) — Voice patterns and speech tics (recognizable without dialogue tags), emotional flickers (specific moments tracking arc trajectory), key scene anchors, intellectual frameworks. These make character docs actually useful during writing.

6. **Series & Shared Universe** (~100 words) — Projects may be part of a series. Check CLAUDE.md for related projects. Consult related projects' docs for shared world facts.

7. **Consistency & Quality Awareness** (~200 words) — Types of issues to watch for: timeline, factual, character state, spatial, prose patterns, pacing, style drift, thematic drift. Severity is context-dependent — use judgment.

**references/propagation-awareness.md** — Guidance on how changes ripple through a doc ecosystem. Not a rigid matrix but examples: "if you change a date in the timeline, think about character ages, event references in manuscript, and outline entries." Shallow vs. deep changes. The concept that CLAUDE.md should also be updated when project-level facts change.

**references/doc-structure-guide.md** — What good worldbuilding docs look like, organized by role. Used by init-world when generating docs for new projects. Describes what each role typically contains, what makes docs useful vs. encyclopedia-like. Examples of good canonical vs. exploratory sections. Guidance on CLAUDE.md content for worldbuilding projects.

### Commands

#### /worldsmith:init-world

Adaptive scaffolding. Assesses project state and responds accordingly.

- **CLAUDE.md exists with doc structure** → Already set up. Read it, confirm docs exist, report gaps. Don't overwrite.
- **Docs exist but no CLAUDE.md** (or CLAUDE.md without doc awareness) → Read existing docs, understand their roles, generate CLAUDE.md content describing the structure. Ask before modifying.
- **Nothing exists** → Ask about the project (name, genre, format, premise, series relationships). Create docs directory and lightweight starter docs. Generate project CLAUDE.md.

Asks about related projects/series. For new projects, uses references/doc-structure-guide.md as guidance for what to generate.

Frontmatter: description, allowed-tools (Read, Write, Edit, Bash, AskUserQuestion), argument-hint: [project-name]

#### /worldsmith:change

Unified change workflow. Claude determines the mode from context.

- **Canonical change**: Update source doc, reconcile references, keep docs and manuscript consistent.
- **Exploratory idea**: Write to exploratory sections, mark provisional, don't update manuscript.
- **Promotion**: Move from exploratory to canonical, then reconcile.

Rules: consult project's CLAUDE.md for doc structure. Think about what else might be affected. CLAUDE.md itself can be updated when project-level facts change. If mode is unclear, ask the user.

Frontmatter: description, allowed-tools (Read, Write, Edit, Grep, Glob, AskUserQuestion), argument-hint: [description of change or idea]

#### /worldsmith:check

Unified diagnostics. READ-ONLY. Modes: consistency, editorial, xref, status, or all.

- **consistency**: Timeline, facts, characters, spatial — check against canonical docs
- **editorial**: Prose patterns, pacing, style drift, thematic drift — can use count-patterns.sh
- **xref**: Cross-reference health in outline
- **status**: Project health overview (doc inventory, manuscript stats, feedback history, maturity)
- **all**: Everything

Reports grouped by severity. For series projects, can check cross-project consistency.

Frontmatter: description, allowed-tools (Read, Grep, Glob, AskUserQuestion), argument-hint: [scope: all|consistency|editorial|xref|status]

### Agents

#### lorekeeper (magenta, read-write)

Creative worldbuilding specialist. Develops lore, mythology, systems, history, cultural depth.

- Reads project's CLAUDE.md to understand doc structure and roles
- Reads relevant canonical docs before writing
- Writes to canonical or exploratory sections based on context
- Updates CLAUDE.md when changes affect project-level rules
- Follows character documentation standards (voice, flickers, scene anchors)
- Quality: narrative prose not encyclopedia, systems with consequences, layers of history, internal diversity

Tools: Read, Write, Edit, Grep, Glob, AskUserQuestion
System prompt: ~800 words

#### critic (yellow, read-only)

Diagnostic specialist. Handles both consistency and editorial analysis.

- Reads project's CLAUDE.md to understand doc structure, canonical hierarchy, and style rules
- Consistency: timeline, facts, characters, spatial — uses canonical hierarchy for conflict resolution
- Editorial: prose patterns, pacing, style drift, character voice consistency
- Can flag CLAUDE.md staleness
- For series projects, checks cross-project consistency
- Reports grouped by severity with locations, sources, and recommended fixes

Tools: Read, Grep, Glob (strictly read-only)
System prompt: ~900 words

### Hooks

#### SessionStart (command hook)

`detect-worldsmith-project.sh` — deterministic file detection.

- Checks for docs/ or lore/ directory with markdown files
- Lists found documents with sizes
- Checks for CLAUDE.md with worldsmith configuration
- Checks for related projects referenced in CLAUDE.md
- Detects manuscript files
- Output gives Claude ambient awareness from first message

Timeout: 10s

#### PostToolUse (prompt hook, matcher: Write|Edit)

Propagation reminder. If the edited file is part of a worldbuilding doc ecosystem or manuscript, briefly note which other files may need checking based on the project's CLAUDE.md.

Timeout: 10s

#### Stop (prompt hook, matcher: *)

Completion verification. If the session involved worldbuilding edits, verify propagation was addressed. Block if incomplete, approve if complete or no worldbuilding edits.

Timeout: 15s

### Scripts

#### count-patterns.sh

Prose pattern counting utility for editorial audits. Counts crutch words, filter words, weak verb patterns, adverb dialogue tags across manuscript files. Genuinely useful mechanical work that's faster as a script than having Claude grep repeatedly.

### What Was Removed

| Current (v0.1.0) | Redesign | Reason |
|---|---|---|
| 4 skills (11 reference docs) | 1 skill (2 reference docs) | Claude doesn't need encyclopedias on mythology design |
| 8 commands | 3 commands | Consolidated: fix+explore+promote→change, check+audit+xref+status→check |
| 3 agents | 2 agents | continuity-checker + editor → critic (same tools, same output format) |
| 7 templates | 0 templates | init-world generates content dynamically |
| detect-doc-type.sh | removed | Claude can determine doc types by reading them |
| check-propagation.sh | removed | Claude reasons about propagation, doesn't need a script |
| Rigid propagation matrix | Propagation awareness | Guidance and examples, not formal rules |
| Hardcoded filenames | Role-based | Works with any project structure |

### What Was Added

| Feature | How |
|---|---|
| Project adoption (existing docs) | init-world detects and adapts |
| Series/shared universe awareness | CLAUDE.md section + skill mention + SessionStart detection |
| SessionStart hook | Ambient project awareness from first message |
| Timeline as authoritative source | Role in canonical hierarchy |
| Themes/anti-cliche | Role in doc ecosystem |
| Feedback directory | Role in doc ecosystem |
| Character voice patterns | In skill's character documentation standards |
| Emotional flickers | In skill's character documentation standards |
| CLAUDE.md as living document | Explicit in philosophy, lorekeeper updates it |
| CLAUDE.md staleness detection | critic agent flags drift |

## Success Criteria

- Plugin works with existing projects (the-policy, echoes-of-the-sublime) without modification to those projects
- Plugin works with new projects scaffolded by init-world
- Claude correctly identifies worldsmith projects on session start
- The skill triggers on natural language about worldbuilding docs, consistency, editorial workflow
- Commands are thin — Claude reasons about the specifics, commands provide the rules
- No encyclopedic content (mythology design, pacing analysis, etc.) in the plugin
- All docs including CLAUDE.md treated as living documents
- Series relationships are detected and used for cross-project consistency
