---
description: Scaffold a fresh non-fiction book project (LaTeX + pluggable notebook + spec/plan directories)
allowed-tools: Read, Write, Bash, Glob, AskUserQuestion
argument-hint: "[book-name]"
---

# /bookwright:init

Scaffold a fresh book project at the current working directory (or a named subdirectory). Asks the user for a notebook stack choice and persists the choice to `docs/superpowers/bookwright.config.yaml`.

## What it creates

- `book/` with `chapters/`, `frontmatter/`, `appendices/`, `parts/`, `alex.sty` (or empty placeholder for project's own notation), `preamble.tex`, `references.bib`, `book.tex`, `Makefile`.
- `notebooks/` (Jupyter) OR `rmd/` (R Markdown) OR `qmd/` (Quarto) per user choice.
- `papers/` (empty; user can git-subtree-add source papers later).
- `docs/superpowers/specs/` and `docs/superpowers/plans/`.
- `docs/superpowers/bookwright.config.yaml` recording the notebook stack choice and other project settings (key: `notebook_stack: python-uv | r-renv | quarto | none`; `none` means prose-only and notebook-author is never dispatched).
- `book/CLAUDE.md` recording the build command (matching the Makefile), the banned-phrase list, label-naming conventions, and the notebook directory. Five agents read this file; a project without it breaks the drafting chain.

## Steps

1. Ask the user (via AskUserQuestion) which notebook stack: Python+uv+Jupyter / R+renv+RMarkdown / Quarto / none.
2. Create the directory tree.
3. Write a minimal `book.tex` that includes empty `parts/part1.tex` and references it.
4. Write a minimal `Makefile` with the standard cleanall + biber + pdflatex pipeline.
5. Write the `bookwright.config.yaml` recording user choices.
6. Write `book/CLAUDE.md` with: the build command from the Makefile, the banned-phrase list (seed from the soul conventions or leave a TODO section), label-naming conventions, and the notebook directory chosen in step 1.
7. Write a README in the new project root summarizing the layout.
8. Initialize git if not already initialized; commit the scaffold.
9. Report success and suggest next steps: `/bookwright:design master` (or `/bookwright:design part1`).

## Dependencies

- The `soul` plugin should be installed in the user's Claude environment for the soul-voice hook to fire on .tex writes in the new project. `init` should remind the user of this if not already done.
