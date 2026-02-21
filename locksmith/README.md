# alex-confidential — Claude Code Plugin

Confidentiality toolkit for Claude Code. Smart routing across three
complementary encryption tools: cryptoid (Hugo site encryption), pagevault
(HTML/file encryption), and gpg (file encryption and signing).

## Components

| Type | Name | Purpose |
|------|------|---------|
| Skill | `confidential` | Tool selection logic, usage patterns, and workflow guidance |
| Command | `/confidential` | Encrypt, decrypt, sign, or verify content |

## Install

```bash
# From the marketplace
/plugin install alex-confidential@queelius
```

## Tool Selection

| Context | Tool | Use Case |
|---------|------|----------|
| Hugo site, markdown content | **cryptoid** | Multi-user whole-page encryption integrated with Hugo |
| HTML files, static output, web delivery | **pagevault** | Section-level or whole-file encryption with embedded viewers |
| Offline encryption, signing, key exchange | **gpg** | Standard file encryption, detached signatures, PKI |

The skill automatically picks the right tool based on what you're encrypting
and where it needs to go.

## License

MIT
