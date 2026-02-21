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

# AI usage disclosure (for JOSS papers and other venues requiring it)
ai_usage:
  used: false                          # set to true if AI tools were used
  tools: []                            # e.g., ["Claude Code", "GitHub Copilot"]
  scope: ""                            # e.g., "code generation, documentation drafting"
  human_oversight: ""                  # e.g., "All design decisions by authors"

# Related work — companion papers, sibling packages, preprints, prior pub-pipeline outputs
related_work: []
  # - type: "companion-paper"          # companion-paper, preprint, sibling-package, dependency
  #   path: "../reliability-paper/"    # local path (relative to project root) or URL
  #   doi: null                        # DOI if published (e.g., "10.31219/osf.io/xxxxx")
  #   notes: "Theory paper; this package implements the methods"
  # - type: "preprint"
  #   doi: "10.31219/osf.io/xxxxx"
  #   path: null
  #   notes: "Submitted via /osf-preprint on 2026-01-15"
  # - type: "sibling-package"
  #   path: "../other-package/"
  #   doi: null
  #   notes: "Shares core algorithms; this package adds the Bayesian layer"

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
