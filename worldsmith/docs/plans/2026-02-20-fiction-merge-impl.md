# Fiction Plugin Merge Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Merge the standalone fiction plugin into worldsmith as a second skill and gated hook.

**Architecture:** Copy the prose-craft skill as a new `skills/prose-craft/SKILL.md`. Move the cliche detection hook into `hooks/scripts/`, add `WORLDSMITH_PROJECT` gate, and register it in `hooks.json`. Update manifest and CLAUDE.md. Delete the fiction repo.

**Tech Stack:** Markdown, Bash, JSON

---

### Task 1: Add prose-craft skill

**Files:**
- Create: `skills/prose-craft/SKILL.md`

**Step 1: Create the skill file**

Copy `~/github/repos/fiction/skills/fiction/SKILL.md` to `skills/prose-craft/SKILL.md`. Change the YAML frontmatter `name` from `fiction` to `prose-craft`. Everything else stays identical.

The frontmatter should read:
```yaml
---
name: prose-craft
description: >
  Use when writing fiction, editing fiction prose, reviewing chapters, or
  drafting scenes. Covers prose craft, dialogue mechanics, scene structure,
  and common failure modes in AI-assisted fiction. Trigger phrases: "write
  fiction", "edit chapter", "prose review", "scene draft", "dialogue check",
  "fiction craft", "edit this scene", "review my prose".
---
```

**Step 2: Verify**

Confirm the file exists and frontmatter parses:
```bash
head -10 skills/prose-craft/SKILL.md
```

**Step 3: Commit**

```bash
git add skills/prose-craft/SKILL.md
git commit -m "Add prose-craft skill (merged from fiction plugin)"
```

---

### Task 2: Add cliche detection hook

**Files:**
- Create: `hooks/scripts/check-fiction-cliches.sh`

**Step 1: Create the hook script**

Copy `~/github/repos/fiction/hooks/check-fiction-cliches.sh` to `hooks/scripts/check-fiction-cliches.sh`. Add the `WORLDSMITH_PROJECT` gate immediately after `set -euo pipefail`, before any other logic:

```bash
# Gate: only run in worldsmith projects
if [ "${WORLDSMITH_PROJECT:-0}" != "1" ]; then
  exit 0
fi
```

This matches the pattern used by `propagation-reminder.sh` and `completion-check.sh`.

Make executable:
```bash
chmod +x hooks/scripts/check-fiction-cliches.sh
```

**Step 2: Verify**

```bash
head -15 hooks/scripts/check-fiction-cliches.sh
ls -la hooks/scripts/check-fiction-cliches.sh
```

Confirm the gate is present and the file is executable.

**Step 3: Commit**

```bash
git add hooks/scripts/check-fiction-cliches.sh
git commit -m "Add cliche detection hook gated on worldsmith projects"
```

---

### Task 3: Register cliche hook in hooks.json

**Files:**
- Modify: `hooks/hooks.json`

**Step 1: Add cliche hook to PostToolUse**

Edit `hooks/hooks.json`. The PostToolUse section should become:

```json
"PostToolUse": [
  {
    "matcher": "Write|Edit",
    "hooks": [
      {
        "type": "command",
        "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/propagation-reminder.sh",
        "timeout": 5
      },
      {
        "type": "command",
        "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/check-fiction-cliches.sh",
        "timeout": 10
      }
    ]
  }
]
```

Also update the top-level description:

```json
"description": "Worldsmith project detection, propagation reminders, cliche detection, and completion verification"
```

**Step 2: Verify JSON is valid**

```bash
python3 -c "import json; json.load(open('hooks/hooks.json')); print('valid')"
```

**Step 3: Commit**

```bash
git add hooks/hooks.json
git commit -m "Register cliche detection hook in hooks.json"
```

---

### Task 4: Update plugin manifest

**Files:**
- Modify: `.claude-plugin/plugin.json`

**Step 1: Update description**

Change the description to:

```
"description": "Documentation-first worldbuilding methodology and prose craft guardrails for fiction projects. The Silmarillion approach: docs ARE the world, story text derives from them."
```

Add `"prose-craft"` to keywords:

```json
"keywords": ["fiction", "worldbuilding", "editorial", "writing", "lore", "consistency", "prose-craft"]
```

**Step 2: Verify JSON is valid**

```bash
python3 -c "import json; json.load(open('.claude-plugin/plugin.json')); print('valid')"
```

**Step 3: Commit**

```bash
git add .claude-plugin/plugin.json
git commit -m "Update manifest to reflect prose-craft addition"
```

---

### Task 5: Update worldsmith CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Update the plugin structure diagram**

Add the new skill and hook to the file tree:

```
skills/prose-craft/SKILL.md                      # Prose craft rules (show-don't-tell, dialogue, scene structure)
```

And in the hooks/scripts section:

```
hooks/scripts/check-fiction-cliches.sh           # Cliche detection (stock reactions, dead metaphors, emotional labeling)
```

**Step 2: Add prose-craft skill documentation**

Add a new subsection under "File Format Conventions" or alongside the existing Skills section:

```markdown
### Skills
Two skills, independently triggered:
- **worldsmith-methodology** (`skills/worldsmith-methodology/SKILL.md`) — Editorial methodology: canonical hierarchy, propagation, doc roles, dual workflow. Triggers on doc ecosystem and worldbuilding keywords.
- **prose-craft** (`skills/prose-craft/SKILL.md`) — Sentence-level prose craft: show-don't-tell, dialogue mechanics, scene structure, AI-fiction failure modes. Triggers on fiction writing and editing keywords.
```

**Step 3: Document the cliche hook**

Update the Hooks section to mention the new hook:

```markdown
- **PostToolUse** (command, matcher: `Write|Edit`): Two hooks — propagation reminders for doc/manuscript edits, and cliche detection for stock body reactions, dead metaphors, and emotional labeling in fiction files (.tex, .md, .mdx, .txt)
```

**Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "Update CLAUDE.md to document prose-craft skill and cliche hook"
```

---

### Task 6: Delete fiction repo

**Step 1: Remove the fiction repo**

```bash
rm -rf ~/github/repos/fiction
```

**Step 2: Verify**

```bash
ls ~/github/repos/fiction 2>&1  # Should say "No such file or directory"
```
