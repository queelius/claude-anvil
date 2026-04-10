# repoindex: Claude Code Plugin

Agent-driven repository intelligence for Claude Code. Multi-step analysis and release preparation workflows backed by the [repoindex](https://github.com/queelius/repoindex) MCP server.

**Requires**: [repoindex](https://github.com/queelius/repoindex) v0.15.0 or newer with MCP extra:
```bash
pip install repoindex[mcp]
repoindex refresh --external
```

And the repoindex MCP server configured in `~/.claude.json`:
```json
{
  "mcpServers": {
    "repoindex": {
      "type": "stdio",
      "command": "/path/to/repoindex",
      "args": ["mcp"]
    }
  }
}
```

## Agents

| Name | Purpose | Model |
|------|---------|-------|
| `repo-doctor` | Collection health triage. "What needs attention?" | sonnet |
| `repo-polish` | Single-repo release preparation (audit, generate, improve) | opus |
| `repo-explorer` | Open-ended collection analysis with custom SQL | sonnet |

All three agents access repoindex data via MCP tools. The plugin has no skills or slash commands. Single queries are handled by Claude Code's built-in MCP tool invocation.

## Install

```bash
# Symlink into your plugins workspace
ln -s /path/to/this/repo ~/github/alex-claude-plugins/repoindex
```

## Usage

Trigger the agents by describing what you want:

- "What needs attention across my repos?" will invoke `repo-doctor`
- "Polish repoindex for release" will invoke `repo-polish`
- "Which of my Python repos are published on PyPI?" will invoke `repo-explorer`

Or ask direct questions that Claude Code will answer via MCP tools without invoking an agent:

- "Show me dirty repos"
- "How many Python repos do I have?"
- "What are my most starred repos?"

## License

MIT
