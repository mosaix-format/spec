---
title: Template — document
type: template
updated: 2026-09-05
tags: [template]
status: sourced
summary: "Starter frontmatter for a composed document: fragments in reading order, an optional pool of candidates and a free-form layout map for the cover, sections and page format."
keywords: [starter template, composed document, fragments in order, optional pool, layout map, cover and sections, view over notes]
entities:
  - {name: Mosaix Format, type: project}
relations: []
links: [§6 Composed documents, Mosaix for a new team, R5 Composition over duplication]
rev: dd44ee55ff66
---

# Template — document

Copy this file to start a composed document ([[§6 Composed documents]]). The fragments stay atomic and separate; the document is only the view.

- **`fragments`** is the ordered list of note titles that make up the document, in reading order; a document needs at least two, and each must resolve.
- **`pool`** is optional: candidate notes you considered but did not include.
- **`layout`** is optional and free-form: cover, page format, sections, and which of each fragment's frontmatter to show.
- **Never copy.** Content that must be read together is joined here, never duplicated into the fragments ([[R5 Composition over duplication]]).
- See [[Mosaix for a new team]] in this vault for a working composed document.

A blank document starts with an empty `fragments` and `pool`; fill them in as you choose fragments, then add `layout` if you want presentation hints. Replace the frontmatter above with this when you copy the template:

```yaml
---
title: {{title}}
updated: {{date:YYYY-MM-DD}}
tags: []
type: document
status: sourced
summary: ""
keywords: []
entities: []
relations: []
links: []
fragments: []
pool: []
layout:
  cover: {title: '', subtitle: '', date: {{date:YYYY-MM-DD}}}
  page: A4
  sections:
    - {title: '', fragments: []}
  show: [summary, status]
rev: ""
---
```
