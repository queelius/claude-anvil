#!/bin/bash
# Fiction cliche check: detect stock body reactions, dead metaphors,
# emotional labeling, redundant adverbs, and fancy dialogue tags in prose content.
# Runs as a PostToolUse hook on Write|Edit for fiction files (.tex, .md, .mdx, .txt).
#
# If it fires, rewrite the passage to show the sensation through physical
# detail or action rather than naming it. See fiction plugin SKILL.md.
set -euo pipefail

# Gate: only run in worldsmith projects
if [ "${WORLDSMITH_PROJECT:-0}" != "1" ]; then
  exit 0
fi

input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name')
file_path=$(echo "$input" | jq -r '.tool_input.file_path // ""')

# Only check fiction-relevant file types
case "$file_path" in
  *.tex|*.md|*.mdx|*.txt) ;;
  *) exit 0 ;;
esac

# Skip files inside the fiction plugin itself (SKILL.md mentions these phrases as examples)
if [ -n "${CLAUDE_PLUGIN_ROOT:-}" ] && [[ "$file_path" == "$CLAUDE_PLUGIN_ROOT"* ]]; then
  exit 0
fi

# Extract the text that was written
if [ "$tool_name" = "Write" ]; then
  text=$(echo "$input" | jq -r '.tool_input.content // ""')
elif [ "$tool_name" = "Edit" ]; then
  text=$(echo "$input" | jq -r '.tool_input.new_string // ""')
else
  exit 0
fi

if [ -z "$text" ]; then
  exit 0
fi

violations=""

# --- Stock body reactions (show it, don't name the sensation) ---
while IFS= read -r phrase; do
  [ -z "$phrase" ] && continue
  if echo "$text" | grep -qi -F "$phrase"; then
    violations="${violations}- \"${phrase}\" (show it, don't name the sensation)\n"
  fi
done <<'PHRASES'
heart raced
heart pounded
heart skipped
eyes widened
eyes went wide
breath caught
blood ran cold
PHRASES

# --- Dead metaphors (show it, don't name the sensation) ---
while IFS= read -r phrase; do
  [ -z "$phrase" ] && continue
  if echo "$text" | grep -qi -F "$phrase"; then
    violations="${violations}- \"${phrase}\" (show it, don't name the sensation)\n"
  fi
done <<'PHRASES'
sent a chill down
a chill ran down
weight of the world
knot in her stomach
knot in his stomach
PHRASES

# --- Emotional labeling (show it, don't name the sensation) ---
while IFS= read -r phrase; do
  [ -z "$phrase" ] && continue
  if echo "$text" | grep -qi -F "$phrase"; then
    violations="${violations}- \"${phrase}\" (show it, don't name the sensation)\n"
  fi
done <<'PHRASES'
couldn't help but think
couldn't help but feel
couldn't help but notice
a mixture of excitement
filled with a sense of
let out a breath
didn't realize they had been holding
PHRASES

# --- Redundant adverbs (adverb duplicates the verb — cut or choose a more precise verb) ---
while IFS= read -r phrase; do
  [ -z "$phrase" ] && continue
  if echo "$text" | grep -qi -F "$phrase"; then
    violations="${violations}- \"${phrase}\" (adverb duplicates the verb — cut it or choose a more precise verb)\n"
  fi
done <<'PHRASES'
whispered quietly
shouted loudly
sprinted quickly
crept slowly
muttered softly
screamed loudly
tiptoed quietly
rushed hurriedly
PHRASES

# --- Fancy dialogue tags (use "said" or a physical beat instead) ---
while IFS= read -r phrase; do
  [ -z "$phrase" ] && continue
  if echo "$text" | grep -qi -F "$phrase"; then
    violations="${violations}- \"${phrase}\" (use \"said\" or a physical beat instead)\n"
  fi
done <<'PHRASES'
exclaimed
opined
mused
interjected
proclaimed
declared
retorted
quipped
remarked
PHRASES

# --- Report ---

if [ -n "$violations" ]; then
  msg=$(printf "Fiction cliche check failed on %s:\n%b\nRewrite to show the sensation through physical detail or action. See fiction plugin SKILL.md." "$file_path" "$violations")
  json_msg=$(echo "$msg" | jq -Rs .)
  echo "{\"systemMessage\": ${json_msg}}" >&2
  exit 2
fi

exit 0
