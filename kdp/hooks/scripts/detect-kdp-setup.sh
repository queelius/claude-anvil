#!/bin/bash
# Detect kdp MCP server readiness on SessionStart.
# Warns if Node dependencies are missing so cover generation fails loudly, not silently.
set -euo pipefail

# Hook contract: never block, never crash. Claude Code sets CLAUDE_PLUGIN_ROOT
# at hook time; if a user runs this script standalone for testing without it,
# exit silently rather than tripping `set -u`.
[ -n "${CLAUDE_PLUGIN_ROOT:-}" ] || exit 0

MCP_DIR="${CLAUDE_PLUGIN_ROOT}/mcp"

# MCP dir absent (e.g., stripped install): nothing to check
[ -d "$MCP_DIR" ] || exit 0

# Node dependencies not installed
if [ ! -d "$MCP_DIR/node_modules" ]; then
  echo "kdp: MCP server dependencies not installed. kdp_cover_specs, kdp_generate_cover, kdp_generate_full_wrap will fail."
  echo "  Run: (cd \"$MCP_DIR\" && npm install)"
  exit 0
fi

# node binary missing
if ! command -v node &>/dev/null; then
  echo "kdp: node not on PATH. Cover generation requires Node.js."
  exit 0
fi

# OPENAI_API_KEY is needed by kdp_generate_cover
if [ -z "${OPENAI_API_KEY:-}" ]; then
  echo "kdp: OPENAI_API_KEY is not set. kdp_generate_cover will fail; set it in your shell environment before publishing."
fi

exit 0
