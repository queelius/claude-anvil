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
  chapters|manuscript|scenes) is_manuscript=1 ;;
esac

# Also check by filename patterns
case "$basename" in
  lore.md|worldbuilding.md|characters.md|timeline.md|themes.md|style-guide.md|outline.md|future-ideas.md)
    is_doc=1 ;;
esac

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
