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
