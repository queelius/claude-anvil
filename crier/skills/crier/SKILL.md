---
name: crier
description: Cross-post blog content to social platforms. Claude handles audit, user selection, and generates rewrites for short-form platforms. Invoke from ANY repo — crier works globally via site_root config.
---

# Crier Cross-Posting Workflow

Crier cross-posts blog content to multiple platforms. The blog is the canonical source of truth.

**Division of labor:**
- **Crier** does mechanics: API calls, registry tracking, clipboard, browser
- **Claude** does judgment: summaries, error handling, user interaction

## Platform Reference

| Platform  | Mode   | Limit  | Updates? | Notes                          |
|-----------|--------|--------|----------|--------------------------------|
| devto     | API    | ∞      | Yes      | Tags auto-sanitized (no hyphens) |
| hashnode  | API    | ∞      | Yes      |                                |
| bluesky   | API    | 300    | No       | Short-form, needs rewrite      |
| mastodon  | API    | 500    | Yes      | Short-form, needs rewrite      |
| medium    | import | ∞      | No       | User imports from canonical URL |
| twitter   | paste  | 280    | No       | Short-form, copy-paste         |
| threads   | paste  | 500    | No       | Short-form, copy-paste         |
| linkedin  | paste  | ∞      | No       | Copy-paste                     |

**Modes:**
- `API` = automatic posting via API
- `import` = user imports from canonical URL (like Medium)
- `paste` = user copy-pastes (content goes to clipboard)

## Configuration

Crier uses a single global config file. No local config, no `--project` flag.

### Global Config (`~/.config/crier/config.yaml`)

```yaml
# Where the content project lives (for registry + resolving relative content_paths)
site_root: ~/github/repos/metafunctor

# Content discovery
content_paths:
  - content/post
site_base_url: https://metafunctor.com
exclude_patterns:
  - _index.md
file_extensions:
  - .md

# Defaults
default_profile: everything
rewrite_author: claude-code

# API keys
platforms:
  bluesky:
    api_key: handle:app-password
  devto:
    api_key: ...

# Publishing profiles
profiles:
  blogs:
    - devto
    - hashnode
    - medium
  social:
    - bluesky
    - mastodon
  everything:
    - blogs
    - social
```

**Key points:**
- `site_root` tells crier where the content project and registry live
- Registry is at `<site_root>/.crier/registry.yaml`
- Content paths resolve relative to `site_root`
- Works from any directory — no need to `cd` to the project
- Precedence: **global config < env vars < CLI args**
- Override config path: `CRIER_CONFIG` env var
- Override API keys: `CRIER_{PLATFORM}_API_KEY` env vars

## Checking Publication Status

Before cross-posting, check what's already published:

```bash
# Single file status
crier status content/post/2026-02-13-slug/index.md

# What needs publishing
crier audit                     # All content
crier audit content/post        # Just posts
crier audit --since 1w          # Last week

# Site-wide registry overview (no API calls)
crier summary
crier summary --json

# Check API keys are working
crier doctor
```

## Typical Workflow (Cross-Posting from Any Repo)

The common pattern: you're working in a project repo (not the blog repo), write a blog post about it, then cross-post. Crier works globally via `site_root`, so no need to switch directories.

```
1. Write/update blog post in metafunctor repo
2. Run audit to see what needs posting
3. Publish to long-form platforms (devto, hashnode)
4. Write short-form rewrites and publish (bluesky, mastodon)
5. Link the content file to fix registry paths (if published from temp files)
```

### Step-by-step

```bash
# 1. Check what needs posting
crier audit content/post/2026-02-13-my-article/index.md

# 2. Publish to long-form (uses the actual content file)
crier publish content/post/2026-02-13-my-article/index.md --to devto
crier publish content/post/2026-02-13-my-article/index.md --to hashnode

# 3. For short-form, Claude writes rewrites and publishes via --rewrite
crier publish content/post/2026-02-13-my-article/index.md --to bluesky \
  --rewrite "Hook text about the interesting insight" --rewrite-author "claude-code"
crier publish content/post/2026-02-13-my-article/index.md --to mastodon \
  --rewrite "Slightly longer summary with #hashtags" --rewrite-author "claude-code"

# 4. If temp files were used for publishing, link the real content file
crier link content/post/2026-02-13-my-article/index.md \
  --url https://metafunctor.com/post/2026-02-13-my-article/

# 5. Verify audit is clean
crier audit content/post/2026-02-13-my-article/index.md
```

**When to use `crier link`:** If you published using temp files (e.g., `/tmp/claude/crier-devto.md` for platform-specific versions), the registry records those temp paths. `crier link` fixes the `source_file`, `content_hash`, and `section` to point at the real content file so audit works correctly.

## Complete Dialogue Examples

### Example 1: Cross-post a new article

```
User: cross-post my new blog post to the usual platforms

Claude: I'll cross-post content/post/2026-01-04-my-article/index.md

Let me check what's needed:
[runs: crier audit content/post/2026-01-04-my-article/index.md]

Platforms to post:
- devto (API) - will auto-post
- hashnode (API) - will auto-post
- bluesky (API, 300 chars) - I'll write a summary
- mastodon (API, 500 chars) - I'll write a summary
- medium (import) - you'll import from your URL

Proceed?

User: yes

Claude: [runs API posts for devto, hashnode]
[generates summaries and posts to bluesky, mastodon with --rewrite]

Done:
- devto: https://dev.to/user/my-article-abc
- hashnode: https://user.hashnode.dev/my-article
- bluesky: posted announcement
- mastodon: posted announcement

For Medium, import from your canonical URL:
https://yourblog.com/post/2026-01-04-my-article/

Go to: https://medium.com/p/import

[runs: crier publish article.md --to medium --yes]

Did you import to Medium successfully?

User: yes

Claude: All platforms complete.
```

### Example 2: Handling short-form platforms

```
User: post this to bluesky

Claude: [runs: crier publish article.md --to bluesky]

Error: Content too long for bluesky: 5000 characters (limit: 300)

I'll write a short announcement:

"New post: Exploring the mathematics of uncertainty - how
probabilistic thinking can transform how we approach
complex problems."

(198 chars + URL = within limit)

[runs: crier publish article.md --to bluesky \
  --rewrite "New post: Exploring..." --rewrite-author "claude-code"]

bluesky: https://bsky.app/profile/user/post/abc123
```

### Example 3: Import mode (Medium)

```
User: post to medium

Claude: Medium uses URL import. I'll set this up:

[runs: crier publish article.md --to medium --yes]

Import your article from this URL:
https://yourblog.com/post/2026-01-04-my-article/

Go to: https://medium.com/p/import

Did the import work?

User: yes

Claude: Registered in crier. Done!
```

### Example 4: Manual paste mode (Twitter)

```
User: share on twitter

Claude: Twitter uses copy-paste mode.

[runs: crier publish article.md --to twitter --yes]

I've copied this to your clipboard:
"New post: My Article Title - exploring key concepts...

https://yourblog.com/post/my-article/"

Go to: https://twitter.com/compose/tweet

Did you post it?

User: yes

Claude: Registered. All done!
```

## Workflow Decision Tree

### User wants to cross-post

1. **Audit first**: `crier audit <file>` or `crier audit` for all content
2. **Show platforms**: List what will happen for each platform
3. **Get confirmation**: Simple "Proceed?" - trust the user
4. **Execute by type**:
   - API long-form: `crier publish <file> --to <platform>`
   - API short-form: Generate summary, use `--rewrite`
   - Import mode: `crier publish ... --to medium --yes`, tell user to import
   - Paste mode: `crier publish ... --to twitter --yes`, tell user to paste
5. **Report results**: Show all successes, ask about manual platforms

### User says something changed

1. Run `crier audit` to see dirty markers
2. For platforms that support update: re-run publish (auto-updates)
3. For platforms without update (bluesky, twitter): tell user they must delete/repost manually

### Failure handling

- Continue through all platforms even if some fail
- Report all failures at the end
- Don't ask user to retry - just report what happened

## Writing Rewrites

You ARE the rewriter. Don't use --auto-rewrite in interactive Claude Code sessions.

### Rewrite Guidelines by Platform

| Platform | Limit | Voice | Format |
|----------|-------|-------|--------|
| Bluesky  | 300   | Conversational, personal | Hook + key insight. No hashtags. |
| Mastodon | 500   | Slightly more detailed   | Can include 2-3 hashtags at end. |
| Twitter  | 280   | Punchy, provocative      | Can thread for longer content. |
| Threads  | 500   | Casual, exploratory      | Like talking to a friend. |
| LinkedIn | ∞     | Professional, structured | 3-4 paragraphs, accomplishment-framed. |

### Rewrite Process

1. Read the full post (or at least title + description + first few paragraphs)
2. Identify the single most interesting or surprising insight
3. Write the rewrite around that insight — not a generic summary
4. Show the user before posting — they may want to adjust tone
5. Pass to crier via `--rewrite`

### Anti-Patterns

- "New blog post: [title]" — boring, no hook
- "I wrote about X" — self-referential
- "Check out my latest..." — generic call-to-action
- Summarizing the entire post — pick ONE angle
- Including the URL in your rewrite — crier appends it automatically

### Good Rewrites Lead with the Insight

- "TIL Bloom filters can give false positives but never false negatives — and the math behind why is beautiful."
- "What if the problem isn't the algorithm but the loss function?"
- "After 4 years of building 120+ open-source projects, I finally mapped how they all connect."

### When to Use --auto-rewrite Instead

| Situation | Use |
|-----------|-----|
| Interactive Claude session | Claude writes rewrite, passes via `--rewrite` |
| Batch/bulk posting (10+ items) | `--auto-rewrite` for throughput |
| User says "just post it" | `--auto-rewrite` as shortcut |
| User cares about quality | Claude writes it, shows for approval |

## Interpreting Audit Scope

The `crier audit` command scans all directories in `content_paths` by default. Users often want to scope to specific content types.

**Reading user intent:**

| User says... | Likely scope |
|--------------|--------------|
| "last month of content", "recent content", "what needs posting" | All content (`crier audit --since 1m`) |
| "blog posts", "posts", "articles" | `crier audit content/post` |
| "projects" | `crier audit content/projects` |
| "papers", "research" | `crier audit content/papers` |

**When uncertain:**
- Run `crier config show` to see configured content paths
- Make a reasonable choice based on available clues
- If wrong, the user will clarify

## Key Commands

```bash
# Check what needs publishing
crier audit
crier audit content/post/my-article/index.md

# Publish to API platform
crier publish article.md --to devto

# Publish with rewrite for short-form
crier publish article.md --to bluesky \
  --rewrite "Short announcement text" \
  --rewrite-author "claude-code"

# Import/paste mode (skips interactive prompts)
crier publish article.md --to medium --yes
crier publish article.md --to twitter --yes

# Registry summary (no API calls)
crier summary
crier summary --json

# Check API keys
crier doctor

# Manual registry management
crier register <file> --platform <platform> [--url <url>]
crier unregister <file> --platform <platform>

# Link content file to registry (fix source_file after temp-file publishing)
crier link <file> --url <canonical_url>
crier link <file>  # uses canonical_url from front matter
```

## Bulk Operations

For large content libraries, use filters to control scope:

```bash
# Post 5 random articles to blog platforms (fully automated)
crier audit --publish --yes --only-api --long-form --sample 5

# All missing to API platforms (skips manual/import)
crier audit --publish --yes --only-api

# Include updates to changed content
crier audit --publish --yes --include-changed

# Filter by path - only posts (not projects, papers, etc.)
crier audit content/post --publish --yes --only-api --long-form --sample 5

# Posts from last week
crier audit --since 1w --publish --yes --only-api

# Sample 5 recent posts (last month)
crier audit --sample 5 --since 1m --only-api --long-form

# Fully automated batch mode (implies --yes --json, skips manual)
crier audit --publish --batch --long-form
```

### Filters
- `[PATH]` — Limit to specific directory (e.g., `content/post`, `content/projects`)
- `--since` — Only content from this date (e.g., `1d`, `1w`, `1m`, `2025-01-01`)
- `--until` — Only content until this date
- `--only-api` — Skip manual/import/paste platforms
- `--long-form` — Skip short-form platforms (bluesky, mastodon, twitter, threads)
- `--sample N` — Random sample of N items
- `--include-changed` — Also update changed content (default: missing only)

## Front Matter Requirements

```yaml
---
title: "Your Article Title"
canonical_url: "https://yourblog.com/your-article/"
---
```

The `canonical_url` is required — it's the article's identity for tracking and linking.

## Section Tracking

Crier automatically tracks the content section (e.g., `post`, `papers`, `projects`) for each registered article, inferred from the source file path. This powers the `crier summary` breakdown by section. No configuration needed.

## Important Rules

1. **Crier appends the canonical URL** to short-form posts automatically. Don't include it in your rewrite text.
2. **DevTo tags are auto-sanitized**. Hyphens removed, lowercase, max 4 tags. No action needed.
3. **Use --yes for non-API modes**. This skips interactive prompts that don't work through Claude Code.
4. **Ask simple yes/no** after manual operations. Trust the user's answer.
5. **Show the canonical URL** for import-mode platforms. It's the key piece of information.
