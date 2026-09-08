---
id: 01JXAC0000000000000000000F
title: Missing Links Target
updated: 2026-09-01
tags: [test, error-testing]
summary: "Test note with a links entry containing a plain filename that does not resolve to any existing note file, triggering E009 which checks non-ULID links via filename resolution."
keywords: [test, e009, links, filename, resolution, conformance]
entities:
  - {name: Test Suite, type: project}
links: [phantom_note]
rev: 000000000000
status: sourced
---

The filename `phantom_note` in `links` does not exist in the vault, triggering E009.
