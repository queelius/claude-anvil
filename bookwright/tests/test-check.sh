#!/usr/bin/env bash
# Smoke test: all command, agent, skill files have valid YAML frontmatter.

set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

FAILED=0

check_frontmatter() {
    local file="$1"
    local first_line
    first_line=$(head -n 1 "$file")
    if [ "$first_line" != "---" ]; then
        echo "FAIL: $file does not start with '---' (no YAML frontmatter)"
        FAILED=$((FAILED + 1))
        return
    fi
    python3 - "$file" << 'PYEOF'
import sys, yaml
path = sys.argv[1]
with open(path) as f:
    lines = f.readlines()
if lines[0].strip() != "---":
    print(f"FAIL: {path} no frontmatter")
    sys.exit(1)
end = None
for i, line in enumerate(lines[1:], start=1):
    if line.strip() == "---":
        end = i
        break
if end is None:
    print(f"FAIL: {path} frontmatter not closed")
    sys.exit(1)
fm = "".join(lines[1:end])
try:
    yaml.safe_load(fm)
except Exception as e:
    print(f"FAIL: {path} frontmatter invalid YAML: {e}")
    sys.exit(1)
PYEOF
    if [ $? -ne 0 ]; then FAILED=$((FAILED + 1)); fi
}

for cmd in init design plan draft notebook check review integrate help; do
    check_frontmatter "$PLUGIN_ROOT/commands/$cmd.md"
done
for ag in writer reviewer section-writer notebook-author source-reformulator spec-auditor quality-auditor math-auditor cross-ref-auditor; do
    check_frontmatter "$PLUGIN_ROOT/agents/$ag.md"
done
for sk in textbook-methodology cross-reference-discipline notebook-paired-with-prose; do
    check_frontmatter "$PLUGIN_ROOT/skills/$sk/SKILL.md"
done

if [ $FAILED -gt 0 ]; then
    echo "FAIL: $FAILED file(s) had invalid frontmatter"
    exit 1
fi

echo "PASS: all component files have valid YAML frontmatter"
