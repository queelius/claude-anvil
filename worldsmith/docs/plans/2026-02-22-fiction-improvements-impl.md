# Fiction Improvements Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Expand cliche hook coverage, connect prose-craft skill to pattern audit, bump version, update docs, and add a help command.

**Architecture:** Five independent changes: new pattern categories in the bash hook, a new section in the prose-craft skill, a version bump in plugin.json, a CLAUDE.md doc update, and a new help command. One new file created (`commands/help.md`), rest are edits.

**Tech Stack:** Bash, Markdown, JSON

---

### Task 1: Add redundant adverbs and fancy dialogue tags to cliche hook

**Files:**
- Modify: `hooks/scripts/check-fiction-cliches.sh`

**Step 1: Add redundant adverbs category**

After the emotional labeling section (line 89, after the closing `PHRASES`), add:

```bash
# --- Redundant adverbs (adverb duplicates the verb — cut or choose a more precise verb) ---
while IFS= read -r phrase; do
  [ -z "$phrase" ] && continue
  if echo "$text" | grep -qi -F "$phrase"; then
    violations="${violations}- \"${phrase}\" (adverb duplicates the verb — cut it or choose a more precise verb)\n"
  fi
done <<'PHRASES'
whispered quietly
shouted loudly
sprinted quickly
crept slowly
muttered softly
screamed loudly
tiptoed quietly
rushed hurriedly
PHRASES
```

**Step 2: Add fancy dialogue tags category**

Immediately after the redundant adverbs block, add:

```bash
# --- Fancy dialogue tags (use "said" or a physical beat instead) ---
while IFS= read -r phrase; do
  [ -z "$phrase" ] && continue
  if echo "$text" | grep -qi -F "$phrase"; then
    violations="${violations}- \"${phrase}\" (use \"said\" or a physical beat instead)\n"
  fi
done <<'PHRASES'
exclaimed
opined
mused
interjected
proclaimed
declared
retorted
quipped
remarked
PHRASES
```

**Step 3: Update the script header comment**

Change line 2 from:
```
# Fiction cliche check: detect stock body reactions, dead metaphors, and
# emotional labeling in prose content.
```
to:
```
# Fiction cliche check: detect stock body reactions, dead metaphors,
# emotional labeling, redundant adverbs, and fancy dialogue tags in prose content.
```

**Step 4: Verify script syntax**

Run: `bash -n hooks/scripts/check-fiction-cliches.sh && echo "syntax ok"`
Expected: `syntax ok`

**Step 5: Commit**

```bash
git add hooks/scripts/check-fiction-cliches.sh
git commit -m "feat(worldsmith): expand cliche hook with redundant adverbs and fancy dialogue tags"
```

---

### Task 2: Add manuscript audit reference to prose-craft skill

**Files:**
- Modify: `skills/prose-craft/SKILL.md`

**Step 1: Add Manuscript-Wide Audit section**

Insert a new section before "## What This Skill Doesn't Cover" (before line 155):

```markdown
## Manuscript-Wide Audit

For pattern counts across an entire manuscript, use `/worldsmith:check editorial`.
It runs `count_patterns.py` to detect accumulating crutch words, filter words, weak
verbs, and adverb dialogue tags. Projects can customize the pattern list by placing
a `patterns.md` in `.worldsmith/` at project root.
```

**Step 2: Verify frontmatter still parses**

Run: `head -10 skills/prose-craft/SKILL.md`
Expected: YAML frontmatter with `name: prose-craft` intact.

**Step 3: Commit**

```bash
git add skills/prose-craft/SKILL.md
git commit -m "feat(worldsmith): reference pattern audit from prose-craft skill"
```

---

### Task 3: Bump version to 0.3.0

**Files:**
- Modify: `.claude-plugin/plugin.json`

**Step 1: Update version**

Change `"version": "0.2.0"` to `"version": "0.3.0"`.

**Step 2: Verify JSON is valid**

Run: `python3 -c "import json; d=json.load(open('.claude-plugin/plugin.json')); print(d['version'])"`
Expected: `0.3.0`

**Step 3: Commit**

```bash
git add .claude-plugin/plugin.json
git commit -m "chore(worldsmith): bump version to 0.3.0"
```

---

### Task 4: Update CLAUDE.md hook documentation

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Update the hook script entry in the file tree**

Change:
```
hooks/scripts/check-fiction-cliches.sh           # Cliche detection (stock reactions, dead metaphors, emotional labeling)
```
to:
```
hooks/scripts/check-fiction-cliches.sh           # Cliche detection (stock reactions, dead metaphors, emotional labeling, redundant adverbs, fancy dialogue tags)
```

**Step 2: Update the Hooks description**

The PostToolUse bullet should read:
```
- **PostToolUse** (command, matcher: `Write|Edit`): Two hooks — propagation reminders for doc/manuscript edits, and cliche detection for stock body reactions, dead metaphors, emotional labeling, redundant adverbs, and fancy dialogue tags in fiction files (.tex, .md, .mdx, .txt)
```

**Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(worldsmith): update CLAUDE.md for expanded cliche hook"
```

---

### Task 5: Add `/worldsmith:help` command

**Files:**
- Create: `commands/help.md`
- Modify: `CLAUDE.md` (add help to command list)

**Step 1: Create the help command**

Create `commands/help.md` with this content:

```markdown
---
description: Show worldsmith commands, skills, and typical workflows
allowed-tools: Read
---

# /worldsmith:help

Display a quick-reference guide to the worldsmith plugin.

## Commands

| Command | Purpose |
|---------|---------|
| `/worldsmith:init-world [name]` | Scaffold or adopt a worldbuilding doc ecosystem |
| `/worldsmith:change [description]` | Apply a change — canonical edits, exploratory ideas, or promotions |
| `/worldsmith:check [scope]` | Run diagnostics: `consistency`, `editorial`, `xref`, `status`, or `all` |
| `/worldsmith:help` | This guide |

## Skills (auto-triggered)

| Skill | Triggers when... |
|-------|-------------------|
| **worldsmith-methodology** | You work on worldbuilding docs, lore, or editorial structure |
| **prose-craft** | You write or edit fiction prose, scenes, or dialogue |

## Typical Workflows

**Starting a new project:**
1. Navigate to your project directory
2. `/worldsmith:init-world` — scaffolds docs and CLAUDE.md

**Writing a chapter:**
1. The prose-craft skill auto-triggers with craft guardrails
2. The cliche detection hook fires on each Write/Edit, catching stock phrases in real-time
3. Propagation reminders fire if you edit docs or manuscript

**Adding or changing lore:**
1. `/worldsmith:change add a new faction called the Ashwalkers`
2. Worldsmith updates canonical docs first, then propagates to manuscript

**Before a writing session:**
1. `/worldsmith:check status` — project health overview
2. `/worldsmith:check consistency` — catch contradictions
3. `/worldsmith:check editorial` — prose pattern audit with `count_patterns.py`

**After a big revision:**
1. `/worldsmith:check all` — full diagnostic sweep

## Automatic Guards

These fire without you invoking anything (in worldsmith-detected projects):

- **Cliche detection** — blocks stock body reactions, dead metaphors, emotional labeling, redundant adverbs, and fancy dialogue tags on Write/Edit to fiction files
- **Propagation reminders** — reminds you to check downstream docs when you edit a canonical source or manuscript
- **Completion check** — verifies propagation before session exit
```

**Step 2: Verify frontmatter**

Run: `head -5 commands/help.md`
Expected: YAML frontmatter with `description` and `allowed-tools`.

**Step 3: Update CLAUDE.md to list the new command**

In the Plugin Structure file tree, add `commands/help.md` to the commands line. Update any references to "3 slash commands" to "4 slash commands".

**Step 4: Commit**

```bash
git add commands/help.md CLAUDE.md
git commit -m "feat(worldsmith): add /worldsmith:help command for workflow discovery"
```
