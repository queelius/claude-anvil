# CLAUDE.md (crier plugin)

Editing guidance for the crier Claude Code plugin. Read before editing.

## What this is

crier cross-posts blog content (the blog is the source of truth) to multiple
platforms: Dev.to, Hashnode, Bluesky, Mastodon, Medium, Twitter, and more. The
plugin is the judgment layer; the mechanics live in an external `crier` CLI.

## External dependency: the MCP server is not in-tree

`.mcp.json` does NOT bundle a server. It shells out to a globally-installed
`crier` CLI run as `crier mcp` (`pip install crier`). The SessionStart hook
(`hooks/scripts/detect-crier-setup.sh`) warns the user if the CLI is missing.
Editors must not expect a bundled server, and must not add `${CLAUDE_PLUGIN_ROOT}`
to the `.mcp.json` command: invoking the global `crier` binary is correct by
design.

## Components

- **`skills/crier/SKILL.md`**: judgment context the tools cannot encode, namely rewrite
  guidelines, platform culture, workflow tips.
- **Commands**: `/crier` (quick audit-and-publish), `/chronicler` (weekly
  cross-posting catch-up). Keep them thin; logic lives in the skill/agents.
- **Agents**: `cross-poster` (autonomous bulk publishing), `auditor` (read-only
  gap, performance, staleness, and failure analysis). Each agent's `tools` list
  should grant only the crier MCP tools it uses, plus `Read` and
  `AskUserQuestion`. IMPORTANT: because the server is plugin-bundled, the tools
  register as `mcp__plugin_crier_crier__crier_*` (NOT `mcp__crier__crier_*`);
  an allowlist with the short prefix matches nothing and locks the agent out.
  Do not grant `Bash`: the agents do not shell out, and the SessionStart hook
  runs outside the agents.

## MCP tool inventory and the count-drift trap

The `crier` MCP server exposes ~20 `crier_*` tools (archive, article,
campaign_plan, campaign_run, check, delete, doctor, failures, list_remote,
missing, publications, publish, query, reconcile, record, search, sql, stats,
stats_refresh, summary), surfaced in sessions under the
`mcp__plugin_crier_crier__` prefix. Do NOT hardcode a tool count in any description: an
earlier "17 tools" claim went stale. If you must reference the count, keep it in
sync or drop the number.

## Platform model and contracts

- **Platform modes**: API (automatic: devto, hashnode, bluesky, mastodon),
  import (medium: user imports from the canonical URL), paste (twitter, threads,
  linkedin: manual).
- **Short-form rewrite contract**: short platforms (bluesky 300, mastodon 500,
  twitter 280, threads 500) need a rewrite. Claude writes it and passes it via
  `rewrite_content`; crier appends the canonical URL automatically, so never
  include the URL in the rewrite.
- **Two-step confirmation** for destructive ops (publish, delete): call once
  without a token to get a preview plus token, then call again with the token to
  execute. Agents and commands all depend on this.

## Boundary with the mf plugin

`mf` owns creating and updating metafunctor.com content (Hugo); crier owns
distribution. The pipeline is mf to Hugo to crier. Do not duplicate
site-management logic here.

## Version bumps

Keep `.claude-plugin/plugin.json` and the `crier` entry in the root
`.claude-plugin/marketplace.json` in sync (both currently 1.2.0).
