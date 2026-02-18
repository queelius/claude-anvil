# Document Structure Guide

What good worldbuilding documents look like, organized by role. This guide serves as reference when generating docs for new projects or assessing existing ones during project adoption. The emphasis throughout is on documents that are useful during active writing — not encyclopedias that are satisfying to create but rarely consulted.

## General Principles

Write docs as working editorial tools, not reference encyclopedias. A document earns its place by answering questions that come up during writing: "What date was the founding?" "How does this character talk when angry?" "Does this scene contradict the magic rules?"

Prefer narrative prose over database-style entries. A lore doc that reads like a Wikipedia article is less useful than one that reads like a historian's notes — it captures not just facts but their significance, their contested interpretations, their emotional weight.

Include both canonical sections (established, authoritative) and exploratory sections (provisional, under development) where appropriate. Label them clearly. Canonical sections are the source of truth; exploratory sections are the workshop.

Keep documents focused on their role. A character doc that also contains timeline entries and system rules becomes hard to maintain and hard to consult. When information belongs in multiple places, put the authoritative version in the appropriate role's doc and cross-reference from others.

## Document Roles

### Timeline Authority

The authoritative chronological reference. Contains dates, event sequences, and duration-dependent facts. Everything else defers to this document on questions of "when."

**What it typically contains:**
- Major era or period breakdown with date ranges
- Event entries keyed to dates, with brief descriptions and chapter/scene references
- Character birth dates and ages at key events
- Day-by-day or scene-by-scene timing within chapters (elapsed time tracking)
- Duration claims that other docs or manuscript passages depend on

**What makes it useful:**
Entries that connect dates to manuscript locations. Not just "The Battle of Greymoor: Year 412" but "The Battle of Greymoor: Year 412 (Ch. 8, day 3 — Sera is 24, Maren is 31. Referenced in Kael's campfire story, Ch. 14)." Cross-referencing makes the timeline a diagnostic tool, not just a list of dates.

**Anti-pattern:** A timeline that lists events without connecting them to the manuscript or to character states. Beautiful but unused.

### Lore/History

The mythological, cultural, and historical backbone of the world. Contains the "why" behind the current state of affairs — founding stories, religious traditions, political history, cultural practices.

**What it typically contains:**
- Founding myths and origin stories (canonical)
- Cultural practices, customs, taboos
- Historical events that shape the present
- Religious or philosophical traditions
- Exploratory sections for myths under development or cultural details not yet referenced

**What makes it useful:**
Narrative truth over exhaustive cataloging. A lore doc is useful when it captures what these stories mean to the people who tell them — which versions are contested, what emotional resonance they carry, how they shape present-day behavior. "The founding myth says the river god sacrificed himself, but the northern clans believe he was murdered — this dispute underlies the current border conflict" is more useful than a neutral retelling of the myth.

**Anti-pattern:** An encyclopedia of myths and cultures with no connection to how they manifest in characters' lives or the plot. Worldbuilding for its own sake.

### Systems/Mechanics

The operational rules of the world: how magic works, how technology functions, how geography constrains travel, how the economy operates, how political power flows.

**What it typically contains:**
- System rules with explicit constraints and costs
- Geographic facts: distances, terrain, climate patterns
- Technology levels and capabilities
- Economic structures and resource flows
- Political hierarchies and power mechanics
- Exploratory sections for systems under development

**What makes it useful:**
Specs with consequences. Not just "mages draw power from ley lines" but "mages draw power from ley lines — sustained casting causes physical exhaustion proportional to distance from the nearest ley line, which means urban mages (near convergence points) can cast longer than rural ones, creating a geographic power disparity that drives the rural-urban political tension." Rules that connect to character experience and plot logic.

**Anti-pattern:** A technical manual that describes the system in isolation without exploring what it means for the people who live with it.

### Character Tracking

The working reference for character consistency during writing. Contains arcs, voice patterns, relationships, emotional trajectories, and key scene anchors.

**What it typically contains:**
- Character entries with arc summaries and current state
- Voice patterns: speech tics, vocabulary tendencies, rhetorical habits
- Emotional flickers: specific moments tracking arc trajectory (chapter + moment)
- Key scene anchors: pivotal choices, revelations, changes (chapter + moment)
- Relationship entries (bidirectional — if A relates to B, B relates to A)
- Intellectual frameworks: which ideas the character embodies
- Knowledge state tracking: what the character knows at various points

**What makes it useful:**
Behavioral specificity over generic description. Compare:
- Generic: "Kael is a brooding warrior haunted by his past."
- Specific: "Kael speaks in short declaratives when comfortable, shifts to passive constructions when lying ('mistakes were made' instead of 'I made a mistake'). Traces the scar on his left wrist when processing difficult emotions — unconscious habit introduced Ch. 3, noticed by Sera in Ch. 11. Thinks in military metaphors even about personal relationships ('tactical retreat' for avoiding a conversation)."

The specific version makes Kael writable. Any new scene can draw on these patterns to produce dialogue and behavior that sounds like Kael, not like a generic brooding warrior.

Emotional flickers work the same way. Not "Sera is becoming more confident" but: "Ch. 4: refuses to speak in council (baseline). Ch. 7: speaks in council but immediately apologizes for interrupting. Ch. 12: speaks in council, doesn't apologize, but hands shake afterward. Ch. 16: speaks in council, doesn't shake, but checks Maren's face for approval." This sequence is a diagnostic tool — any new scene can find its place on the trajectory.

**Anti-pattern:** Character profiles that read like RPG stat blocks or casting notices. "Age: 27. Hair: dark. Personality: brave, loyal, conflicted." These tell nothing about how to write the character.

### Style Conventions

The prose guardrails: how the story should be told, distinct from what it tells. Contains principles, rules, and checklists that maintain consistency across chapters.

**What it typically contains:**
- POV rules (which perspective, how close, what the narrator can and cannot know)
- Tense conventions
- Prose principles (e.g., "concrete over abstract," "show internal state through action")
- Anti-cliche rules (specific patterns to avoid with examples and alternatives)
- Intentional repetitions list (patterns that look like errors but are deliberate)
- Consistency checklist (formatting, naming conventions, terminology)
- Voice conventions for different narrative modes (action, introspection, dialogue)

**What makes it useful:**
Specific rules with examples. Not "avoid cliches" but "avoid: 'a chill ran down her spine,' 'time seemed to stop,' 'little did she know.' Instead: physicalize emotional reactions with character-specific gestures (see character docs for each character's patterns)." The intentional repetitions list is particularly valuable — it prevents well-meaning "corrections" of deliberate stylistic choices.

**Anti-pattern:** Vague aspirational statements ("write with vivid prose") that provide no actionable guidance.

### Outline/Diagnostic Hub

The control panel for the entire project. Scene-by-scene or chapter-by-chapter breakdown with cross-references to every other doc type.

**What it typically contains:**
- Chapter/scene entries with: summary, characters present, world elements in play, status
- Cross-references to timeline entries, system usage, character arc moments
- Character tracking across scenes (who appears where, what state they're in)
- Plot thread tracking (where threads open, develop, and resolve)
- Pacing notes (scene type, emotional weight, information density)

**What makes it useful:**
Dense cross-referencing. An outline entry for Chapter 8 that says "Battle scene, Sera and Kael" is less useful than one that says "Battle of Greymoor. Timeline: Year 412, day 3. Characters: Sera (first combat, arc moment — see flicker entry), Kael (tactical mode, commanding), Maren (absent — traveling, arrives Ch. 9). Systems: extended ley-line casting, exhaustion rules apply. Threads: Sera's confidence arc (escalation), Kael's leadership burden (complication), border conflict (climax of Act II). Status: drafted, needs revision for pacing in second half."

**Anti-pattern:** A simple plot summary that could be written from reading the manuscript. The outline's value is in connections the manuscript doesn't make explicit.

### Themes/Anti-Cliche

The project's aesthetic and intellectual commitments. What makes this story itself and not a generic version of its genre.

**What it typically contains:**
- Core thematic statements (what the story is actually about, beneath the plot)
- Philosophical framework (what questions the story asks, what positions it takes)
- Anti-cliche rules (specific to this project's genre and approach)
- Patterns to preserve (deliberate subversions, distinctive approaches)
- Thematic tracking across chapters (where themes surface, develop, complicate)

**What makes it useful:**
Specificity about what to avoid and why. Not "avoid fantasy cliches" but "avoid: the Chosen One who reluctantly accepts destiny (this story is about collective action, not individual exceptionalism), evil races (cultures in this world have internal diversity and historical reasons for conflict), prophecy as plot engine (characters make choices, the future isn't written)." The "why" matters — it helps apply the rule to edge cases.

**Anti-pattern:** A list of themes without guidance on how they manifest in editorial decisions. "Theme: identity" tells nothing about what to do differently.

### Editorial Backlog

The holding pen for ideas that aren't ready for canonical status. Prevents good ideas from being lost while keeping them from polluting authoritative docs.

**What it typically contains:**
- Future ideas with brief descriptions and potential impact assessment
- Sequel hooks and series-spanning threads
- Unexplored world elements that could be developed
- Deferred editorial decisions with context on why they were deferred
- Priority rankings (high-impact vs. nice-to-have)

**What makes it useful:**
Honest prioritization. Not every idea is equally important. A backlog that ranks items by potential impact ("this changes the entire magic system" vs. "this adds a nice detail to one scene") helps focus creative energy. Including context on why an item was deferred ("waiting to see how the Sera/Kael dynamic resolves before introducing this complication") prevents revisiting the same decision repeatedly.

**Anti-pattern:** An unsorted dump of every idea that comes up. Without prioritization, the backlog becomes noise.

### Feedback

The editorial history of the project. Date-stamped reviews, revision priorities, and progress tracking.

**What it typically contains:**
- Date-stamped editorial reviews (self-reviews, beta reader feedback, editor notes)
- Priority-ranked issues from each review
- Progress tracking (which issues have been addressed, which remain)
- Revision cycle summaries (what changed between drafts)

**What makes it useful:**
Date stamps and priority rankings. Feedback without dates loses its context ("was this about the current draft or two revisions ago?"). Feedback without priorities becomes an undifferentiated list where critical structural issues sit alongside minor word-choice preferences.

**Anti-pattern:** Feedback scattered across multiple files or buried in email threads. Centralizing it creates a revision history.

## CLAUDE.md for Worldbuilding Projects

A good worldbuilding project CLAUDE.md serves as the entry point to the editorial system. It should contain:

**Project overview** — Title, genre, format (novel, series, anthology), premise in one or two sentences, current status (drafting, revising, polishing).

**Document roles table** — Maps roles to filenames. "Timeline Authority: docs/timeline.md. Character Tracking: docs/characters.md." This is the lookup table that makes the role-based system work with actual files.

**Consistency rules** — What's canonical, what's exploratory, the canonical hierarchy as it applies to this project. Any project-specific rules ("Maren's dialogue is always in present tense, even in flashbacks — this is intentional").

**World structure summary** — The key facts about the world in compact form: era, geography basics, major systems, cultural groups. Enough to orient a new session without reading every doc.

**Character conventions** — Voice pattern summaries, anti-cliche commitments specific to characters ("no 'strong female character' tropes — Sera's strength is political, not physical").

**Series/related project references** — Paths to related projects, what's shared vs. local, which project is authoritative for shared facts.

**Propagation awareness notes** — Project-specific propagation patterns. "The timeline is tightly coupled to the character doc because of age-dependent plot points. Always check both when either changes."

Keep CLAUDE.md concise but current. It is read at the start of every session. Stale or bloated content degrades every interaction.
