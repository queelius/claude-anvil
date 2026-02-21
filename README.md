# claude-anvil

A forge for Claude Code plugins.

Claude Anvil is a plugin marketplace containing nine Claude Code plugins for academic research, creative worldbuilding, publication workflows, site management, repository intelligence, personal metadata, encryption, and more. Each plugin provides skills, commands, and agents that extend Claude Code with domain-specific capabilities.

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
| [papermill](papermill/) | Academic paper lifecycle: thesis, lit survey, experiment, review, venue, submission | 0.3.0 |
| [worldsmith](worldsmith/) | Documentation-first fiction worldbuilding (the "Silmarillion approach") | 0.2.0 |
| [pub-pipeline](pub-pipeline/) | Publication workflows: R/CRAN/JOSS, Python/PyPI, books/KDP, preprints/OSF | 0.4.0 |
| [mf](mf/) | Metafunctor site management: blog architecture, content workflows, crier | 1.0.0 |
| [repoindex](repoindex/) | Collection-aware repository intelligence — query, analyze, maintain git repos | 0.10.0 |
| [deets](deets/) | Personal metadata queries — identity, contact, academic, profiles | 1.0.0 |
| [alex-confidential](locksmith/) | Confidentiality toolkit — cryptoid, pagevault, gpg encryption | 0.1.0 |
| [kdp](kdp/) | Amazon KDP book publishing: manuscript audit, listing craft, submission workflow | 0.1.0 |
| [jot](jot/) | Journal-aware sessions — surfaces tasks, ideas, and plans from your jot journal | 0.1.0 |

## Plugin Anatomy

Each plugin follows Claude Code plugin conventions:

```
<plugin>/
├── .claude-plugin/plugin.json   # Manifest: name, version, description, author
├── skills/<name>/SKILL.md       # Interactive skills (the core logic)
├── commands/<name>.md           # Slash commands (thin wrappers or rich docs)
├── agents/<name>.md             # Autonomous subagents with system prompts
└── hooks/hooks.json             # Event handlers (optional)
```

**Skills** are the heart of each plugin — they contain the domain knowledge and workflow logic. Commands are thin wrappers that trigger skills via `/plugin:command` syntax. Agents run autonomously for tasks like literature surveys or code review.

Not every plugin uses every component. Minimal plugins like deets have only a skill and a command. Larger plugins like worldsmith add hooks for ambient project detection and propagation discipline.

## License

MIT
