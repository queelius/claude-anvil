---
name: chronicler
description: Weekly catch-up on cross-posting. Scans recent metafunctor posts, finds platform gaps, proposes cross-posts with rewrites for short-form. Opinionated defaults so you don't have to choose.
---

# /chronicler

Run when you remember (Friday afternoon, end of month, after a posting spree). The goal is to make "did I cross-post the recent stuff?" a one-prompt workflow.

## Scope

Default: posts from the last `2w`, all configured API platforms.

Override via argument: `/chronicler 1m`, `/chronicler 3d`, `/chronicler 6w`. Anything `crier_search` accepts as `since`.

Configured API platforms are usually `devto`, `hashnode`, `bluesky`, `mastodon`. Skip platforms in `import` mode (medium) or `paste` mode (twitter, threads, linkedin), they need browser/clipboard.

## Workflow

### 1. Scan

Run `crier_search(since=<scope>)` to get recent files with metadata.

For each file, check status with `crier_article(<canonical_url_or_file>)`. Note which platforms it's missing from.

Also run `crier_missing(platforms=[devto, hashnode, bluesky, mastodon])` to catch tracked-but-incomplete posts.

Skip:
- Files with `draft: true` in front matter
- Files already on all 4 configured platforms
- Files where `crier_check` reports errors (broken, missing title, etc.)

### 2. Build proposals

For each candidate post, draft the cross-post plan:

- **Long-form platforms** (devto, hashnode): no rewrite needed, use the full body.
- **Short-form platforms** (bluesky, mastodon): generate a rewrite. Read the article first (use `Read` tool on the source file), then write a rewrite that:
  - Leads with the most specific or provocative claim. **Not** "I wrote a post about X."
  - Stays under the budget: **bluesky ~280 chars** (the canonical URL eats ~80), **mastodon ~460**.
  - Contains no canonical URL: crier appends it automatically.
  - Doesn't say "new blog post" or "check out my latest." Just say the thing.
  - Can be more nuanced on mastodon than bluesky. Bluesky is one punch.

### 3. Present an opinionated proposal

Format the user-facing summary like this. Keep it dense:

```
3 posts to cross-post (8 platform actions total):

1. "Intelligence is a Shape, Not a Scalar" (2026-04-05, 2393w)
   → devto, hashnode (full body)
   → bluesky (271 chars):
     "Chollet says intelligence is a ball that's already round. Wrong. It's a shape:
      every architecture trades performance on some problems for performance on others."
   → mastodon (442 chars):
     "Chollet says intelligence is like a ball that's already pretty round. He's right
      it's not a scalar. Wrong about the ball. ..."

2. "Posthumous: A Federated Dead Man's Switch" (2026-02-14, 1298w)
   → devto, hashnode (full body)
   → bluesky (already posted)
   → mastodon (236 chars): "..."

3. "dapple: Terminal Graphics, Composed" (2026-02-15, 1033w)
   ...

Approve all (a) | Approve some (e.g. 1,3) | Edit rewrite (e <num> <platform>) | Skip <num> (s <num>) | Abort (q)
```

### 4. Execute

For each approved item × platform:

1. Long-form: `crier_publish(file, platform)` for step 1, `crier_publish(file, platform, confirmation_token=...)` for step 2.
2. Short-form: `crier_publish(file, platform, rewrite_content=<rewrite>, rewrite_author="claude-code")` for step 1, then step 2 with token.

Run platforms in parallel where possible (single message, multiple tool calls).

If a publish fails (length, API error), report it but continue with the others. Don't abort the batch.

### 5. Report

Final summary table. Include URLs for successes, error messages for failures.

```
Cross-posted:
  Intelligence is a Shape   devto: https://dev.to/...   hashnode: https://...   bluesky: https://...   mastodon: https://...
  Posthumous                devto: https://dev.to/...   hashnode: https://...   bluesky: (already)      mastodon: https://...
  dapple                    devto: ✓   hashnode: ✗ (rate limited, retry later)   bluesky: ✓   mastodon: ✓

Failures (1):
  dapple → hashnode: API rate limit

Run again with /chronicler to retry.
```

## Important rules

- **Never auto-publish without explicit approval.** If the user doesn't respond clearly, abort.
- **Group by post in the proposal**, not by platform. One item per post even if it's missing 4 platforms.
- **If the count is large** (more than ~5 posts to publish, or more than ~15 platform actions), suggest dispatching the `cross-poster` agent instead: "That's 23 platform actions. Want me to dispatch the cross-poster agent to run autonomously, or step through each one with you?"
- **Skip already-posted platforms.** Don't propose re-posts. The MCP tools handle deduplication, but the proposal should never list "→ devto (already)" as an action.
- **Quality bar for rewrites**: if the rewrite is bland or just summarizes the title, regenerate it. The user will catch this anyway, but you should catch it first.

## Mode shortcuts

- `/chronicler --dry` or just looking at proposals without executing: run steps 1–3, stop after presenting. The user can copy any rewrite and run it manually with `crier publish` if they want.
- `/chronicler --long-form` or `/chronicler longform`: only propose devto + hashnode, skip social. Useful when batching technical posts.
- `/chronicler --short-form` or `/chronicler social`: only propose bluesky + mastodon. Useful when you've already done long-form via the web UIs.

## When to use other crier capabilities instead

- **One specific post, all platforms**: just use `/crier <file>`.
- **Bulk publishing 20+ posts autonomously**: dispatch the `cross-poster` agent.
- **"What should I cross-post?" without a date scope**: use the `auditor` agent for analysis-driven recommendations.
- **Re-running failures**: `crier audit --retry` (CLI) or `crier_failures` (MCP) then targeted `crier_publish`.
