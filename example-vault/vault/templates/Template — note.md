---
title: Template — note
type: template
updated: 2026-09-05
tags: [template]
status: sourced
summary: "Starter CORE frontmatter and body for an ordinary Mosaix note, with Obsidian Templates placeholders for title and date, ready to fill in before linking it into the vault."
keywords: [starter template, ordinary note, core frontmatter, obsidian templates plugin, title and date placeholder, fill in before linking, one question one answer]
entities:
  - {name: Mosaix Format, type: project}
  - {name: Obsidian, type: tool}
relations: []
links: [§3 The note, R1 Atomicity, key rev]
rev: aa11bb22cc33
---

# Template — note

Copy this file to start an ordinary note ([[§3 The note]]). One question. Answer it. Name the source.

- **One question.** Write the single thing this note answers; if you need "and", split it into two notes ([[R1 Atomicity]]).
- **Answer it.** The body is the answer, nothing more; length is not the constraint, scope is.
- **Name the source.** Say where the fact comes from, then move `status` from `to-confirm` to `sourced`.
- **Link it in.** Add at least one wikilink to an existing note so this note is not an orphan; `rev` closes the loop once metadata is computed ([[key rev]]).

Replace the frontmatter above with this when you copy the template. `{{title}}` and `{{date:YYYY-MM-DD}}` are Obsidian Templates placeholders; fill them in by hand if you are not using Obsidian.

```yaml
---
title: {{title}}
updated: {{date:YYYY-MM-DD}}
tags: []
status: to-confirm
summary: ""
keywords: []
entities: []
relations: []
links: []
rev: ""
---
```
