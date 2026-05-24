# Cliche Hook Scoping: Implementation Plan

> **For agentic workers:** Execute task-by-task. Each task is a single atomic commit. Steps use checkbox (`- [ ]`) syntax.

**Goal**: Scope `check-fiction-cliches.sh` to manuscript paths only, with multi-work and single-work modes. Add a test harness. Bump to 0.10.0.

**Design doc**: `docs/plans/2026-05-24-cliche-hook-scoping-design.md`

---

## Chunk 1: Hook Edit

### Task 1: Add manuscript-scoping block to check-fiction-cliches.sh

Insert new logic after the file-extension gate (around current line 23) and before the text extraction (current line 30). On exit-with-skip, exit silently with code 0.

**Files**:
- Modify: `hooks/scripts/check-fiction-cliches.sh`

- [ ] **Step 1**: Add manuscript classification block.

Pseudo-structure:

```bash
# After extension gate, before text extraction:

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
is_manuscript=0

if [ -n "${WORLDSMITH_WORK_COUNT:-}" ] && [ "${WORLDSMITH_WORK_COUNT:-0}" -gt 0 ]; then
  # Multi-work mode: check configured manuscript paths
  for i in $(seq 0 $((WORLDSMITH_WORK_COUNT - 1))); do
    ms_var="WORLDSMITH_WORK_${i}_MANUSCRIPT"
    ms_rel="${!ms_var:-}"
    [ -z "$ms_rel" ] && continue
    ms_abs="$PROJECT_DIR/${ms_rel%/}"
    case "$file_path" in
      "$ms_abs"|"$ms_abs"/*) is_manuscript=1; break ;;
    esac
  done
else
  # Single-work mode: dirname/dirpath heuristics matching propagation-reminder.sh
  dirpath=$(dirname "$file_path")
  dirname=$(basename "$dirpath")
  case "$dirname" in
    chapters|manuscript|scenes|stories) is_manuscript=1 ;;
  esac
  if [ "$is_manuscript" = "0" ]; then
    case "$dirpath" in
      */chapters/*|*/manuscript/*|*/scenes/*|*/stories/*) is_manuscript=1 ;;
    esac
  fi
fi

if [ "$is_manuscript" = "0" ]; then
  exit 0
fi
```

- [ ] **Step 2**: Verify by running the test harness from Task 2 (these tasks are coupled in practice; commit them together if convenient).

- [ ] **Step 3**: Commit.

```bash
git add hooks/scripts/check-fiction-cliches.sh
git commit -m "fix(worldsmith): scope cliche hook to manuscript paths only"
```

(Use `fix(worldsmith):` because this corrects a too-broad gate that was producing false positives. Even though the version bump is minor (visible behavior change), the conceptual category is bugfix.)

---

## Chunk 2: Test Harness

### Task 2: Create tests/test-cliche-scoping.sh

First test file in the repo. Establishes a `tests/` convention for future hook scripts.

**Files**:
- Create: `tests/test-cliche-scoping.sh`

- [ ] **Step 1**: Write the test script.

```bash
#!/bin/bash
# Verifies check-fiction-cliches.sh scopes correctly to manuscript paths.
# Single-work-mode only. Multi-work tested manually.

set -uo pipefail

HOOK="$(dirname "$0")/../hooks/scripts/check-fiction-cliches.sh"
PASS=0
FAIL=0

run_test() {
  local desc="$1" file_path="$2" content="$3" expected_exit="$4"
  local input
  input=$(jq -n --arg p "$file_path" --arg c "$content" \
    '{tool_name: "Write", tool_input: {file_path: $p, content: $c}}')
  WORLDSMITH_PROJECT=1 bash "$HOOK" <<<"$input" >/dev/null 2>&1
  local actual=$?
  if [ "$actual" = "$expected_exit" ]; then
    echo "PASS: $desc"
    PASS=$((PASS+1))
  else
    echo "FAIL: $desc (expected $expected_exit, got $actual)"
    FAIL=$((FAIL+1))
  fi
}

CLICHE="her heart raced as the door creaked open"
CLEAN="The rain tapped against the window."

# Should fire (exit 2): manuscript paths with cliches
run_test "manuscript chapter file"        "/proj/chapters/01.md"           "$CLICHE" 2
run_test "manuscript subfolder file"      "/proj/manuscript/part1/ch1.md"  "$CLICHE" 2
run_test "stories subdir file"            "/proj/stories/short/intro.tex"  "$CLICHE" 2
run_test "scenes file"                    "/proj/scenes/opening.md"        "$CLICHE" 2

# Should skip (exit 0): non-manuscript paths with cliches
run_test "README"                          "/proj/README.md"               "$CLICHE" 0
run_test "CLAUDE.md"                       "/proj/CLAUDE.md"               "$CLICHE" 0
run_test "docs plan"                       "/proj/docs/plans/foo.md"       "$CLICHE" 0
run_test "root TODO"                       "/proj/TODO.txt"                "$CLICHE" 0

# Should skip (exit 0): manuscript paths without cliches
run_test "clean chapter file"             "/proj/chapters/02.md"           "$CLEAN"  0

echo
echo "Tests: $PASS passed, $FAIL failed"
[ "$FAIL" = "0" ]
```

- [ ] **Step 2**: Make executable.

```bash
chmod +x tests/test-cliche-scoping.sh
```

- [ ] **Step 3**: Run from worldsmith plugin root.

```bash
./tests/test-cliche-scoping.sh
```

Expected: 9 passed, 0 failed.

- [ ] **Step 4**: Commit (combine with Task 1 if convenient; otherwise separate commit).

```bash
git add tests/test-cliche-scoping.sh
git commit -m "test(worldsmith): add regression tests for cliche hook scoping"
```

---

## Chunk 3: Docs

### Task 3: Update CLAUDE.md and help.md

Two small text edits to keep documentation in sync with behavior.

**Files**:
- Modify: `CLAUDE.md`
- Modify: `commands/help.md`

- [ ] **Step 1**: Update CLAUDE.md hooks description.

In the Hooks section, update the PostToolUse description:

From:
```
**PostToolUse** (command, matcher: `Write|Edit`): Two hooks ...
```

To clarify the cliche hook is now manuscript-scoped:

```
**PostToolUse** (command, matcher: `Write|Edit`): Two hooks. Propagation reminders fire for doc and manuscript edits. Cliche detection fires only for edits to manuscript files (multi-work: paths configured in project.yaml; single-work: chapters/, manuscript/, scenes/, stories/ heuristics). Stops false positives on README, CLAUDE.md, docs/plans/, etc.
```

- [ ] **Step 2**: Update help.md "Automatic Guards" section.

From:
```
- **Cliche detection** -- blocks stock body reactions, dead metaphors, emotional labeling, redundant adverbs, and fancy dialogue tags on Write/Edit to fiction files
```

To:
```
- **Cliche detection** (manuscript-scoped): blocks stock body reactions, dead metaphors, emotional labeling, redundant adverbs, and fancy dialogue tags on Write/Edit to files inside the manuscript directory. Skips README, CLAUDE.md, plans, and other non-prose files.
```

- [ ] **Step 3**: Commit.

```bash
git add CLAUDE.md commands/help.md
git commit -m "docs(worldsmith): document manuscript-scoped cliche detection"
```

---

## Chunk 4: Plans and Version Bump

### Task 4: Commit the plans

The design and impl plans need their own commit per the established workflow.

- [ ] **Step 1**: Commit.

```bash
git add docs/plans/2026-05-24-cliche-hook-scoping-design.md docs/plans/2026-05-24-cliche-hook-scoping-impl.md
git commit -m "docs(worldsmith): add cliche hook scoping design and impl plans"
```

(In practice, this commit lands before Task 1, since plans precede implementation.)

---

### Task 5: Bump version 0.9.0 -> 0.10.0

Three-place version bump per parent CLAUDE.md rule.

**Files**:
- Modify: `.claude-plugin/plugin.json`
- Modify: `../.claude-plugin/marketplace.json`
- Modify: `../CLAUDE.md`

- [ ] **Step 1**: Bump `.claude-plugin/plugin.json` 0.9.0 -> 0.10.0.
- [ ] **Step 2**: Bump worldsmith row in `../.claude-plugin/marketplace.json` 0.9.0 -> 0.10.0.
- [ ] **Step 3**: Bump worldsmith row in `../CLAUDE.md` plugin table 0.9.0 -> 0.10.0.

- [ ] **Step 4**: Commit.

```bash
git add .claude-plugin/plugin.json ../.claude-plugin/marketplace.json ../CLAUDE.md
git commit -m "feat(worldsmith): bump to 0.10.0 for manuscript-scoped cliche detection"
```

---

## Chunk 5: Validation

### Task 6: Run validation block

- [ ] Skill frontmatter
- [ ] Command frontmatter
- [ ] Agent frontmatter
- [ ] `${CLAUDE_PLUGIN_ROOT}` references resolve
- [ ] Hook scripts executable
- [ ] Test script executable and passes
- [ ] No em-dashes in new prose (soul hook compliance)

```bash
ls -la hooks/scripts/*.sh tests/*.sh
./tests/test-cliche-scoping.sh
```

---

## Commit summary (expected)

1. `docs(worldsmith): add cliche hook scoping design and impl plans`
2. `fix(worldsmith): scope cliche hook to manuscript paths only`
3. `test(worldsmith): add regression tests for cliche hook scoping`
4. `docs(worldsmith): document manuscript-scoped cliche detection`
5. `feat(worldsmith): bump to 0.10.0 for manuscript-scoped cliche detection`

Five commits, atomic per concern.
