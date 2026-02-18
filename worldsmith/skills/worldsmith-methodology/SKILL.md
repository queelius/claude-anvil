---
name: worldsmith-methodology
description: This skill should be used when the user asks about "documentation structure", "doc relationships", "cross-references", "propagation", "canonical workflow", "exploratory workflow", "docs-first", "lore management", "worldbuilding docs", "consistency rules", "canonical hierarchy", "update docs", "change propagation", "editorial workflow", "Silmarillion approach", or is working in a project with a worldbuilding documentation ecosystem (docs/ or lore/ directory).
version: 0.2.0
---

# Worldsmith Methodology

Rules and structure for documentation-first fiction worldbuilding. This skill provides what cannot be inferred from context alone: the editorial discipline, canonical hierarchy, propagation awareness, and character documentation standards that keep a worldbuilding project internally consistent as it grows.

## 1. Core Philosophy

Treat documentation as the source of truth for the fictional world. The manuscript is one expression of the world; the docs define it. Docs and manuscript should stay consistent with each other, but recognize that creative work is messy — bidirectional updates happen naturally. A scene might introduce a detail that needs to flow back into the docs, or a doc revision might require manuscript changes. Both directions are legitimate.

When docs and manuscript conflict, the docs are usually right — they represent deliberate editorial decisions. But exercise judgment. Sometimes the manuscript captures a better version of a detail that the docs haven't caught up with. The key discipline is noticing divergence and reconciling it, not enforcing rigid ordering.

All documents are living documents, including the project's CLAUDE.md. As the world evolves through writing, update the docs. As the docs evolve, keep CLAUDE.md current — it is the most frequently read document in any session and serves as the entry point to the entire editorial system. A stale CLAUDE.md undermines every subsequent action.

## 2. The Document Ecosystem

Worldbuilding projects organize their editorial knowledge across documents that serve specific roles. Think in terms of roles, not filenames — a project might call its timeline doc `timeline.md`, `chronology.md`, or `history-dates.md`. The role matters, not the name. Consult the project's CLAUDE.md for the mapping between roles and files.

### Document Roles

- **Timeline Authority** — The authoritative source for dates, event sequences, character ages at specific points, and day-numbering within chapters. When any other doc or the manuscript disagrees with the timeline on a date or sequence, the timeline wins.

- **Lore/History** — Mythology, founding stories, cultural context, historical events in narrative form. Contains the "why" behind the world's current state. Typically has both canonical sections (established history) and exploratory sections (myths being developed, histories not yet referenced in manuscript).

- **Systems/Mechanics** — Magic systems, technology rules, geography and climate, economic structures, political systems. Specs with consequences: not just "how the system works" but "what it means for characters and plot." Typically has exploratory sections for systems under development.

- **Character Tracking** — Character arcs, voice patterns, relationships, emotional trajectories, key scene anchors. The working reference during manuscript writing. See Section 5 for documentation standards.

- **Style Conventions** — Prose principles, POV rules, tense conventions, intentional repetitions list, anti-cliche rules, consistency checklist. The guardrails for how the story is told, distinct from what it tells.

- **Outline/Diagnostic Hub** — Scene-by-scene or chapter-by-chapter breakdown with cross-references to other docs. Functions as a control panel: what happens, which characters are present, which world elements are in play, what state things are in. The place to check "where does X appear?"

- **Editorial Backlog** — Future ideas, sequel hooks, unexplored threads, deferred decisions. Ranked or prioritized by potential impact. A holding pen that prevents good ideas from being lost while keeping them out of canonical docs until they're ready. Typically has exploratory sections only.

- **Themes/Anti-Cliche** — Thematic rules, philosophical framework, what patterns to avoid, what patterns to preserve. The project's aesthetic and intellectual commitments — what makes this story this story and not a generic version of itself.

- **Feedback** — Date-stamped editorial reviews, reader feedback, revision notes with priorities. Progress tracking across revision cycles. A historical record of editorial decisions.

### Canonical Hierarchy

When sources disagree, resolve conflicts using this hierarchy (highest authority first):

1. **Canonical tables** (explicit CANONICAL markers in any doc)
2. **Timeline authority** (dates, sequences, ages)
3. **System specs** (mechanics, rules, geography)
4. **Character entries** (arcs, voice, relationships)
5. **Outline** (scene structure, cross-references)
6. **Manuscript** (the prose itself)

Not every project will have all roles populated. Some projects may combine roles into fewer files. The hierarchy applies regardless of how many files exist.

## 3. Dual Workflow

### Canonical Changes

When modifying established facts — correcting a date, updating a character's arc after a chapter is written, revising a system rule — treat the change as canonical. Update the authoritative source doc first, then reconcile affected docs and manuscript passages. Follow the canonical hierarchy: if the change originates in a lower-authority source, verify it against higher-authority sources before propagating.

### Exploratory Ideas

When developing new material — drafting mythology, sketching a future plot thread, experimenting with a system extension — treat it as exploratory. Write to exploratory or provisional sections of the appropriate doc. Mark the content as provisional or speculative. Do not update the manuscript based on exploratory content. Do not propagate exploratory content to other canonical sections.

### Promotion

When exploratory content is ready to become canonical: resolve any conflicts with existing canonical material, move the content to canonical sections, then reconcile affected docs and manuscript as with any canonical change.

Determine the appropriate mode from context. Most user requests make it clear whether they're establishing facts or exploring possibilities. When ambiguous, ask.

## 4. Propagation Awareness

A change to one document may require changes to others. Developing this awareness is more important than following a rigid checklist. When making a change, pause and consider: what else in the project depends on or references the thing that just changed?

The scope of propagation varies. A typo fix in a character name propagates narrowly — search and replace across files. A restructured timeline propagates widely — character ages, event references, outline entries, and manuscript passages may all need revision. Recognize which kind of change is happening and respond proportionally.

Consult the project's CLAUDE.md for the document structure and role mappings. CLAUDE.md itself is part of the ecosystem — when project-level facts change (world structure, canonical tables, character conventions, anti-cliche rules, series relationships), update CLAUDE.md to reflect those changes.

For detailed guidance on how changes ripple through interconnected docs, including examples organized by document role and the distinction between shallow and deep changes, consult `${CLAUDE_PLUGIN_ROOT}/skills/worldsmith-methodology/references/propagation-awareness.md`.

## 5. Character Documentation Standards

Character docs earn their place by providing what Claude cannot infer from the manuscript alone: patterns, trajectories, and behavioral specifics that make characters recognizable and consistent across chapters.

### Voice Patterns and Speech Tics

Document how each character sounds — not generic labels ("speaks formally") but specific patterns ("uses rhetorical questions when deflecting, drops contractions under stress, favors botanical metaphors"). A well-documented voice pattern makes a character recognizable without dialogue tags.

### Emotional Flickers

Track specific moments that mark a character's arc trajectory. Not summaries ("she's getting braver") but anchored observations ("Chapter 12: flinches at the mention of the treaty but doesn't leave the room — first time she's stayed"). These accumulate into an arc map that shows where a character has been and where they're heading.

### Key Scene Anchors

Reference specific chapter-and-moment pairs where a character makes pivotal choices, reveals information, or undergoes change. These anchors serve as landmarks when checking consistency: "Has this character already learned X? Check the scene anchor list."

### Intellectual Frameworks

Document which concepts, philosophies, or worldview elements a character embodies. Not personality labels but the specific ideas they represent and how those ideas shape their decisions.

### Anti-Pattern

Avoid generic descriptions that could apply to any character: "brave warrior," "wise mentor," "conflicted hero." Instead, document behavioral specificity: "pauses before speaking, fingers tracing the scar on her wrist" tells more than "thoughtful and haunted" ever could.

## 6. Series & Shared Universe

Projects may exist within a series or shared universe. Check the project's CLAUDE.md for references to related projects — sibling novels, prequel/sequel relationships, shared-world anthologies.

When working on world facts that are shared across projects (timeline events, geography, system rules, cultural constants), consult the related projects' docs for consistency. Project-local facts (character arcs, plot details, manuscript-specific style choices) do not require cross-project checking.

When a shared world fact changes, note which related projects may need updating. The current project's CLAUDE.md should list these relationships.

## 7. Consistency & Quality Awareness

Watch for these categories of issues during any worldbuilding or editorial work:

- **Timeline inconsistencies** — Dates, ages, event sequences, duration claims that conflict with the timeline authority or with each other in the manuscript.
- **Factual contradictions** — Canonical values (system rules, geographic facts, established history) that the manuscript states differently.
- **Character state errors** — Characters knowing things they shouldn't yet know, displaying capabilities they haven't developed, emotional states that don't follow from prior scenes.
- **Spatial inconsistencies** — Locations, distances, travel times, architectural details that contradict established geography.
- **Prose pattern issues** — Crutch words, filter words, weak verb constructions, adverb-heavy dialogue tags that accumulate across chapters.
- **Pacing concerns** — Scene balance, info dumps, rushed transitions, chapters that don't earn their length.
- **Style drift** — Departures from the project's style-guide conventions (POV rules, tense, intentional repetitions, prose principles).
- **Thematic drift** — Content that contradicts the themes doc's commitments (anti-cliche rules violated, philosophical framework abandoned, aesthetic principles ignored).

Severity depends on context. A wrong date in a throwaway reference is less urgent than a wrong date in a pivotal scene. A crutch word used twice is different from one used twenty times. Exercise judgment rather than applying rigid severity classifications.

## Additional Resources

- **Propagation awareness guidance**: `${CLAUDE_PLUGIN_ROOT}/skills/worldsmith-methodology/references/propagation-awareness.md` — How changes ripple through interconnected docs, with examples by document role and guidance on shallow vs. deep changes.
- **Document structure guide**: `${CLAUDE_PLUGIN_ROOT}/skills/worldsmith-methodology/references/doc-structure-guide.md` — What good worldbuilding docs look like, organized by role. Used by init-world when generating docs for new or adopted projects.
