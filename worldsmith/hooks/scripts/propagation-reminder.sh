#!/bin/bash
# PostToolUse hook: remind about propagation after Write/Edit in worldsmith projects.
# Gates on WORLDSMITH_PROJECT env var set by detect-worldsmith-project.sh at SessionStart.
# Exits silently if not in a worldsmith project.

set -euo pipefail

# Gate: only run in worldsmith projects
if [ "${WORLDSMITH_PROJECT:-0}" != "1" ]; then
  exit 0
fi

# Read tool input from stdin to get the file path
input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // .tool_input.filePath // empty' 2>/dev/null || true)

# If we can't determine the file path, skip
if [ -z "$file_path" ]; then
  exit 0
fi

basename=$(basename "$file_path")
dirpath=$(dirname "$file_path")
dirname=$(basename "$dirpath")

# Check if this file is in a docs/lore directory or is a manuscript file
is_doc=0
is_manuscript=0

case "$dirname" in
  docs|lore|worldbuilding) is_doc=1 ;;
  chapters|manuscript|scenes|stories) is_manuscript=1 ;;
esac

# Also check by filename patterns
case "$basename" in
  lore.md|worldbuilding.md|characters.md|timeline.md|themes.md|style-guide.md|outline.md|future-ideas.md)
    is_doc=1 ;;
esac

# Also catch files in subdirectories of manuscript-like parents
if [ "$is_manuscript" = "0" ] && [ "$is_doc" = "0" ]; then
  case "$dirpath" in
    */chapters/*|*/manuscript/*|*/scenes/*|*/stories/*) is_manuscript=1 ;;
  esac
fi

# Multi-work projects: match the manuscript and lore dirs configured in
# project.yaml (env vars exported by detect-worldsmith-project.sh), mirroring
# check-fiction-cliches.sh
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
if [ -n "${WORLDSMITH_WORK_COUNT:-}" ] && [ "${WORLDSMITH_WORK_COUNT:-0}" -gt 0 ]; then
  for i in $(seq 0 $((WORLDSMITH_WORK_COUNT - 1))); do
    ms_var="WORLDSMITH_WORK_${i}_MANUSCRIPT"
    ms_rel="${!ms_var:-}"
    if [ "$is_manuscript" = "0" ] && [ -n "$ms_rel" ]; then
      ms_abs="$PROJECT_DIR/${ms_rel%/}"
      case "$file_path" in
        "$ms_abs"|"$ms_abs"/*) is_manuscript=1 ;;
      esac
    fi
    lore_var="WORLDSMITH_WORK_${i}_LORE"
    lore_rel="${!lore_var:-}"
    if [ "$is_doc" = "0" ] && [ -n "$lore_rel" ]; then
      lore_abs="$PROJECT_DIR/${lore_rel%/}"
      case "$file_path" in
        "$lore_abs"|"$lore_abs"/*) is_doc=1 ;;
      esac
    fi
  done
fi
if [ "$is_doc" = "0" ] && [ -n "${WORLDSMITH_LORE_DIR:-}" ]; then
  lore_abs="$PROJECT_DIR/${WORLDSMITH_LORE_DIR%/}"
  case "$file_path" in
    "$lore_abs"|"$lore_abs"/*) is_doc=1 ;;
  esac
fi

# Not a worldbuilding file — exit silently
if [ "$is_doc" = "0" ] && [ "$is_manuscript" = "0" ]; then
  exit 0
fi

# Output propagation reminder (shown in transcript)
if [ "$is_doc" = "1" ]; then
  echo "Propagation check: $basename was edited. Check the project's CLAUDE.md for which other docs and manuscript sections may need updating."
elif [ "$is_manuscript" = "1" ]; then
  echo "Manuscript edited: $basename. Verify this change is consistent with canonical docs. If this introduces a new fact, update the canonical doc first."
fi
