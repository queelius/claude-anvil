---
# pub-pipeline user configuration
# Copy this file to .claude/pub-pipeline.local.md in your project and fill in your details.

# Primary author / submitter
author:
  name: "First M. Last"
  orcid: "0000-0000-0000-0000"
  email: "you@example.com"
  affiliation: "Department, University"

# Additional co-authors (add entries as needed)
coauthors: []
  # - name: "Co Author"
  #   orcid: "0000-0000-0000-0000"
  #   affiliation: "Their Institution"

# R package publication config (fill if publishing an R package)
r:
  domain: ""                           # e.g., "survival analysis", "Bayesian statistics"
  audience: ""                         # e.g., "statisticians and reliability engineers"
  competitors:                         # known competing R packages
    []
    # - name: "survival"
    #   notes: "foundational but different paradigm"
  dependency_chain: []                 # own packages that must be on CRAN first
    # - name: "likelihood.model"
    #   status: "on-cran"              # "not-submitted", "submitted", "on-cran"

# Python package publication config (fill if publishing to PyPI)
python:
  pypi_username: ""

# Amazon KDP book publication config (fill if publishing a book)
kdp:
  pen_name: null                       # if different from author.name
  publisher: null                      # imprint name, if any
  genre: ""                            # e.g., "epic fantasy", "thriller", "literary fiction"
  series:
    name: null                         # series name, if part of a series
    volume: null                       # volume/book number
  trim_size: "5.5x8.5"                # fiction default; "6x9" for nonfiction
  paper_type: "cream"                  # "cream" for fiction, "white" for technical/nonfiction
  target: "both"                       # "ebook", "paperback", or "both"
  categories: []                       # BISAC codes (populated by /kdp-listing)
  keywords: []                         # up to 7 phrases (populated by /kdp-listing)
  blurb: ""                            # Amazon description (populated by /kdp-listing)
  author_bio: ""                       # genre-appropriate bio (populated by /kdp-listing)

# AI usage disclosure (for JOSS papers and other venues requiring it)
ai_usage:
  used: false                          # set to true if AI tools were used
  tools: []                            # e.g., ["Claude Code", "GitHub Copilot"]
  scope: ""                            # e.g., "code generation, documentation drafting"
  human_oversight: ""                  # e.g., "All design decisions by authors"

# Funding and acknowledgements (optional)
funding: null                          # e.g., "NSF Grant #12345"
---

## Additional Context

Any free-form notes about the project that might help with paper drafting, audits,
or publication decisions. For example:

- Background on the project's origins
- Key innovations or design decisions worth highlighting
- Target venues or timeline
- Notes for co-authors
