---
title: W004_invalid_id
id: "not-a-ulid"
updated: 2026-09-08
tags: [concept]
status: sourced
summary: "Test note for W004: the id value 'not-a-ulid' does not match the ULID pattern (26 Crockford Base32 chars, first digit 0-7). In v1.0 this is a warning; it becomes an error from v2.0."
keywords: [invalid id, w004, ulid, conformance, warning, format]
entities:
  - {name: Mosaix Format, type: document}
rev: deadbeef0061
---

# W004_invalid_id

Has `id: "not-a-ulid"` — should trigger W004.
