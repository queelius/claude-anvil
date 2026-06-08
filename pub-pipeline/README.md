# pub-pipeline

A Claude Code plugin for automating publication workflows across multiple ecosystems:

- **R packages**: CRAN → JOSS → JSS
- **Python packages**: PyPI

## Skills & Commands

### R Package Publication

| Command | Skill | Purpose |
|---------|-------|---------|
| `/cran-audit` | cran-audit | Audit package against CRAN Repository Policy |
| `/joss-audit` | joss-audit | Evaluate against JOSS reviewer checklist |
| `/joss-draft` | joss-draft | Draft `paper.md` and `paper.bib` for JOSS |
| `/r-publish` | r-pub-pipeline | Orchestrate the full CRAN → JOSS → JSS pipeline |

### Python Package Publication

| Command | Skill | Purpose |
|---------|-------|---------|
| `/pypi-publish` | pypi-publish | Audit, build, test, and publish to PyPI |

### Auto-Detection

Say "publish my package" or "publication pipeline" and the top-level `pub-pipeline` skill will detect your project type (R or Python) and route to the right workflow.

## Multi-Agent JOSS System

`/joss-draft` and `/joss-audit` are backed by a multi-agent system: two orchestrators each spawn specialist agents in parallel.

- **joss-writer** drafts `paper.md` and `paper.bib`, spawning **field-scout** to map competing packages for the State of the Field.
- **joss-reviewer** evaluates the package and paper against the JOSS checklist, spawning **software-auditor** (tests, coverage, CI, API docs), **community-auditor** (LICENSE, CONTRIBUTING, CODE_OF_CONDUCT, development history), and **field-scout** (missing comparisons), then synthesizes a unified gap report.

Agents pass context via XML tags and return structured findings the orchestrator merges.

## Configuration

Copy `docs/user-config-template.md` to `.claude/pub-pipeline.local.md` in your project and fill in your details:

```yaml
author:
  name: "Your Name"
  orcid: "0000-0000-0000-0000"
  email: "you@example.com"
  affiliation: "Your Institution"
```

The config provides author metadata, competing package info, AI usage disclosure, and ecosystem-specific settings shared across all skills.

## Installation

```bash
/plugin marketplace add queelius/claude-anvil
/plugin install pub-pipeline@queelius
```

## Prerequisites

**R packages**: R with `devtools`, `covr`, `testthat`, `urlchecker`; `gh` CLI

**Python packages**: Python with `build`, `twine`, `pytest`

## Reference Documents

The `docs/` directory contains comprehensive reference material:

- `user-config-template.md` — Shared user configuration template
- `cran-reference.md` — CRAN Repository Policy and submission checklist
- `joss-reference.md` — JOSS requirements and reviewer checklist
- `joss-exemplars.md` — Real JOSS R package paper examples
- `pypi-reference.md` — PyPI publishing requirements and workflow


## License

MIT
