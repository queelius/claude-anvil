#!/usr/bin/env bash
# Smoke test: the plugin.json is valid and declares the expected fields.

set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# plugin.json exists
[ -f "$PLUGIN_ROOT/.claude-plugin/plugin.json" ] || { echo "FAIL: plugin.json missing"; exit 1; }

# plugin.json is valid JSON
python3 -m json.tool "$PLUGIN_ROOT/.claude-plugin/plugin.json" > /dev/null || { echo "FAIL: plugin.json invalid"; exit 1; }

# plugin.json declares name=bookwright
NAME=$(python3 -c "import json; print(json.load(open('$PLUGIN_ROOT/.claude-plugin/plugin.json'))['name'])")
[ "$NAME" = "bookwright" ] || { echo "FAIL: plugin name is '$NAME' not 'bookwright'"; exit 1; }

# README exists
[ -f "$PLUGIN_ROOT/README.md" ] || { echo "FAIL: README.md missing"; exit 1; }

# Required directories exist
for dir in commands agents skills hooks tests; do
    [ -d "$PLUGIN_ROOT/$dir" ] || { echo "FAIL: $dir/ missing"; exit 1; }
done

# Each command file exists
for cmd in init design plan draft notebook check review integrate help; do
    [ -f "$PLUGIN_ROOT/commands/$cmd.md" ] || { echo "FAIL: commands/$cmd.md missing"; exit 1; }
done

# Each agent file exists
for ag in writer reviewer section-writer notebook-author source-reformulator spec-auditor quality-auditor math-auditor cross-ref-auditor; do
    [ -f "$PLUGIN_ROOT/agents/$ag.md" ] || { echo "FAIL: agents/$ag.md missing"; exit 1; }
done

# Each skill exists
for sk in textbook-methodology cross-reference-discipline notebook-paired-with-prose; do
    [ -f "$PLUGIN_ROOT/skills/$sk/SKILL.md" ] || { echo "FAIL: skills/$sk/SKILL.md missing"; exit 1; }
done

# Hooks
[ -f "$PLUGIN_ROOT/hooks/hooks.json" ] || { echo "FAIL: hooks/hooks.json missing"; exit 1; }
[ -x "$PLUGIN_ROOT/hooks/scripts/check-latex-macro-leak.sh" ] || { echo "FAIL: hooks/scripts/check-latex-macro-leak.sh missing or not executable"; exit 1; }

echo "PASS: bookwright plugin structure check"
