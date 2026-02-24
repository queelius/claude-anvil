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
