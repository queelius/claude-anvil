# Multi-Agent Fiction Manuscript Reviewer

**Date:** 2026-02-24

## Summary

A multi-agent manuscript review system for worldsmith, modeled on papermill's academic reviewer. An Opus orchestrator dispatches 5 Sonnet specialist critics in parallel, each evaluating the manuscript against a specific rubric, then synthesizes findings into a unified review report with cross-verification and hallucination detection.

## Research basis

Design informed by:
- Anthropic's "Building Effective Agents" (orchestrator-workers pattern, start simple, add complexity only when it demonstrably improves outcomes)
- Anthropic's multi-agent research system (3-5 subagents, selective context, lightweight references)
- Single-agent-with-skills research (multi-agent justified only for genuine parallelism — review from independent perspectives qualifies)
- Creative writing with AI best practices (selective context injection, 64K degradation threshold, evaluator-optimizer pattern, rubric-specific critique over vague feedback)
- Papermill's proven orchestrator + parallel specialists + synthesis architecture

## Architecture

```
User: "/worldsmith:review [scope]"
    │
    ├─ review skill reads project CLAUDE.md, identifies manuscript + docs
    │
    ├─ [Phase 1] Orchestrator (Opus) reads manuscript + canonical docs
    │            Produces structured comprehension summary
    │            Builds context packets per specialist
    │
    ├─ [Phase 2] 5 specialist critics dispatched in PARALLEL (Sonnet)
    │    ├─ continuity-checker
    │    ├─ prose-analyst
    │    ├─ voice-evaluator
    │    ├─ pacing-analyst
    │    └─ worldbuilding-validator
    │
    ├─ [Phase 3] Cross-verification of critical/low-confidence findings
    │
    ├─ [Phase 4] Synthesis — deduplicate, resolve conflicts, verify quotes
    │
    └─ [Phase 5] Write report to .worldsmith/reviews/YYYY-MM-DD/
```

### Key differences from papermill's reviewer

- No literature scouts (fiction doesn't need web search for prior art)
- Canonical docs replace literature context (specialists receive relevant lore/timeline/characters)
- Voice evaluator is fiction-specific (no academic analog)
- Reports go to `.worldsmith/reviews/` not `.papermill/reviews/`

## The orchestrator

**Agent: `reviewer`** — Opus, read-write

**Tools:** Read, Write, Glob, Grep, Task, AskUserQuestion

**Phases:**

1. **Comprehend** — read the manuscript scope (chapter, section, or full manuscript) and extract relevant canonical docs using the project's CLAUDE.md document roles table.

2. **Build context packets** — selective context injection per specialist. Each specialist gets the manuscript text + only the canonical docs relevant to their rubric. Never dump the full document ecosystem into every specialist.

3. **Dispatch** — launch all 5 specialists in parallel via Task tool, each receiving their tailored context packet.

4. **Cross-verify** — for any finding rated critical or low-confidence, route to a different specialist for a second opinion:
   - Continuity issues → worldbuilding-validator
   - Prose issues → voice-evaluator (is flat prose actually a voice problem?)
   - Voice issues → prose-analyst (is voice drift actually a prose rhythm problem?)
   - Pacing issues → continuity-checker (is the pacing issue caused by a timeline inconsistency?)
   - Worldbuilding issues → continuity-checker (is the system violation also a factual contradiction?)

5. **Synthesize** — deduplicate findings (multiple specialists flag same issue → keep most specific), resolve conflicts, verify all quoted manuscript text actually exists (hallucination check), calibrate severity.

6. **Report** — write unified review + individual specialist reports.

**Recommendation criteria:**
- **polished** — no critical issues, minor polish only
- **revision** — no critical, some major issues, addressable in a revision pass
- **rework** — critical consistency/voice/worldbuilding issues, or multiple major across dimensions
- **structural** — fundamental pacing/structure problems requiring outline-level changes

## The five specialists

All specialists: read-only (Read, Glob, Grep only), Sonnet 4.6, produce findings in shared format: severity (critical/major/minor/suggestion), confidence (high/medium/low), quoted evidence, location, concrete recommendation.

### continuity-checker

**Rubric:** Does the manuscript contradict established canon?

- Timeline: dates, ages, event sequences, elapsed time within scenes
- Character knowledge states: does a character act on information they shouldn't have yet?
- Spatial consistency: distances, travel times, locations, architectural details
- Factual consistency: canonical table values, system rules, established world facts
- Cross-chapter continuity: details introduced in earlier chapters contradicted or forgotten

**Context:** Timeline authority, character entries, system specs, outline.

### prose-analyst

**Rubric:** Is the prose craft sound?

- Show vs tell: emotional labeling, stock body reactions, sensation naming
- Sensory specificity: abstract vs concrete, vague adjectives vs precise detail
- Sentence rhythm: monotonous patterns, paragraph-level pacing, varied length
- Cliche density: dead metaphors, purple prose, AI-fiction stock phrases
- Adverb/dialogue tag discipline: redundant adverbs, fancy tags, attribution vs physical beats
- Scene structure: enter late/leave early, camera-pan openings, lingering exits

**Context:** Style conventions doc. Works primarily from manuscript text.

### voice-evaluator

**Rubric:** Do characters sound like themselves and distinct from each other?

- Voice distinctness: vocabulary, sentence length, world-noticing patterns per character
- Dialogue authenticity: subtext vs statement, "As You Know Bob" exposition
- Internal monologue consistency: POV character interiority matches documented personality
- Voice drift: character starts sounding like narrator or other characters
- Register appropriateness: education, background, profession reflected in speech

**Context:** Character sheets (voice patterns, speech tics, background, education level).

### pacing-analyst

**Rubric:** Does the narrative maintain momentum and earn its length?

- Scene tension: does every scene have tension (even quiet scenes)?
- Scene turns: does something change by the end of each scene?
- Information density: info dumps, lecture scenes, exposition that stops the plot
- Balance: chapter length relative to narrative content, rushed vs draggy sections
- Transition efficiency: transitions that are one sentence vs three pages
- Opening/closing: chapter opens with action or camera pan? Ends on turn or lingers?

**Context:** Outline (scene purposes, arc moments).

### worldbuilding-validator

**Rubric:** Is the world internally consistent and systems applied correctly?

- System rule compliance: magic/technology/social systems used consistently with docs
- Consequences: actions have plausible consequences given world's rules
- Scale and logistics: army sizes, economic plausibility, political structures
- Cultural consistency: characters from documented cultures behave consistently
- Internal plausibility: would this work within the world as established

**Context:** System specs, lore docs, relevant worldbuilding entries.

## Invocation

### Command: `/worldsmith:review [scope]`

Scope can be:
- A chapter reference: `/worldsmith:review chapter 7`
- A file path: `/worldsmith:review chapters/07-the-crossing.md`
- Full manuscript: `/worldsmith:review manuscript`
- Default: asks what to review

### Skill: `skills/review/SKILL.md`

Entry point workflow:
1. Read project CLAUDE.md, parse document roles
2. Identify manuscript files matching the requested scope
3. Ask for optional focus areas (e.g., "I'm worried about pacing in the second half")
4. Dispatch reviewer orchestrator agent via Task tool
5. Present results summary
6. Suggest next steps

### Context packet construction

The orchestrator builds tailored context per specialist:

**All specialists get:**
- Manuscript text being reviewed
- Style conventions (if they exist)

**Additionally:**
- continuity-checker: timeline authority, character entries, system specs, outline
- prose-analyst: style conventions only
- voice-evaluator: character sheets
- pacing-analyst: outline
- worldbuilding-validator: system specs, lore docs

This is selective context injection — each specialist gets only what's relevant to their rubric.

## Report output

Reports go to `.worldsmith/reviews/YYYY-MM-DD/`:

```
.worldsmith/reviews/2026-02-24/
├── review.md                    # Unified report (orchestrator synthesis)
├── continuity-checker.md        # Individual specialist reports
├── prose-analyst.md
├── voice-evaluator.md
├── pacing-analyst.md
└── worldbuilding-validator.md
```

Unified report structure:
- Recommendation (polished / revision / rework / structural)
- Summary + strengths + weaknesses
- Finding counts by severity
- Detailed findings grouped by severity (critical → major → minor → suggestion)
- Domain-specific summaries (one section per specialist)
- Review metadata (scope reviewed, specialists used, cross-verifications, disagreements)

## Integration with existing worldsmith

**Doesn't replace anything:**
- `/worldsmith:check` — quick single-agent diagnostics (daily driver)
- Critic agent — lightweight read-only analysis
- Lorekeeper agent — creative worldbuilding (read-write)
- Prose-craft skill — real-time craft guardrails
- Cliche detection hook — real-time enforcement

**The reviewer is the deep analysis tool** — invoked deliberately for thorough feedback. The fiction equivalent of a developmental editor with a red pen.

## Files to create

```
agents/reviewer.md                    # Orchestrator (Opus)
agents/continuity-checker.md          # Specialist (Sonnet)
agents/prose-analyst.md               # Specialist (Sonnet)
agents/voice-evaluator.md             # Specialist (Sonnet)
agents/pacing-analyst.md              # Specialist (Sonnet)
agents/worldbuilding-validator.md     # Specialist (Sonnet)
skills/review/SKILL.md                # Review workflow skill
commands/review.md                    # /worldsmith:review command
```

**Files to update:** CLAUDE.md, commands/help.md, .claude-plugin/plugin.json (version bump to 0.4.0).

## Design decisions

- **Sonnet for specialists, Opus for orchestrator**: 40-60% cost reduction per the research. Specialists have focused rubrics that Sonnet handles well; the orchestrator needs Opus-level judgment for synthesis, cross-verification, and hallucination detection.
- **5 specialists, not more**: Research shows 3-5 is the sweet spot. Diminishing returns beyond that. Each specialist has a genuinely distinct lens.
- **Selective context injection**: Each specialist gets only the canonical docs relevant to their rubric. Avoids the 64K degradation threshold. The orchestrator curates context packets.
- **Read-only specialists**: Findings flow up to the orchestrator. No specialist writes to disk or sees other specialists' work. Prevents groupthink, enables independent assessment.
- **Cross-verification for critical findings only**: Not every finding needs a second opinion. Only critical severity or low confidence findings are re-routed, keeping cost proportional.
- **Reports in `.worldsmith/`**: Consistent with the new `.worldsmith/` convention. Reviews persist for future reference and can inform subsequent editing sessions.
- **Separate from `/worldsmith:check`**: Check is fast diagnostics; review is deep analysis. Different tools for different moments in the workflow.
