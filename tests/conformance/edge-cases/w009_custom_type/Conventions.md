---
title: Conventions
id: 01000000000000000000000W11
mosaix: "1.2"
updated: 2026-09-13
tags: [meta]
status: sourced
summary: "Conventions for W009 test vault, declaring NO custom entity types in entity_types — the note_with_custom_type uses 'character' which is not declared, triggering W009."
keywords: [conventions, meta, w009, entity types, taxonomy, test vault]
entities:
  - {name: Mosaix Format, type: tool}
rev: 000000000W11
---

# Conventions

## Tag Taxonomy

#moc #meta #ledger #test #conformance

## Entity Types

We deliberately do NOT declare `character` as an entity type here.
The note [[note_with_custom_type]] uses it anyway — this should trigger **W009**, not E005.

## Reliability Convention

Uses `status` key with values: `sourced`, `to-confirm`, `superseded`.
