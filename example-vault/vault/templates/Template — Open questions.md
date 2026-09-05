---
title: Template — Open questions
type: ledger
updated: 2026-09-05
tags: [template]
status: sourced
summary: "Starter frontmatter and entry structure for the open-questions ledger: the question, the competing versions with dates and sources, the consequence, and who resolves it."
keywords: [starter template, open questions ledger, competing versions, dates and sources, practical consequence, who resolves it, record don't resolve]
entities:
  - {name: Mosaix Format, type: project}
relations: []
links: [§7 Rules, Open questions, "R6 Record, don't resolve"]
rev: ff66aa77bb88
---

# Template — Open questions

Copy this file to start the open-questions ledger, canonically `_meta/Open questions.md`, part of the vault's rules ([[§7 Rules]]). One entry per contradiction or unknown.

- **The question.** What is not yet known or is contradictory.
- **The competing versions**, each with its date and its source.
- **The consequence.** What changes in practice depending on which version wins.
- **The owner.** Who is expected to resolve it.
- Nobody picks a winner silently ([[R6 Record, don't resolve]]). See [[Open questions]] in this vault for a working ledger.

Replace the frontmatter above with this when you copy the template. A ready-made entry structure for the body follows it:

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

```markdown
## {{question}}

- Version A — {{date}}, source: {{source}}. {{claim}}
- Version B — {{date}}, source: {{source}}. {{claim}}

Consequence: {{what changes depending on which version wins}}.
Owner: {{who resolves it}}.
```
