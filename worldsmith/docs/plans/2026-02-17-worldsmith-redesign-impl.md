# Worldsmith Redesign Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rebuild worldsmith from 43 files to ~13, replacing encyclopedic skills with lean rules, consolidating commands, and adding project adoption + series awareness.

**Architecture:** Single skill (rules + 2 reference docs), 3 thin commands, 2 agents, 3 hook events, 1 utility script. No templates directory — init-world generates content dynamically. Role-based doc references, not hardcoded filenames.

**Design doc:** `docs/plans/2026-02-17-worldsmith-redesign-design.md` — consult for detailed rationale.

---

### Task 1: Remove old plugin components

**Files:**
- Delete: `skills/doc-ecosystem/` (entire directory)
- Delete: `skills/consistency-rules/` (entire directory)
- Delete: `skills/worldbuilding-methodology/` (entire directory)
- Delete: `skills/editorial-standards/` (entire directory)
- Delete: `commands/fix.md`
- Delete: `commands/explore.md`
- Delete: `commands/promote.md`
- Delete: `commands/check.md`
- Delete: `commands/xref.md`
- Delete: `commands/audit.md`
- Delete: `commands/status.md`
- Delete: `commands/init-world.md`
- Delete: `agents/lorekeeper.md`
- Delete: `agents/continuity-checker.md`
- Delete: `agents/editor.md`
- Delete: `hooks/hooks.json`
- Delete: `templates/` (entire directory)
- Delete: `scripts/detect-doc-type.sh`
- Delete: `scripts/check-propagation.sh`

**Step 1: Remove all old components**

```bash
rm -rf skills/doc-ecosystem skills/consistency-rules skills/worldbuilding-methodology skills/editorial-standards
rm -f commands/fix.md commands/explore.md commands/promote.md commands/check.md commands/xref.md commands/audit.md commands/status.md commands/init-world.md
rm -f agents/lorekeeper.md agents/continuity-checker.md agents/editor.md
rm -f hooks/hooks.json
rm -rf templates/
rm -f scripts/detect-doc-type.sh scripts/check-propagation.sh
```

**Step 2: Verify clean state**

```bash
# Should show only: .claude-plugin/, scripts/count-patterns.sh, CLAUDE.md, README.md, LICENSE, docs/, .serena/
ls -la
ls skills/ 2>/dev/null && echo "FAIL: skills/ should be empty" || echo "OK: skills/ clean"
ls commands/ 2>/dev/null && echo "FAIL: commands/ should be empty" || echo "OK: commands/ clean"
ls agents/ 2>/dev/null && echo "FAIL: agents/ should be empty" || echo "OK: agents/ clean"
```

**Step 3: Commit clean slate**

```bash
git add -A && git commit -m "Remove old plugin components for redesign

Removing 4 skills (11 reference docs), 8 commands, 3 agents,
7 templates, 2 scripts, and hooks in preparation for clean-sheet
redesign per docs/plans/2026-02-17-worldsmith-redesign-design.md

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 2: Create the skill — worldsmith-methodology

**Files:**
- Create: `skills/worldsmith-methodology/SKILL.md`
- Create: `skills/worldsmith-methodology/references/propagation-awareness.md`
- Create: `skills/worldsmith-methodology/references/doc-structure-guide.md`

**Step 1: Create directory structure**

```bash
mkdir -p skills/worldsmith-methodology/references
```

**Step 2: Write SKILL.md**

Target: ~2000 words. Imperative form. Third-person description with trigger phrases.

Frontmatter:
```yaml
---
name: worldsmith-methodology
description: This skill should be used when the user asks about "documentation structure", "doc relationships", "cross-references", "propagation", "canonical workflow", "exploratory workflow", "docs-first", "lore management", "worldbuilding docs", "consistency rules", "canonical hierarchy", "update docs", "change propagation", "editorial workflow", "Silmarillion approach", or is working in a project with a worldbuilding documentation ecosystem (docs/ or lore/ directory).
version: 0.2.0
---
```

Body sections (see design doc for detailed content):
1. Core Philosophy (~200 words) — docs as source of truth, bidirectional OK, living documents including CLAUDE.md
2. The Document Ecosystem (~400 words) — role-based (not filenames), roles list, canonical hierarchy, which roles have exploratory sections
3. Dual Workflow (~200 words) — canonical vs. exploratory vs. promotion, Claude determines mode from context
4. Propagation Awareness (~150 words) — think about what else is affected, consult project CLAUDE.md, points to references/propagation-awareness.md
5. Character Documentation Standards (~200 words) — voice patterns, emotional flickers, scene anchors, intellectual frameworks
6. Series & Shared Universe (~100 words) — check CLAUDE.md for related projects, consult their docs for shared facts
7. Consistency & Quality Awareness (~200 words) — types of issues (timeline, factual, character, spatial, prose, pacing, style, thematic), severity is context-dependent

End with Additional Resources section pointing to the two reference files.

**Step 3: Write references/propagation-awareness.md**

Guidance on how changes ripple. NOT a rigid matrix. Content:
- The concept: changes ripple through interconnected docs
- Examples by doc role (timeline changes → character ages, event refs, outline; system changes → character capabilities, manuscript scenes; etc.)
- Shallow vs. medium vs. deep changes with examples
- CLAUDE.md should be updated when project-level facts change
- For series projects, changes to shared world facts should be checked across projects

Target: ~1500 words.

**Step 4: Write references/doc-structure-guide.md**

What good worldbuilding docs look like, organized by role. Used by init-world when generating docs. Content:
- Each doc role: what it typically contains, what makes it useful vs. encyclopedia-like
- Canonical vs. exploratory section patterns
- What a good worldbuilding CLAUDE.md should contain (doc roles table, consistency rules, world structure, character conventions, series references)
- Examples drawn from real projects (the-policy's character voice docs, echoes-of-the-sublime's bandwidth system specs) as illustration of the level of specificity that's useful

Target: ~2000 words.

**Step 5: Validate skill**

```bash
# Frontmatter check
head -5 skills/worldsmith-methodology/SKILL.md
# Should show --- / name: worldsmith-methodology / description: ...

# Reference files exist
ls skills/worldsmith-methodology/references/
# Should show: propagation-awareness.md  doc-structure-guide.md

# Word count check (SKILL.md body should be ~2000 words)
wc -w skills/worldsmith-methodology/SKILL.md
```

**Step 6: Commit**

```bash
git add skills/worldsmith-methodology/
git commit -m "Add worldsmith-methodology skill with reference docs

Single lean skill replacing 4 encyclopedic skills. Provides core
rules (canonical hierarchy, dual workflow, propagation awareness,
character documentation standards) without teaching Claude things
it already knows.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 3: Create the commands

**Files:**
- Create: `commands/init-world.md`
- Create: `commands/change.md`
- Create: `commands/check.md`

**Step 1: Write commands/init-world.md**

Frontmatter:
```yaml
---
description: Scaffold or adopt a worldbuilding documentation ecosystem
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, AskUserQuestion
argument-hint: [project-name]
---
```

Body: Adaptive scaffolding. Three modes based on project state:
1. CLAUDE.md with doc structure exists → confirm, report gaps, don't overwrite
2. Docs exist but no CLAUDE.md → read docs, understand roles, generate CLAUDE.md content, ask before adding
3. Nothing exists → ask about project (name, genre, format, premise, series), create docs, generate CLAUDE.md

References `${CLAUDE_PLUGIN_ROOT}/skills/worldsmith-methodology/references/doc-structure-guide.md` for guidance on what to generate.

Asks about related projects/series. For new projects, offers sensible doc defaults based on genre/format but lets user choose. Creates lightweight starter docs, not comprehensive schemas.

Target: ~80 lines.

**Step 2: Write commands/change.md**

Frontmatter:
```yaml
---
description: Apply a change to the worldbuilding project — edits, new ideas, or promotions
allowed-tools: Read, Write, Edit, Grep, Glob, AskUserQuestion
argument-hint: [description of change or idea]
---
```

Body: Unified change workflow. Claude determines mode from context. Three modes described as guidance, not rigid scripts:
- Canonical change (established facts): update source doc, reconcile affected docs and manuscript
- Exploratory idea (new, provisional): write to exploratory sections, mark provisional
- Promotion (exploratory → canonical): resolve conflicts, move to canonical, then reconcile

Rules: read project CLAUDE.md for doc structure. Think about what else might be affected. CLAUDE.md itself can be updated. If mode unclear, ask. Bidirectional updates between docs and manuscript are OK.

Target: ~50 lines.

**Step 3: Write commands/check.md**

Frontmatter:
```yaml
---
description: Run diagnostics — consistency, editorial, cross-references, or project status
allowed-tools: Read, Grep, Glob, AskUserQuestion
argument-hint: [scope: all|consistency|editorial|xref|status]
---
```

Body: Unified diagnostics. READ-ONLY. Modes:
- consistency: timeline, facts, characters, spatial vs. canonical docs
- editorial: prose patterns, pacing, style drift, thematic drift (can use `${CLAUDE_PLUGIN_ROOT}/scripts/count-patterns.sh`)
- xref: cross-reference health
- status: project health overview
- all: everything

Report format: group by severity, include locations and recommended fixes. For series projects, check cross-project consistency if CLAUDE.md references related projects.

Target: ~70 lines.

**Step 4: Validate commands**

```bash
# Frontmatter checks
for f in commands/*.md; do echo "=== $f ===" && head -5 "$f" && echo; done
# Each should have description and allowed-tools

# Should be exactly 3 commands
ls commands/*.md | wc -l
# Expected: 3
```

**Step 5: Commit**

```bash
git add commands/
git commit -m "Add consolidated commands: init-world, change, check

Three commands replacing eight. init-world adapts to project state
(new/existing/adopted). change unifies fix+explore+promote. check
unifies consistency+editorial+xref+status diagnostics.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 4: Create the agents

**Files:**
- Create: `agents/lorekeeper.md`
- Create: `agents/critic.md`

**Step 1: Write agents/lorekeeper.md**

Frontmatter:
```yaml
---
name: lorekeeper
description: Use this agent when the user wants to develop worldbuilding content, expand lore, create mythology, design systems, build history, or add depth to their fictional world. Examples:

  <example>
  Context: User wants to develop the history of a kingdom.
  user: "I need to flesh out the history of the Northern Kingdom."
  assistant: "I'll use the lorekeeper agent to develop the Northern Kingdom's history, working with your existing lore docs."
  <commentary>
  Lore development — the lorekeeper reads existing docs and builds coherent new content.
  </commentary>
  </example>

  <example>
  Context: User wants to design a magic system.
  user: "I want a magic system based on sound and resonance."
  assistant: "I'll launch the lorekeeper agent to design a resonance-based magic system with consequences for your world."
  <commentary>
  System design with consequence derivation — the lorekeeper works through implications.
  </commentary>
  </example>

  <example>
  Context: User wants to develop character voice patterns.
  user: "Help me define how each character speaks distinctively."
  assistant: "I'll use the lorekeeper agent to develop character voice documentation — speech patterns, tics, and emotional markers."
  <commentary>
  Character documentation — the lorekeeper creates behaviorally specific character docs.
  </commentary>
  </example>

model: inherit
color: magenta
tools: ["Read", "Write", "Edit", "Grep", "Glob", "AskUserQuestion"]
---
```

System prompt (~800 words): Creative worldbuilding specialist. See design doc section "lorekeeper agent" for full content. Key elements:
- Core principle: docs are the world, write to docs first
- Before writing: read CLAUDE.md, read canonical docs, identify doc role, check conflicts
- Workflow: canonical vs. exploratory based on context
- Quality standards: narrative prose, systems with consequences, historical layers, internal diversity
- Character documentation standards: voice patterns, emotional flickers, scene anchors
- Updates CLAUDE.md when project-level facts change
- Summarizes what was written and which docs were updated

**Step 2: Write agents/critic.md**

Frontmatter:
```yaml
---
name: critic
description: Use this agent when the user wants diagnostic analysis of their worldbuilding project — consistency checks, editorial audits, or cross-reference verification. This agent is strictly READ-ONLY. Examples:

  <example>
  Context: User wants to verify timeline consistency.
  user: "Check for timeline contradictions in my novel."
  assistant: "I'll use the critic agent to audit timeline consistency against your canonical docs."
  <commentary>
  Consistency diagnostic — the critic checks docs against manuscript for contradictions.
  </commentary>
  </example>

  <example>
  Context: User wants a prose quality audit.
  user: "Do a repetition audit on chapters 3-5."
  assistant: "I'll launch the critic agent to analyze prose patterns and flag issues in those chapters."
  <commentary>
  Editorial diagnostic — the critic finds prose patterns, pacing issues, and style drift.
  </commentary>
  </example>

  <example>
  Context: User wants a comprehensive review before submission.
  user: "I'm almost done — do a full review."
  assistant: "I'll use the critic agent for a comprehensive consistency and editorial audit."
  <commentary>
  Combined diagnostic — the critic handles both consistency and editorial analysis.
  </commentary>
  </example>

model: inherit
color: yellow
tools: ["Read", "Grep", "Glob"]
---
```

System prompt (~900 words): Diagnostic specialist, strictly READ-ONLY. See design doc section "critic agent" for full content. Key elements:
- Two diagnostic modes: consistency (timeline, facts, characters, spatial) and editorial (patterns, pacing, style, voice)
- Reads CLAUDE.md for doc structure and canonical hierarchy
- Canonical hierarchy for conflict resolution
- Can flag CLAUDE.md staleness
- For series projects, checks cross-project consistency
- Report format: severity-grouped, with locations, sources, recommended fixes
- Constraints: never modify files, check intentional repetitions before flagging, distinguish unreliable narrator from errors

**Step 3: Validate agents**

```bash
# Frontmatter checks
for f in agents/*.md; do echo "=== $f ===" && head -10 "$f" && echo; done
# Each should have name, description with examples, model, color, tools

# Should be exactly 2 agents
ls agents/*.md | wc -l
# Expected: 2
```

**Step 4: Commit**

```bash
git add agents/
git commit -m "Add lorekeeper and critic agents

Lorekeeper: creative worldbuilding (read-write, explicit tool list).
Critic: merged continuity-checker + editor (read-only diagnostics).
Both use role-based doc references via project CLAUDE.md.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 5: Create the hooks

**Files:**
- Create: `hooks/hooks.json`
- Create: `hooks/scripts/detect-worldsmith-project.sh`

**Step 1: Create directory structure**

```bash
mkdir -p hooks/scripts
```

**Step 2: Write hooks/hooks.json**

```json
{
  "description": "Worldsmith project detection, propagation reminders, and completion verification",
  "hooks": {
    "SessionStart": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/detect-worldsmith-project.sh",
            "timeout": 10
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "A file was just edited. If the file is part of a worldbuilding documentation ecosystem (a docs/ or lore/ directory containing files like lore.md, worldbuilding.md, characters.md, timeline.md, themes.md, style-guide.md, outline.md, or future-ideas.md) OR part of the manuscript (chapters/, manuscript/, or similar), briefly note which other files may need checking for consistency based on the project's CLAUDE.md cross-reference rules. If the edit is unrelated to worldbuilding docs or manuscript, say nothing.",
            "timeout": 10
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Before stopping, check: if this session involved editing worldbuilding docs or manuscript text, verify that consistency was maintained. (1) Were relevant docs and manuscript kept in sync? (2) Were cross-references checked? (3) Was the outline updated if applicable? (4) Should the project CLAUDE.md be updated to reflect any changes? If something was clearly missed, return 'block' with a brief reminder. If everything looks addressed or no worldbuilding edits occurred, return 'approve'.",
            "timeout": 15
          }
        ]
      }
    ]
  }
}
```

**Step 3: Write hooks/scripts/detect-worldsmith-project.sh**

Full script content (see design doc "SessionStart" section). Key behaviors:
- Check for docs/ or lore/ directory with markdown files
- List found documents with line counts
- Check for subdirectories (feedback/, future/)
- Check CLAUDE.md for worldsmith configuration
- Check for related projects referenced in CLAUDE.md (expand ~ paths, verify existence)
- Detect manuscript files
- Output contextual message for Claude

Make executable: `chmod +x hooks/scripts/detect-worldsmith-project.sh`

**Step 4: Validate hooks**

```bash
# JSON syntax check
python3 -c "import json; json.load(open('hooks/hooks.json'))" && echo "OK: valid JSON" || echo "FAIL: invalid JSON"

# Script is executable
test -x hooks/scripts/detect-worldsmith-project.sh && echo "OK: executable" || echo "FAIL: not executable"

# Test script in a non-worldsmith directory (should exit silently)
CLAUDE_PROJECT_DIR=/tmp bash hooks/scripts/detect-worldsmith-project.sh
# Expected: no output (not a worldsmith project)
```

**Step 5: Commit**

```bash
git add hooks/
git commit -m "Add hooks: SessionStart detection, propagation, completion

SessionStart: detect-worldsmith-project.sh provides ambient awareness.
PostToolUse: propagation reminder on Write|Edit of docs/manuscript.
Stop: completion verification before session end.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 6: Update scripts

**Files:**
- Modify: `scripts/count-patterns.sh` (review and keep, possibly update)

**Step 1: Review count-patterns.sh**

Read the existing script. It's already functional — counts crutch words, filter words, weak verbs, dialogue tags. Verify it still works and the patterns are comprehensive.

Consider adding: vague nouns (something, everything, anything), sentence starter repetition. But only if genuinely useful — YAGNI.

**Step 2: Verify script works**

```bash
# Script is executable
test -x scripts/count-patterns.sh && echo "OK" || chmod +x scripts/count-patterns.sh

# Syntax check
bash -n scripts/count-patterns.sh && echo "OK: valid bash" || echo "FAIL"
```

**Step 3: Commit (only if changed)**

```bash
# Only if modifications were made
git add scripts/count-patterns.sh
git commit -m "Update count-patterns.sh for redesign

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 7: Update plugin metadata

**Files:**
- Modify: `.claude-plugin/plugin.json` (version bump)
- Modify: `CLAUDE.md` (reflect new structure)
- Modify: `README.md` (reflect new structure)

**Step 1: Bump version in plugin.json**

Change version from `"0.1.0"` to `"0.2.0"`.

**Step 2: Rewrite CLAUDE.md**

Reflect the new plugin structure. Key sections:
- What this is (plugin, not software project)
- Plugin structure (new layout: 1 skill, 3 commands, 2 agents, hooks, scripts)
- File format conventions (updated for new components)
- Core concept: role-based doc ecosystem (not hardcoded filenames)
- Philosophy: awareness over formalism, CLAUDE.md as living document
- Validation commands (updated for new file set)

**Step 3: Rewrite README.md**

Update to reflect:
- New command list (3 instead of 8)
- New agent list (2 instead of 3)
- New skill description (1 instead of 4)
- Updated hook descriptions (SessionStart added)
- No templates section
- Updated getting started guide
- Philosophy section updated (awareness over formalism)
- Workflow examples updated for new command names

**Step 4: Validate**

```bash
# plugin.json version
grep '"version"' .claude-plugin/plugin.json
# Expected: "version": "0.2.0"

# CLAUDE.md exists and references new structure
grep -c "worldsmith-methodology" CLAUDE.md
# Expected: >= 1

# README.md references new commands
grep -c "init-world\|change\|check" README.md
# Expected: >= 3
```

**Step 5: Commit**

```bash
git add .claude-plugin/plugin.json CLAUDE.md README.md
git commit -m "Update plugin metadata, CLAUDE.md, and README for v0.2.0

Reflects redesigned structure: 1 skill, 3 commands, 2 agents,
3 hook events, 1 utility script. Role-based doc references,
awareness over formalism.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 8: Final validation and cleanup

**Step 1: Full structure validation**

```bash
echo "=== Plugin Structure ==="
find . -not -path './.git/*' -not -path './.serena/*' -not -path './docs/*' -type f | sort

echo ""
echo "=== Skill frontmatter ==="
head -5 skills/worldsmith-methodology/SKILL.md

echo ""
echo "=== Command frontmatter ==="
for f in commands/*.md; do echo "--- $f ---" && head -5 "$f"; done

echo ""
echo "=== Agent frontmatter ==="
for f in agents/*.md; do echo "--- $f ---" && head -4 "$f"; done

echo ""
echo "=== Hooks JSON valid ==="
python3 -c "import json; json.load(open('hooks/hooks.json')); print('OK')"

echo ""
echo "=== Scripts executable ==="
for f in scripts/*.sh hooks/scripts/*.sh; do test -x "$f" && echo "OK: $f" || echo "FAIL: $f"; done

echo ""
echo "=== File count ==="
find . -not -path './.git/*' -not -path './.serena/*' -not -path './docs/*' -type f | wc -l
# Expected: ~13 (plugin.json, SKILL.md, 2 refs, 3 commands, 2 agents, hooks.json, detect script, count-patterns.sh, CLAUDE.md, README.md, LICENSE)
```

**Step 2: Check for broken ${CLAUDE_PLUGIN_ROOT} references**

```bash
grep -roh '\${CLAUDE_PLUGIN_ROOT}/[^`"} ]*' skills/ commands/ agents/ hooks/ | sort -u
# Verify each referenced path exists relative to plugin root
```

**Step 3: Remove .serena cache if stale**

```bash
rm -rf .serena/cache
```

**Step 4: Clean up docs/plans (optional)**

The design doc and this implementation plan live in docs/plans/. These are development artifacts. They can stay for reference or be removed before release.

**Step 5: Final commit if any cleanup was needed**

```bash
git add -A && git status
# Only commit if there are changes
git diff --cached --quiet || git commit -m "Final cleanup for v0.2.0 redesign

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```
