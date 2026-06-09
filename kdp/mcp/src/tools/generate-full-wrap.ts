import { writeFile } from "node:fs/promises";
import { join } from "node:path";
import { tmpdir } from "node:os";
import sharp from "sharp";
import { PDFDocument } from "pdf-lib";
import {
  calculateCoverDimensions,
  ensureContrast,
  SPINE_TEXT_MIN_WIDTH_INCHES,
  type PaperType,
} from "../lib/cover-layout.js";
import { handleCoverSpecs, type CoverSpecsOutput } from "./cover-specs.js";

// ── Types ──────────────────────────────────────────────────────────────────

export interface SpineTextResult {
  svgBuffer: Buffer; // rendered SVG as image buffer
  titleOnly: boolean; // true if spine is too narrow for author name
}

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
  specs: CoverSpecsOutput;
}

// ── Thresholds ─────────────────────────────────────────────────────────────

const SPINE_TOO_NARROW_INCHES = SPINE_TEXT_MIN_WIDTH_INCHES; // shared threshold
const SPINE_TITLE_ONLY_INCHES = 0.5; // threshold-0.5" renders title only

const DPI = 300;
const POINTS_PER_INCH = 72;

// ── createBackCover ────────────────────────────────────────────────────────

export async function createBackCover(opts: {
  width: number;
  height: number;
  blurb: string;
  bgColor: string;
  isbn?: string;
}): Promise<Buffer> {
  const { width, height, blurb, bgColor, isbn } = opts;

  // Barcode zone: 2" x 1.2" at 300 DPI in bottom-right corner
  const barcodeW = Math.round(2 * DPI);
  const barcodeH = Math.round(1.2 * DPI);
  const barcodePadding = Math.round(0.25 * DPI);
  const barcodeX = width - barcodeW - barcodePadding;
  const barcodeY = height - barcodeH - barcodePadding;

  // Text area: leave margins and stay above barcode zone
  const marginPx = Math.round(0.5 * DPI);
  const textWidth = width - marginPx * 2;
  const textAreaHeight = barcodeY - marginPx * 2;
  const fontSize = Math.max(28, Math.round(width * 0.022));

  // Escape XML entities for safe SVG embedding
  const escapeXml = (s: string) =>
    s
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");

  const barcodeRect = isbn
    ? `<rect x="${barcodeX}" y="${barcodeY}" width="${barcodeW}" height="${barcodeH}" fill="white" rx="4"/>`
    : `<rect x="${barcodeX}" y="${barcodeY}" width="${barcodeW}" height="${barcodeH}" fill="white" rx="4" opacity="0.15"/>`;

  // sharp does not support foreignObject/xhtml; plain SVG text with tspan wrapping
  const words = blurb.split(" ");
  const charsPerLine = Math.floor(textWidth / (fontSize * 0.55));
  const lines: string[] = [];
  let currentLine = "";

  for (const word of words) {
    const candidate = currentLine ? `${currentLine} ${word}` : word;
    if (candidate.length <= charsPerLine) {
      currentLine = candidate;
    } else {
      if (currentLine) lines.push(currentLine);
      currentLine = word;
    }
  }
  if (currentLine) lines.push(currentLine);

  const lineHeight = Math.round(fontSize * 1.5);
  // Vertical overflow guard: long blurbs must not render across the barcode
  // zone or off-panel. Clamp to the lines that fit and ellipsize.
  const maxLines = Math.max(1, Math.floor(textAreaHeight / lineHeight));
  if (lines.length > maxLines) {
    lines.length = maxLines;
    lines[maxLines - 1] = lines[maxLines - 1].replace(/\s+\S*$/, "") + " ...";
  }
  const tspans = lines
    .map(
      (line, i) =>
        `<tspan x="${marginPx}" dy="${i === 0 ? 0 : lineHeight}">${escapeXml(line)}</tspan>`,
    )
    .join("\n    ");

  const plainSvg = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}">
  <rect width="${width}" height="${height}" fill="${bgColor}"/>
  <text x="${marginPx}" y="${marginPx + fontSize}" font-family="serif" font-size="${fontSize}" fill="white">
    ${tspans}
  </text>
  ${barcodeRect}
</svg>`;

  const buffer = await sharp(Buffer.from(plainSvg))
    .resize(width, height)
    .png()
    .toBuffer();

  return buffer;
}

// ── createSpineText ────────────────────────────────────────────────────────

export function createSpineText(opts: {
  title: string;
  authorName: string;
  spineWidthInches: number;
  heightPx: number;
}): SpineTextResult | null {
  const { title, authorName, spineWidthInches, heightPx } = opts;

  if (spineWidthInches < SPINE_TOO_NARROW_INCHES) {
    return null;
  }

  const titleOnly = spineWidthInches < SPINE_TITLE_ONLY_INCHES;

  // Spine rendered rotated: width → height axis, height → width axis
  const spineWidthPx = Math.round(spineWidthInches * DPI);

  // SVG is drawn upright then rotated — canvas is heightPx wide, spineWidthPx tall
  const svgW = heightPx;
  const svgH = spineWidthPx;

  const titleFontSize = Math.max(18, Math.min(Math.round(spineWidthPx * 0.35), 48));
  const authorFontSize = Math.max(14, Math.min(Math.round(spineWidthPx * 0.22), 32));

  const cx = svgW / 2;
  const titleY = svgH * 0.45;
  const authorY = svgH * 0.75;

  const escapeXml = (s: string) =>
    s
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");

  const authorLine = titleOnly
    ? ""
    : `<text x="${cx}" y="${authorY}" text-anchor="middle" font-family="sans-serif" font-size="${authorFontSize}" fill="white" opacity="0.85">${escapeXml(authorName)}</text>`;

  const svgString = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="${svgW}" height="${svgH}">
  <rect width="${svgW}" height="${svgH}" fill="none"/>
  <text x="${cx}" y="${titleY}" text-anchor="middle" font-family="sans-serif" font-size="${titleFontSize}" font-weight="bold" fill="white">${escapeXml(title)}</text>
  ${authorLine}
</svg>`;

  const svgBuffer = Buffer.from(svgString);

  return { svgBuffer, titleOnly };
}

// ── Dominant color extraction ──────────────────────────────────────────────

async function extractDominantColor(imagePath: string): Promise<string> {
  const stats = await sharp(imagePath).stats();
  const r = Math.round(stats.channels[0].mean);
  const g = Math.round(stats.channels[1].mean);
  const b = Math.round(stats.channels[2].mean);
  return `#${r.toString(16).padStart(2, "0")}${g.toString(16).padStart(2, "0")}${b.toString(16).padStart(2, "0")}`;
}

// ── handleGenerateFullWrap ─────────────────────────────────────────────────

export async function handleGenerateFullWrap(
  input: FullWrapInput,
): Promise<FullWrapOutput> {
  const specs = handleCoverSpecs({
    page_count: input.page_count,
    trim_size: input.trim_size,
    paper_type: input.paper_type,
  });

  const {
    total_width_px: totalW,
    total_height_px: totalH,
    front_zone: frontZone,
    spine_zone: spineZone,
    back_zone: backZone,
    spine_width_inches: spineWidthInches,
  } = specs;

  // ── Determine background color ──────────────────────────────────────────
  let rawBgColor = input.back_color ?? (await extractDominantColor(input.front_cover_path));
  const bgColor = ensureContrast(rawBgColor, "#ffffff");

  // ── Create blank canvas ─────────────────────────────────────────────────
  // Background is the back-cover color, not black: the 0.125" bleed border
  // must carry printable art (a stock KDP rejection reason is missing bleed),
  // and a bgColor canvas makes the back/spine bleed seamless with the back panel.
  const canvas = sharp({
    create: {
      width: totalW,
      height: totalH,
      channels: 3,
      background: {
        r: parseInt(bgColor.slice(1, 3), 16),
        g: parseInt(bgColor.slice(3, 5), 16),
        b: parseInt(bgColor.slice(5, 7), 16),
      },
    },
  });

  // ── Resize front cover to fill front zone PLUS its bleed ───────────────
  // The front panel owns the right/top/bottom bleed on its side of the wrap;
  // extend the art so the trim line never exposes an unprinted border. Size
  // from canvas geometry (right edge, full height) rather than adding bleed
  // px, so independent rounding can never overflow the canvas.
  const frontBuffer = await sharp(input.front_cover_path)
    .resize(totalW - frontZone.x, totalH, {
      fit: "cover",
    })
    .png()
    .toBuffer();

  // ── Create back cover ──────────────────────────────────────────────────
  const backBuffer = await createBackCover({
    width: backZone.width,
    height: backZone.height,
    blurb: input.blurb,
    bgColor,
    isbn: input.isbn,
  });

  // ── Build composites list ──────────────────────────────────────────────
  const composites: sharp.OverlayOptions[] = [
    // Back cover
    {
      input: backBuffer,
      left: backZone.x,
      top: backZone.y,
    },
    // Front cover (placed at the bleed-extended origin: top of canvas)
    {
      input: frontBuffer,
      left: frontZone.x,
      top: 0,
    },
  ];

  // ── Spine text (if wide enough) ────────────────────────────────────────
  const spineResult = createSpineText({
    title: input.title,
    authorName: input.author_name,
    spineWidthInches,
    heightPx: spineZone.height,
  });

  if (spineResult) {
    // Render the SVG upright first (heightPx wide × spineWidthPx tall)
    const spineWidthPx = Math.round(spineWidthInches * DPI);
    const renderedSpine = await sharp(spineResult.svgBuffer)
      .resize(spineZone.height, spineWidthPx)
      .png()
      .toBuffer();

    // Rotate 90° clockwise so text reads top-to-bottom on the spine
    const rotatedSpine = await sharp(renderedSpine).rotate(90).png().toBuffer();

    composites.push({
      input: rotatedSpine,
      left: spineZone.x,
      top: spineZone.y,
    });
  }

  // ── Composite everything ───────────────────────────────────────────────
  const fullWrapBuffer = await canvas.composite(composites).png().toBuffer();

  // ── Save PNG preview (half resolution) ────────────────────────────────
  const previewPath = join(tmpdir(), `kdp-full-wrap-preview-${Date.now()}.png`);
  await sharp(fullWrapBuffer)
    .resize(Math.round(totalW / 2), Math.round(totalH / 2))
    .png()
    .toFile(previewPath);

  // ── Embed into PDF via pdf-lib ─────────────────────────────────────────
  const pdfDoc = await PDFDocument.create();

  const widthPt = specs.total_width_inches * POINTS_PER_INCH;
  const heightPt = specs.total_height_inches * POINTS_PER_INCH;
  const page = pdfDoc.addPage([widthPt, heightPt]);

  const pngImage = await pdfDoc.embedPng(fullWrapBuffer);
  page.drawImage(pngImage, {
    x: 0,
    y: 0,
    width: widthPt,
    height: heightPt,
  });

  const pdfBytes = await pdfDoc.save();
  const pdfPath = join(tmpdir(), `kdp-full-wrap-${Date.now()}.pdf`);
  await writeFile(pdfPath, pdfBytes);

  return { pdf_path: pdfPath, preview_path: previewPath, specs };
}
