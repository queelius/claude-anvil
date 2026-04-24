# repoindex: Claude Code Plugin

Repository intelligence for Claude Code. MCP-driven access to a local git catalog, with agents for multi-step workflows and slash commands for recurring queries. Backed by the [repoindex](https://github.com/queelius/repoindex) MCP server.

**Requires**: [repoindex](https://github.com/queelius/repoindex) v0.16 or newer with the MCP extra:
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

## Slash commands

| Command | Purpose |
|---------|---------|
| `/repo-week [Nd]` | Weekly activity summary (commits, releases, top churn). Default 7 days. |
| `/repo-status [name]` | Collection overview, or single-repo detail if a name is given. |
| `/repo-audit [filters]` | Read-only audit summary across the collection. |
| `/repo-sprint` | Assembled kickoff context: dirty, unpushed, active, release candidates. |
| `/repo-mirror [flags]` | Wrapper around `repoindex ops mirror`. Dry run by default; pass `--force-real` to push. |

## Skills

| Skill | When it fires |
|-------|---------------|
| `workflows` | Guidance on which tool (MCP call, slash command, agent) fits a given repoindex task, plus tag strategy. |

## Install

```bash
# Symlink into your plugins workspace
ln -s /path/to/this/repo ~/github/alex-claude-plugins/repoindex
```

## Usage

Direct questions go through MCP tools automatically:

- "Show me dirty repos"
- "How many Python repos do I have?"
- "What are my most starred repos?"

Slash commands run fixed-shape workflows:

- `/repo-week 30d`: monthly rollup
- `/repo-status repoindex`: detail view for one repo

Agents handle multi-step jobs:

- "What needs attention across my repos?" invokes `repo-doctor`.
- "Polish repoindex for release" invokes `repo-polish`.
- "Which of my Python repos are published on PyPI?" invokes `repo-explorer` (or resolves directly as a `run_sql` if the question is simple enough).

## License

MIT
