---
description: Draft and execute the paired notebook for a chapter (separable from prose drafting)
allowed-tools: Read, Write, Bash, Glob, Task
argument-hint: "<chapter-name-or-number>"
---

# /bookwright:notebook

Dispatch the `notebook-author` agent to draft (or refresh) the paired notebook for a chapter. Separate command from `/bookwright:draft` so notebooks can be updated without re-drafting prose.

## What it does

1. Reads the chapter's plan file to find the notebook content checklist and numerical-sanity targets.
2. Reads `docs/superpowers/bookwright.config.yaml` to determine notebook stack (Python+uv / R+renv / Quarto).
3. Dispatches the `notebook-author` agent to draft or update the notebook.
4. The agent executes the notebook end-to-end and reports execution exit code + observed numerical values.
5. If execution fails or observed values miss the sanity targets, surfaces the discrepancy for the user to review.

## Stack-specific execution commands

- Python+uv+Jupyter: `cd <project-dir>/notebooks && uv run jupyter nbconvert --to notebook --execute <name>.ipynb --output <name>.ipynb`
- R+renv+RMarkdown: `cd <project-dir>/rmd && Rscript -e 'rmarkdown::render("<name>.Rmd")'`
- Quarto: `cd <project-dir>/qmd && quarto render <name>.qmd`
