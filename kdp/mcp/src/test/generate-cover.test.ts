import { describe, it, expect, vi, beforeEach } from "vitest";
import { buildCoverPrompt } from "../lib/openai-client.js";

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
