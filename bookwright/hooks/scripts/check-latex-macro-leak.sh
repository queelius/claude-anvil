#!/usr/bin/env bash
# check-latex-macro-leak.sh
#
# PostToolUse hook for Write/Edit on .tex files.
# Blocks if reader-visible prose contains references to LaTeX source-tool
# detail: macro names in \texttt{}, mentions of style packages, "rendered
# as" / "the macro" patterns.
#
# Reads the new file content from stdin (the hook protocol provides it),
# inspects it, exits 0 if clean, exits 2 with an explanation if it finds
# a leak.

set -euo pipefail

INPUT=$(cat)

# Extract the file path the hook is operating on.
FILE_PATH=$(echo "$INPUT" | python3 -c "
import json, sys
try:
    d = json.loads(sys.stdin.read())
    print(d.get('tool_input', {}).get('file_path', ''), end='')
except Exception:
    pass
")

# Skip non-tex files.
case "$FILE_PATH" in
    *.tex) ;;
    *) exit 0 ;;
esac

# Extract the new file content. For Write, that's tool_input.content.
# For Edit, that's tool_input.new_string (the post-edit fragment).
CONTENT=$(echo "$INPUT" | python3 -c "
import json, sys
d = json.loads(sys.stdin.read())
ti = d.get('tool_input', {})
print(ti.get('content', ti.get('new_string', '')), end='')
")

# Build a temp file holding only non-comment lines.
TMP=$(mktemp)
trap 'rm -f $TMP' EXIT
printf '%s\n' "$CONTENT" | sed 's/^%.*//' > "$TMP"

# Pattern checks. Each pattern, if matched, is a leak.
LEAKS=()

if grep -qE '\\texttt\{\\textbackslash[ ]?[a-zA-Z]' "$TMP"; then
    LEAKS+=("macro-name in \\texttt{\\textbackslash ...}: '\\texttt{\\textbackslash foo}' style reveals LaTeX macros to the reader")
fi

if grep -qiE '(\bthe macro\b|\brendered as\b)' "$TMP"; then
    LEAKS+=("'the macro' or 'rendered as' phrases reveal LaTeX implementation detail")
fi

if grep -qE '\balex\.sty\b|\btexttt\{alex\.sty\}' "$TMP"; then
    LEAKS+=("reference to 'alex.sty' (or any style package) belongs in source comments only, not reader prose")
fi

if [[ ${#LEAKS[@]} -gt 0 ]]; then
    # Plain text on stderr: with exit 2 the hook protocol feeds stderr to Claude
    # (JSON-on-stdout is the exit-0 path), and plain text avoids JSON escaping
    # of backslashes in LaTeX macro names.
    printf 'LaTeX-macro-leak hook blocked the write to %s. Reader-facing prose must not reveal LaTeX source-tool detail. Found:\n' "$FILE_PATH" >&2
    printf -- '- %s\n' "${LEAKS[@]}" >&2
    exit 2
fi

exit 0
