# Amazon KDP Publishing Reference

## Sources
- [KDP Help & Documentation](https://kdp.amazon.com/en_US/help)
- [Kindle Create User Guide](https://kdp.amazon.com/en_US/help/topic/G202131100)
- [Print Book Specifications](https://kdp.amazon.com/en_US/help/topic/G201834180)
- [KDP Cover Calculator](https://kdp.amazon.com/cover-templates)
- [Content Guidelines](https://kdp.amazon.com/en_US/help/topic/G200672390)

---

## Pre-Publication Checklist

### Manuscript Formatting

#### File Format Requirements
- [ ] **eBook**: DOCX (recommended), EPUB 2.0.1/3.0, HTML, MOBI, or KPF
- [ ] **Paperback**: PDF (print-ready) or DOCX (converted by KDP)
- [ ] **Hardcover**: PDF (print-ready) only
- [ ] File size under 650MB for eBooks (typically not an issue for text)
- [ ] Images in high quality: 300 DPI for print, 72 DPI minimum for eBook

#### Standard Trim Sizes (US)
**Non-fiction (most common)**:
- [ ] 6" × 9" — standard for trade paperbacks, business books, memoirs
- [ ] 7" × 10" — popular for how-to guides, coffee table books
- [ ] 8.5" × 11" — textbooks, workbooks, manuals

**Fiction**:
- [ ] 5.5" × 8.5" — standard for novels
- [ ] 5.25" × 8" — mass market paperback size
- [ ] 6" × 9" — larger print fiction

**Specialized**:
- [ ] 8" × 10" — children's books, photography
- [ ] 8.5" × 8.5" — square format for art/photo books

#### Margin Requirements (Paperback)
Margins vary by **page count** and **binding type**:

**Black & White Interior**:
- 24-150 pages: Inside 0.375", Outside 0.25", Top/Bottom 0.25"
- 151-300 pages: Inside 0.5", Outside 0.25", Top/Bottom 0.25"
- 301-500 pages: Inside 0.625", Outside 0.25", Top/Bottom 0.25"
- 501-700 pages: Inside 0.75", Outside 0.25", Top/Bottom 0.25"
- 701-828 pages: Inside 0.875", Outside 0.25", Top/Bottom 0.25"

**Color Interior** (same pattern, higher inside margins):
- 24-150 pages: Inside 0.5", Outside 0.25", Top/Bottom 0.25"
- 151-300 pages: Inside 0.625", Outside 0.25", Top/Bottom 0.25"
- 301-500 pages: Inside 0.75", Outside 0.25", Top/Bottom 0.25"
- 501-700 pages: Inside 0.875", Outside 0.25", Top/Bottom 0.25"
- 701-828 pages: Inside 1.0", Outside 0.25", Top/Bottom 0.25"

**Formula**: Inside margin = 0.375" + (0.125" per 150 pages) for B&W
Inside margin = 0.5" + (0.125" per 150 pages) for Color

- [ ] **Bleed**: Add 0.125" bleed if using images/backgrounds extending to edge
- [ ] **Safe zone**: Keep all text 0.125" inside trim edge

#### Font Requirements
- [ ] **eBook**: Use standard fonts (Times New Roman, Arial, Verdana, Georgia, Courier)
- [ ] **Print**: Embed all fonts in PDF (including subset for special fonts)
- [ ] Avoid decorative fonts for body text (readability)
- [ ] Minimum 7pt font size for print (10-12pt recommended for body)
- [ ] Standard font list (always safe):
  - Times New Roman
  - Arial / Helvetica
  - Verdana
  - Georgia
  - Courier / Courier New
  - Palatino
  - Garamond
  - Book Antiqua

#### Interior Elements
- [ ] **Table of Contents**: Required for eBooks (auto-generated or manual NCX)
- [ ] **Front matter**: Title page, copyright page, optional dedication/foreword
- [ ] **Headers/Footers**: Consistent styling, avoid putting on first pages of chapters
- [ ] **Page numbers**: Start at 1 on first chapter page (not on front matter)
- [ ] **Chapter starts**: Typically on recto (right-hand) pages for print
- [ ] **Images**: Anchor to text, not free-floating; use alt-text for eBooks
- [ ] **Hyperlinks**: Active in eBook (blue/underlined), printed as text in paperback
- [ ] **Color**: RGB for eBook, CMYK for print (if using color interior)

### Cover Requirements

#### eBook Cover
- [ ] **Minimum dimensions**: 2560 × 1600 pixels (width × height)
- [ ] **Ideal dimensions**: 2560 × 1600 or larger (up to 10,000px on longest side)
- [ ] **Aspect ratio**: 1.6:1 (height should be 1.6× width)
- [ ] **File format**: JPEG (.jpg) or TIFF (.tiff)
- [ ] **Color mode**: RGB
- [ ] **File size**: Under 50MB
- [ ] **Text**: Clearly readable at thumbnail size (reduce to 300px wide to test)
- [ ] **Borders**: Avoid white borders (looks like part of page background)

#### Paperback Cover
- [ ] **Resolution**: 300 DPI minimum
- [ ] **Color mode**: RGB (KDP converts to CMYK for printing)
- [ ] **File format**: PDF (preferred) or TIFF/JPEG for simple covers
- [ ] **Bleed**: Add 0.125" bleed on all sides (extends beyond trim)
- [ ] **Safe zone**: Keep critical text/elements 0.125" inside trim line
- [ ] **Spine width**: Calculate using KDP Cover Calculator
  - Formula: (Page count × paper type multiplier) + 0.06"
  - White paper: 0.002252" per page
  - Cream paper: 0.0025" per page
  - Example: 300-page white = (300 × 0.002252) + 0.06 = 0.7356"
- [ ] **Spine text**: Only include if book is 130+ pages (minimum spine width 0.3")
- [ ] **ISBN/Barcode**: Do NOT add barcode if using free Amazon ASIN (KDP adds it)
- [ ] **ISBN placement**: If using own ISBN, place barcode on back cover lower right

#### Cover Calculator
- [ ] Use [KDP Cover Calculator](https://kdp.amazon.com/cover-templates) for exact dimensions
- [ ] Enter: Trim size, page count, paper type, bleed option
- [ ] Download template with guides for spine placement

### Metadata

#### Title Information
- [ ] **Title**: Match exactly with cover (case-sensitive)
- [ ] **Subtitle**: Optional, appears after colon on Amazon page
- [ ] **Series name**: If part of series (helps with discoverability)
- [ ] **Volume number**: E.g., "Book 1", "Volume 3"
- [ ] **Edition**: "2nd Edition", "Revised", etc. (if applicable)
- [ ] **Author name**: Consistent across all books (important for author page)
- [ ] **Contributors**: Co-authors, editors, translators, illustrators (with roles)

#### Book Description
- [ ] **Length**: Up to 4,000 characters
- [ ] **Formatting**: Use HTML subset for bold, italics, lists, line breaks
  - `<b>bold</b>`, `<i>italic</i>`, `<u>underline</u>`
  - `<br>` for line breaks
  - `<ul><li>item</li></ul>` for bullet lists
  - `<ol><li>item</li></ol>` for numbered lists
  - `<h1>`, `<h2>` for headings
- [ ] **Hook**: First 1-2 sentences are critical (appear in search results)
- [ ] **Structure**: Opening hook → key benefits/plot → call to action
- [ ] **Keywords**: Include target keywords naturally (but don't stuff)
- [ ] **No**: External links, email addresses, promotional language about reviews/rankings

#### BISAC Category Codes
- [ ] **Purpose**: Industry-standard subject classification (Book Industry Study Group)
- [ ] **Selection**: Choose up to 2 categories (or 3 for print books)
- [ ] **Strategy**: Pick specific subcategories (better than broad categories)
- [ ] **Competition**: Check bestseller rank in chosen categories
- [ ] **Top-level BISAC categories** (examples):
  - Fiction > [Genre] (Thriller, Romance, Science Fiction, Fantasy, Mystery, etc.)
  - Biography & Autobiography > [Subject]
  - Business & Economics > [Topic]
  - Self-Help > [Topic]
  - Computers > [Topic]
  - History > [Region/Period]
  - Science > [Field]
  - Education > [Level/Subject]
  - Medical > [Specialty]
  - Reference > [Type]

#### Keywords
- [ ] **Limit**: 7 keywords (or short phrases)
- [ ] **Purpose**: Help readers discover your book in Amazon search
- [ ] **Do**: Use specific phrases readers would search ("corporate espionage thriller")
- [ ] **Do**: Include alternate phrasings ("time management" AND "productivity tips")
- [ ] **Don't**: Repeat words already in title/subtitle
- [ ] **Don't**: Use competitor author names or book titles
- [ ] **Don't**: Use subjective claims ("best", "top rated")
- [ ] **Don't**: Include irrelevant terms for visibility (spam = delisting risk)
- [ ] **Tools**: Use Publisher Rocket, KDP Rocket, or Amazon search auto-complete
- [ ] **Format**: Can be multi-word phrases (e.g., "historical fiction WWII")

#### Author Bio
- [ ] **Length**: 2,000 characters max
- [ ] **Content**: Professional credentials, previous books, relevant experience
- [ ] **Tone**: Third person (traditional) or first person (more personal)
- [ ] **Call to action**: Website URL, newsletter signup (if applicable)

### Pricing and Royalties

#### eBook Royalty Tiers
**35% Royalty**:
- [ ] Available for all prices: $0.99 - $200.00
- [ ] No territorial restrictions
- [ ] No file size delivery fees
- [ ] Best for: Books priced under $2.99 or over $9.99

**70% Royalty**:
- [ ] Price range: $2.99 - $9.99 (USD)
- [ ] Territory restrictions (available in select countries)
- [ ] Delivery costs deducted (file size × $0.15/MB)
- [ ] Book must be priced at least 20% below lowest physical price
- [ ] Best for: Most eBooks in competitive price range

**Calculation Example** (70% tier):
- List price: $4.99
- File size: 2MB
- Delivery cost: 2 × $0.15 = $0.30
- Royalty: ($4.99 × 0.70) - $0.30 = $3.49 - $0.30 = **$3.19**

#### KDP Select / Kindle Unlimited
- [ ] **Enrollment**: 90-day automatic renewal periods
- [ ] **Exclusivity**: Cannot publish eBook on other platforms (Amazon-only)
- [ ] **Benefits**:
  - [ ] Kindle Unlimited borrows (paid per page read from global fund)
  - [ ] Kindle Countdown Deals (limited-time discounts)
  - [ ] Free Book Promotions (up to 5 days per 90-day period)
  - [ ] 70% royalty in Brazil, Japan, India, Mexico (normally 35% only)
- [ ] **Trade-offs**: Loss of wide distribution (Apple Books, Kobo, Google Play, etc.)
- [ ] **Strategy**: Test KU for 90 days, then decide on wide distribution

#### Paperback Royalties
- [ ] **Royalty**: 60% of list price minus printing costs
- [ ] **Printing cost factors**: Page count, trim size, color vs. B&W, paper type
- [ ] **Minimum list price**: Must cover printing cost + Amazon's 60% cut (or $2.99, whichever higher)
- [ ] **Example** (6×9, 250 pages, B&W, cream paper):
  - Printing cost: ~$4.00
  - List price: $12.99
  - Royalty: ($12.99 × 0.60) - $4.00 = $7.79 - $4.00 = **$3.79**
- [ ] **Expanded Distribution**: Optional, lowers royalty to 40% but reaches bookstores/libraries

#### Hardcover Royalties
- [ ] **Availability**: Limited trim sizes (case laminate cover only)
- [ ] **Royalty**: 60% of list price minus printing costs
- [ ] **Printing costs**: Higher than paperback (~1.5-2× more)
- [ ] **Best for**: Premium editions, gift books, library market
- [ ] **Example** (6×9, 250 pages, B&W, white paper):
  - Printing cost: ~$8.00
  - List price: $24.99
  - Royalty: ($24.99 × 0.60) - $8.00 = $14.99 - $8.00 = **$6.99**

### Content Guidelines

#### Prohibited Content
- [ ] **Public domain only books**: Must add substantial new content/commentary
- [ ] **Excessive or gratuitous violence**
- [ ] **Pornographic, obscene, or offensive content**
- [ ] **Illegal content**: Instructions for illegal activity
- [ ] **Stolen content**: Copyright infringement, plagiarism
- [ ] **Keyword stuffing**: Spam in title, description, or keywords
- [ ] **Misleading content**: Clickbait titles, misleading descriptions
- [ ] **Undifferentiated versions**: Same book with minor changes re-published
- [ ] **Low-quality content**: Books padded with filler, lorem ipsum, gibberish
- [ ] **Rights violations**: Using trademarks, celebrity names without permission

#### Quality Standards
- [ ] **Proofreading**: Free of excessive spelling/grammar errors
- [ ] **Formatting**: Consistent, professional layout
- [ ] **Cover quality**: Professional design, readable at thumbnail size
- [ ] **Interior quality**: No blurry images, proper margins, readable fonts

### ISBN Guidance

#### Free ASIN (Amazon Standard Identification Number)
- [ ] **Provided by**: Amazon (automatically assigned at publication)
- [ ] **Cost**: Free
- [ ] **Format**: Unique per format (eBook gets different ASIN than paperback)
- [ ] **Limitation**: Only valid on Amazon marketplace
- [ ] **Distribution**: Cannot sell to bookstores or other retailers with ASIN
- [ ] **Best for**: Amazon-exclusive authors, testing the market

#### Purchased ISBN (International Standard Book Number)
- [ ] **Provider**: Bowker in US (myidentifiers.com), official ISBN agency by country
- [ ] **Cost**: $125 for 1 ISBN, $295 for 10, $575 for 100 (US prices as of 2024)
- [ ] **Ownership**: You own the ISBN permanently
- [ ] **Portability**: Can use on any platform (IngramSpark, Barnes & Noble Press, etc.)
- [ ] **Distribution**: Required for bookstore/library distribution
- [ ] **Format requirement**: Each format needs separate ISBN:
  - [ ] Kindle eBook → 1 ISBN (or use free ASIN)
  - [ ] EPUB eBook (wide distribution) → 1 ISBN
  - [ ] Paperback → 1 ISBN
  - [ ] Hardcover → 1 ISBN
  - [ ] Audiobook → 1 ISBN
- [ ] **Imprint**: Can set up publisher imprint (your own publishing name)

#### ISBN Decision Matrix
- [ ] **Amazon-only strategy**: Use free ASIN (no cost, no portability concerns)
- [ ] **Wide distribution**: Purchase ISBNs (flexibility, professional credibility)
- [ ] **Bookstore distribution**: Must have ISBN (required by wholesalers like Ingram)
- [ ] **Multiple editions**: Each requires new ISBN (new edition, new format, new cover)

#### Barcode Placement
- [ ] **With ASIN**: Do NOT add barcode to cover (Amazon adds it automatically)
- [ ] **With ISBN**: Optional to add barcode to PDF cover (KDP can add it if missing)
- [ ] **Position**: Lower right corner of back cover, inside safe zone
- [ ] **Generator**: Use free barcode generator (e.g., bookow.com, ISBN.org)

## Submission Workflow

### eBook
1. **Sign in**: https://kdp.amazon.com
2. **Create new title**: Kindle eBook
3. **Enter metadata**: Title, author, description, keywords, categories
4. **Upload manuscript**: DOCX/EPUB/PDF (eBook file)
5. **Upload cover**: 2560×1600px JPEG/TIFF
6. **Preview**: Use online previewer or download Kindle Previewer app
7. **Set pricing**: Choose territories, royalty tier, price
8. **Publish**: Review and click "Publish Your Kindle eBook"
9. **Review time**: 24-72 hours (typically within 24 hours)

### Paperback
1. **Create new title**: Paperback (or add to existing eBook)
2. **Enter metadata**: Same as eBook (can pre-fill from eBook)
3. **Choose ISBN**: Free KDP ISBN or provide your own
4. **Upload manuscript**: PDF or DOCX (interior file)
5. **Upload cover**: Use Cover Creator or upload PDF/JPEG (with exact dimensions)
6. **Preview**: Use online previewer (check margins, page count)
7. **Set pricing**: List price (must cover printing costs + minimum royalty)
8. **Order proof**: Optional but recommended (physical proof copy shipped)
9. **Publish**: Click "Publish Your Paperback"
10. **Review time**: 24-72 hours for Amazon, 6-8 weeks for Expanded Distribution

### Hardcover
1. **Add to existing paperback**: Hardcover option appears after paperback published
2. **Upload manuscript**: PDF only (must meet hardcover specs)
3. **Upload cover**: PDF with hardcover template dimensions
4. **Pricing**: Set higher list price (printing costs are higher)
5. **Publish**: Similar review time as paperback

## Post-Publication Checklist

### Immediate (Day 1-7)
- [ ] **Check live listing**: Verify title, cover, description, "Look Inside" preview
- [ ] **Test purchase**: Buy copy yourself (eBook and/or print) to verify quality
- [ ] **Author Central**: Claim your author page at https://authorcentral.amazon.com
  - [ ] Upload author photo
  - [ ] Add biography
  - [ ] Link all your books
  - [ ] Connect blog/Twitter feed (optional)
- [ ] **Categories**: Request additional categories via KDP support (can have up to 10 total)
- [ ] **Editorial reviews**: Add blurbs, testimonials in Author Central
- [ ] **A+ Content**: For certain authors, enhanced product descriptions available

### Marketing Launch (Week 1-4)
- [ ] **Price promotion**: Consider launch pricing ($0.99 or $2.99 for eBook)
- [ ] **Newsletter**: Announce to your email list
- [ ] **Social media**: Share cover reveal, launch announcement
- [ ] **Amazon ads**: Set up Sponsored Products campaigns (keyword targeting)
- [ ] **Review strategy**:
  - [ ] ARC (Advance Review Copies) sent to beta readers before launch
  - [ ] Follow up with ARC readers for honest reviews
  - [ ] Never pay for reviews or use review exchange services (TOS violation)
- [ ] **BookBub**: Submit for Featured Deal (if book has reviews and track record)

### Ongoing Monitoring
- [ ] **Sales dashboard**: Check KDP reports daily/weekly (sales, borrows, royalties)
- [ ] **Reviews**: Monitor customer reviews, engage professionally if needed (via Author Central)
- [ ] **Rankings**: Track Amazon Best Sellers Rank (ABSR) in your categories
- [ ] **Advertising ROI**: Analyze ad performance, adjust bids and keywords
- [ ] **Price testing**: Experiment with pricing ($2.99 vs. $3.99 vs. $4.99)
- [ ] **Seasonal promotions**: Kindle Countdown Deals (KDP Select) or manual price drops

### Quality Maintenance
- [ ] **Errata**: If typos found, upload corrected manuscript (no version change needed)
- [ ] **Edition updates**: Major content changes require new edition (and new ISBN if applicable)
- [ ] **Cover refresh**: Update cover if needed (A/B test with ads to compare)
- [ ] **Description optimization**: Refine based on what resonates with readers

## Common Rejection Reasons

### Content Issues
1. **Copyright violations**: Public domain content without added value
2. **Duplicate content**: Same book published multiple times under different titles
3. **Placeholder content**: Lorem ipsum, gibberish, or AI-generated filler
4. **Misleading content**: Title/description doesn't match interior
5. **Prohibited content**: Pornography, excessive violence, illegal activities
6. **Low-quality interior**: Blurry images, unreadable text, poor formatting

### Cover Issues
7. **Resolution too low**: Under 2560×1600px for eBook, under 300 DPI for print
8. **Text cut off**: Cover elements extend beyond safe zone
9. **Incorrect aspect ratio**: eBook cover not 1.6:1 ratio
10. **Bleed issues**: Print cover missing bleed or elements in bleed area
11. **Barcode conflict**: Added barcode when using free ASIN
12. **Misleading cover**: Implies endorsement or uses copyrighted images without permission

### Metadata Issues
13. **Keyword stuffing**: Excessive keywords in title or description
14. **Trademark violations**: Using brand names, celebrity names without rights
15. **Category mismatch**: Book doesn't fit selected BISAC categories
16. **Misleading description**: Claims book doesn't support (e.g., "bestseller" before launch)
17. **Contact information**: Including email/phone in description

### Technical Issues
18. **File format errors**: Corrupted file, wrong file type
19. **Font embedding**: Fonts not embedded in PDF for print
20. **Margin violations**: Text in gutter or outside safe zone
21. **File size**: eBook over 650MB (very rare for text)
22. **Page count**: Under 24 pages (minimum for paperback)
23. **ISBN errors**: Invalid ISBN format or ISBN already in use

### Compliance Issues
24. **Age restrictions**: Adult content without proper content warning
25. **Review manipulation**: Incentivized reviews, fake reviews
26. **Price manipulation**: Artificially inflating list price to qualify for 70% royalty
27. **Spam**: Publishing low-quality books in bulk to game the system

## Revision and Republishing

### Correcting Errors
- [ ] **Minor fixes**: Upload corrected manuscript anytime (typos, formatting)
- [ ] **No re-review**: Corrections typically go live within hours
- [ ] **Customer notification**: Amazon doesn't notify previous buyers of corrections
- [ ] **Manual notification**: You can contact support to push updates to prior customers (for major fixes)

### New Editions
- [ ] **Major changes**: New content, restructuring, expanded material → new edition
- [ ] **ISBN requirement**: New edition needs new ISBN (if using ISBNs)
- [ ] **Version in title**: Add "2nd Edition", "Revised", etc. to title
- [ ] **Previous edition**: Can unpublish or keep available at lower price

### Cover Redesign
- [ ] **Upload new cover**: In "Kindle eBook Content" or "Paperback Content" section
- [ ] **A/B testing**: Consider keeping old version live briefly to compare sales
- [ ] **Professional design**: Invest in professional cover for long-term sales

## Advanced Features

### Kindle Vella (Serialized Stories)
- [ ] **Format**: Episodic fiction (chapters released serially)
- [ ] **Payment**: Readers buy tokens, you earn per token spent
- [ ] **Best for**: Building audience with ongoing series

### Kindle in Motion
- [ ] **Enhanced eBooks**: Add audio, video, animation (children's books, cookbooks)
- [ ] **Submission**: Apply through KDP for approval

### Kindle Interactive Fiction
- [ ] **Choose-your-own-adventure**: Branching narratives
- [ ] **Tool**: Kindle Create supports basic interactivity

### Print-on-Demand Quality
- [ ] **Order author copies**: Buy at printing cost (no royalty) for proofs
- [ ] **Quality variations**: Some books print darker/lighter (check proof)
- [ ] **Returnability**: Can't control returns, but print-on-demand minimizes risk

## Resources and Tools

### Official KDP Tools
- [ ] **Kindle Create**: Free formatting tool for eBooks (reflowable layout)
- [ ] **Kindle Previewer**: Preview eBook on different devices before publishing
- [ ] **Kindle Kids' Book Creator**: Specialized tool for fixed-layout children's books
- [ ] **Cover Calculator**: Generate print cover template with spine width

### Third-Party Tools
- [ ] **Draft2Digital**: Alternative aggregator for wide distribution
- [ ] **IngramSpark**: Print-on-demand + expanded distribution to bookstores
- [ ] **Vellum**: Mac app for formatting eBooks and print books ($249.99)
- [ ] **Scrivener**: Writing and formatting software for authors ($49)
- [ ] **Reedsy Book Editor**: Free online book formatting tool
- [ ] **Publisher Rocket**: Keyword research tool for KDP ($97)
- [ ] **BookBrush**: Create book mockups and promotional graphics

### Learning Resources
- [ ] **KDP Community forums**: Ask questions, troubleshoot issues
- [ ] **Kindlepreneur**: Dave Chesson's blog (tutorials, tools, strategies)
- [ ] **Written Word Media**: BookBub alternatives, newsletter promos
- [ ] **Alliance of Independent Authors (ALLi)**: Professional organization for self-publishers

---

## Quick Reference: Minimum Requirements

| Format | Trim Size | Margins | File Type | Cover Size |
|--------|-----------|---------|-----------|------------|
| **eBook** | N/A | N/A | DOCX/EPUB | 2560×1600px (1.6:1) |
| **Paperback** | 5.5×8.5 to 8.5×11 | 0.25-0.875" (varies) | PDF/DOCX | Calculator-based |
| **Hardcover** | 5.5×8.5 to 8.5×11 | 0.25-0.875" (varies) | PDF only | Calculator-based |

| Pricing Tier | Price Range | Royalty | Restrictions |
|--------------|-------------|---------|--------------|
| **35% eBook** | $0.99-$200 | 35% | None |
| **70% eBook** | $2.99-$9.99 | 70% - delivery fee | Territory limits, no physical version <20% cheaper |
| **Paperback** | Varies | 60% - print cost | Must cover print cost |
| **Expanded Distribution** | Varies | 40% - print cost | Libraries/bookstores |

---

## KDP Account Setup Walkthrough

First-time publishers must complete the following before submitting a book:

1. **Create account**: Go to https://kdp.amazon.com and sign in with an Amazon account (or create one)
2. **Tax interview**: Complete the tax interview — W-9 for US residents, W-8BEN for international authors. Required before royalties can be paid.
3. **Bank account**: Add bank account details for royalty payments (ACH direct deposit for US, wire transfer for international). Minimum payout threshold: $100.
4. **Email verification**: Verify the email address associated with the KDP account. All review notifications and sales reports go to this address.

---

## Genre-Aware Pricing Guide

### eBook Price Ranges by Genre

| Genre | Debut/New Author | Established Author | Notes |
|-------|------------------|--------------------|-------|
| **Fiction** | $2.99-$6.99 | $4.99-$9.99 | $0.99 as loss leader for series starters |
| **Nonfiction** | $4.99-$9.99 | $4.99-$9.99 | Higher price justified by expertise |
| **Technical** | $9.99-$29.99 | $9.99-$29.99 | 70% royalty caps at $9.99; above $9.99 earns 35% |

### Paperback Pricing

KDP calculates printing cost based on page count, paper type, ink type, and trim size.

**Printing cost examples** (6x9 trim, B&W interior):
- 150 pages, white paper: ~$2.71 printing cost
- 200 pages, white paper: ~$3.38 printing cost
- 300 pages, white paper: ~$4.50 printing cost
- 300 pages, cream paper: ~$4.70 printing cost

**Royalty formula**: (list price - printing cost) x 0.60

**Example**: 300-page book, $14.99 list price, $4.50 printing cost
- Royalty: ($14.99 - $4.50) x 0.60 = $10.49 x 0.60 = **$6.29**

**Minimum list price**: Must cover printing cost + Amazon's share. Use KDP's pricing calculator during submission for exact minimum.

### Typical Paperback Price Ranges

| Genre | Price Range | Notes |
|-------|------------|-------|
| **Fiction** | $12.99-$16.99 | Standard trade paperback |
| **Technical** | $29.99-$49.99 | Higher page count, specialized content |
| **Children's** | $8.99-$14.99 | Color interior increases printing cost |

---

## Post-Publication Detail

### Author Central Setup

Author Central (https://authorcentral.amazon.com) is a separate service from KDP that manages the public-facing author page on Amazon.

**Steps**:
1. Claim the author page using the same name as the KDP author name
2. Upload author photo (professional, minimum 300x300 pixels)
3. Add biography (from `kdp.author_bio` in config — can be longer/different from the product page bio)
4. Link all books to the author profile (automatic for KDP titles, manual for other publishers)
5. Add editorial reviews if available (blurbs, testimonials, review excerpts)
6. Connect blog or social media feeds (optional)

### A+ Content

A+ Content adds rich media (images, comparison charts, expanded descriptions) below the main product description on the Amazon product page.

**Eligibility**: Available for KDP Select books or via vendor/publisher accounts.

**Impact**: A+ Content typically increases conversion rate (visitors who buy) by providing more visual and structured information about the book.

**Content types**: Author story, feature highlights, comparison charts, image galleries, expanded "about the author" section.

### Launch Promotion Strategies

**KDP Countdown Deals** (KDP Select only):
- Temporary price reduction with a visible countdown timer on the product page
- Duration: 1-7 days
- Available once per 90-day enrollment period
- Revenue counts toward bestseller rank at the discounted price

**Free Book Promotions** (KDP Select only):
- Set the eBook price to $0.00 for up to 5 days per 90-day enrollment period
- Drives downloads and visibility but generates no direct revenue
- Free downloads do NOT count toward bestseller rank (separate "Top Free" list)
- Best used for series starters to hook readers into buying subsequent volumes

**Goodreads Integration**:
- Claim the book on Goodreads (separate from Amazon account)
- Import book details from Amazon
- Connect author profile to Goodreads Author Program
- Goodreads is a major book discovery platform — active presence helps discoverability

### Ongoing Monitoring

**Sales dashboard**: Check KDP reports for daily/weekly sales, Kindle Unlimited page reads (if enrolled), and royalty accruals.

**Reviews**: Monitor customer reviews via Author Central. Engage professionally if needed — never argue with reviewers or solicit positive reviews.

**Ranking**: Track Amazon Best Sellers Rank (ABSR) in chosen categories. Ranking is updated hourly based on recent sales velocity.

**Updates**: Upload corrected manuscripts or updated covers anytime. Changes propagate in 24-72 hours. Major content changes may warrant a new edition.

---

**Last Updated**: 2026-02-17 (based on current KDP policies)
