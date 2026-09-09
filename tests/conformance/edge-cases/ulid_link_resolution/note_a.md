---
id: 01JVKE4X2PFNRW8BQDP5MHCG2X
title: Note A
updated: 2026-09-09
tags: [test, conformance]
summary: "Note A — carries id 01JVKE4X2PFNRW8BQDP5MHCG2X so that note_b can reference it by ULID and the id-first resolver can locate it, confirming zero E008 errors for that link."
keywords: [ulid, link-resolution, target, test, e008, conformance]
entities:
  - {name: Test Suite, type: project}
rev: 000000000000
status: sourced
---

This note exists to be referenced by ULID from note_b.
Its `id` field (`01JVKE4X2PFNRW8BQDP5MHCG2X`) must be found by the id-first resolver,
so note_b's link produces no error.
