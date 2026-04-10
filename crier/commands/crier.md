---
name: crier
description: Cross-post blog content to platforms. Audits what needs publishing and guides through the workflow using MCP tools.
---

# /crier

Run a cross-posting workflow for blog content.

## Steps

1. **Check status**: Use `crier_search(since="1m")` and `crier_missing(platforms=["devto","hashnode","bluesky","mastodon"])` to find what needs publishing. If the user provided arguments (like a date range or platform), adjust accordingly.

2. **Summarize**: Show the user what needs publishing, grouped by content item and platform. Highlight:
   - How many items are unposted
   - Which platforms are API (automatic) vs manual/import
   - Which platforms need short-form rewrites

3. **Get scope**: Ask the user what they want to publish:
   - Everything shown?
   - A specific file?
   - Only certain platforms?
   - Only long-form? Only short-form?

4. **Execute**: For the chosen scope:
   - **API long-form** (devto, hashnode): `crier_publish(file, platform)` with confirmation
   - **API short-form** (bluesky, mastodon): Read article, write a rewrite, then `crier_publish(file, platform, rewrite_content=..., rewrite_author="claude-code")`
   - **Import** (medium): Note the canonical URL for manual import
   - **Paste** (twitter, threads, linkedin): Use CLI `crier publish --to <platform> --yes`

5. **Report**: Show results for all platforms.

## Tips

- Use the `crier` skill for rewrite guidelines and platform voice
- For bulk operations with many items, dispatch the **cross-poster** agent
- For analysis (gap analysis, performance review), dispatch the **auditor** agent
- When writing rewrites, lead with the most interesting insight
- Crier appends the canonical URL automatically
