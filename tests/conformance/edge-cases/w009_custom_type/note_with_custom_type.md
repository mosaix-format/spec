---
title: note_with_custom_type
id: 01000000000000000000000W12
updated: 2026-09-13
tags: [test]
status: sourced
summary: "Test note using custom entity type 'character' which is NOT in the base set and NOT declared in the meta note — this triggers W009 warning, demonstrating that v1.2 allows domain-specific types."
keywords: [custom entity type, character, w009, warning, conformance, mosaix]
entities:
  - {name: Westguard Player, type: character}
  - {name: Test Suite, type: project}
links: [Home]
rev: 000000000W12
---

# note_with_custom_type

This note contains an entity with `type: character`, which is:
- NOT in the base set (person, company, product, project, tool, place, document, event)
- NOT declared in the meta note's `entity_types`

Under v1.2, this generates **W009 warning**, not E005 error.

See [[Home]].
