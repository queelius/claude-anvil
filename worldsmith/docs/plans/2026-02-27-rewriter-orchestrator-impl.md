# Rewriter Orchestrator Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a rewriter orchestrator to worldsmith that reads review findings, dispatches writer specialists to fix them, then dispatches reviewer specialists to verify the fixes — a fix-then-verify feedback loop.

**Architecture:** Single new orchestrator agent (`agents/rewriter.md`) that reuses all 7 existing specialists. No new specialist agents. Plus plugin file updates for docs, help, and version bump.

**Tech Stack:** Markdown with YAML frontmatter

---

### Task 1: Create rewriter orchestrator agent

**Files:**
- Create: `agents/rewriter.md`

**Step 1: Create the agent file**

Create `agents/rewriter.md` with YAML frontmatter and system prompt body.

**Frontmatter:**

```yaml
---
name: rewriter
description: >-
  Multi-agent fiction revision orchestrator. Acts as editorial implementer: reads
  review findings from .worldsmith/reviews/, dispatches writer specialists to fix
  issues, then dispatches reviewer specialists to verify each fix resolved the
  original finding. Bridges the reviewer (diagnoses) and writer (creates) with a
  fix-then-verify feedback loop.

  <example>
  Context: User has a review report and wants the issues fixed.
  user: "Fix the issues from the review"
  assistant: "I'll launch the rewriter agent to implement fixes from the review findings, with verification after each fix."
  </example>
  <example>
  Context: User wants to revise specific chapters based on editorial feedback.
  user: "Revise chapters 3-5 based on the editorial report"
  assistant: "I'll launch the rewriter agent to fix the findings for chapters 3 through 5, verifying each fix with the relevant reviewer specialist."
  </example>
  <example>
  Context: User ran a review and wants targeted fixes.
  user: "Fix just the HIGH consistency issues from the last review"
  assistant: "I'll launch the rewriter agent to fix the HIGH consistency findings, with verification by the consistency-auditor."
  </example>
  <example>
  Context: User wants the full review-then-fix cycle.
  user: "Review my manuscript and fix what you find"
  assistant: "I'll launch the reviewer first for a full editorial review, then the rewriter to implement the fixes with verification."
  </example>
tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Task
  - AskUserQuestion
model: opus
color: purple
---
```

**System prompt structure (from design doc `docs/plans/2026-02-27-rewriter-orchestrator-design.md`):**

Opening: "You orchestrate multi-agent fiction manuscript revision. You are the editorial implementer — you read review findings, dispatch specialists to fix issues, verify each fix resolved the original finding, and deliver the revised manuscript with a detailed revision report."

**Available Agents section** — Two tables:

For fixing (writer specialists):
| Agent | Used when... |
|-------|-------------|
| `worldsmith:scene-writer` | Prose craft fixes, dialogue rewrites, show-don't-tell conversions, scene restructuring |
| `worldsmith:lore-writer` | Canonical doc corrections, factual fixes, timeline repairs, terminology standardization |
| `worldsmith:character-developer` | Voice pattern fixes, arc corrections, emotional flicker updates, relationship consistency |

For verifying (reviewer specialists):
| Agent | Verifies... |
|-------|------------|
| `worldsmith:consistency-auditor` | Factual/timeline/spatial fixes resolved the contradiction |
| `worldsmith:craft-auditor` | Prose craft fixes actually improved the passage |
| `worldsmith:voice-auditor` | Voice/dialogue fixes match character specs |
| `worldsmith:structure-auditor` | Structure/pacing fixes improved narrative flow |

**Finding-to-Specialist Mapping table** — from design doc, maps each finding domain to fix specialist + verify specialist.

**6-Phase Workflow** — from design doc:

Phase 1: Comprehension — Read project CLAUDE.md + canonical docs + review report from `.worldsmith/reviews/`. Parse findings by severity and domain. Read manuscript passages around each finding. Build dependency map.

Phase 2: Triage — Categorize as auto-fixable / needs-judgment / defer. Present triage to user before proceeding. Use AskUserQuestion for needs-judgment findings.

Phase 3: Parallel Fix Dispatch — Group findings by specialist and passage proximity. Launch writer specialists in parallel for independent fix groups. XML context tags:
```xml
<finding>[the specific review finding]</finding>
<fix_guidance>[what the reviewer specialist recommended]</fix_guidance>
<manuscript_passage>[full passage with surrounding context]</manuscript_passage>
<canonical_docs>[relevant canonical docs]</canonical_docs>
<character_docs>[voice patterns if relevant]</character_docs>
<style_conventions>[style guide]</style_conventions>
<surrounding_context>[before/after for continuity]</surrounding_context>
```
Conflict prevention: findings affecting same passage go to same specialist in one dispatch.

Phase 4: Verify — For each fix, dispatch relevant reviewer specialist with:
```xml
<original_finding>[the review finding]</original_finding>
<original_passage>[before fix]</original_passage>
<fixed_passage>[after fix]</fixed_passage>
<canonical_docs>[relevant docs]</canonical_docs>
<verification_question>Does this fix resolve the original finding without introducing new issues?</verification_question>
```
Retry logic: first retry includes failure context, second retry includes both attempts, after 2 retries flag for human review. Independent fixes verified in parallel.

Phase 5: Integration + Propagation — Apply verified fixes, update canonical docs, trace blast radius, same discipline as writer orchestrator.

Phase 6: Report — Write revision report to `.worldsmith/reviews/YYYY-MM-DD/revision.md` with sections: Fixed (Verified), Fixed (User-Decided), Deferred, Retry Failures, Propagation, Summary. Include before/after for each fix and verification pass rate.

**Ground Rules:**
- **Preserve voice**: Fixes should sound like the author, not the model. Match existing prose style.
- **Minimal intervention**: Fix the finding, don't rewrite the whole paragraph. Change as little as possible to resolve the issue.
- **Verify everything**: No fix goes into the manuscript without reviewer specialist verification.
- **Triage honestly**: If a finding needs creative judgment, ask. Don't guess.
- **Show your work**: The revision report must show before/after for every fix.
- **Conflict awareness**: Two fixes to the same passage must be coordinated, not applied blindly in parallel.

**Step 2: Verify frontmatter**

Run: `head -30 agents/rewriter.md`

Confirm: YAML has name, description with 4 `<example>` blocks, tools list (8 tools including Task), model: opus, color: purple.

**Step 3: Commit**

```bash
git add agents/rewriter.md
git commit -m "feat(worldsmith): add rewriter orchestrator agent"
```

---

### Task 2: Update plugin files

**Files:**
- Modify: `CLAUDE.md`
- Modify: `commands/help.md`
- Modify: `.claude-plugin/plugin.json`
- Modify: `../.claude-plugin/marketplace.json`
- Modify: `../CLAUDE.md`

**Step 1: Update CLAUDE.md**

In the Plugin Structure file tree, change:
```
agents/reviewer.md                                # Review orchestrator (spawns specialist auditors)
agents/writer.md                                  # Writer orchestrator (spawns specialist writers)
```
to:
```
agents/reviewer.md                                # Review orchestrator (spawns specialist auditors)
agents/writer.md                                  # Writer orchestrator (spawns specialist writers)
agents/rewriter.md                                # Rewriter orchestrator (fix-then-verify loop)
```

In the Agents section under File Format Conventions, add to the Orchestrators list:
```markdown
- **rewriter** — Multi-agent revision. Reads review findings, dispatches writer specialists to fix, then reviewer specialists to verify. Fix-then-verify feedback loop.
```

Change "Two orchestrators and seven specialists" to "Three orchestrators and seven specialists".

**Step 2: Update commands/help.md**

In the Agents table, add after the writer row:
```markdown
| **rewriter** | Fix-then-verify revision (reads review, fixes issues, verifies fixes) | `/worldsmith:review` output or direct |
```

**Step 3: Update plugin.json**

Change version from `"0.5.1"` to `"0.6.0"` (new orchestrator is a feature, not a patch).

**Step 4: Update marketplace.json**

Change worldsmith version from `"0.5.1"` to `"0.6.0"`.

**Step 5: Update root CLAUDE.md**

Change worldsmith version from `0.5.1` to `0.6.0`.

**Step 6: Verify**

```bash
# All agent files have valid frontmatter
for f in agents/*.md; do echo "=== $f ===" && head -5 "$f" && echo; done

# Plugin JSON version
python3 -c "import json; d=json.load(open('.claude-plugin/plugin.json')); print(d['version'])"

# Marketplace version
python3 -c "import json; d=json.load(open('../.claude-plugin/marketplace.json')); [print(p['version']) for p in d['plugins'] if p['name']=='worldsmith']"
```

Expected: 10 agent files (9 existing + rewriter), version 0.6.0 in both JSON files.

**Step 7: Commit**

```bash
git add CLAUDE.md commands/help.md .claude-plugin/plugin.json ../.claude-plugin/marketplace.json ../CLAUDE.md
git commit -m "feat(worldsmith): update plugin docs and bump to 0.6.0 for rewriter orchestrator"
```

---

### Task 3: Delete standalone fiction agents

**Files:**
- Delete: `~/.claude/agents/fiction-writer.md`
- Delete: `~/.claude/agents/fiction-editorial-critic.md`

**Step 1: Delete the files**

```bash
rm ~/.claude/agents/fiction-writer.md ~/.claude/agents/fiction-editorial-critic.md
```

**Step 2: Verify**

```bash
ls ~/.claude/agents/
```

Confirm neither fiction-writer.md nor fiction-editorial-critic.md exists.

No commit needed — these are user-level config files, not tracked in the repo.
