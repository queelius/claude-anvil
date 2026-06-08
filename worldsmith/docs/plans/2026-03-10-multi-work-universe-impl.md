# Multi-Work Universe Support Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enable worldsmith to manage multiple works (novel + short stories, etc.) sharing canonical lore within a single repo.

**Architecture:** New optional `.worldsmith/project.yaml` config file declares the universe and its works. A Python helper script parses it for bash hooks. All commands, orchestrators, and the methodology skill gain multi-work awareness while maintaining full backward compatibility when `project.yaml` is absent.

**Tech Stack:** Bash hooks, Python (PyYAML), Markdown agent/command/skill files.

**Design doc:** `docs/plans/2026-03-10-multi-work-universe-design.md`

---

## Chunk 1: Foundation (Detection + Propagation)

### Task 1: Create project.yaml parser script

The detection hook needs to parse `.worldsmith/project.yaml`. Per project conventions, no regex parsing of structured data — use Python with PyYAML.

**Files:**
- Create: `hooks/scripts/parse-project-yaml.py`

- [ ] **Step 1: Create the parser script**

```python
#!/usr/bin/env python3
"""Parse .worldsmith/project.yaml and output structured data for shell consumption.

Usage: parse-project-yaml.py <path-to-project.yaml> [--env | --human]

--env:   Output shell-eval-able variable assignments (for hooks)
--human: Output human-readable summary (for SessionStart output)

If project.yaml does not exist or is invalid, exits with code 1.
"""
import sys
import os
import yaml


def parse(path):
    with open(path) as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError("project.yaml must be a YAML mapping")
    return data


def output_env(data):
    """Print shell variable assignments."""
    universe = data.get("universe", "")
    lore = data.get("lore", "")
    works = data.get("works", [])
    print(f'WORLDSMITH_UNIVERSE="{universe}"')
    print(f'WORLDSMITH_LORE_DIR="{lore}"')
    print(f"WORLDSMITH_WORK_COUNT={len(works)}")
    # Colon-separated work names for other hooks
    names = ":".join(w.get("name", "") for w in works)
    print(f'WORLDSMITH_WORKS="{names}"')
    # Per-work variables: WORLDSMITH_WORK_0_NAME, _TYPE, _MANUSCRIPT, _FILETYPES
    for i, w in enumerate(works):
        name = w.get("name", "")
        wtype = w.get("type", "")
        manuscript = w.get("manuscript", "")
        master = w.get("master", "")
        file_types = ",".join(w.get("file_types", ["md", "tex", "txt"]))
        print(f'WORLDSMITH_WORK_{i}_NAME="{name}"')
        print(f'WORLDSMITH_WORK_{i}_TYPE="{wtype}"')
        print(f'WORLDSMITH_WORK_{i}_MANUSCRIPT="{manuscript}"')
        print(f'WORLDSMITH_WORK_{i}_MASTER="{master}"')
        print(f'WORLDSMITH_WORK_{i}_FILETYPES="{file_types}"')


def output_human(data, project_dir):
    """Print human-readable summary for Claude."""
    universe = data.get("universe", "unknown")
    lore = data.get("lore", "")
    works = data.get("works", [])
    print(f"Universe: {universe}")
    if lore:
        print(f"Lore directory: {lore}")
    print()
    print("Works:")
    for w in works:
        name = w.get("name", "unnamed")
        wtype = w.get("type", "")
        manuscript = w.get("manuscript", "")
        # Count manuscript files
        ms_path = os.path.join(project_dir, manuscript)
        file_types = w.get("file_types", ["md", "tex", "txt"])
        count = 0
        if os.path.isdir(ms_path):
            for ext in file_types:
                for root, _, files in os.walk(ms_path):
                    count += sum(1 for f in files if f.endswith(f".{ext}"))
        type_label = f" [{wtype}]" if wtype else ""
        print(f"  - {name}{type_label} — {manuscript} ({count} files)")


def main():
    if len(sys.argv) < 2:
        print("Usage: parse-project-yaml.py <path> [--env | --human]", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) >= 3 else "--human"

    if not os.path.isfile(path):
        sys.exit(1)

    try:
        data = parse(path)
    except Exception as e:
        print(f"Error parsing {path}: {e}", file=sys.stderr)
        sys.exit(1)

    project_dir = os.path.dirname(os.path.dirname(path))  # .worldsmith/ -> project root

    if mode == "--env":
        output_env(data)
    else:
        output_human(data, project_dir)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Make it executable**

```bash
chmod +x hooks/scripts/parse-project-yaml.py
```

- [ ] **Step 3: Verify it runs**

```bash
# Create a temporary test project.yaml
mkdir -p /tmp/test-worldsmith/.worldsmith
cat > /tmp/test-worldsmith/.worldsmith/project.yaml << 'YAML'
universe: test-verse
lore: lore/
works:
  - name: Main Novel
    type: novel
    manuscript: chapters/
    file_types: [tex]
  - name: Side Story
    type: short-story
    manuscript: stories/side/
YAML

# Test --env mode
python3 hooks/scripts/parse-project-yaml.py /tmp/test-worldsmith/.worldsmith/project.yaml --env
# Expected: WORLDSMITH_UNIVERSE="test-verse", WORLDSMITH_WORK_COUNT=2, etc.

# Test --human mode
python3 hooks/scripts/parse-project-yaml.py /tmp/test-worldsmith/.worldsmith/project.yaml --human
# Expected: "Universe: test-verse\nWorks:\n  - Main Novel [novel] — chapters/ (0 files)\n  ..."

# Cleanup
rm -rf /tmp/test-worldsmith
```

- [ ] **Step 4: Commit**

```bash
git add hooks/scripts/parse-project-yaml.py
git commit -m "feat(worldsmith): add project.yaml parser for multi-work universe support"
```

---

### Task 2: Update detection script for multi-work awareness

The detection script currently infers a single manuscript directory. With project.yaml, it should report all works.

**Files:**
- Modify: `hooks/scripts/detect-worldsmith-project.sh`

- [ ] **Step 1: Add project.yaml branch to detection script**

After the existing `.worldsmith/` detection and before the current docs/lore inference, add a project.yaml parsing branch. If `.worldsmith/project.yaml` exists, use the Python parser for structured output. If not, fall through to existing inference (zero behavior change for single-work projects).

The key changes:
1. After `WORLDSMITH_PROJECT=1`, check for `.worldsmith/project.yaml`
2. If found: run `parse-project-yaml.py --env` and export variables via `$CLAUDE_ENV_FILE`, then run `--human` for output
3. If found: use `WORLDSMITH_LORE_DIR` instead of inferring `docs/` vs `lore/`
4. If found: skip the old single-manuscript loop (the parser handles work enumeration)
5. If NOT found: existing behavior unchanged

The script's `SCRIPT_DIR` needs to resolve to the hooks/scripts/ directory for locating the parser. Use `${CLAUDE_PLUGIN_ROOT}` if available, otherwise `$(dirname "$0")`.

- [ ] **Step 2: Verify backward compatibility**

Test with a project that has NO project.yaml — output should be identical to current behavior.

- [ ] **Step 3: Verify multi-work detection**

Test with the temporary project.yaml from Task 1:
```
Expected output:
Worldsmith project detected.

Universe: test-verse
Lore directory: lore/
Documents found:
  ...

Works:
  - Main Novel [novel] — chapters/ (N files)
  - Side Story [short-story] — stories/side/ (N files)

This is a worldsmith project with 2 works sharing lore/.
```

- [ ] **Step 4: Commit**

```bash
git add hooks/scripts/detect-worldsmith-project.sh
git commit -m "feat(worldsmith): detection script reads project.yaml for multi-work projects"
```

---

### Task 3: Propagation reminder — add stories/ directory

One-line change. The propagation-reminder.sh script classifies directories as doc or manuscript. `stories` (and subdirectories of stories) should be classified as manuscript.

**Files:**
- Modify: `hooks/scripts/propagation-reminder.sh:30-33`

- [ ] **Step 1: Add `stories` to manuscript directory case**

Change the case statement on line 31-33 from:
```bash
case "$dirname" in
  docs|lore|worldbuilding) is_doc=1 ;;
  chapters|manuscript|scenes) is_manuscript=1 ;;
esac
```
to:
```bash
case "$dirname" in
  docs|lore|worldbuilding) is_doc=1 ;;
  chapters|manuscript|scenes|stories) is_manuscript=1 ;;
esac
```

But this only matches the immediate parent directory name. A file at `stories/hemorrhagic/chapter1.tex` has dirname `hemorrhagic`, not `stories`. Need to also check the grandparent directory or use a path-contains check.

Better approach — also check if any ancestor directory is `stories`:
```bash
case "$dirname" in
  docs|lore|worldbuilding) is_doc=1 ;;
  chapters|manuscript|scenes|stories) is_manuscript=1 ;;
esac

# Also catch files in subdirectories of manuscript-like parents
if [ "$is_manuscript" = "0" ] && [ "$is_doc" = "0" ]; then
  case "$dirpath" in
    */chapters/*|*/manuscript/*|*/scenes/*|*/stories/*) is_manuscript=1 ;;
  esac
fi
```

- [ ] **Step 2: Verify**

Test that a file at `stories/hemorrhagic/chapter1.tex` triggers the manuscript reminder.

- [ ] **Step 3: Commit**

```bash
git add hooks/scripts/propagation-reminder.sh
git commit -m "feat(worldsmith): propagation reminder recognizes stories/ as manuscript directory"
```

---

## Chunk 2: Commands (review, check, change)

### Task 4: Update /worldsmith:review for work-name argument

The review command needs to accept an optional work name to scope the review.

**Files:**
- Modify: `commands/review.md`

- [ ] **Step 1: Update frontmatter and body**

Update `argument-hint` to show work-name option. Add multi-work awareness section to the body:

```yaml
argument-hint: "[work-name] [scope: full manuscript, or specific chapters e.g. 'chapters 3-5']"
```

Add after the existing body:

```markdown
## Multi-Work Awareness

If `.worldsmith/project.yaml` exists, this project contains multiple works sharing canonical lore.

**Work selection from `$ARGUMENTS`:**
- If a recognized work name appears in the arguments, scope the review to that work's manuscript directory.
- If no work name is specified and multiple works exist, review the **primary work** (first in `project.yaml`) and note this in the report preamble.
- Arguments can combine work name and scope: `/worldsmith:review Hemorrhagic` or `/worldsmith:review "The Policy" chapters 3-5`.

**Scoping rules:**
- Manuscript files come from the selected work's `manuscript` directory only.
- Canonical docs (lore) are always shared — all works reference the same lore directory.
- Review reports go to `.worldsmith/reviews/YYYY-MM-DD/<work-name>/` for multi-work projects.
- For single-work projects (no project.yaml), behavior is unchanged.

Pass the resolved work name and manuscript path to the reviewer agent in the launch prompt.
```

- [ ] **Step 2: Commit**

```bash
git add commands/review.md
git commit -m "feat(worldsmith): review command accepts work-name for multi-work projects"
```

---

### Task 5: Update /worldsmith:check for work-name argument

Same pattern as review — accept optional work name.

**Files:**
- Modify: `commands/check.md`

- [ ] **Step 1: Update frontmatter and body**

Update `argument-hint`:
```yaml
argument-hint: [work-name] [scope: all|consistency|editorial|xref|status]
```

Add a "Multi-Work Awareness" section after "Mode Selection":

```markdown
## Multi-Work Awareness

If `.worldsmith/project.yaml` exists, this project contains multiple works.

**Work selection:** Same rules as `/worldsmith:review` — if a work name appears in `$ARGUMENTS`, scope diagnostics to that work. If omitted, use the primary work (first in `project.yaml`).

**Mode-specific scoping:**
- `consistency` — Always checks against shared lore, regardless of which work is scoped. Flags contradictions between the scoped work's manuscript and canonical docs.
- `editorial` — Scoped to the selected work's manuscript files. Run `count_patterns.py` on that work's manuscript glob only.
- `xref` — Checks within the scoped work AND cross-work references (e.g., does a character mentioned in the short story match their entry in the shared lore?).
- `status` — Reports ALL works and their health, regardless of scoping. This is the one mode that always shows the full picture.
- `all` — Runs all modes with the above scoping rules.
```

- [ ] **Step 2: Commit**

```bash
git add commands/check.md
git commit -m "feat(worldsmith): check command accepts work-name for multi-work projects"
```

---

### Task 6: Update /worldsmith:change for cross-work propagation

The change command needs a small addition: when propagating a lore change, check all works' manuscripts, not just the primary.

**Files:**
- Modify: `commands/change.md`

- [ ] **Step 1: Add cross-work propagation step**

Add after the existing "Canonical Change" section (after step 5), a new step:

```markdown
6. If `.worldsmith/project.yaml` exists with multiple works, grep EACH work's manuscript directory for references to the changed fact. A character name change in shared lore affects every work that character appears in.
```

Also add a brief note to the "Rules" section:

```markdown
- For multi-work projects, propagation crosses work boundaries. A lore change that affects the novel may also affect the short story. Check all works' manuscript directories, not just the one you're currently editing.
```

- [ ] **Step 2: Commit**

```bash
git add commands/change.md
git commit -m "feat(worldsmith): change command propagates across all works in multi-work projects"
```

---

## Chunk 3: Orchestrator Agents

### Task 7: Update reviewer orchestrator for multi-work scoping

The reviewer needs to read project.yaml, scope manuscript to the right work, and write reports to work-scoped paths.

**Files:**
- Modify: `agents/reviewer.md`

- [ ] **Step 1: Update Phase 1 (Comprehension)**

Add after item 1 in the Phase 1 numbered list (after "Read the project's CLAUDE.md..."):

```
2. Read `.worldsmith/project.yaml` if it exists. Identify which work is being reviewed (from the prompt, or default to the primary work — first in the works list). Note the work's name, type, and manuscript path.
```

Renumber existing items 2-7 to 3-8.

Add a new item 8 to the structured understanding list:

```
8. **Work being reviewed** — If multi-work project: work name, type, manuscript path. If single-work: "single-work project, no project.yaml"
```

Update the existing "Scope of review" item to mention work:

```
9. **Scope of review** — Which work, and full manuscript or specific chapters (based on user request)
```

- [ ] **Step 2: Update Phase 2 (Parallel Specialist Review)**

In the XML template, update the `<manuscript>` tag comment to mention work scoping:

```xml
<manuscript>[chapters from the selected work's manuscript directory being reviewed]</manuscript>
```

- [ ] **Step 3: Update Phase 6 (Write Report)**

Update the mkdir command and report paths:

```markdown
For multi-work projects:
```bash
mkdir -p .worldsmith/reviews/YYYY-MM-DD/work-name
```

Reports go to `.worldsmith/reviews/YYYY-MM-DD/work-name/`. For single-work projects (no project.yaml), the existing path `.worldsmith/reviews/YYYY-MM-DD/` is used unchanged.

Add `**Work**: [name] ([type])` to the report header template after `**Manuscript**`.
```

- [ ] **Step 4: Commit**

```bash
git add agents/reviewer.md
git commit -m "feat(worldsmith): reviewer orchestrator scopes to specific work in multi-work projects"
```

---

### Task 8: Update writer orchestrator for multi-work scoping

Same pattern as reviewer — Phase 1 reads project.yaml, Phase 7 writes to the correct work's directory.

**Files:**
- Modify: `agents/writer.md`

- [ ] **Step 1: Update Phase 1 (Comprehension)**

Add after item 1:

```
2. Read `.worldsmith/project.yaml` if it exists. Identify which work is being written for (from the prompt, or ask via AskUserQuestion if ambiguous in a multi-work project). Note the work's manuscript path.
```

Renumber items 2-4 to 3-5.

Add to the structured understanding:

```
- **Target work** — If multi-work: work name, type, manuscript path. If single-work: inferred manuscript directory.
```

- [ ] **Step 2: Update Phase 7 (Output)**

Update the first bullet:

```markdown
- **Manuscript content** → the target work's manuscript directory (from project.yaml, or inferred)
```

- [ ] **Step 3: Commit**

```bash
git add agents/writer.md
git commit -m "feat(worldsmith): writer orchestrator targets specific work in multi-work projects"
```

---

### Task 9: Update rewriter orchestrator for multi-work scoping

The rewriter reads review reports, which are now work-scoped. It needs to find the right report and write revision reports to the same work-scoped path.

**Files:**
- Modify: `agents/rewriter.md`

- [ ] **Step 1: Update Phase 1 (Comprehension)**

Add after item 1:

```
2. Read `.worldsmith/project.yaml` if it exists. Identify which work's review is being addressed (from the review report path, or prompt context).
```

Renumber items 2-6 to 3-7.

Update item 3 (was item 3, "Read the review report"):

```
4. Read the review report from `.worldsmith/reviews/` (latest date directory and work subdirectory, or user-specified path)
```

- [ ] **Step 2: Update Phase 6 (Report)**

Update the report path:

```markdown
For multi-work projects, create the revision report at `.worldsmith/reviews/YYYY-MM-DD/work-name/revision.md`. For single-work projects, use `.worldsmith/reviews/YYYY-MM-DD/revision.md`.
```

- [ ] **Step 3: Commit**

```bash
git add agents/rewriter.md
git commit -m "feat(worldsmith): rewriter orchestrator handles work-scoped review reports"
```

---

## Chunk 4: Skill, Init-World, and Plugin Docs

### Task 10: Update methodology skill with multi-work section

**Files:**
- Modify: `skills/worldsmith-methodology/SKILL.md`

- [ ] **Step 1: Add multi-work section**

Add as a new section 8 (before "Additional Resources"), after "7. Consistency & Quality Awareness":

```markdown
## 8. Multi-Work Projects

A universe can contain multiple works sharing the same canonical docs. Configuration lives in `.worldsmith/project.yaml`. If this file does not exist, worldsmith treats the project as single-work (existing behavior, no change).

When working in a multi-work project:

- **Lore is shared.** All works draw from the same canonical docs. A change to a character entry affects every work that character appears in.
- **Manuscripts are scoped.** Each work has its own manuscript directory. Reviews, diagnostics, and writing target one work at a time.
- **Propagation crosses works.** When a canonical doc changes, check ALL works' manuscripts for affected passages, not just the one you're currently editing.
- **Reviews are per-work.** A review of the short story does not review the novel. But consistency checks always verify against shared lore.
- **Work identity from project.yaml.** Each work has a name, type (novel, novella, short-story, collection), manuscript directory, and optional file type filters. The first work listed is the primary work (default when no work is specified).
```

Renumber the "Additional Resources" section header from 8 to 9 (or leave unnumbered since it's already just a heading without a number — check the actual file).

- [ ] **Step 2: Commit**

```bash
git add skills/worldsmith-methodology/SKILL.md
git commit -m "feat(worldsmith): methodology skill documents multi-work project conventions"
```

---

### Task 11: Update /worldsmith:init-world for multi-work scaffolding

**Files:**
- Modify: `commands/init-world.md`

- [ ] **Step 1: Add multi-work awareness to Scaffold Mode**

In the Scaffold Mode section, add after item 2 ("Ask about related projects..."):

```
3. Ask whether this project will contain multiple works (e.g., a novel and short stories sharing the same world). If yes:
   - Ask for each work's name, type (novel/novella/short-story/collection), and manuscript directory.
   - Generate `.worldsmith/project.yaml` with the universe name, lore directory, and works list.
```

Renumber items 3-7 to 4-8.

In the Adopt Mode section, add after item 4 ("Look for manuscript files..."):

```
5. If multiple manuscript-like directories exist (e.g., both `chapters/` and `stories/`), ask whether this is a multi-work project. If yes, generate `.worldsmith/project.yaml`.
```

Renumber items 5-7 to 6-8.

Also fix the pre-existing `Bash(mkdir:*)` issue (same problem as check had):

```yaml
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, AskUserQuestion
```

- [ ] **Step 2: Commit**

```bash
git add commands/init-world.md
git commit -m "feat(worldsmith): init-world scaffolds project.yaml for multi-work projects"
```

---

### Task 12: Update plugin docs and bump version

**Files:**
- Modify: `CLAUDE.md`
- Modify: `commands/help.md`
- Modify: `.claude-plugin/plugin.json`
- Modify: `../.claude-plugin/marketplace.json`
- Modify: `../CLAUDE.md`

- [ ] **Step 1: Update worldsmith CLAUDE.md**

Add `hooks/scripts/parse-project-yaml.py` to the Plugin Structure tree.

In the "Core Concepts" section, add after "Series awareness":

```markdown
**Multi-work projects.** A universe can contain multiple works sharing canonical lore. Configured via `.worldsmith/project.yaml`. If absent, worldsmith infers a single work (backward compatible). Commands, agents, and hooks all respect work scoping when project.yaml is present.
```

- [ ] **Step 2: Update help.md**

Add a brief note under "Typical Workflows":

```markdown
**Multi-work universe:**
1. Place a `project.yaml` in `.worldsmith/` declaring the universe and its works
2. `/worldsmith:review WorkName` — review a specific work
3. `/worldsmith:check status` — see all works and their health
4. Shared lore propagation automatically checks all works
```

- [ ] **Step 3: Bump version 0.6.1 → 0.7.0**

Update all three version locations:
- `.claude-plugin/plugin.json`: `"version": "0.7.0"`
- `../.claude-plugin/marketplace.json`: worldsmith version `"0.7.0"`
- `../CLAUDE.md`: worldsmith row version `0.7.0`

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md commands/help.md .claude-plugin/plugin.json ../.claude-plugin/marketplace.json ../CLAUDE.md
git commit -m "feat(worldsmith): update plugin docs and bump to 0.7.0 for multi-work universe support"
```

- [ ] **Step 5: Validate**

Run the plugin validation script:
```bash
# Skill frontmatter
for f in skills/*/SKILL.md; do echo "=== $f ===" && head -5 "$f" && echo; done

# Command frontmatter
for f in commands/*.md; do echo "=== $f ===" && head -5 "$f" && echo; done

# Agent frontmatter
for f in agents/*.md; do echo "=== $f ===" && head -10 "$f" && echo; done

# Broken references
grep -roh '\${CLAUDE_PLUGIN_ROOT}/[^`"]*' skills/ commands/ | sort -u | while read ref; do
  resolved="${ref/\$\{CLAUDE_PLUGIN_ROOT\}/\.}"
  [ -f "$resolved" ] || echo "BROKEN: $ref"
done

# Hook scripts executable
ls -la hooks/scripts/*.sh hooks/scripts/*.py

# Versions match
python3 -c "import json; d=json.load(open('.claude-plugin/plugin.json')); print('plugin.json:', d['version'])"
python3 -c "import json; d=json.load(open('../.claude-plugin/marketplace.json')); [print('marketplace:', p['version']) for p in d['plugins'] if p['name']=='worldsmith']"
```

- [ ] **Step 6: Push**

```bash
git push
```
