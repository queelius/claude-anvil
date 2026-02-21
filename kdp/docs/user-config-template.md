---
# kdp user configuration
# Copy this file to .claude/kdp.local.md in your project and fill in your details.

# Primary author
author:
  name: "First M. Last"
  email: "you@example.com"
  bio: ""                                # general author bio (adapted per genre by /kdp-listing)

# Amazon KDP book publication config
kdp:
  pen_name: null                       # if different from author.name
  publisher: null                      # imprint name, if any
  genre: ""                            # e.g., "epic fantasy", "thriller", "literary fiction"
  series:
    name: null                         # series name, if part of a series
    volume: null                       # volume/book number
  trim_size: "5.5x8.5"                # fiction default; "6x9" for nonfiction
  paper_type: "cream"                  # "cream" for fiction, "white" for technical/nonfiction
  target: "both"                       # "ebook", "paperback", or "both"
  categories: []                       # BISAC codes (populated by /kdp-listing)
  keywords: []                         # up to 7 phrases (populated by /kdp-listing)
  blurb: ""                            # Amazon description (populated by /kdp-listing)
  author_bio: ""                       # genre-appropriate bio (populated by /kdp-listing)
---

## Additional Context

Any free-form notes about the book that might help with audits, listing craft,
or publication decisions. For example:

- Synopsis or pitch
- Target audience and comparable titles
- Publication timeline
- Notes on cover design or formatting decisions
