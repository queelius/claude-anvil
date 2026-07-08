# claude-anvil

A forge for Claude Code plugins.

Claude Anvil is a plugin marketplace containing eleven Claude Code plugins for academic research, research-direction discovery, fiction worldbuilding, non-fiction book authoring, publication workflows, site management, repository intelligence, book publishing, cross-posting, encryption, and autonomous research. Each plugin provides skills, commands, and agents that extend Claude Code with domain-specific capabilities.

## Quick Start

```bash
# Install the marketplace
/plugin marketplace add queelius/claude-anvil

# Install an individual plugin
/plugin install papermill@queelius
```

## Plugins

| Plugin | Description | Version |
|--------|-------------|---------|
| [papermill](papermill/) | Academic paper lifecycle: thesis, lit survey, experiment, review, venue, submission | 0.8.2 |
| [worldsmith](worldsmith/) | Documentation-first fiction worldbuilding (the "Silmarillion approach") | 0.13.2 |
| [bookwright](bookwright/) | Non-fiction book authoring: LaTeX + paired computational notebooks, multi-agent drafting and review | 0.2.3 |
| [pub-pipeline](pub-pipeline/) | Publication workflows: R (CRAN/JOSS/JSS) and Python (PyPI) | 0.8.2 |
| [mf](mf/) | Metafunctor site management: blog architecture, content workflows, mf CLI | 1.3.0 |
| [repoindex](repoindex/) | Agent-driven repository intelligence with MCP-first architecture | 2.3.1 |
| [alex-confidential](locksmith/) | Confidentiality toolkit: cryptoid, pagevault, gpg encryption | 0.3.0 |
| [kdp](kdp/) | Amazon KDP book publishing: manuscript audit, listing craft, submission | 0.6.0 |
| [crier](crier/) | Cross-post blog content to multiple platforms | 1.3.0 |
| [research-agent](research-agent/) | Autonomous research agent: iterates toward a goal through proofs, code, simulations, tests | 0.5.1 |
| [vista](vista/) | Surface salient research directions from highly-cited papers (live OpenAlex + PDF section extraction) | 0.2.2 |

## Plugin Anatomy

Each plugin follows Claude Code plugin conventions:

```
<plugin>/
├── .claude-plugin/plugin.json   # Manifest: name, version, description, author
├── skills/<name>/SKILL.md       # Interactive skills (the core logic)
├── commands/<name>.md            # Slash commands (thin wrappers or rich docs)
├── agents/<name>.md              # Autonomous subagents with system prompts
├── hooks/hooks.json              # Event handlers (optional)
└── .mcp.json                     # MCP server registration (optional)
```

**Skills** are the heart of each plugin. They contain the domain knowledge and workflow logic. Commands are thin wrappers that trigger skills via `/plugin:command` syntax. Agents run autonomously for tasks like literature surveys or code review. Hooks react to events: SessionStart for ambient project detection, PostToolUse for gating, Stop for completion checks. MCP servers expose external tools to Claude Code.

Not every plugin uses every component. Minimal plugins like alex-confidential have only a skill. Larger plugins like worldsmith add hooks for ambient project detection and propagation discipline, while kdp, crier, and vista ship MCP servers for external tool access.

## License

MIT
