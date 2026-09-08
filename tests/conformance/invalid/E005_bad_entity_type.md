---
title: E005_bad_entity_type
id: 01000000000000000000000026
updated: 2026-09-08
tags: [concept]
status: sourced
summary: "Test note for E005: contains an entity with type 'banana', which is not a built-in Mosaix entity type and is not declared in the meta note. All other CORE keys are valid to isolate this error."
keywords: [bad entity type, e005, entity, conformance, error, mosaix]
entities:
  - {name: Mosaix Format, type: document}
  - {name: TestThing, type: banana}
rev: deadbeef0026
---

# E005_bad_entity_type

Has an entity with type `banana` — should trigger E005.
