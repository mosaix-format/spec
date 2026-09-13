---
title: E005_bad_entity_type
id: 01000000000000000000000026
updated: 2026-09-08
tags: [concept]
status: sourced
summary: "Test note for E005: contains an entity with empty type (empty string), which is an error. All other CORE keys are valid to isolate this error."
keywords: [bad entity type, e005, entity, conformance, error, mosaix]
entities:
  - {name: Mosaix Format, type: document}
  - {name: TestThing, type: ""}
rev: deadbeef0026
---

# E005_bad_entity_type

Has an entity with empty type — should trigger E005 (empty/non-string type is error).
