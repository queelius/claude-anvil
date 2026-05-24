#!/bin/bash
# Regression tests for check-fiction-cliches.sh manuscript scoping.
#
# Verifies that the hook only fires inside manuscript directories
# (chapters/, manuscript/, scenes/, stories/ and their subdirs) and skips
# other locations like README, CLAUDE.md, and docs/plans/, even when the
# file content contains banned phrases.
#
# Single-work mode only. Multi-work mode (project.yaml + env vars) covered
# by manual smoke test.

set -uo pipefail

HOOK="$(dirname "$0")/../hooks/scripts/check-fiction-cliches.sh"
PASS=0
FAIL=0

if ! command -v jq >/dev/null 2>&1; then
  echo "FATAL: jq not installed; cannot run hook test harness" >&2
  exit 1
fi

run_test() {
  local desc="$1" file_path="$2" content="$3" expected_exit="$4"
  local input actual
  input=$(jq -n --arg p "$file_path" --arg c "$content" \
    '{tool_name: "Write", tool_input: {file_path: $p, content: $c}}')
  WORLDSMITH_PROJECT=1 bash "$HOOK" <<<"$input" >/dev/null 2>&1
  actual=$?
  if [ "$actual" = "$expected_exit" ]; then
    echo "PASS: $desc"
    PASS=$((PASS+1))
  else
    echo "FAIL: $desc (expected $expected_exit, got $actual)"
    FAIL=$((FAIL+1))
  fi
}

CLICHE="Her heart raced as the door creaked open."
CLEAN="The rain tapped against the window."

# Should fire (exit 2): manuscript paths with cliches
run_test "chapter file"                "/proj/chapters/01.md"               "$CLICHE" 2
run_test "manuscript file"             "/proj/manuscript/part1/ch1.md"      "$CLICHE" 2
run_test "stories nested file"         "/proj/stories/short/intro.tex"      "$CLICHE" 2
run_test "scenes file"                 "/proj/scenes/opening.md"            "$CLICHE" 2

# Should skip (exit 0): non-manuscript paths even with cliches
run_test "README"                      "/proj/README.md"                    "$CLICHE" 0
run_test "CLAUDE.md"                   "/proj/CLAUDE.md"                    "$CLICHE" 0
run_test "design plan in docs/plans"   "/proj/docs/plans/cliche-design.md"  "$CLICHE" 0
run_test "root TODO"                   "/proj/TODO.txt"                     "$CLICHE" 0
run_test "lore doc"                    "/proj/lore/characters.md"           "$CLICHE" 0

# Should skip (exit 0): manuscript paths without cliches
run_test "clean chapter file"          "/proj/chapters/02.md"               "$CLEAN"  0
run_test "clean scenes file"           "/proj/scenes/03.md"                 "$CLEAN"  0

echo
echo "Tests: $PASS passed, $FAIL failed"
[ "$FAIL" = "0" ]
