#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
[ -d "$DIR/node_modules" ] || { echo "Run 'npm install' in $DIR first" >&2; exit 1; }
# Use the local tsx binary (pinned via package-lock.json) instead of `npx tsx`,
# which resolves to an unpinned version and incurs a network check on each start.
exec "$DIR/node_modules/.bin/tsx" "$DIR/src/index.ts"
