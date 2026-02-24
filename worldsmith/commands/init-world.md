---
description: Scaffold or adopt a worldbuilding documentation ecosystem
allowed-tools: Read, Write, Edit, Bash(mkdir:*), Grep, Glob, AskUserQuestion
argument-hint: [project-name]
---

# /worldsmith:init-world

Assess the project state and set up (or verify) a worldbuilding documentation ecosystem. Adapt behavior to what already exists. Do not impose structure on a project that already has one.

If `$ARGUMENTS` is provided, use it as the project name or description rather than asking.

## Mode Detection

Read the current directory. Determine which mode applies:

1. **CLAUDE.md exists and describes a doc structure** (has a document roles table or references worldbuilding docs) -- go to Verify Mode.
2. **Docs exist but CLAUDE.md is absent or unaware of them** (a `docs/` or `lore/` directory with markdown files, but CLAUDE.md either missing or lacking doc role awareness) -- go to Adopt Mode.
3. **Nothing exists** (no docs directory, no worldbuilding markdown files) -- go to Scaffold Mode.

## Verify Mode

The project is already set up. Do not overwrite or "improve" anything unless asked.

1. If `.worldsmith/` does not exist, create it (`mkdir -p .worldsmith`). This activates worldsmith hooks for this project.
2. Read the project's CLAUDE.md. Parse the document roles table.
3. For each role listed, confirm the referenced file exists and is non-empty.
4. Check for missing roles -- are there standard roles (timeline, lore, systems, characters, style, outline, themes, backlog, feedback) that the project might benefit from but doesn't have?
5. Check for exploratory sections that might be ready for promotion.
6. Report findings: confirmed files, missing files, incomplete sections, suggested additions.
7. If CLAUDE.md references related projects (series/shared universe), confirm those paths are accessible.

## Adopt Mode

Existing docs need a CLAUDE.md to make them work with the worldsmith methodology.

1. Read every markdown file in the docs (or lore) directory. Read any existing CLAUDE.md.
2. For each file, determine which worldsmith role it serves: timeline authority, lore/history, systems/mechanics, character tracking, style conventions, outline/diagnostic hub, editorial backlog, themes/anti-cliche, feedback. A single file may serve multiple roles.
3. Present the mapping to the user. Ask for corrections.
4. Look for manuscript files (chapters/, manuscript/, or similar). Note what exists.
5. Draft CLAUDE.md content following the structure described in `${CLAUDE_PLUGIN_ROOT}/skills/worldsmith-methodology/references/doc-structure-guide.md` (see the "CLAUDE.md for Worldbuilding Projects" section): project overview, document roles table, consistency rules, world structure summary, character conventions, propagation awareness notes.
6. Present the draft. Ask the user before writing or modifying anything. Create `.worldsmith/` (`mkdir -p .worldsmith`) when the user approves.
7. If the user has an existing CLAUDE.md, merge the worldsmith doc-awareness content into it rather than replacing it.

## Scaffold Mode

Nothing exists. Build from scratch.

1. Ask the user about the project (use AskUserQuestion):
   - Project name
   - Genre and subgenre
   - Format: novel, novella, short story, series, anthology
   - Premise (one or two sentences)
   - Manuscript format if any preference (chapter files, single file, etc.)
2. Ask about related projects -- is this part of a series or shared universe? If so, get paths to related projects.
3. Create `.worldsmith/` and `docs/` directories.
4. Generate lightweight starter docs -- not comprehensive schemas, just enough to begin working. Each doc should have:
   - A title and brief description of its role
   - A canonical section (mostly empty, with a few placeholder entries if the premise suggests them)
   - An exploratory section where appropriate (lore, systems, backlog, themes)
   - Use `${CLAUDE_PLUGIN_ROOT}/skills/worldsmith-methodology/references/doc-structure-guide.md` as guidance for content and tone
5. Which docs to create depends on the project. At minimum: timeline, characters, and outline. For longer projects (novel, series): also lore, systems, style guide, themes. Always create a backlog. Only create a feedback doc if the user mentions existing feedback.
6. Generate the project's CLAUDE.md with: project overview, document roles table mapping roles to the files just created, the canonical hierarchy, world structure summary (from what the user described), character conventions section (initially brief), series references if applicable, propagation awareness notes relevant to this project's structure.
7. If a CLAUDE.md already exists (with non-worldbuilding content), append the worldsmith sections rather than replacing the file.

## Series Awareness

In all modes, ask whether this project is part of a series or shared universe. If yes:

- Get paths to related projects.
- Check if those projects have their own CLAUDE.md with worldsmith awareness.
- Add a series/related projects section to this project's CLAUDE.md listing: project paths, what's shared (world facts, timeline, systems, geography) vs. local (plot, character arcs, manuscript style), which project is authoritative for shared facts.

## Guidance

- Be conversational. This is a collaborative setup process, not a silent scaffolding script.
- Ask before writing files. Show the user what will be created.
- Starter docs should be genuinely useful, not boilerplate. If the user described a premise, seed the docs with relevant entries.
- Do not teach the user about worldbuilding methodology. Set up the system and let the methodology skill handle awareness.
- Keep generated CLAUDE.md concise. It will be read at the start of every session.
