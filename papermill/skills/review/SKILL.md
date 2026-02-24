---
name: review
description: >-
  This skill should be used when the user asks to "review my paper",
  "give me feedback on my draft", "editorial review", "is my paper
  ready to submit", "check my paper for issues", or needs structured
  editorial feedback on a paper draft. Launches a multi-agent review
  system with 8 specialists (2 literature scouts + 6 domain reviewers)
  orchestrated by an area chair agent. Produces a unified report in
  .papermill/reviews/. Updates .papermill/state.md.
---

# Multi-Agent Editorial Review

Launch a comprehensive multi-agent review of a research paper. The review system uses 8 specialist agents orchestrated by an area chair to evaluate logic, novelty, methodology, prose, citations, and formatting — grounded in literature context.

## Step 1: Read Context

Read `.papermill/state.md` (Read tool) for:
- **Thesis**: What the paper claims (the review checks if the paper delivers).
- **Venue**: Target venue (review against its standards).
- **Review history**: Previous reviews and their findings.
- **Format**: Paper format (latex, markdown, rmarkdown).

If `.papermill/state.md` does not exist, the review can still proceed by reading the manuscript directly — but the review will be less targeted without thesis and venue context. Note this limitation to the user and suggest running `/papermill:init` first for best results.

## Step 2: Identify the Manuscript

Locate the manuscript files:
1. Check `.papermill/state.md` for format and any recorded manuscript path.
2. Scan for manuscript files (Glob tool): `*.tex`, `*.Rmd`, `paper.md`, `manuscript.md`.
3. Identify the main file and any supporting files (bibliography, figures, included files).

Read the manuscript to confirm it has enough content for review.

## Step 3: Ask for Focus Areas

Before launching the review, ask the user:

> I'll launch a multi-agent review with specialists covering:
> - **Logic & proofs** — mathematical correctness and argument structure
> - **Novelty** — contribution evaluation against the literature
> - **Methodology** — experimental design and statistical rigor
> - **Prose** — writing quality and narrative structure
> - **Citations** — reference accuracy and completeness
> - **Formatting** — build verification and venue compliance
>
> Are there specific areas you want me to focus on, or should I run the full review?

If the user specifies focus areas, note them for the orchestrator. If they want the full review, proceed with all specialists.

## Step 4: Launch the Reviewer Orchestrator

Launch the **reviewer** agent (Task tool with `subagent_type: "papermill:reviewer"`).

Pass the agent:
- Path to the manuscript file(s)
- Path to `.papermill/state.md` (if it exists)
- Any user-specified focus areas or tone preferences
- The thesis statement and target venue (if known)

The agent will:
1. Read the paper and produce a comprehension summary
2. Spawn 2 literature scouts in parallel for field context
3. Spawn 6 specialist reviewers in parallel
4. Cross-verify critical findings
5. Write individual specialist reports and a unified report to `.papermill/reviews/YYYY-MM-DD/`

## Step 5: Present Results

After the agent completes, read `.papermill/reviews/YYYY-MM-DD/review.md` (Read tool).

Present a summary to the user:

> **Review Complete**
>
> **Recommendation**: [ready | minor-revision | major-revision | not-ready]
>
> | Severity | Count |
> |----------|-------|
> | Critical | N |
> | Major | M |
> | Minor | P |
> | Suggestions | Q |
>
> **Top findings:**
> 1. [Most important finding]
> 2. [Second most important finding]
> 3. [Third most important finding]
>
> The full report is at `.papermill/reviews/YYYY-MM-DD/review.md`.
> Individual specialist reports are in the same directory.

Then ask: "Would you like to go through the findings in detail, or address the critical issues first?"

## Step 6: Update State File

Update `.papermill/state.md` (Edit tool):

Add a review record to `review_history`:

```yaml
review_history:
  - date: "YYYY-MM-DD"
    type: "multi-agent-review"
    findings_major: N
    findings_minor: M
    recommendation: "ready | minor-revision | major-revision | not-ready"
    notes: "Brief summary of key findings"
    report_path: ".papermill/reviews/YYYY-MM-DD/review.md"
```

Append a timestamped note to the markdown body.

## Step 7: Suggest Next Steps

Based on the recommendation, suggest the most relevant next step:

- **Ready for submission** → `/papermill:polish` to prepare, then `/papermill:venue` if no venue is selected yet.
- **Minor revision** → Address the minor issues, then re-run `/papermill:review`.
- **Major revision** → Address major issues first. If issues are structural, suggest `/papermill:outline`. If issues are with the argument, suggest `/papermill:thesis`. Then re-run `/papermill:review`.
- **Not ready** → Identify the root cause. Weak thesis → `/papermill:thesis`. Insufficient evidence → `/papermill:experiment` or `/papermill:simulation`. Missing related work → `/papermill:prior-art`. Proof gaps → `/papermill:proof`.
