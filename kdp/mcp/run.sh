#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
[ -d "$DIR/node_modules" ] || { echo "Run 'npm install' in $DIR first" >&2; exit 1; }
exec npx tsx "$DIR/src/index.ts"
