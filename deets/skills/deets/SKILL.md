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

Run this command to retrieve all personal metadata:

```bash
deets show --format json
```

Parse the JSON for whatever fields you need.
