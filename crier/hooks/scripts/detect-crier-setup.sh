#!/bin/bash
# Detect crier CLI availability on SessionStart.
# Warns if the CLI is missing so MCP tools and the /crier skill fail loudly, not silently.
set -euo pipefail

if ! command -v crier &>/dev/null; then
  echo "crier: CLI not found on PATH. Install via: pip install crier"
  echo "  The crier MCP server, /crier command, and cross-poster agent all require the crier CLI."
  exit 0
fi

# Verify the binary actually runs (catches broken installs or wrong Python env)
if ! crier --version &>/dev/null; then
  echo "crier: CLI found but 'crier --version' failed. Installation may be broken."
  exit 0
fi

exit 0
