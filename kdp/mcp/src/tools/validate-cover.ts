import { stat } from "node:fs/promises";
import sharp from "sharp";
import { handleCoverSpecs, type CoverSpecsOutput } from "./cover-specs.js";

// ── Types ──────────────────────────────────────────────────────────────────

export type CoverKind = "ebook" | "paperback_front" | "full_wrap";

export interface ValidateCoverInput {
  cover_path: string;
  kind: CoverKind;
  page_count?: number;
  trim_size?: string;
  paper_type?: string;
}

export interface CoverCheck {
  name: string;
  status: "pass" | "fail" | "warn";
  expected: string;
  actual: string;
  note?: string;
}

export interface ValidateCoverOutput {
  valid: boolean;
  kind: CoverKind;
  checks: CoverCheck[];
  specs?: CoverSpecsOutput;
}

// ── Constants (KDP requirements; see docs/kdp-reference.md) ────────────────

const EBOOK_MIN_LONGEST_SIDE = 1000; // hard minimum
const EBOOK_RECOMMENDED_W = 1600;
const EBOOK_RECOMMENDED_H = 2560;
const EBOOK_RATIO = 1.6; // height / width
const EBOOK_RATIO_TOLERANCE = 0.08;
const EBOOK_MAX_BYTES = 50 * 1024 * 1024;
const PRINT_DPI = 300;
const PX_TOLERANCE = 4; // rounding slack when comparing against computed specs

// ── Helpers ────────────────────────────────────────────────────────────────

function check(
  name: string,
  ok: boolean,
  expected: string,
  actual: string,
  opts: { warnOnly?: boolean; note?: string } = {},
): CoverCheck {
  return {
    name,
    status: ok ? "pass" : opts.warnOnly ? "warn" : "fail",
    expected,
    actual,
    ...(opts.note ? { note: opts.note } : {}),
  };
}

function within(actual: number, expected: number, tol: number): boolean {
  return Math.abs(actual - expected) <= tol;
}

// ── handleValidateCover ────────────────────────────────────────────────────

export async function handleValidateCover(
  input: ValidateCoverInput,
): Promise<ValidateCoverOutput> {
  const meta = await sharp(input.cover_path).metadata();
  const fileBytes = (await stat(input.cover_path)).size;
  const width = meta.width ?? 0;
  const height = meta.height ?? 0;
  const checks: CoverCheck[] = [];
  let specs: CoverSpecsOutput | undefined;

  if (input.kind === "ebook") {
    const longest = Math.max(width, height);
    checks.push(
      check(
        "hard minimum size",
        longest >= EBOOK_MIN_LONGEST_SIDE,
        `longest side >= ${EBOOK_MIN_LONGEST_SIDE}px`,
        `${width}x${height}`,
      ),
    );
    checks.push(
      check(
        "recommended size",
        width >= EBOOK_RECOMMENDED_W && height >= EBOOK_RECOMMENDED_H,
        `>= ${EBOOK_RECOMMENDED_W}x${EBOOK_RECOMMENDED_H}px (WxH)`,
        `${width}x${height}`,
        { warnOnly: true },
      ),
    );
    const ratio = width > 0 ? height / width : 0;
    checks.push(
      check(
        "aspect ratio",
        within(ratio, EBOOK_RATIO, EBOOK_RATIO_TOLERANCE),
        `height/width ~ ${EBOOK_RATIO}`,
        ratio.toFixed(3),
        { warnOnly: true, note: "portrait 1:1.6 is the KDP recommendation" },
      ),
    );
    checks.push(
      check(
        "file format",
        meta.format === "jpeg" || meta.format === "tiff",
        "jpeg or tiff",
        meta.format ?? "unknown",
        {
          warnOnly: meta.format === "png",
          note:
            meta.format === "png"
              ? "PNG usually uploads but KDP documents JPEG/TIFF"
              : undefined,
        },
      ),
    );
    checks.push(
      check(
        "color channels",
        (meta.channels ?? 0) >= 3,
        "RGB (3+ channels)",
        String(meta.channels ?? "unknown"),
      ),
    );
    checks.push(
      check(
        "file size",
        fileBytes < EBOOK_MAX_BYTES,
        "< 50MB",
        `${(fileBytes / (1024 * 1024)).toFixed(1)}MB`,
      ),
    );
  } else {
    // Print kinds need the layout specs to compare against.
    if (input.page_count === undefined) {
      throw new Error(
        `kind "${input.kind}" requires page_count (and optionally trim_size, paper_type) to compute expected dimensions`,
      );
    }
    specs = handleCoverSpecs({
      page_count: input.page_count,
      trim_size: input.trim_size,
      paper_type: input.paper_type,
    });

    if (input.kind === "full_wrap") {
      checks.push(
        check(
          "wrap width",
          within(width, specs.total_width_px, PX_TOLERANCE),
          `${specs.total_width_px}px (2 x trim + spine + 2 x bleed at ${PRINT_DPI} DPI)`,
          `${width}px`,
        ),
      );
      checks.push(
        check(
          "wrap height",
          within(height, specs.total_height_px, PX_TOLERANCE),
          `${specs.total_height_px}px (trim + 2 x bleed at ${PRINT_DPI} DPI)`,
          `${height}px`,
        ),
      );
    } else {
      // paperback_front: the front zone plus its share of the bleed.
      const bleedPx = Math.round(specs.bleed_inches * PRINT_DPI);
      const trimW = specs.front_zone.width;
      const trimH = specs.front_zone.height;
      const wOk =
        within(width, trimW, PX_TOLERANCE) ||
        within(width, trimW + bleedPx, PX_TOLERANCE);
      const hOk =
        within(height, trimH, PX_TOLERANCE) ||
        within(height, trimH + 2 * bleedPx, PX_TOLERANCE);
      checks.push(
        check(
          "front width",
          wOk,
          `${trimW}px (trim) or ${trimW + bleedPx}px (with outer bleed)`,
          `${width}px`,
        ),
      );
      checks.push(
        check(
          "front height",
          hOk,
          `${trimH}px (trim) or ${trimH + 2 * bleedPx}px (with bleed)`,
          `${height}px`,
        ),
      );
    }

    const density = meta.density;
    checks.push(
      check(
        "print resolution",
        density === undefined || density >= PRINT_DPI,
        `>= ${PRINT_DPI} DPI`,
        density === undefined ? "not embedded" : `${density} DPI`,
        {
          warnOnly: density === undefined,
          note:
            density === undefined
              ? "no density metadata; pixel-dimension checks above are the authoritative signal"
              : undefined,
        },
      ),
    );
    checks.push(
      check(
        "color channels",
        (meta.channels ?? 0) >= 3,
        "RGB (3+ channels; KDP converts to CMYK)",
        String(meta.channels ?? "unknown"),
      ),
    );
  }

  return {
    valid: checks.every((c) => c.status !== "fail"),
    kind: input.kind,
    checks,
    ...(specs ? { specs } : {}),
  };
}
