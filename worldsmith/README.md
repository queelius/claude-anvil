# Worldsmith

A Claude Code plugin for documentation-first worldbuilding. The Silmarillion approach: **the documentation IS the world** — manuscript text derives from it, not the other way around.

Worldsmith provides methodology, workflow discipline, and editorial practices for fiction projects with complex worlds. Claude Code does the intelligent synthesis — analysis, consistency checking, cross-referencing. The plugin provides the conceptual framework and editorial discipline.

## Philosophy

- **Docs first, manuscript second.** When a fact changes, update the canonical doc, then propagate to the manuscript. Never the reverse.
- **Dual workflow.** Established facts get the canonical workflow (docs → manuscript → outline). New ideas get the exploratory workflow (provisional sections only, no manuscript changes until promoted).
- **Propagation awareness.** Every change has a blast radius. The plugin reminds you to trace changes through the doc graph.
- **Role-based, not filename-based.** The plugin thinks in document roles (timeline authority, lore, characters, systems, style conventions, outline, themes/anti-cliche, editorial backlog, exploratory ideas). Each project maps roles to its own file structure.
- **Series awareness.** Projects can reference related projects sharing a universe. Shared world facts propagate across projects.

## Installation

```bash
# Local installation
claude plugin add /path/to/worldsmith

# Or use plugin-dir flag
claude --plugin-dir /path/to/worldsmith
```

## What's Included

### Commands (3)

| Command | Description |
|---|---|
| `/worldsmith:init-world` | Set up worldsmith for a project — scaffold new docs, adopt existing ones, or verify an existing setup |
| `/worldsmith:change` | Make canonical changes, explore ideas, or promote exploratory content to canonical status |
| `/worldsmith:check` | Run diagnostics — consistency, editorial, cross-references, or project status |

### Agents (2)

| Agent | Role | Tools |
|---|---|---|
| **Lorekeeper** | Develops worldbuilding content — history, systems, cultures, characters | Read, Write, Edit, Grep, Glob, AskUserQuestion |
| **Critic** | Diagnostic specialist — consistency checks, editorial audits, prose analysis | Read, Grep, Glob (read-only) |

### Skill

**Worldsmith Methodology** — The core editorial methodology. Activates when discussing worldbuilding docs, lore management, character documentation, consistency checking, or editorial practices. Provides document role definitions, propagation awareness, character documentation standards, and series/shared universe guidance.

### Hooks

- **SessionStart**: Detects worldsmith projects and provides ambient context
- **PostToolUse** (Edit/Write): Propagation reminder when docs or manuscript are edited
- **Stop**: Completion verification before ending a session

### Scripts

- `count_patterns.py` — Count prose patterns across manuscript files. Reads pattern definitions from `patterns.md` — customize per project by placing a `.worldsmith/patterns.md` in your project root
- `patterns.md` — Default pattern definitions (crutch words, filter words, weak verbs, adverb dialogue tags). Human-readable, Claude-editable

## Getting Started

1. Install the plugin
2. In your fiction project directory, run `/worldsmith:init-world`
3. The command adapts to your project's state:
   - **New project**: Scaffolds documentation files and a CLAUDE.md with role mappings
   - **Existing docs**: Adopts your current documentation by mapping files to roles
   - **Already configured**: Verifies the setup and reports any gaps

## Workflows

### Making a canonical change

```
/worldsmith:change "Change the founding date from 1714 to 1720"
```

Claude identifies the canonical source, updates it, finds all references, and verifies propagation.

### Exploring an idea

```
/worldsmith:change "What if the magic system also affects dreams?"
```

Claude writes the idea to an exploratory section. When ready to promote:

```
/worldsmith:change promote dream magic
```

### Checking consistency

```
/worldsmith:check consistency
/worldsmith:check editorial
/worldsmith:check all
```

## License

MIT
