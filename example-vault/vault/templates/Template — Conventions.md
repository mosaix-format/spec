---
title: Template — Conventions
type: template
updated: 2026-09-05
tags: [template]
status: sourced
summary: "Starter frontmatter for a vault's meta note: the folder contract, the reliability convention, declared tags, domain keys, aliases, entity and relation types, and maintainers."
keywords: [starter template, meta note, folder contract, reliability convention, declared taxonomy, domain keys, maintainers]
entities:
  - {name: Mosaix Format, type: project}
relations: []
links: [§5 Vault structure, R4 Declared taxonomy, Conventions]
rev: ee55ff66aa77
---

# Template — Conventions

Copy this file to start the meta note of your own vault ([[§5 Vault structure]]). It is the one note that states the vault's own rules.

- **Folder contract.** Which question each folder answers.
- **Reliability convention.** Which key or marker carries axis A: this vault uses `status`.
- **Declared taxonomy.** Every tag in use, in one list; a tag used but not declared is a warning ([[R4 Declared taxonomy]]).
- **Domain keys, aliases, entity and relation types, maintainers.** Anything your vault adds beyond CORE.
- See [[Conventions]] in this vault for a working meta note.

Replace the frontmatter above with this when you copy the template, then fill in the example values for your own vault:

```yaml
---
title: {{title}}
updated: {{date:YYYY-MM-DD}}
tags: [moc, meta, ledger, player, market]
status: sourced
summary: ""
keywords: []
entities: []
relations: []
links: []
mosaix: "1.0"
folders: {01-Company: who they are, 02-Market: where they sell}
reliability: {key: status, values: [sourced, to-confirm, superseded]}
domain_keys: {client: string, country: ISO-3166 alpha-2}
aliases: {aggiornato: updated}
entity_types: [department, regulation]
relation_types: [owns, supplies, competes with, depends on]
payload: [exports/]
maintainers: [{name: '', area: ''}]
rev: ""
---
```
