#!/bin/bash
# Count common prose patterns across manuscript files.
# Usage: count-patterns.sh <manuscript-glob>
# Example: count-patterns.sh "chapters/*.tex"
# Example: count-patterns.sh "manuscript/*.md"

set -euo pipefail

GLOB="${1:?Usage: count-patterns.sh <manuscript-glob>}"

echo "=== Prose Pattern Audit ==="
echo ""

# Crutch words
echo "--- Crutch Words ---"
for word in "something" "just" "really" "very" "actually" "basically" "simply" "quite"; do
    COUNT=$(grep -oi "\b${word}\b" $GLOB 2>/dev/null | wc -l)
    if [ "$COUNT" -gt 0 ]; then
        printf "  %-12s %d\n" "$word" "$COUNT"
    fi
done
echo ""

# Filter words
echo "--- Filter Words ---"
for pattern in "could see" "could feel" "could hear" "could sense" "could notice"; do
    COUNT=$(grep -oi "$pattern" $GLOB 2>/dev/null | wc -l)
    if [ "$COUNT" -gt 0 ]; then
        printf "  %-16s %d\n" "\"$pattern\"" "$COUNT"
    fi
done
echo ""

# Dialogue tags
echo "--- Adverb Dialogue Tags ---"
COUNT=$(grep -oiP "said [a-z]+ly" $GLOB 2>/dev/null | wc -l)
printf "  %-16s %d\n" "said [adverb]" "$COUNT"
echo ""

# Weak verbs
echo "--- Weak Verb Patterns ---"
for pattern in "started to" "began to" "tried to" "managed to" "continued to"; do
    COUNT=$(grep -oi "$pattern" $GLOB 2>/dev/null | wc -l)
    if [ "$COUNT" -gt 0 ]; then
        printf "  %-16s %d\n" "\"$pattern\"" "$COUNT"
    fi
done
echo ""

# Total word count (approximate)
echo "--- Manuscript Size ---"
WORDS=$(cat $GLOB 2>/dev/null | wc -w)
printf "  Total words: ~%d\n" "$WORDS"
