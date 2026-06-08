# Worldsmith

A Claude Code plugin for documentation-first worldbuilding. The Silmarillion approach: **the documentation IS the world**, and manuscript text derives from it, not the other way around.

Worldsmith provides methodology, workflow discipline, and editorial practices for fiction projects with complex worlds. Claude Code does the intelligent synthesis (analysis, consistency checking, cross-referencing). The plugin provides the conceptual framework, editorial discipline, and a multi-agent toolchain for review, drafting, and revision.

## Philosophy

- **Docs first, manuscript second.** When a fact changes, update the canonical doc, then propagate to the manuscript. Never the reverse.
- **Dual workflow.** Established facts get the canonical workflow (docs → manuscript → outline). New ideas get the exploratory workflow (provisional sections only, no manuscript changes until promoted).
- **Propagation awareness.** Every change has a blast radius. The plugin reminds you to trace changes through the doc graph.
- **Role-based, not filename-based.** The plugin thinks in document roles (timeline authority, lore, characters, systems, style conventions, outline, themes/anti-cliche, editorial backlog, exploratory ideas). Each project maps roles to its own file structure.
- **Series and multi-work awareness.** A repo can contain multiple works sharing canonical lore (novel plus short stories, novella plus collection). Shared world facts propagate across works.

## Installation

```bash
# Via the marketplace
/plugin marketplace add queelius/claude-anvil
/plugin install worldsmith@queelius

# Or from a local checkout of the marketplace
/plugin marketplace add ~/github/alex-claude-plugins
/plugin install worldsmith@queelius
```

## What's Included

### Commands (8)

| Command | Purpose |
|---------|---------|
| `/worldsmith:init-world [name]` | Scaffold or adopt a worldbuilding doc ecosystem |
| `/worldsmith:change [description]` | Apply a change: canonical edits, exploratory ideas, or promotions |
| `/worldsmith:check [work] [scope]` | Run diagnostics: `consistency`, `editorial`, `xref`, `status`, `cross-work`, `all` |
| `/worldsmith:review [work] [scope]` | Deep multi-agent editorial review (4 specialists in parallel) |
| `/worldsmith:draft [work] [assignment]` | Launch the writer orchestrator (scenes, chapters, lore, character work) |
| `/worldsmith:revise [work] [filter]` | Launch the rewriter orchestrator (apply fixes from a review report) |
| `/worldsmith:iterate [work] [flags]` | Autonomous review-fix loop until convergence |
| `/worldsmith:help` | Quick reference for everything |

### Agents

Four orchestrators that compose seven specialists for the heavy editorial work:

**Orchestrators:**

| Agent | Role | Launched by |
|-------|------|-------------|
| `reviewer` | Multi-agent editorial review (consistency, craft, voice, structure) | `/worldsmith:review` |
| `writer` | Multi-agent content generation (lore, scenes, characters) | `/worldsmith:draft` |
| `rewriter` | Fix-then-verify revision (reads review, fixes issues, verifies fixes) | `/worldsmith:revise` |
| `iterator` | Autonomous review-fix-review loop with end-of-loop user checkpoint | `/worldsmith:iterate` |

**Review specialists** (launched by `reviewer`): `consistency-auditor`, `craft-auditor`, `voice-auditor`, `structure-auditor`.

**Writing specialists** (launched by `writer` and `rewriter`): `lore-writer`, `scene-writer`, `character-developer`.

### Skills (auto-triggered)

| Skill | Triggers when... |
|-------|------------------|
| `worldsmith-methodology` | You work on worldbuilding docs, lore, or editorial structure |
| `prose-craft` | You write or edit fiction prose, scenes, or dialogue |

### Hooks

| Event | Behavior |
|-------|----------|
| `SessionStart` | Detects worldsmith projects via `.worldsmith/` directory; reads `project.yaml` for multi-work projects; surfaces doc and work inventory |
| `PostToolUse` (Write/Edit) | Propagation reminders for doc and manuscript edits; cliche detection (manuscript-scoped only, skips README and plans) |
| `Stop` | Completion verification before ending a session |

### Scripts

- `count_patterns.py` counts prose patterns across manuscript files. Reads pattern definitions from `patterns.md`, customizable per project by placing `.worldsmith/patterns.md` in your project root.
- `patterns.md` provides default pattern definitions (crutch words, filter words, weak verbs, adverb dialogue tags). Human-readable, Claude-editable.
- `parse-project-yaml.py` parses `.worldsmith/project.yaml` and emits shell env vars consumed by other hooks. Enables structured multi-work configuration without bash YAML parsing.

## Getting Started

1. Install the plugin.
2. In your fiction project directory, run `/worldsmith:init-world`.
3. The command adapts to your project's state:
   - **New project**: scaffolds documentation files and a CLAUDE.md with role mappings.
   - **Existing docs**: adopts your current documentation by mapping files to roles.
   - **Already configured**: verifies the setup and reports any gaps.

For a multi-work universe (novel plus short stories sharing canonical lore), add a `.worldsmith/project.yaml` declaring the universe and its works. Commands, agents, and hooks automatically respect work scoping when this file is present.

## Workflows

### Apply a canonical change

```
/worldsmith:change Change the founding date from 1714 to 1720
```

Claude identifies the canonical source, updates it, finds all references in the manuscript and other docs, and verifies propagation across all works in the universe.

### Explore an idea, then promote it

```
/worldsmith:change What if the magic system also affects dreams?
```

Claude writes the idea to an exploratory section, marked `[PROVISIONAL]`. When ready to promote:

```
/worldsmith:change promote dream magic
```

The provisional content moves to canonical, conflicts are resolved, and the change propagates.

### Check consistency before a session

```
/worldsmith:check status        # project health overview
/worldsmith:check consistency   # catch contradictions
/worldsmith:check all           # full diagnostic sweep
```

### Draft new content

```
/worldsmith:draft chapter 5
/worldsmith:draft Greymoor battle scene
/worldsmith:draft develop the Ashwalker culture
```

The writer orchestrator routes the assignment to lore, scene, and character specialists in parallel, integrates their output, and propagates new facts into the canonical doc ecosystem.

### Review, revise, then iterate

The most common revision pattern:

```
/worldsmith:review                   # deep multi-agent review
/worldsmith:revise                   # apply fixes from the latest review
/worldsmith:revise HIGH consistency  # or filter by severity and category
```

For unattended finishing-pass work, hand the manuscript to the autonomous loop:

```
/worldsmith:iterate                                      # 8 rounds, stop at zero HIGH findings
/worldsmith:iterate --max-iterations 12 --threshold medium
/worldsmith:iterate Hemorrhagic --pause-on all           # multi-work, more interactive
```

The iterator composes the reviewer and rewriter in a loop, defers high-stake creative judgments to a single end-of-loop checkpoint, and produces a summary with cost estimate and convergence reason.

## Multi-work projects

A universe can contain multiple works sharing canonical lore. Configure via `.worldsmith/project.yaml`:

```yaml
universe: the-policy
lore: lore/

works:
  - name: The Policy
    type: novel
    manuscript: chapters/
    file_types: [tex]

  - name: Hemorrhagic
    type: short-story
    manuscript: stories/hemorrhagic/
    file_types: [tex]
```

If absent, worldsmith infers a single work (backward compatible). Commands accept an optional work-name argument: `/worldsmith:review Hemorrhagic`, `/worldsmith:iterate "The Policy" --max-iterations 12`.

## License

MIT
