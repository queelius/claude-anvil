---
description: Show worldsmith commands, skills, and typical workflows
allowed-tools: Read
---

# /worldsmith:help

Display a quick-reference guide to the worldsmith plugin.

## Commands

| Command | Purpose |
|---------|---------|
| `/worldsmith:init-world [name]` | Scaffold or adopt a worldbuilding doc ecosystem |
| `/worldsmith:change [description]` | Apply a change — canonical edits, exploratory ideas, or promotions |
| `/worldsmith:check [scope]` | Run diagnostics: `consistency`, `editorial`, `xref`, `status`, or `all` |
| `/worldsmith:help` | This guide |

## Skills (auto-triggered)

| Skill | Triggers when... |
|-------|-------------------|
| **worldsmith-methodology** | You work on worldbuilding docs, lore, or editorial structure |
| **prose-craft** | You write or edit fiction prose, scenes, or dialogue |

## Typical Workflows

**Starting a new project:**
1. Navigate to your project directory
2. `/worldsmith:init-world` — scaffolds docs and CLAUDE.md

**Writing a chapter:**
1. The prose-craft skill auto-triggers with craft guardrails
2. The cliche detection hook fires on each Write/Edit, catching stock phrases in real-time
3. Propagation reminders fire if you edit docs or manuscript

**Adding or changing lore:**
1. `/worldsmith:change add a new faction called the Ashwalkers`
2. Worldsmith updates canonical docs first, then propagates to manuscript

**Before a writing session:**
1. `/worldsmith:check status` — project health overview
2. `/worldsmith:check consistency` — catch contradictions
3. `/worldsmith:check editorial` — prose pattern audit with `count_patterns.py`

**After a big revision:**
1. `/worldsmith:check all` — full diagnostic sweep

## Automatic Guards

These fire without you invoking anything (in worldsmith-detected projects):

- **Cliche detection** — blocks stock body reactions, dead metaphors, emotional labeling, redundant adverbs, and fancy dialogue tags on Write/Edit to fiction files
- **Propagation reminders** — reminds you to check downstream docs when you edit a canonical source or manuscript
- **Completion check** — verifies propagation before session exit
