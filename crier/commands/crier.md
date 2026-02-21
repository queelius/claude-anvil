---
name: crier
description: Cross-post blog content to platforms. Runs audit, shows what needs publishing, and guides through the workflow.
---

# /crier — Cross-Post Content

Run a cross-posting workflow for blog content.

## Steps

1. **Check status**: Run `crier audit --since 1m` to see what needs publishing recently. If the user provided arguments (like a file path or `--since 2w`), use those instead.

2. **Summarize**: Show the user what needs publishing, grouped by content item and platform. Highlight:
   - How many items are unposted
   - Which platforms are API (automatic) vs manual/import
   - Which platforms need short-form rewrites

3. **Get scope**: Ask the user what they want to publish:
   - Everything shown?
   - A specific file?
   - Only certain platforms?
   - Only API platforms? (`--only-api`)

4. **Execute**: For the chosen scope:
   - **API long-form** (devto, hashnode): `crier publish <file> --to <platform> --yes`
   - **API short-form** (bluesky, mastodon): Read the article, write a rewrite, then `crier publish <file> --to <platform> --rewrite "<text>" --rewrite-author "claude-code" --yes`
   - **Import** (medium): `crier publish <file> --to medium --yes`, show the canonical URL and import link
   - **Paste** (twitter, threads, linkedin): `crier publish <file> --to <platform> --yes`, tell user to paste

5. **Report**: Show results for all platforms. Ask about manual/import platforms if applicable.

## Tips

- Use the `crier` skill for platform reference (limits, modes, rewrite guidelines)
- For bulk operations with many items, consider dispatching the `cross-poster` agent
- When writing rewrites, lead with the most interesting insight — don't just summarize
- Crier appends the canonical URL automatically — don't include it in rewrites
