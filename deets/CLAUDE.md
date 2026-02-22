# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Claude Code plugin that wraps the `deets` CLI (`~/github/golang/deets`) for personal metadata queries. Exposes a skill and a slash command for looking up identity, contact, academic, education, and cross-platform profile information.

## Structure

```
deets/
├── .claude-plugin/plugin.json   # Plugin manifest (name, version, author)
├── commands/deets.md            # /deets slash command (thin wrapper)
└── skills/deets/SKILL.md        # The skill: deets CLI usage patterns
```

No agents or hooks. The skill auto-triggers when Claude needs personal metadata (author fields, git identity, ORCID, profile URLs, etc.). The `/deets` command provides explicit invocation.

## Key Design Decisions

- **Auto-detection + explicit command**: The skill fires implicitly via trigger phrases in its description. The `/deets` command is a thin wrapper for when auto-detection doesn't fire.
- **CLI dependency**: Requires `deets` to be installed on the host system. The skill documents the CLI interface but doesn't install or configure it.
- **Always dump first**: The skill directs Claude to run `deets show --format json` as the first move — never guess field paths. The schema evolves and hardcoded paths break. Targeted `get` is only for refreshing fields whose paths were seen in the dump.
- **Multi-path `get`**: `deets get path1 path2 path3` queries multiple paths in one call. Single exact path returns bare value; multi-path returns structured output. `--default` and `--exists` apply per-path.
- **Read-focused**: The skill teaches querying thoroughly but only mentions `populate` as a suggestion to the user — Claude should not run write commands without explicit user request.

## Editing Guidelines

- The skill's `description` frontmatter controls auto-invocation. Keep trigger phrases broad (identity, metadata, author, profile, ORCID, email, etc.).
- Preserve the output conventions section — other plugins depend on `deets get` returning bare pipe-friendly values.
- The command in `commands/deets.md` must stay minimal (one line delegating to the skill).
