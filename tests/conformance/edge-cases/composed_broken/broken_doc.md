---
id: 01JXAJ00000000000000000004
title: Broken Composed Document
type: document
updated: 2026-09-01
tags: [test, documentation]
summary: "A composed document with two fragment references where one does not exist, triggering E011 for the missing entry while the two-fragment count prevents E010 from also firing."
keywords: [composed, document, broken, missing-fragment, e011, conformance]
entities:
  - {name: Test Suite, type: project}
fragments: [existing_fragment, ghost_fragment]
rev: 000000000000
status: sourced
---

Two fragments listed: `existing_fragment` resolves (no E011), `ghost_fragment` does not (E011 fires).
