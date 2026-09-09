---
id: 01JVKE4X2PFNRW8BQDP5MHCGEE
title: Note C
updated: 2026-09-09
tags: [test, conformance]
summary: "Note C — links to a ULID (01JVKE4X2PFNRW8BQDP5MHCG99) that does not correspond to any note in the vault; the checker must emit exactly one E008 error for this reference."
keywords: [ulid, link-resolution, broken, test, e008, conformance]
entities:
  - {name: Test Suite, type: project}
links: [01JVKE4X2PFNRW8BQDP5MHCG99]
rev: 000000000000
status: sourced
---

This note references a non-existent ULID (`01JVKE4X2PFNRW8BQDP5MHCG99`).
No note in the vault carries this id, so the checker must emit E008.
