---
id: 01JVKE4X2PFNRW8BQDP5MHCGDD
title: Note B
updated: 2026-09-09
tags: [test, conformance]
summary: "Note B — links to Note A via ULID (01JVKE4X2PFNRW8BQDP5MHCG2X); the id-first resolver must find it, producing zero errors for this link."
keywords: [ulid, link-resolution, id-first, test, e008, conformance]
entities:
  - {name: Test Suite, type: project}
links: [01JVKE4X2PFNRW8BQDP5MHCG2X]
rev: 000000000000
status: sourced
---

This note references Note A by ULID, not by filename.
The id-first resolver should find `01JVKE4X2PFNRW8BQDP5MHCG2X` in the id index → no E008.
