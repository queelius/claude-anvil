# gpg Reference

## Overview

GNU Privacy Guard — standard tool for file encryption, digital signatures, and public key
management. Use for offline encryption scenarios, signing documents, and key-based trust
that doesn't involve browser delivery.

## Symmetric Encryption (Password-Based)

For encrypting files with a shared passphrase. No key management needed.

```bash
# Encrypt
gpg -c --cipher-algo AES256 document.pdf
# Creates document.pdf.gpg, prompts for passphrase

# Decrypt
gpg -d document.pdf.gpg > document.pdf
# Or: gpg -o document.pdf -d document.pdf.gpg

# Encrypt with specific passphrase (scripting)
echo "passphrase" | gpg --batch --yes --passphrase-fd 0 -c --cipher-algo AES256 file.txt

# Encrypt to stdout (piping)
gpg -c --cipher-algo AES256 -o - file.txt | base64 > file.txt.b64
```

## Asymmetric Encryption (Key-Based)

For encrypting files so only a specific recipient can decrypt. Requires exchanging public keys.

```bash
# Encrypt for a recipient
gpg -e -r recipient@email.com document.pdf
# Creates document.pdf.gpg

# Encrypt for multiple recipients
gpg -e -r alice@example.com -r bob@example.com document.pdf

# Decrypt (automatic key selection)
gpg -d document.pdf.gpg > document.pdf

# Encrypt and sign in one step
gpg -se -r recipient@email.com document.pdf
```

## Digital Signatures

### Detached Signatures (Most Common)

Signature in a separate `.sig` file. Original file unchanged.

```bash
# Sign
gpg --detach-sign document.pdf
# Creates document.pdf.sig

# Verify
gpg --verify document.pdf.sig document.pdf
# Output: Good signature from "Name <email>"

# Sign with specific key
gpg --detach-sign -u alice@example.com document.pdf
```

### Clear-Text Signatures

Signature embedded in the file (for text files).

```bash
gpg --clearsign message.txt
# Creates message.txt.asc with inline signature

gpg --verify message.txt.asc
```

### Inline Signatures

Signature + content in one binary file.

```bash
gpg -s document.pdf
# Creates document.pdf.gpg (signed, not encrypted)

gpg --verify document.pdf.gpg
gpg -d document.pdf.gpg > document.pdf  # Extract original
```

## Key Management

```bash
# Generate a new key pair
gpg --gen-key                              # Interactive
gpg --full-gen-key                         # More options (algorithm, expiry)

# List keys
gpg --list-keys                            # Public keys
gpg --list-secret-keys                     # Private keys
gpg --list-keys --keyid-format long        # Show full key IDs

# Export keys
gpg --export -a "Alice" > alice-public.key        # ASCII-armored public key
gpg --export-secret-keys -a "Alice" > alice.key   # Private key (protect this!)

# Import keys
gpg --import alice-public.key              # Import someone's public key

# Trust a key
gpg --edit-key alice@example.com
# Then: trust → 5 (ultimate) → quit

# Delete keys
gpg --delete-keys alice@example.com        # Delete public key
gpg --delete-secret-keys alice@example.com # Delete private key
```

## Batch Operations

Encrypt multiple files:
```bash
for f in *.pdf; do gpg -c --cipher-algo AES256 "$f"; done
```

Sign multiple files:
```bash
for f in *.pdf; do gpg --detach-sign "$f"; done
```

Verify all signatures in a directory:
```bash
for sig in *.sig; do
  file="${sig%.sig}"
  gpg --verify "$sig" "$file" 2>&1
done
```

## Compound Workflows with cryptoid/pagevault

### Sign encrypted Hugo output
```bash
cryptoid encrypt --content-dir content/
hugo -o public/
# Sign the built site
for f in public/**/*.html; do gpg --detach-sign "$f"; done
```

### Sign pagevault-locked files
```bash
pagevault lock report.pdf -d _locked/
gpg --detach-sign _locked/report.pdf.html
# Send both .html and .html.sig to recipient
```

### Verify before decrypting
```bash
gpg --verify report.pdf.html.sig report.pdf.html && \
  pagevault unlock report.pdf.html --stdout -p "$PW" > report.pdf
```

## Common Options

| Flag | Description |
|------|-------------|
| `-c` | Symmetric encryption (passphrase) |
| `-e` | Asymmetric encryption (public key) |
| `-d` | Decrypt |
| `-s` | Sign |
| `--detach-sign` | Detached signature |
| `--clearsign` | Clear-text signature |
| `--verify` | Verify signature |
| `-r RECIPIENT` | Encrypt for recipient |
| `-u KEY` | Sign with specific key |
| `-a` | ASCII armor output |
| `-o FILE` | Output file |
| `--batch --yes` | Non-interactive mode |
| `--cipher-algo AES256` | Force AES-256 |
