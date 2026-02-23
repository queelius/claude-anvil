---
name: deets
description: >
  Use before any action requiring the user's personal identity or metadata.
  This includes: populating author fields, git config, creating repos, pushing
  to remotes, publishing packages, writing CITATION.cff, configuring CI/CD,
  or any situation where you need a name, email, username, or profile URL.
---

# deets

When this skill is triggered, immediately run:

```bash
deets show --format json
```

Then extract whatever you need from the JSON output.
