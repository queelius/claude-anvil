#!/bin/bash
# Detect if the current project is a worldsmith-managed worldbuilding project.
# Runs on SessionStart to give Claude ambient awareness of the doc ecosystem.

set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"

# Look for docs/ or lore/ directory with markdown files
DOCS_DIR=""
if [ -d "$PROJECT_DIR/docs" ] && ls "$PROJECT_DIR/docs/"*.md &>/dev/null; then
  DOCS_DIR="$PROJECT_DIR/docs"
elif [ -d "$PROJECT_DIR/lore" ] && ls "$PROJECT_DIR/lore/"*.md &>/dev/null; then
  DOCS_DIR="$PROJECT_DIR/lore"
fi

# Not a worldsmith project — exit silently
if [ -z "$DOCS_DIR" ]; then
  exit 0
fi

# It's a worldsmith project — output context for Claude
echo "Worldsmith project detected."
echo ""
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

# Check for project CLAUDE.md with worldsmith configuration
if [ -f "$PROJECT_DIR/CLAUDE.md" ]; then
  if grep -qi "document roles\|propagation\|canonical hierarchy\|doc.*ecosystem\|worldbuilding\|worldsmith" "$PROJECT_DIR/CLAUDE.md"; then
    echo ""
    echo "Project CLAUDE.md contains worldsmith configuration."
    echo "Read it for document roles and propagation rules."
  fi
fi

# Check for related projects referenced in CLAUDE.md
if [ -f "$PROJECT_DIR/CLAUDE.md" ]; then
  related=$(grep -oP '~/[^\s)]+' "$PROJECT_DIR/CLAUDE.md" 2>/dev/null | head -5)
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
