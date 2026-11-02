# claude-anvil

A forge for Claude Code plugins.

Claude Anvil is the `queelius-plugins` marketplace: eleven Claude Code plugins for academic research, research-direction discovery, fiction worldbuilding, non-fiction book authoring, publication workflows, site management, repository intelligence, book publishing, cross-posting, encryption, and autonomous research.

## Quick Start

```bash
# Add the marketplace
/plugin marketplace add queelius/claude-anvil

# Install a plugin
/plugin install papermill@queelius-plugins
```

papermill, worldsmith, and bookwright are opt-in (`defaultEnabled: false`): enable the one that matches a project from inside that repo with `/plugin enable <name>@queelius-plugins`.

## Plugins

| Plugin | Description |
|--------|-------------|
| [papermill](papermill/) | Academic paper lifecycle: thesis, lit survey, experiment, review, venue, submission |
| [worldsmith](worldsmith/) | Documentation-first fiction worldbuilding (the "Silmarillion approach") |
| [bookwright](bookwright/) | Non-fiction book authoring: LaTeX + paired computational notebooks, multi-agent drafting and review |
| [pub-pipeline](pub-pipeline/) | Publication workflows: R (CRAN/JOSS/JSS) and Python (PyPI) |
| [mf](mf/) | Metafunctor site management: content workflows over the mf CLI |
| [repoindex](repoindex/) | Repository intelligence with an MCP-first architecture |
| [alex-confidential](alex-confidential/) | Confidentiality toolkit: cryptoid, pagevault, gpg |
| [kdp](kdp/) | Amazon KDP book publishing: manuscript audit, listing craft, covers, submission |
| [crier](crier/) | Cross-post blog content to multiple platforms |
| [research-agent](research-agent/) | Autonomous research agent: iterates toward a goal through proofs, code, simulations, tests |
| [vista](vista/) | Surface salient research directions from highly-cited papers (live OpenAlex + PDF section extraction) |
| research-communication | Readable research writing and blind review of drafts. Lives in a private repo (`queelius/writing-style`), so installing it needs GitHub access to that repo |

Each plugin's version is in its `.claude-plugin/plugin.json`.

## Plugin Anatomy

```
<plugin>/
├── .claude-plugin/plugin.json   # Manifest: name, version, description, author
├── skills/<name>/SKILL.md       # Skills: domain logic, also invocable as /plugin:<name>
├── commands/<name>.md            # Standalone slash commands (never named like a skill)
├── agents/<name>.md              # Subagents with system prompts
├── hooks/hooks.json              # Event handlers (optional)
└── .mcp.json                     # MCP server registration (optional)
```

**Skills** are the heart of each plugin and double as slash commands (`/papermill:review`). **Agents** run as subagents for multi-step work such as literature surveys or editorial review. **Hooks** react to events (SessionStart for project detection and dependency checks, PostToolUse for prose and LaTeX checks). **MCP servers** expose structured tools: crier, kdp, and vista ship one.

## Development

`python3 scripts/check-plugins.py` checks plugin conventions; CI (`.github/workflows/validate.yml`) also runs `claude plugin validate`, the vista and kdp test suites, and the worldsmith/bookwright hook tests. See `CLAUDE.md` for conventions.

## License

MIT
