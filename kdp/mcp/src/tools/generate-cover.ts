import { generateCoverImage } from "../lib/openai-client.js";

export interface GenerateCoverInput {
  title: string;
  subtitle?: string;
  author_name: string;
  genre: string;
  art_direction?: string;
  width?: number;
  height?: number;
}

export async function handleGenerateCover(
  input: GenerateCoverInput,
): Promise<{ path: string }> {
  const path = await generateCoverImage({
    title: input.title,
    subtitle: input.subtitle,
    author_name: input.author_name,
    genre: input.genre,
    art_direction: input.art_direction,
    width: input.width ?? 1600,
    height: input.height ?? 2560,
  });

  return { path };
}
