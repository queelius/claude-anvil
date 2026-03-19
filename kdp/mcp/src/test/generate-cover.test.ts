import { describe, it, expect, vi, beforeEach } from "vitest";
import { buildCoverPrompt } from "../lib/openai-client.js";
import { handleGenerateCover } from "../tools/generate-cover.js";
import * as openaiClient from "../lib/openai-client.js";

describe("buildCoverPrompt", () => {
  it("includes title and author in prompt", () => {
    const prompt = buildCoverPrompt({
      title: "The Silent Policy",
      author_name: "Alex Towell",
      genre: "technical",
    });
    expect(prompt).toContain("The Silent Policy");
    expect(prompt).toContain("Alex Towell");
  });

  it("includes subtitle when provided", () => {
    const prompt = buildCoverPrompt({
      title: "Echoes of the Sublime",
      subtitle: "A Journey Through Mathematics",
      author_name: "Alex Towell",
      genre: "technical",
    });
    expect(prompt).toContain("A Journey Through Mathematics");
  });

  it("uses art direction when provided", () => {
    const prompt = buildCoverPrompt({
      title: "Test Book",
      author_name: "Test Author",
      genre: "fantasy",
      art_direction: "dark moody forest with a glowing rune",
    });
    expect(prompt).toContain("dark moody forest with a glowing rune");
  });

  it("generates genre-appropriate prompt when no art direction", () => {
    const prompt = buildCoverPrompt({
      title: "Test Book",
      author_name: "Test Author",
      genre: "thriller",
    });
    expect(prompt.length).toBeGreaterThan(50);
    expect(prompt).toContain("Test Book");
  });
});

describe("handleGenerateCover", () => {
  it("returns path from generateCoverImage", async () => {
    vi.spyOn(openaiClient, "generateCoverImage").mockResolvedValue(
      "/tmp/kdp-cover-mock.png",
    );

    const result = await handleGenerateCover({
      title: "Test",
      author_name: "Author",
      genre: "fantasy",
    });

    expect(result).toEqual({ path: "/tmp/kdp-cover-mock.png" });
  });

  it("passes default dimensions when not specified", async () => {
    const spy = vi
      .spyOn(openaiClient, "generateCoverImage")
      .mockResolvedValue("/tmp/mock.png");

    await handleGenerateCover({
      title: "Test",
      author_name: "Author",
      genre: "fantasy",
    });

    expect(spy).toHaveBeenCalledWith(
      expect.objectContaining({ width: 1600, height: 2560 }),
    );
  });

  it("propagates errors from generateCoverImage", async () => {
    vi.spyOn(openaiClient, "generateCoverImage").mockRejectedValue(
      new Error("OPENAI_API_KEY environment variable is not set."),
    );

    await expect(
      handleGenerateCover({
        title: "Test",
        author_name: "Author",
        genre: "fantasy",
      }),
    ).rejects.toThrow("OPENAI_API_KEY");
  });
});
