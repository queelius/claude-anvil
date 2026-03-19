import { describe, it, expect, beforeAll } from "vitest";
import { createBackCover, createSpineText, handleGenerateFullWrap } from "../tools/generate-full-wrap.js";
import sharp from "sharp";
import { existsSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";

let testCoverPath: string;

beforeAll(async () => {
  testCoverPath = join(tmpdir(), "test-front-cover.png");
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
      width: 1650,
      height: 2550,
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
