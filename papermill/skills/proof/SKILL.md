---
name: proof
description: >-
  This skill should be used when the user asks to "help me prove this
  theorem", "check my proof", "verify this proof is correct", "develop
  a proof for", "is this proof rigorous", or needs to develop, verify,
  or refine mathematical proofs. Guides proof strategy selection, checks
  logical correctness, identifies gaps, and helps with clear mathematical
  writing. Works with existing proof drafts or constructs from scratch.
---

# Proof Development

Act as a mathematical collaborator helping the researcher develop, verify, and present proofs. The role is to ensure logical correctness, identify gaps, and help write proofs that are both rigorous and readable.

## Step 1: Read Context

Read `.papermill.md` (Read tool) for the thesis and paper context, if it exists. Read any existing proofs in the manuscript (Read tool).

If `.papermill.md` does not exist, proceed directly — proof development works from the theorem statement itself. Suggest running `/papermill:init` afterward to track proof status.

Understand what needs proving:
- Is this a new proof to construct from scratch?
- Is this an existing proof draft to verify and refine?
- Is this a proof that needs to be simplified or restructured for the paper?

## Step 2: Understand the Statement

Before working on any proof, make sure the statement being proved is precise:

1. **Read the theorem/proposition/lemma statement carefully.** Identify all quantifiers, assumptions, and conclusions.
2. **Check definitions.** Are all terms defined? Are the definitions the standard ones, or does this paper use non-standard conventions?
3. **Identify the proof obligations.** What exactly must be shown? For "if and only if" statements, both directions. For "for all," a universal argument. For existence, a construction or existence argument.

Present your understanding: "Here is what I understand needs to be proved: [statement in plain language]. Is that correct?"

## Step 3: Select Proof Strategy

Common strategies and when to use them:

| Strategy | When to use |
|----------|------------|
| **Direct proof** | The conclusion follows naturally from the hypotheses by algebraic manipulation or logical deduction |
| **Contradiction** | The negation of the conclusion leads to an impossibility |
| **Contrapositive** | Proving "not Q implies not P" is easier than "P implies Q" |
| **Induction** | The statement is indexed by natural numbers or has recursive structure |
| **Construction** | An existence proof where you build the object explicitly |
| **Counting/combinatorial** | The result involves counting, probabilities, or combinatorial identities |
| **Approximation** | Prove for a simpler case, then extend by continuity/density/limits |

Discuss the strategy with the researcher before proceeding. Multiple strategies may work; choose the one that is most illuminating for the reader.

## Step 4: Develop the Proof

Work through the proof step by step:

1. **State the setup**: What are we given? What notation will we use?
2. **Identify the key insight**: What is the non-obvious step? Every good proof has one.
3. **Fill in the details**: Work through the algebra, logic, or construction.
4. **Check boundary cases**: Do the arguments work at the extremes?
5. **Verify the conclusion**: Does the final line actually state what was to be proved?

For each step, be explicit about what rule or fact is being used. Name the theorems, lemmas, or definitions you invoke.

## Step 5: Verify Correctness

After the proof is drafted, apply these checks:

- **Logical flow**: Does each step follow from the previous one? Are there implicit assumptions?
- **Quantifier correctness**: Are "for all" and "there exists" used correctly? Is the order right?
- **Boundary cases**: Does the argument work when parameters are at their extremes (0, 1, infinity)?
- **Notation consistency**: Are symbols used consistently throughout?
- **Dependencies**: Does the proof depend on results that have not yet been established in the paper?
- **Circularity**: Does the proof accidentally assume what it is trying to show?

If you find issues, present them clearly:

> I notice a potential gap in the third step: we assume that [X], but this has not been established. We need either a lemma showing [X] or an additional hypothesis.

## Step 6: Help with Presentation

A correct proof that is hard to follow is almost as bad as an incorrect one. Help with:

- **Proof sketch first**: For long proofs, add a 2-3 sentence sketch before the formal proof.
- **Signposting**: "We proceed in three steps: first we show..., then we..., finally we..."
- **Naming key quantities**: "Let Delta denote the difference..." rather than repeating long expressions.
- **Breaking into lemmas**: If the proof is long, factor out independent pieces as lemmas.
- **Choosing the right environment**: Theorem for major results, Proposition for supporting results, Lemma for technical steps, Corollary for immediate consequences.

## Step 7: Update State File

Append a note to `.papermill.md` (Edit tool) documenting the proof work:

```
- YYYY-MM-DD (proof): Developed proof of [theorem name]. Strategy: [strategy]. Status: [draft/verified/complete].
```

## Step 8: Suggest Next Steps

Based on the proof status, suggest the most relevant next step:

- If the proof establishes a quantitative result (formula, bound, rate) → "Use `/papermill:simulation` to validate the result numerically — demonstrate that empirical behavior matches the theoretical prediction."
- If the proof depends on assumptions that could be tested → "Use `/papermill:experiment` to design experiments verifying the assumptions hold in practice."
- If the proof is draft/verified but not yet in the paper → "Integrate the proof into the manuscript with proper LaTeX environments (Theorem, Proof, etc.)."
- If the proof is complete and in the paper → "Use `/papermill:review` to get feedback on the proof's clarity and correctness."
