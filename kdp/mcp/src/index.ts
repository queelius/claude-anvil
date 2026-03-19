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
        content: [{ type: "text", text: JSON.stringify(result) }],
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
      .describe("Hex color for back cover background. If omitted, extracted from front cover."),
  },
  async (args) => {
    try {
      const result = await handleGenerateFullWrap(args);
      return {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
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
