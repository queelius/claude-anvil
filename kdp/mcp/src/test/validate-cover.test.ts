import { describe, it, expect } from "vitest";
import { join } from "node:path";
import { tmpdir } from "node:os";
import sharp from "sharp";
import { handleValidateCover } from "../tools/validate-cover.js";
import { handleCoverSpecs } from "../tools/cover-specs.js";

async function makePng(width: number, height: number): Promise<string> {
  const p = join(tmpdir(), `kdp-validate-${width}x${height}-${process.pid}.png`);
  await sharp({
    create: { width, height, channels: 3, background: { r: 30, g: 60, b: 90 } },
  })
    .png()
    .toFile(p);
  return p;
}

describe("handleValidateCover: ebook", () => {
  it("passes a recommended-size ebook cover (PNG warns on format only)", async () => {
    const p = await makePng(1600, 2560);
    const result = await handleValidateCover({ cover_path: p, kind: "ebook" });
    expect(result.valid).toBe(true);
    const formatCheck = result.checks.find((c) => c.name === "file format");
    expect(formatCheck?.status).toBe("warn");
  });

  it("fails an ebook cover below the 1000px hard minimum", async () => {
    const p = await makePng(500, 800);
    const result = await handleValidateCover({ cover_path: p, kind: "ebook" });
    expect(result.valid).toBe(false);
    const sizeCheck = result.checks.find((c) => c.name === "hard minimum size");
    expect(sizeCheck?.status).toBe("fail");
  });

  it("warns (not fails) on an off-ratio but large ebook cover", async () => {
    const p = await makePng(2560, 2560); // square
    const result = await handleValidateCover({ cover_path: p, kind: "ebook" });
    expect(result.valid).toBe(true);
    const ratioCheck = result.checks.find((c) => c.name === "aspect ratio");
    expect(ratioCheck?.status).toBe("warn");
  });
});

describe("handleValidateCover: full_wrap", () => {
  it("passes a wrap rendered at exactly the computed specs", async () => {
    const specs = handleCoverSpecs({
      page_count: 300,
      trim_size: "5.5x8.5",
      paper_type: "cream",
    });
    const p = await makePng(specs.total_width_px, specs.total_height_px);
    const result = await handleValidateCover({
      cover_path: p,
      kind: "full_wrap",
      page_count: 300,
      trim_size: "5.5x8.5",
      paper_type: "cream",
    });
    expect(result.valid).toBe(true);
    expect(result.specs?.total_width_px).toBe(specs.total_width_px);
  });

  it("fails a wrap sized for the wrong page count", async () => {
    const wrong = handleCoverSpecs({
      page_count: 120,
      trim_size: "5.5x8.5",
      paper_type: "cream",
    });
    const p = await makePng(wrong.total_width_px, wrong.total_height_px);
    const result = await handleValidateCover({
      cover_path: p,
      kind: "full_wrap",
      page_count: 300,
      trim_size: "5.5x8.5",
      paper_type: "cream",
    });
    expect(result.valid).toBe(false);
    const widthCheck = result.checks.find((c) => c.name === "wrap width");
    expect(widthCheck?.status).toBe("fail");
  });

  it("requires page_count for print kinds", async () => {
    const p = await makePng(100, 100);
    await expect(
      handleValidateCover({ cover_path: p, kind: "full_wrap" }),
    ).rejects.toThrow(/requires page_count/);
  });
});

describe("handleValidateCover: paperback_front", () => {
  it("accepts trim-exact and bleed-extended front covers", async () => {
    const specs = handleCoverSpecs({
      page_count: 300,
      trim_size: "6x9",
      paper_type: "white",
    });
    const bleedPx = Math.round(specs.bleed_inches * 300);

    const trimExact = await makePng(
      specs.front_zone.width,
      specs.front_zone.height,
    );
    const withBleed = await makePng(
      specs.front_zone.width + bleedPx,
      specs.front_zone.height + 2 * bleedPx,
    );

    for (const p of [trimExact, withBleed]) {
      const result = await handleValidateCover({
        cover_path: p,
        kind: "paperback_front",
        page_count: 300,
        trim_size: "6x9",
        paper_type: "white",
      });
      expect(result.valid).toBe(true);
    }
  });
});
