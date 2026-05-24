# Orchestrator Commands: /worldsmith:draft and /worldsmith:revise

**Date**: 2026-05-23
**Status**: Design
**Scope**: Two new commands wrapping the writer and rewriter orchestrators

## Motivation

Worldsmith ships three orchestrator agents (reviewer, writer, rewriter) but exposes only one of them via a slash command (`/worldsmith:review`). The writer and rewriter agents are invisible to a user who does not already know the architecture.

Evidence in `commands/help.md`:

| Agent | Launched by (current) |
|-------|----------------------|
| reviewer | `/worldsmith:check all` or direct |
| writer | **Direct request** |
| rewriter | `/worldsmith:review` output or **direct** |

"Direct request" means the user must say something like "use the writer agent to draft chapter 5" with knowledge of the agent's name. The whole point of slash commands is to remove that requirement. Users should be able to type `/worldsmith:draft` or `/worldsmith:revise` and have the right orchestrator launch.

Side observation: the "Launched by: `/worldsmith:check all`" attribution for the reviewer is inaccurate. `commands/check.md` lists `allowed-tools: Read, Grep, Glob, Bash, AskUserQuestion` (no Task), so it cannot launch any agent. It runs read-only diagnostics directly. The help table is aspirational, not factual. Fix as part of this change.

### What breaks without these commands

1. **Discoverability.** A user reads `/worldsmith:help`, sees that writer and rewriter are launched "directly," and either gives up or types something the auto-detect heuristics may or may not catch.
2. **Composition with `/worldsmith:review`.** The natural follow-up to a review is a revision. Today the user must manually phrase the rewriter invocation. Tomorrow `/worldsmith:revise` is one keystroke after the review report renders.
3. **Multi-work parity.** `/worldsmith:review [work] [scope]` accepts a work-name argument for project.yaml-configured projects. Without `/worldsmith:draft [work] ...` and `/worldsmith:revise [work] ...`, the writer and rewriter are second-class citizens for multi-work projects.

### What already works

- Both agents are fully functional. They accept Task-tool invocation with prompt-as-context. The commands are thin wrappers around `Task(subagent_type: worldsmith:writer, prompt: <assembled>)`.
- Both agents already have multi-work awareness (Phase 1 of each reads `.worldsmith/project.yaml`). The command only needs to forward `$ARGUMENTS` and the recommended scoping rules.
- The `/worldsmith:review` command is a clean template. The new commands mirror its structure.

## Design

### Naming: action verbs, not agent names

The user-facing names are `draft` and `revise`. Not `writer` and `rewriter`. Slash commands should describe what the user is doing, not which subsystem handles it. This also leaves room to swap the underlying agent without renaming the command.

- `/worldsmith:draft` -> writer orchestrator
- `/worldsmith:revise` -> rewriter orchestrator

### /worldsmith:draft

**Purpose**: Launch the writer orchestrator to produce new content (scene, chapter, lore entry, character work, or a mix).

**Argument shape**: `[work-name] [assignment]`

Examples:
- `/worldsmith:draft chapter 5` (single-work project, full assignment)
- `/worldsmith:draft "Hemorrhagic" the opening scene` (multi-work project, work + assignment)
- `/worldsmith:draft Greymoor battle scene`
- `/worldsmith:draft develop the Ashwalker culture`

**Routing**: The writer orchestrator already classifies assignments (lore vs. scene vs. character vs. multi-specialist) in its Phase 2. The command does not need to do that classification. It forwards `$ARGUMENTS` minus the resolved work name as the assignment, and the writer figures out which specialists to launch.

**Multi-work scoping**: Same rules as `/worldsmith:review`. If a recognized work name appears in `$ARGUMENTS`, scope to that work. Otherwise default to the primary work (first in `project.yaml`) and note in the launch prompt.

**Output destination**: The writer's Phase 7 already writes manuscript content to the target work's manuscript directory. Command does not override.

### /worldsmith:revise

**Purpose**: Launch the rewriter orchestrator to apply fixes from a review report.

**Argument shape**: `[work-name] [review-path | severity-filter | category-filter]`

Examples:
- `/worldsmith:revise` (single-work, latest review, all findings)
- `/worldsmith:revise Hemorrhagic` (multi-work, latest review for that work)
- `/worldsmith:revise HIGH` (single-work, only HIGH-severity findings)
- `/worldsmith:revise Hemorrhagic consistency` (multi-work, only consistency-domain findings)
- `/worldsmith:revise .worldsmith/reviews/2026-03-12/Hemorrhagic/review.md` (explicit path override)

**Review report discovery**: If no explicit path is given, the command should locate the latest review report:
- Multi-work: `.worldsmith/reviews/<latest-date>/<work-name>/review.md`
- Single-work: `.worldsmith/reviews/<latest-date>/review.md`

If no review report exists, the command must tell the user to run `/worldsmith:review` first rather than silently failing.

**Filter forwarding**: Severity (HIGH/MEDIUM/LOW) and category (consistency/craft/voice/structure) filters are passed to the rewriter in the launch prompt. The rewriter already supports filtered fix dispatch (its Phase 2 Triage groups findings, and Phase 3 dispatches groups in parallel).

**Multi-work scoping**: Same rules as `/worldsmith:review` and `/worldsmith:draft`.

### Side fix: help.md reviewer attribution

Current row:

```
| **reviewer** | Multi-agent editorial review (consistency, craft, voice, structure) | `/worldsmith:check all` or direct |
```

Replace with:

```
| **reviewer** | Multi-agent editorial review (consistency, craft, voice, structure) | `/worldsmith:review` |
```

Also update the rewriter and writer rows to reference the new commands.

### Frontmatter conventions

Both commands need:

```yaml
---
description: <one-line description>
allowed-tools: Read, Glob, Grep, Task
argument-hint: "[work-name] [<command-specific>]"
---
```

Note `Task` in allowed-tools (these commands launch agents). `Read/Glob/Grep` for reading the project's CLAUDE.md and project.yaml in the command body, plus discovering the latest review report in the revise case.

`/worldsmith:revise` also needs `Bash` for `ls -t .worldsmith/reviews/` to find the latest date directory.

### Backward compatibility

These are pure additions. No existing commands or agents change behavior. The help.md edit is a docs-accuracy fix, not a contract change.

## Versioning

This is a minor feature addition (two new commands, no breaking changes). Bump 0.8.0 -> 0.9.0.

## Out of scope

Deferred to improvement #3 (`/worldsmith:iterate`):
- Autonomous review -> fix -> re-review loop until findings drop below threshold
- Iteration budget caps
- Convergence criteria

This design covers only the discoverability fix. The iteration loop is its own design exercise.
