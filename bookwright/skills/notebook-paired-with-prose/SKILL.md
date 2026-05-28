---
name: notebook-paired-with-prose
description: Use when drafting or executing a paired notebook for a bookwright chapter. Covers when notebooks are required vs optional, numerical-sanity-target convention, exec-from-fresh-kernel requirement, and stack-specific execution commands (Jupyter/R Markdown/Quarto).
metadata:
  type: convention
---

# Notebook Paired with Prose (bookwright)

In a technical textbook, paired notebooks are not optional decoration. They are empirical verifiers: a chapter that claims a formula or worked example has a notebook that COMPUTES the formula and shows the empirical result matches. Broken notebook means broken chapter.

## When notebooks are required vs optional

Required:

- Any chapter with a worked numerical example. The notebook must compute the same example and match.
- Any chapter with an algorithm. The notebook implements it and runs it.
- Any chapter with an empirical claim ("the SE is roughly 0.05"). The notebook simulates and verifies.

Optional or omitted:

- Theory-only chapters (no worked examples, no algorithms). Bernoulli's chapters 4, 13, 17 had no notebooks; the master spec marks them theory-only.
- Bridge chapters that exist only to connect Parts.

The master spec's chapter outline marks which chapters have notebooks. The per-chapter plan's notebook task spec lists the content + numerical-sanity targets.

## Numerical-sanity-target convention

The plan lists explicit targets like:

- "Empirical FPR at $\fprate = 0.01$, k=7: within plus-or-minus 0.005 of theoretical 0.0078."
- "Wald CI coverage at $n_0 = 200, \fprate = 0.05$: in $[0.93, 0.97]$ band."

The notebook-author agent computes these and compares. Match = pass. Miss = flag for user review (could be the prose is wrong, could be the notebook is wrong, could be sampling noise).

## Exec-from-fresh-kernel requirement

Notebooks MUST execute end-to-end from a fresh kernel with no errors. The notebook-author runs:

- Python+uv+Jupyter: `cd <project>/notebooks && uv run jupyter nbconvert --to notebook --execute <name>.ipynb --output <name>.ipynb`
- R+renv+RMarkdown: `cd <project>/rmd && Rscript -e 'rmarkdown::render("<name>.Rmd")'`
- Quarto: `cd <project>/qmd && quarto render <name>.qmd`

Exit code 0 is required for commit.

## Common gotchas

- Python: forgetting to seed the RNG produces non-reproducible outputs. Always `np.random.default_rng(seed=42)` or similar.
- Python: dependencies must be in `pyproject.toml`. New dependencies require `cd <project> && uv add <pkg>` before re-executing.
- R: `renv::status()` should be clean; new packages require `renv::install("pkg")` then `renv::snapshot()`.
- Quarto: cell-by-cell execution depends on engine; if mixing R + Python, configure the engine carefully.
- All stacks: explicitly seed any randomness. Markdown cells should describe what the code cell will do, not just narrate it.

## Cell discipline

- Title cell (markdown): names the chapter and notebook.
- Setup cell (code): imports + seeded RNG.
- Body cells: alternating code + markdown for narrative + numerical verification.
- Discussion / open-question cell (markdown): forward-reference downstream chapters if relevant.

Match the cell count of prior chapter notebooks for the project (typically 12-18 cells). Light notebooks have ~10; substantive have ~16-20.

## Pluggable stack

The project's `docs/superpowers/bookwright.config.yaml` records the stack choice (set during `/bookwright:init`). The notebook-author reads this config before drafting. Stack-specific commands above; stack-specific conventions (Python uv, R renv, Quarto rendering) are picked up from the config.

## Skipping a notebook

If a chapter is theory-only per the master spec, skip the notebook task entirely. Do NOT write an empty placeholder notebook (clutters the project). The integration check verifies which chapters have notebooks vs theory-only.
