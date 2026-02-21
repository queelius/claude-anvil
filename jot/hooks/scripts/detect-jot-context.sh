#!/bin/bash
# Detect if the current project has related jot journal entries.
# Runs on SessionStart to give Claude ambient awareness of project context.
set -euo pipefail

# Check if jot is installed
if ! command -v jot &>/dev/null; then
  exit 0
fi

# Check if jq is available (needed for JSON parsing)
if ! command -v jq &>/dev/null; then
  exit 0
fi

# Get project name from current directory
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
PROJECT_NAME=$(basename "$PROJECT_DIR")

# Try fuzzy tag matching against the project name
# jot tags --fuzzy --json outputs one JSONL object per matching tag
MATCHING_TAGS=$(jot tags --fuzzy "$PROJECT_NAME" --json 2>/dev/null || true)

if [ -z "$MATCHING_TAGS" ]; then
  exit 0
fi

# Parse the first matching tag name (most relevant)
FIRST_TAG=$(echo "$MATCHING_TAGS" | head -1 | jq -r '.tag' 2>/dev/null || true)

if [ -z "$FIRST_TAG" ] || [ "$FIRST_TAG" = "null" ]; then
  exit 0
fi

# Count items by status using jq slurp (handles multi-line JSON)
OPEN_COUNT=$(jot list --tags="$FIRST_TAG" --status=open --json 2>/dev/null | jq -s 'length' 2>/dev/null || echo "0")
IN_PROGRESS=$(jot list --tags="$FIRST_TAG" --status=in_progress --json 2>/dev/null | jq -s 'length' 2>/dev/null || echo "0")
BLOCKED=$(jot list --tags="$FIRST_TAG" --status=blocked --json 2>/dev/null | jq -s 'length' 2>/dev/null || echo "0")

# Get total count from tag summary
TOTAL=$(echo "$MATCHING_TAGS" | head -1 | jq -r '.count' 2>/dev/null || echo "?")

# Output compact summary (3-5 lines)
echo "jot: ${TOTAL} entries tagged '${FIRST_TAG}' — ${OPEN_COUNT} open, ${IN_PROGRESS} in-progress, ${BLOCKED} blocked"

# Show high-priority items if any
HIGH_PRI=$(jot list --tags="$FIRST_TAG" --status=open --json 2>/dev/null | jq -rs '.[] | select(.priority == "high" or .priority == "critical") | "  ! \(.priority): \(.title)"' 2>/dev/null || true)
if [ -n "$HIGH_PRI" ]; then
  echo "$HIGH_PRI" | head -3
fi

# Show blocked items if any
if [ "$BLOCKED" -gt 0 ]; then
  BLOCKED_ITEMS=$(jot list --tags="$FIRST_TAG" --status=blocked --json 2>/dev/null | jq -rs '.[] | "  blocked: \(.title)"' 2>/dev/null || true)
  echo "$BLOCKED_ITEMS" | head -2
fi

echo "Use /jot for full project journal summary."
