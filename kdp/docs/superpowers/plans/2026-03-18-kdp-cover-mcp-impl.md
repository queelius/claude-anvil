# KDP Cover Generation MCP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a 3-tool TypeScript MCP server for KDP cover generation and compositing, then update the kdp-publish skill to use Playwright MCP for dashboard automation.

**Architecture:** A lightweight TypeScript MCP server in `kdp/mcp/` exposes three tools: `kdp_generate_cover` (OpenAI image API), `kdp_generate_full_wrap` (sharp + pdf-lib compositing), and `kdp_cover_specs` (dimension calculator). The `kdp-publish` skill orchestrates these tools alongside the existing Playwright MCP for KDP dashboard interaction. No custom browser automation code.

**Tech Stack:** TypeScript, `@modelcontextprotocol/sdk`, `openai`, `sharp`, `pdf-lib`, `tsx`, `vitest` (testing)

**Spec:** `docs/superpowers/specs/2026-03-18-kdp-cover-mcp-design.md`

---

## File Map

### New files (MCP server)
| File | Responsibility |
|------|---------------|
| `mcp/package.json` | Dependencies and scripts |
| `mcp/tsconfig.json` | TypeScript config (strict, ESM) |
| `mcp/src/index.ts` | MCP server entry point, tool registration |
| `mcp/src/lib/cover-layout.ts` | Spine width math, zone calculations, bleed, contrast checking |
| `mcp/src/lib/openai-client.ts` | OpenAI API wrapper, prompt construction |
| `mcp/src/tools/cover-specs.ts` | `kdp_cover_specs` tool handler |
| `mcp/src/tools/generate-cover.ts` | `kdp_generate_cover` tool handler |
| `mcp/src/tools/generate-full-wrap.ts` | `kdp_generate_full_wrap` tool handler |
| `mcp/src/test/cover-layout.test.ts` | Unit tests for dimension calculations |
| `mcp/src/test/cover-specs.test.ts` | Unit tests for cover-specs tool |
| `mcp/src/test/generate-cover.test.ts` | Unit tests for cover generation (mocked OpenAI) |
| `mcp/src/test/generate-full-wrap.test.ts` | Unit tests for full-wrap compositing |
| `mcp/run.sh` | Wrapper script (fallback if `${CLAUDE_PLUGIN_ROOT}` doesn't expand in .mcp.json) |

### New files (plugin config)
| File | Responsibility |
|------|---------------|
| `.mcp.json` | MCP server registration |

### Modified files
| File | What changes |
|------|-------------|
| `skills/kdp-publish/SKILL.md` | Phases 6-8 rewritten to use MCP tools + Playwright |
| `docs/user-config-template.md` | New fields: asin, cover, manuscript |
| `.claude-plugin/plugin.json` | Version bump |
| `CLAUDE.md` | Document MCP component |

---

## Task 1: Project scaffolding

**Files:**
- Create: `mcp/package.json`
- Create: `mcp/tsconfig.json`
- Create: `mcp/run.sh`

- [ ] **Step 1: Create package.json**

```json
{
  "name": "kdp-cover-mcp",
  "version": "0.1.0",
  "type": "module",
  "private": true,
  "scripts": {
    "start": "tsx src/index.ts",
    "test": "vitest run",
    "test:watch": "vitest"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.12.0",
    "openai": "^4.90.0",
    "pdf-lib": "^1.17.1",
    "sharp": "^0.33.0",
    "zod": "^3.24.0"
  },
  "devDependencies": {
    "@vitest/coverage-v8": "^3.1.0",
    "tsx": "^4.19.0",
    "typescript": "^5.8.0",
    "vitest": "^3.1.0"
  }
}
```

Note: check latest versions of `@modelcontextprotocol/sdk` and `openai` before writing. Use `npm view <pkg> version` to get current latest.

- [ ] **Step 2: Create tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "strict": true,
    "esModuleInterop": true,
    "outDir": "dist",
    "rootDir": "src",
    "declaration": true,
    "sourceMap": true,
    "skipLibCheck": true
  },
  "include": ["src"]
}
```

- [ ] **Step 3: Create run.sh wrapper**

```bash
#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
[ -d "$DIR/node_modules" ] || { echo "Run 'npm install' in $DIR first" >&2; exit 1; }
exec npx tsx "$DIR/src/index.ts"
```

Make executable: `chmod +x mcp/run.sh`

- [ ] **Step 3b: Create .gitignore for mcp/**

```
node_modules/
dist/
```

- [ ] **Step 4: Install dependencies**

Run: `cd kdp/mcp && npm install`
Expected: `node_modules/` created, `package-lock.json` generated

- [ ] **Step 5: Verify TypeScript works**

Create a minimal `mcp/src/index.ts`:

```typescript
console.log("kdp-cover-mcp: scaffolding works");
```

Run: `cd kdp/mcp && npx tsx src/index.ts`
Expected: prints "kdp-cover-mcp: scaffolding works"

- [ ] **Step 6: Commit**

```bash
git add kdp/mcp/package.json kdp/mcp/package-lock.json kdp/mcp/tsconfig.json kdp/mcp/run.sh kdp/mcp/src/index.ts
git commit -m "feat(kdp): scaffold MCP server project with dependencies"
```

---

## Task 2: Cover layout library (pure math, no I/O)

**Files:**
- Create: `mcp/src/lib/cover-layout.ts`
- Create: `mcp/src/test/cover-layout.test.ts`

This is the core geometry engine. Pure functions, no side effects, easy to test.

- [ ] **Step 1: Write the failing tests**

```typescript
// mcp/src/test/cover-layout.test.ts
import { describe, it, expect } from "vitest";
import {
  calculateSpineWidth,
  calculateCoverDimensions,
  contrastRatio,
  ensureContrast,
} from "../lib/cover-layout.js";

describe("calculateSpineWidth", () => {
  it("calculates white paper spine width", () => {
    // 300 pages white: (300 * 0.002252) + 0.06 = 0.7356"
    const result = calculateSpineWidth(300, "white");
    expect(result).toBeCloseTo(0.7356, 4);
  });

  it("calculates cream paper spine width", () => {
    // 300 pages cream: (300 * 0.0025) + 0.06 = 0.81"
    const result = calculateSpineWidth(300, "cream");
    expect(result).toBeCloseTo(0.81, 4);
  });

  it("calculates minimum page count spine width", () => {
    // 24 pages white: (24 * 0.002252) + 0.06 = 0.1140"
    const result = calculateSpineWidth(24, "white");
    expect(result).toBeCloseTo(0.1140, 3);
  });
});

describe("calculateCoverDimensions", () => {
  it("calculates full wrap for 5.5x8.5 trim, 300 pages cream", () => {
    const dims = calculateCoverDimensions({
      pageCount: 300,
      trimSize: "5.5x8.5",
      paperType: "cream",
    });

    // spine = 0.81"
    expect(dims.spineWidthInches).toBeCloseTo(0.81, 2);

    // total width = back(5.5) + spine(0.81) + front(5.5) + bleed(0.25) = 12.06"
    expect(dims.totalWidthInches).toBeCloseTo(12.06, 2);

    // total height = 8.5 + bleed(0.25) = 8.75"
    expect(dims.totalHeightInches).toBeCloseTo(8.75, 2);

    // at 300 DPI
    expect(dims.totalWidthPx).toBe(Math.round(12.06 * 300));
    expect(dims.totalHeightPx).toBe(Math.round(8.75 * 300));

    // has spine text (300 pages > 130)
    expect(dims.hasSpineText).toBe(true);

    // zones should be defined
    expect(dims.backZone).toBeDefined();
    expect(dims.spineZone).toBeDefined();
    expect(dims.frontZone).toBeDefined();
  });

  it("marks no spine text for thin books", () => {
    const dims = calculateCoverDimensions({
      pageCount: 80,
      trimSize: "5.5x8.5",
      paperType: "white",
    });
    expect(dims.hasSpineText).toBe(false);
  });

  it("parses 6x9 trim size", () => {
    const dims = calculateCoverDimensions({
      pageCount: 200,
      trimSize: "6x9",
      paperType: "white",
    });
    expect(dims.totalHeightInches).toBeCloseTo(9.25, 2);
  });
});

describe("contrastRatio", () => {
  it("returns 21 for black on white", () => {
    expect(contrastRatio("#000000", "#ffffff")).toBeCloseTo(21, 0);
  });

  it("returns 1 for same colors", () => {
    expect(contrastRatio("#336699", "#336699")).toBeCloseTo(1, 0);
  });
});

describe("ensureContrast", () => {
  it("returns original color if contrast is sufficient", () => {
    // dark blue on white text has good contrast
    const result = ensureContrast("#1a1a2e", "#ffffff");
    expect(result).toBe("#1a1a2e");
  });

  it("darkens a light color that has poor contrast with white", () => {
    // light yellow on white has poor contrast
    const result = ensureContrast("#ffff99", "#ffffff");
    // result should be darker
    expect(contrastRatio(result, "#ffffff")).toBeGreaterThanOrEqual(4.5);
  });
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd kdp/mcp && npx vitest run src/test/cover-layout.test.ts`
Expected: FAIL (module not found)

- [ ] **Step 3: Implement cover-layout.ts**

```typescript
// mcp/src/lib/cover-layout.ts

const PAPER_MULTIPLIER = {
  white: 0.002252,
  cream: 0.0025,
} as const;

const BLEED_INCHES = 0.125;
const DPI = 300;
const MIN_SPINE_TEXT_PAGES = 130;

export type PaperType = "white" | "cream";

export interface Zone {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface CoverDimensions {
  spineWidthInches: number;
  totalWidthInches: number;
  totalHeightInches: number;
  totalWidthPx: number;
  totalHeightPx: number;
  bleedInches: number;
  hasSpineText: boolean;
  frontZone: Zone;
  spineZone: Zone;
  backZone: Zone;
  trimWidth: number;
  trimHeight: number;
}

export function calculateSpineWidth(
  pageCount: number,
  paperType: PaperType,
): number {
  return pageCount * PAPER_MULTIPLIER[paperType] + 0.06;
}

export function calculateCoverDimensions(opts: {
  pageCount: number;
  trimSize: string;
  paperType: PaperType;
}): CoverDimensions {
  const [trimWidthStr, trimHeightStr] = opts.trimSize.split("x");
  const trimWidth = parseFloat(trimWidthStr);
  const trimHeight = parseFloat(trimHeightStr);

  const spineWidth = calculateSpineWidth(opts.pageCount, opts.paperType);
  const totalWidthInches =
    trimWidth + spineWidth + trimWidth + BLEED_INCHES * 2;
  const totalHeightInches = trimHeight + BLEED_INCHES * 2;

  const totalWidthPx = Math.round(totalWidthInches * DPI);
  const totalHeightPx = Math.round(totalHeightInches * DPI);

  const bleedPx = Math.round(BLEED_INCHES * DPI);
  const spinePx = Math.round(spineWidth * DPI);
  const panelPx = Math.round(trimWidth * DPI);
  const panelHeightPx = Math.round(trimHeight * DPI);

  const backZone: Zone = {
    x: bleedPx,
    y: bleedPx,
    width: panelPx,
    height: panelHeightPx,
  };

  const spineZone: Zone = {
    x: bleedPx + panelPx,
    y: bleedPx,
    width: spinePx,
    height: panelHeightPx,
  };

  const frontZone: Zone = {
    x: bleedPx + panelPx + spinePx,
    y: bleedPx,
    width: panelPx,
    height: panelHeightPx,
  };

  return {
    spineWidthInches: spineWidth,
    totalWidthInches,
    totalHeightInches,
    totalWidthPx,
    totalHeightPx,
    bleedInches: BLEED_INCHES,
    hasSpineText: opts.pageCount >= MIN_SPINE_TEXT_PAGES,
    frontZone,
    spineZone,
    backZone,
    trimWidth,
    trimHeight,
  };
}

// WCAG relative luminance from sRGB hex
function relativeLuminance(hex: string): number {
  const r = parseInt(hex.slice(1, 3), 16) / 255;
  const g = parseInt(hex.slice(3, 5), 16) / 255;
  const b = parseInt(hex.slice(5, 7), 16) / 255;

  const toLinear = (c: number) =>
    c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;

  return 0.2126 * toLinear(r) + 0.7152 * toLinear(g) + 0.0722 * toLinear(b);
}

export function contrastRatio(hex1: string, hex2: string): number {
  const l1 = relativeLuminance(hex1);
  const l2 = relativeLuminance(hex2);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

export function ensureContrast(
  bgHex: string,
  textHex: string,
  minRatio = 4.5,
): string {
  if (contrastRatio(bgHex, textHex) >= minRatio) {
    return bgHex;
  }

  // Darken the background iteratively until contrast is met
  let r = parseInt(bgHex.slice(1, 3), 16);
  let g = parseInt(bgHex.slice(3, 5), 16);
  let b = parseInt(bgHex.slice(5, 7), 16);

  for (let i = 0; i < 100; i++) {
    r = Math.max(0, r - 5);
    g = Math.max(0, g - 5);
    b = Math.max(0, b - 5);
    const candidate = `#${r.toString(16).padStart(2, "0")}${g.toString(16).padStart(2, "0")}${b.toString(16).padStart(2, "0")}`;
    if (contrastRatio(candidate, textHex) >= minRatio) {
      return candidate;
    }
  }

  return "#000000";
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd kdp/mcp && npx vitest run src/test/cover-layout.test.ts`
Expected: all tests PASS

- [ ] **Step 5: Commit**

```bash
git add kdp/mcp/src/lib/cover-layout.ts kdp/mcp/src/test/cover-layout.test.ts
git commit -m "feat(kdp): add cover layout library with spine/zone/contrast math"
```

---

## Task 3: `kdp_cover_specs` tool

**Files:**
- Create: `mcp/src/tools/cover-specs.ts`
- Create: `mcp/src/test/cover-specs.test.ts`

The simplest tool. Pure computation, no I/O. Validates the layout library integration.

- [ ] **Step 1: Write the failing test**

```typescript
// mcp/src/test/cover-specs.test.ts
import { describe, it, expect } from "vitest";
import { handleCoverSpecs } from "../tools/cover-specs.js";

describe("handleCoverSpecs", () => {
  it("returns specs for standard fiction paperback", () => {
    const result = handleCoverSpecs({
      page_count: 250,
      trim_size: "5.5x8.5",
      paper_type: "cream",
    });

    expect(result.spine_width_inches).toBeCloseTo(0.685, 2);
    expect(result.total_width_inches).toBeGreaterThan(11);
    expect(result.total_height_inches).toBeCloseTo(8.75, 2);
    expect(result.total_width_px).toBeGreaterThan(3000);
    expect(result.total_height_px).toBe(Math.round(8.75 * 300));
    expect(result.has_spine_text).toBe(true);
    expect(result.bleed_inches).toBe(0.125);
    expect(result.front_zone).toBeDefined();
    expect(result.spine_zone).toBeDefined();
    expect(result.back_zone).toBeDefined();
  });

  it("returns no spine text for short books", () => {
    const result = handleCoverSpecs({
      page_count: 60,
      trim_size: "5.5x8.5",
      paper_type: "white",
    });
    expect(result.has_spine_text).toBe(false);
  });

  it("uses defaults when optional fields omitted", () => {
    const result = handleCoverSpecs({ page_count: 200 });
    // defaults: trim_size "5.5x8.5", paper_type "cream"
    expect(result.total_height_inches).toBeCloseTo(8.75, 2);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd kdp/mcp && npx vitest run src/test/cover-specs.test.ts`
Expected: FAIL (module not found)

- [ ] **Step 3: Implement cover-specs.ts**

```typescript
// mcp/src/tools/cover-specs.ts
import {
  calculateCoverDimensions,
  type PaperType,
} from "../lib/cover-layout.js";

export interface CoverSpecsInput {
  page_count: number;
  trim_size?: string;
  paper_type?: string;
}

export interface CoverSpecsOutput {
  spine_width_inches: number;
  total_width_inches: number;
  total_height_inches: number;
  total_width_px: number;
  total_height_px: number;
  front_zone: { x: number; y: number; width: number; height: number };
  spine_zone: { x: number; y: number; width: number; height: number };
  back_zone: { x: number; y: number; width: number; height: number };
  bleed_inches: number;
  has_spine_text: boolean;
}

export function handleCoverSpecs(input: CoverSpecsInput): CoverSpecsOutput {
  const dims = calculateCoverDimensions({
    pageCount: input.page_count,
    trimSize: input.trim_size ?? "5.5x8.5",
    paperType: (input.paper_type ?? "cream") as PaperType,
  });

  return {
    spine_width_inches: dims.spineWidthInches,
    total_width_inches: dims.totalWidthInches,
    total_height_inches: dims.totalHeightInches,
    total_width_px: dims.totalWidthPx,
    total_height_px: dims.totalHeightPx,
    front_zone: dims.frontZone,
    spine_zone: dims.spineZone,
    back_zone: dims.backZone,
    bleed_inches: dims.bleedInches,
    has_spine_text: dims.hasSpineText,
  };
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd kdp/mcp && npx vitest run src/test/cover-specs.test.ts`
Expected: all tests PASS

- [ ] **Step 5: Commit**

```bash
git add kdp/mcp/src/tools/cover-specs.ts kdp/mcp/src/test/cover-specs.test.ts
git commit -m "feat(kdp): add kdp_cover_specs tool handler"
```

---

## Task 4: OpenAI client wrapper

**Files:**
- Create: `mcp/src/lib/openai-client.ts`
- Create: `mcp/src/test/generate-cover.test.ts`

- [ ] **Step 1: Write the failing test**

```typescript
// mcp/src/test/generate-cover.test.ts
import { describe, it, expect, vi, beforeEach } from "vitest";
import { buildCoverPrompt } from "../lib/openai-client.js";

describe("buildCoverPrompt", () => {
  it("includes title and author in prompt", () => {
    const prompt = buildCoverPrompt({
      title: "The Silent Policy",
      author_name: "Alex Towell",
      genre: "technical",
    });
    expect(prompt).toContain("The Silent Policy");
    expect(prompt).toContain("Alex Towell");
  });

  it("includes subtitle when provided", () => {
    const prompt = buildCoverPrompt({
      title: "Echoes of the Sublime",
      subtitle: "A Journey Through Mathematics",
      author_name: "Alex Towell",
      genre: "technical",
    });
    expect(prompt).toContain("A Journey Through Mathematics");
  });

  it("uses art direction when provided", () => {
    const prompt = buildCoverPrompt({
      title: "Test Book",
      author_name: "Test Author",
      genre: "fantasy",
      art_direction: "dark moody forest with a glowing rune",
    });
    expect(prompt).toContain("dark moody forest with a glowing rune");
  });

  it("generates genre-appropriate prompt when no art direction", () => {
    const prompt = buildCoverPrompt({
      title: "Test Book",
      author_name: "Test Author",
      genre: "thriller",
    });
    // Should contain some genre-relevant direction
    expect(prompt.length).toBeGreaterThan(50);
    expect(prompt).toContain("Test Book");
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd kdp/mcp && npx vitest run src/test/generate-cover.test.ts`
Expected: FAIL (module not found)

- [ ] **Step 3: Implement openai-client.ts**

```typescript
// mcp/src/lib/openai-client.ts
import OpenAI from "openai";
import { writeFile } from "node:fs/promises";
import { join } from "node:path";
import { tmpdir } from "node:os";

export interface CoverPromptInput {
  title: string;
  subtitle?: string;
  author_name: string;
  genre: string;
  art_direction?: string;
}

const GENRE_DEFAULTS: Record<string, string> = {
  fantasy:
    "epic, atmospheric scene with rich color palette, magical elements, dramatic lighting",
  thriller:
    "dark, high-contrast imagery, urban or shadowy setting, sense of tension and danger",
  romance:
    "warm color palette, intimate atmosphere, evocative and emotionally charged imagery",
  "science fiction":
    "futuristic elements, cosmic or technological imagery, sleek and modern aesthetic",
  horror:
    "dark, unsettling atmosphere, muted colors with sharp contrasts, creepy imagery",
  mystery:
    "moody lighting, shadows, hints of intrigue, muted sophisticated color palette",
  literary:
    "elegant, understated design, artistic composition, subtle symbolism",
  technical:
    "clean, professional design, abstract geometric patterns or diagrams, modern typography",
  nonfiction:
    "clean, professional layout, relevant thematic imagery, authoritative feel",
};

export function buildCoverPrompt(input: CoverPromptInput): string {
  const artDirection =
    input.art_direction ?? getGenreDefault(input.genre);

  const subtitleLine = input.subtitle
    ? `\nSubtitle text: "${input.subtitle}" (smaller, below the title)`
    : "";

  return `Design a professional book cover for publication.

Title text: "${input.title}" (prominently displayed, clear and readable)${subtitleLine}
Author text: "${input.author_name}" (at the bottom of the cover)

Art direction: ${artDirection}

Requirements:
- Portrait orientation book cover
- Title and author text must be clearly legible and spelled correctly
- Professional typography that fits the genre
- The text must be part of the design, not overlaid awkwardly
- No placeholder text, lorem ipsum, or watermarks
- High quality, publication-ready artwork`;
}

function getGenreDefault(genre: string): string {
  const lower = genre.toLowerCase();
  for (const [key, value] of Object.entries(GENRE_DEFAULTS)) {
    if (lower.includes(key)) return value;
  }
  return GENRE_DEFAULTS.nonfiction;
}

export async function generateCoverImage(
  input: CoverPromptInput & { width?: number; height?: number },
): Promise<string> {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    throw new Error(
      "OPENAI_API_KEY environment variable is not set. " +
        "Set it in your shell or in the plugin's .mcp.json env config.",
    );
  }

  const client = new OpenAI({ apiKey });
  const prompt = buildCoverPrompt(input);

  let response;
  try {
    response = await client.images.generate({
      model: "gpt-image-1",
      prompt,
      n: 1,
      size: "1024x1792",
      quality: "high",
      response_format: "b64_json",
    });
  } catch (error) {
    if (error instanceof OpenAI.APIError && error.status === 400) {
      throw new Error(
        `Content policy rejection: ${error.message}. ` +
          "Try different art direction that avoids copyrighted or restricted content.",
      );
    }
    throw error;
  }

  const imageData = response.data[0];
  if (!imageData?.b64_json) {
    throw new Error("OpenAI returned no image data");
  }

  // Resize to requested dimensions (OpenAI generates at closest supported size)
  const { default: sharp } = await import("sharp");
  const targetWidth = input.width ?? 1600;
  const targetHeight = input.height ?? 2560;
  const resized = await sharp(Buffer.from(imageData.b64_json, "base64"))
    .resize(targetWidth, targetHeight, { fit: "cover" })
    .png()
    .toBuffer();

  const outputPath = join(
    tmpdir(),
    `kdp-cover-${Date.now()}.png`,
  );
  await writeFile(outputPath, resized);

  return outputPath;
}
```

Note: The `size` parameter uses `"1024x1792"` (closest supported portrait size for DALL-E 3 / GPT-image-1). The image is then resized to the requested dimensions with `sharp`. Check the OpenAI API docs at implementation time for any new supported sizes that may be closer to the KDP target. The `response_format: "b64_json"` is required since we process the image data directly rather than fetching a URL.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd kdp/mcp && npx vitest run src/test/generate-cover.test.ts`
Expected: all tests PASS (only testing `buildCoverPrompt`, not the API call)

- [ ] **Step 5: Commit**

```bash
git add kdp/mcp/src/lib/openai-client.ts kdp/mcp/src/test/generate-cover.test.ts
git commit -m "feat(kdp): add OpenAI client with prompt builder for cover generation"
```

---

## Task 5: `kdp_generate_cover` tool handler

**Files:**
- Create: `mcp/src/tools/generate-cover.ts`

- [ ] **Step 1: Implement the tool handler**

```typescript
// mcp/src/tools/generate-cover.ts
import { generateCoverImage } from "../lib/openai-client.js";

export interface GenerateCoverInput {
  title: string;
  subtitle?: string;
  author_name: string;
  genre: string;
  art_direction?: string;
  width?: number;
  height?: number;
}

export async function handleGenerateCover(
  input: GenerateCoverInput,
): Promise<{ path: string }> {
  const path = await generateCoverImage({
    title: input.title,
    subtitle: input.subtitle,
    author_name: input.author_name,
    genre: input.genre,
    art_direction: input.art_direction,
    width: input.width ?? 1600,
    height: input.height ?? 2560,
  });

  return { path };
}
```

- [ ] **Step 2: Add test for handleGenerateCover (mocked OpenAI)**

Add to `mcp/src/test/generate-cover.test.ts`:

```typescript
import { handleGenerateCover } from "../tools/generate-cover.js";
import * as openaiClient from "../lib/openai-client.js";

describe("handleGenerateCover", () => {
  it("returns path from generateCoverImage", async () => {
    vi.spyOn(openaiClient, "generateCoverImage").mockResolvedValue(
      "/tmp/kdp-cover-mock.png",
    );

    const result = await handleGenerateCover({
      title: "Test",
      author_name: "Author",
      genre: "fantasy",
    });

    expect(result).toEqual({ path: "/tmp/kdp-cover-mock.png" });
  });

  it("passes default dimensions when not specified", async () => {
    const spy = vi
      .spyOn(openaiClient, "generateCoverImage")
      .mockResolvedValue("/tmp/mock.png");

    await handleGenerateCover({
      title: "Test",
      author_name: "Author",
      genre: "fantasy",
    });

    expect(spy).toHaveBeenCalledWith(
      expect.objectContaining({ width: 1600, height: 2560 }),
    );
  });

  it("propagates errors from generateCoverImage", async () => {
    vi.spyOn(openaiClient, "generateCoverImage").mockRejectedValue(
      new Error("OPENAI_API_KEY environment variable is not set."),
    );

    await expect(
      handleGenerateCover({
        title: "Test",
        author_name: "Author",
        genre: "fantasy",
      }),
    ).rejects.toThrow("OPENAI_API_KEY");
  });
});
```

- [ ] **Step 3: Run test to verify it passes**

Run: `cd kdp/mcp && npx vitest run src/test/generate-cover.test.ts`
Expected: all tests PASS

- [ ] **Step 4: Commit**

```bash
git add kdp/mcp/src/tools/generate-cover.ts kdp/mcp/src/test/generate-cover.test.ts
git commit -m "feat(kdp): add kdp_generate_cover tool handler with tests"
```

---

## Task 6: `kdp_generate_full_wrap` tool handler

**Files:**
- Create: `mcp/src/tools/generate-full-wrap.ts`
- Create: `mcp/src/test/generate-full-wrap.test.ts`

This is the most complex tool. It composites the front cover with a programmatic back cover and spine into a KDP-ready PDF.

- [ ] **Step 1: Write the failing test**

```typescript
// mcp/src/test/generate-full-wrap.test.ts
import { describe, it, expect, beforeAll } from "vitest";
import { createBackCover, createSpineText } from "../tools/generate-full-wrap.js";
import sharp from "sharp";
import { existsSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { writeFile } from "node:fs/promises";

// Create a test front cover image
let testCoverPath: string;

beforeAll(async () => {
  testCoverPath = join(tmpdir(), "test-front-cover.png");
  // Create a 1600x2560 solid blue image as a test front cover
  await sharp({
    create: {
      width: 1600,
      height: 2560,
      channels: 3,
      background: { r: 30, g: 60, b: 120 },
    },
  })
    .png()
    .toFile(testCoverPath);
});

describe("createBackCover", () => {
  it("creates a back cover image with correct dimensions", async () => {
    const result = await createBackCover({
      width: 1650, // 5.5" * 300 DPI
      height: 2550, // 8.5" * 300 DPI
      blurb: "A thrilling adventure through time and space.",
      bgColor: "#1a1a2e",
    });

    expect(result).toBeInstanceOf(Buffer);
    const metadata = await sharp(result).metadata();
    expect(metadata.width).toBe(1650);
    expect(metadata.height).toBe(2550);
  });
});

describe("createSpineText", () => {
  it("returns null for thin books", () => {
    const result = createSpineText({
      title: "Test",
      authorName: "Author",
      spineWidthInches: 0.2,
      heightPx: 2550,
    });
    expect(result).toBeNull();
  });

  it("returns title-only for narrow spines", () => {
    const result = createSpineText({
      title: "Test Book",
      authorName: "Author Name",
      spineWidthInches: 0.35,
      heightPx: 2550,
    });
    expect(result).not.toBeNull();
    expect(result!.titleOnly).toBe(true);
  });

  it("returns full text for wide spines", () => {
    const result = createSpineText({
      title: "Test Book",
      authorName: "Author Name",
      spineWidthInches: 0.8,
      heightPx: 2550,
    });
    expect(result).not.toBeNull();
    expect(result!.titleOnly).toBe(false);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd kdp/mcp && npx vitest run src/test/generate-full-wrap.test.ts`
Expected: FAIL (module not found)

- [ ] **Step 3: Implement generate-full-wrap.ts**

This file exports `createBackCover`, `createSpineText`, and `handleGenerateFullWrap`. Here are the type signatures that the tests depend on:

```typescript
// Type signatures (must match what the tests import)

export interface SpineTextResult {
  svgBuffer: Buffer;      // rendered SVG as image buffer
  titleOnly: boolean;     // true if spine is too narrow for author name
}

export async function createBackCover(opts: {
  width: number;          // pixels
  height: number;         // pixels
  blurb: string;
  bgColor: string;        // hex color (already contrast-checked)
  isbn?: string;          // if set, mark barcode zone
}): Promise<Buffer>       // returns PNG buffer

export function createSpineText(opts: {
  title: string;
  authorName: string;
  spineWidthInches: number;
  heightPx: number;
}): SpineTextResult | null  // null if spine too narrow for text (< 130 pages)

export interface FullWrapInput {
  front_cover_path: string;
  title: string;
  author_name: string;
  blurb: string;
  page_count: number;
  trim_size?: string;
  paper_type?: string;
  isbn?: string;
  back_color?: string;
}

export interface FullWrapOutput {
  pdf_path: string;
  preview_path: string;
  specs: import("./cover-specs.js").CoverSpecsOutput;
}

export async function handleGenerateFullWrap(
  input: FullWrapInput,
): Promise<FullWrapOutput>
```

The implementation should:

1. Use `sharp` to read and resize the front cover image to fit the front zone
2. Create the back cover as an SVG rendered by `sharp` (SVG supports text layout natively, which `sharp` can then rasterize)
3. Create the spine text as another SVG overlay (rotated 90 degrees clockwise)
4. Composite all pieces onto a blank canvas at the full wrap dimensions
5. Use `pdf-lib` to embed the composited image into a single-page PDF at the exact dimensions
6. Also save a PNG preview at lower resolution

Key implementation notes for the developer:
- `sharp` can render SVG with text. Create SVG strings with `<text>` elements for the back cover blurb and spine text, then convert with `sharp(Buffer.from(svgString))`
- Use a standard font in the SVG (`serif` for back cover blurb, `sans-serif` for spine). SVG text rendering in `sharp` uses system fonts via librsvg.
- For the barcode zone, draw a white rectangle in the lower-right of the back cover SVG (2" x 1.2" at 300 DPI = 600 x 360 px)
- Spine text rotation: use SVG `transform="rotate(90)"` for clockwise rotation (reads top-to-bottom)
- Call `ensureContrast` from `cover-layout.ts` on the back cover color before rendering
- For dominant color extraction when `back_color` is not provided: use `sharp.stats()` on the front cover to get the dominant channel values

The full implementation will be substantial (100-150 lines). Write it following these structural guidelines, adapting as needed when the actual `sharp` and `pdf-lib` APIs are available.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd kdp/mcp && npx vitest run src/test/generate-full-wrap.test.ts`
Expected: all tests PASS

- [ ] **Step 5: Add integration test with actual file output**

Add a test that calls the full `handleGenerateFullWrap` with the test front cover and verifies the output PDF and PNG files exist and have reasonable sizes:

```typescript
describe("handleGenerateFullWrap", () => {
  it("produces PDF and PNG output", async () => {
    const result = await handleGenerateFullWrap({
      front_cover_path: testCoverPath,
      title: "Test Book",
      author_name: "Test Author",
      blurb: "A short blurb for testing.",
      page_count: 250,
      trim_size: "5.5x8.5",
      paper_type: "cream",
    });

    expect(existsSync(result.pdf_path)).toBe(true);
    expect(existsSync(result.preview_path)).toBe(true);
    expect(result.specs.spine_width_inches).toBeGreaterThan(0);
  });
});
```

- [ ] **Step 6: Run full test suite**

Run: `cd kdp/mcp && npx vitest run`
Expected: all tests PASS

- [ ] **Step 7: Commit**

```bash
git add kdp/mcp/src/tools/generate-full-wrap.ts kdp/mcp/src/test/generate-full-wrap.test.ts
git commit -m "feat(kdp): add kdp_generate_full_wrap tool with compositing and PDF output"
```

---

## Task 7: MCP server entry point

**Files:**
- Modify: `mcp/src/index.ts` (replace scaffolding placeholder)

- [ ] **Step 1: Implement MCP server with all three tools**

Replace the scaffolding `index.ts` with the full MCP server. Register all three tools with their JSON schemas and connect to the tool handlers.

```typescript
// mcp/src/index.ts
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { handleCoverSpecs } from "./tools/cover-specs.js";
import { handleGenerateCover } from "./tools/generate-cover.js";
import { handleGenerateFullWrap } from "./tools/generate-full-wrap.js";

const server = new McpServer({
  name: "kdp-cover",
  version: "0.1.0",
});

server.tool(
  "kdp_cover_specs",
  "Calculate KDP paperback cover dimensions (spine width, zone layout, bleed) from page count, trim size, and paper type. Pure math, no image generation.",
  {
    page_count: z.number().int().min(24).describe("Number of pages in the book"),
    trim_size: z
      .string()
      .default("5.5x8.5")
      .describe('Trim size as "WxH" in inches, e.g. "5.5x8.5", "6x9"'),
    paper_type: z
      .enum(["white", "cream"])
      .default("cream")
      .describe("Paper type (affects spine width calculation)"),
  },
  async (args) => {
    const result = handleCoverSpecs(args);
    return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
  },
);

server.tool(
  "kdp_generate_cover",
  "Generate a complete front cover image with artwork and typography via OpenAI image generation. Returns the file path to the generated PNG. Each call costs ~$0.04-0.08.",
  {
    title: z.string().describe("Book title"),
    subtitle: z.string().optional().describe("Book subtitle"),
    author_name: z.string().describe("Author or pen name"),
    genre: z
      .string()
      .describe('Book genre, e.g. "epic fantasy", "thriller", "technical"'),
    art_direction: z
      .string()
      .optional()
      .describe(
        "Visual description for the cover art. If omitted, a genre-appropriate prompt is generated.",
      ),
    width: z.number().default(1600).describe("Cover width in pixels (portrait)"),
    height: z.number().default(2560).describe("Cover height in pixels (portrait)"),
  },
  async (args) => {
    try {
      const result = await handleGenerateCover(args);
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(result),
          },
        ],
      };
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      return {
        content: [{ type: "text", text: `Error: ${message}` }],
        isError: true,
      };
    }
  },
);

server.tool(
  "kdp_generate_full_wrap",
  "Composite a full paperback cover wrap: front cover image + calculated spine + programmatic back cover with blurb text. Outputs a KDP-ready PDF and a PNG preview.",
  {
    front_cover_path: z.string().describe("Path to the approved front cover image"),
    title: z.string().describe("Book title (for spine text)"),
    author_name: z.string().describe("Author name (for spine text)"),
    blurb: z.string().describe("Back cover blurb text"),
    page_count: z.number().int().min(24).describe("Number of pages (for spine width)"),
    trim_size: z.string().default("5.5x8.5").describe('Trim size "WxH" in inches'),
    paper_type: z
      .enum(["white", "cream"])
      .default("cream")
      .describe("Paper type"),
    isbn: z.string().optional().describe("ISBN (marks barcode zone on back cover)"),
    back_color: z
      .string()
      .optional()
      .describe(
        "Hex color for back cover background. If omitted, extracted from front cover.",
      ),
  },
  async (args) => {
    try {
      const result = await handleGenerateFullWrap(args);
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      return {
        content: [{ type: "text", text: `Error: ${message}` }],
        isError: true,
      };
    }
  },
);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch(console.error);
```

Note: The `@modelcontextprotocol/sdk` API may have changed since this plan was written. Check the current MCP SDK docs or other working MCP servers in the user's setup (e.g., crier) for the correct import paths and server construction pattern. `zod` is listed as an explicit dependency in `package.json` to avoid fragile implicit resolution through the MCP SDK.

- [ ] **Step 2: Verify the server starts**

Run: `cd kdp/mcp && echo '{}' | npx tsx src/index.ts`

The server should start without errors and wait for MCP protocol messages on stdin. It will likely close immediately since `echo '{}'` is not valid MCP protocol, but it should not crash with import errors.

- [ ] **Step 3: Commit**

```bash
git add kdp/mcp/src/index.ts
git commit -m "feat(kdp): wire up MCP server entry point with all three tools"
```

---

## Task 8: Plugin integration files

**Files:**
- Create: `.mcp.json`
- Modify: `docs/user-config-template.md`
- Modify: `.claude-plugin/plugin.json`
- Modify: `CLAUDE.md`

- [ ] **Step 1: Create .mcp.json**

```json
{
  "mcpServers": {
    "kdp-cover": {
      "command": "bash",
      "args": ["${CLAUDE_PLUGIN_ROOT}/mcp/run.sh"],
      "env": {
        "OPENAI_API_KEY": "${OPENAI_API_KEY}"
      }
    }
  }
}
```

Note: Using `run.sh` wrapper instead of direct `npx tsx` invocation to avoid `${CLAUDE_PLUGIN_ROOT}` expansion issues in `.mcp.json`. The wrapper resolves the path relative to its own location.

- [ ] **Step 2: Update user-config-template.md**

Add the new fields after the existing `kdp` section. The new fields are:

```yaml
  asin: null                         # eBook ASIN (saved after first publish)
  asin_paperback: null               # paperback ASIN (saved after first publish)
  cover:
    front: null                      # path to approved front cover image
    full_wrap: null                  # path to full-wrap PDF (paperback)
    art_direction: ""                # description of desired cover art style
    color_scheme: null               # back cover color (hex), or auto-extracted from front
  manuscript:
    path: null                       # path to final manuscript file for upload
```

- [ ] **Step 3: Bump version in plugin.json**

Update version from `"0.2.0"` to `"0.3.0"` in `.claude-plugin/plugin.json`.

- [ ] **Step 4: Update CLAUDE.md**

Add a section documenting the MCP component under "Architecture". Key points:
- The `mcp/` directory contains a TypeScript MCP server for cover generation
- Requires `npm install` in `mcp/` before first use
- Requires `OPENAI_API_KEY` environment variable
- Three tools: `kdp_cover_specs`, `kdp_generate_cover`, `kdp_generate_full_wrap`

- [ ] **Step 5: Bump marketplace.json**

Update the kdp version in the top-level `.claude-plugin/marketplace.json` from `"0.2.0"` to `"0.3.0"`. Both `plugin.json` and `marketplace.json` must always match.

- [ ] **Step 6: Commit**

```bash
git add kdp/.mcp.json kdp/docs/user-config-template.md kdp/.claude-plugin/plugin.json kdp/CLAUDE.md .claude-plugin/marketplace.json
git commit -m "feat(kdp): add MCP registration, update config template, bump to 0.3.0"
```

---

## Task 9: Update kdp-publish skill (Phases 6-8)

**Files:**
- Modify: `skills/kdp-publish/SKILL.md`

This is the most important task. It rewrites Phases 6-8 from instructional text to tool-driven automation.

- [ ] **Step 1: Read the current skill**

Read `skills/kdp-publish/SKILL.md` in full. Understand the existing phase structure.

- [ ] **Step 2: Rewrite Phase 6 (Cover Preparation)**

Replace the current Phase 6 content with the automated workflow. The new Phase 6 should:

1. Check if cover files already exist (config paths or glob for `cover*` files)
2. If no cover, ask user for art direction
3. Inform user of approximate cost per generation (~$0.04-0.08 per image)
4. Call `kdp_generate_cover` MCP tool
5. Show the cover to user (Read tool on the image file)
6. Ask user to verify title text is spelled correctly
7. Iterate if user wants changes
8. Save approved front cover path to `.claude/kdp.local.md`
9. If paperback target: call `kdp_cover_specs`, then `kdp_generate_full_wrap`
10. Show the full-wrap preview (Read tool on the PNG preview)
11. Save full-wrap PDF path to config

Use the existing skill format: numbered steps with tool annotations in parentheses.

- [ ] **Step 3: Rewrite Phase 7 (Dashboard Submission)**

Replace the current Phase 7 with Playwright-driven automation:

1. `browser_navigate` to `https://kdp.amazon.com` (Playwright MCP)
2. `browser_snapshot` to check login state (Playwright MCP)
3. If not logged in: tell user to log in in the browser window, then `browser_wait_for` until the dashboard is visible
4. For new title: navigate to "Create New Title", select format
5. For update: use stored ASIN to navigate directly, or search bookshelf by title
6. `browser_snapshot` each form page, `browser_fill_form` / `browser_click` to populate fields from `.claude/kdp.local.md`: title, subtitle, author/pen name, series info, description (blurb), keywords (7 slots), categories
7. `browser_file_upload` for manuscript file (from `kdp.manuscript.path`) and cover image (from `kdp.cover.front` or `kdp.cover.full_wrap`)
8. Navigate to the review/preview page
9. Stop. Tell user to review and click publish.
10. After user confirms publish is done, attempt to capture ASIN via `browser_snapshot` of the bookshelf page
11. Save ASIN to config

Important: This phase should describe what to do adaptively, not prescribe exact selectors. Claude reads each page and figures out what to click. The instructions should focus on the goal of each step, not the DOM.

- [ ] **Step 4: Rewrite Phase 8 (Pricing)**

Update to be semi-automated:
1. Present pricing options conversationally (royalty tier, KDP Select, price, territories)
2. After user decides, use Playwright to fill in the pricing form
3. Reference `${CLAUDE_PLUGIN_ROOT}/docs/kdp-reference.md` for genre-specific price recommendations

- [ ] **Step 5: Add fallback note**

Add a note at the top of Phase 6 (or in a general preamble) that if the MCP tools are not available (Node.js not installed, `OPENAI_API_KEY` not set), Phases 6-8 fall back to the original manual instructions. The skill should check for tool availability before attempting automation.

- [ ] **Step 6: Verify no broken `${CLAUDE_PLUGIN_ROOT}` references**

Run: `grep -roh '\${CLAUDE_PLUGIN_ROOT}/[^`"]*' kdp/skills/ | sort -u | while read ref; do resolved="${ref/\$\{CLAUDE_PLUGIN_ROOT\}/kdp}"; [ -f "$resolved" ] || echo "BROKEN: $ref"; done`

Expected: no BROKEN references

- [ ] **Step 7: Commit**

```bash
git add kdp/skills/kdp-publish/SKILL.md
git commit -m "feat(kdp): rewrite Phases 6-8 to use MCP tools + Playwright automation"
```

---

## Task 10: End-to-end verification

- [ ] **Step 1: Run full test suite**

Run: `cd kdp/mcp && npx vitest run`
Expected: all tests PASS

- [ ] **Step 2: Run test coverage**

Run: `cd kdp/mcp && npx vitest run --coverage`
Review coverage report. Key areas that should be covered:
- `cover-layout.ts`: spine width, dimensions, contrast (should be near 100%)
- `cover-specs.ts`: handler function (should be 100%)
- `openai-client.ts`: prompt builder (should be covered; API call function is not unit-tested)
- `generate-full-wrap.ts`: back cover creation, spine text logic (should be covered)

- [ ] **Step 3: Verify MCP server starts**

Run: `cd kdp/mcp && timeout 3 npx tsx src/index.ts 2>&1 || true`
Expected: no import errors, no crash

- [ ] **Step 4: Validate plugin structure**

Run the validation commands from the plugin's `CLAUDE.md`:

```bash
cd kdp

# Skill frontmatter
for f in skills/*/SKILL.md; do echo "=== $f ===" && head -5 "$f" && echo; done

# Command frontmatter
for f in commands/*.md; do echo "=== $f ===" && head -5 "$f" && echo; done

# Broken references
grep -roh '\${CLAUDE_PLUGIN_ROOT}/[^`"]*' skills/ commands/ | sort -u | while read ref; do
  resolved="${ref/\$\{CLAUDE_PLUGIN_ROOT\}/\.}"
  [ -f "$resolved" ] || echo "BROKEN: $ref"
done
```

Expected: all frontmatter present, no broken references

- [ ] **Step 5: Verify version sync**

Check that `.claude-plugin/plugin.json` version matches the kdp entry in the top-level `.claude-plugin/marketplace.json`.

- [ ] **Step 6: Final commit if any fixes were needed**

```bash
git add -A kdp/
git commit -m "fix(kdp): address issues found in end-to-end verification"
```
