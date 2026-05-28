#!/usr/bin/env bash
# Smoke test: the macro-leak hook blocks the patterns it should and allows clean prose.

set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOK="$PLUGIN_ROOT/hooks/scripts/check-latex-macro-leak.sh"

# Positive case: clean .tex content passes
CLEAN='{"tool_input": {"file_path": "foo.tex", "content": "Standard prose with $\\fprate$ in math mode. The Bloom filter has $\\fprate = 0.01$."}}'
if ! echo "$CLEAN" | bash "$HOOK" > /dev/null 2>&1; then
    echo "FAIL: clean .tex content should pass but was rejected"
    exit 1
fi

# Negative case 1: \texttt{\textbackslash fprate} blocks
LEAK1='{"tool_input": {"file_path": "foo.tex", "content": "The false-positive rate is written \\texttt{\\textbackslash fprate} in the source."}}'
if echo "$LEAK1" | bash "$HOOK" > /dev/null 2>&1; then
    echo "FAIL: macro-name leak should block but passed"
    exit 1
fi

# Negative case 2: "alex.sty" mention blocks
LEAK2='{"tool_input": {"file_path": "foo.tex", "content": "The four rates are written via the standard alex.sty macros."}}'
if echo "$LEAK2" | bash "$HOOK" > /dev/null 2>&1; then
    echo "FAIL: alex.sty mention should block but passed"
    exit 1
fi

# Non-tex file: should be skipped (exit 0)
NONTEX='{"tool_input": {"file_path": "foo.md", "content": "The false-positive rate is written \\texttt{\\textbackslash fprate} in the source."}}'
if ! echo "$NONTEX" | bash "$HOOK" > /dev/null 2>&1; then
    echo "FAIL: non-.tex file should be skipped but was blocked"
    exit 1
fi

# Comment-only line: should be allowed
COMMENT='{"tool_input": {"file_path": "foo.tex", "content": "% This comment mentions \\texttt{\\textbackslash fprate} and alex.sty.\nStandard prose."}}'
if ! echo "$COMMENT" | bash "$HOOK" > /dev/null 2>&1; then
    echo "FAIL: comment-line containing leak patterns should pass but was blocked"
    exit 1
fi

echo "PASS: macro-leak hook accepts clean prose, blocks leaks, skips non-tex, allows comments"
