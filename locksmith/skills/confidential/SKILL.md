---
name: confidential
description: >-
  This skill should be used when the user asks to "encrypt", "decrypt", "lock", "unlock",
  "sign", "verify", "protect", "make confidential", "password-protect", or manage encryption
  for any content. Covers Hugo site encryption (cryptoid), HTML/file encryption (pagevault),
  and file-level encryption/signing (gpg). Provides smart routing to pick the right tool
  based on context.
---

# Confidentiality Toolkit

Smart routing across three complementary encryption tools. Pick the right tool based on what
needs protecting, apply it, and optionally sign the result.

## Tool Selection

| Signal | Tool | Why |
|--------|------|-----|
| Hugo site, markdown content, `_index.md` cascade, `.cryptoid.yaml` | **cryptoid** | Multi-user/group whole-page encryption integrated with Hugo build |
| HTML files, static site output, arbitrary files for web delivery, `<pagevault>` tags | **pagevault** | Section-level or whole-file encryption, self-contained HTML output with viewers |
| Offline encryption, signing, key exchange, `.gpg` files, asymmetric crypto | **gpg** | Standard file encryption, detached signatures, public key infrastructure |

### Decision Tree

```
Is this a Hugo site with markdown content files?
  YES -> cryptoid
  NO  -> Is this HTML, a static site, or files meant for browser viewing?
    YES -> pagevault
    NO  -> gpg
```

Override: the user may explicitly name a tool regardless of context. Honor that.

### Compound Workflows

Some tasks require multiple tools in sequence:

- **Encrypt and sign**: Encrypt with cryptoid or pagevault first, then `gpg --detach-sign` the output
- **Verify then decrypt**: `gpg --verify` the signature, then `pagevault unlock` or `cryptoid decrypt`
- **Web delivery + archival**: `pagevault lock` for browser access, `gpg -e` the original for offline backup

## cryptoid — Hugo Site Encryption

Encrypts whole markdown pages for Hugo static sites. Multi-user access control with
group-based permissions and directory cascade via `_index.md`.

**Key concepts**: `.cryptoid.yaml` config (users/groups/salt), `encrypted: true` front matter,
cascade from `_index.md`, admin group gets universal access, `_index.md` bodies are encrypted
(front matter stays readable).

### Essential Commands

```bash
cryptoid init                                    # Interactive config setup
cryptoid protect content/private/ --groups team  # Cascade-encrypt a directory
cryptoid protect content/doc.md --groups admin   # Encrypt a single file
cryptoid protect -i                              # Interactive TUI selector
cryptoid unprotect content/private/              # Remove encryption marking
cryptoid encrypt --content-dir content/          # Encrypt marked files
cryptoid encrypt --content-dir content/ --dry-run
cryptoid decrypt --content-dir content/          # Restore plaintext
cryptoid status --content-dir content/ --verbose # Show encryption state
cryptoid rewrap --content-dir content/           # Re-wrap after user changes
cryptoid rewrap --rekey                          # New CEK for forward secrecy
cryptoid hugo install                            # Install shortcode + JS
```

### User/Group Management

```bash
cryptoid config list-users
cryptoid config add-user USERNAME [--group GROUP]
cryptoid config remove-user USERNAME
cryptoid config list-groups
cryptoid config add-group NAME [--members alice,bob]
cryptoid config remove-group NAME
cryptoid config generate-salt [--apply]
```

For detailed reference: **`references/cryptoid.md`**

## pagevault — HTML/File Encryption

Encrypts regions within HTML or wraps arbitrary files (PDF, images, text, markdown) into
self-contained encrypted HTML with built-in viewer plugins. Works with any static site.

**Key concepts**: `<pagevault>` tags for section-level encryption, `.pagevault.yaml` config,
self-contained output (HTML+JS+CSS all inline), viewer plugins for different file types,
multi-user support.

### Essential Commands

```bash
pagevault lock page.html                  # Encrypt marked regions
pagevault lock report.pdf                 # Wrap file with viewer
pagevault lock site/ --site               # Bundle entire site
pagevault lock page.html -s "#secret"     # Encrypt only matching selector
pagevault unlock _locked/page.html        # Decrypt back
pagevault mark page.html -s ".private"    # Add encryption tags
pagevault info encrypted.html             # Show metadata without password
pagevault config init                     # Create .pagevault.yaml
pagevault sync _locked/ -r               # Re-encrypt after password change
```

For detailed reference: **`references/pagevault.md`**

## gpg — File Encryption and Signing

Standard GNU Privacy Guard for offline file encryption, digital signatures, and key management.
Use for non-web scenarios or to sign outputs from cryptoid/pagevault.

### Essential Commands

```bash
# Symmetric encryption (password-based)
gpg -c --cipher-algo AES256 file.txt           # Encrypt with passphrase
gpg -d file.txt.gpg > file.txt                 # Decrypt

# Asymmetric encryption (key-based)
gpg -e -r recipient@email.com file.txt         # Encrypt for recipient
gpg -d file.txt.gpg > file.txt                 # Decrypt with your key

# Signing
gpg --detach-sign file.txt                     # Create file.txt.sig
gpg --verify file.txt.sig file.txt             # Verify signature
gpg --clearsign message.txt                    # Inline signature

# Key management
gpg --list-keys                                # List public keys
gpg --list-secret-keys                         # List private keys
gpg --gen-key                                  # Generate new key pair
gpg --export -a "Name" > public.key            # Export public key
gpg --import public.key                        # Import someone's key
```

For detailed reference: **`references/gpg.md`**

## Additional Resources

### Reference Files

For detailed usage, configuration, and troubleshooting:
- **`references/cryptoid.md`** — Full cryptoid reference (config format, cascade rules, front matter options, build workflow, security model)
- **`references/pagevault.md`** — Full pagevault reference (config format, viewers, selectors, site bundling, multi-user)
- **`references/gpg.md`** — GPG reference (key management, trust model, batch operations, common recipes)
