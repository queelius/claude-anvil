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
  fantasy: "epic, atmospheric scene with rich color palette, magical elements, dramatic lighting",
  thriller: "dark, high-contrast imagery, urban or shadowy setting, sense of tension and danger",
  romance: "warm color palette, intimate atmosphere, evocative and emotionally charged imagery",
  "science fiction": "futuristic elements, cosmic or technological imagery, sleek and modern aesthetic",
  horror: "dark, unsettling atmosphere, muted colors with sharp contrasts, creepy imagery",
  mystery: "moody lighting, shadows, hints of intrigue, muted sophisticated color palette",
  literary: "elegant, understated design, artistic composition, subtle symbolism",
  technical: "clean, professional design, abstract geometric patterns or diagrams, modern typography",
  nonfiction: "clean, professional layout, relevant thematic imagery, authoritative feel",
};

export function buildCoverPrompt(input: CoverPromptInput): string {
  const artDirection = input.art_direction ?? getGenreDefault(input.genre);

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

  // gpt-image-1 in v6 supports: 1024x1024, 1536x1024, 1024x1536, auto
  // 1024x1536 is portrait — closest to a book cover aspect ratio
  // response_format is not supported for GPT image models; they always return b64
  let response;
  try {
    response = await client.images.generate({
      model: "gpt-image-1",
      prompt,
      n: 1,
      size: "1024x1536",
      quality: "high",
      output_format: "png",
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

  // Resize to requested dimensions using sharp
  const { default: sharp } = await import("sharp");
  const targetWidth = input.width ?? 1600;
  const targetHeight = input.height ?? 2560;
  const resized = await sharp(Buffer.from(imageData.b64_json, "base64"))
    .resize(targetWidth, targetHeight, { fit: "cover" })
    .png()
    .toBuffer();

  const outputPath = join(tmpdir(), `kdp-cover-${Date.now()}.png`);
  await writeFile(outputPath, resized);

  return outputPath;
}
