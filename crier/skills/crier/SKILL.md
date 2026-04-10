---
name: crier
description: Cross-post blog content to social platforms. Crier is MCP-native with 17 tools. This skill provides judgment context that tools can't: rewrite guidelines, platform culture, workflow tips.
---

# Crier Cross-Posting

Crier cross-posts blog content to multiple platforms. The blog is the source of truth.

**Division of labor:**
- **Crier MCP tools** handle mechanics: publish, track, query, validate
- **Claude** handles judgment: rewrites, platform voice, user interaction

## Platform Reference

| Platform  | Mode   | Limit  | Short-form? | Notes                          |
|-----------|--------|--------|-------------|--------------------------------|
| devto     | API    | none   | No          | Tags auto-sanitized            |
| hashnode  | API    | none   | No          |                                |
| bluesky   | API    | 300    | Yes         | Needs rewrite                  |
| mastodon  | API    | 500    | Yes         | Needs rewrite                  |
| medium    | import | none   | No          | User imports from canonical URL |
| twitter   | paste  | 280    | Yes         | Copy-paste only                |
| threads   | paste  | 500    | Yes         | Copy-paste only                |
| linkedin  | paste  | none   | No          | Copy-paste only                |

## Rewrite Guidelines

When cross-posting to short-form platforms (bluesky, mastodon), write a rewrite
and pass it via `crier_publish(rewrite_content=...)`.

### Rules

1. **Lead with insight, not summary.** Open with the most interesting idea.
2. **No meta-language.** Don't say "New blog post" or "I wrote about."
3. **Crier appends the canonical URL automatically.** Never include it in the rewrite.
4. **Match platform voice:**
   - Bluesky: conversational, personal, like talking to a friend
   - Mastodon: slightly more formal, technical audience
5. **Stay under the limit.** Bluesky 300 chars, Mastodon 500.

### Anti-patterns

- "Check out my latest post on X" (meta)
- "In this article, I explore..." (academic tone for social)
- Including the URL in the rewrite text (crier adds it)
- Generic summaries that could describe any article

### Good example

Article: "pagevault: Hiding an Encryption Platform Inside HTML"
Bluesky rewrite: "What if a single HTML file could encrypt anything you drop into it? No backend, no JS libraries. Just the browser's Web Crypto API and some careful engineering."

## Workflow

### Quick publish (single file)

1. `crier_check(file_path)` to validate
2. `crier_publish(file_path, platform, dry_run=True)` to preview
3. `crier_publish(file_path, platform, confirmation_token=...)` to execute
4. For short-form: read the article, write rewrite, pass as `rewrite_content`

### Audit and bulk publish

1. `crier_search(since="2w")` to find recent content
2. `crier_missing(platforms=["devto","hashnode","bluesky","mastodon"])` for gaps
3. For bulk work, dispatch the **cross-poster** agent
4. For analysis, dispatch the **auditor** agent

### Important rules

- DevTo sanitizes tags: no hyphens, max 4 tags, lowercase
- Medium is import-only: publish registers the URL, user must import manually
- Twitter/LinkedIn are paste-only: content goes to clipboard
- `--long-form` flag (CLI) or filter by `is_short_form` to skip social platforms
