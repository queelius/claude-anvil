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
