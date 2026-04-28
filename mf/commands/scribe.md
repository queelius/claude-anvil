---
name: scribe
description: "Discover latent themes in the metafunctor corpus. Reads titles + descriptions, proposes 3 themes that connect 4+ posts each, with a single-sentence through-line per theme. Output is a proposal, not a draft."
---

# /scribe

The smallest useful agent: find threads in your own corpus that you didn't realize you'd already written.

## What this does (and doesn't)

**Does**: scans every post in `content/post/`, returns 3 candidate themes that connect at least 4 posts each, each with a one-sentence through-line and a list of source posts.

**Does NOT**: write a draft. The output is a proposal you accept or reject. If you accept one, you tell me to expand it; we iterate from there. The smallest scribe stops at "here are the candidates."

This is intentional. Voice fidelity is hard. Validating that the corpus has interesting structure is easy. Do the easy thing first; if the candidates feel real, we build the drafting layer next.

## Workflow

### 1. Read the corpus

Use the `crier_search` MCP tool to get metadata for every post:

```
crier_search(limit=300)   # all posts; metafunctor has ~200, headroom for growth
```

If `crier_search` returns truncated content, fall back to listing files via `Glob` against `~/github/repos/metafunctor/content/post/**/index.md` and reading front matter directly. You only need: title, date, description, tags. Don't read the body for the smallest scribe.

You can optionally filter:
- `/scribe 5y` (last 5 years; useful for narrowing a 200+ post corpus)
- `/scribe --tag philosophy` (filter to a tag's universe)

Default is the full corpus.

### 2. Find themes

Look at all the title + description + tag triples together. Resist clustering by tag alone (tags are too coarse). Find threads that satisfy:

- **Span**: connects 4+ posts (3 is too few; 6+ is ideal).
- **Specificity**: the through-line is a *claim* or *observation*, not a *category*. "Intelligence is verifiable search" is a thread. "AI" is not.
- **Latency**: the user did not consciously frame these posts as a series. If they're already a tagged series (e.g., the "Stepanov" series, the "Long Echo" series, the "RL series"), skip those. We're looking for *implicit* threads.
- **Cross-temporal**: bonus if the thread spans multiple years; that's strong evidence the user keeps returning to the idea unconsciously.

For each candidate theme:
- Pick the 4 to 7 most representative posts (not all posts that mention the theme).
- Write the through-line as a single declarative sentence in the user's voice. Specific, not generic. "Reward shape determines what scales" beats "the user thinks about reward functions."

### 3. Output the proposal

Format:

```
3 candidate themes (95 posts scanned):

═══════════════════════════════════════════════════════════════════
[1] VERIFIABLE SEARCH AS THE ARCHITECTURE OF INTELLIGENCE

Through-line: You keep returning to the asymmetry between checking and
finding, applied to science, ML training, test-time compute, and
induction itself.

Span: 5 posts, 2024-09 to 2026-04 (19 months)

Source posts:
  - 2025-01-05  Science as Verifiable Search
  - 2024-09-30  All Induction Is the Same Induction
  - 2024-06-25  Reverse-Process Synthetic Data Generation
  - 2026-04-01  I Spent $0.48 to Find Out When MCTS Actually Works
  - 2026-03-15  What You Assume vs. What You Compute

Why it's a thread: each one is "easy to verify, hard to find" applied
to a different domain. You haven't named the asymmetry directly.
═══════════════════════════════════════════════════════════════════
[2] LEGACY AS A DESIGN CONSTRAINT
...
═══════════════════════════════════════════════════════════════════
[3] CODE WITHOUT PURPOSE / PURPOSE WITHOUT CODE
...

Pick a theme to develop (1, 2, 3) | Reject all (none feel real) | Show me more themes (regenerate)
```

### 4. Stop

That's the smallest scribe. After this, the user picks one and either:

- Asks you to expand it: propose a structure, sample paragraph, source-post mapping. (This is the "scribe iterative" loop, not yet built.)
- Rejects all and asks for more candidates.
- Says one is interesting but the framing is off and renames it.

For the smallest version, your job ends at presenting the three. Don't auto-expand. The user is the editor.

## Quality bar

The output should pass these tests before you show it:

1. **Each through-line is one sentence.** If it takes two sentences to explain, the theme isn't crisp enough.
2. **Each through-line is specific.** A reader who hasn't seen the posts should be able to predict roughly what the synthesis would argue.
3. **The source posts are chosen, not exhaustive.** Don't list every post that mentions a tag. List the 4 to 7 that *make the thread*.
4. **No themes that are already explicit series.** The user knows about their Stepanov series. Don't propose it back to them.
5. **No "AI/ML topics" or "philosophy posts" themes.** Those are categories. We want claims.

If you can't generate three themes that pass all five tests, return fewer (or zero) and explain why. "Two themes feel real, one feels forced; here are the two." Better than padding.

## What to do when scribe fails

If the corpus genuinely doesn't have three threads, that's useful information. Possible causes:

- The corpus is too small (you'd see this on a 30-post blog, not a 200-post one).
- Tags are too coarse to filter usefully; suggest the user tag with more discrimination.
- The user's thinking has been very project-focused (each post is its own thing) without recurring abstractions; that's a reflection on the writing, not a bug.

Report this honestly. Do not invent a theme to fill the slot.

## When to use other things instead

- **Already know the theme**, just want help with the synthesis: skip scribe, use `/mf` with intent "synthesis post about X."
- **Want to find unposted gaps in cross-posting**: that's `/chronicler`, not scribe.
- **Want to audit cross-posting status**: dispatch the `auditor` agent.
- **Want to draft a brand-new post on a fresh topic** (not synthesis): regular Claude Code, no special command needed.

## Future versions (do NOT implement in the smallest scribe)

The smallest scribe stops at theme proposal. Future iterations would add:

- **Iterative drafting**: theme → outline → sample paragraph → user grades voice → expand section by section.
- **Link graph signal**: actually parse internal links between posts to find anchor posts and co-citations. The smallest version uses LLM clustering only.
- **Tag refinement suggestions**: "your tags are too coarse; here are 8 finer-grained tags I'd add."
- **Cross-pollination**: "this old post about X is relevant to the new conversation about Y."

These are bigger features and need user feedback on the smallest version first. If candidates from the smallest scribe feel real, we keep building. If they don't, we change the signal (link graph, embeddings) before adding drafting.
