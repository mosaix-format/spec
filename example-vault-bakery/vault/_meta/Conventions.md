---
title: Conventions
type: meta
updated: 2026-09-05
tags: [moc, meta, ledger, synthesis, people, product, bread, pastry, seasonal, supplier, market, neighbourhood, competitor, event, operations, equipment, policy, decision, composed-document]
status: sourced
summary: "Meta note of the Forno Vialetto vault: folder contract, reliability convention (status key), declared tags, domain keys (season, channel), entity type recipe, and closed relation vocabulary."
keywords: [conventions, meta note, folder contract, reliability convention, declared tags, bakery taxonomy, domain keys, maintainer]
entities:
  - {name: Forno Vialetto, type: company}
relations: []
links: [Open questions, Home]
mosaix: "1.0"
folders: {01-People: who the partners are, 02-Products: what the bakery sells, 03-Suppliers: who provides ingredients, 04-Market: where they sell and who competes, 05-Operations: how the bakery runs, 06-Decisions: choices that shape the business}
reliability: {key: status, values: [sourced, to-confirm, superseded]}
domain_keys: {season: [spring, summer, autumn, winter], channel: [shop, market, wholesale]}
entity_types: [recipe]
relation_types: [supplies, owns, sells at, competes with, depends on]
maintainers:
  - {name: E. Nordgren, area: products}
  - {name: M. Trevisan, area: operations}
rev: 1a2b3c4d5e6f
---

# Conventions

mosaix: "1.0". Folders: `01-People/` who the partners are, `02-Products/` what the bakery sells, `03-Suppliers/` who provides the ingredients, `04-Market/` where they sell and who competes, `05-Operations/` how the bakery runs, `06-Decisions/` choices that shape the business. Reserved: `_meta/`, `_synthesis/`, `_docs/`.

Reliability: frontmatter key `status` with values sourced · to-confirm · superseded. Domain keys: `season` (spring, summer, autumn, winter), `channel` (shop, market, wholesale). Entity type added: `recipe`. Relation types: supplies, owns, sells at, competes with, depends on.

Tags declared: the `tags` list of this note is the taxonomy. Maintainers: E. Nordgren (products), M. Trevisan (operations). Map of content: [[Home]]. Ledger: [[Open questions]].
