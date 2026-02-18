# Propagation Awareness

When a worldbuilding document changes, other documents and the manuscript may need to change too. This guide describes how changes ripple through an interconnected doc ecosystem. The goal is awareness — developing the habit of asking "what else does this affect?" — not rigid adherence to a propagation checklist.

## The Core Concept

A fictional world is a web of dependencies. A character's age depends on the timeline. A scene's plausibility depends on the magic system's rules. A dialogue choice depends on the character's voice patterns. A cultural reference in the manuscript depends on the lore docs.

When any node in this web changes, trace the connections outward. Some changes are contained (a typo fix in a character name's spelling). Others cascade (restructuring the timeline shifts every character's age and invalidates date references across the manuscript). The discipline is recognizing which kind of change is happening and responding proportionally.

## Changes by Document Role

### Timeline Changes

The timeline is the backbone of chronological consistency. Changes here tend to cascade widely.

**Dates and event sequences** — When a date shifts, check: character ages at affected points (character tracking), event references in the manuscript (search for the old date or event name), outline entries that reference the event, lore entries that describe the event in historical context. A single date change can require updates across four or five files.

**Day-numbering within chapters** — When chapter-internal timing changes, check: character state transitions that depend on elapsed time ("three days without sleep" becomes wrong if day numbers shift), spatial plausibility (can a character travel that distance in the new timeframe), and outline scene sequencing.

**Duration claims** — When "the war lasted ten years" becomes "the war lasted seven years," trace every reference to the war's duration: character backstories, historical lore, political consequences that depended on the longer timeline.

### System/Mechanics Changes

System changes affect what characters can and cannot do, which affects plot plausibility.

**Rule modifications** — When a magic system's rules change, check: scenes where characters use the system (do they still work under the new rules?), character capabilities (does anyone need recalibration?), lore that explains the system's origins, style-guide entries about how to describe the system in prose.

**Geographic changes** — When distances, terrain, or climate change, check: travel times in the manuscript, spatial references in scenes, military or political boundaries in lore, the outline's scene logistics.

**Adding new systems** — When introducing a new system (economic structure, political hierarchy, technology), check: does it conflict with existing systems? Does it require backstory in the lore? Does it affect character capabilities? Does the style guide need conventions for describing it?

### Character Changes

Character changes are often the most interconnected because characters touch every other document type.

**Arc modifications** — When a character's arc changes direction, check: the outline's character tracker, scenes that depended on the previous arc trajectory, relationships with other characters (reciprocal updates), emotional flicker entries that may no longer be on the right trajectory, the themes doc if the character embodies a thematic element.

**Voice pattern updates** — When a character's voice evolves or gets corrected, check: existing manuscript dialogue for consistency, the style guide if the character's speech patterns interact with prose conventions (e.g., a character who uses a distinctive dialect that the style guide addresses).

**Relationship changes** — Relationships are bidirectional. When Character A's relationship to Character B changes, update Character B's entry too. Check: scenes they share in the outline, manuscript dialogue between them, any lore entries where they appear together.

**Knowledge state** — When revising what a character knows at a given point, check: subsequent scenes where they act on (or conspicuously don't act on) that knowledge, other characters they might have told, outline entries tracking information flow.

### Style Guide Changes

Style changes affect how the entire manuscript is written, making them broad but usually shallow.

**Prose principles** — When a prose rule changes (e.g., shifting from third-person limited to close third), the impact is manuscript-wide. Check: existing manuscript chapters for compliance, the outline if it tracks POV, character doc entries that reference POV-specific techniques.

**Anti-cliche additions** — When adding a new anti-cliche rule, search the manuscript for existing violations. Check: character descriptions that might use the now-forbidden pattern, lore prose that might use it, style-guide consistency checklist.

**Intentional repetitions list** — When marking a repetition as intentional (to prevent future "corrections"), note the specific instances in the manuscript. When removing something from the intentional list, flag instances for review.

### Lore/History Changes

Lore changes affect the world's cultural and historical backdrop.

**Mythology revisions** — When a myth changes, check: character beliefs or customs that depend on the myth, cultural references in the manuscript, timeline entries for mythological events, the themes doc if the myth carries thematic weight.

**Cultural context changes** — When revising cultural practices, check: character behavior that reflects the culture, dialogue idioms or references, lore-derived world details in the manuscript, the style guide if cultural terms have specific formatting or usage conventions.

**Founding stories** — Changes to origin stories can affect: political structures in the world, character lineages or heritage claims, sacred sites or objects referenced in the manuscript, timeline entries for founding events.

### Outline Changes

The outline is a diagnostic hub, so changes here are often symptoms of changes elsewhere rather than sources of cascading updates.

**Scene restructuring** — When scenes move or merge, check: chapter numbering in character doc scene anchors, cross-references from other docs that point to specific chapters, manuscript chapter organization.

**Adding/removing scenes** — When the outline gains or loses a scene, check: pacing analysis, character arc completeness (does a character still have their key moments?), plot thread coverage.

### Editorial Backlog Changes

Backlog changes rarely cascade because backlog content is exploratory by definition. The main exception: when an item is promoted from backlog to canonical, it becomes a canonical change and follows the canonical change workflow.

### Themes/Anti-Cliche Changes

Theme changes affect the project's aesthetic commitments and can require manuscript review.

**Thematic rule additions** — When adding a new thematic commitment, search the manuscript for existing content that might violate it. Update the style guide if the theme has prose-level implications.

**Anti-cliche rule changes** — Similar to style guide anti-cliche changes. Search for violations, flag for revision, update the style guide's consistency checklist.

### Feedback Changes

Feedback entries are historical records and don't typically require propagation. However, acting on feedback often produces changes in other docs — track those changes through their appropriate propagation paths.

## Shallow vs. Deep Changes

**Shallow changes** have limited blast radius:
- Fixing a typo or spelling correction
- Minor date adjustment with few downstream references
- Adding detail to an existing entry without changing its substance
- Clarifying prose in a doc without changing the underlying fact

For shallow changes, a quick mental scan of affected docs is usually sufficient. Check the most obvious connections and move on.

**Deep changes** have wide blast radius:
- Restructuring the timeline (affects nearly everything)
- Changing a core system rule (affects all scenes using the system)
- Revising a character's fundamental arc (affects outline, manuscript, relationships)
- Adding or removing a major thematic commitment (affects manuscript review)
- Changing the canonical hierarchy itself (affects conflict resolution everywhere)

For deep changes, work methodically. Update the source doc. Then walk through each connected doc role, checking for impacts. Update the manuscript last (it's the lowest-priority source and the highest-effort update). Consider whether CLAUDE.md needs updating.

## CLAUDE.md as Part of the Ecosystem

The project's CLAUDE.md is not just a configuration file — it's a living document that participates in the propagation ecosystem. Update it when:

- **World structure changes** — New docs added, docs merged, roles reassigned
- **Canonical tables change** — CLAUDE.md often contains canonical summary tables for quick reference
- **Character conventions change** — Voice pattern rules, anti-cliche commitments that CLAUDE.md summarizes
- **Series relationships change** — New related projects, changed relationships between projects
- **Consistency rules change** — Canonical hierarchy modifications, new propagation-relevant patterns
- **Anti-cliche rules are added or removed** — These are often summarized in CLAUDE.md for quick reference

A stale CLAUDE.md is a compounding problem: every future session reads it first, and stale information leads to stale decisions. Prioritize keeping it current.

## Series and Cross-Project Propagation

For projects in a series or shared universe, some facts are shared and some are local.

**Shared facts** require cross-project awareness:
- Timeline events that span projects
- Geographic constants (the world map doesn't change between books)
- System rules (magic works the same way)
- Cultural constants (unless cultural change is part of the story)
- Character backstories that appear in multiple projects

**Local facts** stay within the project:
- Manuscript prose and style choices
- Character arcs specific to one book
- Plot details
- Editorial feedback and backlog

When a shared fact changes, note which related projects may need checking. The current project's CLAUDE.md should list these relationships. Do not modify other projects' files without explicit direction — flag the potential inconsistency and let the user decide how to handle it.
