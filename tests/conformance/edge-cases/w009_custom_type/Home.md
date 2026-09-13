---
title: Home
id: 01000000000000000000000W09
updated: 2026-09-13
tags: [moc]
status: sourced
summary: "MOC for W009 test vault: demonstrates that custom entity types not declared in the meta note generate a WARNING (W009), not an ERROR, maintaining backward compatibility and domain flexibility."
keywords: [home, moc, w009, custom entity type, warning, conformance]
entities:
  - {name: Test Vault, type: project}
rev: 000000000W09
---

# Home — W009 Custom Entity Type Test

This vault contains a note with a custom entity type `character` that is NOT declared in the meta note.

Under v1.2, this generates **W009 warning**, not an error, because entity_types in the meta note serves to DECLARE types for tools, not to RESTRICT what's allowed.

See [[note_with_custom_type]].
