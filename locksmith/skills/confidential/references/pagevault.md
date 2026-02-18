# pagevault Reference

## Overview

Password-protect regions of HTML files or wrap arbitrary files into self-contained encrypted
HTML. Works with any static site generator. Uses AES-256-GCM with PBKDF2-SHA256 (310,000
iterations). All decryption happens client-side via WebCrypto API.

## Configuration: `.pagevault.yaml`

```yaml
password: "your-strong-passphrase"
salt: "auto-generated"

defaults:
  remember: "ask"          # "none", "session", "local", "ask"
  remember_days: 0         # 0 = no expiration
  auto_prompt: true        # Show password prompt on page load

template:
  title: "Protected Content"
  button_text: "Unlock"
  error_text: "Incorrect password"
  hint: "Contact admin for password"

# Multi-user (optional)
users:
  alice: "alice-password"
  bob: "bob-password"
```

Create with `pagevault config init`. Add to `.gitignore`.

Environment variable override: `PAGEVAULT_PASSWORD`.

## CLI Commands

### Lock (Encrypt)
```bash
pagevault lock page.html                    # Encrypt marked <pagevault> regions
pagevault lock report.pdf                   # Wrap file with appropriate viewer
pagevault lock image.png                    # Wrap image with image viewer
pagevault lock site/                        # All files in directory
pagevault lock site/ --site                 # Bundle as encrypted site
pagevault lock page.html -s "#secret"       # Encrypt only elements matching selector
pagevault lock page.html --pad              # Pad to prevent content size leakage
pagevault lock file.txt -p "password"       # Override config password
pagevault lock docs/ -r -d _locked/         # Recursive, output to _locked/
```

### Unlock (Decrypt)
```bash
pagevault unlock _locked/page.html          # Decrypt back to marked state
pagevault unlock _locked/ -r                # Recursive unlock
pagevault unlock file.pdf.html --stdout -p "$PW" > file.pdf  # Extract original
```

### Mark (Add Encryption Tags)
```bash
pagevault mark page.html                    # Wrap entire body
pagevault mark page.html -s ".private"      # Wrap elements matching CSS selector
pagevault mark page.html -s "#secret" --hint "Contact admin"
```

### Inspect and Verify
```bash
pagevault info encrypted.html               # Show metadata (no password needed)
pagevault check encrypted.html -p "pw"      # Verify password (exit 0 = correct)
pagevault audit                             # Health check config and passwords
```

### Config
```bash
pagevault config init                       # Create .pagevault.yaml
pagevault config show                       # Display current config
pagevault config where                      # Find config file location
```

### Sync (Re-encrypt)
```bash
pagevault sync _locked/ -r                  # Re-encrypt after password change
```

## Viewer Plugins

pagevault includes built-in viewers for common file types. When locking a non-HTML file,
the appropriate viewer is automatically selected:

| File type | Viewer | What it does |
|-----------|--------|-------------|
| `.html` | HTML viewer | Renders decrypted HTML inline |
| `.md` | Markdown viewer | Renders markdown to HTML |
| `.pdf` | PDF viewer | Embedded PDF viewer |
| `.png`, `.jpg`, `.gif`, `.svg` | Image viewer | Displays image |
| `.mp4`, `.webm` | Video viewer | Video player |
| `.mp3`, `.wav` | Audio viewer | Audio player |
| `.txt`, `.csv`, `.json` | Text viewer | Monospace text display |

Other file types get a download link after successful decryption.

## Self-Contained Output

Every encrypted HTML file includes the full decryption runtime:
- Web Component (`<pagevault-encrypted>`)
- JavaScript decryption logic (WebCrypto API)
- CSS for the password prompt UI
- No external dependencies at runtime

## Configuration Cascade

Priority order (highest first):
1. Command-line arguments (`-p`, `--hint`, etc.)
2. Environment variables (`PAGEVAULT_PASSWORD`)
3. `.pagevault.yaml` in project root
4. Built-in defaults

## Hugo Integration Example

```bash
# After Hugo builds HTML output:
hugo -o build/
pagevault lock build/posts/ -r --css styles/pagevault.css
# Deploy build/ to static host
```

## Known Limitations

- Encrypted regions are replaced with password prompts — page structure is visible
- File sizes may hint at content length (use `--pad` to mitigate)
- JavaScript must be enabled for decryption
