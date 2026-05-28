---
name: textbook-methodology
description: Use when drafting prose sections for a bookwright (technical non-fiction) project. Encodes the Bernoulli-textbook workflow: atom-outward design, deferral discipline, running threads, page budgets, Path A subagent pattern, header comment block convention.
metadata:
  type: methodology
---

# Textbook Methodology (bookwright)

The Bernoulli-textbook approach: discipline that makes long-form technical books actually finishable.

## Atom-outward design

When designing a Part, sequence the chapters so the FOUNDATION chapter is drafted LAST. The Bernoulli textbook drafted chapter 1 (the noisy bit, the foundational atom) after chapters 2, 3, 4, because chapter 1 is best written knowing where the reader is being taken. The same pattern applies at the Part level: the part introduction chapter benefits from being drafted after the technical chapters it introduces.

## Deferral discipline

Earlier chapters often need to mention a topic that gets full treatment later. Use the "we'll address this in §X" pattern: name the deferral explicitly, cite the section that will retire it, and make sure the integration check verifies that the target section actually does.

Examples from the Bernoulli textbook:
- Chapter 1 §1.4 said "the full treatment of estimation lives in chapter 7." Chapter 7 §7.1 explicitly says it retires this deferral, and §7.2-7.3 cash in.
- Chapter 1 exercise 10 said "what would a non-noisy-bit look like? See chapter 16." Chapter 16 §16.1 lists this as one of the deferrals it cashes.

## Running threads

The master spec names 3-5 running threads (recurring concepts/examples that appear across chapters). Each chapter carries N of M threads. The integration check verifies each thread appears in the chapters the spec assigned it to.

Bernoulli threads: BSC (binary symmetric channel), biased coin, classifier verdict, Bloom filter, Miller-Rabin, Bernoulli[T] type. Each carries through multiple chapters; the integration check produces an inventory.

## Page budgets

Per-section page targets are stated in the per-chapter plan. Plans 1-3 of Bernoulli came in 30-43% over target; Plans 4+ adjusted by aiming for the LOWER end of the target band to land near nominal. Tolerance: plus-or-minus 30 percent is the integration-check band.

If a section comes in significantly over, reviewers should ask: is the math density justifying it (acceptable), or is the prose padded (cut)?

## Path A subagent discipline

For each section drafting task, the cadence is:

1. Implementer subagent: drafts the section per the plan's content checklist, builds the book, commits.
2. spec-auditor subagent: checks against the content checklist.
3. quality-auditor subagent: cold-reads for clarity and craft.
4. If either auditor surfaces substantive findings: a fix subagent applies the changes, then the relevant auditor is re-run to verify.

This pattern protects main conversation context and catches issues per-section rather than per-chapter.

## Header comment block convention

Every section file starts with a comment block (LaTeX % lines) that documents:

- DEFINED here: labels this section creates.
- RESOLVED: labels from prior chapters that this section cites (cite each, with file path).
- FORWARD: labels this section cites that resolve in later sections/chapters (cite the resolving section).

The cross-ref-auditor reads these blocks to verify integrity.

## Source-paper reformulation

If the book draws on prior research papers, the cite-don't-copy discipline applies: cite the paper for results, produce fresh pedagogical prose. The source-reformulator agent handles this.

## Commit discipline

- One drafting task = one commit.
- Commit message HEREDOC with subject "book: <action>" and Co-Authored-By trailer.
- Do NOT stage book.pdf (binary artifact; rebuild from source).
- Review fixes get their own commits ("book: fix chapter X §X.Y per quality review").

## What this skill does NOT cover

- Cross-reference label naming and the header comment block template: see `bookwright:cross-reference-discipline`.
- Notebook execution and numerical-sanity-target conventions: see `bookwright:notebook-paired-with-prose`.
