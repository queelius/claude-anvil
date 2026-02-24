# `.worldsmith/` Detection Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace heuristic keyword detection with explicit `.worldsmith/` directory check across detection script, init-world command, help command, and CLAUDE.md.

**Architecture:** Rewrite the detection script gate (keep contextual output), add `.worldsmith/` creation to all three init-world modes, update help and CLAUDE.md to document the new convention.

**Tech Stack:** Bash, Markdown

---

### Task 1: Rewrite detection script

**Files:**
- Modify: `hooks/scripts/detect-worldsmith-project.sh`

**Step 1: Replace the heuristic gate (lines 10-34) with directory check**

The new script should be:

```bash
#!/bin/bash
# Detect if the current project is a worldsmith-managed worldbuilding project.
# A project is worldsmith-managed if it has a .worldsmith/ directory (created by
# /worldsmith:init-world). Sets WORLDSMITH_PROJECT=1 via $CLAUDE_ENV_FILE so
# other hooks can gate on it.

set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"

# Gate: .worldsmith/ directory is the canonical detection signal
if [ ! -d "$PROJECT_DIR/.worldsmith" ]; then
  if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
    echo "export WORLDSMITH_PROJECT=0" >> "$CLAUDE_ENV_FILE"
  fi
  exit 0
fi

# It's a worldsmith project — persist for other hooks
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo "export WORLDSMITH_PROJECT=1" >> "$CLAUDE_ENV_FILE"
fi

# Output context for Claude
echo "Worldsmith project detected."
echo ""

# Find docs directory
DOCS_DIR=""
if [ -d "$PROJECT_DIR/docs" ] && ls "$PROJECT_DIR/docs/"*.md &>/dev/null; then
  DOCS_DIR="$PROJECT_DIR/docs"
elif [ -d "$PROJECT_DIR/lore" ] && ls "$PROJECT_DIR/lore/"*.md &>/dev/null; then
  DOCS_DIR="$PROJECT_DIR/lore"
fi

if [ -n "$DOCS_DIR" ]; then
  echo "Documentation directory: $DOCS_DIR"
  echo "Documents found:"
  for f in "$DOCS_DIR"/*.md; do
    [ -f "$f" ] && echo "  - $(basename "$f") ($(wc -l < "$f") lines)"
  done

  # Check for subdirectories (feedback/, future/)
  for subdir in feedback future; do
    if [ -d "$DOCS_DIR/$subdir" ]; then
      count=$(find "$DOCS_DIR/$subdir" -name "*.md" 2>/dev/null | wc -l)
      echo "  - $subdir/ ($count files)"
    fi
  done
fi

# Check for related projects referenced in CLAUDE.md
if [ -f "$PROJECT_DIR/CLAUDE.md" ]; then
  related=$(grep -oP '~/[^\s)]+' "$PROJECT_DIR/CLAUDE.md" 2>/dev/null | head -5 || true)
  if [ -n "$related" ]; then
    echo ""
    echo "Related projects:"
    echo "$related" | while read -r proj; do
      expanded="${proj/#\~/$HOME}"
      if [ -d "$expanded" ]; then
        echo "  - $proj (found)"
      else
        echo "  - $proj (not found locally)"
      fi
    done
  fi
fi

# Check for manuscript files
for dir in chapters manuscript; do
  if [ -d "$PROJECT_DIR/$dir" ]; then
    count=$(find "$PROJECT_DIR/$dir" -name "*.md" -o -name "*.tex" -o -name "*.txt" 2>/dev/null | wc -l)
    if [ "$count" -gt 0 ]; then
      echo ""
      echo "Manuscript directory: $dir/ ($count files)"
      break
    fi
  fi
done

echo ""
echo "This is a worldsmith project. The worldsmith-methodology skill provides"
echo "documentation-first editorial rules. Read the project's CLAUDE.md for"
echo "document roles and propagation rules before editing docs or manuscript."
```

**Step 2: Verify syntax**

Run: `bash -n hooks/scripts/detect-worldsmith-project.sh && echo "syntax ok"`
Expected: `syntax ok`

**Step 3: Commit**

```bash
git add hooks/scripts/detect-worldsmith-project.sh
git commit -m "feat(worldsmith): replace heuristic detection with .worldsmith/ directory check"
```

---

### Task 2: Update init-world to create `.worldsmith/`

**Files:**
- Modify: `commands/init-world.md`

**Step 1: Add `.worldsmith/` creation to Verify Mode**

After line 25 (`1. Read the project's CLAUDE.md...`), insert as a new first step:

```
1. If `.worldsmith/` does not exist, create it (`mkdir -p .worldsmith`). This activates worldsmith hooks for this project.
```

Renumber subsequent steps (old 1 becomes 2, etc.).

**Step 2: Add `.worldsmith/` creation to Adopt Mode**

After line 41 (`6. Present the draft...`), add to step 6:

Change step 6 to:
```
6. Present the draft. Ask the user before writing or modifying anything. Create `.worldsmith/` (`mkdir -p .worldsmith`) when the user approves.
```

**Step 3: Add `.worldsmith/` creation to Scaffold Mode**

After line 54 (`2. Ask about related projects...`), change step 3 to:

```
3. Create `.worldsmith/` and `docs/` directories.
```

**Step 4: Commit**

```bash
git add commands/init-world.md
git commit -m "feat(worldsmith): create .worldsmith/ in all init-world modes"
```

---

### Task 3: Update help command

**Files:**
- Modify: `commands/help.md`

**Step 1: Update "Starting a new project" workflow**

Change lines 28-30 from:
```markdown
**Starting a new project:**
1. Navigate to your project directory
2. `/worldsmith:init-world` — scaffolds docs and CLAUDE.md
```
to:
```markdown
**Starting a new project:**
1. Navigate to your project directory
2. `/worldsmith:init-world` — creates `.worldsmith/`, scaffolds docs and CLAUDE.md
```

**Step 2: Update "Automatic Guards" section**

Change line 51 from:
```markdown
These fire without you invoking anything (in worldsmith-detected projects):
```
to:
```markdown
These fire automatically in any project with a `.worldsmith/` directory:
```

**Step 3: Commit**

```bash
git add commands/help.md
git commit -m "docs(worldsmith): update help command for .worldsmith/ detection"
```

---

### Task 4: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Update the detect script description in the file tree**

Change line 19 from:
```
hooks/scripts/detect-worldsmith-project.sh        # Ambient project detection
```
to:
```
hooks/scripts/detect-worldsmith-project.sh        # Project detection (checks for .worldsmith/ directory)
```

**Step 2: Update the Hooks section**

Change line 44 from:
```
- **SessionStart** (command): Runs `detect-worldsmith-project.sh` for ambient awareness
```
to:
```
- **SessionStart** (command): Runs `detect-worldsmith-project.sh` — checks for `.worldsmith/` directory, sets `WORLDSMITH_PROJECT` env var, outputs doc inventory
```

**Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(worldsmith): document .worldsmith/ detection in CLAUDE.md"
```
