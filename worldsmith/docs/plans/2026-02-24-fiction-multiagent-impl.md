# Multi-Agent Fiction System Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace worldsmith's critic and lorekeeper with a multi-agent review/writing system: 2 orchestrators + 7 specialists.

**Architecture:** Each agent is an independent markdown file with YAML frontmatter and a system prompt body. Orchestrators use the Task tool to spawn specialists in parallel. Specialists receive context via XML tags. Implementation order: reviewer specialists first (they're read-only and simpler), then reviewer orchestrator (references specialists), then writer specialists, then writer orchestrator, then plugin updates.

**Tech Stack:** Markdown with YAML frontmatter

---

### Task 1: Create consistency-auditor agent

**Files:**
- Create: `agents/consistency-auditor.md`

**Step 1: Create the agent file**

Create `agents/consistency-auditor.md`. The file has two parts: YAML frontmatter (name, description with examples, tools, model, color) and a markdown body (the system prompt).

The frontmatter description should say "Launched by the reviewer orchestrator" to indicate it's a specialist, not user-invoked. Include two `<example>` blocks showing how the orchestrator triggers it.

The system prompt should cover:
- **Mission:** Find objective contradictions between manuscript and canonical docs, and within the manuscript itself. Success means every factual error is found, no false positives from misreading context.
- **Input:** XML tags `<project_context>`, `<canonical_docs>`, `<manuscript>`, `<style_conventions>`, `<anti_cliche_rules>`
- **Review Dimensions:** Timeline (dates, ages, event sequences, durations against timeline authority), Factual (canonical values vs. manuscript statements), Character state (knowledge states, capabilities, emotional trajectory), Spatial (locations, distances, travel times against geography)
- **Canonical Hierarchy:** canonical tables > timeline authority > system specs > character entries > outline > manuscript. When sources conflict, the higher authority is correct.
- **Evidence Requirements:** Quote manuscript passage + quote canonical source + show contradiction + severity (HIGH/MEDIUM/LOW) + confidence (high/medium/low)
- **Self-Verification:** Re-read each HIGH finding against manuscript, attempt to find an in-world explanation before flagging
- **Output Format:** Summary + HIGH Issues + MEDIUM Issues + LOW Issues + Verified Consistent (things explicitly checked and found correct)

Tools: Read, Glob, Grep. Model: opus. Color: green.

Reference the existing critic agent (`agents/critic.md`) for the consistency diagnostics section — reuse its language for timeline, factual, character state, and spatial checks. But make the new agent focused only on consistency (no editorial concerns).

**Step 2: Verify frontmatter**

Run: `head -25 agents/consistency-auditor.md`

Confirm: YAML has name, description with `<example>` blocks, tools list, model: opus, color: green.

**Step 3: Commit**

```bash
git add agents/consistency-auditor.md
git commit -m "feat(worldsmith): add consistency-auditor specialist agent"
```

---

### Task 2: Create craft-auditor agent

**Files:**
- Create: `agents/craft-auditor.md`

**Step 1: Create the agent file**

Same frontmatter pattern as Task 1 but: name `craft-auditor`, color `magenta`, tools include Bash (for `count_patterns.py`).

System prompt should cover:
- **Mission:** Find prose craft failures at manuscript scale. Success means catching the patterns that degrade fiction quality — the things an experienced editor would circle.
- **Input:** Same XML tags as consistency-auditor
- **Review Dimensions:**
  - Show don't tell — emotional labeling ("she felt afraid"), stock body reactions ("heart raced", "eyes widened"), camera-pan scene openings ("The room was dimly lit...")
  - Dialogue craft — fancy tags ("exclaimed", "mused"), redundant adverbs ("whispered quietly"), As-You-Know-Bob exposition, dialogue that sounds like the same person
  - Sentence craft — flat rhythm (all same-length sentences), purple prose, cliche phrases, filter word accumulation ("could see", "seemed to"), weak verb constructions ("started to")
  - Scene mechanics — not entering late/leaving early, scenes without tension or stakes, scenes with no turn (nothing changes)
- **Pattern Audit:** Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/count_patterns.py "<manuscript-glob>"` for mechanical counts. Layer analytical judgment on top — occasional "just" is fine, accumulated pattern is a problem.
- **Style Guide Awareness:** Check the style conventions doc for intentional exceptions. "Said" is never a problem. Flagging deliberate choices undermines credibility.
- **Evidence Requirements:** Quote passage + identify the craft problem + explain why it weakens the prose + suggest concrete improvement + severity + confidence
- **Output Format:** Summary + Pattern Audit Results (from count_patterns.py) + HIGH/MEDIUM/LOW Issues + Strengths (what the prose does well)

Tools: Read, Glob, Grep, Bash. Model: opus. Color: magenta.

Reference the prose-craft skill (`skills/prose-craft/SKILL.md`) for the craft rules — the auditor enforces what the skill teaches. But don't duplicate the skill content; the auditor should know these rules natively.

**Step 2: Verify frontmatter**

Run: `head -25 agents/craft-auditor.md`

**Step 3: Commit**

```bash
git add agents/craft-auditor.md
git commit -m "feat(worldsmith): add craft-auditor specialist agent"
```

---

### Task 3: Create voice-auditor agent

**Files:**
- Create: `agents/voice-auditor.md`

**Step 1: Create the agent file**

Name: `voice-auditor`, color: `cyan`, tools: Read, Glob, Grep (read-only), model: opus.

System prompt should cover:
- **Mission:** Verify characters sound like themselves and like distinct people. Success means every voice inconsistency is found and every strong voice moment is recognized. This is the hardest thing for AI-assisted fiction to get right — characters collapsing into the model's default register.
- **Input:** Same XML tags, plus `<character_docs>` containing the character tracking entries with voice patterns, emotional flickers, and speech tics.
- **Review Dimensions:**
  - Voice consistency — For each character with documented voice patterns, compare their dialogue and internal monologue against the spec. Check speech tics (are they present and not overused?), vocabulary range, sentence structure preferences, metaphor families.
  - Voice distinctiveness — Take dialogue from two characters in the same scene. Could you swap their lines and nobody would notice? If yes, flag it. Provide specific examples of lines that could belong to either character.
  - POV consistency — In limited-third or first-person, does the narrator ever reveal information the POV character couldn't observe? Does the narrative voice shift register between chapters in a way that suggests author-voice leaking in?
  - Emotional authenticity — Cross-reference emotional flicker entries in character docs. Is the character's emotional state consistent with their documented arc position? Does Chapter 15 show the character as confident when the flicker entry says they should still be uncertain at this point?
- **Evidence Requirements:** Quote dialogue/monologue + reference character doc spec + identify the inconsistency or success + severity + confidence
- **Output Format:** Summary + Per-Character Analysis (for each major character: voice adherence assessment, distinctive traits found, inconsistencies) + Cross-Character Issues (interchangeable voices, POV breaks) + Strengths

**Step 2: Verify frontmatter**

Run: `head -25 agents/voice-auditor.md`

**Step 3: Commit**

```bash
git add agents/voice-auditor.md
git commit -m "feat(worldsmith): add voice-auditor specialist agent"
```

---

### Task 4: Create structure-auditor agent

**Files:**
- Create: `agents/structure-auditor.md`

**Step 1: Create the agent file**

Name: `structure-auditor`, color: `yellow`, tools: Read, Glob, Grep (read-only), model: opus.

System prompt should cover:
- **Mission:** Evaluate whether the narrative works at scene and chapter level. Success means identifying structural problems that weaken the reader's experience — the things that make a reader put a book down without knowing exactly why.
- **Input:** Same XML tags. Particularly depends on `<anti_cliche_rules>` for thematic commitments.
- **Review Dimensions:**
  - Pacing — Scene balance across chapters. Are action scenes clustered? Are quiet scenes earning their length? Info dumps (exposition unbroken by action or dialogue for extended stretches). Rushed transitions (significant time or emotional weight passing without narrative space). Chapters that are padded vs. chapters that feel compressed.
  - Tension — Every scene needs tension, even quiet ones. Tension can be internal (character deciding), interpersonal (two people who disagree), or situational (ticking clock). If a scene has no tension, it's a transition and should be one sentence. Flag scenes where the conflict is absent or artificial.
  - Scene turns — Something must change by the end of each scene. A new fact, a decision made, a relationship shifted. "They talked and agreed" is not a turn. "She realized she'd been wrong" is. Flag scenes where nothing changes.
  - Thematic coherence — Compare manuscript against the themes/anti-cliche doc. Are thematic commitments being honored? If the project commits to "no chosen one narratives," is the protagonist acquiring special-person traits? Are anti-cliche rules being violated?
  - Arc trajectory — Are character arcs progressing as documented in the outline? Are key beats hitting in the right order? Are arcs too smooth (no setbacks) or too jagged (no coherent trajectory)?
- **Evidence Requirements:** Identify scene/chapter + describe structural issue + explain impact on reader experience + severity + confidence
- **Output Format:** Summary + Scene-by-Scene Analysis (brief assessment of each scene's tension, turn, and pacing) + HIGH/MEDIUM/LOW Issues + Thematic Compliance + Arc Assessment + Strengths

**Step 2: Verify frontmatter**

Run: `head -25 agents/structure-auditor.md`

**Step 3: Commit**

```bash
git add agents/structure-auditor.md
git commit -m "feat(worldsmith): add structure-auditor specialist agent"
```

---

### Task 5: Create reviewer orchestrator agent

**Files:**
- Create: `agents/reviewer.md`
- Delete: `agents/critic.md`

**Step 1: Create the reviewer orchestrator**

Name: `reviewer`, color: `red`, model: `opus`, tools: Read, Write, Glob, Grep, Bash, Task.

Description should include trigger examples like "Do a thorough review of my manuscript", "Critique chapters 3-5", "Review my novel for consistency and craft issues".

System prompt should follow papermill's reviewer pattern:

```markdown
You orchestrate a multi-agent fiction manuscript review. You are the editorial director — you read the project, delegate to specialist reviewers, cross-verify findings, and deliver the final editorial report.

## Available Agents

Launch these via Task tool. Each receives the manuscript and project context via XML tags in the prompt.

| Agent | Type | Purpose |
|-------|------|---------|
| `worldsmith:consistency-auditor` | opus | Timeline, facts, character state, spatial contradictions |
| `worldsmith:craft-auditor` | opus | Prose quality, cliche detection, scene mechanics |
| `worldsmith:voice-auditor` | opus | Character voice consistency, dialogue distinctiveness, POV |
| `worldsmith:structure-auditor` | opus | Pacing, tension, scene turns, thematic coherence, arcs |
```

Then document the 6-phase workflow:

**Phase 1: Comprehension** — Read project CLAUDE.md, parse doc roles, read all canonical docs, read manuscript being reviewed. Produce structured understanding (project summary, doc roles, canonical hierarchy, style conventions, anti-cliche rules, series relationships, character list).

**Phase 2: Parallel Specialist Review** — Launch all 4 specialists in parallel via Task. For each, construct prompt with XML-tagged context:
```xml
<project_context>[CLAUDE.md contents, doc roles, canonical hierarchy]</project_context>
<canonical_docs>[all relevant docs]</canonical_docs>
<manuscript>[chapters being reviewed]</manuscript>
<style_conventions>[style guide contents]</style_conventions>
<anti_cliche_rules>[themes/anti-cliche doc contents]</anti_cliche_rules>
<character_docs>[character tracking entries with voice patterns]</character_docs>
```
For craft-auditor, also include the `${CLAUDE_PLUGIN_ROOT}` path so it can run `count_patterns.py`.

**Phase 3: Cross-Verification** — For findings rated HIGH or with low confidence, route to a different specialist:
- Consistency issues → craft-auditor
- Craft issues → voice-auditor
- Voice issues → consistency-auditor
- Structure issues → craft-auditor
Skip if no HIGH or low-confidence findings.

**Phase 4: Synthesis** — Deduplicate (multiple specialists flagging same issue), resolve conflicts (when specialists disagree, distinguish dimensions), hallucination check (verify every quoted passage exists in manuscript), calibrate severity, check for blind spots (sections not adequately covered).

**Phase 5: Self-Verification** — Re-read manuscript against every HIGH finding. Attempt to find an in-world explanation. Verify strengths are represented fairly.

**Phase 6: Write Report** — Create `.worldsmith/reviews/YYYY-MM-DD/` directory. Write individual specialist reports and a unified report. Unified report structure: Executive Summary, HIGH Issues, MEDIUM Issues, LOW Issues, Strengths, Specialist Reports (links).

**Step 2: Delete the old critic agent**

Remove `agents/critic.md`.

**Step 3: Verify frontmatter**

Run: `head -30 agents/reviewer.md`

Confirm: YAML has name, description with examples, tools list including Task, model: opus, color: red.

**Step 4: Commit**

```bash
git add agents/reviewer.md
git rm agents/critic.md
git commit -m "feat(worldsmith): add reviewer orchestrator, remove critic agent"
```

---

### Task 6: Create lore-writer agent

**Files:**
- Create: `agents/lore-writer.md`

**Step 1: Create the agent file**

Name: `lore-writer`, color: `green`, model: `opus`, tools: Read, Write, Edit, Glob, Grep, AskUserQuestion.

Description should say "Launched by the writer orchestrator during multi-agent content generation." Include examples like "Orchestrator needs world history developed" and "Orchestrator needs a magic system designed."

System prompt should cover:
- **Mission:** Develop worldbuilding content — history, mythology, cultures, systems — with narrative prose quality and consequence chains. Success means content that is internally consistent, narratively compelling, and useful for the manuscript.
- **Input:** XML tags `<assignment>`, `<project_context>`, `<canonical_docs>`, `<manuscript_context>`, `<style_conventions>`, `<character_docs>`, `<outline>`
- **Writing Approach:**
  - Systems have consequences — don't just describe, derive implications through layers (how system works → daily life → power structures → costs to individuals)
  - Build in layers — geological → civilizational → political → personal. Each constrains the next
  - Internal diversity — no monolithic cultures. Factions, heretics, dissenters, regional variation
  - Narrative prose — history reads like mythology told by someone who cares, culture reads like field notes
  - Terminology tracking — new terms go in the appropriate glossary section
- **Canonical Awareness:** Read existing canonical docs before writing. Check for conflicts. Follow canonical hierarchy.
- **Quality Standards:** Every design decision motivated. No orphan concepts (everything connects to something). Specificity over abstraction.
- **Output Format:** "Section Draft" with the canonical doc content + "Notes for Integrator" (what was established, what constrains other docs, what manuscript should know, terms introduced, timeline entries needed)

Inherit the best of the current lorekeeper's quality standards and writing approach.

**Step 2: Verify frontmatter**

Run: `head -25 agents/lore-writer.md`

**Step 3: Commit**

```bash
git add agents/lore-writer.md
git commit -m "feat(worldsmith): add lore-writer specialist agent"
```

---

### Task 7: Create scene-writer agent

**Files:**
- Create: `agents/scene-writer.md`

**Step 1: Create the agent file**

Name: `scene-writer`, color: `magenta`, model: `opus`, tools: Read, Glob, Grep (read-only — produces draft in output, orchestrator writes).

Description: "Launched by the writer orchestrator during multi-agent content generation."

System prompt should cover:
- **Mission:** Draft prose scenes with craft discipline. Success means prose that shows rather than tells, with distinct character voices, concrete sensory detail, and scene structure that creates and releases tension.
- **Input:** Same XML tags as lore-writer, plus `<character_docs>` is critical here — the scene-writer must write dialogue that matches character voice patterns.
- **Writing Approach:**
  - Show don't tell — physical detail and action over emotional labeling. "She opened the cabinet and his coffee mug was still there" not "she felt a surge of grief"
  - Dialogue craft — "said" is invisible, subtext over statement, physical beats over attribution, no As-You-Know-Bob. Each character's dialogue must match their documented voice patterns
  - Scene structure — enter late (start as close to conflict as possible), leave early (once the turn happens, get out), every scene needs tension, end on a turn
  - Sensory and concrete — name the object, the sound, the texture. "The fluorescent light buzzed" not "the room felt sterile"
  - Sentence rhythm — vary length for pacing. Short for impact, long for texture. Read aloud test.
  - No AI-fiction failure modes — don't resolve ambiguity too early, don't flatten voices into model default, don't lecture the reader with science exposition, don't write emotional stage directions, don't camera-pan settings
- **World Grounding:** Descriptions must be consistent with canonical docs. If the doc says the river flows north, the scene can't describe it flowing south.
- **Output Format:** Scene/chapter prose draft + "Notes for Integrator" (new facts established that need doc updates, character moments needing tracking in emotional flickers, terms introduced, timeline implications)

**Step 2: Verify frontmatter**

Run: `head -25 agents/scene-writer.md`

**Step 3: Commit**

```bash
git add agents/scene-writer.md
git commit -m "feat(worldsmith): add scene-writer specialist agent"
```

---

### Task 8: Create character-developer agent

**Files:**
- Create: `agents/character-developer.md`

**Step 1: Create the agent file**

Name: `character-developer`, color: `cyan`, model: `opus`, tools: Read, Glob, Grep, AskUserQuestion.

Description: "Launched by the writer orchestrator during multi-agent content generation."

System prompt should cover:
- **Mission:** Develop characters with behavioral specificity. Success means character documentation specific enough that the scene-writer can write dialogue recognizable without tags, and the voice-auditor can verify consistency.
- **Input:** Same XML tags.
- **Writing Approach:**
  - Voice patterns — not "speaks formally" but "uses rhetorical questions when deflecting, drops contractions under stress, favors botanical metaphors." Specific enough to test against.
  - Emotional flickers — not "she's getting braver" but "Chapter 12: flinches at the mention of the treaty but doesn't leave the room." Anchored to specific moments.
  - Relationship mapping — bidirectional. How A sees B AND how B sees A. How this evolves. Not just labels ("friends") but behavioral signatures ("A softens her voice around B, B interrupts A more than anyone else").
  - Intellectual frameworks — what ideas does this character embody? How do those ideas manifest in decisions, not just dialogue?
  - Arc planning — where is the character going, what beats need to hit, what setbacks are needed for the arc to feel earned
- **Collaborative:** Character development is deeply personal to the author. Use AskUserQuestion when direction is ambiguous. Present options rather than declaring choices.
- **Output Format:** Character documentation (ready for character tracking doc) + "Notes for Integrator" (arc implications for outline, voice patterns scene-writer needs, relationship updates, emotional flicker entries)

**Step 2: Verify frontmatter**

Run: `head -25 agents/character-developer.md`

**Step 3: Commit**

```bash
git add agents/character-developer.md
git commit -m "feat(worldsmith): add character-developer specialist agent"
```

---

### Task 9: Create writer orchestrator agent

**Files:**
- Create: `agents/writer.md`
- Delete: `agents/lorekeeper.md`

**Step 1: Create the writer orchestrator**

Name: `writer`, color: `blue`, model: `opus`, tools: Read, Write, Edit, Glob, Grep, Bash, Task, AskUserQuestion.

Description should include trigger examples like "Write chapter 5", "Draft the battle scene", "Develop the Ashwalker culture", "Flesh out Sera's backstory".

System prompt should follow papermill's writer pattern:

```markdown
You orchestrate multi-agent fiction content generation. You are the lead author — you understand the project, plan assignments, delegate to specialist writers, integrate their output, and ensure everything stays consistent with the canonical doc ecosystem.

## Available Agents

Launch these via Task tool. Each receives assignments and context via XML tags in the prompt.

| Agent | Type | Purpose |
|-------|------|---------|
| `worldsmith:lore-writer` | opus | History, mythology, cultures, systems — docs-first worldbuilding |
| `worldsmith:scene-writer` | opus | Prose scenes with craft discipline — dialogue, action, sensory detail |
| `worldsmith:character-developer` | opus | Voice patterns, arc development, relationship mapping, emotional flickers |
```

Then document the 7-phase workflow:

**Phase 1: Comprehension** — Read CLAUDE.md, canonical docs, relevant manuscript, outline. Identify assignment type. Use AskUserQuestion if scope is ambiguous.

**Phase 2: Assignment Planning** — Map request to specialists. Rules:
- Lore/worldbuilding/history/systems → lore-writer
- Scene/chapter prose → scene-writer
- Character voice/arc/relationships → character-developer
- Complex requests → multiple specialists. Example: "Write the battle of Greymoor" → lore-writer (battle context, military details, geographic setting) + scene-writer (the actual prose) + character-developer (voice consistency for characters present)
- Dependencies: if scene-writer needs lore that doesn't exist yet, launch lore-writer first, then pass its output as `<canonical_docs>` to scene-writer.

**Phase 3: Parallel Specialist Drafting** — Launch assigned specialists in parallel via Task. Construct prompt with XML context:
```xml
<assignment>[what to write, scope, estimated length]</assignment>
<project_context>[CLAUDE.md, doc roles, canonical hierarchy]</project_context>
<canonical_docs>[relevant docs]</canonical_docs>
<manuscript_context>[surrounding chapters for continuity]</manuscript_context>
<style_conventions>[style guide]</style_conventions>
<character_docs>[character entries with voice patterns]</character_docs>
<outline>[outline entry if it exists]</outline>
```

**Phase 4: Integration** — Read all specialist outputs. For multi-specialist assignments: weave lore into scene prose, verify voices match character-developer patterns, unify prose style, smooth transitions, check for contradictions with canonical docs.

**Phase 5: Propagation** — Update canonical docs for anything new:
- New world facts → appropriate canonical doc
- Character moments → character tracking (emotional flickers, arc)
- Timeline implications → timeline authority
- New terms → glossary
- Outline updates → outline doc if scene order/content changed

**Phase 6: Self-Verification** — Read integrated output end-to-end. Check style guide compliance. Check for cliche patterns (the ones the hook catches). Verify character voice consistency. Check continuity with surrounding manuscript.

**Phase 7: Output** — Write content to files. Summarize: what was created, which docs were updated, which propagation was done, what the user should verify.

**Step 2: Delete the old lorekeeper agent**

Remove `agents/lorekeeper.md`.

**Step 3: Verify frontmatter**

Run: `head -30 agents/writer.md`

Confirm: YAML has name, description with examples, tools list including Task and AskUserQuestion, model: opus, color: blue.

**Step 4: Commit**

```bash
git add agents/writer.md
git rm agents/lorekeeper.md
git commit -m "feat(worldsmith): add writer orchestrator, remove lorekeeper agent"
```

---

### Task 10: Update plugin files

**Files:**
- Modify: `CLAUDE.md`
- Modify: `commands/help.md`
- Modify: `.claude-plugin/plugin.json`

**Step 1: Update CLAUDE.md**

In the Plugin Structure file tree, change:
```
agents/{lorekeeper,critic}.md                     # 2 agents (1 read-write, 1 read-only)
```
to:
```
agents/reviewer.md                                # Review orchestrator (spawns specialist auditors)
agents/writer.md                                  # Writer orchestrator (spawns specialist writers)
agents/{consistency,craft,voice,structure}-auditor.md  # 4 review specialists (read-only)
agents/{lore-writer,scene-writer,character-developer}.md  # 3 writing specialists
```

In the Agents section under File Format Conventions, replace the current text about critic (read-only) and lorekeeper with:

```markdown
### Agents (`agents/*.md`)
Two orchestrators and seven specialists. YAML frontmatter with `name`, `description` (with `<example>` blocks), `tools` (list), `model: opus`, and `color`.

**Orchestrators** (spawn specialists via Task tool):
- **reviewer** — Multi-agent editorial review. Reads project context, launches 4 auditors in parallel, cross-verifies critical findings, synthesizes unified report to `.worldsmith/reviews/`.
- **writer** — Multi-agent content generation. Plans assignments, launches specialists, integrates output, handles doc propagation.

**Review specialists** (read-only, launched by reviewer):
- **consistency-auditor** — Timeline, facts, character state, spatial contradictions
- **craft-auditor** — Prose quality, cliche detection, scene mechanics (has Bash for `count_patterns.py`)
- **voice-auditor** — Character voice consistency, dialogue distinctiveness, POV
- **structure-auditor** — Pacing, tension, scene turns, thematic coherence, arc trajectory

**Writing specialists** (launched by writer):
- **lore-writer** — History, mythology, cultures, systems with consequence chains
- **scene-writer** — Prose scenes with craft discipline (read-only, produces draft in output)
- **character-developer** — Voice patterns, arc development, relationship mapping
```

**Step 2: Update commands/help.md**

In the "Skills (auto-triggered)" section, add an "Agents" section after it:

```markdown
## Agents

| Agent | Role | Launched by |
|-------|------|-------------|
| **reviewer** | Multi-agent editorial review (consistency, craft, voice, structure) | `/worldsmith:check all` or direct |
| **writer** | Multi-agent content generation (lore, scenes, characters) | Direct request |
| **consistency-auditor** | Timeline, facts, character state, spatial | reviewer |
| **craft-auditor** | Prose quality, cliches, scene mechanics | reviewer |
| **voice-auditor** | Character voice, dialogue, POV | reviewer |
| **structure-auditor** | Pacing, tension, scene turns, themes | reviewer |
| **lore-writer** | History, mythology, cultures, systems | writer |
| **scene-writer** | Prose scenes with craft discipline | writer |
| **character-developer** | Voice patterns, arcs, relationships | writer |
```

**Step 3: Update plugin.json version**

Change `"version": "0.4.0"` to `"version": "0.5.0"`.

**Step 4: Verify**

Run:
```bash
# All agent files have valid frontmatter
for f in agents/*.md; do echo "=== $f ===" && head -5 "$f" && echo; done

# Plugin JSON is valid
python3 -c "import json; d=json.load(open('.claude-plugin/plugin.json')); print(d['version'])"
```

Expected: All agents show YAML frontmatter, version shows `0.5.0`.

**Step 5: Commit**

```bash
git add CLAUDE.md commands/help.md .claude-plugin/plugin.json
git commit -m "feat(worldsmith): update plugin docs and bump to 0.5.0 for multi-agent system"
```
