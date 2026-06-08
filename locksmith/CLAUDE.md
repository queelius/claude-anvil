# CLAUDE.md (alex-confidential plugin)

Editing guidance for the confidentiality plugin. Read before editing.

## Name mapping (important)

The on-disk directory is `locksmith/`, but the public, installed plugin name is
`alex-confidential`. The bridge is `marketplace.json`, whose entry sets
`"source": "./locksmith"` with `name: alex-confidential`. Never rename one
without the other, and grep BOTH names when refactoring: a maintainer searching
for the plugin by its public name will not find it on disk.

## Architecture

A skill-only plugin: no commands, no agents, no MCP server. All routing logic
lives in `skills/confidential/SKILL.md`, with heavy per-tool detail in
`references/{cryptoid,pagevault,gpg}.md`.

- Edit the `references/*.md` files for tool-specific command syntax.
- Edit `SKILL.md` only for routing or decision-tree changes.

The skill triggers on natural language; there is no slash command.

## External dependencies

The skill assumes three out-of-repo tools on PATH:

- `cryptoid` (the user's own package): Hugo-site markdown encryption.
- `pagevault` (the user's own package): HTML and arbitrary-file encryption for
  browser delivery.
- `gpg` (system): offline encryption and signing.

When any of their CLIs change, update the corresponding `references/*.md` command
tables.

## The three-tool routing contract

- cryptoid: Hugo markdown content.
- pagevault: HTML or arbitrary files for the browser.
- gpg: offline encryption and signing.

This selection matrix appears in three places (the SKILL.md selection table, the
README table, and the SKILL decision tree). Keep all three in sync.

## Security-doc discipline

Example configs in `references/` contain cleartext credentials. Any new example
must keep the "add to .gitignore" warning and use obviously-fake placeholder
values, never anything resembling a real secret.

## Version bumps

Keep `.claude-plugin/plugin.json` and the `alex-confidential` entry in the root
`.claude-plugin/marketplace.json` in sync (both currently 0.2.0).
