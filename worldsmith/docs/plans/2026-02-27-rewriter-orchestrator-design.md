# Rewriter Orchestrator Design

**Goal:** Add a third orchestrator to worldsmith's multi-agent system. The rewriter bridges the reviewer (diagnoses) and writer (creates) by implementing fixes from review findings with a fix-then-verify feedback loop.

**Trigger:** "Fix the issues from the review", "Implement the review feedback", "Revise based on the editorial report", or any request to edit existing manuscript based on review findings.

## Architecture

The rewriter is an orchestrator that reuses all 7 existing specialists — 3 writer specialists for fixing, 4 reviewer specialists for verifying. No new specialist agents needed.

- **Name:** `rewriter`
- **Color:** `purple`
- **Model:** opus
- **Tools:** Read, Write, Edit, Glob, Grep, Bash, Task, AskUserQuestion

### Specialists Used

**For fixing (writer specialists):**

| Agent | Used when... |
|-------|-------------|
| `worldsmith:scene-writer` | Prose craft fixes, dialogue rewrites, show-don't-tell conversions, scene restructuring |
| `worldsmith:lore-writer` | Canonical doc corrections, factual fixes, timeline repairs, terminology standardization |
| `worldsmith:character-developer` | Voice pattern fixes, arc corrections, emotional flicker updates, relationship consistency |

**For verifying (reviewer specialists):**

| Agent | Verifies... |
|-------|------------|
| `worldsmith:consistency-auditor` | Factual/timeline/spatial fixes resolved the contradiction without introducing new ones |
| `worldsmith:craft-auditor` | Prose craft fixes actually improved the passage (not just rearranged the problem) |
| `worldsmith:voice-auditor` | Voice/dialogue fixes match character specs and maintain distinctiveness |
| `worldsmith:structure-auditor` | Structure/pacing fixes improved narrative flow without damaging arc trajectory |

### Finding-to-Specialist Mapping

| Finding domain | Fix specialist | Verify specialist |
|---------------|---------------|-------------------|
| Timeline contradiction | lore-writer | consistency-auditor |
| Factual error | lore-writer | consistency-auditor |
| Character state violation | scene-writer + character-developer | consistency-auditor |
| Spatial impossibility | scene-writer | consistency-auditor |
| Show-don't-tell violation | scene-writer | craft-auditor |
| Dialogue craft failure | scene-writer | voice-auditor + craft-auditor |
| Cliche/stock reaction | scene-writer | craft-auditor |
| Voice inconsistency | scene-writer (with character-developer guidance) | voice-auditor |
| POV violation | scene-writer | voice-auditor |
| Pacing problem | scene-writer | structure-auditor |
| Missing scene turn | scene-writer | structure-auditor |
| Thematic violation | scene-writer | structure-auditor |
| Arc trajectory issue | scene-writer + character-developer | structure-auditor |

## 6-Phase Workflow

### Phase 1: Comprehension

Same as reviewer/writer — read project CLAUDE.md, canonical docs, and relevant manuscript. Then:

1. Read the review report from `.worldsmith/reviews/` (latest date directory, or user-specified)
2. Parse all findings: severity (HIGH/MEDIUM/LOW), domain, location, quoted text
3. Read the full manuscript passages around each finding (not just the quoted excerpt)
4. Build a dependency map: which findings affect the same passage? Which fixes might conflict?

### Phase 2: Triage

Categorize each finding into one of three buckets:

**Auto-fixable** — Clear problem, clear fix direction. Most consistency issues (manuscript says X, canonical doc says Y — change manuscript to Y). Most craft issues (stock reaction → concrete physical detail). Most voice issues (character not matching documented patterns).

**Needs judgment** — The fix involves a creative decision the author should make. "The arc feels too smooth" — where should the setback go? "The dialogue is generic" — what should the character actually say? Use AskUserQuestion to present options with context.

**Defer** — Structural issues requiring major rework that goes beyond revision into new creation. "Chapter 7 has no tension" might require rewriting the entire chapter, which is a writer orchestrator job, not a rewriter job. Flag these for the user to plan separately.

Present the triage to the user: "N findings auto-fixable, M need your input, P deferred. Proceed?"

### Phase 3: Parallel Fix Dispatch

Group auto-fixable findings by specialist and passage proximity. Launch writer specialists in parallel for independent fix groups.

Each specialist receives XML-tagged context:

```xml
<finding>[the specific review finding — severity, domain, quoted text, problem description]</finding>
<fix_guidance>[what the reviewer specialist recommended as a fix direction]</fix_guidance>
<manuscript_passage>[the full passage that needs fixing, with surrounding context]</manuscript_passage>
<canonical_docs>[relevant canonical docs for ground truth]</canonical_docs>
<character_docs>[character voice patterns if relevant]</character_docs>
<style_conventions>[style guide for prose quality standards]</style_conventions>
<surrounding_context>[paragraphs/pages before and after for continuity]</surrounding_context>
```

**Conflict prevention:** If two findings affect the same passage, send both to the same specialist in one dispatch (not parallel). The specialist handles both fixes together to avoid contradictory edits.

### Phase 4: Verify

For each fix returned by a writer specialist, dispatch the relevant reviewer specialist to verify:

1. The original finding is resolved (the specific problem no longer exists)
2. No new issues were introduced by the fix
3. The fix is consistent with the surrounding context

Verification prompt:

```xml
<original_finding>[the review finding that was being fixed]</original_finding>
<original_passage>[the passage before the fix]</original_passage>
<fixed_passage>[the passage after the fix]</fixed_passage>
<canonical_docs>[relevant canonical docs]</canonical_docs>
<verification_question>Does this fix resolve the original finding without introducing new issues?</verification_question>
```

**Retry logic:** If verification fails:
- First retry: include the verification failure in the fix prompt as additional context
- Second retry: include both prior attempts and their failure reasons
- After 2 retries: flag for human review with full context (original finding, two fix attempts, verification failures)

**Parallel verification:** Independent fixes (different passages, different chapters) can be verified in parallel.

### Phase 5: Integration + Propagation

Same discipline as the writer orchestrator:

1. Apply verified fixes to manuscript files
2. Update canonical docs if fixes changed established facts
3. Trace propagation blast radius
4. Update character tracking if emotional flickers or arc positions changed
5. Update timeline authority if dates or sequences changed

### Phase 6: Report

Write a revision report to `.worldsmith/reviews/YYYY-MM-DD/revision.md`:

```markdown
# Revision Report

**Date**: YYYY-MM-DD
**Review source**: [path to the review report that triggered this revision]
**Findings processed**: N total (X auto-fixed, Y user-decided, Z deferred)

## Fixed (Verified)
### [Finding title]
- **Original finding**: [from review]
- **Before**: [original passage]
- **After**: [fixed passage]
- **Verified by**: [reviewer specialist name]
- **Verification result**: Resolved, no new issues

## Fixed (User-Decided)
### [Finding title]
- **Original finding**: [from review]
- **User decision**: [what the user chose]
- **Fix applied**: [description]

## Deferred
### [Finding title]
- **Reason**: [why this was deferred — needs major rework, structural change, etc.]
- **Suggestion**: [what the user could do — use writer orchestrator, manual revision, etc.]

## Retry Failures (Needs Human Review)
### [Finding title]
- **Original finding**: [from review]
- **Attempt 1**: [what was tried, why verification failed]
- **Attempt 2**: [what was tried, why verification failed]
- **Recommendation**: [suggested approach for manual fix]

## Propagation
- [List of canonical docs updated and why]

## Summary
- Findings resolved: X of N
- Verification pass rate: Y%
- New issues detected during verification: Z
```

## Design Decisions

1. **Reuses existing specialists** — No new specialist agents. The rewriter orchestrates the same 7 specialists differently (fix+verify loop instead of create or review).

2. **Fix-then-verify loop** — The key technique. Every fix is verified by a reviewer specialist before being accepted. This is the Reflexion pattern: generate → evaluate → retry if needed.

3. **Triage before fixing** — Not all review findings should be auto-fixed. Creative decisions need the author's input. Structural issues may need the writer orchestrator instead. Triage prevents wasted work.

4. **Conflict prevention** — Findings affecting the same passage go to the same specialist in one dispatch. This prevents contradictory edits from parallel specialists.

5. **Retry with context** — Failed verifications include prior attempts in the retry prompt, giving the specialist more information about what didn't work. Max 2 retries prevents infinite loops.

6. **Purple color** — Distinct from reviewer (red) and writer (blue). The three orchestrators form a complete cycle: write (blue) → review (red) → rewrite (purple) → review...

## Plugin Changes

- Create: `agents/rewriter.md`
- Modify: `CLAUDE.md` (add rewriter to orchestrator list)
- Modify: `commands/help.md` (add rewriter to agents table)
- Modify: `.claude-plugin/plugin.json` (bump version)
- Modify: `../.claude-plugin/marketplace.json` (bump version)
- Modify: `../CLAUDE.md` (bump version in table)
- Delete: `~/.claude/agents/fiction-writer.md` (replaced by worldsmith:writer + worldsmith:rewriter)
- Delete: `~/.claude/agents/fiction-editorial-critic.md` (replaced by worldsmith:reviewer)
