# Multi-Agent Fiction Review and Writing System

**Date:** 2026-02-24

## Summary

Replace worldsmith's two single-purpose agents (critic, lorekeeper) with a multi-agent architecture modeled on papermill's reviewer/writer orchestrators. Two orchestrators spawn specialist agents in parallel for deep, focused analysis and generation. The reviewer orchestrator handles editorial critique; the writer orchestrator handles world-grounded content creation.

## Architecture

Two orchestrators + seven specialists = nine agents total.

```
reviewer (orchestrator, opus, red)
  ├── consistency-auditor (opus, green)
  ├── craft-auditor (opus, magenta)
  ├── voice-auditor (opus, cyan)
  └── structure-auditor (opus, yellow)

writer (orchestrator, opus, blue)
  ├── lore-writer (opus, green)
  ├── scene-writer (opus, magenta)
  └── character-developer (opus, cyan)
```

Orchestrators spawn specialists in parallel via the Task tool, collect results, and synthesize/integrate. Specialists are independent — they don't communicate with each other, only with the orchestrator.

## Reviewer Orchestrator

**Replaces:** critic agent
**Trigger:** "review my manuscript", "full editorial review", "critique chapters 3-5", "do a thorough review"
**Tools:** Read, Write, Glob, Grep, Bash, Task

### Workflow

1. **Comprehension** — Read project CLAUDE.md, parse doc roles, read canonical docs (timeline, characters, style guide, themes), read manuscript being reviewed. Produce structured understanding.

2. **Parallel Specialist Review** — Launch all 4 specialists in parallel via Task. Each receives XML context:
   ```xml
   <project_context>[CLAUDE.md, doc roles, canonical hierarchy]</project_context>
   <canonical_docs>[timeline, characters, style, themes, lore, systems]</canonical_docs>
   <manuscript>[chapters being reviewed]</manuscript>
   <style_conventions>[style guide]</style_conventions>
   <anti_cliche_rules>[themes/anti-cliche doc]</anti_cliche_rules>
   ```

3. **Cross-Verification** — For critical or low-confidence findings, route to a different specialist:
   - Consistency → craft-auditor (prose problem masking a fact error?)
   - Craft → voice-auditor (voice issue, not generic craft?)
   - Voice → consistency-auditor (does character doc actually specify this?)
   - Structure → craft-auditor (pacing issue actually prose density?)

4. **Synthesis** — Deduplicate findings, resolve conflicts, verify quoted text exists in manuscript, calibrate severity.

5. **Self-Verification** — Re-read manuscript against critical findings. Verify every HIGH finding.

6. **Report** — Write unified report to `.worldsmith/reviews/YYYY-MM-DD/` with severity-grouped findings (HIGH/MEDIUM/LOW).

### Key difference from papermill reviewer

No literature scouts — fiction's ground truth is the project's own canonical docs, not external literature. The orchestrator front-loads canonical doc reading and passes full project context to all specialists.

## Reviewer Specialists

### consistency-auditor

**Mission:** Find objective contradictions between manuscript and canonical docs, and within the manuscript itself.

**Tools:** Read, Glob, Grep (read-only)

**Review dimensions:**
- **Timeline** — dates, ages, event sequences, durations against timeline authority
- **Factual** — canonical values (system rules, geography, history, culture) vs. manuscript
- **Character state** — knowledge states, capabilities, emotional trajectory consistency
- **Spatial** — locations, distances, travel times against established geography

**Evidence standard:** Quote manuscript passage + quote canonical source + show contradiction + severity + confidence.

### craft-auditor

**Mission:** Find prose craft failures at manuscript scale.

**Tools:** Read, Glob, Grep, Bash (runs `count_patterns.py`)

**Review dimensions:**
- **Show don't tell** — emotional labeling, stock body reactions, camera-pan openings
- **Dialogue craft** — fancy tags, redundant adverbs, As-You-Know-Bob exposition
- **Sentence craft** — flat rhythm, purple prose, cliche phrases, filter word accumulation
- **Scene mechanics** — not entering late/leaving early, scenes without tension, no turn

Bash access for `count_patterns.py` mechanical pattern counting. Layers analytical judgment on top of the counts.

### voice-auditor

**Mission:** Verify characters sound like themselves and like distinct people.

**Tools:** Read, Glob, Grep (read-only)

**Review dimensions:**
- **Voice consistency** — dialogue/monologue vs. character doc voice patterns (speech tics, vocabulary, metaphor preferences)
- **Voice distinctiveness** — interchangeable voices between characters
- **POV consistency** — limited-third accidentally revealing unobservable thoughts
- **Emotional authenticity** — emotional register matches arc position (references emotional flicker entries)

Fiction-specific specialist with no academic analogue.

### structure-auditor

**Mission:** Evaluate whether the narrative works at scene and chapter level.

**Tools:** Read, Glob, Grep (read-only)

**Review dimensions:**
- **Pacing** — scene balance, info dumps, rushed transitions, chapters that don't earn their length
- **Tension** — every scene needs tension, quiet scenes doing work or filling space
- **Scene turns** — something changes by end of each scene, turns are earned
- **Thematic coherence** — manuscript vs. themes/anti-cliche doc, commitments honored
- **Arc trajectory** — character arcs progressing as documented, beats hitting in order

## Writer Orchestrator

**Replaces:** lorekeeper agent
**Trigger:** "write chapter 5", "draft the battle scene", "develop the Ashwalker culture", "flesh out Sera's backstory"
**Tools:** Read, Write, Edit, Glob, Grep, Bash, Task, AskUserQuestion

### Workflow

1. **Comprehension** — Read project CLAUDE.md, canonical docs, relevant manuscript, outline entry. Identify assignment type: lore development, scene draft, or character work.

2. **Assignment Planning** — Map request to specialists:
   - Lore/worldbuilding/history/systems → lore-writer
   - Scene/chapter prose → scene-writer
   - Character voice/arc/relationships → character-developer
   - Complex requests may need multiple specialists (e.g., "write the battle of Greymoor" → lore-writer for context + scene-writer for prose + character-developer for voices)

3. **Parallel Specialist Drafting** — Launch assigned specialists in parallel via Task:
   ```xml
   <assignment>[what to write, scope, estimated length]</assignment>
   <project_context>[CLAUDE.md, doc roles, canonical hierarchy]</project_context>
   <canonical_docs>[relevant docs]</canonical_docs>
   <manuscript_context>[surrounding chapters for continuity]</manuscript_context>
   <style_conventions>[style guide]</style_conventions>
   <character_docs>[relevant character entries with voice patterns]</character_docs>
   <outline>[outline entry if it exists]</outline>
   ```

4. **Integration** — Merge specialist outputs:
   - Weave lore context into scene prose
   - Verify character voices match character-developer's patterns
   - Unify prose style, smooth transitions
   - Ensure canonical consistency

5. **Propagation** — Update canonical docs for anything new established:
   - New world facts → appropriate canonical doc
   - Character moments → character tracking (emotional flickers, arc progression)
   - Timeline implications → timeline authority
   - New terms → glossary

6. **Self-Verification** — Read integrated output end-to-end against style guide, prose-craft rules, character voices, continuity.

7. **Output** — Write content to files. Summarize what was created, what docs were updated, what user should verify.

### Key differences from papermill writer

- **Propagation phase** — fiction has a canonical doc ecosystem that must be updated after writing, not just read before.
- **AskUserQuestion** — creative writing needs user direction. Academic writing follows a spec.
- **No format-validator** — no compilation step. Self-verification against style guide and prose-craft rules instead.

## Writer Specialists

### lore-writer

**Mission:** Develop worldbuilding content with narrative prose quality and consequence chains.

**Tools:** Read, Write, Edit, Glob, Grep, AskUserQuestion

**Writing approach:**
- Systems have consequences — derive implications through layers
- Build in layers — geological → civilizational → political → personal
- Internal diversity — no monolithic cultures
- Narrative prose, not encyclopedia — history reads like mythology, culture reads like field notes

**Output:** Canonical doc content + notes for integrator (what was established, what constrains other docs, what manuscript should know).

### scene-writer

**Mission:** Draft prose scenes with craft discipline — prose-craft rules applied during creation.

**Tools:** Read, Glob, Grep (read-only — produces draft in output, orchestrator writes)

**Writing approach:**
- Show don't tell — physical detail over emotional labeling
- Dialogue craft — "said" invisible, subtext, distinct voices, physical beats
- Scene structure — enter late, leave early, tension, end on turn
- Sensory and concrete — specific objects, sounds, textures
- No AI-fiction failure modes — don't resolve ambiguity early, don't flatten voices, don't lecture

**Output:** Scene/chapter prose + notes for integrator (new facts needing doc updates, character moments needing tracking, terms introduced).

### character-developer

**Mission:** Develop characters with behavioral specificity.

**Tools:** Read, Glob, Grep, AskUserQuestion

**Writing approach:**
- Voice patterns — specific enough to recognize without tags
- Emotional flickers — anchored moments tracking arc trajectory
- Relationship mapping — bidirectional, evolving
- Intellectual frameworks — ideas that shape decisions
- Arc planning — trajectory between key moments

**Output:** Character documentation + notes for integrator (arc implications for outline, voice patterns for scene-writer, relationship updates).

Gets AskUserQuestion because character development is deeply collaborative.

## Plugin Changes

| Current | New | Change |
|---|---|---|
| `agents/critic.md` | `agents/reviewer.md` | Replace |
| `agents/lorekeeper.md` | `agents/writer.md` | Replace |
| — | `agents/consistency-auditor.md` | New |
| — | `agents/craft-auditor.md` | New |
| — | `agents/voice-auditor.md` | New |
| — | `agents/structure-auditor.md` | New |
| — | `agents/lore-writer.md` | New |
| — | `agents/scene-writer.md` | New |
| — | `agents/character-developer.md` | New |
| `commands/help.md` | Update | Document new agents |
| `CLAUDE.md` | Update | Document multi-agent architecture |
| `.claude-plugin/plugin.json` | 0.4.0 → 0.5.0 | Major feature addition |

Net: 2 agents deleted, 9 agents created (+7).

## Design Decisions

- **Approach A (lean specialists):** 4 reviewer + 3 writer specialists rather than further decomposition. Worldbuilding plausibility fits inside consistency-auditor (checks docs against docs). Thematic drift fits inside structure-auditor (narrative-level coherence). Systems design is the lore-writer's core strength. Can split later if overloaded.
- **Replace, don't coexist:** The orchestrators subsume all critic and lorekeeper functionality. Keeping both would confuse which to use and double the maintenance.
- **XML context passing (from papermill):** Orchestrator reads once, packages as XML tags, distributes to specialists. Structured input is cleaner and less ambiguous than prose instructions.
- **Parallel spawning (from papermill):** Specialists are independent — spawn in parallel, collect results, synthesize/integrate. No sequential pipelines unless a specialist's output feeds another.
- **Cross-verification (from papermill):** Only for critical/low-confidence findings, with intelligent routing based on finding type. Not systematic — that would be redundant.
- **Propagation phase (fiction-specific):** Writer orchestrator updates canonical docs after writing. This is the key difference from academic writing — fiction has a living doc ecosystem.
- **scene-writer is read-only:** Produces draft text in output; orchestrator decides where to write. This prevents specialists from making uncoordinated file changes.
- **voice-auditor is fiction-specific:** No academic analogue. Character voice consistency is the hardest thing for AI to get right in fiction — it deserves its own specialist.
- **All specialists opus:** Fiction analysis and generation require deep reasoning. No sonnet specialists — there's no equivalent of format-validator (mechanical checking) in this domain.
