---
title: E008_ulid_not_resolved
id: 01000000000000000000000028
updated: 2026-09-08
tags: [concept]
status: sourced
summary: "Test note for E008: the links list contains a valid ULID that does not match any note's id field in the vault. The checker must resolve ULID entries by id-first lookup and emit E008 when none is found."
keywords: [ulid not resolved, e008, links, id resolution, conformance, error]
entities:
  - {name: Mosaix Format, type: document}
links: [01FAKE000000000000000000ZZ]
rev: deadbeef0028
---

# E008_ulid_not_resolved

The `links` key contains a ULID that resolves to no note — should trigger E008.
