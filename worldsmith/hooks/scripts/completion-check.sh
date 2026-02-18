#!/bin/bash
# Stop hook: verify propagation completeness before session exit in worldsmith projects.
# Gates on WORLDSMITH_PROJECT env var set by detect-worldsmith-project.sh at SessionStart.
# Outputs proper JSON with "decision" field as required by Stop hooks.

set -euo pipefail

# Gate: approve immediately if not in a worldsmith project
if [ "${WORLDSMITH_PROJECT:-0}" != "1" ]; then
  echo '{"decision": "approve"}'
  exit 0
fi

# In a worldsmith project — approve but add a reminder via systemMessage
cat <<'EOF'
{
  "decision": "approve",
  "systemMessage": "This is a worldsmith project. Before finishing: if you edited any worldbuilding docs or manuscript text this session, verify that (1) canonical docs were updated before manuscript, (2) cross-references were checked, and (3) the outline was updated if applicable. If propagation is incomplete, mention it to the user."
}
EOF
