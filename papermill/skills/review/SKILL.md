---
name: review
description: >-
  This skill should be used when the user asks to "review my paper",
  "give me feedback on my draft", "editorial review", "is my paper
  ready to submit", "check my paper for issues", or needs structured
  editorial feedback on a paper draft. Evaluates argument, correctness,
  writing quality, and venue fit. Produces severity-ranked findings.
  Updates .papermill.md. Can launch the reviewer agent for deeper
  autonomous review.
---

# Editorial Review

Conduct a thorough editorial review of a research paper. The goal is to provide actionable feedback that helps the author improve the paper before submission. Be honest, specific, and constructive.

## Step 1: Read Context

Read `.papermill.md` (Read tool) for:
- **Thesis**: What the paper claims (the review should check if the paper delivers on this claim).
- **Venue**: Target venue (review against its standards and conventions).
- **Review history**: Any previous reviews and their findings.

If `.papermill.md` does not exist, the review can still proceed by reading the manuscript directly — but the review will be less targeted without thesis and venue context. Note this limitation to the user and suggest running `/papermill:init` first for best results.

Read the complete manuscript (Read tool).

## Step 2: Review Dimensions

Evaluate the paper along these dimensions, in order:

### Argument and Logic
- Is the main claim clearly stated and supported?
- Does the paper deliver on its promises (abstract matches content)?
- Is the logical flow from problem to method to results to conclusion sound?
- Are all assumptions explicitly stated?
- Are proofs correct? (Check key steps, not just skim.)

### Technical Correctness
- Are equations correct? Check dimensions, boundary cases, and signs.
- Are statistical methods applied correctly?
- Are experimental results reproducible from the description?
- Are baselines appropriate and fairly compared?

### Writing Quality
- Is the abstract self-contained and informative?
- Is the introduction motivating?
- Are definitions introduced before use?
- Is notation consistent throughout?
- Are figures and tables clear and well-captioned?
- Is the paper the right length for the venue?

### Related Work
- Is the literature coverage adequate?
- Is the paper's contribution clearly differentiated from prior work?
- Are citations accurate (right paper, right claim)?

### Venue Fit
- Does the paper match the venue's scope?
- Does it follow the venue's formatting requirements?
- Is the contribution significant enough for this venue?

## Step 3: Present Findings

Organize findings by severity:

### Major Issues
Problems that would likely cause rejection or require significant revision. These must be addressed.

### Minor Issues
Problems that should be fixed but do not undermine the paper's core contribution.

### Suggestions
Optional improvements that would strengthen the paper.

For each finding:
1. **Location**: Section, page, or line number.
2. **Issue**: What the problem is.
3. **Suggestion**: How to fix it.

Example:

> **[Major] Section 3.2, Theorem 3.1**: The proof assumes X is positive definite (line 4 of proof), but this was not established. Either add a lemma proving positive definiteness under the stated assumptions, or add it as an explicit condition.

## Step 4: Summary Assessment

Provide a brief overall assessment:

> **Overall**: [1-2 sentence summary of paper quality]
>
> **Strengths**: [2-3 bullet points]
>
> **Weaknesses**: [2-3 bullet points]
>
> **Recommendation**: [ready for submission / needs minor revision / needs major revision / not ready]

## Step 5: Update State File

Update `.papermill.md` (Edit tool):

Add a review record to `review_history`:

```yaml
review_history:
  - date: "YYYY-MM-DD"
    type: "self-review"
    findings_major: N
    findings_minor: M
    recommendation: "ready | minor-revision | major-revision | not-ready"
    notes: "Brief summary of key findings"
```

Append a timestamped note to the markdown body.

## Step 6: Offer Deep Review

For a more thorough autonomous review, offer to launch the **reviewer agent** (Task tool with `subagent_type: "papermill:reviewer"`):

> I can launch the reviewer agent for a deeper review pass. It will systematically check every theorem, equation, and citation. Would you like me to launch it?

When launching, pass the agent:
- Path to the manuscript file(s)
- The thesis statement from `.papermill.md`
- The target venue (if known)
- Any specific focus areas the user requested

The agent writes its results to `.papermill-review-results.md` in the project root. After it completes:

1. Read `.papermill-review-results.md` (Read tool).
2. Present a summary of findings to the user (major issue count, minor issue count, recommendation).
3. Merge the agent's findings into the review record in `.papermill.md` — update the `review_history` entry created in Step 5 with the combined counts and recommendation.
4. Ask the user which issues to address first.

## Step 7: Suggest Next Steps

Based on the recommendation, suggest the most relevant next step:

- **Ready for submission** → `/papermill:polish` to prepare, then `/papermill:venue` if no venue is selected yet.
- **Minor revision** → Address the minor issues, then re-run `/papermill:review`.
- **Major revision** → Address major issues first. If issues are structural, suggest `/papermill:outline`. If issues are with the argument, suggest `/papermill:thesis`. Then re-run `/papermill:review`.
- **Not ready** → Identify the root cause. Weak thesis → `/papermill:thesis`. Insufficient evidence → `/papermill:experiment` or `/papermill:simulation`. Missing related work → `/papermill:prior-art`. Proof gaps → `/papermill:proof`.
