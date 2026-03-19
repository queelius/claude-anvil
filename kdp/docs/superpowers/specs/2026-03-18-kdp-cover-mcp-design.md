# KDP Cover Generation MCP + Dashboard Automation

**Date**: 2026-03-18
**Status**: Draft
**Scope**: KDP plugin enhancement, cover generation MCP server + Playwright-driven dashboard submission

## Problem

The KDP plugin's `kdp-publish` skill walks users through 10 phases of book publishing, but Phases 6-9 (cover preparation, dashboard submission, pricing, publish) are entirely manual. The skill prints instructions and the user clicks buttons on `kdp.amazon.com`. This is tedious, error-prone, and doesn't scale to publishing many books (series, spin-offs, frequent updates to existing titles).

Cover creation is also a separate manual process requiring external design tools.

## Solution

Two changes to the KDP plugin:

1. **Cover Generation MCP**: A TypeScript MCP server (3 tools) that generates front covers via OpenAI image generation and composites full paperback wraps programmatically.

2. **Playwright-driven dashboard submission**: Update `kdp-publish` skill to use the existing Playwright MCP to navigate `kdp.amazon.com`, fill forms, upload files, and get the user to the review screen. No custom browser automation code. Claude reads the page live and adapts.

## Architecture

### What handles what

| Concern | Owner |
|---------|-------|
| Cover art generation (front cover with typography) | New MCP → OpenAI image API (GPT-image-1) |
| Full paperback wrap (front + spine + back) | New MCP → image compositing (sharp + pdf-lib) |
| Cover dimension calculations | New MCP → `kdp_cover_specs` tool |
| KDP dashboard navigation, form-filling, file uploads | Existing Playwright MCP + Claude intelligence |
| Orchestration, decision-making, user interaction | `kdp-publish` skill |
| State (ASINs, metadata, listing artifacts, cover paths) | `.claude/kdp.local.md` |

### Key design decision: no custom browser automation

The KDP dashboard is driven by Claude using the existing Playwright MCP tools (`browser_navigate`, `browser_snapshot`, `browser_fill_form`, `browser_click`, `browser_file_upload`). Claude reads each page, understands what's on screen, and interacts with it adaptively. No hardcoded DOM selectors, no page objects, no recorded flows. Amazon changes their dashboard UI? Claude just reads the new page.

This means the custom MCP server is small and focused: it only handles cover generation and image processing, which genuinely need code (API calls, pixel math, PDF output).

## MCP Server Tools

### `kdp_generate_cover`

Generate a complete front cover image with artwork, title, and author name.

**Input**:
- `title` (string, required): book title
- `subtitle` (string, optional): book subtitle
- `author_name` (string, required): author/pen name
- `genre` (string, required): e.g., "epic fantasy", "thriller", "technical"
- `art_direction` (string, optional): user's description of desired cover art (e.g., "dark moody forest with a glowing rune"). If omitted, a genre-appropriate prompt is constructed.
- `width` (number, default 1600): pixel width (portrait orientation)
- `height` (number, default 2560): pixel height. Default produces a 1.6:1 height-to-width ratio (KDP eBook standard). All dimensions are width x height in portrait orientation.

**Output**: `{ path: string }`, path to generated cover image (PNG)

**Implementation**: Constructs a prompt that includes the title text, author name, genre conventions, and art direction. Calls OpenAI GPT-image-1 which renders the complete cover including typography. The model handles text rendering directly, so no separate text compositing step is needed for the front cover.

The skill can call this tool multiple times for iteration ("try a different style", "make it darker", "different font").

### `kdp_generate_full_wrap`

Composite a full paperback cover: front + spine + back.

**Input**:
- `front_cover_path` (string, required): path to approved front cover image
- `title` (string, required): for spine text
- `author_name` (string, required): for spine text
- `blurb` (string, required): back cover text
- `page_count` (number, required): for spine width calculation
- `trim_size` (string, default "5.5x8.5"): e.g., "5.5x8.5", "6x9"
- `paper_type` (string, default "cream"): "white" or "cream"
- `isbn` (string, optional): if provided, barcode zone is marked on back cover
- `back_color` (string, optional): hex color for back cover background. If omitted, extracted from front cover dominant color.

**Output**: `{ pdf_path: string, preview_path: string, specs: CoverSpecs }`. Returns both the full-wrap PDF (for KDP upload) and a rasterized PNG preview (for quick visual verification in the terminal).

**Implementation**:
1. Parse trim size into width/height in inches
2. Calculate spine width: `(page_count * paper_multiplier) + 0.06"` (white=0.002252"/page, cream=0.0025"/page)
3. Calculate total cover dimensions at 300 DPI with 0.125" bleed on all sides
4. Layout zones: back cover (left) | spine (center) | front cover (right)
5. Place front cover image in the front zone, scaled to fit
6. Render spine text (title + author, rotated 90 degrees clockwise per US publishing convention, reading top-to-bottom) if page count >= 130 (spine width >= 0.3"). For narrow spines (0.3"-0.5"), use title only (no author name) at a small font size.
7. Render back cover using `pdf-lib` for text layout: solid background color, blurb text (centered, readable serif font bundled with the package). If the auto-extracted back color has insufficient contrast with white text (WCAG AA ratio < 4.5:1), darken it automatically. Barcode zone: 2" x 1.2" clear rectangle in lower-right corner (KDP overlays the barcode here when using free ISBN). Blurb text is truncated with ellipsis if it exceeds the available space after accounting for margins and barcode zone.
8. Output as PDF at exact calculated dimensions

Uses `sharp` for image processing and `pdf-lib` for PDF generation.

### `kdp_cover_specs`

Calculate cover dimensions without generating anything.

**Input**:
- `page_count` (number, required)
- `trim_size` (string, default "5.5x8.5")
- `paper_type` (string, default "cream")

**Output**: JSON with:
- `spine_width_inches` : calculated spine width
- `total_width_inches` / `total_height_inches` : full wrap dimensions (with bleed)
- `total_width_px` / `total_height_px` : at 300 DPI
- `front_zone` / `spine_zone` / `back_zone` : { x, y, width, height } in pixels
- `bleed_inches` : 0.125
- `has_spine_text` : boolean (true if page_count >= 130)

Useful for checking dimensions before generating, or verifying an existing cover.

## Skill Updates

### Phase 6 (Cover Preparation), now automated

**Before**: Tells user to check cover dimensions and recommends hiring a designer.

**After**:
1. Check if cover already exists (saved path in config or cover file in project)
2. If no cover → ask user for art direction (or use genre + title to suggest a direction)
3. Call `kdp_generate_cover` with the inputs
4. Show the generated cover to the user by reading the image file (Claude Code renders images inline in the terminal). Iterate ("like it? try another style?")
5. Once approved, save front cover path to config
6. If paperback target → call `kdp_cover_specs` to show dimensions, then `kdp_generate_full_wrap`
7. Save full-wrap path to config

### Phase 7 (Dashboard Submission), now Playwright-driven

**Before**: Prints 10 step-by-step manual instructions.

**After**:
1. `browser_navigate` to `kdp.amazon.com`
2. `browser_snapshot` to check login state. If not authenticated, tell user to log in, wait until dashboard is visible
3. **New title**: navigate to "Create New Title", select format (eBook/paperback)
4. **Update**: navigate to bookshelf, find title by stored ASIN (direct URL) or search by title name
5. `browser_snapshot` each form section, `browser_fill_form` / `browser_click` to fill: title, subtitle, author, series info, description (blurb), keywords, categories
6. `browser_file_upload` for manuscript file and cover image
7. Navigate through to the review/preview page
8. **Stop**. Tell user: "Everything's filled in. Review and click publish when ready."
9. After user publishes, attempt to capture the ASIN from the confirmation or bookshelf page. If the ASIN is not yet available (books enter a 24-72 hour review queue), note this and instruct the user to run `/kdp-publish` again later to capture it.
10. Write ASIN back to `.claude/kdp.local.md` when available.

### Phase 8 (Pricing), semi-automated

Pricing involves user decisions (royalty tier, KDP Select, territories, price point). The skill presents options conversationally, user decides, then Playwright fills in the pricing form fields.

### Phases 1-5, 9-10 (unchanged)

These phases (assess state, audit, listing, pre-orders, manuscript prep, post-publish) don't involve the KDP dashboard or cover generation. No changes needed.

## Project Structure

```
kdp/
├── .claude-plugin/plugin.json     # version bump
├── .mcp.json                      # registers kdp-cover MCP server
├── mcp/
│   ├── package.json               # @modelcontextprotocol/sdk, openai, sharp, pdf-lib, tsx
│   ├── tsconfig.json
│   └── src/
│       ├── index.ts               # MCP server entry, tool registration
│       ├── tools/
│       │   ├── generate-cover.ts      # kdp_generate_cover
│       │   ├── generate-full-wrap.ts  # kdp_generate_full_wrap
│       │   └── cover-specs.ts         # kdp_cover_specs
│       └── lib/
│           ├── cover-layout.ts    # spine width math, zone calculations, bleed
│           └── openai-client.ts   # OpenAI API wrapper (reads OPENAI_API_KEY from env)
├── skills/
│   ├── kdp-publish/SKILL.md       # updated: Phases 6-8 use Playwright + MCP tools
│   ├── kdp-audit/SKILL.md         # unchanged
│   └── kdp-listing/SKILL.md       # unchanged
├── commands/                       # unchanged
├── docs/                           # unchanged
└── CLAUDE.md                       # updated: documents MCP component
```

### MCP Registration (`.mcp.json`)

```json
{
  "mcpServers": {
    "kdp-cover": {
      "command": "npx",
      "args": ["tsx", "${CLAUDE_PLUGIN_ROOT}/mcp/src/index.ts"],
      "env": {
        "OPENAI_API_KEY": "${OPENAI_API_KEY}"
      }
    }
  }
}
```

## Config Changes

New fields added to `.claude/kdp.local.md` YAML frontmatter:

```yaml
kdp:
  # ... existing fields (genre, series, trim_size, paper_type, target,
  #     categories, keywords, blurb, author_bio) ...
  asin: null                       # eBook ASIN, saved after first publish
  asin_paperback: null             # paperback ASIN, saved after first publish
  cover:
    front: null                    # path to approved front cover image
    full_wrap: null                # path to full-wrap PDF (paperback)
    art_direction: ""              # user's cover art prompt/description
    color_scheme: null             # back cover color (hex, or auto-extracted)
  manuscript:
    path: null                     # path to final manuscript file for upload
```

The `user-config-template.md` is updated to include these fields with documentation.

**Migration**: Existing `kdp.local.md` files without the new fields work without changes. The skill treats missing fields as null/empty and offers to populate them during the workflow. No explicit migration step needed.

## Dependencies

**Runtime**:
- `@modelcontextprotocol/sdk` : MCP server framework
- `openai` : OpenAI API client (GPT-image-1 for cover generation)
- `sharp` : image processing (resize, composite, color extraction)
- `pdf-lib` : PDF generation (full-wrap cover output)
- `tsx` : run TypeScript directly without build step

**Environment**:
- `OPENAI_API_KEY` : user's existing OpenAI API key (passed via `.mcp.json` env)
- Playwright MCP : already installed in user's Claude Code setup

**No build step**: The MCP server runs via `npx tsx`, no compilation needed. This keeps the plugin simple. `npm install` in `mcp/` is the only setup.

### Setup and Installation

This is the first plugin in the marketplace with runtime dependencies. The setup workflow:

1. After plugin installation, the `kdp-publish` skill checks for `node_modules` in the MCP directory on first use
2. If missing, the skill runs `npm install` in the `mcp/` directory automatically (with user confirmation)
3. If Node.js is not available, the skill falls back to the manual workflow (Phases 6-8 revert to instructions) and tells the user what to install

The `.mcp.json` config uses `${CLAUDE_PLUGIN_ROOT}` for the server path. This variable must be verified to expand correctly in `.mcp.json` files during implementation. If it does not expand, the fallback is to use a wrapper script (`mcp/run.sh`) that resolves the path relative to its own location:

```bash
#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
exec npx tsx "$DIR/src/index.ts"
```

And `.mcp.json` would reference: `"args": ["${CLAUDE_PLUGIN_ROOT}/mcp/run.sh"]`

### Error Handling

**OpenAI API**:
- Missing or invalid `OPENAI_API_KEY`: tool returns a structured error with a message explaining how to set the key
- Content policy rejection: tool returns the rejection reason so the skill can suggest modified art direction
- Misspelled title text in generated image: the skill shows the image and asks the user to verify text accuracy before proceeding. If text is wrong, regenerate.

**Cost transparency**: The skill informs the user of approximate cost per generation before the first `kdp_generate_cover` call (currently ~$0.04-0.08 per image for GPT-image-1). Each iteration is a separate API call.

## Scope Boundaries

**In scope**:
- 3 MCP tools for cover generation and compositing
- Skill updates for Phases 6-8 to use Playwright + MCP tools
- Config schema additions (ASINs, cover paths, art direction)
- `.mcp.json` registration

**Out of scope**:
- KDP account setup automation (tax interview, bank details, too sensitive)
- Final publish click (user does this manually after review)
- Hardcover format (paperback + eBook only for now)
- Amazon Ads / marketing automation
- Multi-account support
