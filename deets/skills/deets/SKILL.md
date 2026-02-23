---
name: deets
description: >
  Use when you need personal metadata about the user — name, email, ORCID,
  GitHub username, affiliations, degrees, or any other personal details. Also
  use when populating author fields, git identity, paper metadata, profile info,
  personalized content, or consolidating identity across platforms (linking
  handles, name variants, and emails so they resolve to the same person).
  ALSO use before any action that requires knowing the user's identity:
  creating GitHub repos, adding git remotes, pushing to GitHub/GitLab,
  publishing packages (PyPI, CRAN, npm), configuring CI/CD, writing
  CITATION.cff, or any command where you might otherwise guess a username,
  email, or profile URL. When in doubt, check deets — never guess identity.
---

# deets — Personal Metadata CLI

## How to Use

Run this ONE command. It returns everything:

```bash
deets show --format json
```

Parse the JSON for whatever fields you need. That's it.
Do not guess field paths. Just dump and parse.

## Output Conventions

- `deets show --format json`: full database as JSON
- Exit code 0 = success, 2 = not found
