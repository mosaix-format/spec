---
title: E011_missing_fragment
id: 01000000000000000000000031
updated: 2026-09-08
type: document
tags: [format]
status: sourced
summary: "Test note for E011: a type:document note whose fragments list references one existing note (fragment_real) and one non-existent note (ghost_fragment). The missing fragment triggers E011 fragment_not_found."
keywords: [missing fragment, e011, document type, fragments, conformance, error]
entities:
  - {name: Mosaix Format, type: document}
fragments: [fragment_real, ghost_fragment]
links: [fragment_real]
rev: deadbeef0031
---

# E011_missing_fragment

A composed document with a missing fragment — should trigger E011.
