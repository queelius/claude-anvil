---
name: cross-reference-discipline
description: Use when writing cross-referenced sections in a bookwright project. Covers the header comment block template, label-naming conventions, when to use prose-only vs Cref, forward-reference documentation, and the integration-check baseline.
metadata:
  type: convention
---

# Cross-reference Discipline (bookwright)

LaTeX cross-references are mechanical. The trouble with them is that LaTeX silently emits "Reference undefined" warnings without erroring out, and over a long manuscript a single typo can cascade into chapters of broken refs that nobody notices. This skill encodes the discipline that prevents that.

## Header comment block (every section)

Every section file starts with a comment block. Template:

```
% §X.Y Section Title
%
% Cross-reference resolution status:
%
% DEFINED here: labels this section creates.
%   \label{sec:foo}
%   \label{def:bar}
%   \label{thm:baz}
%
% RESOLVED (chapter X):
%   \Cref{sec:foo-prior}    -- file: book/chapters/chXX/foo.tex
%   \Cref{def:bar-prior}    -- file: book/chapters/chXX/bar.tex
%
% FORWARD REFS (resolve in later sections/chapters):
%   \Cref{sec:foo-future}   -- target: ch. Y §Y.Z (this plan's Task N)
%   \Cref{ch:future-chapter} -- target: ch. Z (drafted in a future plan)
```

Why: the cross-ref-auditor and the integration check both read these blocks. The comment is the section's contract with the rest of the book.

## Label naming conventions

- `sec:foo-bar`: section labels (kebab-case after the type prefix).
- `def:foo-bar`: definitions.
- `prop:foo-bar`: propositions.
- `thm:foo-bar`: theorems.
- `cor:foo-bar`: corollaries.
- `lem:foo-bar`: lemmas.
- `eq:foo-bar`: display equations.
- `tab:foo-bar`: tables.
- `fig:foo-bar`: figures.
- `alg:foo-bar`: algorithms.
- `ex:chN-M`: exercises (chapter N, exercise number M).
- `ch:foo-bar`: chapters.

Label names should be the section/concept name in kebab-case. Avoid generic names like `sec:intro` or `def:1` that collide across chapters.

## When to use \Cref vs prose-only

- Use `\Cref{...}` when the target label EXISTS at build time.
- Use prose-only (e.g., "chapter 17 covers this") when:
  - The target chapter is not yet drafted (Plan 0 stubs aside).
  - The reference is informal ("the next chapter," "the appendix").
  - The reference is to an external paper (use `\cite{}` instead).

The Bernoulli baseline of "expected unresolved refs" includes `ch:composition` (chapter 4 forward into Part II; chapter 6's label is `ch:set-composition`; never renamed) and `ch:sketches` (chapter 9 prose; chapter 10's label is `ch:sketches-estimators`). These are documented in the integration-pass record so they pass the audit.

## Forward-reference documentation

When you write a forward ref, EITHER:

1. The target label exists in a Plan 0 stub file (chapter-level forward refs to undrafted chapters resolve to the stub's label).
2. The target is documented as "resolves in plan N" in the header comment block of THIS section AND in the plan file for the section that will define the label.

A forward ref undocumented in either place is a bug.

## Integration-check baseline

When `/bookwright:integrate` runs, it greps `book.log` with `grep "undefined" book/book.log | grep -iE "reference|citation"` (the literal string "Reference undefined" never appears in LaTeX logs). It expects the set of unresolved refs to match the documented baseline. Any UNEXPECTED unresolved ref is a FAIL.

When you add a new section, EITHER its labels resolve immediately (the section file defines them) OR you add the labels to the documented baseline as expected forward refs in the integration-pass record.

## Cross-ref auditor

The cross-ref-auditor agent reads section header comment blocks and verifies them against actual `\label{}` declarations and `\Cref{}` invocations. Run it after drafting if you want to catch issues per-section.
