# jot — Claude Code Plugin

Journal-aware Claude Code sessions. Surfaces relevant tasks, ideas, and plans
from your [jot](https://github.com/queelius/jot) journal on session start,
providing ambient project context across conversations.

## Prerequisites

- [jot](https://github.com/queelius/jot) CLI installed and on PATH
- `jq` recommended (for SessionStart hook JSON parsing)
- `gh` CLI optional (for `/jot triage` PR cross-referencing)

## Components

| Type | Name | Purpose |
|------|------|---------|
| Skill | `jot` | Full CLI reference — triggers on journal-related queries |
| Command | `/jot` | Project summary (no args) or natural language jot interface |
| Command | `/jot triage` | Intelligent cleanup — cross-references entries with git history |
| Agent | `journal-analyst` | Deep journal analysis across entries and tags |
| Hook | SessionStart | Detects project context and shows compact journal summary |

## How It Works

**On session start**, the SessionStart hook detects if the current project has
related journal entries by fuzzy-matching the directory name against jot tags.
If a match is found, it shows a compact 3-5 line summary of open, in-progress,
and blocked items.

**During a session**, the jot skill activates whenever Claude needs to interact
with your journal — adding entries, searching, listing tasks, etc.

**On demand**, use `/jot` for a project dashboard or `/jot triage` to
intelligently clean up entries that may be finished or abandoned by
cross-referencing with git history.

**For deep analysis**, the journal-analyst agent handles multi-query tasks like
finding patterns across projects, generating reports, and auditing project
health.

## Install

```bash
# From claude-anvil marketplace
claude plugin install jot
```

## License

MIT
