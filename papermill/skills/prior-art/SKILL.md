---
name: prior-art
description: >-
  This skill should be used when the user asks to "survey related work",
  "find prior art", "literature review", "what papers are related to mine",
  "search for references", or needs to conduct a systematic literature
  survey. Reads thesis from .papermill.md, searches academic sources,
  classifies references, identifies gaps, generates BibTeX, and updates
  the state file. Can launch the surveyor agent for deep autonomous search.
---

# Prior Art: Systematic Literature Survey

Conduct a **collaborative, iterative** literature survey with the user. This is not a one-shot dump of references -- work together to map the landscape of existing work, identify gaps, and position the user's contribution.

## Step 1: Read Context

Begin by gathering everything you need to understand the research context.

1. **Read `.papermill.md`** in the project root (Read tool), if it exists. Extract:
   - The thesis statement and core contribution.
   - Any existing `prior_art` entries (key references, gaps, last survey date).
   - The paper's target venue, discipline, and methodology.

   If `.papermill.md` does not exist, the survey can still proceed — ask the user to describe their research topic and thesis directly. Suggest running `/papermill:init` afterward to persist the results.

2. **Read existing `.bib` file(s)** (Glob/Read tools). Scan for all BibTeX files in the project (commonly `references.bib`, `paper/references.bib`, or similar). These are seed references. Parse out author names, titles, years, and keywords -- these seeds will anchor the search.

3. **Summarize your understanding** back to the user before proceeding. Confirm: "Here is what I understand your paper is about, and here are the N existing references I found. Shall I begin the survey from this starting point?"

Do NOT skip the confirmation step. The user may want to adjust scope, add keywords, or exclude certain directions.

## Step 2: Keyword Generation

From the thesis and seed references, derive **5-10 search queries** with:

- **Varying specificity**: Some broad (field-level), some narrow (method + application).
- **Synonym coverage**: Use alternative terminology for the same concept. Different communities use different vocabulary for the same ideas.
- **Author-based queries**: Include searches for key authors from seed references to find their related work.

Present the proposed queries to the user. Ask: "Are there additional terms, subfields, or authors I should include? Any directions to exclude?"

Revise the query list based on feedback before searching.

## Step 3: Search

Use **WebSearch** (WebSearch tool) to query academic sources. For each search query, formulate searches targeting:

- Google Scholar (general academic coverage)
- arXiv (preprints, especially for CS/math/physics/statistics)
- Semantic Scholar (structured metadata, citation graphs)

Use **multiple formulations per concept** -- rephrase, use synonyms, try with and without quotes around key phrases. Academic search is noisy; redundancy is essential.

For each query, collect the top results. Do not chase every link. Focus on results that appear in multiple searches or that are highly cited.

## Step 4: Screen Candidates

For each candidate result, extract and present:

| Field | Description |
|-------|-------------|
| **Title** | Full title of the work |
| **Authors** | First author et al. (or all if few) |
| **Year** | Publication year |
| **Venue** | Journal, conference, or preprint server |
| **Summary** | 1-2 sentence abstract summary focused on relevance to the user's thesis |
| **Relevance** | Brief note on why this may matter for the user's paper |

Do NOT fabricate citations. If you cannot verify a reference exists, say so explicitly. Mark any reference you are uncertain about with "[unverified]" and suggest the user confirm it.

## Step 5: Classify References

Categorize each relevant reference into one of four classes:

- **Foundational**: Established the field, method, or theoretical framework the user builds on. These typically appear in the introduction and background sections.

- **Competing**: Addresses the **same problem** as the user but with a different approach. These require the most careful discussion. They appear in the related work section and sometimes in the discussion.

- **Complementary**: Addresses a **related but distinct** problem. The user's work could combine with theirs, or theirs provides tools/data the user leverages.

- **Tangential**: Loosely related. Useful for context but not central. Include sparingly.

Present your classification rationale. The user may reclassify references, and that is expected and valuable.

## Step 6: Present Findings in Batches

**Show 3-5 references at a time.** For each batch:

1. Present the references with their extracted metadata and proposed classification.
2. Ask the user:
   - "Which of these are relevant? Should any be reclassified?"
   - "Do any of these suggest new search directions I should pursue?"
   - "Should I go deeper into any particular reference's citation network?"
3. Record the user's decisions.

**Iterate.** Run additional searches based on what you learn. Follow citation chains: if a confirmed reference cites something interesting, pursue it. If a confirmed reference is cited by many others, look at the citers.

Continue until the user says the coverage is sufficient or you have exhausted productive search directions.

## Step 7: Gap Analysis

After accumulating confirmed references, synthesize a **gap analysis**:

1. **What questions does prior work answer?** Summarize the state of knowledge.
2. **What questions remain open?** Identify specific gaps, limitations, or unresolved problems.
3. **How does the user's thesis fill those gaps?** This is the paper's positioning.
4. **What assumptions or limitations does the user's approach share with prior work?**

Present this as a structured summary. This analysis directly feeds into the paper's introduction and related work sections.

## Step 8: Generate BibTeX

For each confirmed reference that is **not already in the .bib file**:

1. Generate a well-formed BibTeX entry with a consistent citation key style (match the existing .bib file's conventions).
2. Include at minimum: author, title, year, and venue.
3. Include DOI or URL when available.
4. Present the entries to the user for approval before writing.

After approval, append the new entries to the appropriate `.bib` file (Edit tool).

## Step 9: Update State File

Update `.papermill.md` (Edit tool) with:

- **`prior_art.key_references`**: Add each confirmed reference with citation key, classification, and a one-sentence relation description.
- **`prior_art.last_survey`**: Set to today's date.
- **`prior_art.gaps`**: A concise summary of identified gaps.

Append a timestamped note to the markdown body documenting the survey.

## Step 10: Offer Deep Search

If the user wants broader coverage, offer to launch the **surveyor agent** (Task tool with `subagent_type: "papermill:surveyor"`):

> I can launch the surveyor agent for a deeper autonomous search. It will systematically explore citation networks and compile an extended reference list. Would you like me to launch it?

Only offer this after the interactive survey has established a solid baseline.

When launching, pass the agent:
- The thesis statement
- Seed references (existing `.bib` entries or key papers confirmed so far)
- The search queries from Step 2 (plus any new ones discovered during the survey)
- The current gap analysis from Step 7

The agent writes its results to `.papermill-survey-results.md` in the project root. After it completes:

1. Read `.papermill-survey-results.md` (Read tool).
2. Present a summary to the user (number of new references by category, updated gap analysis).
3. Ask the user to confirm which new references to keep — present them in batches of 3-5, same as Step 6.
4. Append confirmed BibTeX entries to the `.bib` file (Edit tool).
5. Update `prior_art` in `.papermill.md` with any new key references and the refined gap analysis (Edit tool).

## Step 11: Final Summary

Close with a structured summary:

> **Survey Summary**
> - References found: N total (F foundational, C competing, X complementary)
> - New BibTeX entries added: M
> - Key gaps identified: [list]
> - Suggested positioning: [1-2 sentences]
> - Coverage assessment: [honest assessment of completeness]

## Step 12: Suggest Next Steps

Based on what the survey revealed, suggest the most relevant next step:

- If the survey exposed that the thesis overlaps heavily with existing work or needs sharpening → "The literature suggests your thesis may need refinement. Consider running `/papermill:thesis` to sharpen the claim."
- If the survey provides enough context to structure the paper → `/papermill:outline`
- If the paper needs experiments to differentiate from competing work → `/papermill:experiment`
- If the paper is already drafted and needs feedback → `/papermill:review`

## Ground Rules

- **Never fabricate references.** If you are unsure whether a paper exists, say so. Hallucinated citations are worse than missing ones.
- **Always confirm with the user** before writing to any file.
- **Respect the user's time.** Batched presentation (3-5 at a time) prevents information overload.
- **Follow citation trails.** The best references are often found by examining who cites whom.
- **Maintain intellectual honesty.** If the user's thesis overlaps heavily with existing work, say so clearly.
