# Confidentiality Toolkit Plugin — Design

> **Date:** 2026-02-17
> **Status:** Approved

## Goal

A Claude Code plugin that gives Claude smart routing across three confidentiality tools: cryptoid (Hugo site encryption), pagevault (HTML/file encryption), and gpg (file encryption/signing). One skill, auto-triggered by natural language, picks the right tool based on context.

## Architecture

Single plugin with one skill. No slash commands, hooks, or agents.

```
~/github/alex-claude-plugin/
  .claude-plugin/plugin.json
  skills/
    confidential/
      SKILL.md
```

## Tool Landscape

| Tool | Scope | Key use case |
|------|-------|-------------|
| cryptoid | Hugo markdown pages | Multi-user/group cascade encryption for Hugo sites |
| pagevault | HTML regions + arbitrary files | Section-level encryption, self-contained HTML output with viewers |
| gpg | Any file | Offline encryption, signing, key-based trust (asymmetric/symmetric) |

## Routing Logic

```
Hugo site with markdown content?  →  cryptoid
HTML / static site / files for web delivery?  →  pagevault
Offline encryption, signing, key management?  →  gpg
Encrypt AND sign?  →  encrypt first (cryptoid/pagevault), then gpg --detach-sign
```

## Compound Workflows

- **Encrypt and sign**: cryptoid/pagevault encrypt → gpg detach-sign the output
- **Verify then decrypt**: gpg verify signature → pagevault unlock / cryptoid decrypt
- **Encrypt for web, archive original**: pagevault lock for delivery → gpg encrypt original for archival

## Skill Trigger Description

> Use when the user wants to encrypt, decrypt, lock, unlock, sign, verify, protect, or make content confidential. Covers Hugo site encryption (cryptoid), HTML/file encryption (pagevault), and file-level encryption/signing (gpg).

## Skill Content Structure

1. Decision tree (routing logic)
2. cryptoid CLI reference (~40 lines)
3. pagevault CLI reference (~40 lines)
4. gpg CLI reference (~30 lines)
5. Compound workflow recipes

## Out of Scope

- No native `--sign` flag in cryptoid/pagevault (future enhancement)
- No slash commands (natural language trigger via skill description)
- No hooks or MCP servers
- No agents

## Cleanup

Remove `cryptoid/claude/` directory — this plugin replaces it.
