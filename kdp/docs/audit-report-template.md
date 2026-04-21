# KDP Audit Report Template

Canonical structure for the gap report produced by the `kdp-audit` skill. Use this as the skeleton when writing the report; omit sections that do not apply (for example, the Fiction section for a technical book).

## Template

```markdown
# KDP Audit Report: {book title}

## Summary
- **Status**: READY / NEEDS WORK / NOT READY
- **Manuscript type**: Technical / Fiction / Nonfiction
- **Format**: LaTeX / DOCX / EPUB / PDF
- **Target**: eBook only / Paperback only / Both

## Critical Gaps (Must Fix)
1. [Issue description] at [file:line]: [how to fix]

## Warnings (Should Fix)
1. [Issue description]: [recommendation]

## Interior Formatting
- [ ] or [x] Trim size: {size} (supported: yes/no)
- [ ] or [x] Margins: inside {calc}, outside {val}, top {val}, bottom {val}
- [ ] or [x] Fonts embedded and standard
- [ ] or [x] Page numbers start after front matter
- [ ] or [x] Table of Contents present and functional

## Cover Specifications
- [ ] or [x] eBook cover: {resolution}, {ratio}, {format}
- [ ] or [x] Paperback cover: {resolution}, spine width {calc}
- [ ] or [x] Cover dimensions verified: {actual} (required: {minimum})

## Metadata
- [ ] or [x] Title and subtitle
- [ ] or [x] Description/blurb (<4000 chars)
- [ ] or [x] Categories (up to 3 BISAC codes)
- [ ] or [x] Keywords (up to 7)
- [ ] or [x] Author bio present

## Technical Books Only
- [ ] or [x] LaTeX compiles successfully
- [ ] or [x] Math rendering correct
- [ ] or [x] Code listings formatted
- [ ] or [x] Index and bibliography present

## Fiction Only
- [ ] or [x] Front matter order: title, copyright, dedication, TOC
- [ ] or [x] Back matter includes About the Author
- [ ] or [x] Scene breaks use consistent markers
- [ ] or [x] Dialog formatting consistent
- [ ] or [x] Paragraph indentation correct

## eBook Validation
- [ ] or [x] EPUB validates (epubcheck)
- [ ] or [x] No Kindle-breaking issues (footnotes, wide tables, complex CSS)

## Recommended Next Steps
1. [Ordered list of actions to reach READY status]
```

## Writing Guidelines

- **Status line**: use READY only when there are zero critical gaps and all required sections pass. Prefer NEEDS WORK over NOT READY unless the manuscript is fundamentally unsubmittable.
- **Critical vs. Warnings**: Critical means KDP will reject or the book will ship with serious quality issues. Warnings are recommendations that improve the product but do not block publication.
- **Checkbox style**: use `[x]` for passing items and `[ ]` for failing items. Omit genre-specific sections that do not apply.
- **Specific references**: when flagging a gap, cite the file and line number if discoverable. For cover issues, cite the actual measured dimension vs. the requirement.
- **Next steps**: order by blocking severity, then by effort. Put the one-click fixes near the top.
