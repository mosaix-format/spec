---
title: W001_many_entities
id: 01000000000000000000000050
updated: 2026-09-08
tags: [concept]
status: sourced
summary: "Test note for W001: carries 13 entities, which exceeds the recommended maximum of 12 for a non-MOC note. The excess triggers the atomicity warning suggesting this note may answer more than one question."
keywords: [many entities, w001, atomicity, entities count, conformance, warning]
entities:
  - {name: Entity One, type: person}
  - {name: Entity Two, type: person}
  - {name: Entity Three, type: company}
  - {name: Entity Four, type: company}
  - {name: Entity Five, type: product}
  - {name: Entity Six, type: product}
  - {name: Entity Seven, type: project}
  - {name: Entity Eight, type: project}
  - {name: Entity Nine, type: tool}
  - {name: Entity Ten, type: tool}
  - {name: Entity Eleven, type: event}
  - {name: Entity Twelve, type: event}
  - {name: Entity Thirteen, type: place}
rev: deadbeef0050
---

# W001_many_entities

Has 13 entities — should trigger W001.
