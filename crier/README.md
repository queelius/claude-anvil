# crier — Cross-Posting Plugin for Claude Code

Cross-post blog content to multiple platforms (Dev.to, Hashnode, Bluesky, Mastodon, Medium, Twitter, and more).

## Components

- **Skill** (`crier`): CLI reference, workflow guidance, rewrite guidelines
- **Command** (`/crier`): Quick audit-and-publish workflow
- **Agent** (`cross-poster`): Autonomous bulk cross-posting

## Requirements

- [crier](https://pypi.org/project/crier/) CLI installed (`pip install crier`)
- API keys configured via `crier config set`

## Quick Start

```
/crier                    # Run the cross-posting workflow
/crier content/post       # Scope to blog posts only
```
