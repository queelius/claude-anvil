# crier — Cross-Posting Plugin for Claude Code

Cross-post blog content to multiple platforms (Dev.to, Hashnode, Bluesky, Mastodon, Medium, Twitter, and more).

## Components

- **Skill** (`crier`): CLI/MCP reference, workflow guidance, rewrite guidelines
- **Commands**: `/crier` (quick audit-and-publish workflow), `/chronicler` (weekly cross-posting catch-up)
- **Agents**: `cross-poster` (autonomous bulk publishing), `auditor` (read-only gap, performance, and failure analysis)

Crier is MCP-native: the bundled `.mcp.json` registers a `crier` MCP server (the
globally-installed `crier` CLI run as `crier mcp`), and the skill plus agents
drive it through `mcp__crier__*` tools.

## Requirements

- [crier](https://pypi.org/project/crier/) CLI installed (`pip install crier`); this is also the MCP server
- API keys configured via `crier config set`

## Quick Start

```
/crier                    # Run the cross-posting workflow
/crier content/post       # Scope to blog posts only
```
