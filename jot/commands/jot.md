---
name: jot
description: Journal-aware project summary and natural language jot interface
argument-hint: "[query or instruction]"
allowed-tools:
  - Bash
  - Read
---

# /jot - Journal Command

## No Arguments: Project Summary Dashboard

When invoked with no arguments, build a concise project summary dashboard.

1. Determine the project context:
   - Get the current directory basename: `basename "$PWD"`
   - Run `jot tags --fuzzy <basename> --json` to find tags matching the current project.
   - If no matching tags are found, fall back to the global journal overview (see step 4).

2. If project tags are found, gather project data by running these commands:
   - `jot list --tags=<tag> --status=open --json --limit=20` to get open items.
   - `jot list --tags=<tag> --status=in_progress --json` to get in-progress items.
   - `jot stale --tags=<tag> --days 30 --json` to get stale items needing attention.

3. Present a compact dashboard (10-15 lines max) with these sections:
   - **Project name** and matching tag(s).
   - **Open tasks** with priorities if set. Group by type (task, idea, plan, etc.).
   - **In-progress items** currently being worked on.
   - **Ideas and plans** worth noting.
   - **Stale items** needing attention, if any exist.
   - Omit empty sections entirely. Do not show headers with zero items.

4. If no project context is found (no matching tags), show a global overview:
   - Run `jot tags --json` for the full tag overview.
   - Run `jot list --type=task --status=open --json --limit=10` for top open tasks.
   - Present a brief global journal summary showing tag distribution and top tasks.

## With Arguments: Natural Language Router

When invoked with arguments, interpret them as a natural language instruction and translate to the appropriate `jot` CLI command(s).

### Translation Examples

| User says | Command to run |
|---|---|
| "add a task to fix the auth bug" | `jot add "Fix the auth bug" --type=task --tags=<project>` |
| "what am I working on" | `jot list --status=in_progress --json` |
| "show me open tasks" | `jot list --type=task --status=open --json` |
| "search for authentication" | `jot search "authentication" --json` |
| "mark api-redesign as done" | `jot status api-redesign done` |
| "what's stale" | `jot stale --json` |
| "tag overview" | `jot tags` |
| "high priority tasks" | `jot list --type=task --priority=high --status=open --json` |
| "what's blocked" | `jot list --status=blocked --json` |
| "recent entries" | `jot list --json --limit=10` |

### Routing Rules

- When adding entries (`jot add`), automatically include the current project as a tag if project context is available. Determine this by running `basename "$PWD"` and checking for a matching tag via `jot tags --fuzzy <basename> --json`.
- Always use `--json` when the output needs to be parsed programmatically. Present results in a human-readable format to the user.
- For ambiguous queries, prefer listing/searching over modifying. Ask the user for confirmation before destructive operations like `jot purge` or bulk status changes.
- When the user asks to "show" or "list" something, default to `--json` output and format the results as a readable summary.
- When the user asks to "add" or "create" something, infer the `--type` from context (e.g., "task", "idea", "note", "plan", "log"). Default to `--type=note` if unclear.
- When the user provides a slug or partial title for status changes, use it directly with `jot status <slug> <new-status>`.
