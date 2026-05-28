# CLAUDE.md (bookwright plugin)

This file is internal to the bookwright plugin. It is consumed by Claude Code when working ON the plugin (developing it), not when the plugin is invoked by an end user.

## Repository context

bookwright is one plugin in the `~/github/alex-claude-plugins/` (`claude-anvil`) monorepo. Sibling plugins include `worldsmith` (fiction), `papermill` (academic papers), `soul` (banned-phrase hooks).

## Development conventions

- Plugin component files (commands, agents, skills) are Markdown with YAML frontmatter.
- All command names use the `/bookwright:NAME` prefix in user-facing docs.
- Commit messages use `bookwright:` subject prefix.
- The plugin's design spec is at `docs/superpowers/specs/2026-05-28-bookwright-design.md`.
- v0.1 ships 9 agents (defers `rewriter` and `iterator` to v0.2).

## Testing

`tests/` contains shell smoke tests. To run all:

```bash
cd ~/github/alex-claude-plugins/bookwright/tests && bash test-init.sh && bash test-check.sh && bash test-macro-leak-hook.sh
```

## Validation

Before releasing, run `plugin-dev:plugin-validator` against this plugin.
