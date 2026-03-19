import { describe, it, expect } from "vitest";
import {
  calculateSpineWidth,
  calculateCoverDimensions,
  contrastRatio,
  ensureContrast,
} from "../lib/cover-layout.js";

describe("calculateSpineWidth", () => {
  it("calculates white paper spine width", () => {
    const result = calculateSpineWidth(300, "white");
    expect(result).toBeCloseTo(0.7356, 4);
  });

  it("calculates cream paper spine width", () => {
    const result = calculateSpineWidth(300, "cream");
    expect(result).toBeCloseTo(0.81, 4);
  });

  it("calculates minimum page count spine width", () => {
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

    expect(dims.spineWidthInches).toBeCloseTo(0.81, 2);
    expect(dims.totalWidthInches).toBeCloseTo(12.06, 2);
    expect(dims.totalHeightInches).toBeCloseTo(8.75, 2);
    expect(dims.totalWidthPx).toBe(Math.round(12.06 * 300));
    expect(dims.totalHeightPx).toBe(Math.round(8.75 * 300));
    expect(dims.hasSpineText).toBe(true);
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
    const result = ensureContrast("#1a1a2e", "#ffffff");
    expect(result).toBe("#1a1a2e");
  });

  it("darkens a light color that has poor contrast with white", () => {
    const result = ensureContrast("#ffff99", "#ffffff");
    expect(contrastRatio(result, "#ffffff")).toBeGreaterThanOrEqual(4.5);
  });
});
