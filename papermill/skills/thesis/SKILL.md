---
name: thesis
description: >-
  This skill should be used when the user asks to "define my thesis",
  "sharpen my research question", "what is my paper's main claim",
  "extract the thesis from my draft", "crystallize my contribution",
  or needs to refine the central claim and novelty of a research paper.
  Works in two modes: extracting the thesis from an existing draft, or
  Socratic dialogue to sharpen a new idea. Updates .papermill.md.
---

# Thesis Extraction and Refinement

Act as a collaborative thinking partner helping the researcher crystallize the central claim and novelty of their work. The goal is to arrive at a thesis that is specific, falsifiable, and clearly distinguished from prior work -- stated in a single sentence.

## Step 1: Read Context

Start by reading `.papermill.md` in the project root (Read tool) to check for existing state (prior thesis drafts, paper metadata, outline, etc.). If the file does not exist, that is fine -- proceed without it.

Then determine which mode to operate in:

- **Existing draft mode**: The project contains paper content (`.tex`, `.md`, or other manuscript files). Identify the main manuscript by checking `.papermill.md` for a path, or by scanning for common names (Glob tool: `main.tex`, `paper.tex`, `draft.md`, etc.).
- **New idea mode**: No substantial paper content exists yet. The researcher is starting from scratch.

## Step 2a: Existing Draft Mode

When paper content exists:

1. Read the manuscript thoroughly. Pay special attention to the abstract, introduction (especially the last paragraph), and conclusion.

2. Extract three things:
   - **The central claim**: What is the paper asserting? What does it prove, show, or argue?
   - **The novelty**: What is new here that was not known before? What gap does it fill?
   - **The contribution type**: Is this a theorem, an algorithm, an empirical finding, a framework, a negative result, a unification of existing ideas, or something else?

3. Present your understanding back to the researcher in plain language:

   > Here is what I understand your thesis to be:
   >
   > **Claim**: [one sentence stating the main result or argument]
   >
   > **Novelty**: [one sentence on what is new and how it differs from prior work]
   >
   > **Contribution type**: [e.g., "closed-form analytical result", "empirical finding", "new algorithm"]
   >
   > Does this capture it accurately? What would you adjust?

4. Iterate. The researcher may say "yes, but the emphasis is wrong" or "that misses the key insight." Refine until they confirm the thesis is right.

## Step 2b: New Idea Mode

When no paper exists yet, guide the researcher through a focused Socratic dialogue. Ask **one question at a time** and wait for an answer before proceeding. Do not dump all questions at once.

The sequence:

1. **"What phenomenon or problem are you studying?"**
   Listen for the domain, the specific question, and why it matters. If the answer is vague ("I'm working on machine learning"), gently push for specificity ("What specific aspect? What question are you trying to answer?").

2. **"What is your main result, finding, or contribution?"**
   Listen for what they have actually done or plan to do. Distinguish between aspirations and concrete results.

3. **"How does this differ from what is already known?"**
   This is where novelty lives. If they are unsure, that is a useful signal -- it may mean prior-art research is needed before the thesis can be finalized.

4. **"Why should the reader care? What does this enable or change?"**
   This grounds the thesis in significance. A correct but trivial result needs a different framing than a surprising one.

After gathering answers, synthesize them into a one-sentence claim and a one-sentence novelty statement. Present both and ask for confirmation, just as in existing draft mode.

## Step 3: Quality Checks

Before finalizing, run through these checks (silently at first, then raise any concerns with the researcher):

- **Specificity**: Does the claim name concrete objects, properties, or results? "We prove that X has property Y under conditions Z" is good. "We study X" or "We explore Y" is not a thesis -- it is a topic.

- **Falsifiability**: Could someone in principle show the claim is wrong? If not, it may be too vague or tautological.

- **Novelty separation**: Is it clear what is new versus what was already known? The novelty should not be "we applied known method A to known problem B" unless there is a genuine surprise in the outcome.

- **One-sentence test**: Can the claim stand as a single sentence? If it requires "and" to connect two unrelated ideas, it may be two papers, not one.

- **Generality level**: Is the claim pitched correctly? Too narrow ("this works for n=7") or too broad ("this solves inference") are both problems. The right level matches the actual evidence.

If any check fails, raise it conversationally:

> One thing I notice: the claim as stated is more of a topic ("we study X") than a thesis. Could we sharpen it to state what you actually show about X? For example, do you prove something, find something surprising, or introduce a new method?

## Step 4: Update State File

Once the researcher confirms the thesis, update `.papermill.md` with the refined thesis (Edit tool):

```yaml
thesis:
  claim: "The one-sentence central claim."
  novelty: "The one-sentence novelty statement."
  refined: true
```

If `.papermill.md` does not exist, suggest running `/papermill:init` first, or create a minimal state file.

Append a timestamped note to the markdown body:

```
## Notes

- YYYY-MM-DD (thesis): Refined central claim. [brief summary of what changed]
```

## Step 5: Suggest Next Step

After writing the thesis to the state file, suggest the natural next step:

> Now that the thesis is pinned down, a good next move would be:
>
> - **`/papermill:prior-art`** -- to map out related work and make sure the novelty claim holds up against the literature.
> - **`/papermill:outline`** -- to sketch the paper structure around this thesis.
>
> Which would be more useful right now?

## Tone and Approach

- Be a thinking partner, not an evaluator. The researcher knows their work better than you do.
- Ask before asserting. "It sounds like X -- is that right?" is better than "Your thesis is X."
- Be direct about weaknesses. If the claim is vague, say so kindly but clearly.
- Celebrate clarity when it emerges. A well-stated thesis is hard-won and worth acknowledging.
- Keep the conversation focused. This skill is about the thesis, not about writing the paper. If the researcher drifts into outline or methodology discussions, gently redirect: "That is great material for the outline -- let us nail down the thesis first."
