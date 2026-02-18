# Worldsmith

A Claude Code plugin for documentation-first worldbuilding. The Silmarillion approach: **the documentation IS the world** — manuscript text derives from it, not the other way around.

Worldsmith provides methodology, workflow discipline, and editorial practices for fiction projects with complex worlds. It codifies a battle-tested editorial workflow developed across 6 revision cycles of a 105k-word novel.

## Philosophy

Most worldbuilding tools focus on databases and wikis. Worldsmith takes a different approach: your world lives in a set of tightly coupled documentation files that serve as both **canonical reference** (what IS true) and **generative engine** (what COULD become true). Claude Code does the intelligent synthesis — the analysis, the consistency checking, the cross-referencing. The plugin provides the conceptual framework and editorial discipline.

**Key ideas:**
- **Docs first, manuscript second.** When a fact changes, update the canonical doc, then propagate to the manuscript. Never the reverse.
- **Dual workflow.** Established facts get the canonical workflow (docs → manuscript → outline). New ideas get the exploratory workflow (provisional sections only, no manuscript changes until promoted).
- **Propagation awareness.** Every change has a blast radius. The plugin reminds you to trace changes through the doc graph.
- **Consistency as practice.** Not a one-time check but an ongoing discipline — timeline validation, character tracking, cross-reference maintenance.
- **Editorial diagnostics.** Make invisible prose patterns visible so the writer can make informed choices.

## Installation

```bash
# Local installation
claude plugin add /path/to/worldsmith

# Or use plugin-dir flag
claude --plugin-dir /path/to/worldsmith
```

## What's Included

### Commands (8)

| Command | Description |
|---|---|
| `/worldsmith:init-world` | Scaffold the doc ecosystem for a new project |
| `/worldsmith:fix` | Canonical change workflow — docs first, then manuscript |
| `/worldsmith:explore` | Write provisional ideas to exploratory sections |
| `/worldsmith:promote` | Promote an exploratory idea to canonical status |
| `/worldsmith:check` | Run consistency checks (timeline, facts, characters, spatial) |
| `/worldsmith:xref` | Look up or rebuild cross-references |
| `/worldsmith:audit` | Deep editorial audit (prose patterns, pacing, style) |
| `/worldsmith:status` | Project health overview |

### Agents (3)

| Agent | Role | Trigger |
|---|---|---|
| **Lorekeeper** | Develops worldbuilding content, mythology, systems | "flesh out the history of...", "design a magic system...", "develop this culture..." |
| **Continuity Checker** | Finds contradictions and consistency errors | "check for inconsistencies...", "verify the timeline...", "audit cross-references..." |
| **Editor** | Prose diagnostics, repetition tracking, pacing analysis | "do a repetition audit...", "analyze the pacing...", "editorial review..." |

### Skills (4)

| Skill | Activates When | Provides |
|---|---|---|
| **Doc Ecosystem** | Discussing doc structure, cross-references, propagation | Doc relationships, cross-ref guide, propagation rules |
| **Consistency Rules** | Discussing fact-checking, timeline validation, continuity | Timeline validation, character tracking, fact-checking methodology |
| **Worldbuilding Methodology** | Developing lore, designing systems, building history | Historical layering, mythology design, system design, cultural depth |
| **Editorial Standards** | Discussing prose quality, repetition, pacing | Repetition tracking, prose diagnostics, pacing analysis |

### Hooks

- **PostToolUse** (Edit/Write): Propagation reminder — when a doc or manuscript file is edited, reminds about cross-reference propagation
- **Stop**: Completion verification — before ending a session, checks if propagation was completed for any worldbuilding edits

### Templates

Starting-point templates for all six doc types plus CLAUDE.md. Used by `/worldsmith:init-world` to scaffold new projects.

### Scripts

- `detect-doc-type.sh` — Identify which doc type a file is
- `check-propagation.sh` — List files that may need updates after a change
- `count-patterns.sh` — Count common prose patterns across manuscript files

## The Documentation Ecosystem

Six documents form a tightly coupled editorial system:

```
                    outline.md
                   (diagnostic hub)
                   /    |    \
                  /     |     \
          lore.md   characters.md   worldbuilding.md
         (history,    (arcs,         (systems,
          themes,      tracking,      mechanics,
          direction)   states)        specs)
              \         |         /
               \        |        /
                style-guide.md
               (craft constraints)
                        |
                  future-ideas.md
                 (aspirational goals)
```

Every doc points into the manuscript text. The outline points into every doc. When a fact changes anywhere, trace it through this graph.

## Getting Started

1. Install the plugin
2. In your fiction project directory, run `/worldsmith:init-world`
3. Start with `lore.md` — write your world's origin story
4. Then `worldbuilding.md` — define the core systems and rules
5. Then `characters.md` — create character entries
6. Build `outline.md` as scenes are written
7. `style-guide.md` and `future-ideas.md` accumulate over time

## Workflows

### Making a canonical change

```
/worldsmith:fix "Change the founding date from 1714 to 1720"
```

This walks you through: identify canonical source → update doc → find all references → update references → verify propagation.

### Exploring an idea

```
/worldsmith:explore "What if the magic system also affects dreams?"
```

This writes the idea to the appropriate exploratory section without touching the manuscript. When ready:

```
/worldsmith:promote "dream magic system"
```

### Checking consistency

```
/worldsmith:check timeline
/worldsmith:check all
```

### Running an editorial audit

```
/worldsmith:audit patterns
/worldsmith:audit pacing
```

## License

MIT
