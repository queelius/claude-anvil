# kdp — Claude Code Plugin

Amazon KDP (Kindle Direct Publishing) book publishing for Claude Code. Audit
manuscripts against KDP requirements, craft Amazon listings, and run the full
publishing workflow — for technical books, fiction, and general nonfiction.

## Components

| Type | Name | Purpose |
|------|------|---------|
| Skill | `kdp-audit` | Audit manuscript formatting, cover specs, and metadata against KDP requirements |
| Skill | `kdp-listing` | Craft Amazon listing: blurb, keywords, categories, author bio |
| Skill | `kdp-publish` | Full KDP publishing workflow from manuscript to submission |
| Command | `/kdp-audit` | Run a KDP manuscript audit |
| Command | `/kdp-listing` | Generate Amazon listing copy |
| Command | `/kdp-publish` | Guide the full publishing pipeline |

## Install

```bash
# From the marketplace
/plugin install kdp@queelius
```

## User Config

Skills read `.claude/kdp.local.md` in your book project for author and KDP
preferences. On first run, the skill offers to create one from the bundled
template.

## License

MIT
