import { writeFile } from "node:fs/promises";
import { join } from "node:path";
import { tmpdir } from "node:os";
import sharp from "sharp";
import { PDFDocument } from "pdf-lib";
import {
  calculateCoverDimensions,
  ensureContrast,
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

const SPINE_TOO_NARROW_INCHES = 0.3; // < 0.3" → no text
const SPINE_TITLE_ONLY_INCHES = 0.5; // 0.3"–0.5" → title only

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

  const escapedBlurb = escapeXml(blurb);
  const barcodeRect = isbn
    ? `<rect x="${barcodeX}" y="${barcodeY}" width="${barcodeW}" height="${barcodeH}" fill="white" rx="4"/>`
    : `<rect x="${barcodeX}" y="${barcodeY}" width="${barcodeW}" height="${barcodeH}" fill="white" rx="4" opacity="0.15"/>`;

  const svgString = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}">
  <rect width="${width}" height="${height}" fill="${bgColor}"/>
  <foreignObject x="${marginPx}" y="${marginPx}" width="${textWidth}" height="${textAreaHeight}">
    <body xmlns="http://www.w3.org/1999/xhtml" style="margin:0;padding:0;">
      <p style="font-family:serif;font-size:${fontSize}px;color:white;line-height:1.5;word-wrap:break-word;">${escapedBlurb}</p>
    </body>
  </foreignObject>
  ${barcodeRect}
</svg>`;

  // sharp may not support foreignObject/xhtml — use plain SVG text with tspan wrapping instead
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
  const canvas = sharp({
    create: {
      width: totalW,
      height: totalH,
      channels: 3,
      background: { r: 0, g: 0, b: 0 },
    },
  });

  // ── Resize front cover to fit front zone ───────────────────────────────
  const frontBuffer = await sharp(input.front_cover_path)
    .resize(frontZone.width, frontZone.height, { fit: "cover" })
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
    // Front cover
    {
      input: frontBuffer,
      left: frontZone.x,
      top: frontZone.y,
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
